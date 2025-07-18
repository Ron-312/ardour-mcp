# Ardour MCP Server - Testing Guide

This guide explains how to test the Ardour MCP Server using the comprehensive test suite.

## Quick Start

### 1. Check System Status
```bash
python test_status.py
```
This shows:
- ✅ Is the MCP server running?
- ✅ Is Ardour OSC connection working? 
- ✅ Which test files are available?
- ✅ System readiness score

### 2. Run Essential Tests (Quick)
```bash
python run_all_tests.py --quick
```
Runs only the most important tests (~3-5 minutes):
- Transport & Basic Controls
- Recording Controls  
- Plugin Discovery
- Smart Parameter Control

### 3. Run All Tests (Full)
```bash
python run_all_tests.py
```
Runs the complete test suite (~10-15 minutes):
- All quick tests plus advanced features
- Dynamic parameter mapping
- Comprehensive plugin workflows
- Error handling validation

## Prerequisites

### MCP Server Running
```bash
python -m mcp_server.main
```
Should show:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
OSC listener started on port 3820
```

### Ardour Setup
1. **Start Ardour** with a session
2. **Enable OSC**: Edit → Preferences → Control Surfaces → OSC
3. **Set OSC port**: 3819 (default)
4. **Load some plugins** on tracks (for plugin tests)

## Individual Test Files (By Implementation Order)

Run tests in this order - from basic to advanced features:

### Phase 1: Basic Functionality (Start Here)

```bash
# 1. Basic server connectivity and transport
python tests/test_current_server.py

# 2. Environment and configuration
python tests/test_env.py

# 3. Configuration testing
python tests/test_config.py

# 4. Direct OSC communication
python tests/test_direct_osc.py

# 5. OSC client functionality  
python tests/test_osc_client.py

# 6. OSC format testing
python tests/test_osc_formats.py

# 7. Transport API testing
python tests/test_transport_api.py
```

### Phase 2: Core Features

```bash
# 8. Track control (faders, mute, solo, pan)
python tests/test_phase2_features.py

# 9. Selection operations (strip/plugin selection and control)
python tests/test_selection_operations.py

# 10. Send/aux control
python tests/test_phase3_sends.py

# 11. Recording controls (master and track-level)
python tests/test_recording_controls.py

# 12. New features testing
python tests/test_new_features.py
```

### Phase 3: Plugin System (Basic)

```bash
# 13. Basic plugin discovery
python tests/test_plugin_discovery.py

# 14. Plugin control (enable/disable/bypass)
python tests/test_plugin_control.py

# 15. Smart parameter conversion (dB, Hz, ratios)
python tests/test_smart_parameters.py
```

### Phase 4: Advanced Plugin Features

```bash
# 16. Real plugin discovery with OSC feedback
python tests/test_real_plugin_discovery.py

# 17. Dynamic parameter mapping system
python tests/test_dynamic_parameter_mapping.py

# 18. Comprehensive plugin system validation
python tests/test_comprehensive_plugins.py

# 19. Full end-to-end plugin workflow
python tests/test_full_plugin_workflow.py
```

### Phase 5: Development & Testing Tools

```bash
# 20. Server startup and configuration
python tests/test_server_startup.py

# 21. Working server validation
python tests/test_working_server.py

# 22. Ardour connection testing
python tests/test_ardour_connection.py

# 23. OSC mock testing (development only)
python tests/test_osc_mock.py
```

### Copy-Paste Quick Test Sequence

**Basic Functionality Test (Run First):**
```bash
python tests/test_current_server.py && python tests/test_env.py && python tests/test_direct_osc.py && python tests/test_osc_client.py
```

**Core Features Test (Run Second):**
```bash
python tests/test_transport_api.py && python tests/test_phase2_features.py && python tests/test_selection_operations.py && python tests/test_recording_controls.py
```

**Plugin System Test (Run Third):**
```bash
python tests/test_plugin_discovery.py && python tests/test_smart_parameters.py && python tests/test_plugin_control.py
```

**Advanced Features Test (Run Last):**
```bash
python tests/test_real_plugin_discovery.py && python tests/test_dynamic_parameter_mapping.py && python tests/test_comprehensive_plugins.py
```

**Full Test Sequence (All Tests in Order):**
```bash
python tests/test_current_server.py && \
python tests/test_env.py && \
python tests/test_direct_osc.py && \
python tests/test_phase2_features.py && \
python tests/test_selection_operations.py && \
python tests/test_phase3_sends.py && \
python tests/test_recording_controls.py && \
python tests/test_plugin_discovery.py && \
python tests/test_plugin_control.py && \
python tests/test_smart_parameters.py && \
python tests/test_real_plugin_discovery.py && \
python tests/test_dynamic_parameter_mapping.py && \
python tests/test_comprehensive_plugins.py && \
python tests/test_full_plugin_workflow.py
```

## Understanding Test Results

### Status Codes
- ✅ **PASSED** - Test completed successfully
- ⚠️ **PARTIAL** - Some features work, some don't
- ❌ **FAILED** - Test failed with errors
- ⏰ **TIMEOUT** - Test took too long (likely server issue)
- ⏭️ **SKIPPED** - Test file missing or prerequisites not met

### Success Rates
- **90-100%** - 🎉 Excellent: System working perfectly
- **75-89%** - ✅ Good: Minor issues, mostly functional
- **60-74%** - ⚠️ Fair: Some problems need attention
- **40-59%** - ❌ Poor: Significant issues
- **<40%** - 💥 Critical: Major system problems

### Generated Reports
- **Console Report** - Immediate results shown in terminal
- **JSON Report** - Detailed machine-readable file (`test_report_YYYYMMDD_HHMMSS.json`)

## Common Issues & Solutions

### Server Not Running
```
❌ MCP Server is not running
```
**Solution**: Start the server first
```bash
python -m mcp_server.main
```

### Ardour Not Connected
```
❌ Ardour OSC connection not working
```
**Solutions**:
1. Check Ardour OSC settings (port 3819)
2. Restart Ardour
3. Check firewall/network issues

### No Plugins Found
```
⚠️ 0 plugins discovered
```
**Solutions**:
1. Load some plugins in Ardour tracks
2. Check OSC communication in Ardour logs
3. Verify plugin types are supported

### Tests Timeout
```
⏰ Test timed out after 30s
```
**Solutions**:
1. Check server performance
2. Restart MCP server
3. Check system resources

## Test Coverage

### Transport Control ✅
- Play, stop, rewind, fast-forward
- Loop, markers, speed control
- Transport position

### Track Control ✅  
- Fader, gain, pan
- Mute, solo, record enable
- Track naming

### Recording Control ✅
- Global recording enable/disable
- Punch recording (in/out)
- Input monitoring
- Track-specific recording

### Plugin System ✅
- Plugin discovery and listing
- Parameter discovery and mapping
- Plugin enable/disable/bypass
- Smart parameter control (dB, Hz, ratios)
- Dynamic parameter mapping
- Real-time plugin feedback

### Selection Operations ✅
- Strip selection (GUI and local expansion)
- Selected strip controls (gain, mute, solo, pan)
- Plugin selection and control  
- Group operations and sharing
- Automation and touch controls
- Send operations for selected strips

### Send/Aux Control ✅
- Send levels and routing
- Aux bus control
- Send enable/disable

### Error Handling ✅
- Invalid requests
- Network timeouts
- Parameter validation
- Helpful error messages

## Performance Benchmarks

Expected performance (with server running):
- **Plugin Discovery**: <2 seconds per track
- **Parameter Discovery**: <3 seconds per plugin  
- **Parameter Control**: <0.5 seconds per parameter
- **Transport Commands**: <0.1 seconds
- **Full Test Suite**: <15 minutes

## Debugging Failed Tests

### 1. Check Individual Test
```bash
python tests/test_transport_api.py
```

### 2. Check Server Logs
Look for OSC messages and errors in server terminal

### 3. Check Ardour Logs
Window → Logging in Ardour - look for OSC messages

### 4. Test Direct API
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/transport/play
```

### 5. Test OSC Communication
Use OSC debugging tools or check Ardour's OSC log

## Contributing Test Cases

To add new tests:

1. **Create test file**: `tests/test_new_feature.py`
2. **Add to test suite**: Update `run_all_tests.py`
3. **Follow patterns**: Use existing tests as templates
4. **Include assertions**: Verify expected behavior
5. **Add error cases**: Test invalid inputs
6. **Document expectations**: What should work/fail

## Test File Structure

```python
#!/usr/bin/env python3
"""
Test script for [Feature Name]
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_feature():
    """Test specific feature"""
    # Test code here
    pass

def main():
    """Main test execution"""
    print("🧪 Testing [Feature Name]")
    test_feature()
    print("✅ Tests completed")

if __name__ == "__main__":
    main()
```

## Automation

### CI/CD Integration
The test runner can be integrated into CI/CD pipelines:

```bash
# Quick smoke test
python run_all_tests.py --quick || exit 1

# Full validation
python run_all_tests.py || exit 1
```

### Scheduled Testing
Run tests periodically to catch regressions:

```bash
# Daily quick test
0 9 * * * cd /path/to/ardour-mcp && python run_all_tests.py --quick

# Weekly full test  
0 10 * * 0 cd /path/to/ardour-mcp && python run_all_tests.py
```

---

## Summary Commands

```bash
# Quick system check
python test_status.py

# Essential tests (fast)
python run_all_tests.py --quick

# Complete validation (thorough)
python run_all_tests.py

# Individual test
python tests/test_[category].py
```

Happy testing! 🎵