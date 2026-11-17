# TOYSOUND-01 — Implementation Roadmap
**Document:** TOYSOUND_01_IMPLEMENTATION_ROADMAP  
**Version:** 1.0  
**Date:** 2026-11-03  
**Status:** DRAFT — Pending architecture approval

---

> [!IMPORTANT]
> This roadmap describes the intended implementation sequence. **No RTL implementation beyond architecture review should proceed until Section 1 (Architecture Approval Gate) is formally completed and confirmed.**

---

## Phase 0 — Environment Setup (PREREQUISITE)

**Status:** IN PROGRESS (WSL2 not yet installed)

| Task | Tool | Output | Blocker? |
|------|------|--------|----------|
| Install WSL2 (Ubuntu 22.04 LTS) | Windows feature | Running WSL2 instance | YES — blocks all Linux EDA |
| Install iverilog in WSL2 | `sudo apt install iverilog gtkwave` | iverilog binary | YES |
| Install Yosys 0.9 in WSL2 | Build or apt | yosys binary | YES |
| Install OpenLane 1.0.x (Docker) | OpenLane Docker | OpenLane container | YES |
| Install KLayout 0.30.7 | Ubuntu .deb | klayout binary | YES |
| Install Ngspice | `sudo apt install ngspice` | ngspice binary | YES |
| Configure PDK paths in WSL2 | Edit `cshrc_pdk_env_setting` + `config.tcl` | C1D_DATA env variable set | YES |
| Extract analog PDK zip | `unzip Open_Source_SCL_1.2micron_PDK.zip` | Analog model files | YES for oscillator |
| Set up project in WSL2 | Symlink or copy to `/mnt/c/...` | WSL2-accessible project tree | YES |

---

## Phase 1 — Architecture Approval Gate (**CURRENT PHASE**)

**Deliverables:** All architecture documents (this roadmap set)  
**Status:** IN PROGRESS  

| Decision required | Owner action | Blocking what |
|---|---|---|
| ADL-017: Continuous tone vs one-shot melody | Owner confirmation | All RTL work |
| ADL-005: Oscillator topology | After analog PDK extraction | Oscillator design |
| ADL-008: Debounce time (10 ms vs 1 ms) | Owner confirmation | RTL parameter update |
| ADL-009: Tone frequencies (500/700/900/1200 Hz vs musical notes) | Owner confirmation | RTL constant update |
| ADL-011: Output driver type (piezo vs speaker) | Owner confirmation | PCB design |

**Gate criterion:** All ADL decisions resolved and this specification approved in writing.

---

## Phase 2 — Analog Block Design (SPICE)

**Prerequisite:** Phase 1 approved. Analog PDK extracted. Ngspice installed.

| Task | Tool | Output | Notes |
|------|------|--------|-------|
| Extract and review analog PDK SPICE models | File extraction | Confirmed NMOS/PMOS/R/C models | Must check model corners |
| Design RC oscillator circuit (transistor level) | Ngspice schematic | SPICE netlist | Choose R/C values for ~1 MHz |
| Simulate oscillator startup | Ngspice transient | Startup waveform | Must show oscillation beginning |
| Simulate oscillator steady-state | Ngspice transient | Frequency measurement | Record nominal frequency |
| Simulate oscillator PVT corners (SS/FF 0/85°C VDD 4.5/5.5V) | Ngspice | Frequency vs PVT table | Defines oscillator accuracy |
| Design POR circuit (transistor level) | Ngspice schematic | SPICE netlist | |
| Simulate POR across supply ramp conditions | Ngspice transient | Reset pulse timing | Confirm pulse width across ramp rates |
| Create custom GDS for oscillator | KLayout | oscillator.gds | Manual layout required |
| Create custom GDS for POR | KLayout | por.gds | Manual layout required |
| DRC on oscillator and POR layouts | KLayout | DRC report | Zero violations required |
| Post-layout SPICE simulation | Ngspice + extracted parasitics | Post-layout waveforms | Confirm no significant shift |

---

## Phase 3 — Digital RTL Finalisation

**Prerequisite:** Phase 1 approved (ADL-017 resolved).

| Task | File | Notes |
|------|------|-------|
| Confirm/rewrite tone_controller.sv | `01_rtl/core/tone_controller.sv` | Continuous or one-shot per ADL-017 |
| Update DEBOUNCE_CYCLES to 10,000 in toysound_pkg.sv | `01_rtl/pkg/toysound_pkg.sv` | ADL-008 |
| Update tone divider values to 500/700/900/1200 Hz | `01_rtl/pkg/toysound_pkg.sv` | ADL-009 |
| Remove/retain sound_sequencer.sv and timer.sv | Per ADL-017 decision | |
| Add osc_wrapper.sv (Verilog stub for oscillator) | `01_rtl/analog/osc_wrapper.sv` | Simulation uses testbench clock |
| Add por_wrapper.sv (Verilog stub for POR) | `01_rtl/analog/por_wrapper.sv` | Simulation uses testbench reset |
| Update toysound_top.sv to remove external clk/reset_n | `01_rtl/top/toysound_top.sv` | Wire to osc + POR outputs |
| RTL lint review | Yosys `synth -top` or Verilator | No lint errors |

---

## Phase 4 — RTL Simulation

**Prerequisite:** Phase 3 complete. iverilog installed in WSL2.

| Task | Tool | Evidence |
|------|------|---------|
| Compile all RTL modules | iverilog -g2012 | No compile errors |
| Run VER-D01 through VER-D18 | iverilog + GTKWave | VCD files; all tests pass |
| Measure tone frequencies from VCD | Python script | Frequency table matching design |
| Confirm duty cycle 50% | Python script | |
| Confirm debounce behaviour | VCD inspection | No double-fire on bounce |
| Confirm long-press no repeat | VCD inspection | |
| Run gate-level simulation after synthesis (Phase 5) | iverilog + c1d.v | VER-D20 |

---

## Phase 5 — Synthesis

**Prerequisite:** Phase 4 RTL simulation clean. Yosys installed.

| Task | Tool | Output |
|------|------|--------|
| Update `synth.tcl` with correct RTL file list | Yosys | Updated script |
| Run Yosys synthesis | Yosys 0.9 | `04_syn/toysound_netlist.v` |
| Review synthesis area report | Yosys stat | Gate count; area in µm² (if Liberty data supports) |
| Review cell type distribution | Yosys stat | Identify cell types used |
| Gate-level simulation | iverilog + c1d.v | Functional verification at gate level |
| Pre-layout STA | OpenSTA | Timing report; confirm no setup/hold violations at 1 MHz |

---

## Phase 6 — Physical Design

**Prerequisite:** Phase 5 synthesis clean. OpenLane installed in WSL2. PDK paths configured.

| Step | Script | Output |
|------|--------|--------|
| Configure OpenLane project | Modify `config/config.tcl` | Project directory in OpenLane/designs/ |
| Floorplan | `floorplan_c1d.tcl` | Floorplan DEF |
| PDN | `pdn_c1d.tcl` | PDN DEF |
| Placement | `placement_c1d.tcl` | Placed DEF |
| CTS | `cts_c1d.tcl` | Clock tree DEF |
| Routing | `routing_c1d.tcl` | Routed DEF |
| Backup run directory | Manual | Archived run before any re-run |

---

## Phase 7 — Physical Verification

| Step | Tool | Deck | Output |
|------|------|------|--------|
| Import routed DEF into KLayout | KLayout | `scl_c1d.map` + LEF files | GDS |
| DRC | KLayout | `drc.lydrc` | DRC clean report |
| Generate CDL from netlist | `verilog2spice.py` | CDL file | |
| LVS | KLayout | `lvs.lylvs` | LVS clean report |
| PEX | OpenRCX | `scl_c1d.rcx.lib` | SPEF file |

---

## Phase 8 — Post-Layout STA and Simulation

| Task | Tool | Output |
|------|------|--------|
| Post-layout STA with SPEF | OpenSTA | Timing report with extracted parasitics |
| SDF generation | OpenSTA | SDF annotation file |
| Post-layout gate simulation | iverilog + SDF | Verified timing-aware simulation |

---

## Phase 9 — Analog-Digital Integration and Tape-Out Preparation

| Task | Notes |
|------|-------|
| Integrate oscillator GDS with digital core GDS | Custom merge in KLayout |
| Integrate POR GDS | Custom merge |
| Assemble pad frame GDS (select appropriate frame size) | Use frame1mmx1mm.gds or larger |
| Final DRC on full assembled GDS | Must be clean |
| Final LVS on full assembled GDS | Must be clean |
| Submit to eChipHub/NIELIT for manufacturing | Follow OS-series submission procedure |

---

## Milestones Summary

| Milestone | Description | Phase |
|-----------|-------------|-------|
| M0 | WSL2 + tools installed | Phase 0 |
| M1 | Architecture specification approved by owner | Phase 1 |
| M2 | Analog PDK inspected; oscillator topology selected | Phase 2 |
| M3 | Oscillator SPICE validated (TT corner) | Phase 2 |
| M4 | Oscillator PVT corners characterised | Phase 2 |
| M5 | POR circuit SPICE validated | Phase 2 |
| M6 | RTL finalised and lint-clean | Phase 3 |
| M7 | RTL simulation all tests pass | Phase 4 |
| M8 | Synthesis complete; area report reviewed | Phase 5 |
| M9 | Place-and-route complete | Phase 6 |
| M10 | DRC + LVS clean | Phase 7 |
| M11 | Post-layout STA clean | Phase 8 |
| M12 | GDS tape-out submission | Phase 9 |

---

## Project Directory Structure

```
C:\Users\arpit\Desktop\COB\projects\01_toysound\
│
├── 00_docs\               # Architecture documents (this deliverable set)
│   ├── arch\              # Architecture diagrams (editable source)
│   └── reports\           # Generated PDF reports
│
├── 01_rtl\                # RTL source files (version controlled)
│   ├── pkg\               # Package definitions
│   ├── core\              # Core digital logic
│   ├── peripherals\       # Button interface
│   ├── analog\            # Analog wrapper stubs (osc_wrapper, por_wrapper)
│   └── top\               # Top-level integration
│
├── 02_tb\                 # Testbenches
│
├── 03_sim\                # Simulation runs (timestamped subdirectories)
│   └── run_YYYYMMDD_HHMMSS\
│       ├── pre_layout\
│       └── post_layout\
│
├── 04_syn\                # Synthesis outputs
│   ├── c1d_core_typ.lib   # Liberty file (already present)
│   └── run_YYYYMMDD_HHMMSS\
│       ├── toysound_netlist.v
│       └── toysound_stats.txt
│
├── 05_pnr\                # Place and route (OpenLane runs)
│   └── run_YYYYMMDD_HHMMSS\
│
├── 06_analog\             # Analog/custom block designs
│   ├── oscillator\        # SPICE netlist + layout
│   └── por\               # SPICE netlist + layout
│
├── 07_por\                # POR design (may merge with 06_analog)
│
├── 08_dft\                # DFT/testability analysis
│
└── 09_analysis\           # Python analysis scripts
    └── run_analyser.py    # (Future — per Section 15 of requirements)
```

> [!NOTE]
> Never overwrite a successful run. Always create a new timestamped subdirectory for each synthesis, simulation, or P&R run. The `.gitignore` should exclude generated outputs but keep source files and scripts.

