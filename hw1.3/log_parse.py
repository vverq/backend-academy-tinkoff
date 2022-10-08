import re
import datetime
from collections import Counter, defaultdict

PATTERN = '\[(\d{2}\/\w{3}\/\d{4} \d{2}:\d{2}:\d{2})\] \"' \
            '(GET|POST|PUT|OPTIONS|HEAD|PATCH|DELETE|TRACE|CONNECT) ' \
            '(?:https?:\/\/)?(www\.)?([^.\/]+(?:\.[^.\/]+)+(?:\/[\w\d-]+)*' \
            '\/)([\w\.-]*\.\w+)*(#.+|\?.+=.+&?)? (\w+\/?\d+\.?\d*)\" ' \
            '(\d{3}) (\d+)'
LOG_FILENAME = 'log.log'
DATETIME_PATTERN = '%d/%b/%Y %H:%M:%S'
TOP_COUNT = 5


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
) -> list:
    urls = []
    response_times_by_urls = defaultdict(list)
    with open(LOG_FILENAME, 'r', encoding='utf-8') as log_file:
        for log in log_file:
            parsed_log = parse_format(log)
            if parsed_log:
                url = parsed_log['url']
                log_datetime = parsed_log['date']
                filename = parsed_log['file']
                if (ignore_files and filename) or (url in ignore_urls):
                    continue
                if start_at:
                    start_datetime = datetime.datetime.strptime(
                        start_at, DATETIME_PATTERN)
                    if start_datetime > log_datetime:
                        continue
                if stop_at:
                    stop_datetime = datetime.datetime.strptime(
                        stop_at, DATETIME_PATTERN)
                    if stop_datetime < log_datetime:
                        continue
                if request_type and \
                        parsed_log['request_type'] != request_type:
                    continue
                if not ignore_www and parsed_log['www']:
                    url = parsed_log['www'] + url
                if filename:
                    url += filename
                urls.append(url)
                response_times_by_urls[url].append(
                    parsed_log['response_time'])

    if slow_queries:
        for key in response_times_by_urls.keys():
            current_times = response_times_by_urls[key]
            average_time = int(sum(current_times) / len(current_times))
            response_times_by_urls[key] = average_time
        top_urls = Counter(response_times_by_urls).most_common(TOP_COUNT)
    else:
        top_urls = Counter(urls).most_common(TOP_COUNT)
    return get_values_for_top_urls(top_urls)


def get_values_for_top_urls(top_urls: list[tuple]) -> list:
    return [value for url, value in top_urls]


def parse_format(log: str) -> dict:
    parsed_log = {}
    match = re.match(PATTERN, log)
    if match:
        parsed_log['date'] = datetime.datetime.strptime(
            match.group(1), DATETIME_PATTERN)
        parsed_log['request_type'] = match.group(2)
        parsed_log['www'] = match.group(3)
        parsed_log['url'] = match.group(4)
        parsed_log['file'] = match.group(5)
        parsed_log['file_extension'] = match.group(6)
        parsed_log['protocol'] = match.group(7)
        parsed_log['response_code'] = match.group(8)
        parsed_log['response_time'] = int(match.group(9))
    return parsed_log
