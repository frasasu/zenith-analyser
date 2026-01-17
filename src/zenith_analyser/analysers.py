# Copyright 2026 François TUMUSAVYEYESU.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
Analyzers for Zenith language structures.

Contains LawAnalyser, TargetAnalyser, and ZenithAnalyser classes.
"""

import copy
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .exceptions import ZenithAnalyserError, ZenithTimeError, ZenithValidationError
from .utils import (
    add_minutes_to_datetime,
    format_datetime,
    minutes_to_point,
    parse_datetime,
    point_to_minutes,
)


class LawAnalyser:
    """
    Analyzer for individual laws.

    Extracts and validates law data from AST.
    """

    def __init__(self, ast: Dict[str, Any]):
        """
        Initialize the law analyzer.

        Args:
            ast: Abstract Syntax Tree from parser
        """
        self.ast = ast
        self.laws = self.extract_laws(self.ast)

    def extract_laws(self, ast: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract all laws from AST.

        Args:
            ast: Abstract Syntax Tree

        Returns:
            Dictionary of laws indexed by name
        """
        data_laws = {}

        def _traverse(elements: List[Dict[str, Any]]) -> None:
            for element in elements:
                if element.get("type") == "law":
                    self._extract_law_data(element, data_laws)
                elif element.get("type") == "target":
                    contents = element.get("contents", {})
                    blocks = contents.get("blocks", [])
                    _traverse(blocks)

        _traverse(ast.get("elements", []))
        return data_laws

    def _extract_law_data(
        self, law_node: Dict[str, Any], data_laws: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Extract data from a single law node.

        Args:
            law_node: Law AST node
            data_laws: Dictionary to populate
        """
        name = law_node.get("name")
        if not name:
            return

        contents = law_node.get("contents", {})
        start_date = contents.get("start_date", {})

        data_laws[name] = {
            "name": name,
            "date": start_date.get("date"),
            "time": start_date.get("time"),
            "period": contents.get("period"),
            "dictionnary": copy.deepcopy(contents.get("events", [])),
            "group": copy.deepcopy(contents.get("group", [])),
            "source_node": law_node,  # Keep reference for debugging
        }

    def get_law_names(self) -> List[str]:
        """
        Get all law names.

        Returns:
            List of law names
        """
        return list(self.laws.keys())

    def get_law(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific law by name.

        Args:
            name: Law name

        Returns:
            Law data or None if not found
        """
        return copy.deepcopy(self.laws.get(name))

    def validate_law(self, name: str) -> List[str]:
        """
        Validate a specific law.

        Args:
            name: Law name

        Returns:
            List of validation errors
        """
        law = self.get_law(name)
        if not law:
            return [f"Law '{name}' not found"]

        errors = []

        # Check required fields
        required = ["date", "time", "period", "dictionnary", "group"]
        for field in required:
            if not law.get(field):
                errors.append(f"Missing required field: {field}")

        if errors:
            return errors

        # Validate date/time
        try:
            parse_datetime(law["date"], law["time"])
        except ZenithTimeError as e:
            errors.append(str(e))

        # Validate period
        try:
            point_to_minutes(law["period"])
        except ZenithTimeError as e:
            errors.append(f"Invalid period: {str(e)}")

        # Validate dictionnary
        if not isinstance(law["dictionnary"], list):
            errors.append("Dictionnary must be a list")
        else:
            seen_names = set()
            for i, entry in enumerate(law["dictionnary"]):
                if not isinstance(entry, dict):
                    errors.append(f"Dictionnary entry {i} must be a dictionary")
                    continue

                entry_name = entry.get("name")
                if not entry_name:
                    errors.append(f"Dictionnary entry {i} missing name")
                    continue

                if entry_name in seen_names:
                    errors.append(f"Duplicate dictionnary entry: {entry_name}")
                else:
                    seen_names.add(entry_name)

        # Validate group
        if not isinstance(law["group"], list):
            errors.append("Group must be a list")
        else:
            for i, event in enumerate(law["group"]):
                if not isinstance(event, dict):
                    errors.append(f"Group event {i} must be a dictionary")
                    continue

                required_fields = ["name", "chronocoherence", "chronodispersal"]
                for field in required_fields:
                    if field not in event:
                        errors.append(f"Group event {i} missing '{field}'")

        return errors


class TargetAnalyser:
    """
    Analyzer for targets and their hierarchies.

    Extracts targets, analyzes relationships, and manages law inheritance.
    """

    def __init__(self, ast: Dict[str, Any]):
        """
        Initialize the target analyzer.

        Args:
            ast: Abstract Syntax Tree from parser
        """
        self.ast = ast
        self.law_analyser = LawAnalyser(ast)
        self.targets = self.extract_targets(ast)
        self._populate_descendants()

    def extract_targets(self, ast: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Extract all targets from AST.

        Args:
            ast: Abstract Syntax Tree

        Returns:
            Dictionary of targets indexed by name
        """
        data_targets = {}

        def _traverse(
            elements: List[Dict[str, Any]], current_path: List[str] = None
        ) -> None:
            if current_path is None:
                current_path = []

            for element in elements:
                if element.get("type") == "target":
                    self._extract_target_data(element, data_targets, current_path)

                    # Recurse into blocks
                    contents = element.get("contents", {})
                    blocks = contents.get("blocks", [])
                    new_path = current_path + [element["name"]]
                    _traverse(blocks, new_path)

        _traverse(ast.get("elements", []))
        return data_targets

    def _extract_target_data(
        self,
        target_node: Dict[str, Any],
        data_targets: Dict[str, Dict[str, Any]],
        current_path: List[str],
    ) -> None:
        """
        Extract data from a single target node.

        Args:
            target_node: Target AST node
            data_targets: Dictionary to populate
            current_path: Current path in hierarchy
        """
        name = target_node.get("name")
        if not name:
            return

        contents = target_node.get("contents", {})

        data_targets[name] = {
            "name": name,
            "key": contents.get("key", ""),
            "dictionnary": copy.deepcopy(contents.get("dictionnary", [])),
            "direct_laws": [],
            "direct_targets": [],
            "all_descendants_laws": set(),
            "all_descendants_targets": set(),
            "path": current_path + [name],
            "depth": len(current_path) + 1,
            "source_node": target_node,  # Keep reference for debugging
        }

        # Extract direct laws and targets from blocks
        blocks = contents.get("blocks", [])
        for block in blocks:
            if block.get("type") == "law":
                law_name = block.get("name")
                if law_name:
                    data_targets[name]["direct_laws"].append(law_name)
            elif block.get("type") == "target":
                target_name = block.get("name")
                if target_name:
                    data_targets[name]["direct_targets"].append(target_name)

    def _populate_descendants(self) -> None:
        """
        Populate descendant sets for all targets.
        """

        def _get_descendants(target_name: str) -> Tuple[Set[str], Set[str]]:
            """Get all descendant laws and targets for a target."""
            if target_name not in self.targets:
                return set(), set()

            target = self.targets[target_name]

            # Return cached results if available
            if (
                target["all_descendants_laws"]
                and target["all_descendants_targets"]
                and len(target["all_descendants_laws"]) > 0
                and len(target["all_descendants_targets"]) > 0
            ):
                return target["all_descendants_laws"], target["all_descendants_targets"]

            # Calculate descendants
            descendant_laws = set(target["direct_laws"])
            descendant_targets = set(target["direct_targets"])

            for child_name in target["direct_targets"]:
                child_laws, child_targets = _get_descendants(child_name)
                descendant_laws.update(child_laws)
                descendant_targets.update(child_targets)

            # Cache results
            target["all_descendants_laws"] = descendant_laws
            target["all_descendants_targets"] = descendant_targets

            return descendant_laws, descendant_targets

        # Calculate descendants for all targets
        for target_name in list(self.targets.keys()):
            _get_descendants(target_name)

    def get_target_names(self) -> List[str]:
        """
        Get all target names.

        Returns:
            List of target names
        """
        return list(self.targets.keys())

    def get_target(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific target by name.

        Args:
            name: Target name

        Returns:
            Target data or None if not found
        """
        return copy.deepcopy(self.targets.get(name))

    def get_target_hierarchy(self, name: str) -> Dict[str, Any]:
        """
        Get the hierarchy for a specific target.

        Args:
            name: Target name

        Returns:
            Hierarchy information

        Raises:
            ZenithAnalyserError: If target not found
        """
        if name not in self.targets:
            raise ZenithAnalyserError(f"Target '{name}' not found", target_name=name)

        target = self.targets[name]

        return {
            "name": name,
            "path": target["path"],
            "depth": target["depth"],
            "parent": target["path"][-2] if len(target["path"]) > 1 else None,
            "children": target["direct_targets"],
            "descendants": list(target["all_descendants_targets"]),
            "direct_laws": target["direct_laws"],
            "descendant_laws": list(target["all_descendants_laws"]),
        }

    def extract_laws_for_target(self, name_target: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract laws for a specific target with dictionary inheritance.

        Args:
            target_name: Target name

        Returns:
            Dictionary of laws with inherited dictionaries

        Raises:
            ZenithAnalyserError: If target not found
        """
        if name_target not in self.targets:
            raise ZenithAnalyserError(
                f"Target '{name_target}' not found", target_name=name_target
            )

        targets = copy.deepcopy(self.extract_targets(self.ast))
        laws = copy.deepcopy(self.law_analyser.extract_laws(self.ast))

        data_laws = {}

        def _traverse(target_name):

            direct_laws_names = targets[target_name]["direct_laws"]
            direct_laws = {}
            dictionnary = targets[target_name]["dictionnary"]
            direct_targets_names = targets[target_name].get("direct_targets", set())

            for name in direct_laws_names:
                direct_laws[name] = copy.deepcopy(laws[name])

            for dict in dictionnary:
                for name in direct_laws_names:
                    for index, event in enumerate(direct_laws[name]["dictionnary"]):
                        if dict["name"] == event.get("index", ""):
                            direct_laws[name]["dictionnary"][index]["description"] = (
                                dict["description"]
                            )

            for dict in dictionnary:
                for name in direct_targets_names:
                    for index, event in enumerate(targets[name]["dictionnary"]):
                        if dict["name"] == event.get("index", ""):
                            targets[name]["dictionnary"][index]["description"] = dict[
                                "description"
                            ]

            for name in list(direct_laws.keys()):
                data_laws[name] = copy.deepcopy(direct_laws[name])

            for name in direct_targets_names:
                _traverse(name)

        _traverse(name_target)

        return data_laws

    def get_targets_by_generation(self, generation: int) -> List[str]:
        """
        Get targets at a specific generation level.

        Args:
            generation: Generation level (1 = root)

        Returns:
            List of target names at that generation
        """
        result = []
        for name, target in self.targets.items():
            if target["depth"] == generation:
                result.append(name)
        return result

    def get_max_generation(self) -> int:
        """
        Get the maximum generation depth.

        Returns:
            Maximum depth
        """
        max_depth = 0
        for target in self.targets.values():
            if target["depth"] > max_depth:
                max_depth = target["depth"]
        return max_depth

    def get_targets_by_key(self, key: str) -> List[str]:
        """
        Get targets with a specific key.

        Args:
            key: Key to search for

        Returns:
            List of target names with that key
        """
        result = []
        for name, target in self.targets.items():
            if target.get("key") == key:
                result.append(name)
        return result

    def corp_extract_laws_transformed(
        self, generation: int = 1
    ) -> Dict[str, Dict[str, Any]]:
        """
        Extract laws transformed by dictionary inheritance for a specific generation.

        Args:
            generation: Generation level to extract (1 = root generation)

        Returns:
            Dictionary of laws with dictionary inheritance applied

        Raises:
            ZenithValidationError: If generation is less than 1
        """
        if generation < 1:
            raise ZenithValidationError(
                f"Generation level must be at least 1: {generation}",
                validation_type="generation",
            )

        data_laws = {}

        paths = {}
        targets_names = []
        for name in list(self.targets.keys()):
            targets_names.append(name)

        for name in targets_names:
            paths[name] = {
                "name": name,
                "path": self.targets[name]["path"],
                "generation": len(self.targets[name]["path"]),
            }

        allowed_targets_name = []
        for name in targets_names:
            if paths[name]["generation"] == generation:
                allowed_targets_name.append(name)

        for target_name in allowed_targets_name:
            laws = {}
            for name in self.extract_laws_for_target(target_name):
                laws[name] = copy.deepcopy(
                    self.extract_laws_for_target(target_name).get(name, "")
                )

            for name in list(laws.keys()):
                data_laws[name] = copy.deepcopy(laws[name])

        return data_laws

    def extract_laws_population(self, population: int = 1) -> Dict[str, Dict[str, Any]]:
        """
        Extract laws for a specific population level with inheritance.

        Args:
            population: Population level (1 = first generation, 0 = all laws)

        Returns:
            Dictionary of laws with dictionary inheritance for the specified population

        Raises:
            ValueError: If population is negative
        """
        if population < 0:
            raise ZenithValidationError(
                f"Population level cannot be negative: {population}",
                validation_type="population",
            )

        laws_population = {}
        for i in range(population, 0, -1):
            current_gen_laws = self.corp_extract_laws_transformed(i)

            for name_gen, law_data in current_gen_laws.items():
                if name_gen not in laws_population:
                    laws_population[name_gen] = copy.deepcopy(law_data)

        top_level_laws = self.law_analyser.extract_laws(self.ast)

        for name_global, law_data in top_level_laws.items():
            if name_global not in laws_population:
                laws_population[name_global] = copy.deepcopy(law_data)

        return laws_population

    def extract_laws_max_population(self):
        return self.extract_laws_population(self.get_max_generation())


class ZenithAnalyser:
    """
    Main analyzer class with full functionality.

    Combines lexer, parser, and analyzers for complete analysis.
    """

    def __init__(self, code: str):
        """
        Initialize the Zenith analyzer.

        Args:
            code: Zenith code to analyze
        """
        from .lexer import Lexer
        from .parser import Parser
        from .validator import Validator

        self.code = code
        self.lexer = Lexer(code)
        self.tokens = self.lexer.tokenise()

        self.validator = Validator()
        validation_errors = self.validator.validate_tokens(self.tokens)
        if validation_errors:
            raise ZenithValidationError(
                f"Token validation failed: {validation_errors[0]}",
                validation_type="tokens",
            )

        self.parser = Parser(self.tokens)
        self.ast, self.parser_errors = self.parser.parse()

        if self.parser_errors:
            raise ZenithValidationError(
                f"Parsing failed: {self.parser_errors[0]}", validation_type="parsing"
            )

        ast_errors = self.validator.validate_ast(self.ast)
        if ast_errors:
            raise ZenithValidationError(
                f"AST validation failed: {ast_errors[0]}", validation_type="ast"
            )

        self.law_analyser = LawAnalyser(self.ast)
        self.target_analyser = TargetAnalyser(self.ast)

    def _simulate_law_events(
        self, law_data: Dict[str, Any], dict_map: Dict[str, str]
    ) -> List[Tuple[datetime, str, str, str]]:
        """
        Simulate events for a single law.

        Args:
            law_data: Law data dictionary
            dict_map: Dictionary mapping event names to descriptions

        Returns:
            List of simulated events as tuples (start_time, law_name, event_description, end_time)
        """
        if "group" not in law_data or "date" not in law_data or "time" not in law_data:
            return []

        law_name = law_data["name"]
        date = law_data["date"]
        time = law_data["time"]
        start_date = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        current_time = start_date

        simulated_events = []
        group_m = law_data["group"]

        event_descriptions = {
            item["name"]: dict_map.get(
                item["name"], item.get("description", item["name"])
            )
            for item in law_data.get("dictionnary", [])
        }

        for index, event in enumerate(group_m):
            event_id = event["name"]
            event_description = event_descriptions.get(event_id, event_id)

            chronocoherence = point_to_minutes(event["chronocoherence"])
            end_date_event = current_time + timedelta(minutes=chronocoherence)

            simulated_events.append(
                (current_time, law_name, event_description, end_date_event)
            )

            current_time = end_date_event

            if index < len(group_m) - 1:
                chronodispersal = point_to_minutes(event["chronodispersal"])
                current_time += timedelta(minutes=chronodispersal)

        return simulated_events

    def target_description(self, target_name: str) -> Dict[str, Any]:
        """
        Analyse les lois associées à un target spécifique en garantissant une séquence
        chronologique en simulant et triant les événements de toutes les lois liées,
        et retourne le résultat de law_description_data.
        """

        if target_name not in self.target_analyser.targets:
            raise ZenithAnalyserError(
                f"Target '{target_name}' not found", target_name=target_name
            )

        # 1. Extraction des lois transformées (avec dictionnaires mis à jour)
        transformed_laws = self.target_analyser.extract_laws_for_target(target_name)

        if not transformed_laws:
            raise ZenithAnalyserError(
                f"Target '{target_name}' has no direct or descendant laws to analyze.",
                target_name=target_name,
            )

        # 2. Préparation du dictionnaire des descriptions d'événements finales (du target)
        target_dict = self.target_analyser.targets[target_name].get("dictionnary", [])
        merged_dictionnary_map = {
            item["name"]: item["description"] for item in target_dict
        }

        # 3. Simulation et collecte de TOUS les événements triés
        all_simulated_events = []

        for law_name, law_data in transformed_laws.items():
            simulated_events = self._simulate_law_events(
                law_data, merged_dictionnary_map
            )
            all_simulated_events.extend(simulated_events)

        # Trier TOUS les événements simulés par date de début
        all_simulated_events.sort(key=lambda x: x[0])

        if not all_simulated_events:
            raise ZenithAnalyserError(
                f"No simulatible events found for Target '{target_name}'.",
                target_name=target_name,
            )

        # 4. Créer la structure "loi fusionnée" (merged_law_data)

        # Trouver la loi de base (celle qui commence le plus tôt)
        base_law_name = all_simulated_events[0][
            1
        ]  # Nom de la loi de l'événement le plus précoce
        base_law_data = transformed_laws[base_law_name]

        merged_law_data = copy.deepcopy(base_law_data)
        merged_law_data["name"] = target_name

        # Mettre à jour la date de début de la loi fusionnée
        first_event_start_time = all_simulated_events[0][0]
        merged_law_data["date"] = first_event_start_time.strftime("%Y-%m-%d")
        merged_law_data["time"] = first_event_start_time.strftime("%H:%M")

        # 5. Reconstruire le 'group' et le 'dictionnary' factices pour l'analyse métrique

        new_group = []

        for i, (start_time, _, event_desc, end_time) in enumerate(all_simulated_events):

            # 5.1. Calculer Cohérence (durée de l'événement)
            coherence_minutes = int((end_time - start_time).total_seconds() / 60)

            # 5.2. Calculer Dispersal (temps entre la fin de cet événement et le début du suivant)
            dispersal_minutes = 0
            if i < len(all_simulated_events) - 1:
                next_start_time = all_simulated_events[i + 1][0]
                dispersal_minutes = int(
                    (next_start_time - end_time).total_seconds() / 60
                )

            # Pour que law_description_data fonctionne, nous devons utiliser le format de "point" pour chronocoherence/chronodispersal
            # Comme nous travaillons avec des minutes réelles, nous les convertissons en un format simple de type "nombre"
            # (qui est accepté par point_to_minutes car il est traité comme X.0.0.0.0 ou 0.X.0.0.0)
            coherence_str = (
                minutes_to_point(coherence_minutes) if coherence_minutes > 0 else "0"
            )
            dispersal_str = minutes_to_point(max(0, dispersal_minutes))

            new_group.append(
                {
                    # Utiliser la description comme 'name' (ID) pour l'analyse métrique
                    "name": event_desc,
                    "chronocoherence": coherence_str,
                    "chronodispersal": dispersal_str,
                }
            )

        # 5.3. Mettre à jour les données fusionnées
        merged_law_data["group"] = new_group

        # 5.4. Reconstruire le dictionnaire pour mapper la 'name' (qui est la description) à elle-même
        # C'est nécessaire pour que la boucle de substitution de law_description_data ne casse pas l'analyse
        final_dictionnary = []
        unique_event_names = sorted(list(set(event["name"] for event in new_group)))
        for name in unique_event_names:
            final_dictionnary.append({"name": name, "description": name})

        merged_law_data["dictionnary"] = final_dictionnary

        # 6. Appel final
        return self.law_description_data(target_name, merged_law_data)

    def law_description(self, name: str, population: int = 0) -> Dict[str, Any]:
        """
        Get a detailed description of a law.

        Args:
            name: Law name
            population: Population level for dictionary inheritance

        Returns:
            Detailed law description

        Raises:
            ZenithAnalyserError: If law not found or invalid
        """
        # Get law data with appropriate population
        law_data = None

        if population > 0:
            transformed_laws = self.target_analyser.extract_laws_population(population)
            if name in transformed_laws:
                law_data = transformed_laws[name]

        if not law_data:
            law_data = self.law_analyser.get_law(name)
            if not law_data:
                raise ZenithAnalyserError(f"Law '{name}' not found", law_name=name)

        return self.law_description_data(name, law_data)

    def law_description_data(
        self, name: str, law_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate description from law data.

        Args:
            name: Law name
            law_data: Law data dictionary

        Returns:
            Detailed law description

        Raises:
            ZenithAnalyserError: If law data is invalid
        """
        # Validate law data
        required = ["date", "time", "period", "dictionnary", "group"]
        for field in required:
            if field not in law_data:
                raise ZenithAnalyserError(
                    f"Law data missing required field: {field}", law_name=name
                )

        # Prepare group with descriptions
        group = copy.deepcopy(law_data["group"])

        # Map event names to descriptions
        event_descriptions = {}
        for entry in law_data["dictionnary"]:
            entry_name = entry.get("name")
            entry_desc = entry.get("description", "")

            if entry_desc:
                event_descriptions[entry_name] = entry_desc
            else:
                event_descriptions[entry_name] = entry_name

        # Replace event names with descriptions in group
        for event in group:
            event_name = event.get("name", "")
            if event_name in event_descriptions:
                event["name"] = event_descriptions[event_name]
            elif event_name:
                # Keep original name if no description found
                event["name"] = event_name

        # Calculate totals
        total_coherence = 0
        total_dispersal = 0

        for i, event in enumerate(group):
            try:
                coherence = point_to_minutes(event["chronocoherence"])
                total_coherence += coherence

                if i < len(group) - 1:
                    dispersal = point_to_minutes(event["chronodispersal"])
                    total_dispersal += dispersal
            except ZenithTimeError as e:
                raise ZenithAnalyserError(
                    f"Invalid time in event {i}: {str(e)}", law_name=name
                ) from e

        total_duration = total_coherence + total_dispersal

        # Parse start date/time
        try:
            start_dt = parse_datetime(law_data["date"], law_data["time"])
        except ZenithTimeError as e:
            raise ZenithAnalyserError(
                f"Invalid start date/time: {str(e)}", law_name=name
            ) from e

        # Calculate period
        try:
            period_minutes = point_to_minutes(law_data["period"])
        except ZenithTimeError as e:
            raise ZenithAnalyserError(f"Invalid period: {str(e)}", law_name=name) from e

        # Calculate end date
        if total_duration >= period_minutes:
            end_dt = add_minutes_to_datetime(start_dt, total_duration)
        else:
            end_dt = add_minutes_to_datetime(start_dt, period_minutes)

        # Generate simulation
        simulation = []
        current_time = start_dt

        for i, event in enumerate(group):
            try:
                coherence = point_to_minutes(event["chronocoherence"])
                event_end = add_minutes_to_datetime(current_time, coherence)

                simulation.append(
                    {
                        "event_name": event["name"],
                        "start": format_datetime(current_time),
                        "end": format_datetime(event_end),
                        "duration_minutes": int(coherence),
                    }
                )

                current_time = event_end

                if i < len(group) - 1:
                    dispersal = point_to_minutes(event["chronodispersal"])
                    current_time = add_minutes_to_datetime(current_time, dispersal)
            except ZenithTimeError as e:
                raise ZenithAnalyserError(
                    f"Error in event {i} simulation: {str(e)}", law_name=name
                ) from e

        # Calculate event metrics
        event_metrics = {}
        for event in group:
            event_name = event["name"]
            if event_name not in event_metrics:
                event_metrics[event_name] = {
                    "count": 0,
                    "total_coherence": 0,
                    "total_dispersal": 0,
                }

            metrics = event_metrics[event_name]
            metrics["count"] += 1
            metrics["total_coherence"] += point_to_minutes(event["chronocoherence"])

            # Dispersal is for the event that comes before the gap
            # We'll handle this differently in the loop

        # Calculate dispersals
        for i, event in enumerate(group):
            if i < len(group) - 1:
                event_name = event["name"]
                if event_name in event_metrics:
                    dispersal = point_to_minutes(event["chronodispersal"])
                    event_metrics[event_name]["total_dispersal"] += dispersal

        # Format event metrics
        formatted_metrics = []
        for event_name, metrics in event_metrics.items():
            count = metrics["count"]
            formatted_metrics.append(
                {
                    "name": event_name,
                    "count": count,
                    "total_coherence_minutes": int(metrics["total_coherence"]),
                    "total_dispersal_minutes": int(metrics["total_dispersal"]),
                    "mean_coherence_minutes": int(
                        metrics["total_coherence"] / count if count > 0 else 0
                    ),
                    "mean_dispersal_minutes": int(
                        metrics["total_dispersal"] / count if count > 0 else 0
                    ),
                }
            )

        # Calculate dispersion (time between occurrences of same event)
        dispersion_metrics = {}
        event_positions = {}

        for i, event in enumerate(group):
            event_name = event["name"]
            if event_name not in event_positions:
                event_positions[event_name] = []
            event_positions[event_name].append(i)

        for event_name, positions in event_positions.items():
            if len(positions) > 1:
                dispersions = []
                for j in range(len(positions) - 1):
                    start_pos = positions[j]
                    end_pos = positions[j + 1]

                    # Calculate total time between occurrences
                    dispersion_time = 0
                    for k in range(start_pos, end_pos):
                        dispersion_time += point_to_minutes(group[k]["chronocoherence"])
                        if k < len(group) - 1:
                            dispersion_time += point_to_minutes(
                                group[k]["chronodispersal"]
                            )

                    dispersions.append(dispersion_time)

                dispersion_metrics[event_name] = {
                    "mean_dispersion_minutes": int(
                        sum(dispersions) / len(dispersions) if dispersions else 0
                    ),
                    "dispersion_count": len(dispersions),
                }

        formatted_dispersion = [
            {
                "name": event_name,
                "mean_dispersion_minutes": int(metrics["mean_dispersion_minutes"]),
                "dispersion_count": metrics["dispersion_count"],
            }
            for event_name, metrics in dispersion_metrics.items()
        ]

        # Return complete description
        return {
            "name": name,
            "start_date": law_data["date"],
            "start_time": law_data["time"],
            "start_datetime": format_datetime(start_dt),
            "period": law_data["period"],
            "period_minutes": period_minutes,
            "end_datetime": format_datetime(end_dt),
            "total_duration_minutes": total_duration,
            "coherence_total_minutes": total_coherence,
            "dispersal_total_minutes": total_dispersal,
            "event_count": len(group),
            "unique_event_count": len(event_metrics),
            "simulation": simulation,
            "event_metrics": formatted_metrics,
            "dispersion_metrics": formatted_dispersion,
            "mean_coherence_all_minutes": int(
                total_coherence / len(group) if group else 0
            ),
            "mean_dispersal_all_minutes": int(
                total_dispersal / (len(group) - 1) if len(group) > 1 else 0
            ),
            "events": list(event_metrics.keys()),
        }

    def population_description(self, population: int = -1) -> Dict[str, Any]:
        """
        Get description for a population level.

        Args:
            population: Population level (-1 for max population)

        Returns:
            Population description
        """
        if population == -1:
            population = self.target_analyser.get_max_generation()

        # Get laws for this population
        population_laws = {}

        if population > 0:
            # Get targets at this generation
            targets = self.target_analyser.get_targets_by_generation(population)

            for target_name in targets:
                target_laws = self.target_analyser.extract_laws_for_target(target_name)
                for law_name, law_data in target_laws.items():
                    if law_name not in population_laws:
                        population_laws[law_name] = law_data
        else:
            # Population 0 means all laws not in any target
            all_target_laws = set()
            for target in self.target_analyser.targets.values():
                all_target_laws.update(target["all_descendants_laws"])

            for law_name, law_data in self.law_analyser.laws.items():
                if law_name not in all_target_laws:
                    population_laws[law_name] = law_data

        if not population_laws:
            raise ZenithAnalyserError(f"No laws found for population {population}")

        # Analyze each law
        law_descriptions = {}
        all_events = []

        for law_name, law_data in population_laws.items():
            try:
                law_desc = self.law_description_data(law_name, law_data)
                law_descriptions[law_name] = law_desc

                # Collect events
                for event in law_desc.get("simulation", []):
                    all_events.append(
                        {
                            "law_name": law_name,
                            "event_name": event["event_name"],
                            "start_datetime": event["start"],
                            "end_datetime": event["end"],
                            "duration_minutes": int(event["duration_minutes"]),
                        }
                    )
            except ZenithAnalyserError as e:
                law_descriptions[law_name] = {"error": str(e)}

        # Sort all events
        all_events.sort(
            key=lambda x: parse_datetime(
                x["start_datetime"]["date"], x["start_datetime"]["time"]
            )
        )

        # Calculate population statistics
        total_duration = sum(
            desc.get("total_duration_minutes", 0)
            for desc in law_descriptions.values()
            if isinstance(desc, dict) and "error" not in desc
        )

        valid_descriptions = [
            desc
            for desc in law_descriptions.values()
            if isinstance(desc, dict) and "error" not in desc
        ]

        population_stats = {
            "population_level": population,
            "total_laws": len(population_laws),
            "valid_laws": len(valid_descriptions),
            "total_events": len(all_events),
            "total_duration_minutes": total_duration,
            "average_law_duration_minutes": int(
                total_duration / len(valid_descriptions) if valid_descriptions else 0
            ),
            "start_range": all_events[0]["start_datetime"] if all_events else None,
            "end_range": all_events[-1]["end_datetime"] if all_events else None,
        }

        # Event statistics across population
        event_stats = {}
        for event in all_events:
            event_name = event["event_name"]
            if event_name not in event_stats:
                event_stats[event_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "laws": set(),
                }

            stats = event_stats[event_name]
            stats["count"] += 1
            stats["total_duration"] += event["duration_minutes"]
            stats["laws"].add(event["law_name"])

        formatted_event_stats = []
        for event_name, stats in event_stats.items():
            formatted_event_stats.append(
                {
                    "name": event_name,
                    "count": stats["count"],
                    "total_duration_minutes": stats["total_duration"],
                    "mean_duration_minutes": int(
                        stats["total_duration"] / stats["count"]
                        if stats["count"] > 0
                        else 0
                    ),
                    "law_count": len(stats["laws"]),
                    "laws": list(stats["laws"]),
                }
            )

        return {
            "population_stats": population_stats,
            "law_descriptions": law_descriptions,
            "all_events": all_events,
            "event_statistics": formatted_event_stats,
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_corpus(self) -> Dict[str, Any]:
        """
        Perform complete corpus analysis.

        Returns:
            Complete corpus analysis
        """
        # Get AST summary
        ast_summary = self.parser.get_ast_summary(self.ast)

        # Get all laws with validation
        all_laws = {}
        for law_name in self.law_analyser.get_law_names():
            try:
                all_laws[law_name] = self.law_description(law_name)
            except ZenithAnalyserError as e:
                all_laws[law_name] = {"error": str(e)}

        # Get all targets with hierarchy
        all_targets = {}
        for target_name in self.target_analyser.get_target_names():
            try:
                all_targets[target_name] = self.target_analyser.get_target_hierarchy(
                    target_name
                )
            except ZenithAnalyserError as e:
                all_targets[target_name] = {"error": str(e)}

        # Calculate corpus statistics
        total_events = 0
        total_duration = 0

        for law_data in all_laws.values():
            if isinstance(law_data, dict) and "error" not in law_data:
                total_events += law_data.get("event_count", 0)
                total_duration += law_data.get("total_duration_minutes", 0)

        corpus_stats = {
            "total_laws": len(all_laws),
            "total_targets": len(all_targets),
            "total_events": total_events,
            "total_duration_minutes": total_duration,
            "max_nesting": ast_summary.get("max_nesting", 0),
            "analysis_timestamp": datetime.now().isoformat(),
        }

        return {
            "corpus_statistics": corpus_stats,
            "ast_summary": ast_summary,
            "laws": all_laws,
            "targets": all_targets,
            "validation": {
                "lexer": len(self.validator.validate_tokens(self.tokens)) == 0,
                "parser": len(self.parser_errors) == 0,
                "ast": len(self.validator.validate_ast(self.ast)) == 0,
            },
        }

    def export_json(self, filepath: str) -> None:
        """
        Export complete analysis to JSON file.

        Args:
            filepath: Path to output JSON file

        Raises:
            IOError: If file cannot be written
        """
        analysis = self.analyze_corpus()

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, default=str)
        except (IOError, OSError) as e:
            raise IOError(f"Failed to write JSON file: {str(e)}") from e

    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information about the analysis.

        Returns:
            Debug information
        """
        return {
            "code_length": len(self.code),
            "token_count": len(self.tokens),
            "ast_size": self.validator._calculate_ast_size(self.ast),
            "law_count": len(self.law_analyser.laws),
            "target_count": len(self.target_analyser.targets),
            "parser_errors": self.parser_errors,
            "lexer_debug": self.lexer.debug_tokens(),
            "timestamp": datetime.now().isoformat(),
        }
