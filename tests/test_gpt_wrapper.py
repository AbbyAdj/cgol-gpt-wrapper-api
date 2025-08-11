import json
import pytest
from unittest.mock import patch, MagicMock, Mock
from ai_client.wrapper import client_response


@patch("ai_client.wrapper.run_game")
class TestClientResponse:
    def test_client_response_calls_run_game_with_word(self, mock_run_game):
        # Setup
        mock_run_game.return_value = {"generations": 5, "score": 10}
        mock_client = MagicMock()
        # Simulate OpenAI response structure
        mock_call = MagicMock()
        mock_call.type = "function_call"
        mock_call.name = "run_game"
        mock_call.arguments = '{"word": "blunt"}'
        mock_call.call_id = "abc123"
        # Mock the OpenAI client response
        mock_client.responses.create.side_effect = [
            MagicMock(output=[mock_call]),
            MagicMock(output_text='The data for the word \"blunt\" is as follows:\n\n- **Generations**: 42\n- **Score**: 577'),
        ]

        result = client_response(mock_client, "give me data on the word blunt")
        assert result == 'The data for the word "blunt" is as follows:\n\n- Generations: 42\n- Score: 577'
        mock_run_game.assert_called_once_with("blunt")

    def test_client_response_handles_no_function_call(self, mock_run_game):
        mock_client = MagicMock()
        # Simulate OpenAI response with no function call
        mock_client.responses.create.side_effect = [
            MagicMock(output=[]),
            MagicMock(output_text="No function call")
        ]
        result = client_response(mock_client, "no call")
        assert "No function call" in result
        mock_run_game.assert_not_called()

    def test_client_response_handles_multiple_function_calls(self, mock_run_game: Mock):
        mock_run_game.side_effect = [
            {"generations": 44, "score": 760},
            {"generations": 7, "score": 39}
        ]
        # Create two function call mocks for foo and bar
        mock_call_foo = MagicMock()
        mock_call_foo.type = "function_call"
        mock_call_foo.name = "run_game"
        mock_call_foo.arguments = json.dumps({'word': "foo"})
        mock_call_foo.call_id = "foo123"

        mock_call_bar = MagicMock()
        mock_call_bar.type = "function_call"
        mock_call_bar.name = "run_game"
        mock_call_bar.arguments = json.dumps({'word': "bar"})
        mock_call_bar.call_id = "bar123"
        mock_client = MagicMock()

        mock_client.responses.create.side_effect = [
            MagicMock(
                output=[mock_call_foo, mock_call_bar]
            ),
            MagicMock(output_text="Foo has 44 generations and a score of 760. Bar has 7 generations and a score of 39.")
        ]

        result = client_response(mock_client, "how many generations do foo and bar have?")

        assert result == "Foo has 44 generations and a score of 760. Bar has 7 generations and a score of 39."
        mock_run_game.assert_any_call("foo")
        mock_run_game.assert_any_call("bar")
        assert mock_run_game.call_count == 2

    def test_client_response_handles_missing_word(self, mock_run_game):
        mock_client = MagicMock()
        # Simulate OpenAI response with no function call
        mock_client.responses.create.side_effect = [
            MagicMock(output=[]),
            MagicMock(output_text="Please provide a specific word or query to proceed with the request.")
        ]
        result = client_response(mock_client, "")
        assert result == "Please provide a specific word or query to proceed with the request."
        mock_run_game.assert_not_called()
