from collections.abc import Sequence

from .core import Component


def require_component[T: type[Component]](
    *requires: Sequence[type[Component]],
    inherit_child: bool = True,
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
        for com in components:
            if not issubclass(com, Component):
                raise ValueError(f"Class {com} is not Component")
        if inherit_child:
            if component._require_inherit is None:
                component._require_inherit = set()
            _require = component._require_inherit
        else:
            if component._require_uninherit is None:
                component._require_uninherit = set()
            _require = component._require_uninherit
        _require |= set(requires)
        return component
    return update_require


def before_component[T: type[Component]](
    *components: Sequence[type[Component]],
    inherit_child: bool = True,
) -> Callable[[T], T]:
    def set_before(component: T) -> T:
        if len(components) == 0:
            return component
        for com in components:
            if not issubclass(com, Component):
                raise ValueError(f"Class {com} is not Component")
        if inherit_child:
            if component._before_inherit is None:
                component._before_inherit = []
            _before = component._before_inherit
        else:
            if component._before_uninherit is None:
                component._before_uninherit = []
            _before = component._before_uninherit

        checked = set()
        _before.extend(components)
        befores = _before.copy()
        while befores:
            com = befores.pop()
            if com in checked:
                continue
            if com is component:
                raise ValueError(
                    f"Circular before dependency with Component %s."
                    % (component)
                )
            checked.add(com)
            befores.extend(com.before())
        return component
    return set_before


def after_component[T: type[Component]](
    *components: Sequence[type[Component]],
    inherit_child: bool = True,
) -> Callable[[T], T]:
    def set_after(component: T) -> T:
        if len(components) == 0:
            return component
        for com in components:
            if not issubclass(com, Component):
                raise ValueError(f"Class {com} is not Component")
        if inherit_child:
            if component._after_inherit is None:
                component._after_inherit = []
            _after = component._after_inherit
        else:
            if component._after_uninherit is None:
                component._after_uninherit = []
            _after = component._after_uninherit
        _after.extend(components)

        checked = set()
        _after.extend(components)
        afters = _after.copy()
        while afters:
            com = afters.pop()
            if com in checked:
                continue
            if com is component:
                raise ValueError(
                    f"Circular after dependency with %s and %s."
                    % (com, component)
                )
            checked.add(com)
            afters.extend(com.after())
    return set_after
