"""
Ladder Logic Runtime Engine
Implements PLC-style scan cycle execution
"""

import json
import time
import logging
from typing import List, Dict, Any
from .tags import TagDatabase
from .instructions import *


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Rung:
    """Represents a single rung of ladder logic"""
    
    def __init__(self, rung_id: int, instructions: List[Instruction]):
        self.rung_id = rung_id
        self.instructions = instructions
    
    def execute(self, tags: TagDatabase) -> bool:
        """
        Execute the rung left-to-right.
        Returns final rung state (continuity).
        """
        rung_state = True  # Start with power on (left rail)
        
        for instruction in self.instructions:
            rung_state = instruction.evaluate(tags, rung_state)
        
        return rung_state


class LadderProgram:
    """Container for the complete ladder logic program"""
    
    def __init__(self):
        self.rungs: List[Rung] = []
        self.tags = TagDatabase()
    
    def add_rung(self, rung: Rung):
        """Add a rung to the program"""
        self.rungs.append(rung)
    
    def execute_scan(self):
        """Execute one complete scan of all rungs"""
        for rung in self.rungs:
            rung.execute(self.tags)
    
    def load_from_json(self, json_file: str):
        """
        Load ladder program from JSON file.
        
        JSON format:
        {
            "program_name": "MyProgram",
            "scan_time_ms": 100,
            "rungs": [
                {
                    "rung_id": 0,
                    "comment": "Start button logic",
                    "instructions": [
                        {"type": "XIC", "tag": "START_BTN"},
                        {"type": "OTE", "tag": "MOTOR_RUN"}
                    ]
                }
            ]
        }
        """
        with open(json_file, 'r') as f:
            program_data = json.load(f)
        
        self.rungs = []
        
        for rung_data in program_data.get('rungs', []):
            instructions = []
            
            for inst_data in rung_data.get('instructions', []):
                inst_type = inst_data.get('type')
                
                # Create instruction based on type
                if inst_type == 'XIC':
                    instructions.append(XIC(inst_data['tag']))
                
                elif inst_type == 'XIO':
                    instructions.append(XIO(inst_data['tag']))
                
                elif inst_type == 'OTE':
                    instructions.append(OTE(inst_data['tag']))
                
                elif inst_type == 'OTL':
                    instructions.append(OTL(inst_data['tag']))
                
                elif inst_type == 'OTU':
                    instructions.append(OTU(inst_data['tag']))
                
                elif inst_type == 'OSR':
                    instructions.append(OSR(inst_data['tag']))
                
                elif inst_type == 'TON':
                    instructions.append(TON(inst_data['tag'], inst_data['preset']))
                
                elif inst_type == 'TOF':
                    instructions.append(TOF(inst_data['tag'], inst_data['preset']))
                
                elif inst_type == 'CTU':
                    reset_tag = inst_data.get('reset_tag')
                    instructions.append(CTU(inst_data['tag'], inst_data['preset'], reset_tag))
                
                elif inst_type == 'CTD':
                    instructions.append(CTD(inst_data['tag'], inst_data['preset']))
                
                else:
                    logger.warning(f"Unknown instruction type: {inst_type}")
            
            rung = Rung(rung_data['rung_id'], instructions)
            self.add_rung(rung)
        
        logger.info(f"Loaded program with {len(self.rungs)} rungs")
        return program_data.get('scan_time_ms', 100)


class PLCRuntime:
    """
    Main PLC Runtime Engine
    Executes ladder logic in continuous scan cycles
    """
    
    def __init__(self, scan_time_ms: int = 100):
        self.program = LadderProgram()
        self.scan_time_ms = scan_time_ms
        self.running = False
        self.io_manager = None
    
    def attach_io(self, io_manager):
        """Attach I/O manager for physical GPIO"""
        self.io_manager = io_manager
    
    def load_program(self, json_file: str):
        """Load ladder program from JSON"""
        self.scan_time_ms = self.program.load_from_json(json_file)
    
    def start(self):
        """Start the PLC scan cycle"""
        self.running = True
        self.program.tags.set('_SYSTEM.RUNNING', True)
        logger.info(f"PLC Runtime started (scan time: {self.scan_time_ms}ms)")
    
    def stop(self):
        """Stop the PLC scan cycle"""
        self.running = False
        self.program.tags.set('_SYSTEM.RUNNING', False)
        logger.info("PLC Runtime stopped")
    
    def run_scan_cycle(self):
        """
        Execute one complete scan cycle:
        1. Read inputs (from GPIO if attached)
        2. Execute ladder logic
        3. Write outputs (to GPIO if attached)
        """
        scan_start = time.time()
        
        # Step 1: Read inputs
        if self.io_manager:
            self.io_manager.read_inputs(self.program.tags)
        
        # Step 2: Execute ladder logic
        self.program.execute_scan()
        
        # Step 3: Write outputs
        if self.io_manager:
            self.io_manager.write_outputs(self.program.tags)
        
        # Update scan time
        scan_time = (time.time() - scan_start) * 1000
        self.program.tags.set('_SYSTEM.SCAN_TIME', round(scan_time, 2))
        
        # Increment cycle count
        cycle_count = self.program.tags.get('_SYSTEM.CYCLE_COUNT', 0)
        self.program.tags.set('_SYSTEM.CYCLE_COUNT', cycle_count + 1)
    
    def run(self):
        """
        Main execution loop - runs continuously until stopped
        """
        logger.info("Entering main execution loop...")
        
        try:
            while self.running:
                cycle_start = time.time()
                
                self.run_scan_cycle()
                
                # Sleep to maintain scan time
                elapsed = (time.time() - cycle_start) * 1000
                sleep_time = max(0, (self.scan_time_ms - elapsed) / 1000)
                
                if elapsed > self.scan_time_ms:
                    logger.warning(f"Scan overrun: {elapsed:.2f}ms > {self.scan_time_ms}ms")
                
                time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
        except Exception as e:
            logger.error(f"Runtime error: {e}", exc_info=True)
            self.program.tags.set('_SYSTEM.ERROR', True)
        
        finally:
            self.stop()
            if self.io_manager:
                self.io_manager.cleanup()
