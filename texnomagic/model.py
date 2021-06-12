from collections import Counter
import numpy as np
import json

from sklearn import mixture

# TODO: fix in PyInstaller upstream
# hidden import for PyInstaller
import sklearn.utils._weight_vector

from texnomagic.common import NumpyEncoder


class TexnoMagicSymbolModel:

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
        train symbol model from its drawings
        """
        points = symbol.get_all_drawing_points()
        n_points = len(points)
        if n_points < 2 * self.n_gauss:
            # insufficient data
            return False

        self.train_GMM(points)

        score_sum = 0.0
        label_sums = np.zeros(self.gmm.n_components)
        for d in symbol.drawings:
            score_sum += self.gmm.score(d.points)
            labels = self.gmm.predict(d.points)
            labels_norm = normalize_labels(labels, self.gmm.n_components)
            label_sums += labels_norm

        self.labels_avg = label_sums / label_sums.sum()
        self.score_avg = score_sum / len(symbol.drawings)
        self.ready = True
        return True

    def train_GMM(self, data):
        """
        traing GMM model from data points
        """
        # thanks scikit-learn <3
        self.gmm = mixture.GaussianMixture(n_components=self.n_gauss)
        if data is None:
            return
        self.gmm.fit(data)

    def score(self, drawing):
        if not self.ready:
            return -1
        log_score = self.gmm.score(drawing.points)
        labels = self.gmm.predict(drawing.points)

        score = self.score_avg / log_score
        label_counts = normalize_labels(labels, self.n_gauss)
        label_diff = sum(abs(label_counts - self.labels_avg))
        label_k = max(1 - label_diff, 0.3)

        return score * label_k

    def get_preview(self):
        """
        return data for drawing a model preview
        """
        slen = 1000.0
        ssize = np.array([slen, slen])

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

    def __repr__(self):
        return '<TexnoMagicSymbolModel @ %s>' % self.path


def normalize_labels(labels, n):
    counts = dict(Counter(labels))
    for i in range(n):
        if i not in counts:
            counts[i] = 0
    counts = np.array([c for _, c in sorted(counts.items(), key=lambda x: x[0])])
    counts = counts / counts.sum()
    return counts
