# TOYSOUND-01 — PDK Requirements and Inventory
**Document:** TOYSOUND_01_PDK_REQUIREMENTS  
**Version:** 1.0  
**Date:** 2026-11-03  
**Status:** ACTUAL inspection — files confirmed present unless marked UNCONFIRMED

---

## PDK Root

```
C:\Users\arpit\Desktop\COB\pdk\scl-1p2um\
  SCL 1.2 µm PDK\
    SCL_C1D_PDK_17092026\
      Analog_C1D\
      Digital_C1D\
      PadFrame_C1D\
```

---

## 1. Digital Standard Cell Library — CONFIRMED PRESENT

### Liberty Timing/Power Files
| File | Corner | Size | Status |
|------|--------|------|--------|
| `digital_c1d/lib/c1d_core_typ.lib` | Typical (27°C, 5V, nom_process=1.0) | 930 kB | ✅ CONFIRMED |
| `digital_c1d/lib/c1d_core_max.lib` | Slow/max | 930 kB | ✅ CONFIRMED |
| `digital_c1d/lib/c1d_core_min.lib` | Fast/min | 934 kB | ✅ CONFIRMED |
| `digital_c1d/lib/scl1u_pads_typ.lib` | I/O pads typical | 156 kB | ✅ CONFIRMED |
| `digital_c1d/lib/scl1u_pads_max.lib` | I/O pads slow | 157 kB | ✅ CONFIRMED |
| `digital_c1d/lib/scl1u_pads_min.lib` | I/O pads fast | 157 kB | ✅ CONFIRMED |

**Liberty key parameters confirmed from `c1d_core_typ.lib`:**
- `nom_voltage`: 5 V (VDD)
- `nom_temperature`: 27°C
- `nom_process`: 1.0
- `voltage_unit`: 1V
- `time_unit`: 1ns
- `leakage_power_unit`: 1pW
- `capacitive_load_unit`: 1 pF
- `default_input_pin_cap`: 0.062 pF
- Wire load model: `wire_load_1` present

### LEF Physical Abstraction Files
| File | Purpose | Status |
|------|---------|--------|
| `digital_c1d/lef/core_c1d.lef` | Standard cell abstracts (294 kB) | ✅ CONFIRMED |
| `digital_c1d/lef/tech_c1d.lef` | Technology LEF (layers, rules) | ✅ CONFIRMED |
| `digital_c1d/lef/io_c1d.lef` | I/O pad abstracts | ✅ CONFIRMED |
| `digital_c1d/lef/corner_c1d.lef` | Corner cell abstracts | ✅ CONFIRMED |

### GDS Layout Files
| File | Content | Status |
|------|---------|--------|
| `digital_c1d/gds/core_c1d.gds` | Standard cell GDS library (501 kB) | ✅ CONFIRMED |
| `digital_c1d/gds/io_c1d.gds` | I/O pad GDS library (934 kB) | ✅ CONFIRMED |

### Verilog Behavioural Models
| File | Purpose | Status |
|------|---------|--------|
| `digital_c1d/verilog/c1d.v` | Standard cell Verilog models for simulation (70 kB) | ✅ CONFIRMED |

### CDL Netlist (LVS Reference)
| File | Purpose | Status |
|------|---------|--------|
| `digital_c1d/cdl/core_iolib_c1d.cdl` | CDL reference for LVS (144 kB) | ✅ CONFIRMED |

---

## 2. Physical Verification Decks — CONFIRMED PRESENT

### DRC (Design Rule Check)
| File | Tool | Status |
|------|------|--------|
| `libs.tech/klayout/tech/drc/drc.lydrc` | KLayout | ✅ CONFIRMED |
| `libs.tech/klayout/c1d_drc.drc` | KLayout | ✅ CONFIRMED (25 kB) |

### LVS (Layout vs Schematic)
| File | Tool | Status |
|------|------|--------|
| `libs.tech/klayout/tech/lvs/lvs.lylvs` | KLayout | ✅ CONFIRMED |
| `libs.tech/klayout/lvs_os_scl_c1d.lvs` | KLayout | ✅ CONFIRMED (15 kB) |

### Layer Map
| File | Purpose | Status |
|------|---------|--------|
| `libs.tech/klayout/scl_c1d.map` | DEF-to-GDS layer mapping | ✅ CONFIRMED (408 bytes) |

### KLayout Technology Files
| File | Purpose | Status |
|------|---------|--------|
| `libs.tech/klayout/scl_c1d.lyp` | KLayout layer properties | ✅ CONFIRMED |
| `libs.tech/klayout/scl_c1d.lyt` | KLayout technology file | ✅ CONFIRMED |

---

## 3. Parasitic Extraction — CONFIRMED PRESENT

| File | Tool | Status |
|------|------|--------|
| `libs.tech/openrcx/scl_c1d.rcx.lib` | OpenRCX (3.2 kB) | ✅ CONFIRMED |

---

## 4. OpenLane/OpenROAD Configuration — CONFIRMED PRESENT

### Script Templates
| File | Stage | Status |
|------|-------|--------|
| `scripts_template/floorplan_c1d.tcl` | Floorplan | ✅ CONFIRMED |
| `scripts_template/pdn_c1d.tcl` | Power distribution | ✅ CONFIRMED |
| `scripts_template/pdn_order.tcl` | PDN ordering | ✅ CONFIRMED |
| `scripts_template/placement_c1d.tcl` | Placement | ✅ CONFIRMED |
| `scripts_template/cts_c1d.tcl` | Clock tree synthesis | ✅ CONFIRMED |
| `scripts_template/routing_c1d.tcl` | Routing | ✅ CONFIRMED |
| `scripts_template/run_sta.tcl` | Static timing analysis | ✅ CONFIRMED |

### OpenLane Config
| File | Purpose | Status |
|------|---------|--------|
| `config/config.tcl` | OpenLane design configuration template | ✅ CONFIRMED (11 kB) |
| `libs.tech/openlane/config.tcl` | OpenLane PDK config | ✅ CONFIRMED |
| `libs.tech/openlane/digital_c1d/config.tcl` | Design-specific config template | ✅ CONFIRMED |

### Python Utilities
| File | Purpose | Status |
|------|---------|--------|
| `libs.tech/klayout/verilog2spice.py` | Converts post-P&R Verilog netlist to CDL for LVS | ✅ CONFIRMED (7.6 kB) |
| `libs.tech/klayout/sh_py_script` | Shell script template for LVS CDL generation | ✅ CONFIRMED |

---

## 5. Pad Frame — CONFIRMED PRESENT

| Frame size | GDS | CDL | Status |
|-----------|-----|-----|--------|
| 1 mm × 1 mm | `frame1mmx1mm.gds` (71 kB) | `frame1mmx1mm.cdl` (295 bytes) | ✅ CONFIRMED |
| 2 mm × 2 mm | `frame2mmx2mm.gds` | `frame2mmx2mm.cdl` | ✅ CONFIRMED |
| 3 mm × 3 mm | `frame3mmx3mm.gds` | `frame3mmx3mm.cdl` | ✅ CONFIRMED |
| 4 mm × 4 mm | `frame4mmx4mm.gds` | `frame4mmx4mm.cdl` | ✅ CONFIRMED |
| 5 mm × 5 mm | `frame5mmx5mm.gds` | `frame5mmx5mm.cdl` | ✅ CONFIRMED |

DRC and LVS clean verification screenshots for all 5 frame sizes are included in the PDK (`report/drc_report/` and `report/lvs_report/`).

I/O pad GDS for pad frame: `klayout/gds/io_pad_c1d.gds` ✅ CONFIRMED  
I/O pad CDL for pad frame: `klayout/lvs_cdl/io_pad_c1d.cdl` ✅ CONFIRMED

---

## 6. Analog PDK — PARTIALLY CONFIRMED

| Item | File | Status |
|------|------|--------|
| Analog PDK archive | `Analog_C1D/Open_Source_SCL_1.2micron_PDK.zip` (18.8 MB) | ✅ FILE EXISTS — NOT YET EXTRACTED |
| Analog PDK reference doc | `Analog_C1D/Reference Document for SCLs Analog Open Souce PDK (1_2um CMOS Process).pdf` (1.3 MB) | ✅ FILE EXISTS — NOT YET READ |
| NMOS SPICE models | Inside .zip | ⚠️ NOT YET CONFIRMED |
| PMOS SPICE models | Inside .zip | ⚠️ NOT YET CONFIRMED |
| Resistor SPICE models | Inside .zip | ⚠️ NOT YET CONFIRMED |
| Capacitor SPICE models | Inside .zip | ⚠️ NOT YET CONFIRMED |
| Device operating ranges | Reference PDF | ⚠️ NOT YET CONFIRMED |
| Model corners (SS/TT/FF) | Inside .zip | ⚠️ NOT YET CONFIRMED |
| Temperature models | Inside .zip | ⚠️ NOT YET CONFIRMED |

> [!IMPORTANT]
> The analog PDK zip **must be extracted and inspected** before any oscillator design or POR design can proceed. This is a blocking dependency for RISK-001 and RISK-013.

---

## 7. Missing or Unconfirmed Items

| Item | Impact | Action required |
|------|--------|-----------------|
| SPICE device models (analog) | Blocks oscillator and POR design | Extract and inspect analog PDK zip |
| PDK I/O pad current specification | Blocks output driver decision | Read `scl1u_pads_typ.lib` and reference PDF |
| Device W/L ranges for analog design | Blocks oscillator transistor sizing | Read analog PDK reference document |
| ESD HBM specification | Blocks PCB interface finalisation | Read Standard_Pad_Frame_C1D.pdf |
| Operating voltage range (min/max) | Blocks power supply specification | Read Liberty min/max corners and reference PDF |
| WSL2 + tool installation status | Blocks all simulation and synthesis | Install WSL2 Ubuntu 22.04; install tools |

---

## 8. Confirmed EDA Flow (per eChipHub readme_for_digital)

| Stage | Tool version | PDK support |
|-------|-------------|-------------|
| RTL simulation (prelayout) | Icarus Verilog (iverilog) | c1d.v available ✅ |
| Waveform viewing | GTKWave | No PDK dependency ✅ |
| Synthesis | Yosys 0.9 | c1d_core_typ.lib ✅ |
| Floorplan | OpenROAD (via OpenLane 1.0.x) | tech_c1d.lef + core_c1d.lef ✅ |
| Placement | OpenROAD | core_c1d.lef ✅ |
| CTS | OpenROAD | core_c1d.lef ✅ |
| Routing | OpenROAD | tech_c1d.lef ✅ |
| DRC | KLayout 0.30.7 | drc.lydrc ✅ |
| LVS | KLayout | lvs.lylvs + core_iolib_c1d.cdl ✅ |
| PEX | OpenRCX | scl_c1d.rcx.lib ✅ |
| STA | OpenSTA | c1d_core_*.lib ✅ |
| Post-layout simulation | Icarus Verilog + SDF | c1d.v + SDF from STA ✅ |
| Analog SPICE simulation | Ngspice | Pending analog PDK extraction ⚠️ |

