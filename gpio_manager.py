"""
GPIO Manager for Raspberry Pi
Handles physical I/O similar to PLC I/O modules
"""

import logging
import json
from typing import Dict, List

logger = logging.getLogger(__name__)

# Try to import RPi.GPIO, fall back to simulation mode if not available
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available - running in simulation mode")


class IOPoint:
    """Represents a single I/O point (input or output)"""
    
    def __init__(self, tag_name: str, pin: int, io_type: str, invert: bool = False):
        self.tag_name = tag_name
        self.pin = pin
        self.io_type = io_type.upper()  # 'INPUT' or 'OUTPUT'
        self.invert = invert
    
    def __repr__(self):
        return f"IOPoint({self.tag_name}, Pin {self.pin}, {self.io_type})"


class GPIOManager:
    """
    Manages GPIO for ladder logic I/O
    Maps physical GPIO pins to ladder logic tags
    """
    
    def __init__(self, config_file: str = None):
        self.inputs: List[IOPoint] = []
        self.outputs: List[IOPoint] = []
        self.simulation_mode = not GPIO_AVAILABLE
        self.simulation_inputs: Dict[str, bool] = {}
        
        if config_file:
            self.load_config(config_file)
        
        if not self.simulation_mode:
            GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
            GPIO.setwarnings(False)
    
    def load_config(self, config_file: str):
        """
        Load I/O configuration from JSON file.
        
        Format:
        {
            "inputs": [
                {"tag": "START_BTN", "pin": 17, "invert": false},
                {"tag": "STOP_BTN", "pin": 27, "invert": false}
            ],
            "outputs": [
                {"tag": "MOTOR_RUN", "pin": 22, "invert": false},
                {"tag": "STATUS_LED", "pin": 23, "invert": false}
            ]
        }
        """
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Configure inputs
        for inp in config.get('inputs', []):
            io_point = IOPoint(
                tag_name=inp['tag'],
                pin=inp['pin'],
                io_type='INPUT',
                invert=inp.get('invert', False)
            )
            self.inputs.append(io_point)
            
            if not self.simulation_mode:
                GPIO.setup(io_point.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            else:
                self.simulation_inputs[io_point.tag_name] = False
        
        # Configure outputs
        for out in config.get('outputs', []):
            io_point = IOPoint(
                tag_name=out['tag'],
                pin=out['pin'],
                io_type='OUTPUT',
                invert=out.get('invert', False)
            )
            self.outputs.append(io_point)
            
            if not self.simulation_mode:
                GPIO.setup(io_point.pin, GPIO.OUT)
                GPIO.output(io_point.pin, GPIO.LOW)
        
        logger.info(f"Loaded I/O config: {len(self.inputs)} inputs, {len(self.outputs)} outputs")
        if self.simulation_mode:
            logger.info("Running in SIMULATION mode (no physical I/O)")
    
    def read_inputs(self, tags):
        """
        Read all inputs from GPIO and update tags.
        Called at the start of each scan cycle.
        """
        for io_point in self.inputs:
            if not self.simulation_mode:
                value = GPIO.input(io_point.pin)
                if io_point.invert:
                    value = not value
            else:
                # Simulation mode - read from simulation dict
                value = self.simulation_inputs.get(io_point.tag_name, False)
            
            tags.set(io_point.tag_name, bool(value))
    
    def write_outputs(self, tags):
        """
        Write all outputs from tags to GPIO.
        Called at the end of each scan cycle.
        """
        for io_point in self.outputs:
            value = tags.get(io_point.tag_name, False)
            
            if io_point.invert:
                value = not value
            
            if not self.simulation_mode:
                GPIO.output(io_point.pin, GPIO.HIGH if value else GPIO.LOW)
    
    def set_simulation_input(self, tag_name: str, value: bool):
        """
        Set a simulated input value (for testing without hardware)
        """
        if self.simulation_mode:
            self.simulation_inputs[tag_name] = value
            logger.info(f"Simulation: {tag_name} = {value}")
    
    def get_io_status(self) -> Dict:
        """Get current I/O status for monitoring"""
        status = {
            'mode': 'simulation' if self.simulation_mode else 'hardware',
            'inputs': [],
            'outputs': []
        }
        
        for io_point in self.inputs:
            status['inputs'].append({
                'tag': io_point.tag_name,
                'pin': io_point.pin
            })
        
        for io_point in self.outputs:
            status['outputs'].append({
                'tag': io_point.tag_name,
                'pin': io_point.pin
            })
        
        return status
    
    def cleanup(self):
        """Cleanup GPIO on shutdown"""
        if not self.simulation_mode:
            # Turn off all outputs
            for io_point in self.outputs:
                GPIO.output(io_point.pin, GPIO.LOW)
            
            GPIO.cleanup()
            logger.info("GPIO cleaned up")


class VirtualIOSimulator:
    """
    Simple virtual I/O simulator for testing without hardware.
    Provides a CLI interface to toggle inputs.
    """
    
    def __init__(self, gpio_manager: GPIOManager):
        self.gpio_manager = gpio_manager
    
    def toggle_input(self, tag_name: str):
        """Toggle an input on/off"""
        if tag_name in self.gpio_manager.simulation_inputs:
            current = self.gpio_manager.simulation_inputs[tag_name]
            self.gpio_manager.set_simulation_input(tag_name, not current)
            return not current
        return None
    
    def set_input(self, tag_name: str, value: bool):
        """Set an input to a specific value"""
        self.gpio_manager.set_simulation_input(tag_name, value)
    
    def get_inputs(self) -> Dict[str, bool]:
        """Get all simulation input states"""
        return self.gpio_manager.simulation_inputs.copy()
