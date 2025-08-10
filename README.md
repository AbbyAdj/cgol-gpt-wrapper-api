# Conway's Game of Life – Word Seed Edition

This project is an implementation of Conway's Game of Life in Python, where the **initial seed pattern** is generated from a given word.  
Each character of the word is converted into an **8-bit binary representation** (from its ASCII code), with `1` bits as **live cells** and `0` bits as **dead cells**. The seed is **centered** in the grid and evolves according to the standard Game of Life rules.

---

## How It Works

1. **Matrix Dimensions**  
   - The grid is represented as **rows × columns**.  
   - Example: `60 × 40` means **60 rows** (horizontal) and **40 columns** (vertical).  
   - The first coordinate is always **row**, the second is **column**: `(row, col)`.

2. **Word to Bitmask Conversion**
   - Each character → ASCII code → 8-bit binary string.
   - Example: `"H"` → ASCII `72` → Binary `01001000`.

3. **Placing the Seed in the Grid**
   - **Seed width** = `8` (bits per character).  
   - **Seed height** = `len(word)` (one bit-row per character).  
   - Starting position (top-left of seed):
     ```python
     start_row = (rows - seed_height) // 2
     start_col = (cols - seed_width) // 2
     ```
   - Bits with value `1` become **live cells** at `(row, col)` coordinates.

4. **Game of Life Rules**
   - Any live cell with fewer than 2 live neighbours dies (underpopulation).
   - Any live cell with 2 or 3 live neighbours lives on.
   - Any live cell with more than 3 live neighbours dies (overpopulation).
   - Any dead cell with exactly 3 live neighbours becomes alive (reproduction).

---

## Simulation End Conditions

The simulation stops when **any one** of the following conditions is met:

1. **Extinction**: No live cells remain on the grid (`len(live_cells) == 0`).

2. **Persistent State**: The current generation’s live cells are exactly the same as the previous generation (no changes).

3. **Periodic Pattern**: The current generation matches any of the previous 10 generations (indicating a repeating cycle with a period less than 10).

4. **Maximum Generations**: The simulation reaches 1000 generations without reaching stability or extinction.

---

## Example: `"Heya"` in a `60 × 40` Grid

### Step 1 – Binary Representation

| Char | ASCII | Binary     |
|------|-------|------------|
| H    | 72    | 01001000   |
| e    | 101   | 01100101   |
| y    | 121   | 01111001   |
| a    | 97    | 01100001   |

---

### Step 2 – Bitmask to Live Cells

`#` = live cell (`1`), `.` = dead cell (`0`).

`#` = live cell (`1`), `.` = dead cell (`0`).

Row 0: . # . . # . . . (01001000)

Row 1: . # # . . # . # (01100101)

Row 2: . # # # # . . # (01111001)

Row 3: . # # . . . . # (01100001)


---

### Step 3 – Placement in Grid

- `seed_height = 4`
- `seed_width = 8`
- `start_row = (60 - 4) // 2 = 28`
- `start_col = (40 - 8) // 2 = 16`

Live cell coordinates:

(28,17), (28,20)

(29,17), (29,18), (29,21), (29,23)

(30,17), (30,18), (30,19), (30,20), (30,23)

(31,17), (31,18), (31,23)


---

### Step 4 – Slice of Grid Around the Seed

Showing rows 26–33 and cols 14–25:

   Cols → 14 15 16 17 18 19 20 21 22 23 24 25

Row 26 . . . . . . . . . . . .

Row 27 . . . . . . . . . . . .

Row 28 . . . # . . # . . . . .

Row 29 . . . # # . . # . # . .

Row 30 . . . # # # # . . . . .

Row 31 . . . # # . . . . . . .

Row 32 . . . . . . . . . . . .

Row 33 . . . . . . . . . . . .


## API Endpoint Specification

- **Endpoint:** `/cgol`
- **Method:** POST (recommended for sending JSON payload)
- **Request JSON:**
  ```json
  {
    "word": "your_input_word"
  }
- **Response JSON:**
   ```{
   "generations": <int>,    # Number of generations until stability/extinction/limit

  "score": <int>           # Total live cells spawned during the simulation
  }

- **Behavior:**

    - Accepts the word seed (case-sensitive ASCII).

    - Runs Conway’s Game of Life on a 60x40 grid with the seed centered.

    - Applies standard rules until stability, extinction, periodicity (<10 gen), or 1000 generations max.

    - Returns the generation count and score.

## GPT Wrapper Tool (Pseudocode)

The wrapper acts as an interpreter between natural language prompts and the Conway Game of Life API.  
It extracts intent and parameters, calls the API, and returns formatted results.

---

### Core Steps

1. **Parse the prompt** to determine the user's intent:
   - If prompt contains keywords like "how many generations will" and "return":
     - Intent = QUERY_GENERATIONS
   - If prompt contains keywords like "generate", "random words", and "highest Conway score":
     - Intent = GENERATE_RANDOM_AND_HIGHEST_SCORE
   - Otherwise:
     - Intent = UNKNOWN

2. **Handle intents:**

   - **QUERY_GENERATIONS:**
     - Extract the target word from the prompt (e.g., via regex).
     - Call the CGOL API with the word.
     - Receive response with `generations` and `score`.
     - Format and return a user-friendly message.

   - **GENERATE_RANDOM_AND_HIGHEST_SCORE:**
     - Generate 3 random words internally (from a predefined word list).
     - For each word:
       - Call the CGOL API.
       - Collect the scores.
     - Identify the word with the highest score.
     - Format and return a summary message including all words and the highest score.

3. **If intent is UNKNOWN:**
   - Return a message indicating the prompt is not understood.

---

### Pseudocode Outline
    ```pseudocode
    function parse_intent(prompt):
        if "how many generations will" in prompt and "return" in prompt:
            return QUERY_GENERATIONS
        else if "generate" in prompt and "random words" in prompt and "highest Conway score" in prompt:
            return GENERATE_RANDOM_AND_HIGHEST_SCORE
        else:
            return UNKNOWN

    function handle_query_generations(prompt):
        word = extract_word_from_prompt(prompt)
        if word is None:
            return "Sorry, could not find a word."
        response = call_cgol_api(word)
        return "The word '" + word + "' runs for " + response.generations + " generations with a score of " + response.score + "."

    function handle_generate_random_and_highest_score(prompt):
        words = generate_3_random_words()
        scores = []
        for w in words:
            response = call_cgol_api(w)
            scores.append((w, response.score))
        highest = max(scores, key=score)
        return "From words " + words + ", highest score is " + highest.score + " by '" + highest.word + "'."

    function main_wrapper(prompt):
        intent = parse_intent(prompt)
        if intent == QUERY_GENERATIONS:
            return handle_query_generations(prompt)
        else if intent == GENERATE_RANDOM_AND_HIGHEST_SCORE:
            return handle_generate_random_and_highest_score(prompt)
        else:
            return "Sorry, I do not understand that prompt."

### Notes

- The function `call_cgol_api(word)` sends a request to your Conway Game of Life REST API and returns the parsed JSON response.
- The random words are selected internally from a fixed list to ensure consistency.
- This structure allows easy extension to support more prompt types in the future.


---

## Running the Game

```bash
python game_of_life.py "Heya"

ADD SECTIONS FOR VULNERABILITES AND THINGS I COULD  HAVE DONE
