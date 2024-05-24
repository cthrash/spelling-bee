from spelling_bee.node import Node


def test_init():
    node = Node()
    assert node.zero == ord("a")
    assert node.children == None
    assert node.words == []


def test_ensure_child():
    root = Node()
    node = root.ensure_child("c")
    assert root.zero == ord("a")
    assert root.children == [None, None, node] + [None] * 23
    assert root.words == []
    assert repr(root) == "<zero=a children=c words=0>"
    assert node.zero == ord("d")
    assert node.children == None
    assert node.words == []
    assert repr(node) == "<zero=d children=None words=0>"
