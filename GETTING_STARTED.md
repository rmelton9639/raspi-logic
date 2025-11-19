# Getting Started with Pi Ladder Logic

## Welcome!

Pi Ladder Logic brings industrial PLC programming to the Raspberry Pi. If you're familiar with ladder logic from PLCs like Allen-Bradley, Siemens, or Mitsubishi, you'll feel right at home.

## 5-Minute Quick Start

### 1. Test Your Installation

```bash
python3 test_installation.py
```

This verifies all components are working correctly.

### 2. Run Your First Program

```bash
python3 main.py examples/blink.json
```

You'll see:
```
==============================================================
  Pi Ladder Logic - PLC Runtime for Raspberry Pi
==============================================================

Loading program: examples/blink.json
I/O Mode: simulation
Starting PLC runtime (scan time: 50ms)
Press Ctrl+C to stop
==============================================================

PLC Runtime started (scan time: 50ms)
Entering main execution loop...
```

Press `Ctrl+C` to stop.

### 3. Understanding What Just Happened

The blink program:
1. Creates a 1-second timer
2. Toggles an LED when the timer completes
3. Resets and repeats

Even in simulation mode (no physical hardware), the program executes the ladder logic and updates internal tags.

## Understanding Ladder Logic

### Traditional PLC Ladder Diagram

```
     START_BTN    STOP_BTN     MOTOR_RUN
    ──| |───────────|/|──────────( )──
      NO            NC          COIL
```

This rung:
- Checks if START_BTN is pressed (Normally Open contact)
- Checks if STOP_BTN is NOT pressed (Normally Closed contact)
- If both are true, energizes MOTOR_RUN coil

### Same Logic in JSON

```json
{
  "rung_id": 0,
  "instructions": [
    {"type": "XIC", "tag": "START_BTN"},
    {"type": "XIO", "tag": "STOP_BTN"},
    {"type": "OTE", "tag": "MOTOR_RUN"}
  ]
}
```

- **XIC** = Examine If Closed (NO contact)
- **XIO** = Examine If Open (NC contact)
- **OTE** = Output Energize (Coil)

## Your First Custom Program

Let's create a simple push-on, push-off button circuit.

### 1. Create the Program File

Create `my_first_program.json`:

```json
{
  "program_name": "Push On Push Off",
  "scan_time_ms": 50,
  "rungs": [
    {
      "rung_id": 0,
      "comment": "Detect rising edge of button press",
      "instructions": [
        {"type": "XIC", "tag": "BUTTON"},
        {"type": "OSR", "tag": "BUTTON_PULSE"}
      ]
    },
    {
      "rung_id": 1,
      "comment": "Toggle output on each button press",
      "instructions": [
        {"type": "XIC", "tag": "BUTTON_PULSE"},
        {"type": "XIO", "tag": "LED"},
        {"type": "OTL", "tag": "LED"}
      ]
    },
    {
      "rung_id": 2,
      "comment": "Turn off if already on",
      "instructions": [
        {"type": "XIC", "tag": "BUTTON_PULSE"},
        {"type": "XIC", "tag": "LED"},
        {"type": "OTU", "tag": "LED"}
      ]
    }
  ]
}
```

### 2. Run It

```bash
python3 main.py my_first_program.json --no-io
```

### 3. What This Does

- **Rung 0**: One-shot rising edge detector - triggers once per button press
- **Rung 1**: If LED is OFF, turn it ON
- **Rung 2**: If LED is ON, turn it OFF

Result: Each button press toggles the LED.

## Adding Physical Hardware

### Simple LED Circuit

```
GPIO Pin 18 ──[330Ω]──[LED]── GND
```

### Update I/O Configuration

Edit `config/io_config.json`:

```json
{
  "inputs": [
    {
      "tag": "BUTTON",
      "pin": 17,
      "invert": false,
      "description": "Push button on GPIO17"
    }
  ],
  "outputs": [
    {
      "tag": "LED",
      "pin": 18,
      "invert": false,
      "description": "LED on GPIO18"
    }
  ]
}
```

### Wire Your Hardware

**Button Input:**
```
GPIO17 ──[Button]── 3.3V
   |
  GND (internal pull-down)
```

**LED Output:**
```
GPIO18 ──[330Ω]──[LED]── GND
```

### Run on Hardware

```bash
sudo python3 main.py my_first_program.json
```

Note: `sudo` is needed for GPIO access on Raspberry Pi.

## Common Patterns

### Pattern 1: Timed Sequence

```json
{
  "rungs": [
    {
      "rung_id": 0,
      "comment": "Output 1 on for 2 seconds",
      "instructions": [
        {"type": "XIC", "tag": "START"},
        {"type": "TON", "tag": "TIMER_1", "preset": 2000}
      ]
    },
    {
      "rung_id": 1,
      "instructions": [
        {"type": "XIC", "tag": "TIMER_1.TT"},
        {"type": "OTE", "tag": "OUTPUT_1"}
      ]
    },
    {
      "rung_id": 2,
      "comment": "Output 2 starts after output 1 done",
      "instructions": [
        {"type": "XIC", "tag": "TIMER_1.DN"},
        {"type": "TON", "tag": "TIMER_2", "preset": 3000}
      ]
    },
    {
      "rung_id": 3,
      "instructions": [
        {"type": "XIC", "tag": "TIMER_2.TT"},
        {"type": "OTE", "tag": "OUTPUT_2"}
      ]
    }
  ]
}
```

### Pattern 2: Counting Events

```json
{
  "rungs": [
    {
      "rung_id": 0,
      "comment": "Count button presses",
      "instructions": [
        {"type": "XIC", "tag": "BUTTON"},
        {"type": "CTU", "tag": "PRESS_COUNT", "preset": 10, "reset_tag": "RESET"}
      ]
    },
    {
      "rung_id": 1,
      "comment": "Turn on LED after 10 presses",
      "instructions": [
        {"type": "XIC", "tag": "PRESS_COUNT.DN"},
        {"type": "OTE", "tag": "LED"}
      ]
    }
  ]
}
```

## Debugging Tips

### 1. Check System Tags

System tags tell you what's happening:

```python
# In your program, you can check:
_SYSTEM.RUNNING      # Is runtime active?
_SYSTEM.SCAN_TIME    # How long is each scan? (ms)
_SYSTEM.CYCLE_COUNT  # How many scans completed?
```

### 2. Enable Debug Logging

```bash
python3 main.py myprogram.json --debug
```

This shows detailed execution information.

### 3. Start Simple

- Begin with 1-2 rungs
- Test each piece before adding more
- Use simulation mode first

### 4. Common Issues

**"Scan overrun" warnings:**
- Your logic takes longer than scan time
- Solution: Increase `--scan-time` or simplify logic

**Tags not updating:**
- Check tag names for typos
- Remember: tags are case-sensitive
- Use meaningful names

**GPIO errors:**
- Need `sudo` for GPIO access
- Check pin numbers (BCM, not physical)
- Verify wiring

## Next Steps

1. **Study Examples**: Look at `examples/` directory
   - `blink.json` - Basic timer usage
   - `start_stop_motor.json` - Latching logic
   - `traffic_light.json` - State machine

2. **Read Documentation**:
   - `QUICK_REFERENCE.md` - Instruction syntax
   - `ARCHITECTURE.md` - How it works internally
   - `README.md` - Complete feature list

3. **Build Something**:
   - Home automation
   - Garden watering system
   - Temperature control
   - Security system
   - Whatever you imagine!

## Getting Help

### Resources

- Check `QUICK_REFERENCE.md` for instruction syntax
- See `examples/` for working programs
- Read `ARCHITECTURE.md` to understand internals

### Common Questions

**Q: Can I use Arduino code?**
A: No, this is pure ladder logic. But you can interface with Arduino via serial/I2C.

**Q: Does it support analog inputs?**
A: Not yet. Digital I/O only. Future enhancement.

**Q: Can I connect to existing PLCs?**
A: Yes, via Modbus (future enhancement).

**Q: Is it real-time?**
A: Linux on Pi is not real-time, but sufficient for most applications (ms timing).

**Q: Can I mix this with Python code?**
A: Yes! You can read/write tags from Python directly.

## From PLC to Pi: Key Differences

| PLC | Pi Ladder Logic |
|-----|-----------------|
| Proprietary software | Open source, text-based |
| Graphical editor | JSON format (for now) |
| Dedicated I/O modules | GPIO pins |
| Real-time OS | Linux (near real-time) |
| Expensive | Raspberry Pi ($35-75) |
| Rugged hardware | Consumer hardware |
| IEC 61131-3 standard | JSON-based, similar concepts |

## Safety Warning

⚠️ **IMPORTANT**: Raspberry Pi is NOT a safety-rated PLC!

- **DO**: Use for learning, prototyping, non-critical automation
- **DO**: Implement emergency stops in hardware
- **DO NOT**: Use for life-safety or critical industrial applications
- **DO NOT**: Control dangerous equipment without proper safeties

For industrial applications, use proper safety-rated PLCs.

---

## Ready to Go!

You now have everything you need to start programming. Begin with the examples, experiment, and build something amazing!

**Happy Coding!** 🏭⚡🔧
