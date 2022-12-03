import multiprocessing
import time
import pathlib
import requests
from main import Daemon


a = Daemon("a")
b = Daemon("b")
c = Daemon("c")

process_a = multiprocessing.Process(target=a.run)
process_b = multiprocessing.Process(target=b.run)
process_c = multiprocessing.Process(target=c.run)

path_a = pathlib.Path(a.directory).joinpath("file_a")
path_b = pathlib.Path(a.directory).joinpath("file_b")
path_c = pathlib.Path(a.directory).joinpath("file_c")

file_content_a = "Good as dold"
file_content_b = "Better late than never"
file_content_c = "As fit as a fiddle"
text_response_for_nonexisting_file = "Ничего не нашли"


def setup():
    with path_a.open("w", encoding="utf-8") as file:
        file.write(file_content_a)
    with path_b.open("w", encoding="utf-8") as file:
        file.write(file_content_b)
    with path_c.open("w", encoding="utf-8") as file:
        file.write(file_content_c)
    process_a.start()
    process_b.start()
    process_c.start()
    time.sleep(3)  # даем время на запуск


def teardown():
    path_a.unlink()
    path_b.unlink()
    path_c.unlink()
    process_a.terminate()
    process_b.terminate()
    process_c.terminate()


def test_search_existing_file_in_current_dir():
    response = requests.get(f"http://localhost:{a.port}/file_a")
    assert response.status_code == 200
    assert response.text == file_content_a


def test_search_existing_file_in_other_node_dir():
    response = requests.get(f"http://localhost:{a.port}/file_b")
    assert response.status_code == 200
    assert response.text == file_content_b


def test_search_nonexisting_file():
    response = requests.get(f"http://localhost:{a.port}/file_x")
    assert response.status_code == 200
    assert response.text == text_response_for_nonexisting_file


def test_save_file_in_current_dir():
    response = requests.get(f"http://localhost:{b.port}/file_a")
    assert response.status_code == 200
    assert response.text == file_content_a
    assert pathlib.Path(b.directory).joinpath("file_a").exists()


def test_dont_save_file_if_not_flag():
    response = requests.get(f"http://localhost:{c.port}/file_a")
    assert response.status_code == 200
    assert response.text == file_content_a
    assert not pathlib.Path(c.directory).joinpath("file_a").exists()
