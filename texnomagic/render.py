import math

from texnomagic import console
from texnomagic import ex

PIL_AVAILABLE = False
try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    class Image:
        pass


def ensure_pil():
    if not PIL_AVAILABLE:
        console.print("[red]Python module required for this operation isn't available: [bold]PIL (pillow)[/][/]")
        raise ex.ModuleNotAvailable('PIL')


def render_drawing(drawing, res=1000, line_width=None, image=None) -> Image:
    """
    Render TexnoMagicDrawing into a PIL.Image (raster).
    """
    ensure_pil()

    if not image:
        image = Image.new("L", (res, res), 0)
    if not line_width:
        line_width = max(round(res / 20.0), 1)

    draw = ImageDraw.Draw(image)

    ew = math.floor(line_width / 2.0) - 1

    def draw_point(x, y):
        if line_width < 4:
            return
        draw.ellipse((x - ew, y - ew, x + ew, y + ew), fill=255, width=0)

    for curve in drawing.curves_fit_area([0.05 * res, 0.05 * res], [0.9 * res, 0.9 * res]):
        x_p, y_p = curve[0]
        draw_point(x_p, y_p)
        for x, y in curve[1:]:
            draw.line((x_p, y_p, x, y), fill=255, width=line_width)
            draw_point(x, y)
            x_p, y_p = x, y

    return image
