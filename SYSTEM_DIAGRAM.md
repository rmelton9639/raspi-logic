# Pi Ladder Logic - System Diagram

## Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          RASPBERRY PI HARDWARE                              │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         GPIO PINS (BCM)                             │   │
│  │                                                                     │   │
│  │   INPUTS                              OUTPUTS                      │   │
│  │   GPIO17 ◄── Button                   GPIO23 ──► Relay/Motor       │   │
│  │   GPIO27 ◄── Sensor                   GPIO24 ──► LED               │   │
│  │   GPIO22 ◄── E-Stop                   GPIO25 ──► Indicator         │   │
│  │   GPIO5  ◄── Switch                   GPIO18 ──► Output            │   │
│  │                                                                     │   │
│  └──────────────────────┬──────────────────────────────────────────────┘   │
│                         │                                                  │
└─────────────────────────┼──────────────────────────────────────────────────┘
                          │
                          │ GPIO Interface
                          │
┌─────────────────────────▼──────────────────────────────────────────────────┐
│                                                                             │
│                    PI LADDER LOGIC SOFTWARE                                 │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      GPIO MANAGER (io/gpio_manager.py)               │  │
│  │                                                                      │  │
│  │  ┌─────────────────────┐          ┌──────────────────────┐         │  │
│  │  │   Input Scanner     │          │   Output Driver      │         │  │
│  │  │                     │          │                      │         │  │
│  │  │  GPIO → Tag Map     │          │  Tag → GPIO Map      │         │  │
│  │  │  START_BTN = Pin17  │          │  MOTOR_RUN = Pin23   │         │  │
│  │  │  STOP_BTN = Pin27   │          │  STATUS_LED = Pin24  │         │  │
│  │  │                     │          │                      │         │  │
│  │  └──────────┬──────────┘          └────────┬─────────────┘         │  │
│  │             │                               │                       │  │
│  └─────────────┼───────────────────────────────┼───────────────────────┘  │
│                │                               │                          │
│                │ Read Inputs                   │ Write Outputs            │
│                │                               │                          │
│  ┌─────────────▼───────────────────────────────▼───────────────────────┐  │
│  │                                                                      │  │
│  │                   TAG DATABASE (core/tags.py)                       │  │
│  │                   Thread-Safe Tag Storage                           │  │
│  │                                                                      │  │
│  │  ┌────────────────┬────────────────┬─────────────────┐             │  │
│  │  │ INPUT TAGS     │ INTERNAL TAGS  │ OUTPUT TAGS     │             │  │
│  │  │                │                │                 │             │  │
│  │  │ START_BTN = 0  │ TIMER_1.DN = 0 │ MOTOR_RUN = 0   │             │  │
│  │  │ STOP_BTN = 0   │ TIMER_1.TT = 0 │ STATUS_LED = 0  │             │  │
│  │  │ E_STOP = 0     │ TIMER_1.ACC=0  │ RED_LIGHT = 0   │             │  │
│  │  │ SENSOR_1 = 0   │ COUNT_1.ACC=0  │ GREEN_LIGHT = 0 │             │  │
│  │  │                │                │                 │             │  │
│  │  └────────────────┴────────────────┴─────────────────┘             │  │
│  │                                                                      │  │
│  └──────────────────────────────┬───────────────────────────────────────┘  │
│                                 │                                          │
│                                 │ Read/Write Tags                          │
│                                 │                                          │
│  ┌──────────────────────────────▼──────────────────────────────────────┐  │
│  │                                                                      │  │
│  │               LADDER LOGIC PROCESSOR (core/runtime.py)              │  │
│  │                                                                      │  │
│  │  ┌────────────────────────────────────────────────────────────────┐ │  │
│  │  │  SCAN CYCLE LOOP                                               │ │  │
│  │  │                                                                │ │  │
│  │  │  1. ┌─────────────────┐                                       │ │  │
│  │  │     │  READ INPUTS    │  GPIO → Tags                          │ │  │
│  │  │     └────────┬────────┘                                       │ │  │
│  │  │              │                                                │ │  │
│  │  │  2. ┌────────▼────────┐                                       │ │  │
│  │  │     │ EXECUTE RUNGS   │                                       │ │  │
│  │  │     │                 │  ┌──────────────────────────────────┐ │ │  │
│  │  │     │  Rung 0: ──|   |────( )──                             │ │ │  │
│  │  │     │  Rung 1: ──| |──|/|──( )──                            │ │ │  │
│  │  │     │  Rung 2: ──|TON|──( )──                               │ │ │  │
│  │  │     │  Rung 3: ──|CTU|──( )──                               │ │ │  │
│  │  │     │  ...                                                   │ │ │  │
│  │  │     │                 └──────────────────────────────────────┘ │ │  │
│  │  │     └────────┬────────┘                                       │ │  │
│  │  │              │                                                │ │  │
│  │  │  3. ┌────────▼────────┐                                       │ │  │
│  │  │     │ WRITE OUTPUTS   │  Tags → GPIO                          │ │  │
│  │  │     └────────┬────────┘                                       │ │  │
│  │  │              │                                                │ │  │
│  │  │  4. ┌────────▼────────┐                                       │ │  │
│  │  │     │  HOUSEKEEPING   │  Update stats, check errors           │ │  │
│  │  │     └────────┬────────┘                                       │ │  │
│  │  │              │                                                │ │  │
│  │  │  5. ┌────────▼────────┐                                       │ │  │
│  │  │     │ SLEEP/WAIT      │  Maintain scan time (e.g. 100ms)     │ │  │
│  │  │     └────────┬────────┘                                       │ │  │
│  │  │              │                                                │ │  │
│  │  │              └────────► REPEAT                                │ │  │
│  │  │                                                                │ │  │
│  │  └────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                 INSTRUCTION LIBRARY (core/instructions.py)           │  │
│  │                                                                      │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │  │
│  │  │   XIC     │  │   OTE     │  │   TON     │  │   CTU     │       │  │
│  │  │ (NO Cont) │  │  (Coil)   │  │ (Timer)   │  │ (Counter) │       │  │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘       │  │
│  │                                                                      │  │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │  │
│  │  │   XIO     │  │   OTL     │  │   TOF     │  │   CTD     │       │  │
│  │  │ (NC Cont) │  │ (Latch)   │  │ (Timer)   │  │ (Counter) │       │  │
│  │  └───────────┘  └───────────┘  └───────────┘  └───────────┘       │  │
│  │                                                                      │  │
│  │         ┌───────────┐  ┌───────────┐                                │  │
│  │         │   OTU     │  │   OSR     │                                │  │
│  │         │ (Unlatch) │  │(One-Shot) │                                │  │
│  │         └───────────┘  └───────────┘                                │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow During Scan Cycle

```
TIME: T = 0ms (Start of Scan)
┌────────────────────────────────────────────────────────────┐
│  STEP 1: READ INPUTS                                       │
│                                                            │
│  GPIO Pin 17 (Physical) ──► START_BTN = TRUE (Tag)        │
│  GPIO Pin 27 (Physical) ──► STOP_BTN = FALSE (Tag)        │
│  GPIO Pin 22 (Physical) ──► E_STOP = FALSE (Tag)          │
│                                                            │
│  ✓ Input image table updated                               │
└────────────────────────────────────────────────────────────┘

TIME: T = 5ms
┌────────────────────────────────────────────────────────────┐
│  STEP 2: EXECUTE LADDER LOGIC                              │
│                                                            │
│  Rung 0: ──|START_BTN|────|/STOP_BTN|────(MOTOR_RUN)──    │
│           ──|  TRUE  |────|/ FALSE |────(   TRUE   )──    │
│                                                            │
│  Evaluation: TRUE AND (NOT FALSE) = TRUE                   │
│  Result: MOTOR_RUN tag set to TRUE                         │
│                                                            │
│  Rung 1: ──|MOTOR_RUN|────(STATUS_LED)──                  │
│           ──|  TRUE  |────(   TRUE    )──                 │
│                                                            │
│  [... all rungs execute ...]                               │
│                                                            │
│  ✓ All logic evaluated, tags updated                       │
└────────────────────────────────────────────────────────────┘

TIME: T = 85ms
┌────────────────────────────────────────────────────────────┐
│  STEP 3: WRITE OUTPUTS                                     │
│                                                            │
│  MOTOR_RUN = TRUE (Tag) ──► GPIO Pin 23 = HIGH            │
│  STATUS_LED = TRUE (Tag) ──► GPIO Pin 24 = HIGH           │
│  RED_LIGHT = FALSE (Tag) ──► GPIO Pin 25 = LOW            │
│                                                            │
│  ✓ Physical outputs updated                                │
└────────────────────────────────────────────────────────────┘

TIME: T = 90ms
┌────────────────────────────────────────────────────────────┐
│  STEP 4: HOUSEKEEPING                                      │
│                                                            │
│  _SYSTEM.SCAN_TIME = 90ms                                  │
│  _SYSTEM.CYCLE_COUNT = 12543                               │
│  _SYSTEM.RUNNING = TRUE                                    │
│  _SYSTEM.ERROR = FALSE                                     │
│                                                            │
│  ✓ System tags updated                                     │
└────────────────────────────────────────────────────────────┘

TIME: T = 90ms → 100ms
┌────────────────────────────────────────────────────────────┐
│  STEP 5: SLEEP/WAIT                                        │
│                                                            │
│  Target scan time: 100ms                                   │
│  Actual execution: 90ms                                    │
│  Sleep duration: 10ms                                      │
│                                                            │
│  ✓ Waiting to maintain consistent scan time               │
└────────────────────────────────────────────────────────────┘

TIME: T = 100ms → NEXT SCAN BEGINS
```

## File Interaction Map

```
main.py
   │
   ├──► Load Program JSON ──► examples/blink.json
   │
   ├──► Load I/O Config ──► config/io_config.json
   │
   ├──► Create Runtime ──► core/runtime.py
   │                         │
   │                         ├──► LadderProgram
   │                         │      │
   │                         │      ├──► Rung Objects
   │                         │      │      │
   │                         │      │      └──► Instructions ──► core/instructions.py
   │                         │      │
   │                         │      └──► TagDatabase ──► core/tags.py
   │                         │
   │                         └──► Scan Cycle Loop
   │
   └──► Attach I/O ──► io/gpio_manager.py
                         │
                         ├──► Read GPIO Pins
                         └──► Write GPIO Pins
```

## Typical Program Execution Timeline

```
0ms    100ms   200ms   300ms   400ms   500ms   600ms   700ms   800ms
│      │       │       │       │       │       │       │       │
├──────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┤
│Scan 1│Scan 2 │Scan 3 │Scan 4 │Scan 5 │Scan 6 │Scan 7 │Scan 8 │
│      │       │       │       │       │       │       │       │
│      │       │       │       │       │       │       │       │
│Input │Input  │Input  │Input  │Input  │Input  │Input  │Input  │
│ Read │ Read  │ Read  │ Read  │ Read  │ Read  │ Read  │ Read  │
│      │       │       │       │       │       │       │       │
│Logic │Logic  │Logic  │Logic  │Logic  │Logic  │Logic  │Logic  │
│ Exec │ Exec  │ Exec  │ Exec  │ Exec  │ Exec  │ Exec  │ Exec  │
│      │       │       │       │       │       │       │       │
│Output│Output │Output │Output │Output │Output │Output │Output │
│Write │Write  │Write  │Write  │Write  │Write  │Write  │Write  │
│      │       │       │       │       │       │       │       │
└──────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┘
  100ms scan time (configurable)

Example with 500ms timer:
│                         Timer accumulating...              │
└──────────────────────────────────────────────────────────┐│
                                                           Done!
                                                        Timer.DN = TRUE
```

## Instruction Evaluation Example

```
Rung: ──|START|───|/STOP|───|TIMER.DN|───(OUTPUT)──

Initial State:
  START = FALSE
  STOP = FALSE
  TIMER.DN = FALSE
  OUTPUT = ?

Step-by-step evaluation:

1. Rung begins with continuity = TRUE (left rail)
   ┌────┐
   │TRUE│
   └──┬─┘
      │
      
2. XIC("START"): Check if START is TRUE
   START = FALSE → Block continuity
   ┌─────┐
   │FALSE│
   └──┬──┘
      │
      
3. Result: OUTPUT = FALSE (no power to coil)

Next scan, START becomes TRUE:

1. Continuity = TRUE
   ┌────┐
   │TRUE│
   └──┬─┘
      │
      
2. XIC("START"): START = TRUE → Pass continuity
   ┌────┐
   │TRUE│
   └──┬─┘
      │
      
3. XIO("STOP"): STOP = FALSE → Pass continuity
   ┌────┐
   │TRUE│
   └──┬─┘
      │
      
4. XIC("TIMER.DN"): TIMER.DN = FALSE → Block continuity
   ┌─────┐
   │FALSE│
   └──┬──┘
      │
      
5. Result: OUTPUT = FALSE (blocked by timer)

When timer completes (TIMER.DN = TRUE):

All conditions TRUE → OUTPUT = TRUE
```

---

This visual representation shows how all components work together
to create a complete PLC-style control system on Raspberry Pi.
