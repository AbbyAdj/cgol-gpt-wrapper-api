import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch

class TestRunCgolGame:
    @patch("api.main.client_response")
    def test_run_cgol_game(self, mock_client_response):
        client = TestClient(app)

        expected_res = 'The data for the word "blunt" is as follows:\n\n- Generations: 42\n- Score: 577'
        mock_client_response.return_value = expected_res
        
        response = client.post("/results", data={"user_input": "give  me data on the word blunt"})
        
        assert response.status_code == 201
        assert response.json() == {"server_response": expected_res}
        mock_client_response.assert_called_once()

    def test_run_cgol_game_empty(self):
        client = TestClient(app)
        response = client.post("/results", data={"user_input": ""})
        assert response.status_code == 200
        assert response.json()["server_response"] == "Invalid user input"