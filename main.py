#!/usr/bin/env python3
"""
Pi Ladder Logic - Main Entry Point
Raspberry Pi Ladder Logic Runtime System
"""

import sys
import argparse
import logging
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent))

from core.runtime import PLCRuntime
from io.gpio_manager import GPIOManager, VirtualIOSimulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Pi Ladder Logic - PLC-style ladder logic for Raspberry Pi'
    )
    
    parser.add_argument(
        'program',
        help='Path to ladder logic program JSON file'
    )
    
    parser.add_argument(
        '--io-config',
        default='config/io_config.json',
        help='Path to I/O configuration file (default: config/io_config.json)'
    )
    
    parser.add_argument(
        '--scan-time',
        type=int,
        default=100,
        help='Scan cycle time in milliseconds (default: 100ms)'
    )
    
    parser.add_argument(
        '--no-io',
        action='store_true',
        help='Run without I/O (simulation mode)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Print banner
    print("=" * 60)
    print("  Pi Ladder Logic - PLC Runtime for Raspberry Pi")
    print("=" * 60)
    print()
    
    # Create runtime
    runtime = PLCRuntime(scan_time_ms=args.scan_time)
    
    # Load program
    try:
        logger.info(f"Loading program: {args.program}")
        runtime.load_program(args.program)
    except FileNotFoundError:
        logger.error(f"Program file not found: {args.program}")
        return 1
    except Exception as e:
        logger.error(f"Error loading program: {e}")
        return 1
    
    # Setup I/O if not disabled
    if not args.no_io:
        try:
            logger.info(f"Loading I/O config: {args.io_config}")
            io_manager = GPIOManager(args.io_config)
            runtime.attach_io(io_manager)
            
            io_status = io_manager.get_io_status()
            logger.info(f"I/O Mode: {io_status['mode']}")
            logger.info(f"Inputs configured: {len(io_status['inputs'])}")
            logger.info(f"Outputs configured: {len(io_status['outputs'])}")
            
            # If in simulation mode, create virtual I/O simulator
            if io_manager.simulation_mode:
                simulator = VirtualIOSimulator(io_manager)
                print()
                print("SIMULATION MODE - No physical I/O")
                print("Available simulation commands:")
                print("  - Use separate terminal to control inputs")
                print("  - Or modify simulation_inputs dict directly")
                print()
        
        except FileNotFoundError:
            logger.error(f"I/O config file not found: {args.io_config}")
            return 1
        except Exception as e:
            logger.error(f"Error setting up I/O: {e}")
            return 1
    else:
        logger.info("Running in NO-I/O mode")
    
    # Start runtime
    print()
    print(f"Starting PLC runtime (scan time: {runtime.scan_time_ms}ms)")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        runtime.start()
        runtime.run()
    except KeyboardInterrupt:
        print()
        logger.info("Shutdown requested by user")
    finally:
        runtime.stop()
        print()
        print("PLC runtime stopped")
        
        # Print final statistics
        tags = runtime.program.tags.get_all()
        cycle_count = tags.get('_SYSTEM.CYCLE_COUNT', 0)
        avg_scan_time = tags.get('_SYSTEM.SCAN_TIME', 0)
        
        print()
        print("Runtime Statistics:")
        print(f"  Total scan cycles: {cycle_count}")
        print(f"  Average scan time: {avg_scan_time:.2f}ms")
        print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
