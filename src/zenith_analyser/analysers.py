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
import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Set, Union

from .utils import (
    point_to_minutes,
    minutes_to_point,
    parse_datetime,
    format_datetime,
    calculate_duration,
    add_minutes_to_datetime,
    deep_merge_dicts,
    safe_get
)
from .exceptions import (
    ZenithAnalyserError,
    ZenithTimeError,
    ZenithValidationError
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
                if element.get('type') == "law":
                    self._extract_law_data(element, data_laws)
                elif element.get('type') == 'target':
                    contents = element.get('contents', {})
                    blocks = contents.get('blocks', [])
                    _traverse(blocks)
        
        _traverse(ast.get('elements', []))
        return data_laws
    
    def _extract_law_data(self, law_node: Dict[str, Any], data_laws: Dict[str, Dict[str, Any]]) -> None:
        """
        Extract data from a single law node.
        
        Args:
            law_node: Law AST node
            data_laws: Dictionary to populate
        """
        name = law_node.get('name')
        if not name:
            return
        
        contents = law_node.get('contents', {})
        start_date = contents.get('start_date', {})
        
        data_laws[name] = {
            "name": name,
            "date": start_date.get('date'),
            "time": start_date.get('time'),
            "period": contents.get('period'),
            "dictionnary": copy.deepcopy(contents.get('events', [])),
            "group": copy.deepcopy(contents.get('group', [])),
            "source_node": law_node  # Keep reference for debugging
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
        required = ['date', 'time', 'period', 'dictionnary', 'group']
        for field in required:
            if not law.get(field):
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return errors
        
        # Validate date/time
        try:
            parse_datetime(law['date'], law['time'])
        except ZenithTimeError as e:
            errors.append(str(e))
        
        # Validate period
        try:
            point_to_minutes(law['period'])
        except ZenithTimeError as e:
            errors.append(f"Invalid period: {str(e)}")
        
        # Validate dictionnary
        if not isinstance(law['dictionnary'], list):
            errors.append("Dictionnary must be a list")
        else:
            seen_names = set()
            for i, entry in enumerate(law['dictionnary']):
                if not isinstance(entry, dict):
                    errors.append(f"Dictionnary entry {i} must be a dictionary")
                    continue
                
                entry_name = entry.get('name')
                if not entry_name:
                    errors.append(f"Dictionnary entry {i} missing name")
                    continue
                
                if entry_name in seen_names:
                    errors.append(f"Duplicate dictionnary entry: {entry_name}")
                else:
                    seen_names.add(entry_name)
        
        # Validate group
        if not isinstance(law['group'], list):
            errors.append("Group must be a list")
        else:
            for i, event in enumerate(law['group']):
                if not isinstance(event, dict):
                    errors.append(f"Group event {i} must be a dictionary")
                    continue
                
                required_fields = ['name', 'chronocoherence', 'chronodispersal']
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
        
        def _traverse(elements: List[Dict[str, Any]], current_path: List[str] = None) -> None:
            if current_path is None:
                current_path = []
            
            for element in elements:
                if element.get('type') == 'target':
                    self._extract_target_data(element, data_targets, current_path)
                    
                    # Recurse into blocks
                    contents = element.get('contents', {})
                    blocks = contents.get('blocks', [])
                    new_path = current_path + [element['name']]
                    _traverse(blocks, new_path)
        
        _traverse(ast.get('elements', []))
        return data_targets
    
    def _extract_target_data(self, target_node: Dict[str, Any], 
                           data_targets: Dict[str, Dict[str, Any]], 
                           current_path: List[str]) -> None:
        """
        Extract data from a single target node.
        
        Args:
            target_node: Target AST node
            data_targets: Dictionary to populate
            current_path: Current path in hierarchy
        """
        name = target_node.get('name')
        if not name:
            return
        
        contents = target_node.get('contents', {})
        
        data_targets[name] = {
            "name": name,
            "key": contents.get('key', ''),
            "dictionnary": copy.deepcopy(contents.get('dictionnary', [])),
            "direct_laws": [],
            "direct_targets": [],
            "all_descendants_laws": set(),
            "all_descendants_targets": set(),
            "path": current_path + [name],
            "depth": len(current_path) + 1,
            "source_node": target_node  # Keep reference for debugging
        }
        
        # Extract direct laws and targets from blocks
        blocks = contents.get('blocks', [])
        for block in blocks:
            if block.get('type') == 'law':
                law_name = block.get('name')
                if law_name:
                    data_targets[name]['direct_laws'].append(law_name)
            elif block.get('type') == 'target':
                target_name = block.get('name')
                if target_name:
                    data_targets[name]['direct_targets'].append(target_name)
    
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
            if (target['all_descendants_laws'] and target['all_descendants_targets'] and
                len(target['all_descendants_laws']) > 0 and len(target['all_descendants_targets']) > 0):
                return target['all_descendants_laws'], target['all_descendants_targets']
            
            # Calculate descendants
            descendant_laws = set(target['direct_laws'])
            descendant_targets = set(target['direct_targets'])
            
            for child_name in target['direct_targets']:
                child_laws, child_targets = _get_descendants(child_name)
                descendant_laws.update(child_laws)
                descendant_targets.update(child_targets)
            
            # Cache results
            target['all_descendants_laws'] = descendant_laws
            target['all_descendants_targets'] = descendant_targets
            
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
            "path": target['path'],
            "depth": target['depth'],
            "parent": target['path'][-2] if len(target['path']) > 1 else None,
            "children": target['direct_targets'],
            "descendants": list(target['all_descendants_targets']),
            "direct_laws": target['direct_laws'],
            "descendant_laws": list(target['all_descendants_laws'])
        }
    
    def extract_laws_for_target(self, target_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract laws for a specific target with dictionary inheritance.
        
        Args:
            target_name: Target name
        
        Returns:
            Dictionary of laws with inherited dictionaries
        
        Raises:
            ZenithAnalyserError: If target not found
        """
        if target_name not in self.targets:
            raise ZenithAnalyserError(f"Target '{target_name}' not found", target_name=target_name)
        
        target = self.targets[target_name]
        
        # Get all descendant laws
        all_law_names = target['all_descendants_laws']
        all_laws = {}
        
        # Get base laws
        base_laws = self.law_analyser.laws
        
        # Apply dictionary inheritance
        for law_name in all_law_names:
            if law_name in base_laws:
                law_data = copy.deepcopy(base_laws[law_name])
                
                # Apply dictionary from this target
                self._apply_dictionary(law_data, target['dictionnary'])
                
                # Apply dictionaries from parent targets
                current_target = target
                while current_target['path']:
                    parent_path = current_target['path'][:-1]
                    if parent_path:
                        # Find parent target
                        for t_name, t_data in self.targets.items():
                            if t_data['path'] == parent_path:
                                self._apply_dictionary(law_data, t_data['dictionnary'])
                                current_target = t_data
                                break
                    else:
                        break
                
                all_laws[law_name] = law_data
        
        return all_laws
    
    def _apply_dictionary(self, law_data: Dict[str, Any], dictionary: List[Dict[str, Any]]) -> None:
        """
        Apply dictionary entries to a law's events.
        
        Args:
            law_data: Law data to modify
            dictionary: Dictionary to apply
        """
        if not dictionary or 'dictionnary' not in law_data:
            return
        
        # Create mapping from dictionary
        dict_map = {}
        for entry in dictionary:
            entry_name = entry.get('name')
            entry_desc = entry.get('description')
            entry_index = entry.get('index')
            
            if entry_name and entry_desc:
                if entry_index:
                    dict_map[entry_index] = entry_desc
                else:
                    dict_map[entry_name] = entry_desc
        
        # Apply to law's dictionnary
        for event in law_data['dictionnary']:
            event_name = event.get('name')
            event_index = event.get('index')
            
            if event_index and event_index in dict_map:
                event['description'] = dict_map[event_index]
            elif event_name and event_name in dict_map:
                event['description'] = dict_map[event_name]
    
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
            if target['depth'] == generation:
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
            if target['depth'] > max_depth:
                max_depth = target['depth']
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
            if target.get('key') == key:
                result.append(name)
        return result


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
                validation_type="tokens"
            )
        
        self.parser = Parser(self.tokens)
        self.ast, self.parser_errors = self.parser.parse()
        
        if self.parser_errors:
            raise ZenithValidationError(
                f"Parsing failed: {self.parser_errors[0]}",
                validation_type="parsing"
            )
        
        ast_errors = self.validator.validate_ast(self.ast)
        if ast_errors:
            raise ZenithValidationError(
                f"AST validation failed: {ast_errors[0]}",
                validation_type="ast"
            )
        
        self.law_analyser = LawAnalyser(self.ast)
        self.target_analyser = TargetAnalyser(self.ast)
    
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
    
    def law_description_data(self, name: str, law_data: Dict[str, Any]) -> Dict[str, Any]:
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
        required = ['date', 'time', 'period', 'dictionnary', 'group']
        for field in required:
            if field not in law_data:
                raise ZenithAnalyserError(
                    f"Law data missing required field: {field}",
                    law_name=name
                )
        
        # Prepare group with descriptions
        group = copy.deepcopy(law_data['group'])
        
        # Map event names to descriptions
        event_descriptions = {}
        for entry in law_data['dictionnary']:
            entry_name = entry.get('name')
            entry_desc = entry.get('description', '')
            entry_index = entry.get('index')
            
            if entry_index:
                event_descriptions[entry_index] = entry_desc
            elif entry_name:
                event_descriptions[entry_name] = entry_desc
        
        # Replace event names with descriptions in group
        for event in group:
            event_name = event.get('name', '')
            if event_name in event_descriptions:
                event['name'] = event_descriptions[event_name]
            elif event_name:
                # Keep original name if no description found
                event['name'] = event_name
        
        # Calculate totals
        total_coherence = 0
        total_dispersal = 0
        
        for i, event in enumerate(group):
            try:
                coherence = point_to_minutes(event['chronocoherence'])
                total_coherence += coherence
                
                if i < len(group) - 1:
                    dispersal = point_to_minutes(event['chronodispersal'])
                    total_dispersal += dispersal
            except ZenithTimeError as e:
                raise ZenithAnalyserError(
                    f"Invalid time in event {i}: {str(e)}",
                    law_name=name
                ) from e
        
        total_duration = total_coherence + total_dispersal
        
        # Parse start date/time
        try:
            start_dt = parse_datetime(law_data['date'], law_data['time'])
        except ZenithTimeError as e:
            raise ZenithAnalyserError(
                f"Invalid start date/time: {str(e)}",
                law_name=name
            ) from e
        
        # Calculate period
        try:
            period_minutes = point_to_minutes(law_data['period'])
        except ZenithTimeError as e:
            raise ZenithAnalyserError(
                f"Invalid period: {str(e)}",
                law_name=name
            ) from e
        
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
                coherence = point_to_minutes(event['chronocoherence'])
                event_end = add_minutes_to_datetime(current_time, coherence)
                
                simulation.append({
                    "event_name": event['name'],
                    "start": format_datetime(current_time),
                    "end": format_datetime(event_end),
                    "duration_minutes": coherence
                })
                
                current_time = event_end
                
                if i < len(group) - 1:
                    dispersal = point_to_minutes(event['chronodispersal'])
                    current_time = add_minutes_to_datetime(current_time, dispersal)
            except ZenithTimeError as e:
                raise ZenithAnalyserError(
                    f"Error in event {i} simulation: {str(e)}",
                    law_name=name
                ) from e
        
        # Calculate event metrics
        event_metrics = {}
        for event in group:
            event_name = event['name']
            if event_name not in event_metrics:
                event_metrics[event_name] = {
                    "count": 0,
                    "total_coherence": 0,
                    "total_dispersal": 0
                }
            
            metrics = event_metrics[event_name]
            metrics["count"] += 1
            metrics["total_coherence"] += point_to_minutes(event['chronocoherence'])
            
            # Dispersal is for the event that comes before the gap
            # We'll handle this differently in the loop
        
        # Calculate dispersals
        for i, event in enumerate(group):
            if i < len(group) - 1:
                event_name = event['name']
                if event_name in event_metrics:
                    dispersal = point_to_minutes(event['chronodispersal'])
                    event_metrics[event_name]["total_dispersal"] += dispersal
        
        # Format event metrics
        formatted_metrics = []
        for event_name, metrics in event_metrics.items():
            count = metrics["count"]
            formatted_metrics.append({
                "name": event_name,
                "count": count,
                "total_coherence_minutes": metrics["total_coherence"],
                "total_dispersal_minutes": metrics["total_dispersal"],
                "mean_coherence_minutes": metrics["total_coherence"] / count if count > 0 else 0,
                "mean_dispersal_minutes": metrics["total_dispersal"] / count if count > 0 else 0
            })
        
        # Calculate dispersion (time between occurrences of same event)
        dispersion_metrics = {}
        event_positions = {}
        
        for i, event in enumerate(group):
            event_name = event['name']
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
                        dispersion_time += point_to_minutes(group[k]['chronocoherence'])
                        if k < len(group) - 1:
                            dispersion_time += point_to_minutes(group[k]['chronodispersal'])
                    
                    dispersions.append(dispersion_time)
                
                dispersion_metrics[event_name] = {
                    "mean_dispersion_minutes": sum(dispersions) / len(dispersions) if dispersions else 0,
                    "dispersion_count": len(dispersions)
                }
        
        formatted_dispersion = [
            {
                "name": event_name,
                "mean_dispersion_minutes": metrics["mean_dispersion_minutes"],
                "dispersion_count": metrics["dispersion_count"]
            }
            for event_name, metrics in dispersion_metrics.items()
        ]
        
        # Return complete description
        return {
            "name": name,
            "start_date": law_data['date'],
            "start_time": law_data['time'],
            "start_datetime": format_datetime(start_dt),
            "period": law_data['period'],
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
            "mean_coherence_all_minutes": total_coherence / len(group) if group else 0,
            "mean_dispersal_all_minutes": total_dispersal / (len(group) - 1) if len(group) > 1 else 0,
            "events": list(event_metrics.keys())
        }
    
    def target_description(self, target_name: str) -> Dict[str, Any]:
        """
        Get a detailed description of a target and its laws.
        
        Args:
            target_name: Target name
        
        Returns:
            Detailed target description
        
        Raises:
            ZenithAnalyserError: If target not found
        """
        if target_name not in self.target_analyser.targets:
            raise ZenithAnalyserError(f"Target '{target_name}' not found", target_name=target_name)
        
        # Get all laws for this target
        target_laws = self.target_analyser.extract_laws_for_target(target_name)
        
        if not target_laws:
            raise ZenithAnalyserError(
                f"Target '{target_name}' has no laws to analyze",
                target_name=target_name
            )
        
        # Get target data
        target_data = self.target_analyser.get_target(target_name)
        
        # Simulate all events from all laws
        all_events = []
        
        for law_name, law_data in target_laws.items():
            law_desc = self.law_description_data(law_name, law_data)
            
            for event in law_desc.get('simulation', []):
                all_events.append({
                    "law_name": law_name,
                    "event_name": event["event_name"],
                    "start_datetime": event["start"],
                    "end_datetime": event["end"],
                    "duration_minutes": event["duration_minutes"]
                })
        
        # Sort events by start time
        all_events.sort(key=lambda x: parse_datetime(
            x["start_datetime"]["date"],
            x["start_datetime"]["time"]
        ))
        
        # Create merged law data for analysis
        if not all_events:
            raise ZenithAnalyserError(
                f"No events found for target '{target_name}'",
                target_name=target_name
            )
        
        # Use first event as reference
        first_event = all_events[0]
        start_dt = parse_datetime(
            first_event["start_datetime"]["date"],
            first_event["start_datetime"]["time"]
        )
        
        # Create merged group
        merged_group = []
        
        for i, event in enumerate(all_events):
            event_dt = parse_datetime(
                event["start_datetime"]["date"],
                event["start_datetime"]["time"]
            )
            event_end_dt = parse_datetime(
                event["end_datetime"]["date"],
                event["end_datetime"]["time"]
            )
            
            # Calculate coherence (event duration)
            coherence_minutes = calculate_duration(event_dt, event_end_dt)
            
            # Calculate dispersal (gap until next event)
            dispersal_minutes = 0
            if i < len(all_events) - 1:
                next_event = all_events[i + 1]
                next_event_dt = parse_datetime(
                    next_event["start_datetime"]["date"],
                    next_event["start_datetime"]["time"]
                )
                dispersal_minutes = calculate_duration(event_end_dt, next_event_dt)
            
            merged_group.append({
                "name": event["event_name"],
                "chronocoherence": minutes_to_point(coherence_minutes),
                "chronodispersal": minutes_to_point(dispersal_minutes)
            })
        
        # Create merged law data
        merged_law_data = {
            "name": f"merged_{target_name}",
            "date": first_event["start_datetime"]["date"],
            "time": first_event["start_datetime"]["time"],
            "period": minutes_to_point(
                calculate_duration(
                    start_dt,
                    parse_datetime(
                        all_events[-1]["end_datetime"]["date"],
                        all_events[-1]["end_datetime"]["time"]
                    )
                )
            ),
            "dictionnary": [
                {"name": event["event_name"], "description": event["event_name"]}
                for event in all_events
            ],
            "group": merged_group
        }
        
        # Analyze merged law
        return self.law_description_data(target_name, merged_law_data)
    
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
                all_target_laws.update(target['all_descendants_laws'])
            
            for law_name, law_data in self.law_analyser.laws.items():
                if law_name not in all_target_laws:
                    population_laws[law_name] = law_data
        
        if not population_laws:
            raise ZenithAnalyserError(
                f"No laws found for population {population}"
            )
        
        # Analyze each law
        law_descriptions = {}
        all_events = []
        
        for law_name, law_data in population_laws.items():
            try:
                law_desc = self.law_description_data(law_name, law_data)
                law_descriptions[law_name] = law_desc
                
                # Collect events
                for event in law_desc.get('simulation', []):
                    all_events.append({
                        "law_name": law_name,
                        "event_name": event["event_name"],
                        "start_datetime": event["start"],
                        "end_datetime": event["end"],
                        "duration_minutes": event["duration_minutes"]
                    })
            except ZenithAnalyserError as e:
                law_descriptions[law_name] = {"error": str(e)}
        
        # Sort all events
        all_events.sort(key=lambda x: parse_datetime(
            x["start_datetime"]["date"],
            x["start_datetime"]["time"]
        ))
        
        # Calculate population statistics
        total_duration = sum(
            desc.get('total_duration_minutes', 0)
            for desc in law_descriptions.values()
            if isinstance(desc, dict) and 'error' not in desc
        )
        
        valid_descriptions = [
            desc for desc in law_descriptions.values()
            if isinstance(desc, dict) and 'error' not in desc
        ]
        
        population_stats = {
            "population_level": population,
            "total_laws": len(population_laws),
            "valid_laws": len(valid_descriptions),
            "total_events": len(all_events),
            "total_duration_minutes": total_duration,
            "average_law_duration_minutes": total_duration / len(valid_descriptions) if valid_descriptions else 0,
            "start_range": all_events[0]["start_datetime"] if all_events else None,
            "end_range": all_events[-1]["end_datetime"] if all_events else None
        }
        
        # Event statistics across population
        event_stats = {}
        for event in all_events:
            event_name = event["event_name"]
            if event_name not in event_stats:
                event_stats[event_name] = {
                    "count": 0,
                    "total_duration": 0,
                    "laws": set()
                }
            
            stats = event_stats[event_name]
            stats["count"] += 1
            stats["total_duration"] += event["duration_minutes"]
            stats["laws"].add(event["law_name"])
        
        formatted_event_stats = []
        for event_name, stats in event_stats.items():
            formatted_event_stats.append({
                "name": event_name,
                "count": stats["count"],
                "total_duration_minutes": stats["total_duration"],
                "mean_duration_minutes": stats["total_duration"] / stats["count"] if stats["count"] > 0 else 0,
                "law_count": len(stats["laws"]),
                "laws": list(stats["laws"])
            })
        
        return {
            "population_stats": population_stats,
            "law_descriptions": law_descriptions,
            "all_events": all_events,
            "event_statistics": formatted_event_stats,
            "timestamp": datetime.now().isoformat()
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
                all_targets[target_name] = self.target_analyser.get_target_hierarchy(target_name)
            except ZenithAnalyserError as e:
                all_targets[target_name] = {"error": str(e)}
        
        # Calculate corpus statistics
        total_events = 0
        total_duration = 0
        
        for law_data in all_laws.values():
            if isinstance(law_data, dict) and 'error' not in law_data:
                total_events += law_data.get('event_count', 0)
                total_duration += law_data.get('total_duration_minutes', 0)
        
        corpus_stats = {
            "total_laws": len(all_laws),
            "total_targets": len(all_targets),
            "total_events": total_events,
            "total_duration_minutes": total_duration,
            "max_nesting": ast_summary.get('max_nesting', 0),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return {
            "corpus_statistics": corpus_stats,
            "ast_summary": ast_summary,
            "laws": all_laws,
            "targets": all_targets,
            "validation": {
                "lexer": len(self.validator.validate_tokens(self.tokens)) == 0,
                "parser": len(self.parser_errors) == 0,
                "ast": len(self.validator.validate_ast(self.ast)) == 0
            }
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
            with open(filepath, 'w', encoding='utf-8') as f:
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
            "timestamp": datetime.now().isoformat()
        }
