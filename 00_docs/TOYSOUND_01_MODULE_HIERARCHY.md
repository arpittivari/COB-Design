# TOYSOUND-01 — Module Hierarchy Specification
**Document:** TOYSOUND_01_MODULE_HIERARCHY  
**Version:** 1.0  
**Date:** 2026-11-03  
**Status:** PROPOSED — Pending ADL-017 resolution (continuous tone vs one-shot melody)

---

## Approved Module Hierarchy (Continuous-Tone Architecture)

```
toysound_top
├── [analog/custom] osc_wrapper          (oscillator output only — clock source)
│       └── [SPICE] rc_oscillator        (or ring_oscillator — TBD after SPICE analysis)
├── [SPICE/custom]  power_on_reset       (POR — generates reset_n pulse)
├── [RTL]           button_input
│       ├── [RTL]  button_sync           (2-FF synchroniser, async metastability)
│       ├── [RTL]  button_debouncer      (counter-based, 10 ms minimum)
│       └── [RTL]  button_edge_detect    (rising-edge detector on de-asserted-then-reasserted signal)
├── [RTL]           tone_controller      (3-bit FSM + 3-bit state counter)
└── [RTL]           tone_generator
        ├── [RTL]  frequency_divider     (10-bit down-counter, reload on terminal count)
        └── [RTL]  sq_wave_out           (output toggle FF + output enable gate)
```

---

## Module Descriptions

### toysound_top
**Type:** Synthesisable RTL (top integration)  
**Purpose:** Connects all digital sub-blocks and provides wiring to the oscillator clock and POR reset outputs.  
**Ports:** `clk_int` (from osc_wrapper), `reset_n` (from POR), `button_pad`, `sound_out_pad`

> [!NOTE]
> In RTL simulation, `clk_int` and `reset_n` are driven by the testbench. They are NOT synthesised — they come from analog blocks in the actual silicon.

---

### osc_wrapper (analog interface wrapper)
**Type:** Verilog wrapper with no synthesisable content  
**Purpose:** Provides a Verilog `clk` output net to the digital hierarchy. In simulation this is driven by testbench. In silicon it is connected to the output of the RC or ring oscillator custom cell.  
**Implementation:** Transistor-level SPICE / custom cell  
**Not to be:** RTL with `#delay` constructs  

> [!CAUTION]
> A Verilog model with `always #500 clk = ~clk;` is a simulation model ONLY. It does not represent a physical oscillator and cannot be placed-and-routed. The physical oscillator must be designed as a custom analog block.

---

### power_on_reset
**Type:** Transistor-level SPICE / custom cell  
**Purpose:** Generates a synchronous or asynchronous active-low reset pulse at power-up. Holds `reset_n = 0` long enough for supply to stabilise and for all flip-flops to be forced to their reset state.  
**Required characteristics:**  
- Reset pulse width: ≥ 10 µs (target; must be validated)  
- Supply ramp tolerance: functional over supply ramp rates from 0.1 ms to 100 ms  
- Output: `reset_n` (active-low, open-drain with pull-up or CMOS output)

> [!CAUTION]
> Cannot be implemented as synthesisable RTL. Requires explicit transistor-level design and SPICE simulation across PVT corners.

---

### button_input
**Type:** Synthesisable RTL (structural wrapper)  
**Purpose:** Processes the raw external button signal into a single-cycle `btn_event` pulse per confirmed press.

---

### button_sync (two-FF synchroniser)
**Type:** Synthesisable RTL  
**Purpose:** Prevents metastability when the async button signal crosses into the synchronous clock domain.  
**Implementation:** Two cascaded D flip-flops clocked by `clk_int`.  
**Output:** `btn_synced` — synchronised but still potentially bouncy.

---

### button_debouncer
**Type:** Synthesisable RTL  
**Purpose:** Confirms a stable button press for at least 10 ms before generating a confirmed event.  
**Implementation:** Down-counter (10,000 cycles at 1 MHz). Counter resets if button bounces before threshold. Event generated at terminal count.  
**Counter width:** 14 bits (`ceil(log2(10000)) = 14`)  
**Output:** `btn_confirmed` — single-cycle pulse per confirmed press.

> [!WARNING]
> The current RTL uses DEBOUNCE_CYCLES = 1000 (1 ms). This is insufficient for most mechanical push-buttons. Must be updated to 10,000 (10 ms).

---

### button_edge_detect
**Type:** Synthesisable RTL  
**Purpose:** Converts a synchronised, debounced button-press confirmation to a single-cycle rising-edge pulse.  
**Implementation:** One D flip-flop; output = current AND NOT previous.  
**Output:** `btn_event` — one clock cycle high pulse per validated press.

---

### tone_controller
**Type:** Synthesisable RTL  
**Purpose:** Maintains the current tone state. Receives `btn_event` and advances through: OFF → T1 → T2 → T3 → T4 → OFF (cycling).  
**State encoding:** 3 bits (5 states, binary encoded)

| State code | Meaning |
|---|---|
| 3'b000 | OFF |
| 3'b001 | Tone 1 (500 Hz) |
| 3'b010 | Tone 2 (700 Hz) |
| 3'b011 | Tone 3 (900 Hz) |
| 3'b100 | Tone 4 (1,200 Hz) |

**Outputs:** `tone_sel[2:0]` (current tone selection), `tone_en` (1 = tone active, 0 = silence/OFF)

> [!NOTE]
> In the continuous-tone architecture, the controller does NOT wait for a sequence to complete. Each `btn_event` immediately transitions to the next state.

---

### tone_generator
**Type:** Synthesisable RTL  
**Purpose:** Generates the square-wave output at the frequency corresponding to the selected tone.

---

### frequency_divider
**Type:** Synthesisable RTL  
**Purpose:** Programmable down-counter. Loads the divider value N for the selected tone. Counts from N down to 0; at terminal count reloads and signals a toggle event.  
**Counter width:** 10 bits (max N = 1,000)

**Divider values:**

| State | Tone | Target (Hz) | N value | Actual (Hz) | Error |
|---|---|---|---|---|---|
| OFF | — | — | 0 (disabled) | — | — |
| T1 | 500 Hz | 500 | 1,000 | 500.00 | 0.00% |
| T2 | 700 Hz | 700 | 714 | 700.28 | +0.04% |
| T3 | 900 Hz | 900 | 556 | 899.28 | −0.08% |
| T4 | 1,200 Hz | 1,200 | 417 | 1,199.04 | −0.08% |

---

### sq_wave_out
**Type:** Synthesisable RTL  
**Purpose:** Toggles output on each `toggle` pulse from the frequency_divider. When `tone_en = 0`, output is held low.  
**Duty cycle:** 50% (by construction — output toggles at each half-period).

---

## Implementation Classification Summary

| Module | Implementation type | Tool |
|---|---|---|
| toysound_top | Synthesisable RTL | Yosys + OpenROAD |
| osc_wrapper | Custom SPICE / stub | Ngspice (sim) + custom layout |
| power_on_reset | Custom SPICE | Ngspice (sim) + custom layout |
| button_sync | Synthesisable RTL | Yosys + OpenROAD |
| button_debouncer | Synthesisable RTL | Yosys + OpenROAD |
| button_edge_detect | Synthesisable RTL | Yosys + OpenROAD |
| tone_controller | Synthesisable RTL | Yosys + OpenROAD |
| frequency_divider | Synthesisable RTL | Yosys + OpenROAD |
| sq_wave_out | Synthesisable RTL | Yosys + OpenROAD |

---

## Comparison with Existing RTL

| Module needed (this spec) | Module in current 01_rtl/ | Match? | Action |
|---|---|---|---|
| button_sync + debouncer + edge_detect | `button_debounce.sv` (combined) | Partial | Debounce time must change; hierarchy may be flattened or refactored |
| tone_controller (continuous) | `sound_controller.sv` (one-shot) | NO | Rewrite required (pending ADL-017) |
| — (not needed) | `sound_sequencer.sv` | NOT APPLICABLE | Remove if Option A confirmed |
| — (not needed) | `timer.sv` | NOT APPLICABLE | Remove if Option A confirmed |
| tone_generator | `tone_generator.sv` | YES — matches | Keep, verify |
| osc_wrapper | Not present | MISSING | Must be created after oscillator design |
| power_on_reset | Not present | MISSING | Must be created after POR design |
| toysound_top | `toysound_top.sv` | Partial (uses external clk/reset_n) | Must be updated to wire osc + POR outputs |

---

## Open Items

1. **ADL-017:** Confirm continuous tone vs one-shot melody before rewriting `tone_controller`.
2. **Oscillator:** Analog PDK SPICE must be inspected before `osc_wrapper` can be designed.
3. **POR:** SPICE design required; cannot be RTL.
4. **Debounce:** Confirm 10 ms (10,000 cycles) as the correct value.

