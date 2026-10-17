# TOYSOUND-01: Low-Power Digital Sound Controller ASIC

**TOYSOUND-01** is a minimal digital ASIC designed for a toy sound module implemented in **SCL 1.2 µm CMOS (C1D)**. A single button cycles through four square-wave melodies. The design is architected for Chip-On-Board (COB) direct wire-bonding on a minimal PCB.

---

## RTL-to-GDSII Flow Structure

The repository is structured to follow the standard sequential ASIC design flow:

```
01_toysound/
├── 01_rtl/         ── Step 1: SystemVerilog RTL design files
│   ├── pkg/        ── Global constants and note frequency definitions
│   ├── peripherals/── Button debounce filter
│   ├── core/       ── Sound controller FSM, sequencer ROM, timer, tone generator
│   └── top/        ── Top-level wrapper module
├── 02_tb/          ── Step 2: Verification testbench (toysound_top_tb.sv)
├── 03_sim/         ── Step 3: Functional simulation output & waveform directory
├── 04_syn/         ── Step 4: Logic synthesis (Yosys scripts, netlist, cell statistics)
├── 05_pnr/         ── Step 5: Physical design / Place & Route (Floorplanning, CTS, Routing, GDSII)
├── 06_docs/        ── Step 6: Engineering PDF report & design documentation
│
├── synth.tcl       ── Yosys ASIC logic synthesis script
└── build_report.py ── Automated engineering documentation generator
```

---

## Architecture Overview

```
[BUTTON] ──> [DEBOUNCE] ──> [SOUND CONTROLLER FSM]
                                   │
                           [SOUND SEQUENCER]
                                   │
                     [TIMER] ──> [TONE GENERATOR]
                                       │
                                [SOUND_OUT PAD]
```

### Pinout (6-Pad COB Interface)
| Pin | Name | Direction | Description |
|:---:|:----:|:---------:|:------------|
| 1 | `VDD` | Power | Supply Voltage |
| 2 | `GND` | Power | Ground |
| 3 | `CLK` | Input | System Clock (1 MHz target) |
| 4 | `RESET_N` | Input | Active-Low Asynchronous Reset |
| 5 | `BTN` | Input | Active-Low Song Selection Button |
| 6 | `SOUND_OUT` | Output | Tone PWM Square-Wave Output |

---

## How to Run

### 1. Functional Verification (Simulation)
Compile and run the testbench with **Icarus Verilog**:
```bash
iverilog -g2012 -o 03_sim/toysound.vvp \
    01_rtl/pkg/toysound_pkg.sv \
    01_rtl/peripherals/button_debounce.sv \
    01_rtl/core/timer.sv \
    01_rtl/core/tone_generator.sv \
    01_rtl/core/sound_sequencer.sv \
    01_rtl/core/sound_controller.sv \
    01_rtl/top/toysound_top.sv \
    02_tb/toysound_top_tb.sv

vvp 03_sim/toysound.vvp
```

To view waveforms:
```bash
gtkwave 03_sim/waveforms/toysound_top_tb.vcd
```

### 2. Logic Synthesis
Run synthesis using **Yosys** targeting the **SCL 1.2 µm CMOS (C1D)** open-source standard cell library:
```bash
yosys -c synth.tcl
```
*Note: `synth.tcl` targets `c1d_core_typ.lib` (typical PVT corner: 5V, 27°C). Ensure your local SCL 1.2 µm Liberty file is placed in `04_syn/` or update the path in `synth.tcl`.*

Outputs generated in `04_syn/`:
- `04_syn/toysound_netlist.v` — Synthesized gate-level netlist
- `04_syn/toysound_stats.txt` — Standard cell count and area report

### 3. Generate Engineering Report
Generate the complete LaTeX engineering PDF documentation:
```bash
python build_report.py
```
Output: `06_docs/TOYSOUND_01_ENGINEERING_REPORT.pdf`
