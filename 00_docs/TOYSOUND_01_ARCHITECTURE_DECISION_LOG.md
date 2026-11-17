# TOYSOUND-01 — Architecture Decision Log
**Document:** TOYSOUND_01_ARCHITECTURE_DECISION_LOG  
**Version:** 1.0  
**Date:** 2026-11-03  
**Status:** UNDER REVIEW — Pending owner approval before RTL freeze

---

## IMPORTANT NOTICE

> [!CAUTION]
> RTL files have been found in the project tree (`01_rtl/`) that appear to have been generated **before** this architecture specification was formally approved. This log captures the intended frozen architecture. Any RTL that conflicts with this document must be reviewed and reconciled **before** synthesis is accepted as authoritative.

---

## Decision Index

| ADL-ID | Topic | Status | Date |
|--------|-------|--------|------|
| ADL-001 | Process node selection | FROZEN | 2026-10-01 |
| ADL-002 | Functional scope (4 tones, 1 button) | FROZEN | 2026-10-01 |
| ADL-003 | Output waveform type | FROZEN | 2026-10-01 |
| ADL-004 | Clock architecture (internal oscillator) | PROPOSED | OPEN |
| ADL-005 | Oscillator topology selection | OPEN | — |
| ADL-006 | Power-on reset architecture | PROPOSED | OPEN |
| ADL-007 | Button operation mode (active-low) | FROZEN | 2026-10-02 |
| ADL-008 | Debounce interval | PROPOSED | OPEN |
| ADL-009 | Tone frequencies | PROPOSED | OPEN |
| ADL-010 | Tone generation architecture (shared counter) | FROZEN | 2026-10-02 |
| ADL-011 | Output driver (external required) | PROPOSED | OPEN |
| ADL-012 | Pin count and pad type | PROPOSED | OPEN |
| ADL-013 | Module hierarchy | PROPOSED | OPEN |
| ADL-014 | DFT approach (minimal, no scan) | PROPOSED | OPEN |
| ADL-015 | EDA toolchain (Yosys + OpenROAD/OpenLane) | CONFIRMED | 2026-10-01 |
| ADL-016 | Physical verification tool (KLayout) | CONFIRMED | 2026-10-01 |
| ADL-017 | State machine behaviour — sound vs. hold | IMPORTANT OPEN | — |
| ADL-018 | Button press during playback | OPEN | — |
| ADL-019 | Existing RTL vs. this specification | REQUIRES RECONCILIATION | — |

---

## Detailed Decision Records

---

### ADL-001 — Process Node Selection

**Decision:** SCL 1.2 µm CMOS (C1D) process via eChipHub/NIELIT.  
**Status:** FROZEN  
**Rationale:**  
- Low-cost COB target for toy application.  
- Academic and low-volume access through eChipHub.  
- Open-source PDK (C1D) confirmed present with Liberty, LEF, GDS, CDL, DRC, LVS decks.  
- Not substitutable with SKY130 or GF180 without owner permission.

**Evidence:** PDK directory confirmed at `C:\Users\arpit\Desktop\COB\pdk\scl-1p2um\SCL 1.2 µm PDK\SCL_C1D_PDK_17092026\`.

**Operating conditions from Liberty file (c1d_core_typ.lib):**
- Nominal voltage: 5 V (VDD)
- Nominal temperature: 27 °C
- Process: nom_process 1.0

**Corner libraries confirmed present:**  
- `c1d_core_typ.lib` — typical corner  
- `c1d_core_max.lib` — slow corner  
- `c1d_core_min.lib` — fast corner

---

### ADL-002 — Functional Scope

**Decision:** Single push button; five states (OFF + four tones); cyclic operation.  
**Status:** FROZEN  

**Approved state sequence:**

```
Power-on → OFF
Press 1  → Tone 1
Press 2  → Tone 2
Press 3  → Tone 3
Press 4  → Tone 4
Press 5  → OFF
Press 6  → Tone 1 (cycle repeats)
```

**Important:** This is a **tone-on-demand, hold-active** architecture. Each press transitions to the next state. The selected tone plays **continuously** (not as a one-shot sound sequence) until the next press moves to the next state.

> [!WARNING]
> The existing RTL (`sound_sequencer.sv`, `sound_controller.sv`) implements a **one-shot melody sequencer** that plays a short musical sequence per press, then returns to IDLE. This is **architecturally different** from the approved specification above. The RTL must be reconciled with the owner before proceeding.

**Unresolved decision:** Does a tone play continuously while in that state, or does it play a short sequence then become silent until next press? **Owner approval required.**

---

### ADL-003 — Output Waveform Type

**Decision:** Square wave.  
**Status:** FROZEN  
**Rationale:** Simplest digital implementation. No DAC, no PWM filter required. Suitable for piezo transducers and magnetic buzzers with appropriate driver.

---

### ADL-004 — Clock Architecture

**Decision (proposed):** Internal on-chip oscillator. No external crystal. No PLL.  
**Status:** PROPOSED — Pending oscillator SPICE validation.  
**Target frequency:** 1 MHz nominal.

**Risk:** Without SPICE models for the analog PDK (the SPICE zip is present but not yet extracted and inspected), the oscillator cannot be designed or simulated. The Analog PDK zip (`Open_Source_SCL_1.2micron_PDK.zip`) is 18.8 MB and is available in `Analog_C1D/`. Its SPICE models must be inspected before any oscillator topology is finalised.

**Unresolved:** SPICE device models for NMOS, PMOS, resistors, and capacitors in the SCL 1.2 µm process have not yet been confirmed for the analog components.

---

### ADL-005 — Oscillator Topology

**Status:** OPEN — Pending SPICE model inspection.

**Topologies evaluated (conceptually):**

| Topology | Transistors | Passives needed | Area estimate | PVT stability | Recommended? |
|----------|-------------|-----------------|---------------|---------------|--------------|
| CMOS Ring oscillator (odd inverter chain) | 6–12 (3–5 inverters) | None | Very small | Poor (high PVT sensitivity) | Fallback only |
| CMOS RC relaxation oscillator | 10–20 (with comparator) | R + C | Medium | Moderate | Preferred if R/C available |
| Current-starved ring oscillator | 8–16 | None | Small | Better than plain ring | Alternative |
| Schmitt trigger RC oscillator | 6–10 | R + C | Small | Good | Strong candidate |

**Decision pending:** Inspect the Analog PDK SPICE models. Determine if resistor and capacitor models are available. Confirm device W/L ranges. Then select topology and perform SPICE simulation.

**Key risk:** A ring oscillator implemented using RTL `#delay` constructs is **not** a physical oscillator and cannot be used for silicon implementation.

---

### ADL-006 — Power-On Reset Architecture

**Status:** PROPOSED — Pending transistor-level analysis.

**Requirement:** Controller must initialise to OFF state reliably after power-up.

**Proposed approach:** Transistor-level POR circuit using a capacitor-based ramp detector. The capacitor charges through a resistor; the voltage is compared against a threshold to generate an active-low reset pulse.

**Risk:** Standard-cell flip-flops do **not** have a guaranteed power-up state in most CMOS processes. An explicit POR is required.

**Unresolved:** POR circuit must be designed and verified at SPICE level. Cannot be implemented as RTL.

**Reset polarity:** Active-low (`reset_n`). Matches existing RTL.  
**Initial state:** OFF (all flip-flops to known state).

---

### ADL-007 — Button Operation

**Decision:** Active-low button input. External pull-up resistor on PCB. Two-flip-flop synchroniser inside the digital domain. Hardware debounce using a counter.  
**Status:** FROZEN (button polarity and synchroniser topology)

**Active-low rationale:** With an external pull-up, the button pin sits at logic-1 at rest. A press pulls the pin to ground (logic-0). This is the standard low-cost implementation.

---

### ADL-008 — Debounce Interval

**Status:** PROPOSED  
**Proposed value:** 10 ms (10,000 cycles at 1 MHz).  
**Current RTL uses:** 1 ms (1,000 cycles). This is below the standard mechanical debounce time. **Requires owner decision.**

> [!IMPORTANT]
> The existing `button_debounce.sv` uses `DEBOUNCE_CYCLES = 1000` (1 ms at 1 MHz). Standard mechanical push-button bounce times are 5–20 ms. The debounce counter width must accommodate the correct value. At 10 ms / 1 MHz = 10,000 cycles, a 14-bit counter is required (`ceil(log2(10000)) = 14` bits).

---

### ADL-009 — Tone Frequencies

**Status:** PROPOSED  
**Target frequencies and divider calculations:**

| Tone | Target (Hz) | N = f_clk / (2 × f_out) | Actual f_out (Hz) | Error (%) | Counter bits |
|------|-------------|--------------------------|-------------------|-----------|--------------|
| Tone 1 | 500 | 1,000 | 500.0 | 0.00% | 10 |
| Tone 2 | 700 | 714 (round) | 700.28 | +0.04% | 10 |
| Tone 3 | 900 | 556 (round) | 899.28 | −0.08% | 10 |
| Tone 4 | 1,200 | 417 (round) | 1,199.04 | −0.08% | 10 |

**Formula:** $f_{out} = \frac{f_{clk}}{2N}$

**Exact N values:**
- Tone 1: N = 1,000,000 / (2 × 500) = **1,000** exactly
- Tone 2: N = 1,000,000 / (2 × 700) = 714.286 → use **714** (actual: 700.28 Hz, error +0.04%)
- Tone 3: N = 1,000,000 / (2 × 900) = 555.556 → use **556** (actual: 899.28 Hz, error −0.08%)
- Tone 4: N = 1,000,000 / (2 × 1200) = 416.667 → use **417** (actual: 1199.04 Hz, error −0.08%)

**Counter bit width required:** Max N = 1,000. `ceil(log2(1000)) = 10` bits.

**Duty cycle:** 50% (by design — the counter toggles the output at each terminal count).

**Effect of oscillator frequency error:** If the oscillator runs at frequency $f_{clk}' = f_{clk}(1+\epsilon)$ due to PVT variation, then:
$$f_{out}' = f_{out}(1+\epsilon)$$
All tones scale together — the ratio between tones is preserved. A ±20% oscillator variation (typical for an untuned ring oscillator) produces ±20% frequency error on all tones. For a toy application this may be acceptable, but requires validation.

**Decision pending:** Confirm whether the existing RTL note values (A4=440 Hz, C4=261 Hz, etc.) match the approved tone specification, or whether a new mapping is required.

---

### ADL-010 — Tone Generation Architecture

**Decision:** Single shared frequency divider (one counter). Tone selected by loading the appropriate divider value.  
**Status:** FROZEN  
**Rationale:** Minimum area. One counter. Multiplexer selects divider value based on current state.  
**Output enable:** When state is OFF, the output is held low (silence).

---

### ADL-011 — Output Driver

**Status:** PROPOSED — Pending I/O pad specification inspection.

**SCL C1D Liberty file confirms:** VDD = 5 V (nom). I/O pad Liberty file (`scl1u_pads_typ.lib`) is present.

**Piezoelectric buzzer:** High-impedance load (~nF capacitance). The digital output pad may be able to drive it directly if pad current capability is confirmed.

**Magnetic buzzer/speaker:** Low-impedance load (8–32 Ω). Cannot be driven directly from a logic output pad. Requires an external NPN transistor or MOSFET driver.

**Decision pending:** Inspect `io_c1d.lef` and `scl1u_pads_typ.lib` to determine actual I/O pad drive strength and current capability.

---

### ADL-012 — Pin Count

**Status:** PROPOSED  

| Signal | Direction | Pad type needed | Count |
|--------|-----------|-----------------|-------|
| VDD | Power | Power pad | ≥1 |
| VSS | Ground | Ground pad | ≥1 |
| BUTTON | Input | I/O pad (with ESD) | 1 |
| SOUND_OUT | Output | I/O pad (with ESD) | 1 |
| TEST_OUT (optional) | Output | I/O pad | 0 or 1 |

**Minimum physical pad count:** 4 pads + corner cells.

**Notes:**
- No external RESET pin in proposed architecture (POR handles reset internally).
- No external CLOCK pin (internal oscillator).
- COB packaging: pad-ring size is constrained by the die frames available (1 mm × 1 mm minimum per PadFrame CDL files).

---

### ADL-013 — Module Hierarchy

**Status:** PROPOSED

**Approved hierarchy for TOYSOUND-01:**

```
toysound_top                     [synthesisable RTL — top level]
├── ring_oscillator / rc_osc     [SPICE / custom — NOT RTL]
├── power_on_reset               [SPICE / custom — NOT RTL]
├── button_input                 [synthesisable RTL]
│   ├── button_synchronizer      [synthesisable RTL — 2 FF]
│   ├── button_debouncer         [synthesisable RTL — counter]
│   └── button_edge_detector     [synthesisable RTL — 1 FF + AND]
├── tone_controller              [synthesisable RTL — 3-bit FSM + 3-bit counter]
└── tone_generator               [synthesisable RTL]
    ├── frequency_divider        [synthesisable RTL — 10-bit counter]
    └── square_wave_out          [synthesisable RTL — 1 FF toggle]
```

**Important difference from current RTL:** The current RTL includes `sound_sequencer.sv` which implements a melody ROM. This module is **not** in the approved architecture. The approved architecture uses a **continuous tone** mode, not one-shot melodies.

---

### ADL-014 — DFT Approach

**Status:** PROPOSED  

**Recommendation:** No scan chain for this design. Design is small (estimated < 500 gates). Functional test via test mode is sufficient.

**Minimum testability proposed:**
1. SOUND_OUT observable at the pad — functional test at speed.
2. BUTTON input controllable from test equipment.
3. Optional: dedicated TEST pin to bypass the oscillator with an external clock during manufacturing test. Decision pending.

---

### ADL-015 — EDA Toolchain

**Status:** CONFIRMED (per eChipHub guide)

| Stage | Tool | Confirmed by |
|-------|------|--------------|
| RTL simulation | Icarus Verilog (iverilog) | readme_for_digital |
| Waveform viewing | GTKWave | readme_for_digital |
| Synthesis | Yosys 0.9 | readme_for_digital |
| Physical design | OpenLane 1.0.x / OpenROAD | readme_for_digital |
| Physical verification (DRC/LVS) | KLayout 0.30.7 | readme_for_digital |
| Parasitic extraction | OpenRCX | readme_for_digital |
| STA | OpenSTA (via OpenLane) | readme_for_digital |
| SPICE simulation | Ngspice (to be confirmed for analog) | Analog PDK to be inspected |

---

### ADL-016 — Physical Verification

**Status:** CONFIRMED  
**DRC deck:** `drc.lydrc` and `c1d_drc.drc` — confirmed present in KLayout tech directory.  
**LVS deck:** `lvs.lylvs` and `lvs_os_scl_c1d.lvs` — confirmed present.  
**CDL netlist:** `core_iolib_c1d.cdl` — confirmed present for standard cell LVS reference.  
**Layer map:** `scl_c1d.map` — confirmed present.

---

### ADL-017 — Sound Playback Behaviour (CRITICAL OPEN)

**Status:** OPEN — Requires owner decision.

**Option A (Approved specification):** Each press cycles through OFF → T1 → T2 → T3 → T4 → OFF. The tone plays **continuously** until the next press.

**Option B (Current RTL):** Each press triggers a short melody sequence (3-note ROM sequence per tone). After the melody finishes, the controller returns to IDLE. The button can then advance to the next tone.

These are fundamentally different products. The approved specification in Section 2 of this document specifies Option A. **Owner must confirm which behaviour is required.**

---

### ADL-018 — Button Press During Playback

**Status:** OPEN

**If Option A:** Button press during active tone immediately transitions to next tone (or next state). This is simple and natural.

**If Option B (current RTL behaviour):** Button press during playback is ignored until the melody completes.

**Decision required from owner.**

---

### ADL-019 — Existing RTL vs. This Specification

**Status:** REQUIRES RECONCILIATION  

**Observed:** The `01_rtl/` directory contains fully written RTL modules including:
- `toysound_pkg.sv` — note dividers, melody ROM types, FSM states
- `sound_sequencer.sv` — 3-note ROM-based melody sequencer
- `sound_controller.sv` — one-shot play-and-return-to-IDLE FSM
- `tone_generator.sv` — correct architecture, shared divider
- `button_debounce.sv` — correct synchroniser + counter (but 1 ms debounce)
- `timer.sv` — melody duration timer
- `toysound_top.sv` — uses `clk` and `reset_n` as external ports (no internal oscillator)
- `synth.tcl` — Yosys synthesis script targeting `c1d_core_typ.lib`

**This RTL exists and a synthesis script has been written, which means some implementation work was already done before the architecture specification was formally approved.**

**Actions required (pending owner decision):**
1. Confirm functional behaviour (Option A vs B — ADL-017).
2. If Option A: the `sound_sequencer.sv` and `sound_controller.sv` must be rewritten; the `timer.sv` is not required.
3. If Option B: the existing RTL is largely aligned with that behaviour, but the debounce time should be corrected (ADL-008).
4. In either case: the oscillator and POR must be designed at transistor level (analog SPICE) and integrated at the top level. The `toysound_top.sv` must add the oscillator wrapper ports.

---

## Open Decisions Summary

| ADL-ID | Decision required | Owner action |
|--------|-------------------|--------------|
| ADL-004 | Internal oscillator feasibility | Inspect Analog PDK SPICE models |
| ADL-005 | Oscillator topology | After SPICE model inspection |
| ADL-006 | POR circuit design | After SPICE model inspection |
| ADL-008 | Debounce time (10 ms vs 1 ms) | Confirm |
| ADL-009 | Tone frequencies (500/700/900/1200 Hz vs current musical notes) | Confirm |
| ADL-011 | Output driver (piezo vs speaker; external transistor?) | Confirm buzzer type |
| ADL-012 | Pin count (TEST pin?) | Confirm |
| ADL-017 | **CRITICAL: Continuous tone vs one-shot melody** | **MUST CONFIRM BEFORE RTL** |
| ADL-018 | Button during playback behaviour | Linked to ADL-017 |
| ADL-019 | Existing RTL reconciliation | After ADL-017 |

