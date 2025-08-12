"""Fastapi logic with endpoints
This module sets up the FastAPI application for the Conway's Game of Life project.
It defines endpoints for the homepage and for running the game logic, and handles
interaction with the OpenAI API through the ai_client.wrapper.
"""
from pprint import pprint
import os
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse,  HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from ai_client.wrapper import client_response, ServerError, OpenAIServerError

load_dotenv(override=True)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PASSWORD = os.environ.get("PASSWORD")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()
templates = Jinja2Templates(directory="api/templates")
app.mount("/static", StaticFiles(directory="api/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request): 
    """
    Renders the homepage using the frontend.html Jinja2 template.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        TemplateResponse: The rendered homepage.
    """
    return templates.TemplateResponse("frontend.html", {"request": request})


@app.post("/results", status_code=201)
def run_cgol_game(user_input: str =  Form(...)):
    """
    Processes user input from the frontend, calls the client_response function to interact
    with the OpenAI API, and returns the game results as a JSON response.

    Args:
        user_input (str): The word or prompt submitted by the user.

    Returns:
        JSONResponse: The server's response containing the game results or an error message.
    """
    try:
        if not user_input:
            return JSONResponse(content={"server_response": "Invalid user input"})
        server_response = client_response(client, user_input=user_input)
        return JSONResponse(content={"server_response": server_response}, status_code=201)
    
    except (ServerError, OpenAIServerError) as e:
        return JSONResponse(content={"server_response": "Internal Server Error"}, status_code=500)

