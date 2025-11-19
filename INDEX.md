# Pi Ladder Logic - Project Index

## 📁 Project Structure

```
pi_ladder_logic/
│
├── 📄 Documentation
│   ├── README.md              - Complete project documentation
│   ├── GETTING_STARTED.md     - Beginner-friendly tutorial
│   ├── QUICK_REFERENCE.md     - Instruction syntax reference
│   ├── ARCHITECTURE.md        - System design and internals
│   └── INDEX.md              - This file
│
├── 🐍 Core Application
│   ├── main.py               - Main entry point (executable)
│   ├── test_installation.py  - Installation verification
│   └── requirements.txt      - Python dependencies
│
├── ⚙️ Core Modules
│   └── core/
│       ├── __init__.py
│       ├── runtime.py        - PLC runtime engine
│       ├── tags.py           - Tag database
│       └── instructions.py   - Ladder instructions
│
├── 🔌 I/O System
│   └── io/
│       ├── __init__.py
│       └── gpio_manager.py   - GPIO interface & simulation
│
├── ⚙️ Configuration
│   └── config/
│       └── io_config.json    - GPIO pin mappings
│
├── 📝 Examples
│   └── examples/
│       ├── blink.json               - LED blink timer
│       ├── start_stop_motor.json    - Motor control with latching
│       └── traffic_light.json       - State machine sequencer
│
└── 🌐 Web Interface (Future)
    └── web/
        └── (planned for future development)
```

## 📖 Documentation Guide

### For Beginners
1. **Start here**: `GETTING_STARTED.md`
   - 5-minute quick start
   - First program tutorial
   - Hardware setup guide
   - Common patterns

2. **Then read**: `QUICK_REFERENCE.md`
   - Instruction syntax
   - JSON format guide
   - Quick lookup table
   - Common patterns

### For Advanced Users
3. **Complete reference**: `README.md`
   - All features
   - Complete instruction set
   - Command-line options
   - Troubleshooting

4. **System internals**: `ARCHITECTURE.md`
   - Scan cycle details
   - Component design
   - Class relationships
   - Extension points

## 🚀 Quick Commands

```bash
# Test installation
python3 test_installation.py

# Run example programs
python3 main.py examples/blink.json
python3 main.py examples/start_stop_motor.json
python3 main.py examples/traffic_light.json

# Run with custom settings
python3 main.py program.json --scan-time 50
python3 main.py program.json --no-io
python3 main.py program.json --debug

# Make scripts executable (Linux/Mac)
chmod +x main.py test_installation.py
```

## 🎯 Key Features

### Implemented
✅ Standard PLC instructions (XIC, XIO, OTE, OTL, OTU, OSR)
✅ Timers (TON, TOF)
✅ Counters (CTU, CTD)
✅ Scan cycle execution
✅ GPIO interface
✅ Simulation mode
✅ JSON program format
✅ System monitoring

### Planned for Future
⏳ Web-based HMI
⏳ Modbus TCP/RTU
⏳ MQTT integration
⏳ Math instructions
⏳ Comparison instructions
⏳ Analog I/O
⏳ Data logging
⏳ Graphical ladder editor

## 📚 Instruction Reference

| Type | Instructions |
|------|-------------|
| **Contacts** | XIC, XIO |
| **Coils** | OTE, OTL, OTU, OSR |
| **Timers** | TON, TOF |
| **Counters** | CTU, CTD |

See `QUICK_REFERENCE.md` for detailed syntax.

## 🔧 File Purposes

### Core System Files

**main.py**
- Application entry point
- Argument parsing
- Runtime initialization
- Execution loop management

**core/runtime.py**
- PLCRuntime: Main execution engine
- LadderProgram: Program container
- Rung: Individual rung execution
- Scan cycle implementation

**core/instructions.py**
- All ladder instruction implementations
- Base Instruction class
- Contacts: XIC, XIO
- Coils: OTE, OTL, OTU, OSR
- Timers: TON, TOF
- Counters: CTU, CTD

**core/tags.py**
- TagDatabase: Thread-safe tag storage
- System tag management
- Get/Set operations

**io/gpio_manager.py**
- GPIOManager: GPIO abstraction
- IOPoint: Individual I/O configuration
- Simulation mode support
- VirtualIOSimulator: Test interface

**test_installation.py**
- Verifies installation
- Tests all components
- Provides diagnostic info

### Configuration Files

**config/io_config.json**
- GPIO pin mappings
- Input configuration
- Output configuration
- Pin descriptions

**requirements.txt**
- Python dependencies
- Optional packages
- Version specifications

### Example Programs

**examples/blink.json**
- Simple LED blink
- Timer usage
- One-shot pulse
- Toggle logic

**examples/start_stop_motor.json**
- Motor control
- Start/Stop buttons
- Latching logic
- Emergency stop
- Run time counter

**examples/traffic_light.json**
- State machine
- Sequential control
- Multiple timers
- State transitions

## 🎓 Learning Path

### Level 1: Basics
1. Run `test_installation.py`
2. Read `GETTING_STARTED.md`
3. Run `examples/blink.json`
4. Understand contacts and coils
5. Create simple on/off program

### Level 2: Intermediate
1. Study `examples/start_stop_motor.json`
2. Learn latching (OTL/OTU)
3. Understand timers (TON)
4. Create timed sequence
5. Add physical hardware

### Level 3: Advanced
1. Study `examples/traffic_light.json`
2. Learn state machines
3. Use counters (CTU/CTD)
4. Combine multiple features
5. Build complex application

### Level 4: Expert
1. Read `ARCHITECTURE.md`
2. Understand scan cycle
3. Modify core code
4. Add new instructions
5. Contribute enhancements

## 🛠️ Development Workflow

### Creating a New Program
1. Copy an example: `cp examples/blink.json myprogram.json`
2. Edit JSON structure
3. Test in simulation: `python3 main.py myprogram.json --no-io`
4. Debug if needed: `python3 main.py myprogram.json --debug`
5. Add hardware connections
6. Update I/O config
7. Test with hardware: `sudo python3 main.py myprogram.json`

### Adding New Features
1. Study existing code in `core/`
2. Follow class patterns
3. Add to appropriate module
4. Update `instructions.py` for new instructions
5. Test thoroughly
6. Document in README

## 📊 System Tags

```
_SYSTEM.RUNNING      - Runtime status (Boolean)
_SYSTEM.SCAN_TIME    - Current scan time in ms (Float)
_SYSTEM.CYCLE_COUNT  - Total scans executed (Integer)
_SYSTEM.ERROR        - Error flag (Boolean)
```

## 🔍 Troubleshooting Index

| Issue | Solution | Reference |
|-------|----------|-----------|
| Installation problems | Run test_installation.py | GETTING_STARTED.md |
| Scan overruns | Increase scan time | README.md |
| GPIO errors | Check permissions, use sudo | README.md |
| Tag not updating | Check spelling, case | QUICK_REFERENCE.md |
| Program not loading | Validate JSON syntax | README.md |
| Hardware not responding | Check wiring, config | GETTING_STARTED.md |

## 🎯 Use Cases

### Educational
- Learning PLC programming
- Teaching automation concepts
- Prototyping control logic
- Understanding scan cycles

### Hobbyist
- Home automation
- Garden irrigation
- Aquarium control
- Weather station
- Security system

### Professional
- Prototyping PLC programs
- Testing ladder logic
- Small-scale automation
- Control system research
- IoT integration

### Industrial (Non-Critical)
- Monitoring systems
- Data logging
- Operator interfaces
- Test equipment
- R&D projects

⚠️ **Not suitable for**: Life-safety, critical infrastructure, certified applications

## 📞 Support Resources

### Internal Resources
- `README.md` - Complete reference
- `GETTING_STARTED.md` - Tutorials
- `QUICK_REFERENCE.md` - Quick lookup
- `ARCHITECTURE.md` - Technical details
- Example programs - Working code

### External Resources
- Raspberry Pi GPIO pinout: https://pinout.xyz
- PLC basics: Allen-Bradley manuals
- Ladder logic fundamentals: IEC 61131-3

## 🔄 Version History

**v1.0** - Initial Release
- Core ladder logic runtime
- Basic instructions (contacts, coils)
- Timers and counters
- GPIO interface
- Simulation mode
- Example programs
- Complete documentation

**Future Versions**
- v1.1: Web HMI
- v1.2: Modbus support
- v1.3: Math instructions
- v2.0: Graphical editor

## 📝 License

Open source - use and modify for your projects.

## 🤝 Contributing

Contributions welcome for:
- Additional instructions
- Protocol implementations
- HMI development
- Documentation improvements
- Bug fixes
- Example programs

---

**This project bridges industrial automation and embedded systems development.**

Built with ❤️ for makers, engineers, and automation enthusiasts.
