import csv
import itertools
import numpy as np


class TexnoMagicDrawing:

    def __init__(self, path=None, curves=None, points_range=1000.0):
        self.path = path
        self.points_range = points_range
        self._curves = None
        self._points = None
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

    def __repr__(self):
        return '<TexnoMagicDrawing @ %s: %d points in %d curves>' % (
            self.path, len(self._points), len(self._curves))
