from abc import ABC
from collections.abc import Sequence, Iterable
from typing import dataclass_transform, Callable, TYPE_CHECKING
from dataclass import dataclass

from .util import defined

if TYPE_CHECKING:
    from .game_object import GameObject

@dataclass_transform()
class Component(ABC):
    ADDED_DEF_NAME = "added"
    REMOVED_DEF_NAME = "removed"
    START_DEF_NAME = "start"
    POST_UPDATE_DEF_NAME = "post_update"
    UPDATE_DEF_NAME = "update"
    LATE_UPDATE_DEF_NAME = "late_update"

    _require: set | None = None

#    def __init__(self, go: GameObject, /, *, active: bool = True) -> None:
#        self._go = go
#        self.active = active
#        if go.active and active:
#            if defined(component, Component.START_DEF_NAME):
#                component.start()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(cls, **kwargs)
        dataclass(cls)

    def added(self) -> None: ...
    def removed(self) -> None: ...

    def start(self) -> None: ...

    def post_update(self, dt: float) -> None: ...
    def update(self, dt: float) -> None: ...
    def late_update(self, dt: float) -> None: ...



class Component_list(Iterable[Component]):
    _dict: dict[int, Component]
    _go: GameObject

    _starts: dict[int, Component] = {}

    _post_updates: dict[int, Component] = {}
    _updates: dict[int, Component] = {}
    _late_updates: dict[int, Component] = {}

    def __init__(self, go: GameObject) -> None:
        self._dict: dict[int, Component] = {}
        self._go = go

    def __iter__(self) -> None:
        return self._dict.values()

    def append(self, *components: Sequence[Component]) -> None:
        if len(components) == 0:
            return
        cls = type(self)
        requires: set[Component] = set()
        for component in components:
            self._dict[id(component)] = component
            require = type(component)._require
            if require is not None:
                requires |= require
        if len(requires) > 0:
            requires ^= self._dict.keys()
        if len(requires) > 0:
            components = list(*components, *(req() for req in requires))
        for component in components:
            id_ = id(component)
            if defined(component, Component.START_DEF_NAME):
                if id_ not in cls._starts:
                    cls._starts[id_] = []
                cls._starts[id_].append(component)
            if defined(component, Component.POST_UPDATE_DEF_NAME):
                if id_ not in cls._post_updates:
                    cls._post_updates[id_] = []
                cls._post_updates[id_].append(component)
            if defined(component, Component.UPDATE_DEF_NAME):
                if id_ not in cls._updates:
                    cls._updates[id_] = []
                cls._updates[id_].append(component)
            if defined(component, Component.LATE_UPDATE_DEF_NAME):
                if id_ not in cls._late_updates:
                    cls._late_updates[id_] = []
                cls._late_updates[id_].append(component)
            if defined(component, Component.ADDED_DEF_NAME):
                getattr(component, Component.ADDED_DEF_NAME)()

    def remove(self, *components: Sequence[Component]) -> None:
        if len(components) == 0:
            return
        cls = type(self)
        for component in Components:
            if defined(component, Component.REMOVED_DEF_NAME):
                getattr(component, Component.REMOVED_DEF_NAME)()
            id_ = id(component)
            cls._updates.pop(id_, None)
            cls._starts.pop(id_, None)
            del self[id_]

    def get_component[T: Component](self, type_: type[T]) -> T:
        for component in self:
            if isinstance(component, type_):
                return component

    def get_components[T: Component](self, type_: type[T]) -> T:
        res: list[Component] = []
        for component in self:
            if isinstance(component, type_):
                 res.append(component)
        return res

    def remove_by_type[T: Component](self, type_: type[T]) -> T:
        for component in self:
            if isinstance(component, type_):
                self.remove(component)


def require_component[T: type[Component]](
    *requires: Sequence[Component],
) -> Callable[[T], T]:
    """Add require component to component.
    Required componet will be automatically added in gameobject when needed.

    Usage:
        class ComponentA(Component): ...

        @require_component(ComponentA)
        class ComponentB(Component): ...
    """
    def update_require(component: T) -> T:
        if len(requires) == 0:
            return component
        if component._require is not None:
            component._require |= set(requires)
            return component
        component._require = set(requires)
        return component
    return update_require
