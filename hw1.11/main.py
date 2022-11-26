from abc import ABC, abstractmethod
from urllib import request
import bs4
import re


class Strategy(ABC):
    def __init__(self, url):
        html = request.urlopen(url).read().decode("utf8")
        parser = bs4.BeautifulSoup(html, "html.parser")
        self.title = parser.find("title").text

    @abstractmethod
    def parse(self) -> str:
        pass


class Parser:
    strategy: Strategy

    def __init__(self, strategy: Strategy) -> None:
        self.strategy = strategy

    def get_title(self) -> str:
        return self.strategy.parse()


class StrategyYouTube(Strategy):
    def parse(self) -> str:
        title = re.search("(.+) - YouTube", self.title)
        return title.group(1) if title else ""


class StrategyYandexMusic(Strategy):
    def parse(self) -> str:
        title = re.search("(.+) слушать онлайн на Яндекс Музыке", self.title)
        return title.group(1) if title else ""


class StrategyHabr(Strategy):
    def parse(self) -> str:
        title = re.search("(.+) / Хабр", self.title)
        return title.group(1) if title else ""


if __name__ == "__main__":
    yandex_url = "https://music.yandex.ru/album/13707793/track/60292250"
    youtube_url = "https://www.youtube.com/watch?v=90RLzVUuXe4"
    habr_url = "https://habr.com/ru/post/280238/"

    youtube_parser = Parser(StrategyYouTube(youtube_url))
    yandex_music_parser = Parser(StrategyYandexMusic(yandex_url))
    habr_parser = Parser(StrategyHabr(habr_url))

    print(youtube_parser.get_title())
    print(yandex_music_parser.get_title())
    print(habr_parser.get_title())
