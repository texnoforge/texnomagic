import math
import numpy as np

import cairo

from texnomagic import drawing
from texnomagic.gui import gui_common
from texnomagic.gui.gui_common import pygame


def show_drawings_gui(
        drawings,
        resolution=drawing.RESOLUTION_DEFAULT,
        line_width=drawing.LINE_WIDTH_DEFAULT,
        margin=drawing.MARGIN_DEFAULT,
        merge=False):

    n_drawings = len(drawings)

    pygame.init()
    pygame.event.set_blocked(pygame.MOUSEMOTION)

    if n_drawings == 1:
        pygame.display.set_caption(f'TexnoMagic Drawing: {drawings[0].name}')
    elif n_drawings > 1:
        pygame.display.set_caption(f'{n_drawings} TexnoMagic Drawings')

    screen_size = np.full(2, resolution)
    if merge:
        n_cols = 1
        res = resolution
    else:
        n_cols = math.ceil(math.sqrt(n_drawings))
        res = int(resolution / n_cols)

    print(f"{n_drawings} drawings, {n_cols}x{n_cols} grid")

    screen = pygame.display.set_mode(screen_size)
    screen.fill((0, 0, 0))

    col, row = 0, 0
    for d in drawings:
        offset = np.array([col * res, row * res])
        cairo_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, res, res)
        ctx = cairo.Context(cairo_surface)
        d.render_cairo(ctx, res=res, line_width=line_width, margin=margin)
        pygame_surface = gui_common.surface_cairo2pygame(cairo_surface)
        pygame_surface.convert_alpha()
        screen.blit(pygame_surface, offset)

        if not merge:
            col += 1
            if col >= n_cols:
                col = 0
                row += 1

    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if gui_common.is_exit_event(event):
                return True

    pygame.quit()
