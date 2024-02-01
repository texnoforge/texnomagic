import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame  # noqa


EXIT_KEYS = [pygame.K_ESCAPE, pygame.K_q, pygame.K_SPACE, pygame.K_KP_ENTER]


def is_exit_event(event):
    if event.type == pygame.QUIT:
        return True
    elif event.type == pygame.KEYDOWN:
        if event.key in EXIT_KEYS:
            return True
    return False


def surface_cairo2pygame(surface):
    buf = surface.get_data()
    ssize = (surface.get_width(), surface.get_height())
    img = pygame.image.frombuffer(buf, ssize, "ARGB")
    return img
