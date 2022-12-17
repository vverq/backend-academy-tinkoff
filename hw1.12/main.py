import asyncio
import multiprocessing
import pathlib
import aiohttp.web
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor
from yaml import safe_load


class Daemon:
    def __init__(self, name: str):
        path = pathlib.Path(f"configurations/conf_{name}.yml")
        with path.open("r") as file:
            data = safe_load(file)
            self.port = data["port"]
            self.directory = data["directory"]
            self.nodes = dict(data["nodes"])
            self.save_file_from_other = data["save_file_from_other"]
            self.app = web.Application()
            self.app.add_routes([web.get("/{name}", self.get_file_content)])
            self.app.add_routes(
                [web.get("/other_nodes_files/{name}", self.get_file_by_other)]
            )

    def run(self):
        web.run_app(self.app, host="localhost", port=self.port)

    async def get_file_by_other(self, request: web.Request):
        filename = str(request.match_info.get("name"))
        file_content = await read_file(self.directory, filename)
        if file_content:
            return web.Response(text=str(file_content))
        return web.Response()

    async def get_file_content(self, request: web.Request):
        filename = str(request.match_info.get("name"))
        file_content = await read_file(self.directory, filename)
        if file_content:
            return web.Response(text=str(file_content))
        else:
            for _, node in self.nodes.items():
                async with aiohttp.ClientSession(
                    f'http://{node["host"]}:{node["port"]}'
                ) as session:
                    url = f"/other_nodes_files/{filename}"
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            file_content = await resp.content.read()
                            break
            if file_content:
                file_content = file_content.decode()
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
