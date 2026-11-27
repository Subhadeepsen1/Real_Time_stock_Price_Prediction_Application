"""NumPy implementations shared by the desktop and web stock apps."""

import numpy as np


def as_numeric_array(values):
    if hasattr(values, "to_numpy"):
        return values.to_numpy(dtype=float)
    return np.asarray(values, dtype=float)


class LinearRegression:
    def fit(self, X, y):
        values = as_numeric_array(X)
        self.mean_ = values.mean(axis=0)
        self.scale_ = values.std(axis=0)
        self.scale_[self.scale_ == 0] = 1
        standardized = (values - self.mean_) / self.scale_
        design = np.column_stack((np.ones(len(standardized)), standardized))
        self.coef_ = np.linalg.lstsq(design, as_numeric_array(y), rcond=None)[0]
        return self

    def predict(self, X):
        values = (as_numeric_array(X) - self.mean_) / self.scale_
        design = np.column_stack((np.ones(len(values)), values))
        return design @ self.coef_


class RandomForestRegressor:
    def __init__(self, n_estimators=100, random_state=None, min_samples_leaf=1):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.min_samples_leaf = min_samples_leaf

    def fit(self, X, y):
        values = as_numeric_array(X)
        targets = as_numeric_array(y).reshape(-1)
        if len(values) != len(targets) or not len(targets):
            raise ValueError("Training features and targets must contain matching rows.")

        rng = np.random.default_rng(self.random_state)
        self.trees_ = []
        importances = np.zeros(values.shape[1], dtype=float)

        def grow_tree(rows):
            node_values = values[rows]
            node_targets = targets[rows]
            leaf_value = float(node_targets.mean())
            if len(rows) < 2 * self.min_samples_leaf or np.all(node_targets == node_targets[0]):
                return leaf_value

            parent_sse = float(np.sum((node_targets - leaf_value) ** 2))
            best_gain = 0.0
            best_split = None

            for feature in range(values.shape[1]):
                order = np.argsort(node_values[:, feature], kind="stable")
                sorted_x = node_values[order, feature]
                sorted_y = node_targets[order]
                left_n = np.arange(1, len(rows))
                valid = (
                    (left_n >= self.min_samples_leaf)
                    & (len(rows) - left_n >= self.min_samples_leaf)
                    & (sorted_x[:-1] < sorted_x[1:])
                )
                if not np.any(valid):
                    continue

                cumulative = np.cumsum(sorted_y)
                cumulative_sq = np.cumsum(sorted_y * sorted_y)
                left_sum = cumulative[:-1]
                right_sum = cumulative[-1] - left_sum
                left_sse = cumulative_sq[:-1] - left_sum * left_sum / left_n
                right_n = len(rows) - left_n
                right_sse = (
                    cumulative_sq[-1] - cumulative_sq[:-1] - right_sum * right_sum / right_n
                )
                gains = parent_sse - left_sse - right_sse
                gains[~valid] = -np.inf
                split_at = int(np.argmax(gains))
                if gains[split_at] > best_gain:
                    best_gain = float(gains[split_at])
                    threshold = (sorted_x[split_at] + sorted_x[split_at + 1]) / 2
                    best_split = (feature, threshold)

            if best_split is None:
                return leaf_value

            feature, threshold = best_split
            left_rows = rows[node_values[:, feature] <= threshold]
            right_rows = rows[node_values[:, feature] > threshold]
            if not len(left_rows) or not len(right_rows):
                return leaf_value
            importances[feature] += best_gain
            return (
                feature,
                threshold,
                grow_tree(left_rows),
                grow_tree(right_rows),
            )

        row_indices = np.arange(len(targets))
        for _ in range(self.n_estimators):
            sample = rng.choice(row_indices, size=len(row_indices), replace=True)
            self.trees_.append(grow_tree(sample))

        total_importance = importances.sum()
        self.feature_importances_ = (
            importances / total_importance if total_importance else importances
        )
        return self

    @staticmethod
    def _predict_tree(tree, row):
        node = tree
        while isinstance(node, tuple):
            feature, threshold, left, right = node
            node = left if row[feature] <= threshold else right
        return node

    def predict(self, X):
        values = as_numeric_array(X)
        predictions = [
            np.mean([self._predict_tree(tree, row) for tree in self.trees_])
            for row in values
        ]
        return np.asarray(predictions, dtype=float)


class StandardScaler:
    def fit_transform(self, values):
        values = as_numeric_array(values)
        self.mean_ = values.mean(axis=0)
        self.scale_ = values.std(axis=0)
        self.scale_[self.scale_ == 0] = 1
        return (values - self.mean_) / self.scale_


class KMeans:
    def __init__(self, n_clusters=8, random_state=None, n_init=10, max_iter=300):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.n_init = n_init
        self.max_iter = max_iter

    def fit_predict(self, values):
        values = as_numeric_array(values)
        if len(values) < self.n_clusters:
            raise ValueError("The number of rows must be at least the number of clusters.")

        rng = np.random.default_rng(self.random_state)
        best_inertia = np.inf
        for _ in range(self.n_init):
            centers = values[rng.choice(len(values), self.n_clusters, replace=False)].copy()
            for _ in range(self.max_iter):
                distances = np.sum((values[:, None, :] - centers[None, :, :]) ** 2, axis=2)
                labels = np.argmin(distances, axis=1)
                updated = centers.copy()
                for cluster in range(self.n_clusters):
                    members = values[labels == cluster]
                    if len(members):
                        updated[cluster] = members.mean(axis=0)
                if np.allclose(updated, centers):
                    centers = updated
                    break
                centers = updated

            distances = np.sum((values - centers[labels]) ** 2, axis=1)
            inertia = float(distances.sum())
            if inertia < best_inertia:
                best_inertia = inertia
                self.cluster_centers_ = centers
                self.labels_ = labels
        return self.labels_


class PCA:
    def fit_transform(self, values):
        values = as_numeric_array(values)
        centered = values - values.mean(axis=0)
        _, singular_values, right_vectors = np.linalg.svd(centered, full_matrices=False)
        variances = singular_values ** 2 / max(len(values) - 1, 1)
        total_variance = variances.sum()
        self.explained_variance_ratio_ = (
            variances / total_variance if total_variance else np.zeros_like(variances)
        )
        self.components_ = right_vectors
        return centered @ self.components_.T


def mean_squared_error(actual, predicted):
    errors = as_numeric_array(actual) - as_numeric_array(predicted)
    return float(np.mean(errors ** 2))


def r2_score(actual, predicted):
    actual = as_numeric_array(actual)
    predicted = as_numeric_array(predicted)
    residual_sum = np.sum((actual - predicted) ** 2)
    total_sum = np.sum((actual - actual.mean()) ** 2)
    if total_sum == 0:
        return 1.0 if residual_sum == 0 else 0.0
    return float(1 - residual_sum / total_sum)
