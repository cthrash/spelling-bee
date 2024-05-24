from io import StringIO
import pytest

from spelling_bee.filter import _filter


def test_filter():
    istream = StringIO("lion\ntiger")
    ostream = StringIO()
    _filter(istream, ostream)
    ostream.seek(0)
    assert ["lion\n", "tiger\n"] == ostream.readlines()


@pytest.mark.parametrize(
    "excluded",
    [
        "cat",  # too short
        "sass",  # contains one or more s
        "pokémon",  # non-alphabet
        "Batman",  # Proper noun (captialized)
        "zzzz",  # Single character
        "abcdefgh",  # More than seven unique letters
    ],
)
def test_exclusion(excluded):
    istream = StringIO("\n".join(["good", excluded, "fine"]))
    ostream = StringIO()
    _filter(istream, ostream)
    ostream.seek(0)
    assert ["good\n", "fine\n"] == ostream.readlines()
