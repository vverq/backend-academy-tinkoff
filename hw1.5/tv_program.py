import requests
import sys
import os
import pathlib
from pydantic import BaseModel, Field
from cachetools import TTLCache, cached
from datetime import datetime, timedelta

URL = "https://api.tvmaze.com/singlesearch/shows?"


class TvProgram(BaseModel):
    name: str = Field(..., min_length=1)
    network_name: str = Field(..., min_length=1)
    network_country_name: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)


class TvProgramCache(TTLCache):
    def __init__(self, maxsize, ttl, time_start):
        super().__init__(maxsize, ttl)
        self.time_start = time_start
        self.path = pathlib.Path("cached_search_results")

    def __getitem__(self, key: str, **kwargs):
        for cached_result_file in self.path.iterdir():
            if cached_result_file.name == key[0]:
                TvProgram.parse_file(cached_result_file)
        return self.__missing__(key)

    def __setitem__(self, key: str, value: TvProgram, **kwargs):
        if datetime.now() >= self.time_start + self.ttl:
            self.__delitem__(key)
        new_file_path = self.path / key[0]
        with new_file_path.open("w", encoding="utf-8") as file:
            file.write(value.json())

    def __delitem__(self, key: str, **kwargs):
        # почему-то если использую self.path.unlink(filename),
        # то падает PermissionError и я не смогла это побороть,
        # поэтому стала использовать привычный os.remove и с ним ок
        os.remove(self.path / key[0])


CACHE = TvProgramCache(30, timedelta(minutes=5), datetime.now())


@cached(cache=CACHE)
def search(program_name: str):
    params = {"q": program_name.lower()}
    try:
        response = requests.get(url=URL, params=params)
        response.raise_for_status()
    except requests.ConnectionError as error:
        print("Ошибка соединения, что-то пошло не так")
        raise SystemExit(error)
    except requests.HTTPError as error:
        print(f"Пришел {response.status_code}, скорее всего ничего не нашли")
        raise SystemExit(error)
    except requests.Timeout as error:
        print("Превышено время ожидание ответа")
        raise SystemExit(error)
    except requests.RequestException as error:
        raise SystemExit(error)
    response_json = response.json()
    try:
        tv_program = TvProgram(
            name=response_json["name"],
            network_name=response_json["network"]["name"],
            network_country_name=response_json["network"]["country"]["name"],
            summary=response_json["summary"],
        )
    except KeyError or TypeError:
        raise ValueError(
            "В ответе не хватает как минимум одного из полей: "
            "name, network name, network country name, summary"
        )

    print(f"Name: {tv_program.name}")
    print(f"Network Name: {tv_program.network_name}")
    print(f"Network Country Name: {tv_program.network_country_name}")
    print(f"Summary: {tv_program.summary}")

    return tv_program


def main():
    program_name = " ".join(sys.argv[1:])
    search(program_name)


if __name__ == "__main__" or __name__ == "tv_program":
    main()
