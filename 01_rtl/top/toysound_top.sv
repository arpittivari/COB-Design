// =============================================================================
// toysound_top.sv
// TOYSOUND-01 — Top-level integration
//
// Process : SCL 1.2 µm CMOS (C1D)
// Revision: B
// Date    : 2026-10-02
//
// Hierarchy:
//   toysound_top
//     ├── button_debounce      (rtl/peripherals/)
//     ├── sound_controller     (rtl/core/)
//     ├── sound_sequencer      (rtl/core/)
//     └── tone_generator       (rtl/core/)
//
// Interface:
//   clk       — system clock (external; 1 MHz nominal)
//   reset_n   — active-low asynchronous reset
//   button    — 1 raw button input, active-low, mechanical ("Next" button)
//   sound_out — digital square-wave output to driver/speaker
//   busy      — high while sound playing
// =============================================================================

`default_nettype none

import toysound_pkg::*;

module toysound_top (
  input  wire       clk,
  input  wire       reset_n,
  input  wire       button,      // raw button input, active-low
  output wire       sound_out,   // digital audio output
  output wire       busy         // high during playback
);

  // -------------------------------------------------------------------------
  // Internal wires
  // -------------------------------------------------------------------------
  wire                btn_event;    // debounced single-cycle event

  wire [1:0]          sound_sel;    // controller → sequencer
  wire                play_en;      // controller → sequencer (start)
  wire                seq_done;     // sequencer → controller

  wire [DIV_WIDTH-1:0] tone_div;   // sequencer → tone generator
  wire                 tone_en;     // sequencer → tone generator

  // -------------------------------------------------------------------------
  // Button debounce instance (Single Button)
  // -------------------------------------------------------------------------
  button_debounce #(
    .DEBOUNCE_CYCLES(DEBOUNCE_CYCLES)
  ) u_debounce (
    .clk      (clk),
    .reset_n  (reset_n),
    .btn_raw  (button),
    .btn_event(btn_event)
  );

  // -------------------------------------------------------------------------
  // Sound controller
  // -------------------------------------------------------------------------
  sound_controller u_ctrl (
    .clk       (clk),
    .reset_n   (reset_n),
    .btn_event (btn_event),
    .sound_sel (sound_sel),
    .play_en   (play_en),
    .seq_done  (seq_done),
    .busy      (busy)
  );

  // -------------------------------------------------------------------------
  // Sound sequencer
  // -------------------------------------------------------------------------
  sound_sequencer u_seq (
    .clk      (clk),
    .reset_n  (reset_n),
    .start    (play_en),
    .sound_sel(sound_sel),
    .tone_div (tone_div),
    .tone_en  (tone_en),
    .done     (seq_done)
  );

  // -------------------------------------------------------------------------
  // Tone generator
  // -------------------------------------------------------------------------
  tone_generator #(
    .DIV_WIDTH(DIV_WIDTH)
  ) u_tone (
    .clk      (clk),
    .reset_n  (reset_n),
    .divider  (tone_div),
    .enable   (tone_en),
    .tone_out (sound_out)
  );

endmodule : toysound_top

`default_nettype wire
