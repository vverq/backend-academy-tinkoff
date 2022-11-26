from abc import ABC, abstractmethod
from urllib import request
import bs4
import re


class Strategy(ABC):
    @abstractmethod
    def parse(self, html: str) -> str:
        pass


class Parser:
    strategy: Strategy

    def __init__(self, strategy: Strategy, url: str) -> None:
        self.strategy = strategy
        self.html = request.urlopen(url).read().decode("utf8")

    def get_title(self) -> str:
        return self.strategy.parse(self.html)


class StrategyYouTube(Strategy):
    def parse(self, html: str) -> str:
        parser = bs4.BeautifulSoup(html, "html.parser")
        tag = parser.find("title")
        if tag:
            title = re.search("(.+) - YouTube", tag.text)
            return title.group(1) if title else ""
        return ""


class StrategyYandexMusic(Strategy):
    def parse(self, html: str) -> str:
        parser = bs4.BeautifulSoup(html, "html.parser")
        tag = parser.find("title")
        if tag:
            title = re.search("(.+) слушать онлайн", tag.text)
            return title.group(1) if title else ""
        return ""


class StrategyHabr(Strategy):
    def parse(self, html: str) -> str:
        parser = bs4.BeautifulSoup(html, "html.parser")
        tag = parser.find("title")
        if tag:
            title = re.search("(.+) / Хабр", tag.text)
            return title.group(1) if title else ""
        return ""


if __name__ == "__main__":
    yandex_url = "https://music.yandex.ru/album/13707793/track/60292250"
    youtube_url = "https://www.youtube.com/watch?v=90RLzVUuXe4"
    habr_url = "https://habr.com/ru/post/280238/"

    youtube_parser = Parser(StrategyYouTube(), youtube_url)
    yandex_music_parser = Parser(StrategyYandexMusic(), yandex_url)
    habr_parser = Parser(StrategyHabr(), habr_url)

    print(youtube_parser.get_title())
    print(yandex_music_parser.get_title())
    print(habr_parser.get_title())
