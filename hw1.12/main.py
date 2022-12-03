import asyncio
import pathlib
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor
from yaml import safe_load


class Daemon:
    def __init__(self, name: str):
        with open(f"configurations/conf_{name}.yml", "r") as file:
            data = safe_load(file)
            self.port = data["port"]
            self.directory = data["directory"]
            self.nodes = data["nodes"]
            self.save_file_from_other = data["save_file_from_other"]
            self.app = web.Application()
            self.app.add_routes([web.get("/{name}", self.get_file_content)])

    def run(self):
        web.run_app(self.app, host="localhost", port=self.port)

    async def get_file_content(self, request: web.Request):
        filename = str(request.match_info.get("name"))
        file_content = await read_file(self.directory, filename)
        if file_content:
            return web.Response(text=str(file_content))
        else:
            tasks = []
            for node in self.nodes:
                node_daemon = Daemon(node)
                function = read_file(node_daemon.directory, filename)
                task = asyncio.create_task(function)
                tasks.append(task)
            results = list(filter(lambda x: x, await asyncio.gather(*tasks)))
            if results:
                file_content = str(results[0])
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
    a.run()


if __name__ == "__main__":
    main()
