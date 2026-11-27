from collections.abc import Sequence
from typing import Self

from .component import Component, ComponentList


class GameObject:
    name: str
    active: bool
    components: ComponentList
    _scene: Scene | None

    def __init__(
        self,
        name: str,
        *components: Sequence[Component],
        active: bool = True,
    ) -> None:
#        self.transformer = Transformer()
#        self.components.extend(self.transformer, *components)
        self.active = active
        self._scene = None
        self.components = ComponentList(self)
        self.components.append(*components)

    def set_scene(self, scene: Scene) -> Self:
        self._scene = scene
        return self

    def add_component(
        self,
        *components: Sequence[Component | type[Component]]
    ) -> Self:
        self.components.append(
            *(c() if isinstance(c, type) else c for c in components)
        )
        return self

    def remove_component(self, *components: Sequence[Component]) -> Self:
        self.components.remove(*components)
        return self
