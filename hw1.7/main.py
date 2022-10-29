import os
from enum import Enum

import requests
from flask import Flask
from flask import request
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


class TvProgramBot:
    def __init__(self, token_name: str):
        self.token = os.getenv(token_name)
        self.url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, request: requests.Request, text="Wait..."):
        url = self.url + "/sendMessage"
        chat_id = request.json["message"]["chat"]["id"]
        answer = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=answer)
        return response.json()

    @staticmethod
    def get_message(request: requests.Request):
        message = request.json()["message"]
        if "text" in message.keys():
            return message["text"]
        return


app = Flask(__name__)
bot = TvProgramBot("token_telegram_bot")
tvProgramService = TvProgramService()


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        message = bot.get_message(request)
        if message:
            try:
                result = tvProgramService.search(message)
            except SystemExit:
                result = TvProgramBotErrorMessages.NOT_FOUND.value
            except ValueError:
                result = TvProgramBotErrorMessages.NO_FULL_INFO.value
        else:
            result = TvProgramBotErrorMessages.NO_TEXT.value
        bot.send_message(request, result)
        return result
    return {"ok": True}


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    main()
