import json
import os
import time
from enum import Enum

import requests
from pydantic import BaseModel, Field


class TvProgramModel(BaseModel):
    name: str = Field(..., min_length=1)
    network_name: str = Field(..., min_length=1)
    network_country: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1)


class TvProgramService:
    def __init__(self):
        self.url = "https://api.tvmaze.com/singlesearch/shows?"

    def search(self, program_name: str):
        params = {"q": program_name.lower()}
        try:
            response = requests.get(url=self.url, params=params)
            response.raise_for_status()
        except requests.ConnectionError as error:
            print("Ошибка соединения, что-то пошло не так")
            raise SystemExit(error)
        except requests.HTTPError as error:
            print(f"Пришел {response.status_code}, возможно ничего не нашли")
            raise SystemExit(error)
        except requests.Timeout as error:
            print("Превышено время ожидание ответа")
            raise SystemExit(error)
        except requests.RequestException as error:
            raise SystemExit(error)
        response_json = response.json()
        try:
            tv_program = TvProgramModel(
                name=response_json["name"],
                network_name=response_json["network"]["name"],
                network_country=response_json["network"]["country"]["name"],
                summary=response_json["summary"],
            )
        except KeyError or TypeError:
            raise ValueError(
                "В ответе не хватает как минимум одного из полей: "
                "name, network name, network country name, summary"
            )

        result = (
            f"Name: {tv_program.name}\n"
            f"Network Name: {tv_program.network_name}\n"
            f"Network Country Name: {tv_program.network_country}\n"
            f"Summary: {tv_program.summary}"
        )
        return result


class TvProgramBotErrorMessages(Enum):
    NOT_FOUND = "Не удалось найти телепрограмму"
    NO_FULL_INFO = "Не удалось получить полные сведения о телепрограмме"
    NO_TEXT = "Некорректное сообщение, отправьте текстовое сообщение"


tvProgramService = TvProgramService()


class TvProgramBot:
    def __init__(self, token: str):
        self.url = f"https://api.telegram.org/bot{token}"

    def send_message(self, chat_id: str, text: str):
        url = self.url + "/sendMessage"
        answer = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=answer)
        return response.json()

    def get_updates(self, last_update_id=None):
        url = self.url + "/getUpdates"
        new_url = url + f"?offset={last_update_id}" if last_update_id else url
        updates = json.loads(requests.get(new_url).content)
        return updates

    def process_updates(self, updates: dict):
        for update in updates:
            message = update["message"]
            if "text" in message.keys():
                text = message["text"]
                print(text)
                try:
                    result = tvProgramService.search(text)
                except SystemExit:
                    result = TvProgramBotErrorMessages.NOT_FOUND.value
                except ValueError:
                    result = TvProgramBotErrorMessages.NO_FULL_INFO.value
            else:
                result = TvProgramBotErrorMessages.NO_TEXT.value
            self.send_message(message["chat"]["id"], result)
            return result

    def start(self):
        last_update_id = None
        while True:
            updates = self.get_updates(last_update_id)
            if updates["ok"]:
                result = updates["result"]
                if result:
                    self.process_updates(result)
                    last_update_id = result[0]["update_id"] + 1
            time.sleep(3)


def main():
    bot = TvProgramBot("token_telegram_bot")
    bot.start()


if __name__ == "__main__":
    main()
