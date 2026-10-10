// =============================================================================
// sound_controller.sv
// TOYSOUND-01 — Top-level sound controller FSM
//
// Process : SCL 1.2 µm CMOS (C1D)
// Revision: B
// Date    : 2026-10-02
//
// Description:
//   Receives a single debounced button event.
//   On press, increments an internal sound index, starts the sequencer,
//   and monitors for completion.
//   Prevents button interruption while a sound is playing (buttons ignored).
//   Returns to IDLE when the sequencer signals done.
//
//   FSM:
//     SC_IDLE       : Wait for button event
//     SC_LOAD_SOUND : Command sequencer to start with current sound_index
//     SC_PLAYING    : Sound playing; ignore further button events
//     SC_DONE       : Sound finished; clear busy
// =============================================================================

`default_nettype none

import toysound_pkg::*;

module sound_controller (
  input  wire        clk,
  input  wire        reset_n,
  // Debounced button event (one cycle pulse)
  input  wire        btn_event,
  // Sequencer interface
  output reg  [1:0]  sound_sel,   // which sound to play
  output reg         play_en,     // start the sequencer (one-cycle pulse)
  input  wire        seq_done,    // sequencer signals completion
  // Status
  output reg         busy         // high while sound is playing
);

  sc_state_t state;
  reg [1:0]  song_index;

  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      state      <= SC_IDLE;
      sound_sel  <= 2'b00;
      play_en    <= 1'b0;
      busy       <= 1'b0;
      song_index <= 2'b11; // Initializes so first press plays sound 0
    end else begin
      // Defaults
      play_en <= 1'b0;

      case (state)
        // ------------------------------------------------------------------
        SC_IDLE: begin
          busy <= 1'b0;
          if (btn_event) begin
            // Increment sound index, wrap at 3 (0-3)
            song_index <= song_index + 1'b1;
            state      <= SC_LOAD_SOUND;
          end
        end

        // ------------------------------------------------------------------
        SC_LOAD_SOUND: begin
          sound_sel <= song_index;
          play_en   <= 1'b1;   // pulse sequencer start
          busy      <= 1'b1;
          state     <= SC_PLAYING;
        end

        // ------------------------------------------------------------------
        SC_PLAYING: begin
          busy <= 1'b1;
          // Button events are ignored while playing
          if (seq_done) begin
            state <= SC_DONE;
          end
        end

        // ------------------------------------------------------------------
        SC_DONE: begin
          busy  <= 1'b0;
          state <= SC_IDLE;
        end

        // ------------------------------------------------------------------
        default: state <= SC_IDLE;
      endcase
    end
  end

endmodule : sound_controller

`default_nettype wire
