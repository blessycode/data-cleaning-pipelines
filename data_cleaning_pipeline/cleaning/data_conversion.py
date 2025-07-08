import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MinMaxScaler, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.exceptions import NotFittedError
from typing import List, Union

class DataConverter(BaseEstimator, TransformerMixin):
    """
    Handles data conversion:
    - Imputation
    - Scaling
    - Encoding
    """

    def __init__(
        self,
        categorical_features: List[str] = None,
        numerical_features: List[str] = None,
        encoding_method: str = 'onehot',      # 'onehot', 'ordinal'
        scaling_method: str = 'minmax',       # 'minmax', 'standard'
        imputation_strategy: str = 'mean'     # 'mean', 'median', 'most_frequent'
    ):
        self.categorical_features = categorical_features or []
        self.numerical_features = numerical_features or []
        self.encoding_method = encoding_method
        self.scaling_method = scaling_method
        self.imputation_strategy = imputation_strategy
        self.pipeline = None
        self.feature_names_out = None

    def fit(self, X: pd.DataFrame, y: Union[pd.Series, None] = None):
        transformers = []

        # Categorical pipeline
        if self.categorical_features:
            cat_steps = [('imputer', SimpleImputer(strategy='most_frequent'))]
            if self.encoding_method == 'onehot':
                cat_steps.append(('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)))
            elif self.encoding_method == 'ordinal':
                cat_steps.append(('encoder', OrdinalEncoder()))
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

        # Create ColumnTransformer
        self.pipeline = ColumnTransformer(transformers=transformers)
        self.pipeline.fit(X)

        # Capture feature names
        self.feature_names_out = self._get_feature_names_out()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not self.pipeline:
            raise NotFittedError("The DataConverter instance is not fitted yet.")

        transformed_array = self.pipeline.transform(X)

        # Defensive fallback if shape mismatch
        if transformed_array.shape[1] != len(self.feature_names_out):
            self.feature_names_out = [f"feature_{i}" for i in range(transformed_array.shape[1])]

        transformed_df = pd.DataFrame(transformed_array, columns=self.feature_names_out)
        return transformed_df

    def _get_feature_names_out(self):
        output_features = []
        for name, trans, cols in self.pipeline.transformers_:
            if name == 'cat' and self.encoding_method == 'onehot':
                encoder = trans.named_steps['encoder']
                try:
                    cats = encoder.get_feature_names_out(cols)
                    output_features.extend(cats)
                except:
                    output_features.extend(cols)
            else:
                if isinstance(cols, list):
                    output_features.extend(cols)
                else:
                    output_features.append(cols)
        return output_features
