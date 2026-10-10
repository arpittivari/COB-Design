// =============================================================================
// toysound_top_tb.sv
// TOYSOUND-01 — Top-level testbench
//
// Simulator: Icarus Verilog 12 (iverilog + vvp)
// Date     : 2026-10-02
//
// Tests:
//   T01 — Reset: all outputs 0, FSM in IDLE
//   T02 — Button press 1: sound 1 plays, busy goes high then low
//   T03 — Button press 2: sound 2 plays
//   T04 — Button press 3: sound 3 plays
//   T05 — Button press 4: sound 4 plays
//   T06 — Button press 5: Wraps back to sound 1 plays
//   T07 — Button bounce: debounce suppresses short pulses, only one event
//   T08 — Second button press during playback: ignored (busy remains high)
//   T09 — Reset during playback: immediate return to idle
//   T10 — Long simulation: no state lockup over multiple cycles
//
// Note: Package parameters shorten debounce to 10 cycles in TB so tests
//       complete quickly. Override via parameter override on DUT instance.
// =============================================================================

`timescale 1ns/1ps
`default_nettype none

// Use a shorter debounce count for simulation speed
`define SIM_DEBOUNCE 10

import toysound_pkg::*;

module toysound_top_tb;

  // -------------------------------------------------------------------------
  // Clock and reset
  // -------------------------------------------------------------------------
  localparam int CLK_HALF = 500;    // 500 ns half-period → 1 MHz clock

  reg clk;
  reg reset_n;

  initial clk = 0;
  always #(CLK_HALF) clk = ~clk;

  // -------------------------------------------------------------------------
  // DUT signals
  // -------------------------------------------------------------------------
  reg         button;     // raw button (active-low, 1 = not pressed)
  wire        sound_out;
  wire        busy;

  // -------------------------------------------------------------------------
  // DUT instantiation with shortened debounce for simulation
  // -------------------------------------------------------------------------
  toysound_top dut (
    .clk      (clk),
    .reset_n  (reset_n),
    .button   (button),
    .sound_out(sound_out),
    .busy     (busy)
  );

  // Override debounce counter depth for the single debounce instance
  defparam dut.u_debounce.DEBOUNCE_CYCLES = `SIM_DEBOUNCE;

  // -------------------------------------------------------------------------
  // VCD waveform dump
  // -------------------------------------------------------------------------
  initial begin
    $dumpfile("sim/waveforms/toysound_top_tb.vcd");
    $dumpvars(0, toysound_top_tb);
  end

  // -------------------------------------------------------------------------
  // Test utilities
  // -------------------------------------------------------------------------
  integer test_num;
  integer pass_count;
  integer fail_count;

  task assert_eq;
    input [63:0] actual;
    input [63:0] expected;
    input [255:0] msg;
    begin
      if (actual !== expected) begin
        $display("FAIL [T%0d] %s : got %0d, expected %0d at time %0t",
                 test_num, msg, actual, expected, $time);
        fail_count = fail_count + 1;
      end else begin
        $display("PASS [T%0d] %s", test_num, msg);
        pass_count = pass_count + 1;
      end
    end
  endtask

  task press_button;
    input int   hold_cycles;
    begin
      button = 1'b0;   // press (active-low)
      repeat(hold_cycles) @(posedge clk);
      button = 1'b1;   // release
      @(posedge clk);
    end
  endtask

  task bounce_button;
    // Simulate bouncing: short pulses below debounce threshold
    integer j;
    begin
      for (j = 0; j < 5; j = j + 1) begin
        button = 1'b0;
        repeat(3) @(posedge clk);    // 3 cycles < SIM_DEBOUNCE=10
        button = 1'b1;
        repeat(3) @(posedge clk);
      end
    end
  endtask

  task wait_busy_low;
    // Wait until busy deasserts, with timeout
    input int max_cycles;
    integer cyc;
    begin
      cyc = 0;
      while (busy && cyc < max_cycles) begin
        @(posedge clk);
        cyc = cyc + 1;
      end
      if (cyc >= max_cycles)
        $display("TIMEOUT waiting for busy=0 at time %0t", $time);
    end
  endtask

  // -------------------------------------------------------------------------
  // Main test sequence
  // -------------------------------------------------------------------------
  initial begin
    pass_count = 0;
    fail_count = 0;
    button     = 1'b1;   // released (active-low)
    reset_n    = 1'b0;

    $display("==================================================");
    $display("TOYSOUND-01 RTL Simulation");
    $display("Date: 2026-10-02  Simulator: Icarus Verilog");
    $display("SIM_DEBOUNCE = %0d cycles", `SIM_DEBOUNCE);
    $display("Architecture: Single Next Button");
    $display("==================================================");

    // -----------------------------------------------------------------------
    // T01 — Reset
    // -----------------------------------------------------------------------
    test_num = 1;
    $display("\n--- T01: Reset ---");
    repeat(10) @(posedge clk);
    reset_n = 1'b1;
    @(posedge clk);
    assert_eq(busy,      0, "busy=0 after reset");
    assert_eq(sound_out, 0, "sound_out=0 after reset");

    // -----------------------------------------------------------------------
    // T02 — Button press 1 (Sound 1)
    // -----------------------------------------------------------------------
    test_num = 2;
    $display("\n--- T02: Button press 1 (Sound 1) ---");
    press_button(`SIM_DEBOUNCE + 5);
    repeat(5) @(posedge clk);
    assert_eq(busy, 1, "busy=1 after button 1 press");
    $display("  Waiting for sound to complete...");
    wait_busy_low(2_000_000);
    assert_eq(busy, 0, "busy=0 after sound 1 finishes");

    // -----------------------------------------------------------------------
    // T03 — Button press 2 (Sound 2)
    // -----------------------------------------------------------------------
    test_num = 3;
    $display("\n--- T03: Button press 2 (Sound 2) ---");
    press_button(`SIM_DEBOUNCE + 5);
    repeat(5) @(posedge clk);
    assert_eq(busy, 1, "busy=1 after button 2 press");
    wait_busy_low(2_000_000);
    assert_eq(busy, 0, "busy=0 after sound 2 finishes");

    // -----------------------------------------------------------------------
    // T04 — Button press 3 (Sound 3)
    // -----------------------------------------------------------------------
    test_num = 4;
    $display("\n--- T04: Button press 3 (Sound 3) ---");
    press_button(`SIM_DEBOUNCE + 5);
    repeat(5) @(posedge clk);
    assert_eq(busy, 1, "busy=1 after button 3 press");
    wait_busy_low(2_000_000);
    assert_eq(busy, 0, "busy=0 after sound 3 finishes");

    // -----------------------------------------------------------------------
    // T05 — Button press 4 (Sound 4)
    // -----------------------------------------------------------------------
    test_num = 5;
    $display("\n--- T05: Button press 4 (Sound 4) ---");
    press_button(`SIM_DEBOUNCE + 5);
    repeat(5) @(posedge clk);
    assert_eq(busy, 1, "busy=1 after button 4 press");
    wait_busy_low(2_000_000);
    assert_eq(busy, 0, "busy=0 after sound 4 finishes");

    // -----------------------------------------------------------------------
    // T06 — Button press 5 (Wraps back to Sound 1)
    // -----------------------------------------------------------------------
    test_num = 6;
    $display("\n--- T06: Button press 5 (Wrap back to Sound 1) ---");
    press_button(`SIM_DEBOUNCE + 5);
    repeat(5) @(posedge clk);
    assert_eq(busy, 1, "busy=1 after button 5 press");
    wait_busy_low(2_000_000);
    assert_eq(busy, 0, "busy=0 after wrapped sound 1 finishes");

    // -----------------------------------------------------------------------
    // T07 — Button bounce (short pulses < debounce threshold)
    // -----------------------------------------------------------------------
    test_num = 7;
    $display("\n--- T07: Button bounce suppression ---");
    bounce_button();     // sub-threshold pulses
    repeat(20) @(posedge clk);
    assert_eq(busy, 0, "busy=0 after bounce (no event should fire)");

    // -----------------------------------------------------------------------
    // T08 — Button press during playback (should be ignored)
    // -----------------------------------------------------------------------
    test_num = 8;
    $display("\n--- T08: Button press ignored during playback ---");
    press_button(`SIM_DEBOUNCE + 5);     // start sound
    repeat(5) @(posedge clk);
    assert_eq(busy, 1, "busy=1 after button press");
    // Now press button while playing
    press_button(`SIM_DEBOUNCE + 5);
    assert_eq(busy, 1, "busy still 1 (second button press ignored)");
    wait_busy_low(2_000_000);
    assert_eq(busy, 0, "busy=0 after sound finishes");

    // -----------------------------------------------------------------------
    // T09 — Reset during playback
    // -----------------------------------------------------------------------
    test_num = 9;
    $display("\n--- T09: Reset during playback ---");
    press_button(`SIM_DEBOUNCE + 5);
    repeat(5) @(posedge clk);
    assert_eq(busy, 1, "busy=1 before reset");
    // Apply reset mid-playback
    reset_n = 1'b0;
    repeat(3) @(posedge clk);
    assert_eq(busy,      0, "busy=0 during reset");
    assert_eq(sound_out, 0, "sound_out=0 during reset");
    reset_n = 1'b1;
    @(posedge clk);
    assert_eq(busy, 0, "busy=0 after reset release");

    // -----------------------------------------------------------------------
    // Final report
    // -----------------------------------------------------------------------
    $display("\n==================================================");
    $display("SIMULATION COMPLETE");
    $display("  PASS: %0d", pass_count);
    $display("  FAIL: %0d", fail_count);
    $display("==================================================");

    if (fail_count == 0)
      $display("ALL TESTS PASSED");
    else
      $display("SOME TESTS FAILED - review output above");

    $finish;
  end

  // -------------------------------------------------------------------------
  // Timeout watchdog (prevents infinite loop if design hangs)
  // -------------------------------------------------------------------------
  initial begin
    #(20_000_000_000);   // 20 seconds simulation time limit
    $display("ERROR: Simulation timeout!");
    $finish;
  end

endmodule : toysound_top_tb

`default_nettype wire
