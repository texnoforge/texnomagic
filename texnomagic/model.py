from collections import Counter
import numpy as np
import json

from sklearn import mixture

# TODO: fix in PyInstaller upstream
# hidden import for PyInstaller
import sklearn.utils._weight_vector  # noqa

from texnomagic.common import NumpyEncoder


SYMBOL_SCORE_THRESHOLDS = [
    (0.1, "NOPE", "red"),
    (0.2, "NO", "red"),
    (0.3, "BAD", "bright_red"),
    (0.4, "CRUDE", "dark_orange3"),
    (0.5, "MEH", "orange3"),
    (0.6, "OK", "dark_green"),
    (0.7, "NICE", "green4"),
    (0.8, "GREAT", "bright_green"),
    (0.9, "EPIC", "light_green"),
    (1.0, "PERFECT", "bright_cyan"),
    (1.1, "GODLIKE", "bright_cyan"),
]


class TexnoMagicSymbolModelScore(float):
    """
    A subclass of float with extra features
    for symbol model score output and formatting.

    Currently specific for GMM symbol model.
    """
    @property
    def rating(self):
        r, _ = self._threshold_data()
        return r

    @property
    def color(self):
        _, c = self._threshold_data()
        return c

    def pretty(self, rating=False):
        r, c = self._threshold_data()
        txt = "[%s]%0.2f" % (c, self)
        if rating:
            txt += f" {r}"
        txt += "[/]"
        return txt

    def _threshold_data(self):
        for t, name, color in SYMBOL_SCORE_THRESHOLDS:
            if self < t:
                return name, color
        _, name, color = SYMBOL_SCORE_THRESHOLDS[-1]
        return name, color


class TexnoMagicSymbolModel:
    """
    A model of TexnoMagic symbol.

    This is currently implemented using Gaussian Mixture Models (GMM).

    See https://scikit-learn.org/stable/modules/generated/sklearn.mixture.GaussianMixture.html

    Neural networks and other models might require per-alphabet models which
    should be implemented using TexnoMagicAlphabetModel equivalent.
    """

    def __init__(self, path=None):
        self.path = path
        self.ready = False
        self.gmm = None
        self.n_gauss = 10
        self.score_avg = 0
        self.labels_avg = []

    @property
    def info_path(self):
        if self.path:
            return self.path / 'texno_model.json'
        return None

    def train_symbol(self, symbol):
        """
        Train symbol model from its drawings.
        """
        points = symbol.get_all_drawing_points()
        n_points = len(points)
        if n_points < 2 * self.n_gauss:
            # insufficient data
            return False

        # train the symbol GMM model
        self.train_GMM(points)

        # aggregate average scores per label and per drawing
        score_sum = 0.0
        label_sums = np.zeros(self.gmm.n_components)
        for d in symbol.drawings:
            score_sum += self.gmm.score(d.points)
            labels = self.gmm.predict(d.points)
            labels_counts = count_labels(labels, self.gmm.n_components)
            label_sums += labels_counts
        # average scores per label (component)
        self.labels_avg = label_sums / label_sums.sum()
        # average score per drawing (for score normalization)
        self.score_avg = score_sum / len(symbol.drawings)

        self.ready = True
        return True

    def train_GMM(self, data):
        """
        Traing GMM model from data points.
        """
        # thanks scikit-learn <3
        self.gmm = mixture.GaussianMixture(n_components=self.n_gauss)
        if data is None:
            return
        self.gmm.fit(data)

    def score(self, drawing):
        """
        Get a model score for a drawing.

        This is transforming negative log likelyhood into <0;INF> range
        using questionable math.

        It's rare but possible for a score to exceed 1.

        Result is a float subclass TexnoMagicSymbolModelScore
        which provides convenient formatting features.
        """
        if not self.ready:
            return -1

        # Compute the average log-likelihood of each drawing point.
        log_score = self.gmm.score(drawing.points)
        # Predict the component labels for drawing each drawing point.
        labels = self.gmm.predict(drawing.points)

        # "Normalize" the negative log-likelyhood from GMM model
        # into <0; INF> using score average.
        score = self.score_avg / log_score

        label_counts = count_labels(labels, self.n_gauss)
        label_diff = sum(abs(label_counts - self.labels_avg))
        label_k = max(1 - label_diff, 0.3)
        score *= label_k

        return TexnoMagicSymbolModelScore(score)

    def get_preview(self):
        """
        Return data for drawing a model preview.
        """
        p = {
            'type': 'gmm',
            'components': []
        }
        comps = []
        if not self.gmm or not hasattr(self.gmm, 'means_'):
            return p

        means = self.gmm.means_
        covs = self.gmm.covariances_
        weights = self.gmm.weights_
        # draw covariances for each Gaussian
        for i, cov in enumerate(covs):
            # eigenvectors are magic
            v, w = np.linalg.eigh(cov)
            u = w[0] / np.linalg.norm(w[0])
            angle = np.arctan2(u[1], u[0])
            angle = 180 * angle / np.pi  # convert to degrees
            size = 2. * np.sqrt(2.) * np.sqrt(v)
            center = means[i, :2]
            weight = weights[i]
            comp = [center.tolist(), size.tolist(), angle, weight]
            comps.append(comp)
        p['components'] = comps
        return p

    def save(self):
        """
        Save symbol to its path.

        [!] Overwrites existing data!
        """
        self.path.mkdir(parents=True, exist_ok=True)
        info = {
            'model_type': 'gmm',
            'n_gauss': self.n_gauss,
            'score_avg': self.score_avg,
            'labels_avg': self.labels_avg,
            'params': self.gmm._get_parameters()
        }
        return json.dump(info, self.info_path.open('w'), cls=NumpyEncoder, indent=2)

    def load(self, path=None):
        """
        Load symbol from path.
        """
        if path:
            self.path = path

        # reinit model before load
        self.__init__(path=self.path)

        if not self.info_path.exists():
            return False

        info = json.load(self.info_path.open())
        self.n_gauss = info['n_gauss']
        self.score_avg = info['score_avg']
        self.labels_avg = np.array(info['labels_avg'])
        self.gmm = mixture.GaussianMixture(n_components=self.n_gauss)
        params = [np.array(p) for p in info['params']]
        self.gmm._set_parameters(params)
        self.ready = True
        return True

    def as_dict(self, relative_to=None):
        path = self.path
        if relative_to:
            path = path.relative_to(relative_to)
        return {
            'model_type': 'GMM',
            'n_gauss': self.n_gauss,
            'score_avg': self.score_avg,
        }

    def pretty(self):
        return (f"[magenta]GMM[/] model (n_gauss: {self.n_gauss}, "
                "score_avg: %.1f)" % self.score_avg)

    def __repr__(self):
        return '<TexnoMagicSymbolModel @ %s>' % self.path


def count_labels(labels, n, normalize=True):
    """
    Count and optionally normalize labels.

    This returns the counts for each label as a np.array

    When normalize is True (default), normalize the counts
    into <0;1> by dividing by total sum.
    """
    counts = dict(Counter(labels))
    for i in range(n):
        if i not in counts:
            # fill in labels with 0 occurances for conversion
            counts[i] = 0
    # convert unordered {label: count} dict into np.array [label0_count, label1_count, ...]
    counts = np.array([c for _, c in sorted(counts.items(), key=lambda x: x[0])])
    # normalize into <0;1> using total sum
    if normalize:
        counts = counts / counts.sum()
    return counts
