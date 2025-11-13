import pygame as pg

BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (255, 255, 255)
DEFAULT_FONT_SIZE = 32

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
    