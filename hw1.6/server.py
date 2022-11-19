import argparse
import json
import pathlib
import socket
import uuid
from datetime import datetime, timedelta
from json import JSONEncoder
from queue import Queue


class Task:
    def __init__(self, length, data):
        self.id = str(uuid.uuid4())
        self.length = length
        self.data = data
        self.getting_time = None


class TaskQueue(Queue):
    def __init__(self, timeout):
        super().__init__()
        self.timedelta = timedelta(seconds=timeout)
        self.tasks = dict()

    def put(self, task, **kwargs):
        self.queue.append(task)
        self.tasks[task.id] = task

    def get(self, **kwargs):
        for task in self.queue:
            if (
                task.getting_time is None
                or datetime.now() - task.getting_time >= self.timedelta
            ):
                task.getting_time = datetime.now()
                return task
        return None


class TaskQueueEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class TaskQueueServer:
    def __init__(self, ip, port, path, timeout):
        self.sock = socket.socket()
        self.ip = ip
        self.port = port
        self.path = path
        self.timeout = timeout
        self.queues = dict()

    def add_task_in_queue(self, queue_name, task, connection):
        if self.is_queue_exists(queue_name):
            self.queues[queue_name].put(task)
        else:
            self.queues[queue_name] = TaskQueue(self.timeout)
            self.queues[queue_name].put(task)
        self.queues[queue_name].tasks[task.id] = task
        connection.send(str.encode(task.id))

    def get_task_from_queue(self, queue_name, connection):
        if self.is_queue_exists(queue_name):
            task = self.queues[queue_name].get()
            if task:
                response = f"{task.id} {task.length} {task.data}"
                connection.send(str.encode(response))
            else:
                connection.send(str.encode("NONE"))
        else:
            connection.send(str.encode("ERROR"))

    def ack_task(self, queue_name, id, connection):
        if self.is_queue_exists(queue_name):
            queue = self.queues[queue_name]
            if id in queue.tasks.keys():
                task = queue.tasks[id]
                if task.getting_time is not None:
                    queue.tasks.pop(id)
                    queue.queue.remove(task)
                    connection.send(str.encode("YES"))
                else:
                    connection.send(str.encode("NO"))
            else:
                connection.send(str.encode("NO"))
        else:
            connection.send(str.encode("ERROR"))

    def check_is_task_in_queue(self, queue_name, id, connection):
        if self.is_queue_exists(queue_name):
            if id in self.queues[queue_name].tasks.keys():
                connection.send(str.encode("YES"))
            else:
                connection.send(str.encode("NO"))
        else:
            connection.send(str.encode("ERROR"))

    def save(self, queue_name, path, connection):
        if self.is_queue_exists(queue_name):
            path = pathlib.Path(path) / queue_name
            with path.open("w", encoding="utf-8") as f:
                f.write(json.dumps(self.queues[queue_name].tasks, cls=TaskQueueEncoder))
            with pathlib.Path("meta_info").open("w", encoding="utf-8") as f:
                f.write(f"{queue_name} {path}")
            connection.send(str.encode("OK"))
        else:
            connection.send(str.encode("ERROR"))

    def is_queue_exists(self, queue_name):
        return queue_name in self.queues.keys()

    def run(self):
        path_meta = pathlib.Path("meta_info")
        with path_meta.open("r", encoding="utf-8") as meta_file:
            for line in meta_file:
                queue_name, path = line.split(" ")
                filepath = pathlib.Path(path)
                with filepath.open("r", encoding="utf-8") as file:
                    self.queues[queue_name] = TaskQueue(self.timeout)
                    self.queues[queue_name].tasks = json.load(file)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        while True:
            connection, address = self.sock.accept()
            data = connection.recv(1048576)
            if not data:
                continue
            command = data.decode("utf-8").split(" ")
            type_command = command[0]
            queue_name = command[1]
            # todo тут пригодился бы паттерн-матчинг,
            #  но я все еще сижу на питоне 3.9...
            if type_command == "ADD":
                if len(command) < 4:
                    connection.send(str.encode("ERROR"))
                self.add_task_in_queue(
                    queue_name, Task(command[2], command[3]), connection
                )
            elif type_command == "GET":
                self.get_task_from_queue(queue_name, connection)
            elif type_command == "ACK":
                if len(command) < 3:
                    connection.send(str.encode("ERROR"))
                self.ack_task(queue_name, command[2], connection)
            elif type_command == "IN":
                if len(command) < 3:
                    connection.send(str.encode("ERROR"))
                self.check_is_task_in_queue(queue_name, command[2], connection)
            elif type_command == "SAVE":
                if len(command) < 3:
                    connection.send(str.encode("ERROR"))
                self.save(queue_name, command[2], connection)
            else:
                connection.send(str.encode("ERROR"))
            connection.close()


def parse_args():
    parser = argparse.ArgumentParser(
        description="This is a simple task queue server with custom protocol"
    )
    parser.add_argument(
        "-p", action="store", dest="port", type=int, default=5555, help="Port"
    )
    parser.add_argument(
        "-i",
        action="store",
        dest="ip",
        type=str,
        default="127.0.0.1",
        help="Server ip adress",
    )
    parser.add_argument(
        "-c",
        action="store",
        dest="path",
        type=str,
        default="./",
        help="Server checkpoints dir",
    )
    parser.add_argument(
        "-t",
        action="store",
        dest="timeout",
        type=int,
        default=300,
        help="Task maximum GET timeout in seconds",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    server = TaskQueueServer(**args.__dict__)
    server.run()
