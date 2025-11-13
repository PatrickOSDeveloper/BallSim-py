import pygame as pg
from typing import Dict

BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (255, 255, 255)
DEFAULT_FONT_SIZE = 32

TEXT_INPUT_COLOR = (200, 200, 200)
TEXT_INPUT_ACTIVE_COLOR = (255, 255, 255)
TEXT_INPUT_TEXT_COLOR = (0, 0, 0)
TEXT_INPUT_FADED_COLOR = (150, 150, 150)
LABEL_TEXT_COLOR = (255, 255, 255)
ERROR_TEXT_COLOR = (255, 100, 100)

TOGGLE_ACTIVE_COLOR = (170, 170, 170)
TOGGLE_INACTIVE_COLOR = (100, 100, 100)
TOGGLE_HOVER_COLOR = (150, 150, 150)


class Button:
    """A clickable, text-based button."""

    def __init__(self, text: str, rect: pg.Rect, callback: callable):
        self.text = text
        self.rect = rect
        self.callback = callback # The function to call when the button is clicked
        self.is_hovered = False

        try:
            self.font = pg.font.Font(None, DEFAULT_FONT_SIZE)
        except Exception:
            self.font = pg.font.SysFont('arial', DEFAULT_FONT_SIZE)

    def handle_event(self, event: pg.event.Event):
        """Checks for clicks and hover state."""
        if event.type == pg.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered: # 1 = Left-click
                self.callback() # Execute the function stored in this button
    
    def draw(self, surface: pg.Surface):
        """Draws the button onto a Surface."""
        # Determine what color the button currently should be
        bg_color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pg.draw.rect(surface, bg_color, self.rect, border_radius=5)

        # Render button text
        text_surf = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)

        # Blit text
        surface.blit(text_surf, text_rect)

class TextInput:
    """A text input box."""
    def __init__(self, rect: pg.Rect, initial_text: str = "", font_size: int = DEFAULT_FONT_SIZE):
        self.rect = rect
        self.text = initial_text
        self.is_active = False
        self.is_enabled = True
        self.error_message = None
    
        try:
            self.font = pg.font.Font(None, font_size)
            self.error_font = pg.font.Font(None, font_size // 2)
        except Exception:
            self.font = pg.font.SysFont('arial', font_size)
            self.error_font = pg.font.SysFont('arial', font_size // 2)
    
    def handle_event(self, event: pg.event.Event):
        """Handles user input for the text box."""
        if not self.is_enabled:
            self.is_active = False
            return
        
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1: # Left-click
                self.is_active = self.rect.collidepoint(event.pos)
        
        if event.type == pg.KEYDOWN and self.is_active:
            if event.key == pg.K_RETURN:
                self.is_active = False
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            
            self.error_message = None
    
    def draw(self, surface: pg.Surface):
        """Draws the text input box."""

        if not self.is_enabled:
            bg_color = TEXT_INPUT_FADED_COLOR
            text_color = TEXT_INPUT_TEXT_COLOR
        else:
            bg_color = TEXT_INPUT_ACTIVE_COLOR if self.is_active else TEXT_INPUT_COLOR
            text_color = TEXT_INPUT_TEXT_COLOR
        
        pg.draw.rect(surface, bg_color, self.rect, border_radius=3)

        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(centery=self.rect.centery, left=self.rect.left + 5)
        surface.blit(text_surf, text_rect)

        if self.is_active and self.is_enabled:
            cursor_x = text_rect.right + 2
            if cursor_x > self.rect.right - 2:
                cursor_x - self.rect.right - 2
            cursor_start = (cursor_x, self.rect.top + 5)
            cursor_end = (cursor_x, self.rect.bottom - 5)
            if pg.time.get_ticks() % 1000 < 500:
                pg.draw.line(surface, text_color, cursor_start, cursor_end, 2)
        
        if self.error_message:
            error_surf = self.error_font.render(self.error_message, True, ERROR_TEXT_COLOR)
            error_rect = error_surf.get_rect(centery=self.rect.centery + 22, left=self.rect.left)
            surface.blit(error_surf, error_rect)
    
    def set_enabled(self, enabled: bool):
        """Enables or disables the text field."""
        self.is_enabled = enabled
        if not enabled:
            self.is_active = False
    
class ToggleButtonGroup:
    """Manages a group of toggle buttons, ensuring exactly one is active at a time."""
    def __init__(self, active_option: str, on_toggle: callable):
        self.buttons: Dict[str, pg.Rect] = {}
        self.active_option = active_option
        self.on_toggle = on_toggle
        self.hovered_option = None

        try:
            self.font = pg.font.Font(None, 24)
        except Exception:
            self.font = pg.font.SysFont('arial', 24)

    def add_button(self, option_name: str, rect: pg.Rect):
        """Adds a button to the group."""
        self.buttons[option_name] = rect

    def handle_event(self, event: pg.event.Event):
        """Handles clicks and hover for all buttons in the group."""
        if event.type == pg.MOUSEMOTION:
            self.hovered_option = None
            for option, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    self.hovered_option = option
                    break

        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                for option, rect in self.buttons.items():
                    if rect.collidepoint(event.pos):
                        if self.active_option != option:
                            self.active_option = option
                            self.on_toggle(self.active_option)
                        break

    def draw(self, surface: pg.Surface):
        """Draws all buttons in the group."""
        for option, rect in self.buttons.items():
            if option == self.active_option:
                bg_color = TOGGLE_ACTIVE_COLOR
            elif option == self.hovered_option:
                bg_color = TOGGLE_HOVER_COLOR
            else:
                bg_color = TOGGLE_INACTIVE_COLOR

            pg.draw.rect(surface, bg_color, rect, border_radius=5)

            text_surf = self.font.render(option, True, BUTTON_TEXT_COLOR)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

    
def draw_label(surface: pg.Surface, text: str, pos: tuple[int, int],
               font_size: int = DEFAULT_FONT_SIZE, color: pg.Color = LABEL_TEXT_COLOR):
    """Draws a simple text label."""
    try:
        font = pg.font.Font(None, font_size)
    except Exception:
        font = pg.font.SysFont('arial', font_size)

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(topleft=pos)
    surface.blit(text_surf, text_rect)