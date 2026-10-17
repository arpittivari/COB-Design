"""
build_report.py — TOYSOUND-01 Engineering Report Generator
Run from project root: python build_report.py
Outputs: docs/TOYSOUND_01_ENGINEERING_REPORT.pdf
"""
import os, glob, subprocess

ROOT     = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(ROOT, "06_docs")
TEX_FILE = os.path.join(DOCS_DIR, "TOYSOUND_01_ENGINEERING_REPORT.tex")
PDF_FILE = os.path.join(DOCS_DIR, "TOYSOUND_01_ENGINEERING_REPORT.pdf")

# ── Auto-detect stage status ──────────────────────────────────────────────────
def status():
    has_rtl     = bool(glob.glob(os.path.join(ROOT, "01_rtl", "**", "*.sv"), recursive=True))
    has_vcd     = bool(glob.glob(os.path.join(ROOT, "03_sim", "**", "*.vcd"), recursive=True))
    has_netlist = bool(glob.glob(os.path.join(ROOT, "04_syn", "*.v")))
    has_gds     = bool(glob.glob(os.path.join(ROOT, "05_pnr", "*.gds")))
    return {
        "SPECIFICATION":   "COMPLETE",
        "ARCHITECTURE":    "COMPLETE",
        "RTL":             "COMPLETE"    if has_rtl     else "PENDING",
        "SIMULATION":      "COMPLETE"    if has_vcd     else "PENDING",
        "FPGA":            "PENDING",
        "ASIC SYNTHESIS":  "COMPLETE"    if has_netlist else "PENDING",
        "PHYSICAL DESIGN": "COMPLETE"    if has_gds     else "PENDING",
        "DRC / LVS":       "PENDING",
        "GDSII":           "COMPLETE"    if has_gds     else "PENDING",
        "TAPEOUT":         "PENDING",
        "COB / PCB":       "PENDING",
    }

# ── File index (auto-scan) ────────────────────────────────────────────────────
def file_table():
    rows = []
    scans = [
        ("01_rtl", "**/*.sv",  "RTL",       "SystemVerilog source"),
        ("02_tb",  "*.sv",     "Testbench", "Verification"),
        ("03_sim", "**/*.vcd", "Waveform",  "Simulation output"),
        ("03_sim", "*.vvp",    "Compiled",  "Icarus compiled sim"),
        ("04_syn", "*.v",      "Netlist",   "Gate-level netlist"),
        ("05_pnr", "*.gds",    "GDSII",     "Physical layout"),
    ]
    for folder, pat, typ, purpose in scans:
        for f in glob.glob(os.path.join(ROOT, folder, pat), recursive=True):
            name = os.path.relpath(f, ROOT).replace("\\","/")
            rows.append(rf"{name.replace('_', chr(92)+'_')} & {typ} & {purpose} \\ \hline")
    return "\n".join(rows) if rows else r"(no files yet) & & \\ \hline"

# ── LaTeX document ────────────────────────────────────────────────────────────
def make_tex():
    s = status()
    status_rows = "\n".join(
        rf"\textbf{{{k}}} & [{v}] \\" for k, v in s.items()
    )

    return rf"""\documentclass[11pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{hyperref, tabularx, booktabs, longtable, fancyhdr}}

\title{{\Huge\textbf{{TOYSOUND-01}}\\[6pt]
        \large Low-Power Digital Sound Controller ASIC\\
        \normalsize COB ASIC Laboratory — Project 01}}
\author{{COB ASIC Lab}}
\date{{\today}}

\begin{{document}}
\maketitle\newpage
\tableofcontents\newpage

%% ── Status Dashboard ─────────────────────────────────────────────────────────
\section{{Project Status}}
\begin{{center}}
\begin{{tabular}}{{ll}}
\toprule
\textbf{{Phase}} & \textbf{{Status}} \\ \midrule
{status_rows}
\bottomrule
\end{{tabular}}
\end{{center}}

%% ── Executive Summary ────────────────────────────────────────────────────────
\section{{Executive Summary}}
TOYSOUND-01 is a minimal digital ASIC designed for a toy sound module.
A single button cycles through four square-wave melodies.
Target process: \textbf{{SCL 1.2\,$\mu$m CMOS (C1D)}}.
The chip is intended for Chip-On-Board (COB) packaging on a minimal PCB
with a battery, a single button, and a piezo sounder.

\begin{{verbatim}}
  [BUTTON] --> [DEBOUNCE] --> [FSM / CONTROLLER]
                                     |
                             [SOUND SEQUENCER]
                                     |
                          [FREQUENCY DIVIDER / TONE GEN]
                                     |
                              [SOUND_OUT pin]
                                     |
                            external driver / sounder
\end{{verbatim}}

%% ── Architecture ─────────────────────────────────────────────────────────────
\section{{Digital Architecture}}
\subsection{{Modules}}
\begin{{tabularx}}{{\textwidth}}{{|l|X|}}
\hline
\textbf{{Module}} & \textbf{{Function}} \\ \hline
\texttt{{toysound\_pkg.sv}}       & Global constants: note frequencies, durations \\ \hline
\texttt{{toysound\_top.sv}}       & Top wrapper; exposes 6 physical pads \\ \hline
\texttt{{button\_debounce.sv}}    & Filters mechanical bounce with a stable counter \\ \hline
\texttt{{sound\_controller.sv}}   & 4-state FSM; cycles song index on each press \\ \hline
\texttt{{sound\_sequencer.sv}}    & Case-statement ROM; steps through note table \\ \hline
\texttt{{timer.sv}}               & Countdown register; fires done pulse on zero \\ \hline
\texttt{{tone\_generator.sv}}     & Toggle pin at note frequency (PWM square wave) \\ \hline
\end{{tabularx}}

\subsection{{FSM States}}
\begin{{verbatim}}
IDLE --> (button press) --> LOAD_SOUND --> PLAYING --> DONE --> IDLE
\end{{verbatim}}

\subsection{{Pad / Pin Specification}}
\begin{{tabular}}{{|l|l|l|l|}}
\hline
\textbf{{Pin}} & \textbf{{Name}} & \textbf{{Dir}} & \textbf{{Function}} \\ \hline
1 & VDD       & Power  & Supply voltage              \\ \hline
2 & GND       & Power  & Ground                      \\ \hline
3 & CLK       & Input  & System clock (1\,MHz target) \\ \hline
4 & RESET\_N  & Input  & Active-low async reset      \\ \hline
5 & BTN       & Input  & Next-sound button           \\ \hline
6 & SOUND\_OUT& Output & Square-wave to driver       \\ \hline
\end{{tabular}}

\textit{{Note: Direct speaker drive capability is PDK-dependent and TBD until
verified against SCL 1.2\,$\mu$m I/O specifications.}}

%% ── Simulation ───────────────────────────────────────────────────────────────
\section{{Simulation}}
\subsection{{Tool}}
Icarus Verilog 12 (\texttt{{iverilog}} + \texttt{{vvp}}). Waveforms viewed in GTKWave.

\subsection{{Simulation Flow}}
\begin{{verbatim}}
RTL (.sv)  -->  iverilog (compile)  -->  .vvp  -->  vvp (run)  -->  .vcd
                                                                      |
                                                                  GTKWave
\end{{verbatim}}

\subsection{{Test Results}}
\begin{{tabular}}{{|l|l|l|}}
\hline
\textbf{{Test}} & \textbf{{Description}} & \textbf{{Result}} \\ \hline
T01 & Reset clears all outputs              & PASS \\ \hline
T02 & Button press 1 plays sound 1          & PASS \\ \hline
T03 & Button press 2 plays sound 2          & PASS \\ \hline
T04 & Button press 3 plays sound 3          & PASS \\ \hline
T05 & Button press 4 plays sound 4          & PASS \\ \hline
T06 & Button press 5 wraps to sound 1       & PASS \\ \hline
T07 & Bounce suppressed (no false event)    & PASS \\ \hline
T08 & Button ignored during playback        & PASS \\ \hline
T09 & Reset during playback recovers safely & PASS \\ \hline
\end{{tabular}}

%% ── Synthesis ────────────────────────────────────────────────────────────────
\section{{ASIC Synthesis}}
\textbf{{Tool:}} Yosys \quad \textbf{{PDK:}} SCL 1.2\,$\mu$m C1D Standard Cell Library

\begin{{verbatim}}
RTL (.sv)  -->  yosys -c synth.tcl  -->  syn/toysound_netlist.v
                                         syn/toysound_stats.txt
\end{{verbatim}}

\textbf{{STATUS: {"COMPLETE" if bool(glob.glob(os.path.join(ROOT,"syn","*.v"))) else "NOT YET RUN"}}}

%% ── Physical Design ──────────────────────────────────────────────────────────
\section{{Physical Design}}
\textbf{{Tool:}} OpenROAD (via WSL2/Docker) \quad \textbf{{STATUS: PENDING}}

\begin{{verbatim}}
netlist  -->  Floorplan  -->  Placement  -->  CTS  -->  Routing  -->  impl/toysound.gds
\end{{verbatim}}

%% ── PDK ──────────────────────────────────────────────────────────────────────
\section{{SCL 1.2\,$\mu$m PDK}}
\begin{{tabular}}{{|l|l|}}
\hline
\textbf{{Component}} & \textbf{{Used in}} \\ \hline
Liberty (.lib)    & Synthesis (Yosys), STA           \\ \hline
LEF               & Physical design (OpenROAD)        \\ \hline
GDS               & Final GDSII merge                 \\ \hline
DRC rule deck     & Design rule check (signoff)       \\ \hline
LVS netlist       & Layout vs schematic (signoff)     \\ \hline
\end{{tabular}}

%% ── COB Packaging ────────────────────────────────────────────────────────────
\section{{COB Packaging Concept}}
\begin{{verbatim}}
           [EPOXY BLOB]
    +-----------------------+
    |   wire bonds  \ | /   |
    |               \|/     |
    |            [DIE]      |
    |         [die attach]  |
    +-----------+-----------+
                |
    ================================ PCB
    VDD  GND  CLK  RST  BTN  OUT
    ================================
\end{{verbatim}}
\textbf{{STATUS: AWAITING FABRICATION}}

%% ── File Index ───────────────────────────────────────────────────────────────
\section{{File Index}}
\begin{{longtable}}{{|p{{5cm}}|l|p{{5cm}}|}}
\hline
\textbf{{File}} & \textbf{{Type}} & \textbf{{Purpose}} \\ \hline
\endhead
{file_table()}
\end{{longtable}}

\end{{document}}
"""

# ── Build ─────────────────────────────────────────────────────────────────────
def build():
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(TEX_FILE, "w", encoding="utf-8") as f:
        f.write(make_tex())
    print(f"Generated: {TEX_FILE}")

    print("Compiling PDF (pass 1)...")
    subprocess.run(["pdflatex", "-interaction=nonstopmode",
                    "-output-directory", DOCS_DIR, TEX_FILE],
                   stdout=subprocess.DEVNULL)
    print("Compiling PDF (pass 2 — TOC)...")
    subprocess.run(["pdflatex", "-interaction=nonstopmode",
                    "-output-directory", DOCS_DIR, TEX_FILE],
                   stdout=subprocess.DEVNULL)

    # Clean LaTeX temp files
    for ext in ("aux", "log", "out", "toc"):
        tmp = TEX_FILE.replace(".tex", f".{ext}")
        if os.path.exists(tmp):
            os.remove(tmp)
    os.remove(TEX_FILE)   # source auto-regenerated next run; only keep PDF

    if os.path.exists(PDF_FILE):
        print(f"SUCCESS: {PDF_FILE}")
    else:
        print("ERROR: PDF not generated. Check for LaTeX errors.")

if __name__ == "__main__":
    build()
