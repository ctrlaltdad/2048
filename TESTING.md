# 2048 Simulation Automated Test Suite

This project includes automated tests for the core simulation logic in `ml_sim.py` using `pytest`.

## How to Run the Tests

1. **Install pytest** (if not already installed):
   ```sh
   pip install pytest
   ```
2. **Run the tests from the project root:**
   ```sh
   pytest tests/test_ml_sim.py
   ```

## Test Cases

### test_simulate_sequence_basic
- **Purpose:** Ensure `simulate_sequence` returns valid results for a simple move sequence.
- **Checks:**
  - Output types (int, list)
  - Move count is positive

### test_run_parallel_simulations_consistency
- **Purpose:** Ensure running the same sequence multiple times returns the correct number of results.
- **Checks:**
  - Output list lengths match number of runs
  - All outputs are integers

### test_simulate_two_phase_sequence_switch
- **Purpose:** Ensure two-phase simulation switches to the second sequence at the correct tile value.
- **Checks:**
  - Output types
  - Sequences used match input
  - Move count is positive

### test_run_parallel_two_phase_length
- **Purpose:** Ensure `run_parallel_two_phase` returns the correct number of results.
- **Checks:**
  - Output list lengths match number of runs

### test_simulate_two_phase_best_top_percent
- **Purpose:** Ensure `simulate_two_phase_best` returns the correct number of improved results for the top percent.
- **Checks:**
  - Output list lengths match expectations

### test_simulate_sequence_invalid_moves
- **Purpose:** Ensure `simulate_sequence` terminates if only invalid moves are given.
- **Checks:**
  - Move count is not excessive (should not loop forever)

---

For any failed tests, check your implementation in `ml_sim.py` for logic or edge case errors.
