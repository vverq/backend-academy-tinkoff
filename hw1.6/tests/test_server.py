import unittest
from unittest import TestCase

import time
import socket

import subprocess


class ServerBaseTest(TestCase):
    def setUp(self):
        self.server = subprocess.Popen(["python3", "server.py"])
        # даем серверу время на запуск
        time.sleep(1)

    def tearDown(self):
        self.server.terminate()
        self.server.wait()

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 5555))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_base_scenario(self):
        task_id = self.send(b"ADD 1 5 12345")
        self.assertEqual(b"YES", self.send(b"IN 1 " + task_id))
        self.assertEqual(task_id + b" 5 12345", self.send(b"GET 1"))
        self.assertEqual(b"YES", self.send(b"IN 1 " + task_id))
        self.assertEqual(b"YES", self.send(b"ACK 1 " + task_id))
        self.assertEqual(b"NO", self.send(b"ACK 1 " + task_id))
        self.assertEqual(b"NO", self.send(b"IN 1 " + task_id))

    def test_two_tasks(self):
        first_task_id = self.send(b"ADD 1 5 12345")
        second_task_id = self.send(b"ADD 1 5 12345")
        self.assertEqual(b"YES", self.send(b"IN 1 " + first_task_id))
        self.assertEqual(b"YES", self.send(b"IN 1 " + second_task_id))

        self.assertEqual(first_task_id + b" 5 12345", self.send(b"GET 1"))
        self.assertEqual(b"YES", self.send(b"IN 1 " + first_task_id))
        self.assertEqual(b"YES", self.send(b"IN 1 " + second_task_id))
        self.assertEqual(second_task_id + b" 5 12345", self.send(b"GET 1"))

        self.assertEqual(b"YES", self.send(b"ACK 1 " + second_task_id))
        self.assertEqual(b"NO", self.send(b"ACK 1 " + second_task_id))

    def test_long_input(self):
        data = "12345" * 1000
        data = "{} {}".format(len(data), data)
        data = data.encode("utf")
        task_id = self.send(b"ADD 1 " + data)
        self.assertEqual(b"YES", self.send(b"IN 1 " + task_id))
        self.assertEqual(task_id + b" " + data, self.send(b"GET 1"))

    def test_wrong_command(self):
        self.assertEqual(b"ERROR", self.send(b"ADDD 1 5 12345"))

    def test_add_tasks_to_different_queues(self):
        first_task_id = self.send(b"ADD 1 5 12345")
        second_task_id = self.send(b"ADD 2 5 12345")
        self.assertEqual(b"YES", self.send(b"IN 1 " + first_task_id))
        self.assertEqual(b"NO", self.send(b"IN 2 " + first_task_id))
        self.assertEqual(b"YES", self.send(b"IN 2 " + second_task_id))
        self.assertEqual(b"NO", self.send(b"IN 1 " + second_task_id))

    def test_get_empty_queue(self):
        self.assertEqual(b"ERROR", self.send(b"GET 1"))

    def test_ack_invalid_task(self):
        self.send(b"ADD 1 5 12345")
        self.assertEqual(b"NO", self.send(b"ACK 1 100500"))

    def test_get_tasks_in_right_order(self):
        first_task_id = self.send(b"ADD 1 5 12345")
        second_task_id = self.send(b"ADD 1 5 12345")
        third_task_id = self.send(b"ADD 1 5 12345")
        self.assertEqual(first_task_id + b" 5 12345", self.send(b"GET 1"))
        self.assertEqual(second_task_id + b" 5 12345", self.send(b"GET 1"))
        self.assertEqual(third_task_id + b" 5 12345", self.send(b"GET 1"))

    def test_all_tasks_get(self):
        first_task_id = self.send(b"ADD 1 5 12345")
        second_task_id = self.send(b"ADD 1 5 12345")
        self.assertEqual(first_task_id + b" 5 12345", self.send(b"GET 1"))
        self.assertEqual(second_task_id + b" 5 12345", self.send(b"GET 1"))
        self.assertEqual(b"NONE", self.send(b"GET 1"))


if __name__ == "__main__":
    unittest.main()
