import json
import re
from datetime import datetime
from pathlib import Path

from requests_html import HTMLSession

from mjimdb.models.imdb import Movie, TopMovies

session = HTMLSession()
data = Path("data").joinpath("movies.json")


def write_json(path: Path, top: TopMovies):
    top.last_update = datetime.now()
    with open(path, "w", encoding="utf-8") as f:
        f.write(top.json(ensure_ascii=False, indent=4))


if not data.is_file():
    top = TopMovies(url="https://www.imdb.com/chart/top/")
    column_pattern = r"(\d+)\.\s(.*)\s\(\d{4}\)"
    res = session.get(top.url)
    columns = res.html.find("td.titleColumn")
    for col in columns:
        m = re.search(column_pattern, col.text)
        top.movies.append(
            Movie(
                rank=m.group(1),
                title_tw=m.group(2),
                url=col.absolute_links.pop().split("?")[0],
            )
        )
    write_json(data, top)
else:
    top = TopMovies.parse_file(data)


for movie in top.movies:
    if movie.presentation:
        continue
    res = session.get(movie.url)
    res.raise_for_status()
    try:
        movie.title = res.html.xpath(
            "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[1]/div[1]/div/div",
            first=True,
        ).text.split(": ")[1]
    except AttributeError:
        movie.title = movie.title_tw
        print(movie.rank)
    try:
        movie.presentation = res.html.xpath(
            "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[1]/p/span[3]",
            first=True,
        ).text
    except AttributeError:
        movie.presentation = res.html.xpath(
            "/html/body/div[2]/main/div/section[1]/section/div[3]/section/section/div[3]/div[2]/div[1]/div[1]/div[2]/span[3]",
            first=True,
        ).text

    write_json(data, top)
