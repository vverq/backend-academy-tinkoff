from main import Parser, StrategyYouTube, StrategyYandexMusic, StrategyHabr


def test_youtube_strategy():
    url = "https://www.youtube.com/watch?v=90RLzVUuXe4"
    youtube_parser = Parser(StrategyYouTube(), url)
    assert (
        youtube_parser.get_title() == "David Guetta & Bebe Rexha - I'm "
        "Good (Blue) [Official Music Video]"
    )


def test_yandex_music_strategy():
    url = "https://music.yandex.ru/album/13707793/track/60292250"
    youtube_parser = Parser(StrategyYandexMusic(), url)
    assert youtube_parser.get_title() == "Blinding Lights The Weeknd"


def test_habr_strategy():
    url = "https://habr.com/ru/post/280238/"
    youtube_parser = Parser(StrategyHabr(), url)
    assert youtube_parser.get_title() == "Web Scraping с помощью python"
