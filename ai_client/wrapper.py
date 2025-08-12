"""AI client wrapper logic

This module provides a wrapper for interacting with the OpenAI API in the context of Conway's Game of Life.
It defines custom exceptions for server errors and provides a function to handle user input, call the LLM,
and invoke the game logic as needed.
"""

import json
from pprint import pprint
from openai import OpenAI, APIConnectionError, APITimeoutError, AuthenticationError, BadRequestError, InternalServerError, RateLimitError
from api.cgol import run_game

GPT_MODEL = "gpt-4o-mini"

class ServerError(Exception):
    """Exception raised for server-related errors when communicating with the OpenAI API."""
    pass

class OpenAIServerError(Exception):
    """Exception raised for OpenAI-specific errors such as timeouts or bad requests."""
    pass

def client_response(client: OpenAI, user_input: str)->str:
    """
    Handles user input, interacts with the OpenAI API, and returns a formatted response.

    This function:
    - Defines the available tools (functions) for the LLM, specifically the 'run_game' function.
    - Constructs the input prompt for the LLM, including system instructions and the user's input.
    - Sends the prompt to the OpenAI API and processes the response.
    - If the LLM requests a function call (e.g., 'run_game'), it executes the function and appends the result to the input list.
    - Sends the updated input list back to the LLM for a final response.
    - Returns the model's response as a string, with asterisks removed for formatting.

    Args:
        client (OpenAI): An authenticated OpenAI client instance.
        user_input (str): The user's input or query.

    Returns:
        str: The formatted response from the LLM.

    Raises:
        ServerError: If there is a connection, authentication, or rate limit error.
        OpenAIServerError: If there is a timeout, bad request, or internal server error.
    """
    try:
        tools = [
            {
                "type": "function",
                "name": "run_game",
                "description": "Get information about the generations and scores for Conways game of life",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "The search query for the data which must include the query or word to call the function with"
                        }
                    },
                    "required": ["word"],
                },
            }
        ]

        # Create a running input list we will add to over time
        input_list = [
            {"role": "system", "content": "Parse the prompt and use it to call the run_game function as many times as needed"},
            {"role": "system", "content": "If you are asked to generate/decide the words, come up with N number of words that do not share similarities"},
            {"role": "system", "content": "Format your response well, do not add any asterix."},
            {"role": "system", "content": "If a word or prompt is not provided by the user, return an appropriate error message."},
            {"role": "user", "content": user_input}
        ]

        # 2. Prompt the model with tools defined
        response = client.responses.create(
            model=GPT_MODEL,
            tools=tools, # type: ignore
            input=input_list, # type: ignore
        )

        # Save function call outputs for subsequent requests
        function_call = None
        function_call_arguments = None
        input_list += response.output


        for item in response.output:
            if item.type == "function_call" and item.name == "run_game":
                function_call = item
                function_call_arguments = json.loads(item.arguments)
            

                result = run_game(function_call_arguments["word"])
                input_list.append({
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(result),
                })

        response = client.responses.create(
            model=GPT_MODEL,
            instructions="Respond in a way that answers the user's question using the response",
            tools=tools, # type: ignore
            input=input_list, # type: ignore
        )

        return response.output_text.replace("*", "") #The model tends to respond with double asterisks, I assume for emphasis, so I removed them

    except (APIConnectionError, AuthenticationError, RateLimitError) as e:
        raise ServerError()

    except (APITimeoutError, BadRequestError, InternalServerError) as e:
        raise OpenAIServerError()
    