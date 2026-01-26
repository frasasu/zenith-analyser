#!/usr/bin/env python3
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
Basic usage examples for Zenith Analyser.
"""

import json

from zenith_analyser import ZenithAnalyser


def example_1_simple_analysis():
    """Example 1: Simple law analysis."""
    print("=" * 60)
    print("Example 1: Simple Law Analysis")
    print("=" * 60)

    code = """
law simple_day:
    start_date:2024-01-01 at 09:00
    period:8.0
    Event:
        work:"Work session"
        lunch:"Lunch break"
        meeting:"Team meeting"
    GROUP:(work 4.0^1.0 - lunch 1.0^1.0 - meeting 2.0^0)
end_law
"""

    analyser = ZenithAnalyser(code)
    result = analyser.law_description("simple_day")

    print(f"Law: {result['name']}")
    print(f"Duration: {result['sum_duration']} minutes")
    print(f"Events: {result['event_count']}")
    print("\nTimeline:")
    for event in result["simulation"]:
        print(
            f"  {event['event_name']}: {event['start']['time']} - {event['end']['time']}"
        )

    return result


def example_2_target_hierarchy():
    """Example 2: Target hierarchy analysis."""
    print("\n" + "=" * 60)
    print("Example 2: Target Hierarchy Analysis")
    print("=" * 60)

    code = """
target project:
    key:"Software Project"
    dictionnary:
        planning:"Planning activities"
        development:"Development work"

    target frontend:
        key:"Frontend Development"
        dictionnary:
            ui[development]:"User Interface"
            ux[development]:"User Experience"

        law frontend_sprint:
            start_date:2024-01-01 at 09:00
            period:40.0
            Event:
                design[ui]:"UI Design"
                implement[ui]:"Implementation"
                test[ux]:"Usability testing"
            GROUP:(design 10.0^1.0 - implement 25.0^1.0 - test 4.0^0)
        end_law
    end_target

    law project_planning:
        start_date:2024-01-01 at 08:00
        period:1.0
        Event:
            kickoff[planning]:"Project kickoff"
        GROUP:(kickoff 1.0^0)
    end_law
end_target
"""

    analyser = ZenithAnalyser(code)

    # Analyze the root target
    target_result = analyser.target_description("project")
    print(f"Target: {target_result['name']}")
    print(f"Total events: {len(target_result['simulation'])}")
    print(f"Total duration: {target_result['sum_duration']} minutes")

    # Show hierarchy
    print("\nTarget Hierarchy:")
    for target_name in analyser.target_analyser.get_target_names():
        hierarchy = analyser.target_analyser.get_target_hierarchy(target_name)
        indent = "  " * (hierarchy["depth"] - 1)
        print(f"{indent}{target_name} (depth: {hierarchy['depth']})")

    return target_result


def example_3_population_analysis():
    """Example 3: Population-based analysis."""
    print("\n" + "=" * 60)
    print("Example 3: Population Analysis")
    print("=" * 60)

    code = """
target organization:
    key:"Organization Structure"
    dictionnary:
        dept_a_activity:"Department A activities"
    target department_a:
        key:"Department A"
        dictionnary:
            dept_a_activity:"Department A activities"
        law dept_a_activity:
            start_date:2024-01-01 at 09:00
            period:8.0
            Event:
                task1:"Task A1"
                task2:"Task A2"
            GROUP:(task1 4.0^1.0 - task2 3.0^0)
        end_law
    end_target

    target department_b:
        key:"Department B"
        dictionnary:
            team_b1:"Team B1 activities"
        target team_b1:
            key:"Team B1"
            dictionnary:
                 dept_a_activity:"Department A activities"
            law team_b1_activity:
                start_date:2024-01-01 at 10:00
                period:6.0
                Event:
                    task3:"Task B1"
                    task4:"Task B2"
                GROUP:(task3 3.0^1.0 - task4 2.0^0)
            end_law
        end_target
    end_target
end_target
"""

    analyser = ZenithAnalyser(code)

    # Analyze different population levels
    for population in [1, 2, 3]:
        stats = analyser.population_description(population)

        print(f"\nPopulation {population}:")
        print(f"  Duration: {stats['sum_duration']} minutes")


def example_4_export_and_import():
    """Example 4: Export to JSON and import."""
    print("\n" + "=" * 60)
    print("Example 4: Export and Import")
    print("=" * 60)

    code = """
law export_example:
    start_date:2024-01-01 at 09:00
    period:6.0
    Event:
        morning:"Morning session"
        afternoon:"Afternoon session"
    GROUP:(morning 4.0^1.0 - afternoon 2.0^0)
end_law
"""

    analyser = ZenithAnalyser(code)

    # Export to dictionary (simulating JSON export)
    analysis = analyser.analyze_corpus()

    print("Exported analysis contains:")
    for key in analysis.keys():
        if isinstance(analysis[key], dict):
            print(f"  {key}: dict with {len(analysis[key])} items")
        elif isinstance(analysis[key], list):
            print(f"  {key}: list with {len(analysis[key])} items")
        else:
            print(f"  {key}: {type(analysis[key]).__name__}")

    # Show sample of law data
    law_name = list(analysis["laws"].keys())[0]
    law_data = analysis["laws"][law_name]
    print(f"\nSample law '{law_name}':")
    print(f"  Duration: {law_data.get('sum_duration', 0)} minutes")
    print(f"  Events: {law_data.get('event_count', 0)}")

    return analysis


def example_5_custom_analysis():
    """Example 5: Custom analysis with extracted data."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Analysis")
    print("=" * 60)

    code = """
law weekly_schedule:
    start_date:2024-01-01 at 09:00
    period:40.0
    Event:
        mon:"Monday tasks"
        tue:"Tuesday tasks"
        wed:"Wednesday tasks"
        thu:"Thursday tasks"
        fri:"Friday tasks"
    GROUP:(mon 8.0^16.0 - tue 8.0^16.0 - wed 8.0^16.0 - thu 8.0^16.0 - fri 8.0^0)
end_law
"""

    analyser = ZenithAnalyser(code)
    result = analyser.law_description("weekly_schedule")

    # Custom analysis: Calculate statistics
    events = result["simulation"]

    print(f"Schedule: {result['name']}")
    print(f"Total work hours: {result['sum_duration'] / 60:.1f} hours")
    print(f"Daily average: {result['sum_duration'] / 5 / 60:.1f} hours/day")

    print("\nDaily breakdown:")
    for event in events:
        hours = event["duration_minutes"] / 60
        print(f"  {event['event_name']}: {hours:.1f} hours")

    # Calculate gaps (dispersal)
    total_gap = result["dispersal"]
    print(f"\nTotal gap time: {total_gap / 60:.1f} hours")
    print(
        f"Average daily gap: {total_gap / 4 / 60:.1f} hours/day"
    )  # 4 gaps between 5 days


def main():
    """Run all examples."""
    print("Zenith Analyser - Basic Usage Examples")
    print("=" * 60)

    try:
        # Run examples
        example_1_simple_analysis()
        example_2_target_hierarchy()
        example_3_population_analysis()
        example_4_export_and_import()
        example_5_custom_analysis()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError in example: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
