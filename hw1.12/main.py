import asyncio
import multiprocessing
import pathlib
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor
from yaml import safe_load
import requests


class Daemon:
    def __init__(self, name: str):
        path = pathlib.Path(f"configurations/conf_{name}.yml")
        with path.open("r") as file:
            data = safe_load(file)
            self.port = data["port"]
            self.directory = data["directory"]
            self.nodes = data["nodes"]
            self.save_file_from_other = data["save_file_from_other"]
            self.app = web.Application()
            self.app.add_routes([web.get("/{name}", self.get_file_content)])
            self.app.add_routes([web.get("/other_nodes_files/{name}", self.get_file_content_by_other_node)])

    def run(self):
        web.run_app(self.app, host="localhost", port=self.port)

    async def get_file_content_by_other_node(self, request: web.Request):
        filename = str(request.match_info.get("name"))
        file_content = await read_file(self.directory, filename)
        if file_content:
            return web.Response(text=str(file_content))

    async def get_file_content(self, request: web.Request):
        filename = str(request.match_info.get("name"))
        file_content = await read_file(self.directory, filename)
        if file_content:
            return web.Response(text=str(file_content))
        else:
            for node in self.nodes:
                file_content = requests.get(f'{node["host"]}:{node["port"]}/other_nodes_files/{filename}')
                if file_content:
                    break
            if file_content:
                if self.save_file_from_other:
                    await write_file(self.directory, filename, file_content)
                return web.Response(text=file_content)
            return web.Response(text="Ничего не нашли")


async def read_file(directory: str, filename: str):
    io_pool_exc = ThreadPoolExecutor()
    loop = asyncio.get_event_loop()
    path = pathlib.Path(directory).joinpath(filename)
    if path.is_file():
        with path.open("r", encoding="utf-8") as file:
            return await loop.run_in_executor(io_pool_exc, file.read)


async def write_file(directory: str, filename: str, content: str):
    io_pool_exc = ThreadPoolExecutor()
    loop = asyncio.get_event_loop()
    path = pathlib.Path(directory).joinpath(filename)
    with path.open("w", encoding="utf-8") as file:
        return await loop.run_in_executor(io_pool_exc, file.write, content)


def main():
    a = Daemon("a")
    b = Daemon("b")
    c = Daemon("c")

    process_a = multiprocessing.Process(target=a.run)
    process_b = multiprocessing.Process(target=b.run)
    process_c = multiprocessing.Process(target=c.run)

    process_a.start()
    process_b.start()
    process_c.start()


if __name__ == "__main__":
    main()
