from __future__ import annotations

from abc import ABC
from collections.abc import Sequence, Iterable
from typing import dataclass_transform, Callable, TYPE_CHECKING, Self
from dataclasses import dataclass
from itertools import chain

from src.util import overridden

from .order_resolver import ComponentOrderResolver

if TYPE_CHECKING:
    from .game_object import GameObject

@dataclass_transform()
class Component(ABC):
    START_DEF_NAME = "start"
    UPDATE_DEF_NAME = "update"
    LATE_UPDATE_DEF_NAME = "late_update"
    REMOVED_DEF_NAME = "removed"
    START_DEF_TYPE: ClassVar[Callable[[Component], None]]
    UPDATE_DEF_TYPE: ClassVar[Callable[[Component, float], None]]

    _require_uninherit: set[type[Component]] | None = None
    _require_inherit: set[type[Component]] | None = None

    @classmethod
    def require(cls) -> set[type[Component]] | None:
        match (cls._require_uninherit is None, cls._require_inherit is None):
            case (True, True):
                return None
            case (False, True):
                return cls._require_uninherit
            case (True, False):
                return cls._require_inherit
            case _:
                return chain(cls._require_uninherit, cls._require_inherit)

    _before_uninherit: list[type[Component]] | None = None
    _before_inherit: list[type[Component]] | None = None

    @classmethod
    def before(cls) -> Iterable[type[Component]]:
        match (cls._before_uninherit is None, cls._before_inherit is None):
            case (True, True):
                return ()
            case (False, True):
                return cls._before_uninherit
            case (True, False):
                return cls._before_inherit
            case _:
                return chain(cls._before_uninherit, cls._before_inherit)

    _after_uninherit: list[type[component]] | None = None
    _after_inherit: list[type[component]] | None = None

    @classmethod
    def after(cls) -> Iterable[type[Component]]:
        match (cls._after_uninherit is None, cls._after_inherit is None):
            case (True, True):
                return ()
            case (False, True):
                return cls._after_uninherit
            case (True, False):
                return cls._after_inherit
            case _:
                return chain(cls._after_uninherit, cls._after_inherit)

    gameobject: GameObject

#    def __init__(self, go: GameObject, /, *, active: bool = True) -> None:
#        self._go = go
#        self.active = active
#        if go.active and active:
#            if defined(component, Component.START_DEF_NAME):
#                component.start()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._before_inherit = None
        cls._after_inherit = None
        cls._before_uninherit = None
        cls._after_uninherit = None
        cls._require_uninherit = None
        cls._require_inherit = None
        for bclass in cls.__bases__:
            if not issubclass(bclass, Component):
                continue
            if bclass._require_inherit is not None:
                if cls._require_inherit is None:
                    cls._require_inherit= []
                cls._require_inherit.extend(bclass._require_inherit)
            if bclass._before_inherit is not None:
                if cls._before_inherit is None:
                    cls._before_inherit = []
                cls._before_inherit.extend(bclass._before_inherit)
            if bclass._after_inherit is not None:
                if cls._after_inherit is None:
                    cls._after_inherit = []
                cls._after_inherit.extend(bclass._after_inherit)
        dataclass(cls)

    def set_gameobject(self, gameobject: GameObject) -> Self:
        self.gameobject = gameobject
        self.added()
        return self

    def added(self) -> None: ...
    def removed(self) -> None: ...
    def start(self) -> None: ...

    def update(self, dt: float) -> None: ...
    def late_update(self, dt: float) -> None: ...


Component.START_DEF_TYPE = Callable[[Component], None]
Component.UPDATE_DEF_TYPE = Callable[[Component, float], None]


class ComponentList(Iterable[Component]):
    _dict: dict[type[Component], dict[int, Component]]
    _go: GameObject

    _starts: dict[type[Component], dict[int, Component.START_DEF_TYPE]]
    _starts_sorted: list[Component.START_DEF_TYPE]
    _starts_cached: bool = True
    _starts_order: ComponentOrderResolver

    _updates: dict[type[Component], dict[int, Component.UPDATE_DEF_TYPE]]
    _updates_sorted: list[Component.UPDATE_DEF_TYPE]
    _updates_cached: bool = True
    _updates_order: ComponentOrderResolver

    _late_updates: dict[int, Component.UPDATE_DEF_TYPE]
    _late_updates_sorted: list[Component.UPDATE_DEF_TYPE]
    _late_updates_cached: bool = True
    _late_updates_order: ComponentOrderResolver

    def __init__(self, go: GameObject) -> None:
        self._dict: dict[int, Component] = {}
        self._go = go
        self._starts = {}
        self._starts_sorted = []
        self._starts_order = ComponentOrderResolver()
        self._updates = {}
        self._updates_sorted = []
        self._updates_order = ComponentOrderResolver()
        self._late_updates = {}
        self._late_updates_sorted = []
        self._late_updates_order = ComponentOrderResolver()

    def __iter__(self) -> Iterator[Component]:
        return chain(c.values() for c in self._dict.values())

    def __contains__(self, item: type[Component]) -> bool:
        return item in self._dict

    def __getitem__[T: Component](
        self,
        idx: type[T],
    ) -> Iterable[T]:
        return self._dict[idx].values()

    def starts(self) -> Sequence[Component.START_DEF_TYPE]:
        if self._starts_cached:
            return self._starts_sorted
        self._starts_sorted.clear()
        for t in chain(*self._starts_order.resolve()):
            self._starts_sorted.extend(self._starts[t].values())
        self._starts_cached = True
        return self._starts_sorted

    def updates(self) -> Sequence[Component.UPDATE_DEF_TYPE]:
        if self._updates_cached:
            return self._updates_sorted
        self._updates_sorted.clear()
        for t in chain(self._updates_order.resolve()):
            self._updates_sorted.extend(self._updates[t].values())
        self._updates_cached = True
        return self._updates_sorted

    def late_updates(self) -> Sequence[Component.LATE_UPDATE_DEF_TYPE]:
        if self._late_updates_cached:
            return self._late_updates_sorted
        self._late_updates_sorted.clear()
        for t in chain(self._late_updates_order.resolve()):
            self._late_updates_sorted.extend(self._late_updates[t].values())
        self._late_updates_cached = True
        return self._late_updates_sorted

    def append(self, *components: Sequence[Component]) -> None:
        if len(components) == 0:
            return
        requires: set[Component] = set()
        for component in components:
            self._dict[id(component)] = component
            require = type(component).require()
            if require is not None:
                requires |= require
        if len(requires) > 0:
            requires ^= self._dict.keys()
        if len(requires) > 0:
            components = list(*components, *(req() for req in requires))
        for component in components:
            id_ = id(component)
            t = type(component)
            if overridden(t, Component, Component.START_DEF_NAME):
                if t not in self._starts:
                    self._starts[t] = {}
                self._starts[t][id_] = getattr(component, Component.START_DEF_NAME)
                self._starts_order.add_component(t)
                self._starts_cached = False
            if overridden(t, Component, Component.UPDATE_DEF_NAME):
                if t not in self._updates:
                    self._updates[t] = {}
                self._updates[t][id_] = getattr(component, Component.UPDATE_DEF_NAME)
                self._updates_order.add_component(t)
                self._updates_cached = False
            if overridden(t, Component, Component.LATE_UPDATE_DEF_NAME):
                if t not in self._late_updates:
                    self._late_updates[t] = {}
                self._late_updates[t][id_] = getattr(component, Component.LATE_UPDATE_DEF_NAME)
                self._late_updates_order.add_component(t)
                self._late_updates_cached = False

    def remove(self, *components: Sequence[Component]) -> None:
        if len(components) == 0:
            return
        types: set[type[Component]] = set()
        for component in Components:
            id_ = id(component)
            t = type(component)
            types.add(t)
            if overridden(t, Component, Component.REMOVED_DEF_NAME):
                getattr(component, Component.REMOVED_DEF_NAME)()
            self._starts[t].pop(id_, None)
            self._updates[t].pop(id_, None)
            self._late_updates[t].pop(id_, None)
            del self[id_]
        for c_type in types:
            if len(self._starts[c_type]) <= 0:
                del self._starts[c_type]
                self._starts_order.remove_component(c_type)
                self._starts_chaced = False
            if len(self._updates[c_type]) <= 0:
                del self._updates[c_type]
                self._updates_order.remove_component(c_type)
                self._updates_chaced = False
            if len(self._late_updates[c_type]) <= 0:
                del self._late_updates[c_type]
                self._late_updates_order.remove_component(c_type)
                self._late_updates_chaced = False

    def get_component[T: Component](self, /, type_: type[T]) -> T:
        return next(iter(self._dict[type_]))

    def get_components[T: Component](self, /, type_: type[T]) -> Iterable[T]:
        return self._dict[type_].values()

    def remove_by_type[T: Component](self, type_: type[T]) -> T:
        del self._dict[type_]
        if type_ in self._starts:
            del self._starts[type_]
            self._starts_order.remove_component(type_)
            self._starts_chaced = False
        if type_ in self._updates:
            del self._updates[type_]
            self._updates_order.remove_component(type_)
            self._updates_chaced = False
        if type_ in self._late_updates:
            del self._late_updates[type_]
            self._late_updates_order.remove_component(type_)
            self._late_updates_chaced = False
