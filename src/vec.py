from typing import ClassVar


class Vec2:
    x: float
    y: float

    zero: ClassVar[Vec2]
    one: ClassVar[Vec2]
    up: ClassVar[Vec2]
    down: ClassVar[Vec2]
    left: ClassVar[Vec2]
    right: ClassVar[Vec2]

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __get_item__(self, idx: int) -> float:
        match idx:
            case 0:
                return self.x
            case 1:
                return self.y

    def __set_item__(self, idx: int, value: float) -> None:
        match idx:
            case 0:
                self.x = value
            case 1:
                self.y = value


Vec2.zero = Vec2(0., 0.)
Vec2.one = Vec2(1., 1.)
Vec2.up = Vec2(0., 1.)
Vec2.down = Vec2(0., -1.)
Vec2.left = Vec2(-1., 0.)
Vec2.right = Vec2(1., 0.)


class Vec3:
    x: float
    y: float
    z: float

    zero: ClassVar[Vec3]
    one: ClassVar[Vec3]
    up: ClassVar[Vec3]
    down: ClassVar[Vec3]
    left: ClassVar[Vec3]
    right: ClassVar[Vec3]
    forward: ClassVar[Vec3]
    backward: ClassVar[Vec3]


    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __get_item__(self, idx: int) -> float:
        match idx:
            case 0:
                return self.x
            case 1:
                return self.y

    def __set_item__(self, idx: int, value: float) -> None:
        match idx:
            case 0:
                self.x = value
            case 1:
                self.y = value


Vec3.zero = Vec3(0., 0., 0.)
Vec3.one = Vec3(1., 1., 1.)
Vec3.up = Vec3(0., 1., 0.)
Vec3.down = Vec3(0., -1., 0.)
Vec3.left = Vec3(-1., 0., 0.)
Vec3.right = Vec3(1., 0., 0.)
Vec3.forward = Vec3(0., 0., 1.)
Vec3.backward = Vec3(0., 0., -1.)
