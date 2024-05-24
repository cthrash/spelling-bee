import os
import sys
from typing import Iterable


def _filter(istream: Iterable[str], ostream):
    for rawword in istream:
        word = rawword.strip()
        if word[0].isupper():
            continue
        if len(word) < 4:
            continue
        key = set(list(word))
        if not 1 < len(key) <= 7:
            continue
        if "s" in key:
            continue
        if not all(["a" <= c <= "z" for c in key]):
            continue
        ostream.write(f"{word}\n")


def filter():
    """Filter word list suitable for Spelling Bee by excluding:
      - proper nouns,
      - words with any punctuation
      - words that include the letter 's'
      - words that include accented characters
      - words shorter than 4 letters long,
      - words containing more than 7 unique letters
      - words containing at least two unique letters (aaaa, etc.)

    Proper nouns are obviously not excluded, nor are swear words, so the
    resulting list will likely differ from actual game word list.

    Reads from stdin, writes to stdout.  Invoke like this:
      poetry run filter < count_1w.txt | head -100000 > words.txt
    """
    try:
        _filter(sys.stdin, sys.stdout)
        sys.stdout.flush()
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)  # Python exits with error code 1 on EPIPE
