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
Advanced analysis examples for Zenith Analyser.
"""

import json
from datetime import datetime, timedelta
from zenith_analyser import ZenithAnalyser


def example_1_multiple_laws_analysis():
    """Example 1: Analyzing multiple laws with temporal relationships."""
    print("=" * 60)
    print("Example 1: Multiple Laws Analysis")
    print("=" * 60)
    
    code = """
target multi_project:
    key:"Multiple Project Management"
    dictionnary:
        planning:"Project planning"
        dev:"Development"
        test:"Testing"
        deploy:"Deployment"
        review:"Review"
    
    law project_a_planning:
        start_date:2024-01-01 at 09:00
        period:16.0
        Event:
            a_req[planning]:"Requirements gathering"
            a_design[planning]:"System design"
        GROUP:(a_req 8.0^4.0 - a_design 4.0^0)
    end_law
    
    law project_a_development:
        start_date:2024-01-02 at 13:00 
        period:80.0
        Event:
            a_frontend[dev]:"Frontend development"
            a_backend[dev]:"Backend development"
            a_integration[dev]:"System integration"
        GROUP:(a_frontend 30.0^5.0 - a_backend 30.0^5.0 - a_integration 10.0^0)
    end_law
    
    law project_b_planning:
        start_date:2024-01-03 at 09:00  
        period:12.0
        Event:
            b_req[planning]:"Mobile requirements"
            b_design[planning]:"App design"
        GROUP:(b_req 6.0^2.0 - b_design 4.0^0)
    end_law
    
    law project_b_development:
        start_date:2024-01-04 at 14:00
        period:60.0
        Event:
            b_ui[dev]:"UI development"
            b_logic[dev]:"App logic"
            b_testing[test]:"Testing"
        GROUP:(b_ui 20.0^5.0 - b_logic 20.0^5.0 - b_testing 10.0^0)
    end_law
end_target
"""
    
    analyser = ZenithAnalyser(code)
    
    # Get all laws
    laws = analyser.law_analyser.laws
    print(f"Total laws in corpus: {len(laws)}")
    
    # Analyze temporal relationships
    print("\nTemporal Analysis:")
    law_descriptions = {}
    
    for law_name in laws.keys():
        desc = analyser.law_description(law_name)
        law_descriptions[law_name] = desc
        
        start = datetime.strptime(
            f"{desc['start_date']} {desc['start_time']}",
            "%Y-%m-%d %H:%M"
        )
        end = datetime.strptime(
            f"{desc['end_datetime']['date']} {desc['end_datetime']['time']}",
            "%Y-%m-%d %H:%M"
        )
        
        duration_hours = desc['total_duration_minutes'] / 60
        print(f"\n{law_name}:")
        print(f"  Start: {start.strftime('%Y-%m-%d %H:%M')}")
        print(f"  End: {end.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Duration: {duration_hours:.1f} hours")
        print(f"  Events: {desc['event_count']}")
    
    # Find overlaps
    print("\n\nTemporal Overlaps:")
    law_list = list(law_descriptions.items())
    
    for i, (name1, desc1) in enumerate(law_list):
        for name2, desc2 in law_list[i+1:]:
            start1 = datetime.strptime(
                f"{desc1['start_date']} {desc1['start_time']}",
                "%Y-%m-%d %H:%M"
            )
            end1 = datetime.strptime(
                f"{desc1['end_datetime']['date']} {desc1['end_datetime']['time']}",
                "%Y-%m-%d %H:%M"
            )
            start2 = datetime.strptime(
                f"{desc2['start_date']} {desc2['start_time']}",
                "%Y-%m-%d %H:%M"
            )
            end2 = datetime.strptime(
                f"{desc2['end_datetime']['date']} {desc2['end_datetime']['time']}",
                "%Y-%m-%d %H:%M"
            )
            
            # Check for overlap
            latest_start = max(start1, start2)
            earliest_end = min(end1, end2)
            
            if latest_start < earliest_end:
                overlap_hours = (earliest_end - latest_start).total_seconds() / 3600
                print(f"  {name1} overlaps with {name2}: {overlap_hours:.1f} hours")
    
    return law_descriptions


def example_2_resource_allocation():
    """Example 2: Resource allocation and conflict detection."""
    print("\n" + "=" * 60)
    print("Example 2: Resource Allocation Analysis")
    print("=" * 60)
    
    code = """
target resource_management:
    key:"Team Resource Management"
    dictionnary:
        dev_john:"John (Senior Developer)"
        dev_sarah:"Sarah (Frontend Specialist)"
        dev_mike:"Mike (Backend Developer)"
        qa_lisa:"Lisa (QA Engineer)"
        pm_tom:"Tom (Project Manager)"
    

    law monday_schedule:
        start_date:2024-01-01 at 09:00
        period:8.0
        Event:
            meeting[pm_tom]:"Standup meeting"
            frontend[dev_sarah]:"UI development"
            backend[dev_mike]:"API development"
            code_review[dev_john]:"Code review session"
        GROUP:(meeting 0.30^0.30 - frontend 3.0^1.0 - backend 3.0^1.0 - code_review 1.0^0)
    end_law
    

    law tuesday_schedule:
        start_date:2024-01-02 at 09:00
        period:8.0
        Event:
            planning[pm_tom]:"Sprint planning"
            frontend[dev_sarah]:"Component development"  
            api_work[dev_mike]:"API optimization"
            testing[qa_lisa]:"Test automation"
        GROUP:(planning 2.0^0.30 - frontend 4.0^0.30 - api_work 3.0^0.30 - testing 2.0^0)
    end_law
    
    law wednesday_schedule:
        start_date:2024-01-03 at 09:00
        period:8.0
        Event:
            architecture[dev_john]:"System architecture"
            frontend[dev_sarah]:"Frontend polish"  
            database[dev_mike]:"Database optimization"
            uat[qa_lisa]:"User acceptance testing"
        GROUP:(architecture 3.0^1.0 - frontend 3.0^1.0 - database 2.0^1.0 - uat 1.0^0)
    end_law
end_target
"""
    
    analyser = ZenithAnalyser(code)
    
    # Analyze resource allocation
    print("Resource Allocation Analysis:")
    
    # Get all events from all laws
    all_events = []
    for law_name in analyser.law_analyser.get_law_names():
        desc = analyser.law_description(law_name)
        for event in desc['simulation']:
            event['law'] = law_name
            all_events.append(event)
    
    # Group events by resource (based on event name patterns)
    resource_events = {}
    for event in all_events:
        # Extract resource from event name (simplified)
        resource = event['event_name'].split('[')[1].split(']')[0] if '[' in event['event_name'] else 'unknown'
        
        if resource not in resource_events:
            resource_events[resource] = []
        
        resource_events[resource].append(event)
    
    # Check for resource conflicts
    print("\nPotential Resource Conflicts:")
    conflicts_found = False
    
    for resource, events in resource_events.items():
        if len(events) > 1:
            # Sort events by start time
            events.sort(key=lambda e: datetime.strptime(
                f"{e['start']['date']} {e['start']['time']}",
                "%Y-%m-%d %H:%M"
            ))
            
            # Check for overlaps
            for i in range(len(events) - 1):
                event1 = events[i]
                event2 = events[i + 1]
                
                end1 = datetime.strptime(
                    f"{event1['end']['date']} {event1['end']['time']}",
                    "%Y-%m-%d %H:%M"
                )
                start2 = datetime.strptime(
                    f"{event2['start']['date']} {event2['start']['time']}",
                    "%Y-%m-%d %H:%M"
                )
                
                if end1 > start2:  # Overlap detected
                    conflicts_found = True
                    overlap_minutes = (end1 - start2).total_seconds() / 60
                    print(f"\n  Conflict for {resource}:")
                    print(f"    {event1['law']}: {event1['event_name']}")
                    print(f"      Ends: {end1.strftime('%H:%M')}")
                    print(f"    {event2['law']}: {event2['event_name']}")
                    print(f"      Starts: {start2.strftime('%H:%M')}")
                    print(f"    Overlap: {overlap_minutes:.0f} minutes")
    
    if not conflicts_found:
        print("  No resource conflicts detected.")
    
    # Resource utilization statistics
    print("\nResource Utilization:")
    for resource, events in resource_events.items():
        total_minutes = sum(e['duration_minutes'] for e in events)
        total_hours = total_minutes / 60
        print(f"\n  {resource}:")
        print(f"    Total assigned time: {total_hours:.1f} hours")
        print(f"    Number of assignments: {len(events)}")
        print(f"    Average assignment: {total_minutes/len(events):.0f} minutes" if events else "    No assignments")
    
    return resource_events


def example_3_progress_tracking():
    """Example 3: Project progress tracking and forecasting."""
    print("\n" + "=" * 60)
    print("Example 3: Progress Tracking and Forecasting")
    print("=" * 60)
    
    code = """
target software_project:
    key:"Software Development Project"
    dictionnary:
        phase1:"Phase 1: Foundation"
        phase2:"Phase 2: Core Development"
        phase3:"Phase 3: Testing & Deployment"
        milestone:"Project Milestone"
        delay:"Delay or Issue"
    

    law phase_1_foundation:
        start_date:2024-01-01 at 09:00
        period:80.0  
        Event:
            setup[phase1]:"Project setup"
            architecture[phase1]:"System architecture"
            prototyping[phase1]:"Prototype development"
        GROUP:(setup 16.0^4.0 - architecture 40.0^8.0 - prototyping 12.0^0)
    end_law
    
    law phase_2_development:
        start_date:2024-01-12 at 09:00  
        period:240.0  
        Event:
            frontend[phase2]:"Frontend development"
            backend[phase2]:"Backend development"
            integration[phase2]:"System integration"
            milestone1[milestone]:"Mid-project milestone"
        GROUP:(frontend 80.0^20.0 - backend 80.0^20.0 - integration 40.0^10.0 - milestone1 10.0^0)
    end_law
    
    law unexpected_delay:
        start_date:2024-01-25 at 09:00  
        period:40.0  
        Event:
            issue[delay]:"Technical issue resolution"
        GROUP:(issue 40.0^0)
    end_law
    
    law phase_3_final:
        start_date:2024-02-16 at 09:00 
        period:120.0  
        Event:
            testing[phase3]:"Comprehensive testing"
            deployment[phase3]:"Production deployment"
            documentation[phase3]:"Documentation"
            final_milestone[milestone]:"Project completion"
        GROUP:(testing 60.0^20.0 - deployment 20.0^10.0 - documentation 20.0^5.0 - final_milestone 5.0^0)
    end_law
end_target
"""
    
    analyser = ZenithAnalyser(code)
    
    # Get project timeline
    print("Project Timeline Analysis:")
    
    # Analyze each phase
    phases = {}
    for law_name in analyser.law_analyser.get_law_names():
        desc = analyser.law_description(law_name)
        phases[law_name] = desc
        
        start_dt = datetime.strptime(
            f"{desc['start_date']} {desc['start_time']}",
            "%Y-%m-%d %H:%M"
        )
        end_dt = datetime.strptime(
            f"{desc['end_datetime']['date']} {desc['end_datetime']['time']}",
            "%Y-%m-%d %H:%M"
        )
        
        duration_days = desc['total_duration_minutes'] / 60 / 8  # 8-hour days
        print(f"\n{law_name}:")
        print(f"  Start: {start_dt.strftime('%Y-%m-%d')}")
        print(f"  End: {end_dt.strftime('%Y-%m-%d')}")
        print(f"  Duration: {duration_days:.1f} working days")
        print(f"  Events: {desc['event_count']}")
    
    # Calculate project statistics
    print("\n\nProject Statistics:")
    
    total_duration = sum(p['total_duration_minutes'] for p in phases.values())
    total_days = total_duration / 60 / 8  # 8-hour days
    
    start_dates = [
        datetime.strptime(f"{p['start_date']} {p['start_time']}", "%Y-%m-%d %H:%M")
        for p in phases.values()
    ]
    end_dates = [
        datetime.strptime(f"{p['end_datetime']['date']} {p['end_datetime']['time']}", "%Y-%m-%d %H:%M")
        for p in phases.values()
    ]
    
    project_start = min(start_dates)
    project_end = max(end_dates)
    calendar_days = (project_end - project_start).days + 1
    
    print(f"Total project duration: {total_days:.1f} working days")
    print(f"Calendar duration: {calendar_days} days")
    print(f"Start: {project_start.strftime('%Y-%m-%d')}")
    print(f"End: {project_end.strftime('%Y-%m-%d')}")
    
    # Efficiency metrics
    efficiency = (total_days / calendar_days) * 100
    print(f"Efficiency: {efficiency:.1f}% (work days / calendar days)")
    
    # Identify critical path (longest phase)
    longest_phase = max(phases.items(), key=lambda x: x[1]['total_duration_minutes'])
    print(f"\nCritical path (longest phase): {longest_phase[0]}")
    print(f"  Duration: {longest_phase[1]['total_duration_minutes']/60/8:.1f} days")
    
    return phases


def example_4_what_if_scenarios():
    """Example 4: What-if scenario analysis."""
    print("\n" + "=" * 60)
    print("Example 4: What-If Scenario Analysis")
    print("=" * 60)
    
    base_code = """
law original_schedule:
    start_date:2024-01-01 at 09:00
    period:40.0
    Event:
        phase1:"Phase 1: Analysis"
        phase2:"Phase 2: Development"
        phase3:"Phase 3: Testing"
    GROUP:(phase1 10.0^2.0 - phase2 20.0^2.0 - phase3 6.0^0)
end_law
"""
    
    # Scenario 1: Compressed schedule
    scenario_1_code = """
law compressed_schedule:
    start_date:2024-01-01 at 09:00
    period:30.0  
    Event:
        phase1:"Phase 1: Analysis (compressed)"
        phase2:"Phase 2: Development (compressed)"
        phase3:"Phase 3: Testing (compressed)"
    GROUP:(phase1 8.0^1.0 - phase2 16.0^1.0 - phase3 4.0^0)
end_law
"""
    
    # Scenario 2: Extended schedule with buffer
    scenario_2_code = """
law extended_schedule:
    start_date:2024-01-01 at 09:00
    period:50.0  
    Event:
        phase1:"Phase 1: Analysis (with buffer)"
        phase2:"Phase 2: Development (with buffer)"
        buffer:"Contingency buffer"
        phase3:"Phase 3: Testing (with buffer)"
    GROUP:(phase1 12.0^3.0 - phase2 24.0^3.0 - buffer 4.0^2.0 - phase3 8.0^0)
end_law
"""
    
    print("Comparing scheduling scenarios:")
    
    scenarios = {
        "Original": base_code,
        "Compressed (25% faster)": scenario_1_code,
        "Extended (25% buffer)": scenario_2_code
    }
    
    results = {}
    
    for scenario_name, code in scenarios.items():
        analyser = ZenithAnalyser(code)
        law_name = list(analyser.law_analyser.get_law_names())[0]
        desc = analyser.law_description(law_name)
        results[scenario_name] = desc
        
        print(f"\n{scenario_name}:")
        print(f"  Total duration: {desc['total_duration_minutes']/60:.1f} hours")
        print(f"  Work time: {desc['coherence_total_minutes']/60:.1f} hours")
        print(f"  Gap time: {desc['dispersal_total_minutes']/60:.1f} hours")
        print(f"  Efficiency: {(desc['coherence_total_minutes']/desc['total_duration_minutes'])*100:.1f}%")
    
    # Comparative analysis
    print("\n\nComparative Analysis:")
    original = results["Original"]
    
    for scenario_name, desc in results.items():
        if scenario_name != "Original":
            time_diff = desc['total_duration_minutes'] - original['total_duration_minutes']
            efficiency_diff = ((desc['coherence_total_minutes']/desc['total_duration_minutes']) - 
                             (original['coherence_total_minutes']/original['total_duration_minutes'])) * 100
            
            print(f"\n{scenario_name} vs Original:")
            print(f"  Time difference: {time_diff/60:+.1f} hours ({time_diff/original['total_duration_minutes']*100:+.1f}%)")
            print(f"  Efficiency difference: {efficiency_diff:+.1f}%")
    
    return results


def example_5_custom_metrics():
    """Example 5: Calculating custom business metrics."""
    print("\n" + "=" * 60)
    print("Example 5: Custom Business Metrics")
    print("=" * 60)
    
    code = """
target business_project:
    key:"Business Project with Metrics"
    dictionnary:
        high_value:"High-value activity ($500/hour)"
        medium_value:"Medium-value activity ($250/hour)"
        low_value:"Low-value activity ($100/hour)"
        meeting:"Meeting ($300/hour)"
        admin:"Administrative ($50/hour)"
    
    law week_1:
        start_date:2024-01-01 at 09:00
        period:40.0
        Event:
            planning[high_value]:"Strategic planning"
            client_meeting[meeting]:"Client meeting"
            research[medium_value]:"Market research"
            documentation[admin]:"Documentation"
            analysis[high_value]:"Data analysis"
        GROUP:(planning 8.0^1.0 - client_meeting 2.0^1.0 - research 6.0^1.0 - documentation 4.0^1.0 - analysis 8.0^0)
    end_law
    
    law week_2:
        start_date:2024-01-08 at 09:00
        period:40.0
        Event:
            development[high_value]:"Product development"
            team_meeting[meeting]:"Team sync"
            testing[medium_value]:"Quality testing"
            reporting[admin]:"Progress reporting"
            optimization[high_value]:"Performance optimization"
        GROUP:(development 12.0^1.0 - team_meeting 1.0^1.0 - testing 8.0^1.0 - reporting 3.0^1.0 - optimization 10.0^0)
    end_law
end_target
"""
    
    analyser = ZenithAnalyser(code)
    
    # Define value rates for different activity types
    value_rates = {
        "high_value": 500,    # $500 per hour
        "medium_value": 250,  # $250 per hour
        "low_value": 100,     # $100 per hour
        "meeting": 300,       # $300 per hour
        "admin": 50,          # $50 per hour
    }
    
    # Analyze value generation
    print("Business Value Analysis:")
    
    total_value = 0
    activity_summary = {activity: {"hours": 0, "value": 0} for activity in value_rates.keys()}
    
    for law_name in analyser.law_analyser.get_law_names():
        desc = analyser.law_description(law_name)
        
        print(f"\n{law_name}:")
        law_value = 0
        
        for event in desc['simulation']:
            # Determine activity type from event name
            event_name = event['event_name']
            activity_type = None
            
            for activity in value_rates.keys():
                if f"[{activity}]" in event_name:
                    activity_type = activity
                    break
            
            if activity_type:
                hours = event['duration_minutes'] / 60
                value = hours * value_rates[activity_type]
                law_value += value
                
                # Update summary
                activity_summary[activity_type]["hours"] += hours
                activity_summary[activity_type]["value"] += value
                
                print(f"  {event_name.split('[')[0]}: {hours:.1f} hours = ${value:,.0f}")
            else:
                print(f"  {event_name}: {event['duration_minutes']/60:.1f} hours (unvalued)")
        
        total_value += law_value
        print(f"  Total value: ${law_value:,.0f}")
    
    # Summary statistics
    print("\n\nSummary Statistics:")
    print("=" * 40)
    
    total_hours = sum(summary["hours"] for summary in activity_summary.values())
    print(f"\nTotal tracked hours: {total_hours:.1f}")
    print(f"Total generated value: ${total_value:,.0f}")
    print(f"Average hourly rate: ${total_value/total_hours:,.0f}/hour" if total_hours > 0 else "No hours tracked")
    
    print("\nBreakdown by activity type:")
    for activity, summary in activity_summary.items():
        if summary["hours"] > 0:
            percentage = (summary["value"] / total_value) * 100 if total_value > 0 else 0
            hourly_rate = summary["value"] / summary["hours"] if summary["hours"] > 0 else 0
            print(f"\n  {activity}:")
            print(f"    Hours: {summary['hours']:.1f} ({summary['hours']/total_hours*100:.1f}%)")
            print(f"    Value: ${summary['value']:,.0f} ({percentage:.1f}%)")
            print(f"    Rate: ${hourly_rate:,.0f}/hour")
    
    # Efficiency metrics
    print("\nEfficiency Metrics:")
    
    # Calculate potential value (if all time was high-value)
    potential_value = total_hours * value_rates["high_value"]
    value_efficiency = (total_value / potential_value) * 100 if potential_value > 0 else 0
    
    print(f"Value efficiency: {value_efficiency:.1f}%")
    print(f"Value gap: ${potential_value - total_value:,.0f}")
    
    return {
        "total_value": total_value,
        "activity_summary": activity_summary,
        "value_efficiency": value_efficiency
    }


def main():
    """Run all advanced examples."""
    print("Zenith Analyser - Advanced Analysis Examples")
    print("=" * 60)
    
    try:
        # Run advanced examples
        example_1_multiple_laws_analysis()
        example_2_resource_allocation()
        example_3_progress_tracking()
        example_4_what_if_scenarios()
        example_5_custom_metrics()
        
        print("\n" + "=" * 60)
        print("All advanced examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError in example: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
 
