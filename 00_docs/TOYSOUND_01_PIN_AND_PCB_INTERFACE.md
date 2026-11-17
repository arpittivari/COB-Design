# TOYSOUND-01 — Pin and PCB Interface Specification
**Document:** TOYSOUND_01_PIN_AND_PCB_INTERFACE  
**Version:** 1.0  
**Date:** 2026-11-03  
**Status:** PROPOSED — Pending PDK I/O pad specification confirmation

---

## 1. Logical Interface Summary

| Signal | Direction | Logic Level | Active State | Description |
|--------|-----------|-------------|--------------|-------------|
| VDD | Power | 5 V (nom) | — | Positive supply. From Liberty: `nom_voltage = 5 V` |
| VSS | Ground | 0 V | — | Ground reference |
| BUTTON | Input | 5 V CMOS | Active-Low (0 = pressed) | User push button, debounced on-chip |
| SOUND_OUT | Output | 5 V CMOS | High = sound signal | Square-wave audio output |

> [!NOTE]
> No external CLOCK pin. Clock is generated internally by the on-chip oscillator (architecture pending validation).  
> No external RESET pin in proposed architecture. Reset is generated internally by the POR circuit (architecture pending validation).

---

## 2. Physical Pad Count

The difference between logical I/O count and physical pad count is significant in ASIC design.

### Logical pins: 4
`VDD`, `VSS`, `BUTTON`, `SOUND_OUT`

### Physical pads required:

| Pad function | Required count | PDK pad type | Notes |
|---|---|---|---|
| VDD power pad | 1 (minimum) | Power pad from io_c1d library | One per power domain |
| VSS ground pad | 1 (minimum) | Ground pad from io_c1d library | One per ground domain |
| BUTTON input pad | 1 | Bidirectional or input pad with ESD | ESD protection mandatory |
| SOUND_OUT output pad | 1 | Output pad | Drive strength TBD |
| Corner cells | 4 | Corner pad (corner_c1d.lef) | Required at all four die corners |
| Optional TEST/CLK pad | 0 or 1 | Input pad | For manufacturing test clock bypass |

**Minimum physical pad count: 8 (4 signal + 4 corner cells)**

> [!IMPORTANT]
> The above pad counts are based on inspecting the PDK LEF files (`io_c1d.lef`, `corner_c1d.lef`, `tech_c1d.lef`). Actual pad names and exact dimensions must be read from `scl1u_pads_typ.lib` and `io_c1d.lef`. Do not invent pad names or dimensions.

---

## 3. Available Die Frame Sizes

From the PadFrame_C1D directory, the following pre-defined die frames are available:

| Frame name | Die size |
|---|---|
| frame1mmx1mm | 1 mm × 1 mm |
| frame2mmx2mm | 2 mm × 2 mm |
| frame3mmx3mm | 3 mm × 3 mm |
| frame4mmx4mm | 4 mm × 4 mm |
| frame5mmx5mm | 5 mm × 5 mm |

**Recommendation:** Select the smallest frame that contains the digital core. Given the small gate count (estimated < 500 standard cells), the 1 mm × 1 mm frame is the first candidate. Confirm after place-and-route area report.

---

## 4. Power Supply Requirements

| Parameter | Value | Source |
|---|---|---|
| Nominal VDD | 5 V | Liberty file `nom_voltage` |
| Operating voltage range | TBD (inspect Liberty min/max corners) | c1d_core_max/min.lib |
| Maximum supply current | TBD (SPICE simulation required) | Risk: RISK-015 |
| Recommended decoupling | 100 nF ceramic, close to VDD pad | Standard practice |

> [!CAUTION]
> The actual supply voltage range and current specifications must be taken from the PDK documentation. The Liberty `nom_voltage = 5` statement confirms 5 V nominal but does not define the operating range. The `Reference Document for SCL's Analog Open Source PDK (1_2um CMOS Process).pdf` must be consulted for device operating ranges.

---

## 5. Button Interface

### Electrical Requirements

| Parameter | Value | Notes |
|---|---|---|
| Button logic | Active-low | 0 = pressed, 1 = released |
| Pull-up resistor | External, 10 kΩ (recommended) | On PCB |
| ESD protection | On-chip (I/O pad) | Pad provides ESD clamp |
| Debounce | On-chip (counter, 10 ms proposed) | See ADL-008 |
| Synchroniser | On-chip (2 FF) | Prevents metastability |
| Maximum contact resistance | TBD | Must be << pull-up R × V_IL threshold |

### Button Circuit

```
VDD (5V)
  │
[10 kΩ]  ← External pull-up resistor (on PCB)
  │
  ├──── BUTTON pad (ASIC input, with ESD)
  │
[SW1]    ← Momentary push button (SPDT or SPST-NO)
  │
VSS
```

---

## 6. Sound Output Interface

### 6.1 Piezoelectric Buzzer

A piezoelectric transducer presents a high-impedance capacitive load (typically 10 nF–100 nF, impedance > 1 kΩ at audio frequencies).

**Direct drive possibility:** A standard CMOS output pad driving 5 V into a piezo is possible if the pad can source/sink sufficient current. For a 100 nF load at 1,200 Hz: peak current ≈ C × V × f = 100 nF × 5 V × 1,200 Hz = 0.6 mA. This may be within a standard logic pad's drive capability, but **must be confirmed from the PDK I/O spec**.

```
SOUND_OUT pad ────────── [Piezo transducer] ────── VSS
                (optional 100R series resistor for protection)
```

### 6.2 Magnetic Buzzer / Speaker

A magnetic buzzer presents a low-impedance inductive load (typically 8–32 Ω). At 5 V / 8 Ω = 625 mA. This is far beyond any standard logic pad drive capability. **An external driver is mandatory.**

#### Recommended External NPN Driver

```
                       VDD (5V)
                         │
                      [Buzzer / Speaker]
                         │
                    [Collector]
SOUND_OUT pad ──[1kΩ]──[Base]  NPN transistor (e.g. 2N2222 / BC547)
                    [Emitter]
                         │
                        VSS
```

> [!WARNING]
> Never connect the SOUND_OUT pad directly to a low-impedance speaker or magnetic buzzer. Excess current will destroy the I/O pad.

### 6.3 Decision Required

The output driver selection (Option A: direct piezo vs. Option B: transistor + magnetic buzzer) affects the PCB BOM. **Owner confirmation required.**

---

## 7. Conceptual PCB Interface Diagram

```
┌─────────────────────────────────────────────────────┐
│                   PCB                               │
│                                                     │
│  VDD ──┬── [100nF] ── GND                          │
│        │                                           │
│        └── VDD_PAD ──────────────────────────────┐ │
│                                                  │ │
│  GND ────── VSS_PAD ─────────────────────────────┤ │
│                                                  │ │
│        ┌── [10kΩ to VDD]                         │ │
│  SW1 ──┴── BUTTON_PAD ──────────────────────────┤ │
│                                                  │ │
│        SOUND_OUT_PAD ──────────────────────────  │ │
│              │                         │          │ │
│          [Option A]                [Option B]     │ │
│         [Piezo direct]       [1kΩ]──Base(NPN)     │ │
│              │                  Collector──[BUZ]──VDD│
│             GND               Emitter──GND         │ │
│                                                  │ │
│                    ┌─────────────────────────────┘ │
│                    │     TOYSOUND-01 ASIC (COB)    │
│                    │                               │
│                    └───────────────────────────────│
└─────────────────────────────────────────────────────┘
```

**Legend:**
- **Mandatory components:** VDD decoupling capacitor, pull-up resistor for button, VSS connection
- **Mandatory if magnetic buzzer:** NPN transistor driver
- **Optional:** Series resistor on SOUND_OUT (protection)
- **Not shown:** Crystal (not required), external clock (not required), external reset (not required in proposed architecture)

---

## 8. ESD Considerations

All signal pads (BUTTON, SOUND_OUT) must include ESD protection cells as part of the I/O pad ring. The SCL C1D I/O pad library (`io_c1d.lef`, `io_c1d.gds`) provides ESD-protected I/O cells. **Do not use core cells as I/O pads.**

ESD protection level is not yet confirmed from the PDK documentation — it must be read from `Standard_Pad_Frame_C1D.pdf`.

---

## 9. Open Items

| Item | Required action |
|---|---|
| I/O pad drive strength | Read from `scl1u_pads_typ.lib` |
| I/O pad DC output current specification | Read from PDK I/O documentation |
| ESD HBM rating | Read from `Standard_Pad_Frame_C1D.pdf` |
| Buzzer type decision (piezo vs magnetic) | Owner confirmation required |
| External reset pin decision | Linked to POR validation (ADL-006, RISK-017) |
| Operating voltage range | Read from Liberty min/max corners and analog PDK reference doc |

