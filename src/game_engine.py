from .util import Singleton


class GameEngine(Singleton):
    _scenes: dict[str, Scene]

    def __init__(self) -> None:
        print("init")

    def load_scene(self, scene: Scene) -> None:
        _scenes[scene.name] = scene
        # load scene

    def unload_scene(self, scene: Scene | str) -> None:
        if isinstance(scene, Scene):
            scene = scene.name
        del _scenes[scene]
        # unload scene

    def get_scene(self, scene: str) -> None:
        return _scenes[scene]
