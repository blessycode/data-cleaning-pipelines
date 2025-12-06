# data_converter.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.exceptions import NotFittedError
from typing import List, Optional

class DataConverter(BaseEstimator, TransformerMixin):
    """
    Handles preprocessing for categorical and numerical features:
    - Categorical: imputation + encoding (onehot or ordinal)
    - Numerical: imputation + scaling (minmax or standard)
    """

    def __init__(
        self,
        categorical_features: Optional[List[str]] = None,
        numerical_features: Optional[List[str]] = None,
        encoding_method: str = 'onehot',      # 'onehot' or 'ordinal'
        scaling_method: str = 'minmax',       # 'minmax' or 'standard'
        imputation_strategy: str = 'mean',    # 'mean', 'median', 'most_frequent'
        remainder: str = 'passthrough'        # what to do with untouched columns
    ):
        self.categorical_features = categorical_features or []
        self.numerical_features = numerical_features or []
        self.encoding_method = encoding_method
        self.scaling_method = scaling_method
        self.imputation_strategy = imputation_strategy
        self.remainder = remainder
        self.pipeline = None
        self.feature_names_out = None

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        transformers = []

        # Categorical pipeline
        if self.categorical_features:
            cat_steps = [('imputer', SimpleImputer(strategy='most_frequent'))]

            if self.encoding_method == 'onehot':
                cat_steps.append(('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)))
            elif self.encoding_method == 'ordinal':
                cat_steps.append(('encoder', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)))
            else:
                raise ValueError(f"Invalid encoding_method: {self.encoding_method}")

            cat_pipeline = Pipeline(steps=cat_steps)
            transformers.append(('cat', cat_pipeline, self.categorical_features))

        # Numerical pipeline
        if self.numerical_features:
            num_steps = [('imputer', SimpleImputer(strategy=self.imputation_strategy))]

            if self.scaling_method == 'minmax':
                num_steps.append(('scaler', MinMaxScaler()))
            elif self.scaling_method == 'standard':
                num_steps.append(('scaler', StandardScaler()))
            else:
                raise ValueError(f"Invalid scaling_method: {self.scaling_method}")

            num_pipeline = Pipeline(steps=num_steps)
            transformers.append(('num', num_pipeline, self.numerical_features))

        # ColumnTransformer
        self.pipeline = ColumnTransformer(transformers=transformers, remainder=self.remainder)
        self.pipeline.fit(X)

        # Extract feature names
        self.feature_names_out = self._get_feature_names_out(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.pipeline is None:
            raise NotFittedError("This DataConverter instance is not fitted yet.")
        transformed_array = self.pipeline.transform(X)
        return pd.DataFrame(transformed_array, columns=self.feature_names_out, index=X.index)

    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

    def _get_feature_names_out(self, X: pd.DataFrame):
        """Extract feature names from fitted ColumnTransformer"""
        feature_names = []

        for name, transformer, columns in self.pipeline.transformers_:
            if name == 'remainder' and self.remainder == 'passthrough':
                if transformer == 'passthrough':
                    feature_names.extend([col for col in X.columns if col not in self.categorical_features + self.numerical_features])
                continue
            elif name == 'drop':
                continue

            # Get feature names from transformer
            if isinstance(transformer, Pipeline):
                encoder = transformer.named_steps.get('encoder')
                if encoder:
                    if isinstance(encoder, OneHotEncoder):
                        feature_names.extend(encoder.get_feature_names_out(columns))
                    else:  # OrdinalEncoder
                        feature_names.extend(columns)
                else:  # No encoder, just original columns
                    feature_names.extend(columns)
            else:
                feature_names.extend(columns)

        return feature_names
