import pytest
import time
import requests
import subprocess

from main import TvProgramBotErrorMessages


URL = "http://127.0.0.1:5000/"


@pytest.fixture
def setup_and_teardown():
    server = subprocess.Popen(["python3", "main.py"])
    time.sleep(5)
    yield
    server.terminate()
    server.wait()


def send_correct_message(text):
    data = {"message": {"chat": {"id": 123}, "text": text}}
    return requests.post(URL, json=data)


def send_incorrect_message_without_text():
    data = {"message": {"chat": {"id": 123}}}
    return requests.post(URL, json=data)


@pytest.mark.usefixtures("setup_and_teardown")
class TestBot:
    def test_search_existing_program(self):
        response = send_correct_message("friends")
        expected_response = (
            "Name: Friends\n"
            "Network Name: NBC\n"
            "Network Country Name: United States\n"
            "Summary: <p>Six young (20-something) people from New York City "
            "(Manhattan), on their own and struggling to survive in the real "
            "world, find the companionship, comfort and support they get "
            "from each other to be the perfect antidote to the pressures "
            "of life.</p><p>This average group of buddies goes through "
            "massive mayhem, family trouble, past and future romances, "
            "fights, laughs, tears and surprises as they learn what it "
            "really means to be a friend.</p>"
        )
        assert response.status_code == 200
        assert response.text == expected_response

    def test_search_nonexistent_program(self):
        response = send_correct_message("123456")
        assert response.status_code == 200
        assert response.text == TvProgramBotErrorMessages.NOT_FOUND.value

    def test_search_program_without_full_info(self):
        response = send_correct_message("friend")
        assert response.status_code == 200
        assert response.text == TvProgramBotErrorMessages.NO_FULL_INFO.value

    def test_get_incorrect_message(self):
        response = send_incorrect_message_without_text()
        assert response.status_code == 200
        assert response.text == TvProgramBotErrorMessages.NO_TEXT.value
