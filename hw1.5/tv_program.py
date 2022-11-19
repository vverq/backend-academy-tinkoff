import requests
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from cachetools import TTLCache, cached
from datetime import datetime, timedelta
from collections import defaultdict

URL = "https://api.tvmaze.com/singlesearch/shows?"


class TvProgram(BaseModel):
    name: str = Field(..., min_length=1)
    network_name: str = Field(..., min_length=1)
    network_country_name: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)


class TvProgramCache(TTLCache):
    def __init__(self, maxsize, ttl):
        super().__init__(maxsize, ttl)
        self.path = Path("cached_search_results")
        self.time_latest_search = defaultdict(datetime.now)

    def __getitem__(self, key: str, **kwargs):
        file = Path(self.path / key[0])
        if file.is_file():
            TvProgram.parse_file(file)
        return self.__missing__(key)

    def __setitem__(self, key: str, value: TvProgram, **kwargs):
        program_name = key[0]
        if datetime.now() >= self.time_latest_search[program_name] + self.ttl:
            self.__delitem__(key)
        self.time_latest_search[program_name] = datetime.now()
        new_file_path = self.path / program_name
        Path(new_file_path).write_text(value.json())

    def __delitem__(self, key: str, **kwargs):
        Path(self.path / key[0]).unlink()


cache = TvProgramCache(30, timedelta(minutes=5))


@cached(cache=cache)
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
    try:
        response_json = response.json()
    except AttributeError:
        raise AttributeError("Ожидали, что в ответ придет json")
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
