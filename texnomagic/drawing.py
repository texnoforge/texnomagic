import csv
import itertools
import math
import numpy as np

import cairo


RESOLUTION_DEFAULT = 1000
LINE_WIDTH_DEFAULT = 0.04
MARGIN_DEFAULT = 0.05

EXPORT_FORMATS = ['svg', 'png']
EXPORT_FORMAT_DEFAULT = 'svg'


class TexnoMagicDrawing:

    def __init__(self, path=None, curves=None, points_range=1000.0):
        self.path = path
        self.points_range = points_range
        self._curves = None
        self._points = None
        self._file_size = None
        if curves:
            self.set_curves(curves)

    @property
    def curves(self):
        if self._curves is None:
            self.load_curves()
        return self._curves

    @property
    def points(self):
        if self._points is None:
            self.load_curves()
        return self._points

    @property
    def file_size(self):
        if self._file_size is None:
            self._file_size = self.path.stat().st_size
        return self._file_size

    @property
    def name(self):
        if self.path:
            return self.path.name
        return None

    def set_curves(self, curves):
        # keep all points in single continuous numpy array
        self._points = np.array(list(itertools.chain(*curves)), dtype=np.float64)
        self._curves = []
        i = 0
        for curve in curves:
            n = len(curve)
            # curves are numpy views into main points array
            cview = self._points[i:i+n]
            self._curves.append(cview)
            i += n

    def load(self, path=None):
        if path:
            self.path = path
        return self

    def load_curves(self):
        curves = []
        curve = []
        with self.path.open('r') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or '' in row:
                    curves.append(curve)
                    curve = []
                    continue
                point = list(map(float, row[:2]))
                curve.append(point)
        curves.append(curve)
        self.set_curves(curves)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open('w', newline='') as f:
            writer = csv.writer(f)
            first = True
            for curve in self.curves:
                if first:
                    first = False
                else:
                    # curves separator
                    writer.writerow([None, None])
                writer.writerows(curve.tolist())

    def normalize(self):
        """
        normalize drawing points in-place into <0, self.points_range> range
        """
        # move to [0,0]
        self._points -= np.min(self._points, axis=0)
        # normalize
        k = self.points_range / np.max((np.max(np.max(self._points, axis=0)), 0.2))
        self._points *= k
        # center
        offset = (self.points_range - np.max(self._points, axis=0)) / 2
        self._points += offset

    def flip_y_axis(self):
        """
        flip drawing along Y axis in-place

        useful for compatibility with systems that use different Y axis sign
        """
        self._points[:,1] = self.points_range - self._points[:,1]

    def curves_fit_area(self, pos, size):
        """
        return curves scaled to fit area

        useful for drawing curves in UI
        """
        pos = np.array(pos)
        size = np.array(size)

        k = np.min(size) / self.points_range
        max_range = self.points_range * k

        offset = pos + (size - max_range) / 2

        scurves = []
        for curve in self.curves:
            if len(curve) > 0:
                scurve = curve * k + offset
            else:
                scurve = curve
            scurves.append(scurve)
        return scurves

    def delete(self):
        if not self.path or not self.path.exists():
            return
        self.path.unlink()

    def render_cairo(self,
                     cairo_context,
                     res=RESOLUTION_DEFAULT,
                     margin=MARGIN_DEFAULT,
                     line_width=LINE_WIDTH_DEFAULT):
        """
        Render drawing path using cairo surface context.

        This is used to render curves as SVG and PNG - see cairo docs.
        """
        line_width = min(0.5, line_width)
        margin = min(0.45, line_width)

        ctx = cairo_context
        ctx.scale(res, res)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        ctx.fill()

        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.set_line_width(line_width)
        ctx.set_line_cap(cairo.LineCap.ROUND)
        ctx.set_line_join(cairo.LineJoin.ROUND)

        margin_real = margin + 0.5 * line_width
        content_size = 1.0 - 2 * margin_real
        for curve in self.curves_fit_area(np.full(2, margin_real), np.full(2, content_size)):
            x, y = curve[0]
            ctx.move_to(x, y)
            for x, y in curve[1:]:
                ctx.line_to(x, y)
            ctx.stroke()

        return ctx

    def export(self, out_path,
               format=EXPORT_FORMAT_DEFAULT,
               res=RESOLUTION_DEFAULT,
               margin=MARGIN_DEFAULT,
               line_width=LINE_WIDTH_DEFAULT):

        assert(format in EXPORT_FORMATS)
        if format == 'svg':
            surface = cairo.SVGSurface(out_path, res, res)
        else:
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, res, res)
        ctx = cairo.Context(surface)

        self.render_cairo(ctx, res=res, line_width=line_width, margin=margin)

        if format == 'png':
            surface.write_to_png(out_path)

        surface.finish()
        surface.flush()

    def pretty(self, size=True):
        n_curves = len(self.curves)
        n_points = len(self.points)
        s = f"[white bold]{self.path.name}[/]: "
        s += f"{n_points} points, {n_curves} curves"
        if size:
            fsize = math.ceil(self.file_size / 1024.0)
            s += f", {fsize} kB"
        return s

    def __repr__(self):
        if self._curves is None:
            info = "curves not loaded"
        else:
            info = f"{len(self._points)} points, {len(self._curves)} curves"
        return f"<TexnoMagicDrawing @ {self.path}: {info}>"
