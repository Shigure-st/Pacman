from collections.abc import Sequence
from typing import Self

from .component import Component, Component_list


class GameObject:
    name: str
    active: bool

    def __init__(
        self,
        name: str,
        *components: Sequence[Component],
        active: bool = True,
    ) -> None:
        self.transformer = Transformer()
        self.components = Component_list()
        self.components.append(self.transformer, *components)
        self.active = active

    def add_component(self, *components: Sequence[Component]) -> Self:
        self.components.append(components)
        return self

    def remove_component(self, *components: Sequence[Component]) -> Self:
        self.components.remove(components)
        return self
