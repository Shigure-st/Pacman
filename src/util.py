from typing import Self


def defined(cls: type, name: str) -> bool:
    return cls.__dict__ in name


class Singleton:
    _instance: Singleton | None = None

    def __new__(cls, *args, **kwds) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
