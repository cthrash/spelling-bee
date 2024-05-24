from collections import defaultdict, deque, namedtuple
from typing import Dict, Iterable, List, Optional, Tuple
import os

from spelling_bee.node import Node


class Bee:
    WordInfo = namedtuple("WordInfo", ["letters", "points", "is_pangram"])
    Score = namedtuple("Score", ["score", "key", "pangrams", "words"])

    def __init__(self, words: Optional[Iterable[str]] = None):
        if not words:
            path = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "data", "words.txt"
            )
            with open(path, "rt") as f:
                self._init_from(f)
        else:
            self._init_from(words)

    def _init_from(self, words: Iterable[str]):
        def normalize(word: Iterable[str]):
            for word in words:
                yield word.strip().lower()

        self.words_dict = {
            word: Bee.get_word_info(word) for word in normalize(words) if word
        }
        self.root = self._create_tree()

        self._populate_tree()
        self.root = Bee._prune_tree(self.root)

    @staticmethod
    def get_word_info(word: str) -> WordInfo:
        letters = set(list(word))
        points, is_pangram = Bee.get_points(word)
        return Bee.WordInfo(letters, points, is_pangram)

    def _create_tree(self) -> Node:
        root = Node()
        for word in self.words_dict.values():
            if word.is_pangram:
                sorted_letters = sorted(word.letters)
                node = root
                for letter in sorted_letters:
                    node = node.ensure_child(letter)
        return root

    def _populate_tree(self) -> None:
        for word, info in self.words_dict.items():
            q = deque([(self.root, 0)])
            letter_ords = [ord(letter) for letter in sorted(info.letters)]
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

    @staticmethod
    def _prune_tree(node: Node) -> Node:
        if not node:
            return None
        if not node.children:
            return node if node.words else None

        node.children = [Bee._prune_tree(child) for child in node.children]
        return node if any(node.children) else None

    @staticmethod
    def get_points(word: str) -> Tuple[int, bool]:
        """Returns the word's point value (by daily Spelling Bee rules),
        plus a flag indicating whether the word is a pangram"""
        if len(word) == 4:
            return 1, False
        if len(word) < 7:
            return len(word), False
        is_pangram = 7 == len(set(list(word)))
        return len(word) + (7 if is_pangram else 0), is_pangram

    @staticmethod
    def from_list(words: List[str]) -> "Bee":
        """Construct a Bee object from a list of words"""
        return Bee(iter(words))

    @staticmethod
    def from_file(file: str) -> "Bee":
        """Construct a Bee object from a file containing a list of words"""
        with open(file, "rt") as f:
            return Bee(f)

    def list_words(self, key: str) -> Tuple[List[str], List[str]]:
        """List the words composable by a set of 7 letters.
        The key must be seven letters long (after stripping out non-letter characters), and the first letter is the 'center' letter.
        Returns two sorted lists, first of those which are pangrams, the second of non-pangrams
        """
        non_pangrams = []
        _key = [c for c in key.lower() if "a" <= c <= "z"]
        center = _key[0]
        steps = sorted(list(_key))
        node = self.root
        for letter in steps:
            if not node:
                return [], []
            for word in node.words:
                if center in word:
                    non_pangrams.append(word)
            node = node.children[ord(letter) - node.zero]
        pangrams = []
        for word in node.words:
            if center in word:
                _, is_pangram = Bee.get_points(word)
                if is_pangram:
                    pangrams.append(word)
                else:
                    non_pangrams.append(word)
        return sorted(pangrams), sorted(non_pangrams)

    def score_tree(self) -> List[Score]:
        def _score_tree(
            node: Node, history: List[Bee.Score], results: List[Tuple[str, int, int]]
        ) -> None:
            pangrams = 0
            if node.words:
                check_pangram = not node.children
                history_dict = {score.key: score for score in history}
                for word in node.words:
                    word_info = self.words_dict[word]
                    letters = word_info.letters
                    if check_pangram:
                        pangrams += word_info.is_pangram
                    for letter, score in history_dict.items():
                        if letter in letters:
                            history_dict[letter] = Bee.Score(
                                score.score + word_info.points,
                                letter,
                                0,
                                score.words + 1,
                            )
                if check_pangram and not pangrams:
                    history = []
                else:
                    history = [score for score in history_dict.values()]

            if not node.children:
                pattern = "".join([score.key for score in history])
                for i, score in enumerate(history):
                    if score.score:
                        key = pattern[i] + ":" + pattern[:i] + pattern[i + 1 :]
                        results.append(
                            Bee.Score(score.score, key, pangrams, score.words)
                        )
                pass
            else:
                for index, child in enumerate(node.children):
                    if not child:
                        continue
                    next_letter = chr(node.zero + index)
                    _score_tree(
                        child, history + [Bee.Score(0, next_letter, 0, 0)], results
                    )
            pass

        results = []
        _score_tree(self.root, [], results)

        return results

    def count_words(self) -> Dict[str, int]:
        """Return of dictionary of words and the count of puzzles the word can be found in."""

        def _count_words(node: Node, word_counts: Dict[str, int]) -> int:
            if node.children:
                leaves = sum(
                    [
                        _count_words(child, word_counts)
                        for child in node.children
                        if child
                    ]
                )
            else:
                leaves = 1
            if node.words:
                for word in node.words:
                    word_counts[word] += leaves * len(self.words_dict[word].letters)
            return leaves

        word_counts = defaultdict(int)
        _count_words(self.root, word_counts)

        return dict(word_counts)
