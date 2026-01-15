#!/usr/bin/env python3
"""
Custom workflow examples for Zenith Analyser.
"""

import json
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any
from zenith_analyser import ZenithAnalyser, ASTUnparser


def workflow_1_batch_processing():
    """Workflow 1: Batch processing multiple Zenith files."""
    print("=" * 60)
    print("Workflow 1: Batch Processing")
    print("=" * 60)
    
    # Simulate multiple Zenith files
    zenith_files = {
        "project_a.zenith": """
target project_a:
    key:"Project Alpha"
    law sprint_1:
        start_date:2024-01-01 at 09:00
        period:40.0
        Event:
            planning:"Sprint planning"
            development:"Feature development"
            review:"Code review"
        GROUP:(planning 8.0^2.0 - development 25.0^3.0 - review 2.0^0)
    end_law
end_target
""",
        
        "project_b.zenith": """
target project_b:
    key:"Project Beta"
    law sprint_1:
        start_date:2024-01-08 at 09:00
        period:40.0
        Event:
            design:"UI/UX design"
            implementation:"Implementation"
            testing:"Testing"
        GROUP:(design 10.0^2.0 - implementation 20.0^5.0 - testing 3.0^0)
    end_law
end_target
""",
        
        "project_c.zenith": """
target project_c:
    key:"Project Gamma"
    law sprint_1:
        start_date:2024-01-15 at 09:00
        period:40.0
        Event:
            research:"Market research"
            prototyping:"Prototype development"
            validation:"User validation"
        GROUP:(research 15.0^3.0 - prototyping 18.0^2.0 - validation 2.0^0)
    end_law
end_target
"""
    }
    
    print(f"Processing {len(zenith_files)} Zenith files...")
    
    results = {}
    summary = {
        "total_projects": len(zenith_files),
        "total_hours": 0,
        "projects": []
    }
    
    for filename, code in zenith_files.items():
        print(f"\nProcessing {filename}...")
        
        try:
            analyser = ZenithAnalyser(code)
            
            # Get project name from first target
            project_name = analyser.target_analyser.get_target_names()[0]
            
            # Analyze the law
            law_name = analyser.law_analyser.get_law_names()[0]
            analysis = analyser.law_description(law_name)
            
            # Store results
            results[filename] = {
                "project_name": project_name,
                "analysis": analysis,
                "raw_code": code[:100] + "..."  # Store snippet
            }
            
            # Update summary
            hours = analysis['total_duration_minutes'] / 60
            summary["total_hours"] += hours
            summary["projects"].append({
                "name": project_name,
                "file": filename,
                "hours": hours,
                "events": analysis['event_count'],
                "start_date": analysis['start_date']
            })
            
            print(f"  ✓ {project_name}: {hours:.1f} hours, {analysis['event_count']} events")
            
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
            results[filename] = {"error": str(e)}
    
    # Generate summary report
    print("\n\nBatch Processing Summary:")
    print("=" * 40)
    print(f"Total projects processed: {summary['total_projects']}")
    print(f"Total hours: {summary['total_hours']:.1f}")
    print(f"Average hours per project: {summary['total_hours']/summary['total_projects']:.1f}")
    
    # Sort projects by start date
    summary['projects'].sort(key=lambda x: x['start_date'])
    
    print("\nProjects by start date:")
    for project in summary['projects']:
        print(f"  {project['name']}: {project['start_date']}, {project['hours']:.1f} hours")
    
    return results, summary


def workflow_2_data_transformation():
    """Workflow 2: Transform Zenith data to other formats."""
    print("\n" + "=" * 60)
    print("Workflow 2: Data Transformation")
    print("=" * 60)
    
    code = """
target transformation_example:
    key:"Data Transformation Example"
    dictionnary:
        dev:"Development work"
        test:"Testing activities"
        meet:"Meetings"
        doc:"Documentation"
    
    law weekly_activities:
        start_date:2024-01-01 at 09:00
        period:40.0
        Event:
            monday_dev[dev]:"Monday development"
            tuesday_test[test]:"Tuesday testing"
            wednesday_meet[meet]:"Wednesday meeting"
            thursday_doc[doc]:"Thursday documentation"
            friday_dev[dev]:"Friday development"
        GROUP:(monday_dev 8.0^16.0 - tuesday_test 8.0^16.0 - wednesday_meet 8.0^16.0 - thursday_doc 8.0^16.0 - friday_dev 8.0^0)
    end_law
end_target
"""
    
    analyser = ZenithAnalyser(code)
    analysis = analyser.analyze_corpus()
    
    print("Transforming Zenith data to various formats...")
    
    # 1. Transform to CSV
    print("\n1. CSV Format:")
    csv_data = []
    
    for law_name, law_data in analysis['laws'].items():
        if isinstance(law_data, dict) and 'error' not in law_data:
            for event in law_data.get('simulation', []):
                csv_data.append({
                    'law': law_name,
                    'event': event['event_name'],
                    'start_date': event['start']['date'],
                    'start_time': event['start']['time'],
                    'end_date': event['end']['date'],
                    'end_time': event['end']['time'],
                    'duration_minutes': event['duration_minutes'],
                    'duration_hours': event['duration_minutes'] / 60
                })
    
    # Print CSV sample
    if csv_data:
        print("Sample CSV data:")
        headers = csv_data[0].keys()
        print(",".join(headers))
        for i, row in enumerate(csv_data[:3]):  # First 3 rows
            print(",".join(str(row[h]) for h in headers))
        if len(csv_data) > 3:
            print(f"... and {len(csv_data) - 3} more rows")
    
    # 2. Transform to iCalendar format (simplified)
    print("\n2. iCalendar Format (simplified):")
    ical_events = []
    
    for law_name, law_data in analysis['laws'].items():
        if isinstance(law_data, dict) and 'error' not in law_data:
            for event in law_data.get('simulation', []):
                ical_event = {
                    'SUMMARY': f"{law_name}: {event['event_name']}",
                    'DTSTART': f"{event['start']['date'].replace('-', '')}T{event['start']['time'].replace(':', '')}00",
                    'DTEND': f"{event['end']['date'].replace('-', '')}T{event['end']['time'].replace(':', '')}00",
                    'DESCRIPTION': f"Duration: {event['duration_minutes']} minutes"
                }
                ical_events.append(ical_event)
    
    # Print iCalendar sample
    if ical_events:
        print("BEGIN:VCALENDAR")
        print("VERSION:2.0")
        print("PRODID:-//Zenith Analyser//EN")
        for i, event in enumerate(ical_events[:2]):  # First 2 events
            print("BEGIN:VEVENT")
            for key, value in event.items():
                print(f"{key}:{value}")
            print("END:VEVENT")
        print("END:VCALENDAR")
        if len(ical_events) > 2:
            print(f"... and {len(ical_events) - 2} more events")
    
    # 3. Transform to Gantt chart data (JSON)
    print("\n3. Gantt Chart Data (JSON):")
    gantt_data = {
        "tasks": [],
        "resources": []
    }
    
    resource_id = 1
    resources_map = {}
    
    for law_name, law_data in analysis['laws'].items():
        if isinstance(law_data, dict) and 'error' not in law_data:
            # Add law as a group task
            gantt_data["tasks"].append({
                "id": f"law_{law_name}",
                "text": law_name,
                "start_date": law_data['start_date'],
                "duration": law_data['total_duration_minutes'] / 60 / 8,  # in days
                "progress": 0.5,
                "parent": 0,
                "type": "project"
            })
            
            # Add events as subtasks
            for i, event in enumerate(law_data.get('simulation', [])):
                # Extract resource from event name if present
                resource = "default"
                if '[' in event['event_name']:
                    resource = event['event_name'].split('[')[1].split(']')[0]
                
                if resource not in resources_map:
                    resources_map[resource] = resource_id
                    gantt_data["resources"].append({
                        "id": resource_id,
                        "name": resource
                    })
                    resource_id += 1
                
                gantt_data["tasks"].append({
                    "id": f"event_{law_name}_{i}",
                    "text": event['event_name'].split('[')[0].strip(),
                    "start_date": event['start']['date'],
                    "duration": event['duration_minutes'] / 60 / 8,  # in days
                    "progress": 1.0,
                    "parent": f"law_{law_name}",
                    "resource": resources_map[resource],
                    "type": "task"
                })
    
    print(f"Generated {len(gantt_data['tasks'])} tasks for Gantt chart")
    print(f"Using {len(gantt_data['resources'])} resources")
    
    return {
        'csv_data': csv_data,
        'ical_events': ical_events,
        'gantt_data': gantt_data
    }


def workflow_3_custom_validation_pipeline():
    """Workflow 3: Custom validation and quality assurance pipeline."""
    print("\n" + "=" * 60)
    print("Workflow 3: Custom Validation Pipeline")
    print("=" * 60)
    
    # Test code with various issues
    test_code = """
target validation_test:
    key:"Validation Test Project"
    dictionnary:
        dev:"Development"
        test:"Testing"
        meet:"Meeting"
    
    law valid_law:
        start_date:2024-01-01 at 09:00
        period:8.0
        Event:
            session1[dev]:"Development session"
            session2[test]:"Testing session"
        GROUP:(session1 4.0^1.0 - session2 3.0^0)
    end_law
    
    law tight_schedule:
        start_date:2024-01-02 at 09:00
        period:8.0
        Event:
            task1[dev]:"Task 1"
            task2[dev]:"Task 2"
            task3[dev]:"Task 3"
        GROUP:(task1 2.0^0.05 - task2 2.0^0.05 - task3 2.0^0)  # Very short gaps
    end_law
    
    law marathon_session:
        start_date:2024-01-03 at 09:00
        period:16.0  
        Event:
            long_task[dev]:"Marathon task"
        GROUP:(long_task 16.0^0)
    end_law
    
    law fragmented_day:
        start_date:2024-01-04 at 09:00
        period:8.0
        Event:
            e1[meet]:"Meeting 1"
            e2[dev]:"Dev 1"
            e3[meet]:"Meeting 2"
            e4[dev]:"Dev 2"
            e5[meet]:"Meeting 3"
            e6[dev]:"Dev 3"
            e7[meet]:"Meeting 4"
            e8[dev]:"Dev 4"
        GROUP:(e1 0.30^0.15 - e2 1.0^0.15 - e3 0.30^0.15 - e4 1.0^0.15 - e5 0.30^0.15 - e6 1.0^0.15 - e7 0.30^0.15 - e8 1.0^0)
    end_law
end_target
"""
    
    analyser = ZenithAnalyser(test_code)
    
    print("Running custom validation checks...")
    
    validation_results = {
        "warnings": [],
        "errors": [],
        "suggestions": []
    }
    
    # Custom validation rules
    for law_name in analyser.law_analyser.get_law_names():
        try:
            law_data = analyser.law_description(law_name)
            
            print(f"\nValidating: {law_name}")
            
            # Rule 1: Check for very short gaps (< 10 minutes)
            short_gaps = []
            for i in range(len(law_data['simulation']) - 1):
                event1 = law_data['simulation'][i]
                event2 = law_data['simulation'][i + 1]
                
                end1 = datetime.strptime(
                    f"{event1['end']['date']} {event1['end']['time']}",
                    "%Y-%m-%d %H:%M"
                )
                start2 = datetime.strptime(
                    f"{event2['start']['date']} {event2['start']['time']}",
                    "%Y-%m-%d %H:%M"
                )
                
                gap_minutes = (start2 - end1).total_seconds() / 60
                if 0 < gap_minutes < 10:
                    short_gaps.append({
                        'between': f"{event1['event_name']} and {event2['event_name']}",
                        'minutes': gap_minutes
                    })
            
            if short_gaps:
                validation_results["warnings"].append({
                    'law': law_name,
                    'type': 'short_gaps',
                    'message': f"Found {len(short_gaps)} very short gap(s) (< 10 minutes)",
                    'details': short_gaps
                })
                print(f"  ⚠ Found {len(short_gaps)} very short gap(s)")
            
            # Rule 2: Check for very long events (> 4 hours)
            long_events = []
            for event in law_data['simulation']:
                if event['duration_minutes'] > 240:  # 4 hours
                    long_events.append({
                        'event': event['event_name'],
                        'hours': event['duration_minutes'] / 60
                    })
            
            if long_events:
                validation_results["suggestions"].append({
                    'law': law_name,
                    'type': 'long_events',
                    'message': f"Found {len(long_events)} very long event(s) (> 4 hours)",
                    'details': long_events
                })
                print(f"  💡 Found {len(long_events)} very long event(s)")
            
            # Rule 3: Check for fragmentation (many short events)
            if len(law_data['simulation']) > 6:
                validation_results["suggestions"].append({
                    'law': law_name,
                    'type': 'fragmentation',
                    'message': f"Law has {len(law_data['simulation'])} events (consider consolidation)",
                    'details': {'event_count': len(law_data['simulation'])}
                })
                print(f"  💡 Law has {len(law_data['simulation'])} events (potentially fragmented)")
            
            # Rule 4: Check work-life balance (events outside normal hours)
            off_hours_events = []
            for event in law_data['simulation']:
                start_time = datetime.strptime(event['start']['time'], "%H:%M")
                end_time = datetime.strptime(event['end']['time'], "%H:%M")
                
                # Check if starts before 8 AM or ends after 6 PM
                if start_time.hour < 8 or end_time.hour >= 18:
                    off_hours_events.append({
                        'event': event['event_name'],
                        'start': event['start']['time'],
                        'end': event['end']['time']
                    })
            
            if off_hours_events:
                validation_results["warnings"].append({
                    'law': law_name,
                    'type': 'off_hours',
                    'message': f"Found {len(off_hours_events)} event(s) outside normal working hours (8 AM - 6 PM)",
                    'details': off_hours_events
                })
                print(f"  ⚠ Found {len(off_hours_events)} event(s) outside normal hours")
            
            print(f"  ✓ Validation complete for {law_name}")
            
        except Exception as e:
            validation_results["errors"].append({
                'law': law_name,
                'type': 'validation_error',
                'message': f"Error during validation: {str(e)}"
            })
            print(f"  ✗ Error validating {law_name}: {e}")
    
    # Generate validation report
    print("\n\nValidation Report:")
    print("=" * 40)
    
    print(f"\nSummary:")
    print(f"  Laws validated: {len(analyser.law_analyser.get_law_names())}")
    print(f"  Warnings: {len(validation_results['warnings'])}")
    print(f"  Errors: {len(validation_results['errors'])}")
    print(f"  Suggestions: {len(validation_results['suggestions'])}")
    
    if validation_results['warnings']:
        print("\nWarnings:")
        for warning in validation_results['warnings']:
            print(f"  • {warning['law']}: {warning['message']}")
    
    if validation_results['suggestions']:
        print("\nSuggestions:")
        for suggestion in validation_results['suggestions']:
            print(f"  • {suggestion['law']}: {suggestion['message']}")
    
    if validation_results['errors']:
        print("\nErrors:")
        for error in validation_results['errors']:
            print(f"  • {error['law']}: {error['message']}")
    
    return validation_results


def workflow_4_continuous_integration():
    """Workflow 4: Continuous integration and automated testing."""
    print("\n" + "=" * 60)
    print("Workflow 4: Continuous Integration Pipeline")
    print("=" * 60)
    
    # Simulate CI pipeline
    print("Simulating CI/CD pipeline for Zenith code...")
    
    pipeline_steps = [
        ("Code Quality Check", True),
        ("Syntax Validation", True),
        ("Semantic Analysis", True),
        ("Performance Test", True),
        ("Integration Test", True),
        ("Documentation Generation", True)
    ]
    
    test_code = """
target ci_test:
    key:"CI/CD Test Project"
    
    law build_pipeline:
        start_date:2024-01-01 at 09:00
        period:2.0
        Event:
            lint:"Code linting"
            test:"Running tests"
            build:"Building package"
            deploy:"Deployment"
        GROUP:(lint 0.15^0.15 - test 0.30^0.15 - build 0.30^0.15 - deploy 0.30^0)
    end_law
end_target
"""
    
    print(f"\nPipeline configuration:")
    for step, enabled in pipeline_steps:
        status = "✓ ENABLED" if enabled else "✗ DISABLED"
        print(f"  {step}: {status}")
    
    print("\nRunning pipeline...")
    
    pipeline_results = []
    
    # Step 1: Code Quality Check
    print("\n1. Code Quality Check...")
    analyser = ZenithAnalyser(test_code)
    
    # Check code metrics
    code_metrics = {
        'lines': len(test_code.split('\n')),
        'laws': len(analyser.law_analyser.get_law_names()),
        'targets': len(analyser.target_analyser.get_target_names()),
        'complexity': analyser.parser.get_ast_summary(analyser.ast)['max_nesting']
    }
    
    pipeline_results.append({
        'step': 'Code Quality',
        'status': 'PASS',
        'metrics': code_metrics,
        'details': 'Code structure is valid and well-formed'
    })
    print("  ✓ Code quality check passed")
    
    # Step 2: Syntax Validation
    print("\n2. Syntax Validation...")
    from zenith_analyser import Validator
    validator = Validator()
    
    syntax_errors = validator.validate_code(test_code)
    if not syntax_errors:
        pipeline_results.append({
            'step': 'Syntax Validation',
            'status': 'PASS',
            'details': 'No syntax errors found'
        })
        print("  ✓ Syntax validation passed")
    else:
        pipeline_results.append({
            'step': 'Syntax Validation',
            'status': 'FAIL',
            'details': f'Found {len(syntax_errors)} syntax error(s)',
            'errors': syntax_errors
        })
        print(f"  ✗ Syntax validation failed: {len(syntax_errors)} error(s)")
    
    # Step 3: Semantic Analysis
    print("\n3. Semantic Analysis...")
    try:
        # Analyze the law
        law_name = analyser.law_analyser.get_law_names()[0]
        law_analysis = analyser.law_description(law_name)
        
        # Check semantic rules
        semantic_issues = []
        
        # Rule: Total duration should match sum of events
        calculated_duration = sum(e['duration_minutes'] for e in law_analysis['simulation'])
        if abs(law_analysis['total_duration_minutes'] - calculated_duration) > 1:
            semantic_issues.append(f"Duration mismatch: {law_analysis['total_duration_minutes']} vs {calculated_duration}")
        
        if not semantic_issues:
            pipeline_results.append({
                'step': 'Semantic Analysis',
                'status': 'PASS',
                'details': 'Semantic analysis passed all checks',
                'metrics': {
                    'total_duration': law_analysis['total_duration_minutes'],
                    'event_count': law_analysis['event_count']
                }
            })
            print("  ✓ Semantic analysis passed")
        else:
            pipeline_results.append({
                'step': 'Semantic Analysis',
                'status': 'WARN',
                'details': f'Found {len(semantic_issues)} semantic issue(s)',
                'issues': semantic_issues
            })
            print(f"  ⚠ Semantic analysis warnings: {len(semantic_issues)} issue(s)")
            
    except Exception as e:
        pipeline_results.append({
            'step': 'Semantic Analysis',
            'status': 'FAIL',
            'details': f'Semantic analysis failed: {str(e)}'
        })
        print(f"  ✗ Semantic analysis failed: {e}")
    
    # Step 4: Performance Test
    print("\n4. Performance Test...")
    import time
    
    # Time the analysis
    start_time = time.time()
    for _ in range(100):  # Run analysis 100 times
        analyser = ZenithAnalyser(test_code)
        analyser.law_description(law_name)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    
    if avg_time < 0.1:  # Less than 100ms per analysis
        pipeline_results.append({
            'step': 'Performance Test',
            'status': 'PASS',
            'details': f'Performance acceptable: {avg_time*1000:.1f}ms per analysis',
            'metrics': {'avg_time_ms': avg_time * 1000}
        })
        print(f"  ✓ Performance test passed: {avg_time*1000:.1f}ms per analysis")
    else:
        pipeline_results.append({
            'step': 'Performance Test',
            'status': 'WARN',
            'details': f'Performance slow: {avg_time*1000:.1f}ms per analysis',
            'metrics': {'avg_time_ms': avg_time * 1000}
        })
        print(f"  ⚠ Performance test warning: {avg_time*1000:.1f}ms per analysis (slow)")
    
    # Step 5: Integration Test
    print("\n5. Integration Test...")
    try:
        # Test round-trip: parse -> unparse -> parse
        unparser = ASTUnparser(analyser.ast)
        unparsed = unparser.unparse()
        
        # Parse the unparsed code
        analyser2 = ZenithAnalyser(unparsed)
        
        # Compare key metrics
        laws1 = analyser.law_analyser.get_law_names()
        laws2 = analyser2.law_analyser.get_law_names()
        
        if set(laws1) == set(laws2):
            pipeline_results.append({
                'step': 'Integration Test',
                'status': 'PASS',
                'details': 'Round-trip parsing successful'
            })
            print("  ✓ Integration test passed")
        else:
            pipeline_results.append({
                'step': 'Integration Test',
                'status': 'FAIL',
                'details': f'Round-trip parsing failed: laws mismatch {laws1} vs {laws2}'
            })
            print("  ✗ Integration test failed: laws mismatch")
            
    except Exception as e:
        pipeline_results.append({
            'step': 'Integration Test',
            'status': 'FAIL',
            'details': f'Integration test failed: {str(e)}'
        })
        print(f"  ✗ Integration test failed: {e}")
    
    # Step 6: Documentation Generation
    print("\n6. Documentation Generation...")
    try:
        # Generate analysis documentation
        analysis = analyser.analyze_corpus()
        
        # Create simple documentation
        doc = {
            'project': 'CI/CD Test Project',
            'analysis_timestamp': datetime.now().isoformat(),
            'summary': analysis['corpus_statistics'],
            'laws': list(analysis['laws'].keys()),
            'targets': list(analysis['targets'].keys())
        }
        
        pipeline_results.append({
            'step': 'Documentation Generation',
            'status': 'PASS',
            'details': 'Documentation generated successfully',
            'documentation': doc
        })
        print("  ✓ Documentation generation passed")
        
    except Exception as e:
        pipeline_results.append({
            'step': 'Documentation Generation',
            'status': 'WARN',
            'details': f'Documentation generation warning: {str(e)}'
        })
        print(f"  ⚠ Documentation generation warning: {e}")
    
    # Pipeline Summary
    print("\n\nPipeline Summary:")
    print("=" * 40)
    
    total_steps = len(pipeline_results)
    passed = sum(1 for r in pipeline_results if r['status'] == 'PASS')
    warnings = sum(1 for r in pipeline_results if r['status'] == 'WARN')
    failed = sum(1 for r in pipeline_results if r['status'] == 'FAIL')
    
    print(f"\nTotal steps: {total_steps}")
    print(f"Passed: {passed}")
    print(f"Warnings: {warnings}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ All pipeline steps completed successfully!")
        overall_status = 'SUCCESS'
    else:
        print(f"\n❌ Pipeline failed with {failed} error(s)")
        overall_status = 'FAILURE'
    
    # Detailed results
    print("\nDetailed Results:")
    for result in pipeline_results:
        status_icon = '✓' if result['status'] == 'PASS' else '⚠' if result['status'] == 'WARN' else '✗'
        print(f"  {status_icon} {result['step']}: {result['status']}")
        if 'details' in result:
            print(f"     {result['details']}")
    
    return {
        'overall_status': overall_status,
        'results': pipeline_results,
        'summary': {
            'total_steps': total_steps,
            'passed': passed,
            'warnings': warnings,
            'failed': failed
        }
    }


def workflow_5_custom_report_generation():
    """Workflow 5: Custom report generation with multiple formats."""
    print("\n" + "=" * 60)
    print("Workflow 5: Custom Report Generation")
    print("=" * 60)
    
    code = """
target report_project:
    key:"Quarterly Report Project"
    dictionnary:
        planning:"Strategic Planning"
        execution:"Project Execution"
        review:"Progress Review"
        delivery:"Project Delivery"
    
    law q1_activities:
        start_date:2024-01-01 at 09:00
        period:480.0 
        Event:
            q1_planning[planning]:"Q1 Planning"
            q1_execution[execution]:"Q1 Execution"
            q1_review[review]:"Q1 Review"
        GROUP:(q1_planning 80.0^40.0 - q1_execution 300.0^40.0 - q1_review 20.0^0)
    end_law
    
    law q2_activities:
        start_date:2024-03-01 at 09:00
        period:480.0  
        Event:
            q2_planning[planning]:"Q2 Planning"
            q2_execution[execution]:"Q2 Execution"
            q2_delivery[delivery]:"Q2 Delivery"
        GROUP:(q2_planning 60.0^40.0 - q2_execution 320.0^40.0 - q2_delivery 20.0^0)
    end_law
end_target
"""
    
    analyser = ZenithAnalyser(code)
    
    print("Generating custom reports...")
    
    # Generate different types of reports
    reports = {}
    
    # 1. Executive Summary Report
    print("\n1. Generating Executive Summary...")
    analysis = analyser.analyze_corpus()
    
    executive_summary = {
        'report_title': 'Project Quarterly Report',
        'generation_date': datetime.now().strftime('%Y-%m-%d'),
        'project_summary': {
            'total_laws': analysis['corpus_statistics']['total_laws'],
            'total_targets': analysis['corpus_statistics']['total_targets'],
            'total_events': analysis['corpus_statistics']['total_events'],
            'total_duration_hours': analysis['corpus_statistics']['total_duration_minutes'] / 60,
            'time_period': 'Q1-Q2 2024'
        },
        'key_findings': [],
        'recommendations': []
    }
    
    # Add key findings from analysis
    for law_name, law_data in analysis['laws'].items():
        if isinstance(law_data, dict) and 'error' not in law_data:
            finding = {
                'law': law_name,
                'duration_hours': law_data['total_duration_minutes'] / 60,
                'efficiency': (law_data['coherence_total_minutes'] / law_data['total_duration_minutes']) * 100
            }
            executive_summary['key_findings'].append(finding)
    
    reports['executive_summary'] = executive_summary
    print(f"  ✓ Executive summary generated with {len(executive_summary['key_findings'])} findings")
    
    # 2. Detailed Technical Report
    print("\n2. Generating Technical Report...")
    
    technical_report = {
        'ast_analysis': analyser.parser.get_ast_summary(analyser.ast),
        'law_analyses': {},
        'validation_results': {
            'syntax': analyser.parser_errors == [],
            'semantic': True,
            'performance': True
        }
    }
    
    for law_name in analyser.law_analyser.get_law_names():
        law_desc = analyser.law_description(law_name)
        technical_report['law_analyses'][law_name] = {
            'metrics': {
                'duration_hours': law_desc['total_duration_minutes'] / 60,
                'event_count': law_desc['event_count'],
                'unique_events': len(law_desc['events']),
                'coherence_ratio': law_desc['coherence_total_minutes'] / law_desc['total_duration_minutes'],
                'dispersal_ratio': law_desc['dispersal_total_minutes'] / law_desc['total_duration_minutes']
            },
            'timeline': [
                {
                    'event': event['event_name'],
                    'start': event['start'],
                    'end': event['end'],
                    'duration_hours': event['duration_minutes'] / 60
                }
                for event in law_desc['simulation'][:5]  # First 5 events
            ]
        }
    
    reports['technical_report'] = technical_report
    print(f"  ✓ Technical report generated with {len(technical_report['law_analyses'])} law analyses")
    
    # 3. Visualization Data Report
    print("\n3. Generating Visualization Data...")
    
    visualization_data = {
        'timeline_data': [],
        'event_distribution': {},
        'duration_breakdown': {}
    }
    
    # Prepare timeline data for visualization
    for law_name in analyser.law_analyser.get_law_names():
        law_desc = analyser.law_description(law_name)
        
        for event in law_desc['simulation']:
            timeline_entry = {
                'law': law_name,
                'event': event['event_name'],
                'start': f"{event['start']['date']}T{event['start']['time']}",
                'end': f"{event['end']['date']}T{event['end']['time']}",
                'duration_hours': event['duration_minutes'] / 60,
                'type': 'event'
            }
            visualization_data['timeline_data'].append(timeline_entry)
        
        # Add law as a group
        law_timeline = {
            'law': law_name,
            'event': 'TOTAL',
            'start': f"{law_desc['start_date']}T{law_desc['start_time']}",
            'end': f"{law_desc['end_datetime']['date']}T{law_desc['end_datetime']['time']}",
            'duration_hours': law_desc['total_duration_minutes'] / 60,
            'type': 'law'
        }
        visualization_data['timeline_data'].append(law_timeline)
    
    # Calculate event distribution
    event_counts = {}
    for law_name in analyser.law_analyser.get_law_names():
        law_desc = analyser.law_description(law_name)
        for event in law_desc['events']:
            event_counts[event] = event_counts.get(event, 0) + 1
    
    visualization_data['event_distribution'] = event_counts
    
    reports['visualization_data'] = visualization_data
    print(f"  ✓ Visualization data generated with {len(visualization_data['timeline_data'])} timeline entries")
    
    # 4. Export reports
    print("\n4. Exporting Reports...")
    
    report_formats = {
        'json': lambda data: json.dumps(data, indent=2),
        'summary_text': lambda data: f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}\nTotal entries: {len(data.get('timeline_data', []))}",
        'csv_snippet': lambda data: "\n".join([','.join(row.keys()) for row in data.get('timeline_data', [][:3])])
    }
    
    exported_reports = {}
    for format_name, formatter in report_formats.items():
        try:
            # Use visualization data for export example
            exported = formatter(visualization_data)
            exported_reports[format_name] = exported[:500] + "..." if len(exported) > 500 else exported
            print(f"  ✓ Exported {format_name} report")
        except Exception as e:
            print(f"  ✗ Failed to export {format_name}: {e}")
    
    # Print report summary
    print("\n\nReport Generation Summary:")
    print("=" * 40)
    print(f"Reports generated: {len(reports)}")
    print(f"Formats exported: {len(exported_reports)}")
    
    for report_name, report_data in reports.items():
        if isinstance(report_data, dict):
            print(f"\n{report_name}:")
            for key, value in report_data.items():
                if isinstance(value, (dict, list)):
                    print(f"  {key}: {len(value)} items")
                else:
                    print(f"  {key}: {value}")
    
    return {
        'reports': reports,
        'exported_formats': list(exported_reports.keys()),
        'sample_data': exported_reports.get('json', '')
    }


def main():
    """Run all custom workflows."""
    print("Zenith Analyser - Custom Workflow Examples")
    print("=" * 60)
    
    try:
        # Run workflows
        workflow_1_batch_processing()
        workflow_2_data_transformation()
        workflow_3_custom_validation_pipeline()
        workflow_4_continuous_integration()
        workflow_5_custom_report_generation()
        
        print("\n" + "=" * 60)
        print("All custom workflows completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError in workflow: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
