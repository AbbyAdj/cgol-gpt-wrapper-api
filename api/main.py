"""Fastapi logic with endpoints"""
from pprint import pprint
import os
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from ai_client.wrapper import client_response

load_dotenv(override=True)

API_KEY = os.environ.get("API_KEY")
client = OpenAI(api_key=API_KEY)

app = FastAPI()
templates = Jinja2Templates(directory="api/templates")


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request): 
    return templates.TemplateResponse("frontend.html", {"request": request})


@app.post("/", status_code=201,response_class=HTMLResponse)
def run_cgol_game(request: Request, user_input: str =  Form(...)):
    if not user_input:
        return templates.TemplateResponse("frontend.html", {"request": request})
    server_response = client_response(client, user_input=user_input)
    return templates.TemplateResponse("frontend.html", {"request": request, "server_response": server_response}, status_code=201)

