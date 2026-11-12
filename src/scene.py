from game_object import GameObject
from typing import Sequence, Self


class Scene:
    """
    Usage:
        Scene("TestScene",
            GameObject("Gameobject0", Movement()),
            Gameobject("Gameobject1", Manager()),
        )
    """
    name: str
    active: bool
    gameobjects: dict[int, GameObject]

    def __init__(self, name: str, *gos: Sequence[GameObject]) -> None:
        self.name = name
        self.gameobjects = {id(go): go for go in gos}

    def add_gameobject(self, *gos: Sequence[GameObject]) -> Self:
        self.gameobjects.update({id(go): go for go in gos})
        return self
