try:
    import pygame as pg
    import sys
    import math
    from pygame.locals import *
    from typing import Dict, Any, Optional, List
    from enum import Enum, auto
    
    from ui_elements import Button, TextInput, ToggleButtonGroup, draw_label, LABEL_TEXT_COLOR
except ImportError as err:
    print(f"Failed to load module. {err}")
    sys.exit(2)

class AppState(Enum):
    STATE_SUPPORT_MENU = auto()
    STATE_SCENE_ATTRIBUTES = auto()
    STATE_SCENE_EDITOR = auto()
    # TODO: Add further states

# Scene Editor constants
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_BG_COLOR = (34, 34, 34)
DEFAULT_BALL_RADIUS = 24
DEFAULT_BALL_COLOR = (255, 0, 0)
# Scene Editor grid constants
GRID_SPACING = 50
GRID_COLOR = (173, 216, 230)
GRID_DASH_LENGTH = 5
GRID_GAP_LENGTH = 5
# Scene Editor vector constants
PATH_COLOR = (255, 255, 0)
PATH_LINE_WIDTH = 2
PATH_ARROW_SIZE = 10
# Support Menu GUI constants
MENU_WIDTH = 400
MENU_HEIGHT = 300
MENU_BG_COLOR = (50, 50, 50)
MENU_BUTTON_WIDTH = 200
MENU_BUTTON_HEIGHT = 50
# Scene Attribute Window GUI constants
ATTR_MENU_WIDTH = 600
ATTR_MENU_HEIGHT = 500
ATTR_MENU_BG_COLOR = (50, 50, 50)
ATTR_LABEL_WIDTH = 150
ATTR_INPUT_WIDTH = 100
ATTR_INPUT_HEIGHT = 32

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
        
    def is_colliding_with_point(self, point: tuple[int, int]) -> bool:
        """Checks if a 2D point is inside this Ball."""
        distance = self.position.distance_to(point)
        return distance <= self.radius

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
        """Adds a ball to the scene. Ensures that new Balls are placed in a unique layer."""
        max_layer = -1
        if self.balls:
            max_layer = max(b.layer for b in self.balls)
        ball.layer = max_layer + 1
        self.balls.append(ball)

    def remove_ball(self, ball: Ball):
        """Removes a ball from the scene."""
        if ball in self.balls:
            self.balls.remove(ball)

class BallSimApp:
    """Manages the main game loop and application state."""

    def __init__(self):
        pg.init()

        self.app_state = AppState.STATE_SUPPORT_MENU
        self.scene = Scene()

        self.screen = pg.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
        pg.display.set_caption("BallSim")

        self.clock = pg.time.Clock()
        self.running = True

        # Scene Editor-specific state
        self.is_dragging_path = False
        self.drag_ball: Optional[Ball] = None

        # Menu-specific state
        self.menu_buttons: List[Button] = []
        self.create_support_menu()

        # Scene Attributes-specific state
        self.attr_ui_elements = []
        self.attr_inputs: Dict[str, TextInput] = {}
        self.attr_toggles: Optional[ToggleButtonGroup] = None
        self.attr_buttons: List[Button] = []

    def create_support_menu(self):
        """Creates and positions the buttons for the support menu."""
        self.menu_buttons = [] # Flush existing buttons

        new_scene_rect = pg.Rect(
            (MENU_WIDTH - MENU_BUTTON_WIDTH) // 2,
            75,
            MENU_BUTTON_WIDTH,
            MENU_BUTTON_HEIGHT
        )

        self.menu_buttons.append(Button("New Scene", new_scene_rect, self.go_to_scene_attributes))

        load_scene_rect = pg.Rect(
            (MENU_WIDTH - MENU_BUTTON_WIDTH) // 2,
            140,
            MENU_BUTTON_WIDTH,
            MENU_BUTTON_HEIGHT
        )
        # TODO: Implement file loading
        self.menu_buttons.append(Button("Load Scene", load_scene_rect, self.load_scene_stub))

        help_rect = pg.Rect(
            (MENU_WIDTH - MENU_BUTTON_WIDTH) // 2,
            205,
            MENU_BUTTON_WIDTH,
            MENU_BUTTON_HEIGHT
        )
        # TODO: Implement help window
        self.menu_buttons.append(Button("Help", help_rect, self.show_help_stub))
    
    def go_to_scene_attributes(self):
        """Switches to the Scene Attributes menu."""
        self.app_state = AppState.STATE_SCENE_ATTRIBUTES
        self.screen = pg.display.set_mode((ATTR_MENU_WIDTH, ATTR_MENU_HEIGHT))
        pg.display.set_caption("BallSim — New Scene Attributes")
        self.create_scene_attributes_menu()

    def create_scene_attributes_menu(self):
        """Builds all UI elements for the attributes menu."""
        self.attr_ui_elements = []
        self.attr_inputs = {}
        self.attr_buttons = []

        x_col1 = 50
        x_col2 = x_col1 + ATTR_LABEL_WIDTH + 10

        # 1. Canvas Size
        y_pos = 75
        self.attr_inputs['width'] = TextInput(pg.Rect(x_col2, y_pos, ATTR_INPUT_WIDTH, ATTR_INPUT_HEIGHT), "1280")
        self.attr_inputs['height'] = TextInput(pg.Rect(x_col2 + ATTR_INPUT_WIDTH + 30, y_pos, ATTR_INPUT_WIDTH, ATTR_INPUT_HEIGHT), "720")
        
        # 2. Color Space
        y_pos = 120
        self.attr_toggles = ToggleButtonGroup(
            active_option='oklab', 
            on_toggle=self.on_color_space_toggle
        )
        self.attr_toggles.add_button("RGB", pg.Rect(x_col2, y_pos, 80, ATTR_INPUT_HEIGHT))
        self.attr_toggles.add_button("HSLA", pg.Rect(x_col2 + 90, y_pos, 80, ATTR_INPUT_HEIGHT))
        self.attr_toggles.add_button("oklab", pg.Rect(x_col2 + 180, y_pos, 80, ATTR_INPUT_HEIGHT))
        
        # 3. Background Color
        y_pos = 200
        # RGB
        self.attr_inputs['rgb_r'] = TextInput(pg.Rect(x_col2, y_pos, 60, ATTR_INPUT_HEIGHT), "34")
        self.attr_inputs['rgb_g'] = TextInput(pg.Rect(x_col2 + 70, y_pos, 60, ATTR_INPUT_HEIGHT), "34")
        self.attr_inputs['rgb_b'] = TextInput(pg.Rect(x_col2 + 140, y_pos, 60, ATTR_INPUT_HEIGHT), "34")
        
        y_pos = 250
        # HSLA
        self.attr_inputs['hsla_h'] = TextInput(pg.Rect(x_col2, y_pos, 60, ATTR_INPUT_HEIGHT), "0")
        self.attr_inputs['hsla_s'] = TextInput(pg.Rect(x_col2 + 70, y_pos, 60, ATTR_INPUT_HEIGHT), "0")
        self.attr_inputs['hsla_l'] = TextInput(pg.Rect(x_col2 + 140, y_pos, 60, ATTR_INPUT_HEIGHT), "34")
        
        y_pos = 300
        # oklab
        self.attr_inputs['oklab_l'] = TextInput(pg.Rect(x_col2, y_pos, 60, ATTR_INPUT_HEIGHT), "34")
        self.attr_inputs['oklab_a'] = TextInput(pg.Rect(x_col2 + 70, y_pos, 60, ATTR_INPUT_HEIGHT), "0")
        self.attr_inputs['oklab_b'] = TextInput(pg.Rect(x_col2 + 140, y_pos, 60, ATTR_INPUT_HEIGHT), "0")
        
        # 4. Control Buttons
        y_pos = ATTR_MENU_HEIGHT - 70
        self.attr_buttons.append(Button("Back", pg.Rect(x_col1, y_pos, 120, 50), self.go_to_support_menu))
        self.attr_buttons.append(Button("Create Scene", pg.Rect(ATTR_MENU_WIDTH - 170, y_pos, 150, 50), self.validate_and_create_scene))

        # Store all elements for easy event handling
        self.attr_ui_elements = [self.attr_toggles] + self.attr_buttons + list(self.attr_inputs.values())
        
        # Set initial enable state
        self.on_color_space_toggle('oklab') # Default

    def on_color_space_toggle(self, active_option: str):
        """Callback to enable/disable color input fields."""
        # RGB fields
        rgb_enabled = (active_option == 'RGB')
        self.attr_inputs['rgb_r'].set_enabled(rgb_enabled)
        self.attr_inputs['rgb_g'].set_enabled(rgb_enabled)
        self.attr_inputs['rgb_b'].set_enabled(rgb_enabled)
        
        # HSLA fields
        hsla_enabled = (active_option == 'HSLA')
        self.attr_inputs['hsla_h'].set_enabled(hsla_enabled)
        self.attr_inputs['hsla_s'].set_enabled(hsla_enabled)
        self.attr_inputs['hsla_l'].set_enabled(hsla_enabled)
        
        # oklab fields
        oklab_enabled = (active_option == 'oklab')
        self.attr_inputs['oklab_l'].set_enabled(oklab_enabled)
        self.attr_inputs['oklab_a'].set_enabled(oklab_enabled)
        self.attr_inputs['oklab_b'].set_enabled(oklab_enabled)

    def validate_and_create_scene(self):
        """Reads all inputs, validates them, and creates a new scene if valid."""
        print("Validating scene attributes...")
        is_valid = True
        
        # 1. Validate Width/Height
        try:
            width = int(self.attr_inputs['width'].text)
            if not (100 <= width <= 3840): # Min/max screen size
                raise ValueError("Width must be 100-3840")
            self.attr_inputs['width'].error_message = None
        except Exception as e:
            self.attr_inputs['width'].error_message = "Invalid (100-3840)"
            is_valid = False
            
        try:
            height = int(self.attr_inputs['height'].text)
            if not (100 <= height <= 2160):
                raise ValueError("Height must be 100-2160")
            self.attr_inputs['height'].error_message = None
        except Exception as e:
            self.attr_inputs['height'].error_message = "Invalid (100-2160)"
            is_valid = False
            
        # 2. Get Color Space
        color_space = self.attr_toggles.active_option
        bg_color_dict = {}
        
        # 3. Validate Colors (basic int check for now)
        # We will implement real validation later
        try:
            if color_space == 'RGB':
                r = int(self.attr_inputs['rgb_r'].text)
                g = int(self.attr_inputs['rgb_g'].text)
                b = int(self.attr_inputs['rgb_b'].text)
                # TODO: Add real 0-255 validation
                bg_color_dict['rgb'] = (r, g, b)
            elif color_space == 'HSLA':
                h = int(self.attr_inputs['hsla_h'].text)
                s = int(self.attr_inputs['hsla_s'].text)
                l = int(self.attr_inputs['hsla_l'].text)
                # TODO: Add real 0-360/0-100 validation
                bg_color_dict['hsla'] = (h, s, l)
            elif color_space == 'oklab':
                l = int(self.attr_inputs['oklab_l'].text)
                a = int(self.attr_inputs['oklab_a'].text)
                b = int(self.attr_inputs['oklab_b'].text)
                # TODO: Add real validation
                bg_color_dict['oklab'] = (l, a, b)
                # --- TEMP: Store an RGB equivalent for now ---
                # This is a HACK until we build color conversion.
                # We'll just use the oklab 'l' value for gray.
                l_gray = max(0, min(255, int(l * 2.55))) # Rough guess
                bg_color_dict['rgb'] = (l_gray, l_gray, l_gray)

        except Exception as e:
            print(f"Color validation error: {e}")
            is_valid = False
            # TODO: Add error messages to the specific failing fields
            
        if is_valid:
            print("Validation successful! Creating new scene.")
            # Create the new scene
            new_scene = Scene(
                width=width,
                height=height,
                bg_color=bg_color_dict,
                color_space=color_space
            )
            # Switch to the editor
            self.go_to_scene_editor(new_scene)
        else:
            print("Validation failed. Please fix errors.")

    def go_to_scene_editor(self, scene: Scene):
        """Switches the app to the Scene Editor Window."""
        self.scene = scene
        self.app_state = AppState.STATE_SCENE_EDITOR
        self.screen = pg.display.set_mode((self.scene.width, self.scene.height))
        pg.display.set_caption("BallSim — Scene Editor")

    def go_to_support_menu(self):
        """Switches the app state to the Support Menu."""
        self.app_state = AppState.STATE_SUPPORT_MENU
        self.screen = pg.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
        pg.display.set_caption("BallSim")
        self.create_support_menu()

    def go_to_scene_editor_stub(self):
        """Callback for 'New Scene' button."""
        print("Clicked 'New Scene'. Opening Scene Editor with default scene.")
        # TODO: Implement Scene Attributes intermediate window.
        self.go_to_scene_editor(Scene())

    def load_scene_stub(self):
        """Callback for 'Load Scene' button."""
        print("Clicked 'Load Scene'. This will open a file explorer.")
        # TODO: Implement file dialog logic
        pass

    def show_help_stub(self):
        """Callback for 'Help' button."""
        print("Clicked 'Help'. This will open the help window.")
        # TODO: Implement help window
        pass

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
        """Process user input based on the current app state."""

        for event in pg.event.get():
            if event.type == QUIT:
                self.running = False
                return

            if self.app_state == AppState.STATE_SUPPORT_MENU:
                self.handle_events_menu(event)
            elif self.app_state == AppState.STATE_SCENE_ATTRIBUTES:
                self.handle_events_attributes(event)
            elif self.app_state == AppState.STATE_SCENE_EDITOR:
                self.handle_events_editor(event)
    
    def update(self):
        """Update game state based on the current app state."""
        if self.app_state == AppState.STATE_SUPPORT_MENU:
            self.update_menu()
        elif self.app_state == AppState.STATE_SCENE_ATTRIBUTES:
            self.update_attributes()
        elif self.app_state == AppState.STATE_SCENE_EDITOR:
            self.update_editor()
    
    def draw(self):
        """Draw everything to the screen based on the current app state."""
        if self.app_state == AppState.STATE_SUPPORT_MENU:
            self.draw_menu()
        elif self.app_state == AppState.STATE_SCENE_ATTRIBUTES:
            self.draw_attributes()
        elif self.app_state == AppState.STATE_SCENE_EDITOR:
            self.draw_editor()
        
        pg.display.flip()

    def handle_events_menu(self, event):
        """Process input for the support menu."""
        for button in self.menu_buttons:
            button.handle_event(event)

    def update_menu(self):
        """Update logic for the support menu."""
        # TODO: Update when we have logic
        pass

    def draw_menu(self):
        """Draws the support menu GUI."""
        self.screen.fill(MENU_BG_COLOR)
        for button in self.menu_buttons:
            button.draw(self.screen)

    def handle_events_attributes(self, event):
        """Process input for the attributes menu."""
        for element in self.attr_ui_elements:
            element.handle_event(event)

    def update_attributes(self):
        """Update logic for the attributes menu (none for now)."""
        pass

    def draw_attributes(self):
        """Draws the scene attributes menu."""
        self.screen.fill(ATTR_MENU_BG_COLOR)
        
        x_col1 = 50
        
        # Draw labels
        draw_label(self.screen, "Canvas Size:", (x_col1, 50))
        draw_label(self.screen, "W:", (x_col1 + ATTR_LABEL_WIDTH + 5 - 25, 80))
        draw_label(self.screen, "H:", (x_col1 + ATTR_LABEL_WIDTH + ATTR_INPUT_WIDTH + 40 - 25, 80))
        
        draw_label(self.screen, "Color Space:", (x_col1, 120))
        
        draw_label(self.screen, "Background Color:", (x_col1, 170))
        
        draw_label(self.screen, "RGB:", (x_col1, 200), font_size=24)
        draw_label(self.screen, "HSLA:", (x_col1, 250), font_size=24)
        draw_label(self.screen, "oklab:", (x_col1, 300), font_size=24)
        
        # Draw all UI elements
        for element in self.attr_ui_elements:
            element.draw(self.screen)

    def handle_events_editor(self, event):
        """Process user input at every time step."""
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1: # 1 = Left-click
                keys = pg.key.get_pressed()
                mouse_pos = event.pos
                clicked_ball = self.get_ball_at_pos(mouse_pos)

                is_shift = keys[K_LSHIFT] or keys[K_RSHIFT]
                is_del = keys[K_DELETE] or keys[K_BACKSPACE]

                if clicked_ball:
                    if is_shift:
                        self.is_dragging_path = True
                        self.drag_ball = clicked_ball
                    elif is_del:
                        self.scene.remove_ball(clicked_ball)
                else:
                    # Clicked on empty space
                    if not is_shift and not is_del:
                        snapped_pos = self.snap_to_grid(mouse_pos)
                        new_ball = Ball(position=pg.math.Vector2(snapped_pos))
                        self.scene.add_ball(new_ball)
        
        # Handle mouse release to finish creation of a child BallPath
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1: # 1 = Left-click
                if self.is_dragging_path and self.drag_ball:
                    end_pos_snapped = self.snap_to_grid(event.pos)
                    start_pos = self.drag_ball.position

                    if start_pos.distance_to(end_pos_snapped) == 0:
                        # Destroy existing child BallPath
                        self.drag_ball.path = None
                    else:
                        # Create new child BallPath or update current one
                        new_path = BallPath(
                            start_pos=start_pos,
                            end_pos=pg.math.Vector2(end_pos_snapped)
                        )
                        self.drag_ball.path = new_path
            # Reset dragging state
                    self.is_dragging_path = False
                    self.drag_ball = None

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                print("Escape pressed. Returning to support menu.")
                # TODO: Add AUTOSAVE logic here later
                self.go_to_support_menu()

    # TODO: Add support for other user events.
    
    def update_editor(self):
        """Update logic for the scene editor."""
        pass

    def draw_editor(self):
        """Draws the scene editor window."""
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
            if ball.path:
                self.draw_ball_path(ball.path.start_pos, ball.path.end_pos, PATH_COLOR)
        
        if self.is_dragging_path and self.drag_ball:
            mouse_pos = pg.mouse.get_pos()
            snapped_end = self.snap_to_grid(mouse_pos)
            self.draw_ball_path(self.drag_ball.position, snapped_end, PATH_COLOR)
    
    def get_ball_at_pos(self, pos: tuple[int, int]) -> Optional[Ball]:
        """Finds the top-most ball at a given screen position."""
        # Iterate in reverse to find the ball of the highest layer
        for ball in reversed(self.scene.balls):
            if ball.is_colliding_with_point(pos):
                return ball
        return None

    def draw_ball_path(self, start_pos: pg.math.Vector2, end_pos: pg.math.Vector2, color: pg.Color):
        """Draws a vector onto the canvas, representing a BallPath."""
        pg.draw.line(self.screen, color, start_pos, end_pos, PATH_LINE_WIDTH)
        try:
            # Get unit vector for BallPath direction
            direction = (end_pos - start_pos).normalize()
            p1 = end_pos - direction * PATH_ARROW_SIZE + direction.rotate(90) * (PATH_ARROW_SIZE / 2)
            p2 = end_pos - direction * PATH_ARROW_SIZE + direction.rotate(-90) * (PATH_ARROW_SIZE / 2)
            pg.draw.polygon(self.screen, color, [end_pos, p1, p2])
        except ValueError:
            # If start_pos == end_pos then direction would attempt to normalize the zero vector
            pass # Don't draw arrowhead shape if we have a line of zero length
    
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