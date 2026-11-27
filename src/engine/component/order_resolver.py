from typing import Self, TYPE_CHECKING
from collections import defaultdict
from collections.abc import Iterable
from itertools import chain


if TYPE_CHECKING:
    from .core import Component


class ComponentOrderResolver:
    _nodes: dict[type[Component], _ResolveNode]
    _heads: dict[type[Component], _ResolveNode]
    _order: dict[type[Component], list[type[Component]]]
    _changed: set[_ResolveNode]

    def __init__(self) -> None:
        self._nodes = {}
        self._heads = {}
        self._order = {}
        self._changed = set()

    def __iter__(self) -> Iterable[list[type[Component]]]:
        return self.resolve()

    def resolve(self) -> Iterable[list[type[Component]]]:
        if not self._changed:
            return self._order.values()
        # re-calculate order
        heads = set(node.head for node in self._changed)
        order_dict = defaultdict(set)
        for head in heads:
            order_dict.clear()
            i = head.update_order_dict(order_dict)
            order_list = []
            while len(order_dict[i]):
                order_list.extend(order_dict[i])
                i += 1
            self._order[head] = order_list
        self._changed.clear()
        return self._order.values()

    def _update_node_head(node: _ResolveNode, new_head: _ResolveNode) -> None:
        old_head = node.head
        del self._heads[old_head]
        if old_head in self._order:
            del self._order[old_head]
        node.update_head(new_head)

    def add_component(self, *components: Iterable[type[Component]]) -> Self:
        print("trying to add component:", components)
        for component in components:
            if component in self._nodes:
                continue
            befores = [
                self._nodes[c]
                for c in component.before()
                if c in self._nodes
            ]
            afters = [
                self._nodes[c]
                for c in component.after()
                if c in self._nodes
            ]
            if not befores and not afters:
                new_node = _ResolveNode(component, None)
                self._nodes[component] = new_node
                self._heads[component] = new_node
                self._changed.add(new_node)
                continue
            node_iter = chain(befores, afters)
            new_head = next(node_iter)
            for node in set(n.head for n in node_iter):
                self._update_node_head(node, new_head)
            match (not befores, not afters):
                case (False, True):
                    new_node = _ResolveNode(
                        component, new_head, before=befores,
                    )
                case (True, False):
                    new_node = _ResolveNode(
                        component, new_head, after=afters,
                    )
                case _:
                    new_node = _ResolveNode(
                        component, new_head, before=befores, after=afters,
                    )
            self._nodes[component] = new_node
            self._changed.add(new_node)
            for node in befores:
                if node.after is None:
                    node.after = [new_node]
                else:
                    node.after.append(new_node)
            for node in afters:
                if node.before is None:
                    node.before = [new_node]
                else:
                    node.before.append(new_node)

    def add_node(self, node: _ResolveNode):
        node.before = None
        node.after = None
        befores = [
            self._nodes[c]
            for c in component.before()
            if c in _nodes
        ]
        afters = [
            self._nodes[c]
            for c in component.after()
            if c in _nodes
        ]

    def remove_component(self, *components: Iterable[type[Component]]) -> None:
        re_add: set[_ResolveNode] = set()
        for component in components:
            if component not in self._nodes:
                continue
            node = self._nodes[component]
            del self._nodes[component]
            re_add |= (node.all_connection())
        for node in re_add:
            if node.before is not None:
                node.before = [
                    c for c in node.before if c in self._nodes
                ]
            if node.after is not None:
                node.after = [
                    c for c in node.after if c in self._nodes
                ]
        for node in re_add:
            node.update_head(None)
        node_iter = iter(re_add)
        heads = []
        while True:
            try:
                head = next(node_iter)
                head.update_head(head)
                heads.append(head)
                node = next(node_iter)
            except StopIteration:
                break
            while node.head is head:
                node = next(node_iter)
        for head in heads:
            self._heads[head.component] = head
            self._changed.add(head)



class _ResolveNode:
    component: type[Component]
    before: list[_ResolveNode] | None
    after: list[_ResolveNode] | None
    head: _ResolveNode | None

    def __init__(
        self,
        component: type[Component],
        head: _ResolveNode | None,
        *,
        before: list[_ResolveNode] | None = None,
        after: list[_ResolveNode] | None = None,
    ) -> None:
        self.component = component
        self.head = head or self
        self.before = before
        self.after = after

    def update_head(self, head: _ResolveNode) -> None:
        if self.head is head:
            return
        for node in self.before:
            node.update_head(head)
        for node in self.after:
            node.update_head(head)

    def all_connection(self) -> Iterator[type[Component]]:
        _set = set()
        self._all_connection(_set)
        return _set

    def _all_connection(self, _set: set[type[Component]]) -> None:
        if self.component in _set:
            return
        if self.before is not None:
            for node in self.before:
                node._all_connection(_set)
        if self.after is not None:
            for node in self.after:
                node._all_connection(_set)

    def update_order_dict(
        self,
        d: defaultdict[int, set[type[Component]]],
        *,
        _order: int = 0,
    ) -> int:
        if self.component in d[_order]:
            return _order + 1
        min_order = _order
        d[_order].add(self.component)
        if self.before is not None:
            for node in self.before:
                min_order = min(
                    min_order,
                    node.update_order_dict(d, _order=_order + 1),
                )
        if self.after is not None:
            for node in self.after:
                min_order = min(
                    min_order,
                    node.update_order_dict(d, _order=_order - 1),
                )
        return min_order
