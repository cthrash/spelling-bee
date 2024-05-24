import os
import pytest

from spelling_bee import __version__
from spelling_bee.bee import Bee

TEST_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def min_file_name():
    """The minimum dictionary, one pangram, one word"""
    return os.path.join(TEST_DIR, "jukebox.txt")


@pytest.fixture
def min_list():
    """The minimum dictionary, one pangram, one word"""
    return ["jukebox"]


def test_version():
    assert __version__ == "0.1.0"


def _assert_min(bee: Bee):
    assert len(bee.words_dict) == 1
    assert ["jukebox"] == list(bee.words_dict.keys())

    keys = ["jukebox", "ujkebox", "kjuebox", "ejukbox", "bjukeox", "ojukebx", "xjukebo"]

    for key in keys:
        words = bee.list_words(key)
        assert words == (["jukebox"], [])

    assert bee.list_words("abcdefgh") == ([], [])

    scores = bee.score_tree()

    assert len(scores) == 7
    for i in range(7):
        assert scores[i].score == 14
        assert scores[i].pangrams == 1
        assert scores[i].words == 1

    def keyword(key: str) -> str:
        return key[0] + ":" + "".join(sorted(list(key[1:])))

    assert sorted([keyword(k) for k in keys]) == sorted([score.key for score in scores])


def test_ctor_file(min_file_name):
    bee = Bee.from_file(min_file_name)
    _assert_min(bee)


def test_ctor_list(min_list):
    bee = Bee.from_list(min_list)
    _assert_min(bee)


def test_ctor_stock():
    bee = Bee()
    assert ["jukebox"], [] == bee.list_words("jukebox")


def test_count_words():
    bee = Bee.from_list(['azimuth', 'imam', 'maim', 'mitt'])
    counts = bee.count_words()
    assert 7 == counts['azimuth']
    assert all([3 == counts[word] for word in ['imam', 'maim', 'mitt']])
    assert 4 == len(counts)
