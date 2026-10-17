// =============================================================================
// sound_sequencer.sv
// TOYSOUND-01 — Sound sequencer (ROM-based tone sequence player)
//
// Process : SCL 1.2 µm CMOS (C1D)
// Revision: A
// Date    : 2026-10-02
//
// Description:
//   Walks through a ROM table of tones for the selected sound.
//   Each entry has: divider (frequency) + duration (cycles).
//   Uses an internal timer instance to track note duration.
//
//   Interface:
//     start     — pulse high for one cycle to begin playback
//     sound_sel — select which of the 4 sounds to play
//     tone_div  — current note divider (connect to tone_generator)
//     tone_en   — high while a note is playing (low during rest or idle)
//     done      — one-cycle pulse when the entire sound sequence completes
// =============================================================================

`default_nettype none

import toysound_pkg::*;

module sound_sequencer (
  input  wire        clk,
  input  wire        reset_n,
  // Control
  input  wire        start,           // begin playback (one-cycle pulse)
  input  wire [1:0]  sound_sel,       // which sound (0–3)
  // To tone_generator
  output reg  [DIV_WIDTH-1:0] tone_div, // current note divider
  output reg               tone_en,     // 1 = tone on, 0 = rest/idle
  // Status
  output reg               done         // one-cycle pulse: all notes complete
);

  // -------------------------------------------------------------------------
  // ROM: 4 sounds × NOTES_PER_SOUND notes
  // -------------------------------------------------------------------------
  // We store all four sounds as a flat 2D array.
  // Index: sound[sound_id][note_index]
  //
  // Use case-statement ROM rather than Verilog array parameters for maximum
  // synthesis compatibility across tools.
  // -------------------------------------------------------------------------

  // Internal state
  reg [1:0]                state;
  reg [$clog2(NOTES_PER_SOUND):0] note_idx; // current note index
  reg [DIV_WIDTH-1:0]      cur_div;         // latched divider for this note
  reg [DUR_WIDTH-1:0]      cur_dur;         // latched duration for this note
  reg [1:0]                cur_sound;       // latched sound selection

  // Timer interface
  reg               tmr_load;
  reg  [DUR_WIDTH-1:0] tmr_load_val;
  wire              tmr_done;
  reg               tmr_en;

  // -------------------------------------------------------------------------
  // Timer instance
  // -------------------------------------------------------------------------
  timer #(.WIDTH(DUR_WIDTH)) u_dur_timer (
    .clk      (clk),
    .reset_n  (reset_n),
    .load_val (tmr_load_val),
    .load     (tmr_load),
    .enable   (tmr_en),
    .done     (tmr_done)
  );

  // -------------------------------------------------------------------------
  // ROM lookup: given (sound_id, note_idx), return (divider, duration)
  // This synthesises to a mux/combinational ROM.
  // -------------------------------------------------------------------------
  logic [DIV_WIDTH-1:0] rom_div;
  logic [DUR_WIDTH-1:0] rom_dur;

  always_comb begin
    // Default (safety)
    rom_div = NOTE_REST;
    rom_dur = DUR_QUARTER;

    unique case ({cur_sound, note_idx[1:0]})
      // Sound 0: A4 → A5 → REST
      4'b00_00: begin rom_div = NOTE_A4;   rom_dur = DUR_QUARTER;  end
      4'b00_01: begin rom_div = NOTE_A5;   rom_dur = DUR_QUARTER;  end
      4'b00_10: begin rom_div = NOTE_REST; rom_dur = DUR_REST_S;   end

      // Sound 1: C4 → E4 → G4
      4'b01_00: begin rom_div = NOTE_C4;   rom_dur = DUR_DOTTED_Q; end
      4'b01_01: begin rom_div = NOTE_E4;   rom_dur = DUR_DOTTED_Q; end
      4'b01_10: begin rom_div = NOTE_G4;   rom_dur = DUR_DOTTED_Q; end

      // Sound 2: G4 → G4 → A4
      4'b10_00: begin rom_div = NOTE_G4;   rom_dur = DUR_SHORT_G;  end
      4'b10_01: begin rom_div = NOTE_G4;   rom_dur = DUR_SHORT_G;  end
      4'b10_10: begin rom_div = NOTE_A4;   rom_dur = DUR_LONG_G;   end

      // Sound 3: B4 → A4 → G4
      4'b11_00: begin rom_div = NOTE_B4;   rom_dur = DUR_MED;      end
      4'b11_01: begin rom_div = NOTE_A4;   rom_dur = DUR_MED;      end
      4'b11_10: begin rom_div = NOTE_G4;   rom_dur = DUR_LONG;     end

      default:  begin rom_div = NOTE_REST; rom_dur = DUR_QUARTER;  end
    endcase
  end

  // -------------------------------------------------------------------------
  // Sequencer FSM
  // -------------------------------------------------------------------------
  always_ff @(posedge clk or negedge reset_n) begin
    if (!reset_n) begin
      state        <= SEQ_IDLE;
      note_idx     <= '0;
      cur_div      <= '0;
      cur_dur      <= '0;
      cur_sound    <= '0;
      tone_div     <= '0;
      tone_en      <= 1'b0;
      done         <= 1'b0;
      tmr_load     <= 1'b0;
      tmr_load_val <= '0;
      tmr_en       <= 1'b0;
    end else begin
      // Defaults
      done     <= 1'b0;
      tmr_load <= 1'b0;
      tmr_en   <= 1'b0;

      case (state)
        // ----------------------------------------------------------------
        SEQ_IDLE: begin
          tone_div <= '0;
          tone_en  <= 1'b0;
          note_idx <= '0;
          if (start) begin
            cur_sound <= sound_sel;
            note_idx  <= '0;
            state     <= SEQ_PLAY;
          end
        end

        // ----------------------------------------------------------------
        SEQ_PLAY: begin
          // Latch current note from ROM (cur_sound+note_idx already set)
          cur_div      <= rom_div;
          cur_dur      <= rom_dur;
          tone_div     <= rom_div;
          tone_en      <= (rom_div != '0); // no tone during REST
          // Load the duration timer
          tmr_load_val <= rom_dur;
          tmr_load     <= 1'b1;
          state        <= SEQ_WAIT_DUR;
        end

        // ----------------------------------------------------------------
        SEQ_WAIT_DUR: begin
          tmr_en <= 1'b1;   // count down
          if (tmr_done) begin
            // Note finished
            if (note_idx == ($clog2(NOTES_PER_SOUND))'(NOTES_PER_SOUND - 1)) begin
              // Last note: sound complete
              tone_div <= '0;
              tone_en  <= 1'b0;
              state    <= SEQ_DONE;
            end else begin
              // Advance to next note
              note_idx <= note_idx + 1'b1;
              state    <= SEQ_PLAY;
            end
          end
        end

        // ----------------------------------------------------------------
        SEQ_DONE: begin
          done     <= 1'b1;   // one-cycle pulse
          note_idx <= '0;
          state    <= SEQ_IDLE;
        end

        // ----------------------------------------------------------------
        default: state <= SEQ_IDLE;
      endcase
    end
  end

endmodule : sound_sequencer

`default_nettype wire
