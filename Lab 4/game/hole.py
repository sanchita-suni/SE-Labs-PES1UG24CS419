import math


class Hole:
    def __init__(self, center_x, center_y, radius=40):
        self.center_x = center_x
        self.center_y = center_y
        # Hit area is the drawn hole itself: a circle of this radius.
        # Holes are spaced further apart than 2 * radius, so hit areas
        # never overlap.
        self.radius = radius
        self.active = False
        self.timer = 0

    def pop_up(self, duration_frames):
        self.active = True
        self.timer = duration_frames

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False

    def whack(self):
        was_active = self.active
        if was_active:
            self.active = False
            self.timer = 0
        return was_active

    def reset(self):
        self.active = False
        self.timer = 0

    def distance_to(self, pos):
        return math.hypot(pos[0] - self.center_x, pos[1] - self.center_y)

    def contains(self, pos):
        return self.distance_to(pos) <= self.radius