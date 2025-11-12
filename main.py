__version__ = '0.0'

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

dir_main = os.path.split(os.path.abspath(__file__))[0]
dir_saved_scenes = os.path.join(dir_main, "saved_scenes")
dir_exports = os.path.join(dir_main, "exports")


#   Resource Acquisition for Startup Menu:
#       Load list of all saved scenes
#       Render thumbnails for:
#        - (2) Two most recently saved scenes
#        - (1) Autosaved scene (most recently open scene, even if it was closed without saving)

#   Startup Menu (GUI):
#       - Create new scene
#       - Load scene
#       - Import scene
#         - Recent scenes shown below

#   Scene Editing Loop (GUI):
#       - Toolbar on left side of screen allows a normal cursor (hold for grabby hand),
#           Ball placement, Vector placement
#         - Normal cursor:
#           - click object with normal cursor (Ball or Path or Vector) to select. Properties tab will display
#               object info on right side of screen
#           - hold and drag object with normal cursorto move it somewhere else.
#           - click on grid with Ball Placement cursor to place a default Ball object
#           - click and drag on Ball with Vector Placement cursor to place a default Vector object in a specified direction
#       - File menu on top of screen with save and export options (JSON, mp4) and a Run simulation button
#           

class BallPath:
    """Represents the behavior a ball will follow during the simulation"""

    def __init__(self, parent: Ball, end_pos: pg.math.Vector2, start_time: int, end_time: int, path_type="linear"):
        self.start_pos = Ball.position
        self.end_pos = end_pos
        self.start_time = start_time
        self.end_time = end_time
        self.path_type = path_type
        self.layer = -1

    

class Ball:
    """Represents a single ball in a simulation."""

    def __init__(self, position: pg.math.Vector2, velocity: pg.math.Vector2,
                 radius: int, color: Dict[str, Any], layer: int, path: BallPath):
        self.position = position
        self.velocity = velocity
        self.radius = radius
        self.color_data = color # Color Space -> Color Values e.g. {'space': 'oklab', 'value': [0.7, 0.1, 0.1]}
        self.layer = layer

        # TODO: This color should be calculated from color_data
        self.render_color = (0, 0, 0)

    def update(self, dt: int):
        """Update ball's position based on its path."""
        self.position += 