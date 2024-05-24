from collections import defaultdict, deque
import os
import sys
from typing import Dict, List, TextIO, Tuple


def read_words(f: TextIO) -> List[str]:
    words: List[str] = []
    while rawword := f.readline():
        words.append(rawword.strip().lower())
    return words


class Node:
    def __init__(self, zero=ord("a")) -> None:
        self.zero: int = zero
        self.children: List["Node"] = None
        self.words: List[str] = []

    def ensure_child(self, letter) -> "Node":
        index = ord(letter) - self.zero
        if not self.children:
            self.children = [None] * (26 - (self.zero - ord("a")))
        child = self.children[index]
        if not self.children[index]:
            child = Node(ord(letter) + 1)
            self.children[index] = child
        return child

    def __repr__(self):
        letters = (
            [chr(i + self.zero) for i, v in enumerate(self.children) if v]
            if self.children
            else "None"
        )
        return f"<zero={chr(self.zero)} children={''.join(letters)} words={len(self.words)}>"


def compute_points(word: str) -> int:
    if len(word) == 4:
        return 1
    if len(word) < 7:
        return len(word)
    pangram = 7 == len(set(list(word)))
    return len(word) + (7 if pangram else 0)


def build_tree(words: List[str]):
    word_tree = Node()
    for word in words:
        key = set(list(word))
        if len(key) == 7:
            letters = sorted(key)
            node = word_tree
            for letter in letters:
                node = node.ensure_child(letter)
    return word_tree


def fill_tree(root: Node, words: List[str]):
    for word in words:
        freq = 0
        q = deque([(root, 0)])
        letter_ords = [ord(letter) for letter in sorted(set(list(word)))]
        while q:
            node, index = q.pop()
            if index == len(letter_ords):
                node.words.append(word)
            elif node.children:
                end = letter_ords[index] - node.zero
                for offset in range(end):
                    child = node.children[offset]
                    if child:
                        q.append((child, index))
                child = node.children[end]
                if child:
                    q.append((child, index + 1))


def prune_tree(node: Node) -> Node:
    if not node:
        return None
    if not node.children:
        return node if node.words else None

    node.children = [prune_tree(child) for child in node.children]
    return node if any(node.children) else None


def score_tree(root: Node, words: List[str]):
    points = {word: compute_points(word) for word in words}

    def _get_bitmask(word):
        bitmask = 0
        for word in words:
            for letter in word:
                bitmask |= 1 << (ord(letter) - ord("a"))
        return bitmask

    # bitmasks = {word:_get_bitmask(word) for word in words}
    word_letters = {word: set(list(word)) for word in words}
    pass

    def _score_tree(node: Node, history, results):
        if node.words:
            check_pangram = not node.children
            has_pangram = False
            history_dict = {letter: score for letter, score in history}
            for word in node.words:
                letters = word_letters[word]
                if check_pangram and not has_pangram:
                    has_pangram = len(letters) == 7
                for letter in history_dict:
                    if letter in letters:
                        history_dict[letter] += points[word]
            if check_pangram and not has_pangram:
                history = []
            else:
                history = [(letter, score) for letter, score in history_dict.items()]

        if not node.children:
            pattern = "".join([letter for letter, _ in history])
            for i, (letter, score) in enumerate(history):
                if score:
                    key = letter + ":" + pattern[:i] + pattern[i + 1 :]
                    results.append((score, key))
            pass
        else:
            for index, child in enumerate(node.children):
                if not child:
                    continue
                next_letter = chr(node.zero + index)
                _score_tree(child, history + [(next_letter, 0)], results)
        pass

    results = []
    _score_tree(root, [], results)

    return results


def list_words(word_tree: Node, key: str) -> List[str]:
    words = []
    center = key[0]
    steps = sorted(list(key.replace(":", "")))
    node = word_tree
    for letter in steps:
        for word in node.words:
            if center in word:
                words.append(word)
        node = node.children[ord(letter) - node.zero]
    for word in node.words:
        if center in word:
            words.append(word)
    return words


def show_stats(words: List[str]):
    print(f"Total words: {len(words)}")
    words_by_length = defaultdict(int)
    for word in words:
        words_by_length[len(word)] += 1
    print("Word count by length:")
    for word_len in sorted(words_by_length.keys()):
        print(f"\t{word_len:>2}: {words_by_length[word_len]}")


def _score(f: TextIO):
    """Compute the total Spelling Bee scores for a corpus.  T
      - words containing more than 7 unique letters

    Proper nouns are obviously not excluded, nor are swear words, so the
    resulting list will likely differ from actual game word list.

    Reads from stdin, writes to stdout.  Invoke like this, for example:
      poetry run filter < /etc/dictionaries-common/words > words.txt
    """

    # Read forward/reverse word-ID lookup tables
    words = read_words(f)

    # Compute the points of each word
    points = [compute_points(word) for word in words]

    # Create a tree for 7-letter set
    word_tree = build_tree(words)

    def _count(node):
        if not node.children:
            return 1
        return sum([_count(child) for child in node.children if child])

    combinations = _count(word_tree)
    print(f"Total 7-letter combinations: {combinations}")

    # Add each word to the tree
    fill_tree(word_tree, words)
    word_tree = prune_tree(word_tree)

    list_words(word_tree, "x:jukebo")
    scores = score_tree(word_tree, words)

    # show stats
    max_points = max(points)
    max_points_words = [
        word for word, point in zip(words, points) if point == max_points
    ]
    print(
        f"Maximum score word{'' if len(max_points_words)==1 else 's'} [{max_points}]:"
    )
    for word in sorted(max_points_words):
        print(word)
    print()


def score():
    _score(sys.stdin)


if __name__ == "__main__":
    input_filename = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "words.txt"
    )
    with open(input_filename, "rt") as f:
        _score(f)
