// =============================================================================
// timer.sv
// TOYSOUND-01 — Generic down-counter timer
//
// Process : SCL 1.2 µm CMOS (C1D)
// Revision: A
// Date    : 2026-10-02
//
// Description:
//   Parameterised synchronous down-counter.
//   - Load a value with load=1 on any clock edge.
//   - When enable=1, decrements each cycle.
//   - done pulses for one cycle when counter reaches 1 and transitions to 0.
//   - done stays 0 while counter is already 0 (prevents repeated firing).
//   - Can be loaded with a new value at any time.
// =============================================================================

`default_nettype none

module timer #(
  parameter int WIDTH = 20   // counter width; 20 bits → up to ~1M cycles
) (
  input  wire             clk,
  input  wire             reset_n,
  input  wire [WIDTH-1:0] load_val,  // value to load
  input  wire             load,      // load strobe (priority over enable)
  input  wire             enable,    // count-down enable
  output reg              done       // one-cycle pulse when counter hits 0
);

  reg [WIDTH-1:0] count;

  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      count <= '0;
      done  <= 1'b0;
    end else begin
      done <= 1'b0;  // default

      if (load) begin
        count <= load_val;
      end else if (enable && count != '0) begin
        if (count == WIDTH'(1)) begin
          done  <= 1'b1;
          count <= '0;
        end else begin
          count <= count - 1'b1;
        end
      end
    end
  end

endmodule : timer

`default_nettype wire
