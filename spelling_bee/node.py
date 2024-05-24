from typing import List


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
