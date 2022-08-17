import re
from dataclasses import dataclass
from typing import Any, Literal, Tuple, Union

from num2words import num2words


def find_year(string: str) -> int:
    """
    Parse string from start, until last instance of a year between .1000-2999. found, keep last instance of year
    https://regex101.com/r/r5TwxJ/1

    Args:
        string (str): Title.Of.The.Movie.YEAR.Source.Codec-GROUP

    Returns:
        str: YEAR
    """
    # from start of string until number between 1000-2999 ending with. found
    _year = re.findall("^.*\.([1-2][0-9]{3})\.", string)
    if len(_year) > 0:
        year = _year[0]
        return int(year)
    return 0


def find_title_by_year(string: str) -> str:
    """
    Parse string from start, until last instance of a year between .1000-2999. found, keep everything before last instance of .year
    https://regex101.com/r/FKUpY0/1

    Args:
        string (str): Title.Of.The.Movie.YEAR.Source.Codec-GROUP

    Returns:
        str: Title.Of.The.Movie
    """
    _title = re.findall("^(.*)\.[1-2][0-9]{3}\.", string)
    if len(_title) > 0:
        title: str = _title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_title_by_show(string: str) -> str:
    """
    Parse string from start, until last instance of .s00e00. found, keep everything before .season
    https://regex101.com/r/41OZE5/1

    Args:
        string (str): Title.Of.The.Show.s01e01.Source.Codec-GROUP

    Returns:
        str: Title.Of.The.Show
    """
    _title = re.findall("^(.*)\.[s]\d*[e]\d*\.", string)
    if len(_title) > 0:
        title: str = _title[0]
        title = title.replace(".", " ")
        return title
    return "N/A"


def find_season_episode(string: str) -> str:
    """
    Parse string from start, until last instance of .s00e00. found, keep .s00e00.
    https://regex101.com/r/8Nwlr6/1

    Args:
        string (str): Title.Of.The.Show.s01e01.Source.Codec-GROUP

    Returns:
        str: s01e01
    """
    _se = re.findall("\.([s]\d*[e]\d*)\.", string)
    if len(_se) > 0:
        se: str = _se[0]
        return se
    return "N/A"


def find_ordinal(string: str, lang_abbr_iso6391: str) -> tuple[Any | str, str, str, str, bool]:
    """
    Convert numbers into ordinal strings, 01 = First, 02 = Second...

    Args:
        string (str): s01e01
        lang_abbr (str): abbreviation of ordinal language

    Returns:
        str | int: _description_
    """
    if string == "N/A":
        season, season_ordinal, episode, episode_ordinal = "N/A", "N/A", "N/A", "N/A"
        show_bool = False

        return season, season_ordinal, episode, episode_ordinal, show_bool
    else:
        season, episode = string.replace("s", "").replace("e", " ").split(" ")
        season_ordinal = num2words(int(season), lang=lang_abbr_iso6391, to="ordinal")
        episode_ordinal = num2words(int(episode), lang=lang_abbr_iso6391, to="ordinal")
        show_bool = True
        return season, season_ordinal, episode, episode_ordinal, show_bool


def find_group(string: str) -> str:
    group = string.rsplit("-", 1)[-1]
    return group


@dataclass(frozen=True, order=True)
class SearchParameters:
    url_subscene: str
    url_opensubtitles: str
    title: str
    year: int
    season: str
    season_ordinal: str
    episode: str
    episode_ordinal: str
    show_bool: bool
    release: str
    group: str
    file_hash: str


def get_parameters(filename: str, file_hash: str, language: str, lang_abbr_iso6391: str) -> SearchParameters:
    """
    Parse filename and get parameters for searching on subscene and opensubtitles
    Uses regex expressions to find the parameters

    Args:
        file_name (str): name of the file
        file_hash (str): hash of the file
        lang_abbr (str): language abbreviation for ordinal numbers

    Returns:
        SearchParameters: title, year, season, season_ordinal, episode, episode_ordinal, tv_series, release, group
    """
    filename = filename.lower()
    lang_abbr_iso6392b = language[:3].lower()

    year = find_year(filename)

    season_episode = find_season_episode(filename)
    season, season_ordinal, episode, episode_ordinal, show_bool = find_ordinal(season_episode, lang_abbr_iso6391)

    if year > 0:
        title = find_title_by_year(filename)
    elif show_bool:
        title = find_title_by_show(filename)
        title = f"{title} - {season_ordinal} season"
    else:
        title = filename.rsplit("-", 1)[0]

    group = find_group(filename)
    subscene = "https://subscene.com/subtitles/searchbytitle?query="
    opensubtitles = f"https://www.opensubtitles.org/en/search/sublanguageid-{lang_abbr_iso6392b}/moviename-"
    url_subscene = f"{subscene}{title}".replace(" ", "%20")
    url_opensubtitles = f"{opensubtitles}{file_hash}"

    parameters = SearchParameters(
        url_subscene,
        url_opensubtitles,
        title,
        year,
        season,
        season_ordinal,
        episode,
        episode_ordinal,
        show_bool,
        filename,
        group,
        file_hash,
    )
    return parameters