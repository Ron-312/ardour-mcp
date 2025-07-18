#!/usr/bin/env python3
"""
Master Test Runner for Ardour MCP Server

This script runs all available tests and generates a comprehensive report.
"""

import sys
import os
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestRunner:
    """Master test runner for all Ardour MCP tests"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.report_data = {}
        
    def print_header(self):
        """Print test suite header"""
        print("=" * 80)
        print("🎵 ARDOUR MCP SERVER - MASTER TEST SUITE")
        print("=" * 80)
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  System: {os.name} - Python {sys.version.split()[0]}")
        print()
        
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        print("🔍 CHECKING PREREQUISITES")
        print("-" * 40)
        
        # Check if server files exist
        required_files = [
            "mcp_server/main.py",
            "mcp_server/osc_client.py",
            "mcp_server/api/plugins.py",
            "tests/test_comprehensive_plugins.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
                
        if missing_files:
            print("❌ Missing required files:")
            for file_path in missing_files:
                print(f"   - {file_path}")
            return False
            
        print("✅ All required files present")
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=3)
            if response.status_code == 200:
                print("✅ MCP Server is running")
                server_running = True
            else:
                print("⚠️  MCP Server returned unexpected status")
                server_running = False
        except Exception:
            print("❌ MCP Server is not running")
            server_running = False
            
        if not server_running:
            print()
            print("💡 TO START THE SERVER:")
            print("   python -m mcp_server.main")
            print()
            return False
            
        return True
        
    def run_test_module(self, test_name: str, test_file: str, timeout: int = 300) -> Dict[str, Any]:
        """Run a specific test module"""
        print(f"\n🧪 RUNNING: {test_name}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Run the test as a subprocess with proper environment and encoding
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()
            env['PYTHONIOENCODING'] = 'utf-8'  # Force UTF-8 encoding
            
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd(),
                env=env,
                encoding='utf-8',
                errors='replace'  # Replace problematic characters instead of failing
            )
            
            execution_time = time.time() - start_time
            
            # Parse output for results
            output_lines = result.stdout.split('\n')
            error_lines = result.stderr.split('\n') if result.stderr else []
            
            # Look for success indicators in output
            success_indicators = [
                "SUCCESS", "EXCELLENT", "✅", "PASSED", "COMPLETED"
            ]
            
            failure_indicators = [
                "FAILED", "ERROR", "❌", "POOR", "CRITICAL"
            ]
            
            output_text = result.stdout.lower()
            
            success_count = sum(1 for indicator in success_indicators if indicator.lower() in output_text)
            failure_count = sum(1 for indicator in failure_indicators if indicator.lower() in output_text)
            
            # Determine overall status
            if result.returncode == 0 and success_count > failure_count:
                status = "PASSED"
            elif result.returncode == 0:
                status = "PARTIAL"
            else:
                status = "FAILED"
                
            # Extract metrics if available
            metrics = self._extract_metrics(output_lines)
            
            test_result = {
                "status": status,
                "execution_time": execution_time,
                "return_code": result.returncode,
                "output_lines": len(output_lines),
                "error_lines": len(error_lines),
                "success_indicators": success_count,
                "failure_indicators": failure_count,
                "metrics": metrics,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Print summary
            status_emoji = "✅" if status == "PASSED" else "⚠️" if status == "PARTIAL" else "❌"
            print(f"{status_emoji} {test_name}: {status} in {execution_time:.1f}s")
            
            if metrics:
                for key, value in metrics.items():
                    print(f"   📊 {key}: {value}")
                    
            return test_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏰ {test_name}: TIMEOUT after {timeout}s")
            return {
                "status": "TIMEOUT",
                "execution_time": execution_time,
                "return_code": -1,
                "error": f"Test timed out after {timeout} seconds"
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ {test_name}: ERROR - {str(e)}")
            return {
                "status": "ERROR",
                "execution_time": execution_time,
                "return_code": -1,
                "error": str(e)
            }
            
    def _extract_metrics(self, output_lines: List[str]) -> Dict[str, Any]:
        """Extract metrics from test output"""
        metrics = {}
        
        for line in output_lines:
            # Look for metric patterns
            line = line.strip()
            
            # Plugin/parameter counts
            if "plugins discovered:" in line.lower():
                try:
                    metrics["plugins_discovered"] = int(line.split(":")[-1].strip())
                except:
                    pass
                    
            if "parameters discovered:" in line.lower():
                try:
                    metrics["parameters_discovered"] = int(line.split(":")[-1].strip())
                except:
                    pass
                    
            # Score patterns
            if "score:" in line.lower() and "/" in line:
                try:
                    score_part = line.split("score:")[-1].strip()
                    if "/" in score_part:
                        score = score_part.split("/")[0].strip()
                        metrics["test_score"] = int(score)
                except:
                    pass
                    
            # Time patterns
            if " in " in line and "s" in line:
                try:
                    if "discovery" in line.lower():
                        time_part = line.split(" in ")[-1].split("s")[0].strip()
                        metrics["discovery_time"] = float(time_part)
                except:
                    pass
                    
        return metrics
        
    def run_all_tests(self):
        """Run all available tests"""
        self.start_time = time.time()
        
        # Define test suite with shorter timeouts
        test_suite = [
            {
                "name": "Transport & Basic Controls",
                "file": "tests/test_transport_api.py",
                "timeout": 30,
                "description": "Basic transport control and OSC connection"
            },
            {
                "name": "Track Control", 
                "file": "tests/test_phase2_features.py", 
                "timeout": 45,
                "description": "Track fader, mute, solo, pan control"
            },
            {
                "name": "Send/Aux Control",
                "file": "tests/test_phase3_sends.py",
                "timeout": 45,
                "description": "Send levels and aux routing"
            },
            {
                "name": "Recording Controls",
                "file": "tests/test_recording_controls.py",
                "timeout": 45,
                "description": "Master and track recording controls"
            },
            {
                "name": "Plugin Discovery",
                "file": "tests/test_plugin_discovery.py",
                "timeout": 60,
                "description": "Basic plugin discovery and listing"
            },
            {
                "name": "Real Plugin Discovery",
                "file": "tests/test_real_plugin_discovery.py",
                "timeout": 60,
                "description": "Real plugin discovery with OSC feedback"
            },
            {
                "name": "Dynamic Parameter Mapping",
                "file": "tests/test_dynamic_parameter_mapping.py",
                "timeout": 90,
                "description": "Dynamic plugin parameter mapping system"
            },
            {
                "name": "Smart Parameter Control",
                "file": "tests/test_smart_parameters.py",
                "timeout": 60,
                "description": "Smart parameter value conversion"
            },
            {
                "name": "Plugin Control",
                "file": "tests/test_plugin_control.py",
                "timeout": 60,
                "description": "Plugin enable/disable and parameter control"
            },
            {
                "name": "Comprehensive Plugin Tests",
                "file": "tests/test_comprehensive_plugins.py",
                "timeout": 120,
                "description": "Complete plugin system validation"
            },
            {
                "name": "Full Plugin Workflow",
                "file": "tests/test_full_plugin_workflow.py", 
                "timeout": 90,
                "description": "End-to-end plugin workflow testing"
            }
        ]
        
        print(f"🚀 RUNNING {len(test_suite)} TEST SUITES")
        print("=" * 80)
        
        # Run each test
        for i, test_config in enumerate(test_suite, 1):
            print(f"\n[{i}/{len(test_suite)}] {test_config['name']}")
            print(f"📝 {test_config['description']}")
            print(f"⏱️  Timeout: {test_config['timeout']}s")
            
            # Check if test file exists
            if not os.path.exists(test_config['file']):
                print(f"⚠️ Test file not found: {test_config['file']}")
                self.test_results[test_config['name']] = {
                    "status": "SKIPPED",
                    "error": "Test file not found",
                    "execution_time": 0
                }
                continue
                
            # Show progress
            print(f"🔄 Running test... (will timeout after {test_config['timeout']}s)")
            
            # Run the test
            result = self.run_test_module(
                test_config['name'],
                test_config['file'],
                test_config['timeout']
            )
            
            self.test_results[test_config['name']] = result
            
            # Show immediate result
            status_emoji = {
                'PASSED': '✅',
                'PARTIAL': '⚠️',
                'FAILED': '❌',
                'SKIPPED': '⏭️',
                'TIMEOUT': '⏰',
                'ERROR': '💥'
            }.get(result.get('status', 'UNKNOWN'), '❓')
            
            print(f"{status_emoji} Test completed: {result.get('status', 'UNKNOWN')}")
            
            # Short delay between tests
            time.sleep(0.5)
            
        self.end_time = time.time()
        
    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'PASSED'])
        partial_tests = len([r for r in self.test_results.values() if r.get('status') == 'PARTIAL'])
        failed_tests = len([r for r in self.test_results.values() if r.get('status') == 'FAILED'])
        skipped_tests = len([r for r in self.test_results.values() if r.get('status') == 'SKIPPED'])
        
        print(f"🎯 EXECUTION SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ⚠️  Partial: {partial_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⏭️  Skipped: {skipped_tests}")
        print(f"   ⏱️  Total Time: {total_time:.1f}s")
        
        # Success rate
        success_rate = (passed_tests + partial_tests * 0.5) / total_tests * 100 if total_tests > 0 else 0
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        
        for test_name, result in self.test_results.items():
            status = result.get('status', 'UNKNOWN')
            exec_time = result.get('execution_time', 0)
            
            status_emoji = {
                'PASSED': '✅',
                'PARTIAL': '⚠️',
                'FAILED': '❌',
                'SKIPPED': '⏭️',
                'TIMEOUT': '⏰',
                'ERROR': '💥'
            }.get(status, '❓')
            
            print(f"   {status_emoji} {test_name}: {status} ({exec_time:.1f}s)")
            
            # Show metrics if available
            metrics = result.get('metrics', {})
            if metrics:
                for key, value in metrics.items():
                    print(f"      📊 {key.replace('_', ' ').title()}: {value}")
                    
            # Show errors if any
            if result.get('error'):
                print(f"      💬 Error: {result['error']}")
                
        # System assessment
        print(f"\n🎯 SYSTEM ASSESSMENT:")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: Ardour MCP Server is working perfectly!")
            print("   All major functionality is operational")
        elif success_rate >= 75:
            print("✅ GOOD: Ardour MCP Server is working well")
            print("   Most functionality is operational with minor issues")
        elif success_rate >= 60:
            print("⚠️ FAIR: Ardour MCP Server has some issues")
            print("   Core functionality works but needs improvement")
        elif success_rate >= 40:
            print("❌ POOR: Ardour MCP Server has significant issues")
            print("   Many features are not working correctly")
        else:
            print("💥 CRITICAL: Ardour MCP Server is not functional")
            print("   Major system components are failing")
            
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if failed_tests > 0:
            print("   1. Check server logs for error details")
            print("   2. Verify Ardour is running with OSC enabled")
            print("   3. Ensure plugins are loaded for plugin tests")
            
        if skipped_tests > 0:
            print("   1. Install missing test files")
            print("   2. Check file permissions")
            
        if success_rate < 80:
            print("   1. Run individual test files to debug specific issues")
            print("   2. Check Ardour OSC configuration (port 3819)")
            print("   3. Verify all API endpoints are accessible")
            
        # Generate JSON report
        self.save_json_report()
        
        print(f"\n📄 REPORTS GENERATED:")
        print(f"   📊 Console Report: Above")
        print(f"   📋 JSON Report: test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        print(f"   📝 Individual Test Outputs: Available in test results")
        
    def save_json_report(self):
        """Save detailed JSON report"""
        report_data = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_time": self.end_time - self.start_time if self.end_time and self.start_time else 0,
                "python_version": sys.version,
                "platform": os.name
            },
            "summary": {
                "total_tests": len(self.test_results),
                "passed": len([r for r in self.test_results.values() if r.get('status') == 'PASSED']),
                "partial": len([r for r in self.test_results.values() if r.get('status') == 'PARTIAL']),
                "failed": len([r for r in self.test_results.values() if r.get('status') == 'FAILED']),
                "skipped": len([r for r in self.test_results.values() if r.get('status') == 'SKIPPED'])
            },
            "test_results": self.test_results
        }
        
        filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"✅ JSON report saved: {filename}")
        except Exception as e:
            print(f"❌ Failed to save JSON report: {e}")
            
    def run(self, quick_mode=False):
        """Main execution method"""
        self.print_header()
        
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix issues and try again.")
            return False
            
        if quick_mode:
            print("\n🚀 Starting QUICK test execution (essential tests only)...")
        else:
            print("\n🚀 Starting FULL test execution...")
        self.run_all_tests(quick_mode)
        self.generate_report()
        
        return True
        
    def run_all_tests(self, quick_mode=False):
        """Run all available tests"""
        self.start_time = time.time()
        
        # Define test suite with shorter timeouts
        full_test_suite = [
            {
                "name": "Transport & Basic Controls",
                "file": "tests/test_current_server.py",
                "timeout": 30,
                "description": "Basic transport control and OSC connection",
                "essential": True
            },
            {
                "name": "Track Control", 
                "file": "tests/test_phase2_features.py", 
                "timeout": 45,
                "description": "Track fader, mute, solo, pan control",
                "essential": False
            },
            {
                "name": "Send/Aux Control",
                "file": "tests/test_phase3_sends.py",
                "timeout": 45,
                "description": "Send levels and aux routing",
                "essential": False
            },
            {
                "name": "Recording Controls",
                "file": "tests/test_recording_controls.py",
                "timeout": 45,
                "description": "Master and track recording controls",
                "essential": True
            },
            {
                "name": "Plugin Discovery",
                "file": "tests/test_plugin_discovery.py",
                "timeout": 60,
                "description": "Basic plugin discovery and listing",
                "essential": True
            },
            {
                "name": "Real Plugin Discovery",
                "file": "tests/test_real_plugin_discovery.py",
                "timeout": 60,
                "description": "Real plugin discovery with OSC feedback",
                "essential": False
            },
            {
                "name": "Dynamic Parameter Mapping",
                "file": "tests/test_dynamic_parameter_mapping.py",
                "timeout": 90,
                "description": "Dynamic plugin parameter mapping system",
                "essential": False
            },
            {
                "name": "Smart Parameter Control",
                "file": "tests/test_smart_parameters.py",
                "timeout": 60,
                "description": "Smart parameter value conversion",
                "essential": True
            },
            {
                "name": "Plugin Control",
                "file": "tests/test_plugin_control.py",
                "timeout": 60,
                "description": "Plugin enable/disable and parameter control",
                "essential": False
            },
            {
                "name": "Comprehensive Plugin Tests",
                "file": "tests/test_comprehensive_plugins.py",
                "timeout": 120,
                "description": "Complete plugin system validation",
                "essential": False
            },
            {
                "name": "Full Plugin Workflow",
                "file": "tests/test_full_plugin_workflow.py", 
                "timeout": 90,
                "description": "End-to-end plugin workflow testing",
                "essential": False
            }
        ]
        
        # Filter tests based on mode
        if quick_mode:
            test_suite = [test for test in full_test_suite if test.get("essential", False)]
            print(f"🚀 RUNNING {len(test_suite)} ESSENTIAL TESTS (Quick Mode)")
        else:
            test_suite = full_test_suite
            print(f"🚀 RUNNING {len(test_suite)} TEST SUITES (Full Mode)")
            
        print("=" * 80)
        
        # Run each test
        for i, test_config in enumerate(test_suite, 1):
            print(f"\n[{i}/{len(test_suite)}] {test_config['name']}")
            print(f"📝 {test_config['description']}")
            print(f"⏱️  Timeout: {test_config['timeout']}s")
            
            # Check if test file exists
            if not os.path.exists(test_config['file']):
                print(f"⚠️ Test file not found: {test_config['file']}")
                self.test_results[test_config['name']] = {
                    "status": "SKIPPED",
                    "error": "Test file not found",
                    "execution_time": 0
                }
                continue
                
            # Show progress
            print(f"🔄 Running test... (will timeout after {test_config['timeout']}s)")
            
            # Run the test
            result = self.run_test_module(
                test_config['name'],
                test_config['file'],
                test_config['timeout']
            )
            
            self.test_results[test_config['name']] = result
            
            # Show immediate result
            status_emoji = {
                'PASSED': '✅',
                'PARTIAL': '⚠️',
                'FAILED': '❌',
                'SKIPPED': '⏭️',
                'TIMEOUT': '⏰',
                'ERROR': '💥'
            }.get(result.get('status', 'UNKNOWN'), '❓')
            
            print(f"{status_emoji} Test completed: {result.get('status', 'UNKNOWN')}")
            
            # Short delay between tests
            time.sleep(0.5)
            
        self.end_time = time.time()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Ardour MCP Server tests')
    parser.add_argument('--quick', action='store_true', help='Run only essential tests (faster)')
    args = parser.parse_args()
    
    runner = TestRunner()
    success = runner.run(quick_mode=args.quick)
    
    if success:
        mode = "QUICK" if args.quick else "FULL"
        print(f"\n🎉 {mode} TEST EXECUTION COMPLETED!")
        print(f"📊 Check the report above for detailed results")
    else:
        print(f"\n❌ TEST EXECUTION FAILED!")
        print(f"🔧 Fix prerequisites and try again")
        
    return success

if __name__ == "__main__":
    main()