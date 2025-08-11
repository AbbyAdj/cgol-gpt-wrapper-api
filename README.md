# Conway’s Game of Life With GPT Integration

![alt text](UI.png)

This project implements Conway's Game of Life in Python, where the initial seed pattern is generated from a word/words taken from the user prompt.

Each character of the word is converted into an 8-bit binary representation (from its ASCII code), with `1` bits as live cells and `0` bits as dead cells.

The seed is centered in the grid with each letter's ASCII binary occupying a row. This pattern then evolves according to the standard Game of Life rules.

The project is hosted on [this link](https://cgol-gpt-wrapper.onrender.com/)

## Features

- **Word-to-Pattern Conversion**: Transform any input word into a unique Game of Life seed pattern.
- **Generative AI Integration**: Leverage large language models to generate dynamic seed patterns based on textual prompts.
- **API/UI Interface**: Interact with the Game of Life simulation through a RESTful API, enabling programmatic access and control, or through a UI exposed by this tool. Note this is protected by password access.

## How It Works

1. **Matrix Dimensions**: The grid is represented as 60 X 40 matrix which uses an input word to determine the initial live cells (starting pattern).
2. **Word Processing**: Each character of the word is converted into its ASCII value, then into an 8-bit binary string. These binary strings form the initial pattern.
3. **Pattern Centering**: The generated pattern is centered in the grid to maintain symmetry and consistency.
4. **Simulation**: The Game of Life rules are applied to evolve the pattern over time, allowing users to observe the progression from the initial seed using the run_game function.
5. **Post-Stability**: Once the pattern has reached stability (extinction, a persistent state, repeating patterns or exceeding 1000 generations), the function run_game will return a dictionary with the keys generation and score.
The score defines the sum of all live cells during each generation.
6. **GPT Integration**: The GPT wrapper client uses [function calling](https://platform.openai.com/docs/guides/function-calling) to call the run_game method. Depending on the prompt, the tool extracts the word(s) to be used in calling the function and returns the appropriate response to the user.
7. **API**: There are two endpoints, the GET / renders the user interface. The POST /results with an input body, returns a json which is rendered by the frontend. Fastapi was chosen for its ease of use as an API framework and easy integration with jinja2 for frontent rendering.

## Tech Stack
- Python 3 (Backend logic and GPT integration)
- FastAPI (API framework)
- Javascript (Client side logic and validation)
- HTML and CSS (User interface)

## Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/AbbyAdj/cgol-gpt-wrapper-api.git

cd cgol-gpt-wrapper-api

pip install -r requirements.txt

touch .env 

```
 add an API_KEY to your .env file. Your server would not run without it. To set this up, visit [this link](https://platform.openai.com/).

---

## Usage

To start the API server:

```bash
python run.py
```

---

## API Endpoints

### `GET /`

```
Renders client side UI
```

### `POST /results`

Generate a Game of Life seed pattern from a given word.

**Request Body**:

```
{
  "user_input": "How many generations will the word 'monument' return from the Conway tool?"
}

```
**Response Body**:
```
An example of what the response body might look like:

{
  "server_response": "The word "monument" will return 13 generations from the Conway tool."
}

```
---

## Development

For development purposes, you can use the following command to start the server with live reloading:

```bash
fastapi dev api/main.py
```
---

## Testing

To run the test suite:

```bash
pip install -r dev-requirements.txt
pytest
```
---

## Future Work/Extensions

- Testing: More tests will be added in order to ensure the integrity of the code.

- Validation: More validation will be added for user inputs. This will include more pydantic models for stricter enforcements.

- Extensive Error handling: Error handling will be explored further to ensure integrity of code.

- Rate Limiting: As we are calling Openai's APIs with each call and this can both be costly and/or abused, rate limits will be implemented per user to minimize costs.

- Live Animation/Simulation: An animation is to be added for users to see a live simulation of their pattern and how it evolves.


## Known Issues

- For a user prompt, say "Generate 6 random words and tell me the highest Conway score and lowest generation", the tool does not return any response. However when it is called again immediately after, it runs as expected.

- For the random word generation, the wrapper seems to call complex words which usually exceed 1000 generations unless explicitly stated by the user to use simple words.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

