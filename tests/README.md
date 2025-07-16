# Ardour MCP Test Suite

This directory contains all test scripts for the Ardour MCP server.

## Test Files

### Core Functionality Tests
- `test_working_server.py` - **Main test** - Complete Phase 2 functionality test
- `test_osc_formats.py` - OSC message format debugging and validation
- `test_direct_osc.py` - Direct OSC communication bypassing server

### Phase-Specific Tests  
- `test_new_features.py` - Phase 1 features (track naming, record, pan)
- `test_phase2_features.py` - Phase 2 features (enhanced transport, session management)
- `test_phase3_sends.py` - Phase 3A features (send/aux control)
- `test_plugin_discovery.py` - Plugin discovery and metadata
- `test_plugin_control.py` - Plugin enable/disable control
- `test_smart_parameters.py` - Smart parameter conversion with real-world values
- `test_recording_controls.py` - Master recording controls and workflows

### Diagnostic Tools
- `diagnose_server.py` - Server status and endpoint availability diagnostic
- `restart_server.py` - Server restart helper script

## Usage

### Quick Test Everything
```bash
# Main comprehensive test
python tests/test_working_server.py

# Diagnostic check
python tests/diagnose_server.py
```

### Debug OSC Issues
```bash
# Test direct OSC (bypasses server)
python tests/test_direct_osc.py

# Test OSC formats
python tests/test_osc_formats.py
```

### Development Testing
```bash
# Test specific phase features
python tests/test_new_features.py
python tests/test_phase2_features.py
python tests/test_phase3_sends.py

# Test plugin functionality
python tests/test_plugin_discovery.py
python tests/test_plugin_control.py
python tests/test_smart_parameters.py

# Test recording functionality
python tests/test_recording_controls.py
```

## Test Results Expected

All tests should show:
- ✅ All endpoints return 200 OK (not 404/405)
- ✅ OSC format: `/transport_play` (not `/ardour/transport_play`)  
- ✅ No Unicode encoding errors
- ✅ Ardour responds to commands (transport moves, track changes, dialogs open)
- ✅ Plugin parameters change in real-time
- ✅ Recording indicators update (red record buttons, input meters)
- ✅ Smart parameter conversion works with real-world values

## Prerequisites

1. **Ardour running** with session loaded
2. **OSC enabled** in Edit > Preferences > Control Surfaces > OSC
3. **OSC port 3819** configured
4. **MCP Server running** on localhost:8000

## Troubleshooting

- If 404 errors: Server needs restart to load new endpoints
- If transport doesn't move: Check Ardour OSC settings
- If encoding errors: Unicode symbols in logs need fixing
- If 422 errors: Check request body field names match API schema