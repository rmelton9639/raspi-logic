# Pi Ladder Logic

A PLC-style ladder logic runtime system for Raspberry Pi, bringing industrial automation programming practices to embedded systems development.

## Overview

Pi Ladder Logic implements a traditional PLC scan cycle execution model, allowing you to write control logic using familiar ladder logic concepts adapted for Raspberry Pi GPIO and modern embedded applications.

### Features

- **Standard PLC Instructions**: XIC, XIO, OTE, OTL, OTU, OSR
- **Function Blocks**: TON, TOF, CTU, CTD timers and counters  
- **Scan Cycle Execution**: Classic PLC scan cycle (read inputs → execute logic → write outputs)
- **GPIO Integration**: Map Raspberry Pi GPIO pins to ladder logic tags
- **JSON Program Format**: Human-readable program files
- **Simulation Mode**: Test programs without physical hardware
- **Real-time Monitoring**: System scan time and cycle count tracking

## Installation

```bash
git clone https://github.com/rmelton9639/raspi-logic.git
cd raspi-logic
pip3 install -r requirements.txt
```

## Quick Start

```bash
# Run a simple blink program
python3 main.py examples/blink.json

# Run motor control example
python3 main.py examples/start_stop_motor.json

# Run traffic light sequencer
python3 main.py examples/traffic_light.json
```

## Documentation

For complete documentation, see the docs folder in this repository.

## License

Open source - use and modify as needed for your projects.

## Author

Created by Russell Melton - Bridging industrial automation with embedded systems development.

---

**Happy Coding! 🏭⚡**