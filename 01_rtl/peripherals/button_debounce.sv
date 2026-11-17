
module button_debounce #(
  parameter int DEBOUNCE_CYCLES = 1000  // stable cycles needed (1 ms at 1 MHz)
) (
  input  wire clk,
  input  wire reset_n,
  input  wire btn_raw,    // raw button input, active-low (0 = pressed)
  output reg  btn_event   // single-cycle pulse, active-high, on confirmed press
);

  // -------------------------------------------------------------------------
  // Internal counter — needs enough bits to count to DEBOUNCE_CYCLES
  // -------------------------------------------------------------------------
  localparam int COUNT_WIDTH = $clog2(DEBOUNCE_CYCLES + 1);

  reg [COUNT_WIDTH-1:0] count;
  reg                   armed;   // 0 = waiting for release before next event

  // -------------------------------------------------------------------------
  // Synchronise the raw button input to clk (two-FF synchroniser)
  // btn_raw is assumed to come from off-chip; always synchronise external inputs
  // -------------------------------------------------------------------------
  reg btn_sync0, btn_sync1;

  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      btn_sync0 <= 1'b1;
      btn_sync1 <= 1'b1;
    end else begin
      btn_sync0 <= btn_raw;
      btn_sync1 <= btn_sync0;
    end
  end

  // -------------------------------------------------------------------------
  // Debounce counter and event generation
  // btn_sync1 = 0 means button is pressed
  // -------------------------------------------------------------------------
  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      count     <= '0;
      armed     <= 1'b1;
      btn_event <= 1'b0;
    end else begin
      // Default: no event
      btn_event <= 1'b0;

      if (!btn_sync1) begin
        // Button appears pressed
        if (armed) begin
          if (count == COUNT_WIDTH'(DEBOUNCE_CYCLES - 1)) begin
            // Counter saturated: confirmed press
            btn_event <= 1'b1;   // fire event for one cycle
            armed     <= 1'b0;   // disarm until release
            count     <= '0;
          end else begin
            count <= count + 1'b1;
          end
        end
        // If not armed, hold count at zero and wait for release
      end else begin
        // Button released (or bouncing high): reset counter and re-arm
        count <= '0;
        armed <= 1'b1;
      end
    end
  end

endmodule : button_debounce

`default_nettype wire
