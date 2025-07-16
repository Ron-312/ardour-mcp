"""
Smart parameter value conversion system for Ardour plugins
Converts between real-world values (dB, Hz, ratios) and OSC 0-1 values
"""

import math
from typing import Union, Dict, Any, Optional
from enum import Enum

class ParameterType(Enum):
    """Parameter value types for conversion"""
    DB_GAIN = "db_gain"              # -60dB to +12dB
    DB_THRESHOLD = "db_threshold"    # -60dB to 0dB  
    FREQUENCY = "frequency"          # 20Hz to 20kHz (log scale)
    RATIO = "ratio"                  # 1:1 to 20:1
    PERCENTAGE = "percentage"        # 0% to 100%
    TIME_MS = "time_ms"             # 0.1ms to 1000ms (log scale)
    TIME_SEC = "time_sec"           # 0.001s to 10s (log scale)
    Q_FACTOR = "q_factor"           # 0.1 to 30 (log scale)
    RAW = "raw"                     # Direct 0-1 value (no conversion)

class ParameterConverter:
    """Handles conversion between real-world and OSC values"""
    
    @staticmethod
    def db_gain_to_osc(db_value: float, min_db: float = -60.0, max_db: float = 12.0) -> float:
        """Convert dB gain to OSC 0-1 value
        
        Args:
            db_value: dB value to convert
            min_db: Minimum dB value (default -60)
            max_db: Maximum dB value (default +12)
            
        Returns:
            OSC value between 0.0 and 1.0
        """
        # Clamp to valid range
        db_value = max(min_db, min(max_db, db_value))
        return (db_value - min_db) / (max_db - min_db)
    
    @staticmethod
    def osc_to_db_gain(osc_value: float, min_db: float = -60.0, max_db: float = 12.0) -> float:
        """Convert OSC 0-1 value to dB gain
        
        Args:
            osc_value: OSC value between 0.0 and 1.0
            min_db: Minimum dB value (default -60)
            max_db: Maximum dB value (default +12)
            
        Returns:
            dB value
        """
        # Clamp OSC value
        osc_value = max(0.0, min(1.0, osc_value))
        return min_db + (osc_value * (max_db - min_db))
    
    @staticmethod
    def db_threshold_to_osc(db_value: float, min_db: float = -60.0, max_db: float = 0.0) -> float:
        """Convert dB threshold to OSC 0-1 value (typically -60 to 0 dB)"""
        return ParameterConverter.db_gain_to_osc(db_value, min_db, max_db)
    
    @staticmethod
    def osc_to_db_threshold(osc_value: float, min_db: float = -60.0, max_db: float = 0.0) -> float:
        """Convert OSC 0-1 value to dB threshold"""
        return ParameterConverter.osc_to_db_gain(osc_value, min_db, max_db)
    
    @staticmethod
    def frequency_to_osc(hz_value: float, min_hz: float = 20.0, max_hz: float = 20000.0) -> float:
        """Convert frequency to OSC 0-1 value (logarithmic scale)
        
        Args:
            hz_value: Frequency in Hz
            min_hz: Minimum frequency (default 20Hz)
            max_hz: Maximum frequency (default 20kHz)
            
        Returns:
            OSC value between 0.0 and 1.0
        """
        # Clamp to valid range
        hz_value = max(min_hz, min(max_hz, hz_value))
        
        # Logarithmic conversion
        log_min = math.log10(min_hz)
        log_max = math.log10(max_hz)
        log_value = math.log10(hz_value)
        
        return (log_value - log_min) / (log_max - log_min)
    
    @staticmethod
    def osc_to_frequency(osc_value: float, min_hz: float = 20.0, max_hz: float = 20000.0) -> float:
        """Convert OSC 0-1 value to frequency (logarithmic scale)"""
        # Clamp OSC value
        osc_value = max(0.0, min(1.0, osc_value))
        
        # Logarithmic conversion
        log_min = math.log10(min_hz)
        log_max = math.log10(max_hz)
        log_value = log_min + (osc_value * (log_max - log_min))
        
        return 10 ** log_value
    
    @staticmethod
    def ratio_to_osc(ratio_value: float, min_ratio: float = 1.0, max_ratio: float = 20.0) -> float:
        """Convert compression ratio to OSC 0-1 value
        
        Args:
            ratio_value: Compression ratio (e.g., 4.0 for 4:1)
            min_ratio: Minimum ratio (default 1.0)
            max_ratio: Maximum ratio (default 20.0)
            
        Returns:
            OSC value between 0.0 and 1.0
        """
        # Clamp to valid range
        ratio_value = max(min_ratio, min(max_ratio, ratio_value))
        return (ratio_value - min_ratio) / (max_ratio - min_ratio)
    
    @staticmethod
    def osc_to_ratio(osc_value: float, min_ratio: float = 1.0, max_ratio: float = 20.0) -> float:
        """Convert OSC 0-1 value to compression ratio"""
        # Clamp OSC value
        osc_value = max(0.0, min(1.0, osc_value))
        return min_ratio + (osc_value * (max_ratio - min_ratio))
    
    @staticmethod
    def percentage_to_osc(percent_value: float) -> float:
        """Convert percentage to OSC 0-1 value"""
        return max(0.0, min(1.0, percent_value / 100.0))
    
    @staticmethod
    def osc_to_percentage(osc_value: float) -> float:
        """Convert OSC 0-1 value to percentage"""
        return max(0.0, min(100.0, osc_value * 100.0))
    
    @staticmethod
    def time_ms_to_osc(ms_value: float, min_ms: float = 0.1, max_ms: float = 1000.0) -> float:
        """Convert time in milliseconds to OSC 0-1 value (logarithmic scale)"""
        # Clamp to valid range
        ms_value = max(min_ms, min(max_ms, ms_value))
        
        # Logarithmic conversion
        log_min = math.log10(min_ms)
        log_max = math.log10(max_ms)
        log_value = math.log10(ms_value)
        
        return (log_value - log_min) / (log_max - log_min)
    
    @staticmethod
    def osc_to_time_ms(osc_value: float, min_ms: float = 0.1, max_ms: float = 1000.0) -> float:
        """Convert OSC 0-1 value to time in milliseconds (logarithmic scale)"""
        # Clamp OSC value
        osc_value = max(0.0, min(1.0, osc_value))
        
        # Logarithmic conversion
        log_min = math.log10(min_ms)
        log_max = math.log10(max_ms)
        log_value = log_min + (osc_value * (log_max - log_min))
        
        return 10 ** log_value
    
    @staticmethod
    def time_sec_to_osc(sec_value: float, min_sec: float = 0.001, max_sec: float = 10.0) -> float:
        """Convert time in seconds to OSC 0-1 value (logarithmic scale)"""
        return ParameterConverter.time_ms_to_osc(sec_value * 1000, min_sec * 1000, max_sec * 1000)
    
    @staticmethod
    def osc_to_time_sec(osc_value: float, min_sec: float = 0.001, max_sec: float = 10.0) -> float:
        """Convert OSC 0-1 value to time in seconds (logarithmic scale)"""
        return ParameterConverter.osc_to_time_ms(osc_value, min_sec * 1000, max_sec * 1000) / 1000
    
    @staticmethod
    def q_factor_to_osc(q_value: float, min_q: float = 0.1, max_q: float = 30.0) -> float:
        """Convert Q factor to OSC 0-1 value (logarithmic scale)"""
        # Clamp to valid range
        q_value = max(min_q, min(max_q, q_value))
        
        # Logarithmic conversion
        log_min = math.log10(min_q)
        log_max = math.log10(max_q)
        log_value = math.log10(q_value)
        
        return (log_value - log_min) / (log_max - log_min)
    
    @staticmethod
    def osc_to_q_factor(osc_value: float, min_q: float = 0.1, max_q: float = 30.0) -> float:
        """Convert OSC 0-1 value to Q factor (logarithmic scale)"""
        # Clamp OSC value
        osc_value = max(0.0, min(1.0, osc_value))
        
        # Logarithmic conversion
        log_min = math.log10(min_q)
        log_max = math.log10(max_q)
        log_value = log_min + (osc_value * (log_max - log_min))
        
        return 10 ** log_value

class SmartParameterValue:
    """Smart parameter value that can handle multiple input formats"""
    
    def __init__(self, 
                 param_type: ParameterType,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None):
        self.param_type = param_type
        self.min_value = min_value
        self.max_value = max_value
    
    def to_osc(self, value_dict: Dict[str, Any]) -> float:
        """Convert real-world parameter value to OSC 0-1 value
        
        Args:
            value_dict: Dictionary with real-world parameter value
                       e.g., {"db": -12.0}, {"hz": 1000}, {"ratio": 4.0}
        
        Returns:
            OSC value between 0.0 and 1.0
        """
        if self.param_type == ParameterType.DB_GAIN:
            if "db" in value_dict:
                return ParameterConverter.db_gain_to_osc(
                    value_dict["db"], 
                    self.min_value or -60.0, 
                    self.max_value or 12.0
                )
        
        elif self.param_type == ParameterType.DB_THRESHOLD:
            if "db" in value_dict:
                return ParameterConverter.db_threshold_to_osc(
                    value_dict["db"],
                    self.min_value or -60.0,
                    self.max_value or 0.0
                )
        
        elif self.param_type == ParameterType.FREQUENCY:
            if "hz" in value_dict:
                return ParameterConverter.frequency_to_osc(
                    value_dict["hz"],
                    self.min_value or 20.0,
                    self.max_value or 20000.0
                )
        
        elif self.param_type == ParameterType.RATIO:
            if "ratio" in value_dict:
                return ParameterConverter.ratio_to_osc(
                    value_dict["ratio"],
                    self.min_value or 1.0,
                    self.max_value or 20.0
                )
        
        elif self.param_type == ParameterType.PERCENTAGE:
            if "percent" in value_dict:
                return ParameterConverter.percentage_to_osc(value_dict["percent"])
        
        elif self.param_type == ParameterType.TIME_MS:
            if "ms" in value_dict:
                return ParameterConverter.time_ms_to_osc(
                    value_dict["ms"],
                    self.min_value or 0.1,
                    self.max_value or 1000.0
                )
        
        elif self.param_type == ParameterType.TIME_SEC:
            if "sec" in value_dict:
                return ParameterConverter.time_sec_to_osc(
                    value_dict["sec"],
                    self.min_value or 0.001,
                    self.max_value or 10.0
                )
        
        elif self.param_type == ParameterType.Q_FACTOR:
            if "q" in value_dict:
                return ParameterConverter.q_factor_to_osc(
                    value_dict["q"],
                    self.min_value or 0.1,
                    self.max_value or 30.0
                )
        
        elif self.param_type == ParameterType.RAW:
            if "value" in value_dict:
                return max(0.0, min(1.0, value_dict["value"]))
        
        # Fallback: check for raw value
        if "value" in value_dict:
            return max(0.0, min(1.0, value_dict["value"]))
        
        raise ValueError(f"Invalid value format for parameter type {self.param_type.value}: {value_dict}")
    
    def from_osc(self, osc_value: float) -> Dict[str, float]:
        """Convert OSC 0-1 value to real-world parameter value
        
        Args:
            osc_value: OSC value between 0.0 and 1.0
        
        Returns:
            Dictionary with real-world parameter value
        """
        if self.param_type == ParameterType.DB_GAIN:
            return {"db": ParameterConverter.osc_to_db_gain(
                osc_value, 
                self.min_value or -60.0, 
                self.max_value or 12.0
            )}
        
        elif self.param_type == ParameterType.DB_THRESHOLD:
            return {"db": ParameterConverter.osc_to_db_threshold(
                osc_value,
                self.min_value or -60.0,
                self.max_value or 0.0
            )}
        
        elif self.param_type == ParameterType.FREQUENCY:
            return {"hz": ParameterConverter.osc_to_frequency(
                osc_value,
                self.min_value or 20.0,
                self.max_value or 20000.0
            )}
        
        elif self.param_type == ParameterType.RATIO:
            return {"ratio": ParameterConverter.osc_to_ratio(
                osc_value,
                self.min_value or 1.0,
                self.max_value or 20.0
            )}
        
        elif self.param_type == ParameterType.PERCENTAGE:
            return {"percent": ParameterConverter.osc_to_percentage(osc_value)}
        
        elif self.param_type == ParameterType.TIME_MS:
            return {"ms": ParameterConverter.osc_to_time_ms(
                osc_value,
                self.min_value or 0.1,
                self.max_value or 1000.0
            )}
        
        elif self.param_type == ParameterType.TIME_SEC:
            return {"sec": ParameterConverter.osc_to_time_sec(
                osc_value,
                self.min_value or 0.001,
                self.max_value or 10.0
            )}
        
        elif self.param_type == ParameterType.Q_FACTOR:
            return {"q": ParameterConverter.osc_to_q_factor(
                osc_value,
                self.min_value or 0.1,
                self.max_value or 30.0
            )}
        
        elif self.param_type == ParameterType.RAW:
            return {"value": osc_value}
        
        return {"value": osc_value}