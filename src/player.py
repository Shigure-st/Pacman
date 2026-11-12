class Player(GameObject):
    def __init__(self):
        super().__init__()
        self.component.append(
            SpriteRenderer(),
            PlayerMove()
        )


class PlayerMove(Component):
    player_speed = 0.5

    def update(self, dt: float):
        self.transformer.position.x += player_speed * dt
