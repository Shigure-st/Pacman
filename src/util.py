from typing import Self


def defined(obj: object, name: str) -> bool:
    if not isinstance(obj, type):
        obj = type(obj)
#    print(f"Defined check: obj: {obj}, obj.dict: {obj.__dict__}, name: {name}")
    return name in obj.__dict__


def overridden(type_: type, base: type, name: str) -> bool:
    for t in type_.__mro__:
        if t is base:
            print(f"t: {type_}, base: {base}, name: {name}, False")
            return False
        if defined(t, name):
            print(f"t: {type_}, base: {base}, name: {name}, True")
            return True
    return False


class Singleton:
    _instance: Singleton | None = None

    def __new__(cls, *args, **kwds) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
