try:
    import json
    import sys
    import math
    import os
    import pygame as pg
    from pygame.locals import *
    from pathlib import Path
    from datetime import datetime
    from typing import List, Dict, Any, Optional
except ImportError as err:
    print(f"Failed to load module. {err}")
    sys.exit(2)

# Initial Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
SIMULATION_FPS = 60

# --- UI Panel Dimensions ---
TOOLBAR_WIDTH = 80
PROPERTIES_WIDTH = 240
FILE_MENU_HEIGHT = 40
CANVAS_RECT = pg.Rect(
    TOOLBAR_WIDTH, 
    FILE_MENU_HEIGHT, 
    SCREEN_WIDTH - TOOLBAR_WIDTH - PROPERTIES_WIDTH, 
    SCREEN_HEIGHT - FILE_MENU_HEIGHT
)

# --- Colors ---
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
C_GRAY_DARK = (40, 40, 40)
C_GRAY_MED = (60, 60, 60)
C_GRAY_LIGHT = (100, 100, 100)
C_BLUE = (100, 100, 255)
C_RED = (255, 100, 100)

# --- Directory Setup (using pathlib) ---
DIR_MAIN = Path(__file__).parent
DIR_SAVED_SCENES = DIR_MAIN / "gemini_saved_scenes"
DIR_EXPORTS = DIR_MAIN / "gemini_exports"

# Ensure directories exist
DIR_SAVED_SCENES.mkdir(exist_ok=True)
DIR_EXPORTS.mkdir(exist_ok=True)

# --- Physics / Object Classes ---

class Ball:
    """Represents a single ball in the simulation."""
    def __init__(self, position: pg.math.Vector2, velocity: pg.math.Vector2, 
                 radius: int, color: Dict[str, Any], layer: int):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.color_data = color  # e.g., {'space': 'oklab', 'value': [0.7, 0.1, 0.1]}
        self.layer = layer
        
        # TODO: This color should be calculated from color_data
        self.render_color = C_RED 

    def update(self, dt: float):
        """Update ball's position based on velocity. dt is delta time."""
        self.position += self.velocity * dt

    def draw(self, screen: pg.Surface, camera_offset: pg.math.Vector2):
        """Draws the ball onto the screen."""
        draw_pos = (
            int(self.position.x + camera_offset.x), 
            int(self.position.y + camera_offset.y)
        )
        pg.draw.circle(screen, self.render_color, draw_pos, self.radius)

    def get_rect(self) -> pg.Rect:
        """Returns a rect for collision/selection detection."""
        return pg.Rect(
            self.position.x - self.radius,
            self.position.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        
    def contains_point(self, point: pg.math.Vector2) -> bool:
        """Check if a point is inside this ball."""
        return self.position.distance_to(point) <= self.radius

    # --- Save/Load Methods ---
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the Ball object into a JSON-friendly dictionary."""
        return {
            "position": [self.position.x, self.position.y],
            "velocity": [self.velocity.x, self.velocity.y],
            "radius": self.radius,
            "color": self.color_data,
            "layer": self.layer
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ball':
        """Creates a new Ball object from a dictionary."""
        return cls(
            position=pg.math.Vector2(data["position"][0], data["position"][1]),
            velocity=pg.math.Vector2(data["velocity"][0], data["velocity"][1]),
            radius=data["radius"],
            color=data["color"],
            layer=data["layer"]
        )

# --- Scene Management Class ---

class Scene:
    """Manages all objects, properties, and serialization for a scene."""
    def __init__(self, width: int, height: int, bg_color: Dict, 
                 framerate: int, color_space: str):
        self.width = width
        self.height = height
        self.bg_color_data = bg_color
        self.framerate = framerate
        self.color_space = color_space
        self.balls: List[Ball] = []
        
        # TODO: This color should be calculated from bg_color_data
        self.render_bg_color = C_GRAY_DARK

    def add_ball(self, ball: Ball):
        self.balls.append(ball)
        
    def get_ball_at_pos(self, canvas_pos: pg.math.Vector2) -> Optional[Ball]:
        """Finds the topmost ball at a given canvas position."""
        # Check in reverse order (top layers first)
        for ball in sorted(self.balls, key=lambda b: b.layer, reverse=True):
            if ball.contains_point(canvas_pos):
                return ball
        return None

    def update(self, dt: float):
        """Update all objects in the scene."""
        for ball in self.balls:
            ball.update(dt)
        
        # TODO: Add your collision logic here if not using Pymunk
        # self.handle_collisions()

    def draw(self, screen: pg.Surface, camera_offset: pg.math.Vector2):
        """Draw the entire scene."""
        # Draw background (we fill the whole canvas)
        screen.fill(self.render_bg_color)
        
        # TODO: Draw a grid relative to the camera_offset
        
        # Draw balls, sorted by layer
        for ball in sorted(self.balls, key=lambda b: b.layer):
            ball.draw(screen, camera_offset)

    # --- Save/Load Methods ---

    def save_to_json(self, filename: str):
        """Saves the current scene state to a JSON file."""
        scene_data = {
            "scene_settings": {
                "width": self.width,
                "height": self.height,
                "background_color": self.bg_color_data,
                "framerate": self.framerate,
                "color_space": self.color_space,
                "last_accessed": datetime.now().isoformat()
            },
            "objects": {
                "balls": [ball.to_dict() for ball in self.balls]
            }
        }
        
        filepath = DIR_SAVED_SCENES / f"{filename}.json"
        try:
            with open(filepath, 'w') as f:
                json.dump(scene_data, f, indent=4)
            print(f"Scene saved to {filepath}")
        except Exception as e:
            print(f"Error saving scene: {e}")

    @classmethod
    def load_from_json(cls, filename: str) -> 'Scene':
        """Loads a scene from a JSON file and returns a new Scene object."""
        filepath = DIR_SAVED_SCENES / f"{filename}.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"No scene file found at {filepath}")
            
        with open(filepath, 'r') as f:
            scene_data = json.load(f)
        
        settings = scene_data["scene_settings"]
        new_scene = cls(
            width=settings["width"],
            height=settings["height"],
            bg_color=settings["background_color"],
            framerate=settings["framerate"],
            color_space=settings["color_space"]
        )
        
        for ball_data in scene_data["objects"]["balls"]:
            new_ball = Ball.from_dict(ball_data)
            new_scene.add_ball(new_ball)
            
        print(f"Scene loaded from {filepath}")
        return new_scene

# --- Main Application Class ---

class App:
    """Manages the overall application state, GUI, and loops."""
    
    def __init__(self):
        pg.init()
        pg.display.set_caption("Visual Perception Engine")
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("Arial", 18)
        self.font_title = pg.font.SysFont("Arial", 30)
        
        self.running = True
        self.app_state = "STARTUP_MENU"  # STARTUP_MENU, EDITOR, SIMULATION
        
        self.current_scene: Optional[Scene] = None
        
        # --- Editor State ---
        self.editor_tool = "NORMAL"  # NORMAL, PLACE_BALL, PLACE_VECTOR
        self.selected_object: Optional[Ball] = None
        self.is_dragging_object = False
        self.is_panning = False
        self.pan_start_pos = pg.math.Vector2(0, 0)
        self.camera_offset = pg.math.Vector2(CANVAS_RECT.x, CANVAS_RECT.y) # Start with canvas origin at top-left
        
        # --- UI Element Rects (for click detection) ---
        self.ui_elements = {
            "file_menu": pg.Rect(0, 0, SCREEN_WIDTH, FILE_MENU_HEIGHT),
            "toolbar": pg.Rect(0, FILE_MENU_HEIGHT, TOOLBAR_WIDTH, SCREEN_HEIGHT - FILE_MENU_HEIGHT),
            "properties": pg.Rect(SCREEN_WIDTH - PROPERTIES_WIDTH, FILE_MENU_HEIGHT, PROPERTIES_WIDTH, SCREEN_HEIGHT - FILE_MENU_HEIGHT),
            # --- Menu Buttons ---
            "btn_new_scene": pg.Rect(50, 100, 200, 50),
            "btn_load_scene": pg.Rect(50, 170, 200, 50),
            # --- Editor Buttons ---
            "btn_save": pg.Rect(10, 5, 50, 30),
            "btn_run": pg.Rect(70, 5, 50, 30),
            "btn_tool_normal": pg.Rect(10, FILE_MENU_HEIGHT + 10, 60, 40),
            "btn_tool_ball": pg.Rect(10, FILE_MENU_HEIGHT + 60, 60, 40),
            "btn_tool_vector": pg.Rect(10, FILE_MENU_HEIGHT + 110, 60, 40),
        }

    def run(self):
        """Main application loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            # Get mouse position once
            self.mouse_pos = pg.math.Vector2(pg.mouse.get_pos())
            
            # --- State Machine ---
            if self.app_state == "STARTUP_MENU":
                self.handle_startup_events()
                self.draw_startup_menu()
            elif self.app_state == "EDITOR":
                self.handle_editor_events()
                self.update_editor(dt)
                self.draw_editor()
            elif self.app_state == "SIMULATION":
                self.handle_simulation_events()
                self.update_simulation(dt)
                self.draw_simulation()
                
            pg.display.flip()
            
        pg.quit()
        sys.exit()

    def draw_text(self, text: str, pos: tuple, color=C_WHITE, font=None):
        """Helper function to draw text."""
        if font is None:
            font = self.font
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, pos)

    # --- STARTUP MENU ---
    
    def handle_startup_events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if self.ui_elements["btn_new_scene"].collidepoint(event.pos):
                    # Create a default new scene
                    self.current_scene = Scene(
                        width=2000, height=2000,
                        bg_color={'space': 'rgb', 'value': [10, 10, 40]},
                        framerate=60, color_space='rgb'
                    )
                    self.app_state = "EDITOR"
                elif self.ui_elements["btn_load_scene"].collidepoint(event.pos):
                    # TODO: Add a file dialog
                    # For now, just load a hardcoded scene if it exists
                    try:
                        self.current_scene = Scene.load_from_json("my_test_scene")
                        self.app_state = "EDITOR"
                    except FileNotFoundError:
                        print("'my_test_scene.json' not found. Create and save one first.")

    def draw_startup_menu(self):
        self.screen.fill(C_GRAY_DARK)
        self.draw_text("Visual Perception Engine", (50, 40), font=self.font_title)
        
        # New Scene Button
        pg.draw.rect(self.screen, C_GRAY_MED, self.ui_elements["btn_new_scene"])
        self.draw_text("Create New Scene", (self.ui_elements["btn_new_scene"].x + 30, self.ui_elements["btn_new_scene"].y + 15))
        
        # Load Scene Button
        pg.draw.rect(self.screen, C_GRAY_MED, self.ui_elements["btn_load_scene"])
        self.draw_text("Load Scene", (self.ui_elements["btn_load_scene"].x + 55, self.ui_elements["btn_load_scene"].y + 15))
        
        # TODO: Add logic for thumbnails and recent scenes

    # --- SCENE EDITOR ---

    def is_pos_on_canvas(self, pos: pg.math.Vector2) -> bool:
        """Check if a screen position is within the drawable canvas area."""
        return CANVAS_RECT.collidepoint(pos)
        
    def screen_to_canvas(self, screen_pos: pg.math.Vector2) -> pg.math.Vector2:
        """Converts screen coordinates to scene (canvas) coordinates."""
        return screen_pos - self.camera_offset
        
    def canvas_to_screen(self, canvas_pos: pg.math.Vector2) -> pg.math.Vector2:
        """Converts scene (canvas) coordinates to screen coordinates."""
        return canvas_pos + self.camera_offset

    def handle_editor_events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                self.running = False
            
            # --- Mouse Button Down ---
            if event.type == MOUSEBUTTONDOWN:
                # 1. Check for UI clicks first
                if self.ui_elements["btn_save"].collidepoint(event.pos):
                    self.current_scene.save_to_json("my_test_scene") # TODO: Add "Save As"
                
                elif self.ui_elements["btn_run"].collidepoint(event.pos):
                    self.app_state = "SIMULATION"
                
                elif self.ui_elements["btn_tool_normal"].collidepoint(event.pos):
                    self.editor_tool = "NORMAL"
                
                elif self.ui_elements["btn_tool_ball"].collidepoint(event.pos):
                    self.editor_tool = "PLACE_BALL"
                
                elif self.ui_elements["btn_tool_vector"].collidepoint(event.pos):
                    self.editor_tool = "PLACE_VECTOR"

                # 2. Check for canvas clicks
                elif self.is_pos_on_canvas(self.mouse_pos):
                    canvas_pos = self.screen_to_canvas(self.mouse_pos)
                    
                    if event.button == 1: # Left Click
                        if self.editor_tool == "NORMAL":
                            self.selected_object = self.current_scene.get_ball_at_pos(canvas_pos)
                            if self.selected_object:
                                self.is_dragging_object = True
                        
                        elif self.editor_tool == "PLACE_BALL":
                            new_ball = Ball(
                                position=canvas_pos,
                                velocity=pg.math.Vector2(0, 0),
                                radius=20,
                                color={'space': 'rgb', 'value': [255, 0, 0]},
                                layer=1
                            )
                            self.current_scene.add_ball(new_ball)
                            
                        elif self.editor_tool == "PLACE_VECTOR":
                            # TODO: Logic for click-and-drag vector placement
                            pass
                            
                    elif event.button == 3: # Right Click (Pan)
                        self.is_panning = True
                        self.pan_start_pos = self.mouse_pos
                        
            # --- Mouse Button Up ---
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging_object = False
                if event.button == 3:
                    self.is_panning = False
                    
            # --- Mouse Motion ---
            if event.type == MOUSEMOTION:
                if self.is_dragging_object and self.selected_object:
                    canvas_pos = self.screen_to_canvas(self.mouse_pos)
                    self.selected_object.position = canvas_pos
                
                elif self.is_panning:
                    self.camera_offset += self.mouse_pos - self.pan_start_pos
                    self.pan_start_pos = self.mouse_pos
                    # Clamp camera offset to prevent scrolling too far
                    self.camera_offset.x = min(CANVAS_RECT.x, self.camera_offset.x)
                    self.camera_offset.y = min(CANVAS_RECT.y, self.camera_offset.y)


    def update_editor(self, dt: float):
        # No physics updates in the editor
        pass

    def draw_editor(self):
        self.screen.fill(C_GRAY_DARK)
        
        # 1. Draw Scene Canvas
        # We use a subsurface to clip the scene drawing to the canvas rect
        canvas_surface = self.screen.subsurface(CANVAS_RECT)
        if self.current_scene:
            # We pass the relative camera offset
            relative_camera_offset = self.camera_offset - pg.math.Vector2(CANVAS_RECT.topleft)
            self.current_scene.draw(canvas_surface, relative_camera_offset)
            
        # Draw selection highlight
        if self.selected_object:
            screen_pos = self.canvas_to_screen(self.selected_object.position)
            if CANVAS_RECT.collidepoint(screen_pos): # Only draw if on screen
                r = self.selected_object.radius + 4
                pg.draw.rect(self.screen, C_WHITE, (screen_pos.x - r, screen_pos.y - r, r*2, r*2), 2)


        # 2. Draw UI Panels
        pg.draw.rect(self.screen, C_BLACK, self.ui_elements["file_menu"])
        pg.draw.rect(self.screen, C_GRAY_MED, self.ui_elements["toolbar"])
        pg.draw.rect(self.screen, C_GRAY_MED, self.ui_elements["properties"])
        
        # --- File Menu Buttons ---
        pg.draw.rect(self.screen, C_GRAY_LIGHT, self.ui_elements["btn_save"])
        self.draw_text("Save", (self.ui_elements["btn_save"].x+10, self.ui_elements["btn_save"].y+7), C_BLACK)
        pg.draw.rect(self.screen, C_BLUE, self.ui_elements["btn_run"])
        self.draw_text("Run", (self.ui_elements["btn_run"].x+10, self.ui_elements["btn_run"].y+7), C_BLACK)
        
        # --- Toolbar Buttons ---
        pg.draw.rect(self.screen, C_GRAY_LIGHT if self.editor_tool != "NORMAL" else C_WHITE, self.ui_elements["btn_tool_normal"])
        self.draw_text("Select", (self.ui_elements["btn_tool_normal"].x+5, self.ui_elements["btn_tool_normal"].y+12), C_BLACK)
        
        pg.draw.rect(self.screen, C_GRAY_LIGHT if self.editor_tool != "PLACE_BALL" else C_WHITE, self.ui_elements["btn_tool_ball"])
        self.draw_text("Ball", (self.ui_elements["btn_tool_ball"].x+15, self.ui_elements["btn_tool_ball"].y+12), C_BLACK)
        
        pg.draw.rect(self.screen, C_GRAY_LIGHT if self.editor_tool != "PLACE_VECTOR" else C_WHITE, self.ui_elements["btn_tool_vector"])
        self.draw_text("Vector", (self.ui_elements["btn_tool_vector"].x+5, self.ui_elements["btn_tool_vector"].y+12), C_BLACK)

        # --- Properties Panel ---
        self.draw_text("Properties", (self.ui_elements["properties"].x + 10, self.ui_elements["properties"].y + 10))
        if self.selected_object:
            self.draw_text(f"Selected: Ball", (self.ui_elements["properties"].x + 10, self.ui_elements["properties"].y + 40))
            self.draw_text(f"Pos: {self.selected_object.position.x:.1f}, {self.selected_object.position.y:.1f}", (self.ui_elements["properties"].x + 10, self.ui_elements["properties"].y + 60))
            self.draw_text(f"Radius: {self.selected_object.radius}", (self.ui_elements["properties"].x + 10, self.ui_elements["properties"].y + 80))
            # TODO: Add inputs to change these values
            
    # --- SIMULATION ---
    
    def handle_simulation_events(self):
        for event in pg.event.get():
            if event.type == QUIT:
                self.running = False
            # TODO: Add a "Stop" button to return to editor
            # if event.type == MOUSEBUTTONDOWN and stop_button.collidepoint(event.pos):
            #     self.app_state = "EDITOR"
            #     # You might want to reset the scene
            #     self.current_scene = Scene.load_from_json("my_test_scene") 
    
    def update_simulation(self, dt: float):
        if self.current_scene:
            self.current_scene.update(dt)
            
    def draw_simulation(self):
        # In simulation, the scene takes up the whole screen
        # We can use a simpler camera or just lock it
        self.screen.fill(C_BLACK)
        if self.current_scene:
            # Draw scene with a 0,0 offset
            self.current_scene.draw(self.screen, pg.math.Vector2(0, 0))
            
        # TODO: Draw a "Stop" button
        self.draw_text("SIMULATION RUNNING... (Press [?] to stop)", (10, 10))
        

# --- Main Execution ---
if __name__ == "__main__":
    app = App()
    app.run()