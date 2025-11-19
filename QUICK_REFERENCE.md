# Pi Ladder Logic - Quick Reference

## Instruction Quick Reference

### Contacts (Examine Instructions)

```
--|XIC|--    Examine If Closed (NO)
  TAG       Passes power when TAG is TRUE

--|XIO|--    Examine If Open (NC)
  TAG       Passes power when TAG is FALSE
```

### Coils (Output Instructions)

```
--|OTE|--    Output Energize
  TAG       TAG = rung_state

--|OTL|--    Output Latch
  TAG       Sets TAG = TRUE (stays TRUE)

--|OTU|--    Output Unlatch
  TAG       Sets TAG = FALSE

--|OSR|--    One Shot Rising
  TAG       Triggers once on rising edge
```

### Timers

```
--|TON|--    Timer On Delay
  TAG       Delays TRUE transition
  PRE       
            Tags: .DN .TT .EN .ACC .PRE

--|TOF|--    Timer Off Delay
  TAG       Delays FALSE transition
  PRE       
            Tags: .DN .TT .EN .ACC .PRE
```

### Counters

```
--|CTU|--    Count Up
  TAG       Increments on rising edge
  PRE       
  RST       Tags: .DN .CU .ACC .PRE

--|CTD|--    Count Down
  TAG       Decrements on rising edge
  PRE       
            Tags: .DN .CD .ACC .PRE
```

## JSON Instruction Syntax

### Contacts
```json
{"type": "XIC", "tag": "INPUT_1"}
{"type": "XIO", "tag": "STOP_BTN"}
```

### Coils
```json
{"type": "OTE", "tag": "OUTPUT_1"}
{"type": "OTL", "tag": "MOTOR_START"}
{"type": "OTU", "tag": "MOTOR_START"}
{"type": "OSR", "tag": "TRIGGER"}
```

### Timers
```json
{"type": "TON", "tag": "TIMER_1", "preset": 5000}
{"type": "TOF", "tag": "TIMER_2", "preset": 2000}
```

### Counters
```json
{"type": "CTU", "tag": "COUNT_1", "preset": 100, "reset_tag": "RESET"}
{"type": "CTD", "tag": "COUNT_2", "preset": 50}
```

## Common Patterns

### Start-Stop Station
```json
{
  "rungs": [
    {
      "rung_id": 0,
      "instructions": [
        {"type": "XIC", "tag": "START"},
        {"type": "OTL", "tag": "RUN"}
      ]
    },
    {
      "rung_id": 1,
      "instructions": [
        {"type": "XIC", "tag": "RUN"},
        {"type": "XIO", "tag": "STOP"},
        {"type": "OTE", "tag": "RUN"}
      ]
    },
    {
      "rung_id": 2,
      "instructions": [
        {"type": "XIC", "tag": "STOP"},
        {"type": "OTU", "tag": "RUN"}
      ]
    }
  ]
}
```

### Delay On/Off
```json
{
  "rungs": [
    {
      "rung_id": 0,
      "comment": "2 second on-delay",
      "instructions": [
        {"type": "XIC", "tag": "INPUT"},
        {"type": "TON", "tag": "ON_DELAY", "preset": 2000}
      ]
    },
    {
      "rung_id": 1,
      "instructions": [
        {"type": "XIC", "tag": "ON_DELAY.DN"},
        {"type": "OTE", "tag": "OUTPUT"}
      ]
    }
  ]
}
```

### Flasher (Blink)
```json
{
  "rungs": [
    {
      "rung_id": 0,
      "instructions": [
        {"type": "XIO", "tag": "FLASH_TIMER.DN"},
        {"type": "TON", "tag": "FLASH_TIMER", "preset": 500}
      ]
    },
    {
      "rung_id": 1,
      "instructions": [
        {"type": "XIC", "tag": "FLASH_TIMER.DN"},
        {"type": "OSR", "tag": "FLASH_PULSE"}
      ]
    },
    {
      "rung_id": 2,
      "instructions": [
        {"type": "XIC", "tag": "FLASH_PULSE"},
        {"type": "XIO", "tag": "FLASH_OUTPUT"},
        {"type": "OTL", "tag": "FLASH_OUTPUT"}
      ]
    },
    {
      "rung_id": 3,
      "instructions": [
        {"type": "XIC", "tag": "FLASH_PULSE"},
        {"type": "XIC", "tag": "FLASH_OUTPUT"},
        {"type": "OTU", "tag": "FLASH_OUTPUT"}
      ]
    }
  ]
}
```

## System Tags

```
_SYSTEM.RUNNING      - Runtime active (TRUE/FALSE)
_SYSTEM.SCAN_TIME    - Current scan time (ms)
_SYSTEM.CYCLE_COUNT  - Total scan cycles
_SYSTEM.ERROR        - Error flag
```

## GPIO Pin Reference (Raspberry Pi 4)

### BCM Pin Numbers (Use these in config)

Common pins:
- GPIO 17 (Pin 11) - Input 1
- GPIO 27 (Pin 13) - Input 2
- GPIO 22 (Pin 15) - Input 3
- GPIO 23 (Pin 16) - Output 1
- GPIO 24 (Pin 18) - Output 2
- GPIO 25 (Pin 22) - Output 3

## Command Line

```bash
# Basic run
python3 main.py program.json

# Custom scan time
python3 main.py program.json --scan-time 50

# Custom I/O config
python3 main.py program.json --io-config my_io.json

# Simulation mode (no GPIO)
python3 main.py program.json --no-io

# Debug mode
python3 main.py program.json --debug
```

## Timing Reference

| Preset Value | Time |
|--------------|------|
| 100 | 100ms (0.1 sec) |
| 500 | 500ms (0.5 sec) |
| 1000 | 1 second |
| 5000 | 5 seconds |
| 10000 | 10 seconds |
| 60000 | 1 minute |

## Typical Scan Times

| Application | Scan Time |
|-------------|-----------|
| Simple I/O | 10-20ms |
| Motor control | 50-100ms |
| Process control | 100-500ms |
| Slow monitoring | 500-1000ms |

## Tag Naming Conventions

Good practices:
- `START_BTN`, `STOP_BTN` - Descriptive input names
- `MOTOR_1_RUN`, `PUMP_ENABLE` - Clear output names
- `TIMER_DELAY_ON`, `COUNTER_PARTS` - Function-based names
- Use UPPERCASE for consistency
- Use underscores for readability

Avoid:
- `X`, `Y`, `Z` - Too generic
- `temp1`, `temp2` - Unclear purpose
- Mixed case inconsistently

## Safety Checklist

- [ ] Emergency stop implemented in hardware
- [ ] All outputs initialized to safe state
- [ ] Scan time appropriate for application
- [ ] Physical interlocks for dangerous equipment
- [ ] Tested in simulation before deployment
- [ ] GPIO current limits respected
- [ ] Optocouplers used for high voltage
- [ ] Backup/fallback logic implemented
