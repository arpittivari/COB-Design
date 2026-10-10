// =============================================================================
// tone_generator.sv
// TOYSOUND-01 — Programmable square-wave tone generator
//
// Process : SCL 1.2 µm CMOS (C1D)
// Revision: A
// Date    : 2026-10-02
//
// Description:
//   Generates a square wave at a programmable frequency by clock division.
//
//   Frequency:
//     tone_freq = clk_freq / (2 × divider)
//
//   When divider = 0 (NOTE_REST), output is held low (silence).
//   When enable = 0, output is held low regardless of divider.
//
//   The divider is loaded combinatorially from the input port on every cycle.
//   Changing divider mid-note will change pitch immediately (acceptable for
//   this design; could be registered if glitch-sensitivity were a concern).
// =============================================================================

`default_nettype none

module tone_generator #(
  parameter int DIV_WIDTH = 16   // divider register width
) (
  input  wire               clk,
  input  wire               reset_n,
  input  wire [DIV_WIDTH-1:0] divider,  // half-period in clock cycles
  input  wire               enable,     // 1 = generate; 0 = output held low
  output reg                tone_out    // square wave output
);

  reg [DIV_WIDTH-1:0] count;

  // -------------------------------------------------------------------------
  // Toggle logic: count down; when count hits 0, reload and toggle
  // -------------------------------------------------------------------------
  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      count    <= '0;
      tone_out <= 1'b0;
    end else begin
      if (!enable || divider == '0) begin
        // Silence: reset counter and output
        count    <= '0;
        tone_out <= 1'b0;
      end else begin
        if (count == '0) begin
          // Reload and toggle
          count    <= divider - 1'b1;
          tone_out <= ~tone_out;
        end else begin
          count <= count - 1'b1;
        end
      end
    end
  end

endmodule : tone_generator

`default_nettype wire
