# Pi Ladder Logic - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│  (Command line / Future: Web HMI / MQTT / Modbus)          │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                   PLC RUNTIME ENGINE                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Main Execution Loop (scan cycle)                    │  │
│  │  - Start/Stop control                                 │  │
│  │  - Timing management                                  │  │
│  │  - Error handling                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐              ┌──────▼──────────┐
│  LADDER LOGIC  │              │   I/O MANAGER   │
│   PROCESSOR    │              │                 │
│                │              │  GPIO Interface │
│ - Tag Database │              │  - Read Inputs  │
│ - Rung Exec    │◄────────────►│  - Write Outputs│
│ - Instructions │              │  - Simulation   │
│ - Timers/Count │              │                 │
└────────────────┘              └────────┬────────┘
                                         │
                        ┌────────────────┴────────────────┐
                        │                                 │
                ┌───────▼────────┐              ┌────────▼────────┐
                │  INPUTS (GPIO) │              │ OUTPUTS (GPIO)  │
                │                │              │                 │
                │  - Buttons     │              │  - Relays       │
                │  - Sensors     │              │  - LEDs         │
                │  - Switches    │              │  - Indicators   │
                └────────────────┘              └─────────────────┘
```

## Scan Cycle Flow

```
START
  │
  ▼
┌─────────────────────┐
│  1. READ INPUTS     │  ◄── GPIO Manager reads all input pins
│  Input Image Table  │      and updates tag database
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. EXECUTE LADDER   │  ◄── Execute rungs sequentially
│    LOGIC            │      - Rung 0 → Rung 1 → ... → Rung N
│                     │      - Each instruction evaluates left-to-right
│  Rung 0: ──| |──( )─│      - Updates internal tags
│  Rung 1: ──| |──( )─│
│  Rung n: ──|/|──( )─│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. WRITE OUTPUTS    │  ◄── GPIO Manager writes output tags
│  Output Image Table │      to physical GPIO pins
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. HOUSEKEEPING     │  ◄── Update scan time, cycle count,
│  System Updates     │      check for errors
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  5. WAIT/SLEEP      │  ◄── Sleep to maintain scan time
│  Maintain Scan Time │      (e.g., 100ms cycle)
└──────────┬──────────┘
           │
           └────────────► REPEAT
```

## Tag Database Structure

```
┌──────────────────────────────────────────────────┐
│              TAG DATABASE                        │
│  (Thread-safe key-value store)                   │
├──────────────────────────────────────────────────┤
│                                                  │
│  USER TAGS:                                      │
│    "START_BTN"      → False                      │
│    "STOP_BTN"       → False                      │
│    "MOTOR_RUN"      → True                       │
│    "STATUS_LED"     → True                       │
│                                                  │
│  TIMER TAGS:                                     │
│    "TIMER_1.DN"     → True   (Done bit)          │
│    "TIMER_1.TT"     → False  (Timing bit)        │
│    "TIMER_1.EN"     → True   (Enable bit)        │
│    "TIMER_1.ACC"    → 5000   (Accumulated ms)    │
│    "TIMER_1.PRE"    → 5000   (Preset ms)         │
│                                                  │
│  COUNTER TAGS:                                   │
│    "COUNT_1.DN"     → False  (Done bit)          │
│    "COUNT_1.CU"     → True   (Count up bit)      │
│    "COUNT_1.ACC"    → 45     (Accumulated)       │
│    "COUNT_1.PRE"    → 100    (Preset)            │
│                                                  │
│  SYSTEM TAGS:                                    │
│    "_SYSTEM.RUNNING"     → True                  │
│    "_SYSTEM.SCAN_TIME"   → 12.34 ms              │
│    "_SYSTEM.CYCLE_COUNT" → 15042                 │
│    "_SYSTEM.ERROR"       → False                 │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Instruction Execution Flow

```
RUNG EXECUTION:
Initial state: rung_state = TRUE (power from left rail)

┌────────────┐         ┌────────────┐         ┌────────────┐
│ Instruction│  state  │ Instruction│  state  │ Instruction│
│     1      ├────────►│     2      ├────────►│     3      │
│   (XIC)    │  TRUE   │   (XIO)    │  FALSE  │   (OTE)    │
└────────────┘         └────────────┘         └────────────┘
     │                      │                      │
     │ Check if             │ Check if             │ Set output
     │ tag is TRUE          │ tag is FALSE         │ to rung state
     │                      │                      │
     └► TRUE                └► FALSE               └► Output = FALSE


Example Rung:
  ──| START_BTN |────|/STOP_BTN|────( MOTOR_RUN )──
     XIC              XIO            OTE
     
Execution:
1. rung_state = TRUE (start)
2. XIC("START_BTN"): If START_BTN is TRUE → rung_state = TRUE
3. XIO("STOP_BTN"): If STOP_BTN is FALSE → rung_state = TRUE  
4. OTE("MOTOR_RUN"): Set MOTOR_RUN = rung_state (TRUE)
```

## Timer Operation (TON)

```
INPUT SIGNAL:
         ┌─────────────────────┐
    ─────┘                     └─────
    
TIMING (TT) BIT:
         ┌──────────┐
    ─────┘          └────────────────
         │◄─ PRE ─►│
    
DONE (DN) BIT:
                    ┌──────────────────
    ────────────────┘
                    │◄── Stays TRUE until input FALSE

ACCUMULATED VALUE:
    0   ┌────────────► PRE
        │          /
    ────┘         / 
         │◄─PRE─►│
         
States:
- EN (Enable): TRUE when input is TRUE
- TT (Timing): TRUE while 0 < ACC < PRE
- DN (Done):   TRUE when ACC >= PRE
- ACC: Counts from 0 to PRE (milliseconds)
```

## Counter Operation (CTU)

```
INPUT PULSES:
    ──┐  ┐  ┐  ┐  ┐
      └──┘  └──┘  └──┘  └──┘  └──

ACCUMULATED COUNT:
        ┌──────┐
       1│  ┌───┘
        │ 2│  ┌────┐
        │  │ 3│   4│
    ────┘  └──┘    └────────
    
DONE (DN) BIT:
    (If PRE = 3)
              ┌───────────────
    ──────────┘
              │◄── Once count >= preset
              
RESET:
    Normal ───────────┐     ┐────
                      └─────┘
    
    Count  ────┐         ┌───
               └─────────┘0
```

## GPIO Manager States

```
HARDWARE MODE (Raspberry Pi with RPi.GPIO):
┌─────────────────────────────────────────┐
│           GPIO Manager                  │
│                                         │
│  Physical Pins ◄──► BCM Pin Numbers     │
│                                         │
│  Pin 11 (GPIO17) ──► "START_BTN"        │
│  Pin 13 (GPIO27) ──► "STOP_BTN"         │
│  Pin 16 (GPIO23) ◄── "MOTOR_RUN"        │
│  Pin 18 (GPIO24) ◄── "STATUS_LED"       │
│                                         │
└─────────────────────────────────────────┘
                  │
                  ▼
        ┌──────────────────┐
        │  Raspberry Pi    │
        │  GPIO Hardware   │
        └──────────────────┘

SIMULATION MODE (Development machine):
┌─────────────────────────────────────────┐
│       GPIO Manager (Simulation)         │
│                                         │
│  simulation_inputs = {                  │
│    "START_BTN": False,                  │
│    "STOP_BTN": False,                   │
│    "SENSOR_1": True                     │
│  }                                      │
│                                         │
│  Outputs written to tag database only   │
│  No physical hardware interaction       │
│                                         │
└─────────────────────────────────────────┘
```

## Program Loading Process

```
JSON FILE:
┌─────────────────────────────┐
│ {                           │
│   "program_name": "...",    │
│   "scan_time_ms": 100,      │
│   "rungs": [                │
│     {                       │
│       "rung_id": 0,         │
│       "instructions": [     │
│         {"type": "XIC"...}, │
│         {"type": "OTE"...}  │
│       ]                     │
│     }                       │
│   ]                         │
│ }                           │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│   JSON Parser               │
│   (load_from_json)          │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│   Instruction Factory       │
│   - Creates XIC, OTE, etc.  │
│   - Initializes with params │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│   Rung Objects              │
│   - Contains instructions   │
│   - Ready for execution     │
└─────────────────────────────┘
            │
            ▼
┌─────────────────────────────┐
│   Ladder Program Object     │
│   - List of rungs           │
│   - Tag database            │
│   - Ready to run            │
└─────────────────────────────┘
```

## Class Relationships

```
┌──────────────┐
│ PLCRuntime   │
│              │
│ + start()    │
│ + stop()     │
│ + run()      │
└──────┬───────┘
       │ owns
       ▼
┌──────────────┐          ┌──────────────┐
│LadderProgram │◄─────────│ GPIOManager  │
│              │ attached │              │
│ + rungs[]    │          │ + inputs[]   │
│ + tags       │          │ + outputs[]  │
│ + execute()  │          └──────────────┘
└──────┬───────┘
       │ contains
       ▼
┌──────────────┐          ┌──────────────┐
│    Rung      │          │ TagDatabase  │
│              │ uses     │              │
│ + rung_id    ├─────────►│ + tags{}     │
│ + instruct[] │          │ + set()      │
│ + execute()  │          │ + get()      │
└──────┬───────┘          └──────────────┘
       │ contains
       ▼
┌──────────────┐
│ Instruction  │
│  (abstract)  │
│              │
│ + evaluate() │
└──────┬───────┘
       │ implemented by
       ▼
┌──────────────┬──────────────┬──────────────┐
│     XIC      │     OTE      │     TON      │
│     XIO      │     OTL      │     TOF      │
│              │     OTU      │     CTU      │
│              │     OSR      │     CTD      │
└──────────────┴──────────────┴──────────────┘
```

## File Organization

```
pi_ladder_logic/
│
├── main.py                      # Entry point
│   └─► Creates PLCRuntime
│       └─► Loads program & I/O
│           └─► Starts execution loop
│
├── core/
│   ├── __init__.py
│   ├── runtime.py               # PLCRuntime, LadderProgram, Rung
│   ├── tags.py                  # TagDatabase (thread-safe)
│   └── instructions.py          # All instruction classes
│
├── io/
│   ├── __init__.py
│   └── gpio_manager.py          # GPIOManager, IOPoint
│
├── config/
│   └── io_config.json           # Pin mappings
│
├── examples/
│   ├── blink.json               # Example programs
│   ├── start_stop_motor.json
│   └── traffic_light.json
│
└── web/ (future)
    └── server.py                # Web HMI
```

## Threading Model

```
SINGLE-THREADED EXECUTION:
┌──────────────────────────────────────┐
│       Main Thread                    │
│  ┌────────────────────────────────┐  │
│  │  while running:                │  │
│  │    read_inputs()               │  │
│  │    execute_ladder()            │  │
│  │    write_outputs()             │  │
│  │    sleep(scan_time)            │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘

Tag database uses locks for thread safety
to allow future multi-threaded extensions
(e.g., web server, data logging)
```

## Future Extensions

```
Current:                    Planned:
┌─────────┐               ┌─────────┐
│  CLI    │               │ Web HMI │
└────┬────┘               └────┬────┘
     │                         │
     ▼                         ▼
┌─────────┐               ┌─────────┐
│ Runtime │               │ Runtime │
└────┬────┘               └────┬────┘
     │                         │
     ▼                    ┌────┴────┐
┌─────────┐               │         │
│  GPIO   │          ┌────▼────┐ ┌──▼──────┐
└─────────┘          │  GPIO   │ │ Modbus  │
                     └─────────┘ └─────────┘
```

---

This architecture provides:
- Clean separation of concerns
- Extensibility for future features
- Familiar patterns for PLC programmers
- Safety through scan cycle isolation
