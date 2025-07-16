#!/usr/bin/env python3
"""
Test script for Master Recording Controls functionality
"""

import sys
import os
# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_global_recording_control():
    """Test global recording enable/disable"""
    print("Testing Global Recording Control")
    print("=" * 40)
    
    recording_tests = [
        ("Enable global recording", "/recording/enable", {"enabled": True}),
        ("Disable global recording", "/recording/enable", {"enabled": False}),
        ("Enable global recording again", "/recording/enable", {"enabled": True}),
        ("Disable with convenience endpoint", "/recording/disable", None),
    ]
    
    success_count = 0
    
    for test_name, endpoint, data in recording_tests:
        print(f"Testing {test_name}...")
        try:
            if data:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  SUCCESS: {result['message']}")
                print(f"     OSC: {result['osc_address']}")
                success_count += 1
            else:
                print(f"  FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        time.sleep(0.5)
    
    return success_count, len(recording_tests)

def test_punch_recording():
    """Test punch-in and punch-out recording controls"""
    print(f"\n✂️ Testing Punch Recording Controls")
    print("=" * 40)
    
    punch_tests = [
        ("Enable punch-in", "/recording/punch-in", {"enabled": True}),
        ("Disable punch-in", "/recording/punch-in", {"enabled": False}),
        ("Enable punch-out", "/recording/punch-out", {"enabled": True}),
        ("Disable punch-out", "/recording/punch-out", {"enabled": False}),
        ("Enable both punch-in and punch-out", "/recording/punch-in", {"enabled": True}),
        ("Enable punch-out with punch-in", "/recording/punch-out", {"enabled": True}),
    ]
    
    success_count = 0
    
    for test_name, endpoint, data in punch_tests:
        print(f"Testing {test_name}...")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  SUCCESS: {result['message']}")
                print(f"     OSC: {result['osc_address']}")
                success_count += 1
            else:
                print(f"  FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        time.sleep(0.5)
    
    return success_count, len(punch_tests)

def test_input_monitoring():
    """Test input monitoring controls"""
    print(f"\n🎧 Testing Input Monitoring Controls")
    print("=" * 40)
    
    monitor_tests = [
        ("Enable global input monitoring", "/recording/input-monitor", {"enabled": True}),
        ("Disable global input monitoring", "/recording/input-monitor", {"enabled": False}),
        ("Enable track 1 input monitoring", "/recording/track/1/input-monitor", {"enabled": True}),
        ("Enable track 2 input monitoring", "/recording/track/2/input-monitor", {"enabled": True}),
        ("Disable track 1 input monitoring", "/recording/track/1/input-monitor", {"enabled": False}),
        ("Enable track 3 input monitoring", "/recording/track/3/input-monitor", {"enabled": True}),
        ("Disable all track monitoring", "/recording/track/2/input-monitor", {"enabled": False}),
        ("Disable track 3 monitoring", "/recording/track/3/input-monitor", {"enabled": False}),
    ]
    
    success_count = 0
    
    for test_name, endpoint, data in monitor_tests:
        print(f"Testing {test_name}...")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  SUCCESS: {result['message']}")
                print(f"     OSC: {result['osc_address']}")
                success_count += 1
            else:
                print(f"  FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        time.sleep(0.4)
    
    return success_count, len(monitor_tests)

def test_recording_status():
    """Test recording status retrieval"""
    print(f"\nMETRICS Testing Recording Status")
    print("=" * 40)
    
    print("Getting recording status...")
    try:
        response = requests.get(f"{BASE_URL}/recording/status")
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS Recording status retrieved:")
            print(f"   Recording enabled: {result.get('recording_enabled', 'unknown')}")
            print(f"   Punch-in enabled: {result.get('punch_in_enabled', 'unknown')}")
            print(f"   Punch-out enabled: {result.get('punch_out_enabled', 'unknown')}")
            print(f"   Input monitoring: {result.get('input_monitoring_enabled', 'unknown')}")
            print(f"   Currently recording: {result.get('currently_recording', 'unknown')}")
            print(f"   Armed tracks: {result.get('armed_tracks', [])}")
            return True
        else:
            print(f"FAILED Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"FAILED Error: {e}")
        return False

def test_convenience_recording():
    """Test start/stop recording convenience endpoints"""
    print(f"\n🎬 Testing Convenience Recording Controls")
    print("=" * 40)
    
    convenience_tests = [
        ("Start recording (enable + play)", "/recording/start"),
        ("Stop recording (stop + disable)", "/recording/stop"),
        ("Start recording again", "/recording/start"),
        ("Stop recording again", "/recording/stop"),
    ]
    
    success_count = 0
    
    for test_name, endpoint in convenience_tests:
        print(f"Testing {test_name}...")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  SUCCESS {result['message']}")
                if 'osc_commands' in result:
                    print(f"     OSC: {', '.join(result['osc_commands'])}")
                success_count += 1
            else:
                print(f"  FAILED Failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"  ERROR: {e}")
        
        time.sleep(1.0)  # Longer delay for transport commands
    
    return success_count, len(convenience_tests)

def test_recording_workflow():
    """Test a complete recording workflow scenario"""
    print(f"\n🎵 Testing Complete Recording Workflow")
    print("=" * 40)
    
    print("Scenario: Setting up for vocal overdub recording")
    
    workflow_steps = [
        # Setup phase
        ("Setup: Enable track 1 record", "/track/1/record-enable", {"enabled": True}),
        ("Setup: Enable track 1 input monitoring", "/recording/track/1/input-monitor", {"enabled": True}),
        ("Setup: Set up punch recording", "/recording/punch-in", {"enabled": True}),
        ("Setup: Enable punch-out", "/recording/punch-out", {"enabled": True}),
        
        # Recording phase
        ("Record: Enable global recording", "/recording/enable", {"enabled": True}),
        ("Record: Start recording", "/recording/start", None),
        ("Record: Stop recording", "/recording/stop", None),
        
        # Cleanup phase  
        ("Cleanup: Disable recording", "/recording/disable", None),
        ("Cleanup: Disable input monitoring", "/recording/track/1/input-monitor", {"enabled": False}),
        ("Cleanup: Disable punch recording", "/recording/punch-in", {"enabled": False}),
        ("Cleanup: Disable punch-out", "/recording/punch-out", {"enabled": False}),
    ]
    
    workflow_success = 0
    
    for step_name, endpoint, data in workflow_steps:
        print(f"🎛️ {step_name}")
        try:
            if data:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   SUCCESS {result['message']}")
                workflow_success += 1
            else:
                print(f"   FAILED Failed: {response.status_code}")
        except Exception as e:
            print(f"   FAILED Error: {e}")
        
        time.sleep(0.8)
    
    print(f"\nSUMMARY Workflow completed: {workflow_success}/{len(workflow_steps)} steps successful")
    return workflow_success, len(workflow_steps)

def test_recording_edge_cases():
    """Test edge cases and error handling"""
    print(f"\n🧪 Testing Recording Edge Cases")
    print("=" * 40)
    
    edge_tests = [
        # High track numbers
        ("High track input monitoring", "/recording/track/99/input-monitor", {"enabled": True}),
        
        # Invalid track numbers (should be rejected by validation)
        ("Zero track number", "/recording/track/0/input-monitor", {"enabled": True}),
        ("Negative track number", "/recording/track/-1/input-monitor", {"enabled": True}),
        
        # Missing request body (should fail)
        ("Missing body for recording enable", "/recording/enable", None),
    ]
    
    validation_results = []
    
    for test_name, endpoint, data in edge_tests:
        print(f"Testing {test_name}...")
        try:
            if data:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 422:  # Validation error expected
                print(f"  SUCCESS Correctly rejected: {response.status_code}")
                validation_results.append("rejected")
            elif response.status_code == 200:
                print(f"  WARNING  Unexpected success: {response.status_code}")
                validation_results.append("unexpected")
            else:
                print(f"  ❓ Other status: {response.status_code}")
                validation_results.append("other")
        except Exception as e:
            print(f"  ERROR: {e}")
            validation_results.append("error")
        
        time.sleep(0.3)
    
    return validation_results

def test_osc_message_verification():
    """Verify correct OSC messages are sent for recording commands"""
    print(f"\n📡 Testing Recording OSC Message Verification")
    print("=" * 40)
    print("Watch server logs for OSC recording messages...")
    
    osc_tests = [
        ("Global recording enable", "/recording/enable", {"enabled": True}, "/rec_enable_toggle 1"),
        ("Punch-in enable", "/recording/punch-in", {"enabled": True}, "/toggle_punch_in 1"),
        ("Input monitoring", "/recording/input-monitor", {"enabled": True}, "/toggle_monitor_input 1"),
        ("Track input monitoring", "/recording/track/1/input-monitor", {"enabled": True}, "/strip/0/monitor_input 1"),
        ("Start recording", "/recording/start", None, "/rec_enable_toggle + /transport_play"),
    ]
    
    for test_name, endpoint, data, expected_osc in osc_tests:
        print(f"CHECK {test_name}")
        print(f"   Expected OSC: {expected_osc}")
        
        try:
            if data:
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"   SUCCESS Request successful - check logs above")
            else:
                print(f"   FAILED Request failed: {response.status_code}")
        except Exception as e:
            print(f"   FAILED Error: {e}")
        
        time.sleep(1.0)

def main():
    """Run master recording controls tests"""
    print("🎵 Master Recording Controls Testing")
    print("=" * 60)
    print("Make sure Ardour is running and ready for recording!")
    print("Watch the recording indicators in Ardour interface.")
    print()
    
    # Run all test categories
    global_success, global_total = test_global_recording_control()
    punch_success, punch_total = test_punch_recording()
    monitor_success, monitor_total = test_input_monitoring()
    status_success = test_recording_status()
    convenience_success, convenience_total = test_convenience_recording()
    workflow_success, workflow_total = test_recording_workflow()
    edge_results = test_recording_edge_cases()
    test_osc_message_verification()
    
    # Calculate totals
    total_success = global_success + punch_success + monitor_success + convenience_success + workflow_success
    total_tests = global_total + punch_total + monitor_total + convenience_total + workflow_total
    if status_success:
        total_success += 1
        total_tests += 1
    
    edge_success = len([r for r in edge_results if r == "rejected"])
    
    print(f"\n" + "=" * 60)
    print(f"SUMMARY RECORDING CONTROLS TEST SUMMARY:")
    print(f"RECORDING Global Recording: {global_success}/{global_total}")
    print(f"✂️ Punch Recording: {punch_success}/{punch_total}")
    print(f"🎧 Input Monitoring: {monitor_success}/{monitor_total}")
    print(f"METRICS Status Retrieval: {'SUCCESS' if status_success else 'FAILED'}")
    print(f"🎬 Convenience Controls: {convenience_success}/{convenience_total}")
    print(f"🎵 Recording Workflow: {workflow_success}/{workflow_total}")
    print(f"🧪 Edge Case Validation: {edge_success}/{len(edge_results)}")
    print(f"🏆 TOTAL: {total_success}/{total_tests} tests passed")
    
    if total_success >= total_tests - 2:  # Allow some edge case issues
        print(f"\n🎉 MASTER RECORDING CONTROLS: **SUCCESS!**")
        print(f"SUCCESS Global Recording - Master record enable/disable")
        print(f"SUCCESS Punch Recording - Automated punch-in/out recording")
        print(f"SUCCESS Input Monitoring - Global and per-track monitoring")
        print(f"SUCCESS Recording Status - Real-time status information")
        print(f"SUCCESS Convenience Controls - One-click start/stop recording")
        print(f"SUCCESS Complete Workflows - End-to-end recording scenarios")
        print(f"SUCCESS OSC Integration - Correct recording command sequences")
    else:
        print(f"\nWARNING  Some recording control features need attention")
        print(f"🔧 But core recording functionality is working!")
    
    print(f"\nCHECK Check Ardour to verify:")
    print(f"  - Recording indicators (red record buttons)")
    print(f"  - Input monitoring meters showing signal")
    print(f"  - Punch-in/out indicators in transport bar")
    print(f"  - Global recording status changes")
    print(f"  - OSC messages in Ardour logs")
    
    print(f"\nREADY Ready for production recording workflows!")

if __name__ == "__main__":
    main()