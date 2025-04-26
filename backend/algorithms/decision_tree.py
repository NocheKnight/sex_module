"""
A complete implementation of CART (Classification and Regression Trees)
algorithm.

This module contains:
- Decision tree construction with recursive binary splitting
- Support for both classification and regression tasks
- Cost-complexity pruning to prevent overfitting
- CSV-based data loading and prediction

The implementation features automatic tree growing and pruning during
initialization.
"""

from typing import Union, Optional
import numpy as np
import pandas as pd


class DecisionTree:
    """Decision tree implementation using CART algorithm with automatic
    pruning.

    Attributes:
        regression: Boolean flag for regression tasks (False for
        classification)
        ccp_alpha: Complexity parameter for cost-complexity pruning
        tree: The constructed decision tree structure
        _y_dtype: Data type of target variable
        _num_samples: Number of samples in training data
    """

    def __init__(
        self,
        regression: bool = False,
        ccp_alpha: float = 0.01
    ):
        """
        Initialize and build decision tree from CSV data.

        Args:
            csv_path: Path to training data CSV file
            regression: Whether to perform regression (default: classification)
            ccp_alpha: Complexity parameter for pruning (0 = no pruning)
            sep: CSV field separator character

        Raises:
            ValueError: If CSV data is invalid or missing
        """
        self.regression = regression
        self.ccp_alpha = ccp_alpha
        self.tree: Optional[dict] = None
        self._y_dtype: Optional[type] = None
        self._num_samples: Optional[int] = None
        self.feature_names: Optional[list] = None
        self.target_name: Optional[str] = None

    def build_tree(self, csv_path: str, sep: str = ','):
        """Complete tree construction pipeline from CSV data."""
        df = pd.read_csv(csv_path, sep=sep)
        self.feature_names = df.columns[:-1].tolist()
        self.target_name = df.columns[-1]
        features = df.iloc[:, :-1].values.astype(float)
        target = df.iloc[:, -1].values
        self._y_dtype = target.dtype
        self._num_samples = len(target)
        self.tree = self._grow_tree(features, target)
        if self.ccp_alpha > 0:
            self.tree = self._prune_tree(self.tree)

    def predict(self, csv_path: str, sep: str = ',') -> dict:
        """
        Make prediction for single data row in CSV file.

        Args:
            csv_path: Path to CSV file containing single prediction row
            sep: CSV field separator character

        Returns:
            Predicted value (float for regression, int for classification)
        """
        df = pd.read_csv(csv_path, sep=sep)

        features = df.values.astype(float)
        return self._traverse_tree(features[0], self.tree)

    def _grow_tree(
        self,
        features: np.ndarray,
        target: np.ndarray,
        path: str = ""
    ) -> dict:
        """Recursively build decision tree from training data."""
        if self._is_pure(target):
            return self._create_leaf_node(target, path)

        split_name, split_thr = self._find_optimal_split(features, target)
        if split_name is None:
            return self._create_leaf_node(target, path)

        split_idx = self.feature_names.index(split_name)
        left_mask = features[:, split_idx] <= split_thr
        left = self._grow_tree(
            features[left_mask], target[left_mask], path + "0")
        right = self._grow_tree(
            features[~left_mask], target[~left_mask], path + "1")

        return {
            'feature_name': split_name,
            'threshold': split_thr,
            'left': left,
            'right': right,
            'error': self._calculate_node_error(target),
            'is_leaf': False,
            'path': path
        }

    def _prune_tree(self, node: dict) -> dict:
        """Recursively prune tree using cost-complexity pruning.

        Args:
            node: Current node to consider for pruning

        Returns:
            Pruned node structure
        """
        if node['is_leaf']:
            return node

        node['left'] = self._prune_tree(node['left'])
        node['right'] = self._prune_tree(node['right'])

        if node['left']['is_leaf'] and node['right']['is_leaf']:
            pruning_gain = self._calculate_pruning_gain(node)
            if pruning_gain < self.ccp_alpha:
                return self._merge_leaf_nodes(node)

        return node

    def _create_leaf_node(self, target: np.ndarray, path: str) -> dict:
        """Create leaf node structure.

        Args:
            target: Target values for leaf node
            path: Binary path from root to this leaf

        Returns:
            Leaf node dictionary
        """
        return {
            'value': self._calculate_leaf_value(target),
            'error': self._calculate_node_error(target),
            'is_leaf': True,
            'path': path
        }

    def _merge_leaf_nodes(self, node: dict) -> dict:
        """Merge child leaf nodes into single leaf.

        Args:
            node: Parent node with two leaf children

        Returns:
            New merged leaf node
        """
        merged_values = np.array(
            [node['left']['value'], node['right']['value']]
        )
        if self.regression:
            return self._create_leaf_node(merged_values, node['path'])
        return self._create_leaf_node(
            np.concatenate(merged_values), node['path']
        )

    def _find_optimal_split(
        self,
        features: np.ndarray,
        target: np.ndarray
    ) -> tuple:
        """Find optimal feature and threshold for node split.

        Args:
            features: Feature matrix
            target: Target vector

        Returns:
            Tuple of (best_feature_name, best_threshold)
        """
        best_cost = np.inf
        best_idx, best_thr = None, None
        cost_func = self._calculate_mse if self.regression\
            else self._calculate_gini

        for feat_idx, feat_name in enumerate(self.feature_names):
            thresholds = np.unique(features[:, feat_idx])
            for thr in thresholds:
                left_mask: np.ndarray = features[:, feat_idx] <= thr
                if left_mask.sum() == 0 or (~left_mask).sum() == 0:
                    continue

                cost = self._calculate_split_cost(target, left_mask, cost_func)
                if cost < best_cost:
                    best_cost, best_idx, best_thr = cost, feat_idx, thr

        return self.feature_names[best_idx], best_thr

    def _calculate_split_cost(
        self,
        target: np.ndarray,
        mask: np.ndarray,
        cost_func: callable
    ) -> float:
        """Calculate weighted cost for potential split.

        Args:
            target: Target values
            mask: Boolean mask for left split
            cost_func: Cost function (gini or mse)

        Returns:
            Weighted cost of split
        """
        left, right = target[mask], target[~mask]
        return (cost_func(left) * len(left)
                + cost_func(right) * len(right)) / len(target)

    def _calculate_leaf_value(self, target: np.ndarray) -> Union[float, int]:
        """Calculate appropriate leaf value.

        Args:
            target: Target values at leaf

        Returns:
            Mean for regression, mode for classification
        """
        return np.mean(target) if self.regression\
            else pd.Series(target).mode()[0]

    def _calculate_node_error(self, target: np.ndarray) -> float:
        """Calculate node error for pruning.

        Args:
            target: Target values at node

        Returns:
            Normalized node error
        """
        method = self._calculate_mse if self.regression\
            else self._calculate_gini
        return len(target) / self._num_samples * method(target)

    def _calculate_pruning_gain(self, node: dict) -> float:
        """Calculate potential gain from pruning node.

        Args:
            node: Node to evaluate for pruning

        Returns:
            Pruning gain value
        """
        return (
            node['error'] - (node['left']['error'] + node['right']['error'])
        ) / 1

    @staticmethod
    def _is_pure(target: np.ndarray) -> bool:
        """Check if node contains single class/value.

        Args:
            target: Target values

        Returns:
            True if all values are identical
        """
        return len(np.unique(target)) == 1

    @staticmethod
    def _calculate_gini(target: np.ndarray) -> float:
        """Calculate Gini impurity for classification.

        Args:
            target: Target class values

        Returns:
            Gini impurity score
        """
        _, counts = np.unique(target, return_counts=True)
        return 1 - np.sum((counts / len(target)) ** 2)

    @staticmethod
    def _calculate_mse(target: np.ndarray) -> float:
        """Calculate MSE for regression.

        Args:
            target: Target values

        Returns:
            Mean squared error
        """
        return np.mean((target - np.mean(target)) ** 2)

    def _traverse_tree(
            self,
            features: np.ndarray,
            node: dict
    ) -> dict:
        """
        Recursively traverse tree to make prediction.

        Args:
            features: Feature vector for prediction
            node: Current node in tree

        Returns:
            Predicted value (float for regression, int for classification)
        """
        if node['is_leaf']:
            return node

        feature_idx = self.feature_names.index(node['feature_name'])
        if features[feature_idx] <= node['threshold']:
            return self._traverse_tree(features, node['left'])
        return self._traverse_tree(features, node['right'])

    def save_tree_to_file(self, file_path: str):
        """
        Save the tree structure, feature names, target name, and paths in
        leaves to a file.

        Args:
            file_path: Path to the file where the tree structure will be saved.
        """
        data_to_save = {
            "feature_names": self.feature_names,
            "target_name": self.target_name,
            "tree_structure": self.tree
        }
        with open(file_path, 'w') as f:
            f.write(str(data_to_save))

    def load_tree_from_file(self, file_path: str):
        """
        Load the tree structure, feature names, target name, and paths in
        leaves from a file.

        Args:
            file_path: Path to the file from which the tree structure will be
            loaded.
        """
        with open(file_path, 'r') as f:
            data = eval(f.read())
        self.feature_names = data.get("feature_names", [])
        self.target_name = data.get("target_name", "")
        self.tree = data.get("tree_structure", {})