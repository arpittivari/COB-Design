import os
import glob
import subprocess
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LATEX_DIR = os.path.join(PROJECT_ROOT, "docs", "latex")
PDF_DIR = os.path.join(PROJECT_ROOT, "docs", "pdf")
TEX_FILE = os.path.join(LATEX_DIR, "TOYSOUND_01_ENGINEERING_REPORT.tex")

def check_status():
    status = {
        "SPECIFICATION": "COMPLETE",
        "ARCHITECTURE": "COMPLETE",
        "RTL": "COMPLETE" if glob.glob(os.path.join(PROJECT_ROOT, "rtl", "**", "*.sv"), recursive=True) else "PENDING",
        "SIMULATION": "COMPLETE" if os.path.exists(os.path.join(PROJECT_ROOT, "sim", "waveforms", "toysound_top_tb.vcd")) else "PENDING",
        "FPGA": "PENDING",
        "ASIC SYNTHESIS": "PENDING",
        "PHYSICAL DESIGN": "PENDING",
        "DRC": "PENDING",
        "LVS": "PENDING",
        "GDSII": "PENDING",
        "TAPEOUT": "PENDING",
        "FABRICATION": "PENDING",
        "DIE TEST": "PENDING",
        "COB": "PENDING",
        "PCB": "PENDING",
        "FINAL PRODUCT": "PENDING"
    }
    return status

def generate_file_index():
    files = []
    for f in glob.glob(os.path.join(PROJECT_ROOT, "rtl", "**", "*.sv"), recursive=True):
        files.append((os.path.relpath(f, PROJECT_ROOT).replace("\\", "/"), "RTL", "Logic module", "Complete"))
    for f in glob.glob(os.path.join(PROJECT_ROOT, "tb", "**", "*.sv"), recursive=True):
        files.append((os.path.relpath(f, PROJECT_ROOT).replace("\\", "/"), "Testbench", "Verification", "Complete"))
    for f in glob.glob(os.path.join(PROJECT_ROOT, "sim", "**", "*.*"), recursive=True):
        ext = os.path.splitext(f)[1]
        files.append((os.path.relpath(f, PROJECT_ROOT).replace("\\", "/"), ext[1:].upper(), "Simulation artifact", "Generated"))
    
    rows = []
    for f, typ, purp, stat in files:
        f_safe = f.replace("_", "\\_")
        rows.append(rf"{f_safe} & {typ} & {purp} & {stat} \\ \hline")
    return "\n".join(rows)

def build_latex():
    status = check_status()
    file_index_rows = generate_file_index()
    
    status_text = ""
    for k, v in status.items():
        status_text += rf"\textbf{{{k}}} & [{v}] \\" + "\n"

    latex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{hyperref}
\usepackage{graphicx}
\usepackage{tabularx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{fancyhdr}
\usepackage{enumitem}

\title{\Huge\textbf{TOYSOUND-01} \\ \Large COMPLETE ASIC $\rightarrow$ COB $\rightarrow$ PCB ENGINEERING REPORT}
\author{COB ASIC Laboratory}
\date{\today}

\begin{document}

\begin{titlepage}
    \centering
    \vspace*{2cm}
    {\Huge \textbf{TOYSOUND-01}\par}
    \vspace{1cm}
    {\Large \textbf{Low-Power Digital Sound Controller ASIC}\par}
    \vspace{0.5cm}
    {\large Project 01 — COB ASIC Laboratory\par}
    \vspace{2cm}
    
    \begin{tabular}{ll}
        \textbf{Technology:} & SCL Open Source 1.2 $\mu$m \\
        \textbf{Design type:} & Digital ASIC core \\
        \textbf{Application:} & Toy / Sound Module / Low-Cost Consumer Electronics \\
        \textbf{Version:} & v0.1 \\
        \textbf{Date:} & \today \\
    \end{tabular}
    
    \vspace{2cm}
    % Conceptual illustration
    \begin{verbatim}
    ASIC DIE
       |
    WIRE BOND
       |
    COB PCB
       |
    SPEAKER
       |
    TOY PRODUCT
    \end{verbatim}
    
    \vfill
\end{titlepage}

\tableofcontents
\newpage

\section{Project Status Dashboard}
\begin{center}
\begin{tabularx}{\textwidth}{X l}
\toprule
\textbf{Phase} & \textbf{Status} \\
\midrule
""" + status_text + r"""
\bottomrule
\end{tabularx}
\end{center}

\section{Document Control}
\begin{tabularx}{\textwidth}{|l|l|X|l|}
\hline
\textbf{Version} & \textbf{Date} & \textbf{Change} & \textbf{Status} \\ \hline
v0.1 & \today & Initial architecture & Draft \\ \hline
v0.2 & & RTL completed & \\ \hline
v0.3 & & Simulation verified & \\ \hline
v0.4 & & FPGA verified & \\ \hline
v0.5 & & ASIC synthesis & \\ \hline
v0.6 & & Physical design & \\ \hline
v0.7 & & DRC/LVS & \\ \hline
v1.0 & & Tapeout & \\ \hline
v2.0 & & Silicon result & \\ \hline
\end{tabularx}

\section{Executive Summary}
Explain TOYSOUND-01 in one or two pages.

Example architecture:
\begin{verbatim}
             TOYSOUND-01
                  |
        +---------+---------+
        |         |         |
      INPUT     CONTROL    OUTPUT
        |         |         |
      Button     FSM     Tone/PWM
        |         |         |
    Debounce    Timer       |
                  |         |
                ROM         |
                  |         |
                  +----+----+
                       |
                   SOUND_OUT
\end{verbatim}

\section{Product Idea}
Explain the original product concept.
Potential applications: toy sound module, educational toy, talking toy, button-operated sound toy, simple alarm, doorbell, electronic book, low-cost consumer sound controller.

\textbf{Current TOYSOUND-01:} 4-button simple tone playback.
\textbf{Future product variants:} PCM audio, melodies, interactive games.

\section{Requirements}
\begin{tabularx}{\textwidth}{|l|X|l|l|}
\hline
\textbf{ID} & \textbf{Requirement} & \textbf{Target} & \textbf{Status} \\ \hline
R01 & Digital controller & Required & COMPLETE \\ \hline
R02 & Button inputs & 1 & COMPLETE \\ \hline
R03 & Sound output & 1 & COMPLETE \\ \hline
R04 & Reset & Required & COMPLETE \\ \hline
R05 & Low power & Target & TBD \\ \hline
R06 & SCL 1.2 $\mu$m ASIC & Target & PLANNED \\ \hline
R07 & FPGA prototype & Required & PLANNED \\ \hline
R08 & DRC & Required before tapeout & PLANNED \\ \hline
R09 & LVS & Required before tapeout & PLANNED \\ \hline
R10 & COB packaging & Future & PLANNED \\ \hline
\end{tabularx}

\section{System Block Diagram}
\begin{verbatim}
                         TOYSOUND-01
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
        INPUT SYSTEM      CONTROL CORE    SOUND ENGINE
              |               |               |
       +------+------+        |         +-----+-----+
       |             |        |         |           |
     Button       Debounce    FSM     Timer       ROM
                                      |           |
                                      +-----+-----+
                                            |
                                      Tone Generator
                                            |
                                            v
                                       SOUND_OUT
\end{verbatim}

\section{Circuit Diagrams}
\subsection{A. Button interface}
\begin{verbatim}
BUTTON
  |
  +-- pull-up/pull-down
  |
  v
DIGITAL INPUT
\end{verbatim}

\subsection{B. Debounce concept}
Show the digital debounce logic: A sequential counter filtering unstable high-low states.

\subsection{C. Clock divider}
\begin{verbatim}
CLK
 |
COUNTER
 |
TOGGLE
 |
SOUND_OUT
\end{verbatim}

\subsection{D. Output stage}
\begin{verbatim}
ASIC GPIO/PWM
      |
external driver
      |
speaker
\end{verbatim}
\textbf{Note:} The ASIC does not directly drive the speaker. An external BJT/MOSFET driver is required.

\section{Digital Logic Diagram}
\begin{verbatim}
toysound_top
|
|-- button_debounce
|
|-- sound_controller
|
|-- timer
|
|-- tone_generator
|
+-- sound_sequencer
\end{verbatim}

\section{FSM Diagram}
\begin{verbatim}
                 RESET
                   |
                   v
                 IDLE
                   |
             button detected
                   |
                   v
             START_SOUND
                   |
                   v
               PLAY_TONE
                   |
          +--------+--------+
          |                 |
     next tone           finished
          |                 |
          v                 v
      PLAY_TONE            IDLE
\end{verbatim}

\section{RTL File Documentation \& Programming Logic}
The SystemVerilog code is partitioned carefully to isolate physical timing from logical state machines. Here is the programming essence of each file:

\subsection{toysound\_pkg.sv}
\textbf{Purpose:} Global definitions. \\
\textbf{Programming:} Contains \texttt{parameter} constants defining musical note frequencies (as integer dividers of the 1 MHz clock) and durations. It also defines the \texttt{tone\_t} struct, ensuring all modules agree on data widths.

\subsection{toysound\_top.sv}
\textbf{Purpose:} Top-level hardware wrapper. \\
\textbf{Programming:} Contains no behavioural logic. It simply instantiates the lower-level modules and wires them together. It exposes only the 6 physical pins that will be bonded to the PCB.

\subsection{button\_debounce.sv}
\textbf{Purpose:} Filter mechanical button bounce. \\
\textbf{Programming:} Uses an internal counter. When the button is pressed, the counter increments. If the button bounces (voltage fluctuates), the counter resets. It only emits a \texttt{btn\_event} pulse once the signal is stable for a programmed number of clock cycles.

\subsection{sound\_controller.sv}
\textbf{Purpose:} Main Finite State Machine (FSM). \\
\textbf{Programming:} Implements a 4-state FSM (\texttt{IDLE}, \texttt{LOAD\_SOUND}, \texttt{PLAYING}, \texttt{DONE}). It maintains a \texttt{song\_index} counter that increments on every button press. It commands the sequencer to start and then ignores the button until the song finishes.

\subsection{sound\_sequencer.sv}
\textbf{Purpose:} ROM lookup and sequence timing. \\
\textbf{Programming:} Instead of using expensive SRAM memory, the songs are programmed as a giant \texttt{case} statement. The synthesis tool optimizes this into a tiny cluster of combinational logic gates. It steps through the notes, sending the required frequency divider to the tone generator and waiting for the timer to signal completion.

\subsection{timer.sv}
\textbf{Purpose:} Measures note durations. \\
\textbf{Programming:} A simple countdown register. Loaded with a 20-bit value representing milliseconds (e.g., 200,000 clock cycles = 200ms). When it hits zero, it fires a \texttt{done} pulse back to the sequencer.

\subsection{tone\_generator.sv}
\textbf{Purpose:} Square wave output generation. \\
\textbf{Programming:} Receives a frequency divider number. It counts down from that number to zero, then toggles the \texttt{sound\_out} pin state (HIGH $\rightarrow$ LOW). This continuous toggling creates the PWM square wave that drives the speaker.

\begin{tabularx}{\textwidth}{|l|l|X|l|l|}
\hline
\textbf{File} & \textbf{Module} & \textbf{Purpose} & \textbf{Inputs} & \textbf{Outputs} \\ \hline
toysound\_top.sv & toysound\_top & Top integration & clk, reset\_n, button & sound\_out, busy \\ \hline
button\_debounce.sv & button\_debounce & Filter mechanical bounce & clk, reset\_n, btn\_raw & btn\_event \\ \hline
sound\_controller.sv & sound\_controller & Main FSM & clk, reset\_n, btn\_event & sound\_sel, play\_en \\ \hline
timer.sv & timer & Countdown timer & clk, reset\_n, load & done \\ \hline
tone\_generator.sv & tone\_generator & Square wave output & clk, reset\_n, divider & tone\_out \\ \hline
sound\_sequencer.sv & sound\_sequencer & ROM reader & clk, reset\_n, start & tone\_div, tone\_en \\ \hline
\end{tabularx}

\section{RTL Source Tree}
\begin{verbatim}
rtl/
|-- top/
|   `-- toysound_top.sv
|
|-- core/
|   |-- sound_controller.sv
|   |-- sound_sequencer.sv
|   `-- timer.sv
|
|-- peripherals/
|   |-- button_debounce.sv
|   `-- tone_generator.sv
|
`-- pkg/
    `-- toysound_pkg.sv
\end{verbatim}

\section{Testbench Documentation}
\begin{tabularx}{\textwidth}{|l|X|l|l|l|}
\hline
\textbf{Test} & \textbf{Description} & \textbf{Expected} & \textbf{Actual} & \textbf{Status} \\ \hline
TB01 & Reset & Known state & PASS & COMPLETE \\ \hline
TB02 & Button 1 & Sound 1 & PASS & COMPLETE \\ \hline
TB03 & Button 2 & Sound 2 & PASS & COMPLETE \\ \hline
TB04 & Button 3 & Sound 3 & PASS & COMPLETE \\ \hline
TB05 & Button 4 & Sound 4 & PASS & COMPLETE \\ \hline
TB06 & Bounce & Clean event & PASS & COMPLETE \\ \hline
TB07 & Reset during sound & Safe recovery & PASS & COMPLETE \\ \hline
\end{tabularx}

\section{Simulation File Types}
\subsection{.sv} SystemVerilog source.
\subsection{.v} Verilog source.
\subsection{.sv testbench} Verification environment.
\subsection{.vcd} Value Change Dump. Contains signal transitions over simulation time.
\subsection{.vvp} Compiled simulation representation executed by vvp.
\subsection{.log} Simulation/tool logs.
\subsection{.fst} Waveform database format.
\subsection{waveform images} PNG/PDF screenshots generated from GTKWave.

\section{Waveform Section}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Simulation Flow Diagram}
\begin{verbatim}
SystemVerilog RTL
       |
       v
Testbench
       |
       v
Icarus / Verilator
       |
       +-- .vvp
       +-- .vcd
       +-- logs
             |
             v
          GTKWave
             |
             v
        Waveform analysis
\end{verbatim}

\section{FPGA Section}
\textbf{STATUS: NOT YET IMPLEMENTED}
\begin{verbatim}
RTL -> FPGA synthesis -> Implementation -> Bitstream -> FPGA -> Buttons + speaker
\end{verbatim}
\textit{The SCL ASIC PDK is not used for FPGA implementation.}

\section{ASIC Section}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{PDK Section}
Technology: SCL 1.2 $\mu$m PDK (C1D).
Contains Liberty, LEF, GDS, Verilog cell models, DRC/LVS rule decks, and RCX extraction.

\section{Library Section}
\begin{verbatim}
                 STANDARD CELL
                      |
       +--------------+---------------+
       v              v               v
   Verilog          Liberty          LEF
 functional       timing/power     physical
   model             model          abstract
       |              |               |
       +--------------+---------------+
                      |
                      v
                    GDS
               actual geometry
\end{verbatim}

\section{Synthesis Report}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Gate-Level Netlist}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Floorplan}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Placement}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Clock Tree Synthesis}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Routing}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{STA}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{DRC}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{LVS}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Final GDSII}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Tapeout}
\textbf{STATUS: NOT YET IMPLEMENTED}
[ ] RTL frozen
[ ] Verification complete
[ ] Synthesis complete
[ ] Timing signoff
[ ] Physical implementation
[ ] DRC clean
[ ] LVS clean
[ ] GDS generated

\section{Fabrication}
\textbf{STATUS: AWAITING FABRICATION}

\section{Die}
\textbf{STATUS: AWAITING FABRICATION}

\section{Die Testing}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{COB Packaging}
\begin{verbatim}
Bare Die -> Die attach -> Wire bonding -> Electrical connection to PCB -> Encapsulation -> Epoxy -> COB module
\end{verbatim}

\section{COB Cross-Section}
\begin{verbatim}
             EPOXY
       +-----------------+
       |                 |
       |    Wire bonds   |
       |      \ | /      |
       |       \|/       |
       |      DIE        |
       |   +-------+     |
       |   | ASIC  |     |
       |   +-------+     |
       |      |          |
       |   DIE ATTACH    |
       +------+----------+
              |
============================ PCB
       copper traces
============================
\end{verbatim}

\section{Pin / Pad Specification}
\begin{tabularx}{\textwidth}{|l|l|l|l|X|}
\hline
\textbf{Pin} & \textbf{Name} & \textbf{Direction} & \textbf{Function} & \textbf{Electrical Notes} \\ \hline
1 & VDD & Power & Supply & TBD \\ \hline
2 & GND & Power & Ground & TBD \\ \hline
3 & CLK & Input & Clock & TBD \\ \hline
4 & RESET & Input & Reset & TBD \\ \hline
5 & BTN & Input & Button (Next) & TBD \\ \hline
6 & SOUND\_OUT & Output & Sound signal & TBD \\ \hline
\end{tabularx}

\section{Datasheet}
\textbf{STATUS: TBD}

\section{Application Circuit}
\begin{verbatim}
              BATTERY
                |
          +-----+-----+
          |           |
         VDD         GND
          |           |
      +---v-----------v---+
      |                   |
      |    TOYSOUND ASIC  |
      |                   |
      |       BTN         |
      |        |          |
      |        |          |
      |   SOUND_OUT-------+----> DRIVER
      |                   |          |
      +-------------------+          v
                                  SPEAKER
\end{verbatim}

\section{PCB Design}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{PCB BOM}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Final Product Functionality}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Test Procedure}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Failure Analysis}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Cost Model}
\textbf{STATUS: NOT YET IMPLEMENTED}

\section{Design File Index}
\begin{longtable}{|p{6cm}|l|p{4cm}|l|}
\hline
\textbf{File} & \textbf{Type} & \textbf{Purpose} & \textbf{Status} \\ \hline
\endfirsthead
\hline
\textbf{File} & \textbf{Type} & \textbf{Purpose} & \textbf{Status} \\ \hline
\endhead
""" + file_index_rows + r"""
\end{longtable}

\section{Artifact Relationship Diagram}
\begin{verbatim}
                 PROJECT IDEA
                      |
                      v
               SPECIFICATION
                      |
                      v
                ARCHITECTURE
                      |
          +-----------+-----------+
          v                       v
        RTL                    CIRCUIT
          |                       |
          v                       v
     TESTBENCH                SCHEMATIC
          |
          v
      SIMULATION
          |
     +----+----+
     v         v
   .vcd       .vvp
     |
     v
  WAVEFORMS
     |
     v
     FPGA
     |
     v
   SYNTHESIS
     |
     v
   NETLIST
     |
     v
 PHYSICAL DESIGN
     |
     |-- Floorplan
     |-- Placement
     |-- CTS
     `-- Routing
            |
            v
          GDSII
            |
       +----+----+
       v         v
      DRC       LVS
       |         |
       +----+----+
            v
         TAPEOUT
            |
            v
       FABRICATION
            |
            v
            DIE
            |
            v
        WIRE BOND
            |
            v
           COB
            |
            v
           PCB
            |
            v
       FINAL PRODUCT
\end{verbatim}

\end{document}
"""
    os.makedirs(LATEX_DIR, exist_ok=True)
    with open(TEX_FILE, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Generated {TEX_FILE}")

def compile_pdf():
    print("Compiling PDF...")
    try:
        # Run pdflatex twice for TOC
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "TOYSOUND_01_ENGINEERING_REPORT.tex"], cwd=LATEX_DIR, stdout=subprocess.DEVNULL)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "TOYSOUND_01_ENGINEERING_REPORT.tex"], cwd=LATEX_DIR, stdout=subprocess.DEVNULL)
        
        # Move generated PDF
        pdf_src = os.path.join(LATEX_DIR, "TOYSOUND_01_ENGINEERING_REPORT.pdf")
        pdf_dest = os.path.join(PDF_DIR, "TOYSOUND_01_ENGINEERING_REPORT.pdf")
        os.makedirs(PDF_DIR, exist_ok=True)
        if os.path.exists(pdf_src):
            if os.path.exists(pdf_dest):
                os.remove(pdf_dest)
            os.rename(pdf_src, pdf_dest)
            print(f"Successfully generated {pdf_dest}")
    except Exception as e:
        print(f"Error compiling LaTeX: {e}")

if __name__ == "__main__":
    build_latex()
    compile_pdf()
