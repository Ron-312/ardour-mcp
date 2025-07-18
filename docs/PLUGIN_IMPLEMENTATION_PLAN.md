# Plugin Control Implementation Plan

## 🎯 **Phase 3B: Smart Plugin Control - Complete Roadmap**

### **Overview**
Implement comprehensive plugin control with real-world parameter values, automatic discovery, and smart parameter conversion.

---

## 📋 **Implementation Tasks** 

### **🔍 Phase 3B-1: Plugin Discovery & Metadata** (High Priority)

#### **Task 1: Plugin Discovery Endpoints**
- **Goal**: List all plugins on any track
- **API**: `GET /track/{n}/plugins`
- **Returns**: Plugin list with IDs, names, active status
- **OSC**: Use `/select/strip N` + plugin feedback
- **Test**: Verify plugin lists match Ardour mixer

#### **Task 2: Plugin Parameter Metadata System**  
- **Goal**: Get detailed parameter information
- **API**: `GET /track/{n}/plugin/{id}/parameters`
- **Returns**: Parameter names, current values, min/max, units
- **OSC**: Parse parameter feedback messages
- **Test**: Compare with plugin GUI parameter lists

#### **Task 3: Plugin Parameter Feedback Listening**
- **Goal**: Receive real-time parameter updates from Ardour
- **Implementation**: OSC server to listen for parameter changes
- **Messages**: `/select/plugin/parameter/N/name`, `/select/plugin/parameter/N/value`
- **Test**: Change parameters in Ardour GUI, verify API reflects changes

---

### **🎛️ Phase 3B-2: Basic Plugin Control** (High Priority)

#### **Task 4: Plugin Enable/Disable Control**
- **Goal**: Bypass/activate plugins
- **API**: `POST /track/{n}/plugin/{id}/activate`
- **Body**: `{"active": true/false}`
- **OSC**: `/select/plugin/activate 1/0`
- **Test**: Verify plugin bypass indicators in Ardour

#### **Task 5: Raw Parameter Control** 
- **Goal**: Direct parameter control with 0-1 values
- **API**: `POST /track/{n}/plugin/{id}/parameter/{param_id}`
- **Body**: `{"value": 0.75}` (raw 0-1 range)
- **OSC**: `/select/plugin/parameter N value`
- **Test**: Set parameters, verify in plugin GUI

---

### **🧠 Phase 3B-3: Smart Parameter Conversion** (High Priority)

#### **Task 6: Parameter Value Conversion System**
- **Goal**: Convert between real-world values and 0-1 OSC values
- **Types**: 
  - dB values (-60 to +12)
  - Frequency (20Hz to 20kHz)  
  - Ratios (1:1 to 20:1)
  - Percentages (0% to 100%)
  - Time (ms, seconds)
- **Implementation**: Conversion functions for each parameter type
- **Test**: Round-trip conversion accuracy

#### **Task 7: Common Plugin Type Handlers**
- **Goal**: Smart handling for common plugin types
- **Plugins**:
  - **ACE Compressor**: threshold_db, ratio, attack_ms, release_ms
  - **ACE EQ**: band_freq_hz, band_gain_db, band_q
  - **ACE Limiter**: threshold_db, release_ms
- **API**: Real-world parameter names
- **Test**: Compressor with dB values, EQ with Hz values

---

### **🚀 Phase 3B-4: Advanced Plugin Features** (Medium Priority)

#### **Task 8: Plugin Preset Management**
- **Goal**: Save/load plugin configurations
- **API**: 
  - `GET /track/{n}/plugin/{id}/presets`
  - `POST /track/{n}/plugin/{id}/preset/{name}/save`
  - `POST /track/{n}/plugin/{id}/preset/{name}/load`
- **Storage**: JSON preset files
- **Test**: Save preset, load on different track

#### **Task 9: Plugin Loading/Removal** (Low Priority)
- **Goal**: Add/remove plugins from tracks
- **API**: 
  - `POST /track/{n}/plugins/add`
  - `DELETE /track/{n}/plugin/{id}`
- **OSC**: Menu actions for plugin insertion
- **Test**: Dynamic plugin chain modification

---

## 🧪 **Testing Strategy**

### **Test Files to Create**

#### **`tests/test_plugin_discovery.py`**
```python
def test_list_track_plugins()
def test_get_plugin_parameters()  
def test_plugin_metadata_accuracy()
def test_parameter_feedback_updates()
```

#### **`tests/test_plugin_control.py`**
```python
def test_plugin_enable_disable()
def test_raw_parameter_control()
def test_parameter_boundary_values()
def test_multiple_plugin_control()
```

#### **`tests/test_smart_parameters.py`**
```python
def test_db_conversion()
def test_frequency_conversion()
def test_ratio_conversion()
def test_time_conversion()
def test_round_trip_accuracy()
```

#### **`tests/test_common_plugins.py`**
```python
def test_ace_compressor_control()
def test_ace_eq_control()  
def test_ace_limiter_control()
def test_real_world_mixing_scenario()
```

#### **`tests/test_plugin_presets.py`**
```python
def test_save_preset()
def test_load_preset()
def test_preset_list()
def test_preset_cross_track()
```

---

## 📊 **API Examples**

### **Plugin Discovery**
```bash
# List plugins on track 1
curl GET /track/1/plugins
# Response: 
{
  "plugins": [
    {"id": 0, "name": "ACE Compressor", "active": true, "type": "compressor"},
    {"id": 1, "name": "ACE EQ", "active": true, "type": "eq"}
  ]
}

# Get compressor parameters
curl GET /track/1/plugin/0/parameters  
# Response:
{
  "parameters": [
    {"id": 1, "name": "threshold", "value_raw": 0.8, "value_db": -12.0, "min_db": -60, "max_db": 0},
    {"id": 2, "name": "ratio", "value_raw": 0.3, "value_ratio": 4.0, "min_ratio": 1, "max_ratio": 20}
  ]
}
```

### **Smart Parameter Control**
```bash
# Set compressor threshold in dB (smart conversion)
curl POST /track/1/plugin/0/parameter/threshold -d '{"db": -18.0}'

# Set EQ frequency in Hz (smart conversion)  
curl POST /track/1/plugin/1/parameter/band1_freq -d '{"hz": 1000}'

# Set ratio as real ratio (smart conversion)
curl POST /track/1/plugin/0/parameter/ratio -d '{"ratio": 6.0}'
```

### **Preset Management**
```bash
# Save current compressor settings as preset
curl POST /track/1/plugin/0/preset/vocal_comp/save

# Load preset on different track
curl POST /track/2/plugin/0/preset/vocal_comp/load
```

---

## 🎛️ **Parameter Conversion Examples**

### **dB Conversion**
```python
# -60dB to 0dB -> 0.0 to 1.0
def db_to_osc(db_value: float) -> float:
    return (db_value + 60) / 60

def osc_to_db(osc_value: float) -> float:
    return (osc_value * 60) - 60
```

### **Frequency Conversion** 
```python
# 20Hz to 20kHz -> 0.0 to 1.0 (logarithmic)
def hz_to_osc(hz_value: float) -> float:
    return math.log10(hz_value / 20) / math.log10(1000)

def osc_to_hz(osc_value: float) -> float:
    return 20 * (1000 ** osc_value)
```

### **Ratio Conversion**
```python
# 1:1 to 20:1 -> 0.0 to 1.0
def ratio_to_osc(ratio: float) -> float:
    return (ratio - 1) / 19

def osc_to_ratio(osc_value: float) -> float:
    return 1 + (osc_value * 19)
```

---

## 🎯 **Implementation Priority**

### **Week 1: Foundation**
1. ✅ Plugin Discovery Endpoints
2. ✅ Plugin Parameter Metadata  
3. ✅ Basic Plugin Enable/Disable

### **Week 2: Smart Control**
4. ✅ Raw Parameter Control
5. ✅ Parameter Conversion System
6. ✅ Common Plugin Handlers

### **Week 3: Polish** 
7. ✅ Comprehensive Testing
8. ✅ Plugin Presets (if time allows)
9. ✅ Documentation & Examples

---

## 🔍 **Success Criteria**

### **Must Have**
- ✅ List all plugins on any track
- ✅ Get complete parameter metadata
- ✅ Enable/disable any plugin
- ✅ Control parameters with real-world values (dB, Hz, ratios)
- ✅ Full test coverage

### **Nice to Have**  
- ✅ Plugin presets save/load
- ✅ Real-time parameter feedback
- ✅ Plugin loading/removal
- ✅ Multi-track plugin operations

### **Stretch Goals**
- ✅ Plugin chain reordering
- ✅ A/B preset comparisons
- ✅ Plugin automation integration
- ✅ Custom plugin type definitions

---

**Ready to implement?** Let's start with **Plugin Discovery Endpoints** - this will give us the foundation to build everything else on!