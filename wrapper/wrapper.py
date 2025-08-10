import json
from pprint import pprint
from openai import OpenAI, api_key
from api.cgol import run_game

GPT_MODEL = "gpt-4o-mini"


def client_response(client: OpenAI, user_input: str)->str:
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
        {"role": "system", "content": "Format your response well, do not asterix."},
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
           

            # 3. Execute the function logic for get_horoscope
            result = run_game(function_call_arguments["word"])

            # 4. Provide function call results to the model
            input_list.append({
                "type": "function_call_output",
                "call_id": function_call.call_id, # type: ignore
                "output": json.dumps(result),
            })

    response = client.responses.create(
        model=GPT_MODEL,
        instructions="Respond in a way that answers the user's question using the response",
        tools=tools, # type: ignore
        input=input_list, # type: ignore
    )

    # 5. The model should be able to give a response!
    return response.output_text
