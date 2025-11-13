try:
    import pygame as pg
    import sys
    from pygame.locals import *
    from typing import Dict, Any, Optional, List
except ImportError as err:
    print(f"Failed to load module. {err}")
    sys.exit(2)

DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_BG_COLOR = (34, 34, 34)
DEFAULT_BALL_RADIUS = 24
DEFAULT_BALL_COLOR = (255, 0, 0)

GRID_SPACING = 50
GRID_COLOR = (173, 216, 230)
GRID_DASH_LENGTH = 5
GRID_GAP_LENGTH = 5

class BallPath:
    """Holds the animation path data for a Ball object."""
    def __init__(self,
                 start_pos: pg.math.Vector2,
                 end_pos: pg.math.Vector2,
                 start_time: int = 0,
                 end_time: int = 1):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.start_time = start_time
        self.end_time = end_time

class Ball:
    """Holds all data for a single Ball."""
    def __init__(self,
                 position: pg.math.Vector2,
                 radius: int = DEFAULT_BALL_RADIUS,
                 color: Dict[str, Any] = {'rgb': DEFAULT_BALL_COLOR},
                 layer: int = 0,
                 path: Optional[BallPath] = None):
        self.position = position # Position in the Scene
        self.radius = radius
        self.color = color
        self.layer = layer
        self.path = path
    
    def get_render_color(self, color_space: str) -> pg.Color:
        """
        Retrieves the RGB color for rendering.
        """
        # TODO: Add support for other color spaces.

        if 'rgb' in self.color:
            return pg.Color(self.color['rgb'])
        else:
            return pg.Color(DEFAULT_BALL_COLOR)
        
class Scene:
    """Holds all data for the current scene."""
    def __init__(self,
                 width: int = DEFAULT_WIDTH,
                 height: int = DEFAULT_HEIGHT,
                 bg_color: Dict[str, Any] = {'rgb': DEFAULT_BG_COLOR},
                 color_space: str = 'oklab'):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.color_space = color_space
        self.balls: List[Ball] = []

        # TODO: Add support for other color spaces.
    
    def get_render_bg_color(self) -> pg.Color:
        """
        Retrieves the RGB background color for rendering.
        """
        if 'rgb' in self.bg_color:
            return pg.Color(self.bg_color['rgb'])
        else:
            return pg.Color(DEFAULT_BG_COLOR)
        
    def add_ball(self, ball: Ball):
        """Adds a ball to the scene."""
        self.balls.append(ball)

class BallSimApp:
    """Manages the main game loop and application state."""

    def __init__(self):
        pg.init()

        self.scene = Scene()

        self.screen = pg.display.set_mode((self.scene.width, self.scene.height))
        pg.display.set_caption("BallSim — Scene Editor")

        self.clock = pg.time.Clock()
        self.running = True
    
    def run(self):
        """Main application loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pg.quit()
        sys.exit()
    
    def handle_events(self):
        """Process user input at every time step."""
        for event in pg.event.get():
            if event.type == QUIT:
                self.running = False

            if event.type == MOUSEBUTTONDOWN:
                # 1 = Left-click
                if event.button == 1:
                    mouse_pos = pg.mouse.get_pos()
                    snapped_pos = self.snap_to_grid(mouse_pos)

                    new_ball = Ball(position=pg.math.Vector2(snapped_pos))

                    self.scene.add_ball(new_ball)
        
        # TODO: Add support for other user events.
    
    def update(self):
        """Update game state (e.g., window animations). Not implemented yet."""
        pass

    def draw(self):
        """Draw everything to the screen."""
        self.screen.fill(self.scene.get_render_bg_color())

        self.draw_grid()

        sorted_balls = sorted(self.scene.balls, key=lambda b: b.layer)

        for ball in sorted_balls:
            pg.draw.circle(
                self.screen,
                ball.get_render_color(self.scene.color_space),
                ball.position,
                ball.radius
            )
        
        pg.display.flip()
    
    def draw_grid(self):
        """Draws the grid over the canvas in the scene editor window."""

        for x in range(0, self.scene.width, GRID_SPACING):
            for y in range(0, self.scene.height, GRID_DASH_LENGTH + GRID_GAP_LENGTH):
                start_pos = (x, y)
                end_pos = (x, y + GRID_DASH_LENGTH)
                # Check that we do not draw past the screen height
                if end_pos[1] > self.scene.height:
                    end_pos = (x, self.scene.height)
                pg.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 1)

        for y in range(0, self.scene.height, GRID_SPACING):
            for x in range(0, self.scene.width, GRID_DASH_LENGTH + GRID_GAP_LENGTH):
                start_pos = (x, y)
                end_pos = (x + GRID_DASH_LENGTH, y)
                # Check that we do not draw past the screen width
                if end_pos[0] > self.scene.width:
                    end_pos = (self.scene.width, y)
                pg.draw.line(self.screen, GRID_COLOR, start_pos, end_pos, 1)
        
    def snap_to_grid(self, pos: tuple[int, int]) -> tuple[int, int]:
        """Calculate the nearest grid intersection to a given position."""
        x, y = pos
        snapped_x = round(x / GRID_SPACING) * GRID_SPACING
        snapped_y = round(y / GRID_SPACING) * GRID_SPACING
        return (snapped_x, snapped_y)

# --- Entry Point ---
if __name__ == "__main__":
    app = BallSimApp()
    app.run()