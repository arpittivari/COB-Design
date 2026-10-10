// =============================================================================
// toysound_pkg.sv
// TOYSOUND-01 — Package: types, constants, tone table
//
// Process : SCL 1.2 µm CMOS (C1D)
// Revision: A
// Date    : 2026-10-02
// =============================================================================

package toysound_pkg;

  // ---------------------------------------------------------------------------
  // Clock frequency — set this once; all dividers reference it
  // ---------------------------------------------------------------------------
  parameter int CLK_FREQ_HZ = 1_000_000;   // 1 MHz default

  // ---------------------------------------------------------------------------
  // Debounce
  //   1 ms debounce window at 1 MHz = 1000 cycles
  // ---------------------------------------------------------------------------
  parameter int DEBOUNCE_CYCLES = 1000;

  // ---------------------------------------------------------------------------
  // Number of buttons / sounds
  // ---------------------------------------------------------------------------
  parameter int N_BUTTONS = 1;
  parameter int N_SOUNDS  = 4;

  // ---------------------------------------------------------------------------
  // Sound controller FSM states
  // ---------------------------------------------------------------------------
  typedef enum logic [2:0] {
    SC_IDLE       = 3'b000,
    SC_LOAD_SOUND = 3'b001,
    SC_PLAYING    = 3'b010,
    SC_DONE       = 3'b011
  } sc_state_t;

  // ---------------------------------------------------------------------------
  // Sequencer FSM states
  // ---------------------------------------------------------------------------
  typedef enum logic [1:0] {
    SEQ_IDLE     = 2'b00,
    SEQ_PLAY     = 2'b01,
    SEQ_WAIT_DUR = 2'b10,
    SEQ_DONE     = 2'b11
  } seq_state_t;

  // ---------------------------------------------------------------------------
  // Tone divider width and duration width
  // ---------------------------------------------------------------------------
  parameter int DIV_WIDTH = 16;
  parameter int DUR_WIDTH = 20;

  // ---------------------------------------------------------------------------
  // Note divider values for 1 MHz clock
  //   formula: divider = CLK_FREQ_HZ / (2 * target_freq_hz)
  //   Output toggles every divider cycles → square wave period = 2*divider cycles
  // ---------------------------------------------------------------------------
  parameter logic [DIV_WIDTH-1:0] NOTE_A4  = 16'd1136;  // 440 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_A5  = 16'd568;   // 880 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_B4  = 16'd1012;  // 494 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_C4  = 16'd1916;  // 261 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_C5  = 16'd958;   // 523 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_D4  = 16'd1703;  // 294 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_E4  = 16'd1515;  // 330 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_F4  = 16'd1430;  // 349 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_G4  = 16'd1276;  // 392 Hz
  parameter logic [DIV_WIDTH-1:0] NOTE_REST = 16'd0;    // Silence

  // ---------------------------------------------------------------------------
  // Duration values (in clock cycles at 1 MHz)
  //   100_000 cycles = 100 ms
  // ---------------------------------------------------------------------------
  parameter logic [DUR_WIDTH-1:0] DUR_EIGHTH   = 20'd50_000;   //  50 ms
  parameter logic [DUR_WIDTH-1:0] DUR_QUARTER  = 20'd100_000;  // 100 ms
  parameter logic [DUR_WIDTH-1:0] DUR_DOTTED_Q = 20'd150_000;  // 150 ms
  parameter logic [DUR_WIDTH-1:0] DUR_HALF     = 20'd200_000;  // 200 ms
  parameter logic [DUR_WIDTH-1:0] DUR_WHOLE    = 20'd400_000;  // 400 ms
  parameter logic [DUR_WIDTH-1:0] DUR_SHORT_G  = 20'd80_000;   //  80 ms
  parameter logic [DUR_WIDTH-1:0] DUR_LONG_G   = 20'd160_000;  // 160 ms
  parameter logic [DUR_WIDTH-1:0] DUR_MED      = 20'd120_000;  // 120 ms
  parameter logic [DUR_WIDTH-1:0] DUR_LONG     = 20'd240_000;  // 240 ms
  parameter logic [DUR_WIDTH-1:0] DUR_REST_S   = 20'd50_000;   //  50 ms rest

  // ---------------------------------------------------------------------------
  // Tone record: one note in a sound sequence
  // ---------------------------------------------------------------------------
  typedef struct packed {
    logic [DIV_WIDTH-1:0] divider;   // frequency divider
    logic [DUR_WIDTH-1:0] duration;  // duration in clock cycles
  } tone_t;

  // ---------------------------------------------------------------------------
  // Sound sequences are implemented as a case-statement ROM inside
  // sound_sequencer.sv for maximum synthesis compatibility.
  // ---------------------------------------------------------------------------
  parameter int NOTES_PER_SOUND = 3;

endpackage : toysound_pkg
