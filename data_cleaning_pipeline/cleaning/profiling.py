import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import normaltest, skew, kurtosis
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import warnings
from typing import List, Dict, Optional, Union, Tuple
import matplotlib
from matplotlib.colors import LinearSegmentedColormap

warnings.filterwarnings('ignore')

# Set modern styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Custom color palettes
MODERN_COLORS = ['#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
                 '#06B6D4', '#EC4899', '#84CC16', '#F97316', '#78716C']

# Create custom colormap
custom_cmap = LinearSegmentedColormap.from_list("modern", ['#6366F1', '#10B981', '#F59E0B'])


#### 1 Basic Profile
def generate_basic_profile(df):
    """Generate basic profile with enhanced metrics"""
    profile = {}

    # Missing values analysis
    missing_counts = df.isnull().sum()
    missing_percent = (df.isnull().mean() * 100).round(3)

    profile["dataset_info"] = {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 ** 2), 3)
    }

    profile["missing_values"] = {
        "total_missing": int(missing_counts.sum()),
        "total_missing_percent": round(missing_counts.sum() / (df.shape[0] * df.shape[1]) * 100, 3),
        "columns_with_missing": missing_counts[missing_counts > 0].to_dict(),
        "missing_percentage_by_column": missing_percent.to_dict()
    }

    profile["duplicates"] = {
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_percent": round(df.duplicated().mean() * 100, 3)
    }

    profile["empty_columns"] = df.columns[df.isnull().all()].tolist()

    # Data types overview
    dtypes_count = df.dtypes.value_counts().to_dict()
    profile["data_types"] = {
        str(k): int(v) for k, v in dtypes_count.items()
    }

    return profile


#### 2 Numerical Profiling with Enhanced Statistics
def generate_numerical_profile(df):
    """Enhanced numerical profiling with more statistical tests"""
    num_cols = df.select_dtypes(include=[np.number]).columns
    stats_dict = {}

    for col in num_cols:
        col_data = df[col].dropna()

        if len(col_data) == 0:
            continue

        # Basic statistics
        q1, q3 = np.percentile(col_data, [25, 75])
        iqr = q3 - q1

        stat = {
            # Counts
            "count": int(col_data.count()),
            "missing": int(df[col].isnull().sum()),
            "missing_percent": round(df[col].isnull().mean() * 100, 3),
            "zeros": int((col_data == 0).sum()),
            "zero_percent": round((col_data == 0).mean() * 100, 3),

            # Central tendency
            "mean": round(float(col_data.mean()), 6),
            "median": round(float(col_data.median()), 6),
            "mode": round(float(col_data.mode().iloc[0] if not col_data.mode().empty else np.nan), 6),

            # Dispersion
            "std": round(float(col_data.std()), 6),
            "variance": round(float(col_data.var()), 6),
            "range": round(float(col_data.max() - col_data.min()), 6),
            "iqr": round(float(iqr), 6),
            "cv": round(float(col_data.std() / col_data.mean() if col_data.mean() != 0 else np.nan), 6),
            # Coefficient of variation

            # Percentiles
            "min": round(float(col_data.min()), 6),
            "5th": round(float(col_data.quantile(0.05)), 6),
            "25th": round(float(q1), 6),
            "50th": round(float(col_data.quantile(0.50)), 6),
            "75th": round(float(q3), 6),
            "95th": round(float(col_data.quantile(0.95)), 6),
            "max": round(float(col_data.max()), 6),

            # Shape
            "skewness": round(float(col_data.skew()), 6),
            "kurtosis": round(float(col_data.kurtosis()), 6),

            # Normality tests
            "is_normal": None,
            "normality_pvalue": None,
            "shapiro_pvalue": None
        }

        # Normality tests (only for reasonable sample sizes)
        if len(col_data) >= 20 and len(col_data) <= 5000:
            try:
                # D'Agostino's K^2 test
                _, dagostino_p = normaltest(col_data)
                stat["normality_pvalue"] = round(dagostino_p, 6)
                stat["is_normal"] = dagostino_p > 0.05

                # Shapiro-Wilk test (for smaller samples)
                if len(col_data) <= 5000:
                    _, shapiro_p = stats.shapiro(col_data)
                    stat["shapiro_pvalue"] = round(shapiro_p, 6)
            except:
                pass

        # Outlier detection using multiple methods
        # IQR method
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers_iqr = col_data[(col_data < lower_bound) | (col_data > upper_bound)]

        # Z-score method (for normal-ish distributions)
        if stat.get("is_normal", False):
            z_scores = np.abs(stats.zscore(col_data))
            outliers_z = col_data[z_scores > 3]
            outlier_count_z = len(outliers_z)
        else:
            outlier_count_z = 0

        stat["outliers"] = {
            "iqr_method": int(len(outliers_iqr)),
            "iqr_percent": round(len(outliers_iqr) / len(col_data) * 100, 3),
            "z_score_method": int(outlier_count_z),
            "z_score_percent": round(outlier_count_z / len(col_data) * 100, 3) if len(col_data) > 0 else 0
        }

        # Data quality flags
        stat["quality_flags"] = {
            "high_missing": stat["missing_percent"] > 20,
            "high_zeros": stat["zero_percent"] > 50,
            "high_outliers": stat["outliers"]["iqr_percent"] > 5,
            "high_skew": abs(stat["skewness"]) > 1,
            "high_kurtosis": abs(stat["kurtosis"]) > 3
        }

        stats_dict[col] = stat

    return stats_dict


#### 3 Enhanced Categorical Profiler
def generate_categorical_profile(df):
    """Enhanced categorical profiling with frequency analysis"""
    cat_cols = df.select_dtypes(include=['object', 'string', 'category', 'bool']).columns
    stats_dict = {}

    for col in cat_cols:
        col_data = df[col].dropna()

        if len(col_data) == 0:
            continue

        value_counts = col_data.value_counts()
        value_counts_normalized = col_data.value_counts(normalize=True)

        stats_dict[col] = {
            "count": int(col_data.count()),
            "missing": int(df[col].isnull().sum()),
            "missing_percent": round(df[col].isnull().mean() * 100, 3),
            "unique_count": int(col_data.nunique()),
            "unique_percent": round(col_data.nunique() / len(col_data) * 100, 3),

            "cardinality": "high" if col_data.nunique() > 50 else "medium" if col_data.nunique() > 10 else "low",

            "top_values": {
                "values": value_counts.head(10).index.tolist(),
                "counts": value_counts.head(10).tolist(),
                "percentages": (value_counts_normalized.head(10) * 100).round(3).tolist()
            },

            "distribution": {
                "dominant_value": value_counts.index[0] if len(value_counts) > 0 else None,
                "dominant_percent": round(value_counts_normalized.iloc[0] * 100, 3) if len(
                    value_counts_normalized) > 0 else None,
                "gini_coefficient": round(1 - sum((value_counts_normalized ** 2)), 6),  # Measure of inequality
                "entropy": round(stats.entropy(value_counts_normalized), 6)  # Information entropy
            },

            "rare_values": {
                "rare_count": int((value_counts_normalized < 0.01).sum()),
                "rare_percent": round((value_counts_normalized < 0.01).mean() * 100, 3)
            }
        }

        # Data quality flags
        stats_dict[col]["quality_flags"] = {
            "high_missing": stats_dict[col]["missing_percent"] > 20,
            "high_cardinality": col_data.nunique() > len(col_data) * 0.5,
            "high_dominance": stats_dict[col]["distribution"]["dominant_percent"] > 80,
            "many_rares": stats_dict[col]["rare_values"]["rare_percent"] > 30
        }

    return stats_dict


#### 4 Enhanced DateTime Profile
def generate_datetime_profile(df):
    """Enhanced datetime profiling with temporal patterns"""
    dt_cols = [col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]
    stats_dict = {}

    for col in dt_cols:
        col_data = df[col].dropna()

        if len(col_data) == 0:
            continue

        # Extract temporal components
        year = col_data.dt.year
        month = col_data.dt.month
        day = col_data.dt.day
        hour = col_data.dt.hour if hasattr(col_data.dt, 'hour') else None
        dayofweek = col_data.dt.dayofweek

        stats_dict[col] = {
            "range": {
                "min": str(col_data.min()),
                "max": str(col_data.max()),
                "range_days": int((col_data.max() - col_data.min()).days),
                "range_seconds": int((col_data.max() - col_data.min()).total_seconds())
            },

            "completeness": {
                "count": int(col_data.count()),
                "missing": int(df[col].isnull().sum()),
                "missing_percent": round(df[col].isnull().mean() * 100, 3)
            },

            "temporal_patterns": {
                "year_distribution": year.value_counts().sort_index().to_dict() if len(year.unique()) > 1 else None,
                "month_distribution": month.value_counts().sort_index().to_dict() if len(month.unique()) > 1 else None,
                "hour_distribution": hour.value_counts().sort_index().to_dict() if hour is not None and len(
                    hour.unique()) > 1 else None,
                "weekday_distribution": dayofweek.value_counts().sort_index().to_dict() if len(
                    dayofweek.unique()) > 1 else None
            },

            "quality_flags": {
                "future_dates": int((col_data > pd.Timestamp.now()).sum()),
                "inconsistent_range": (col_data.max() - col_data.min()).days > 365 * 50,  # > 50 years
                "high_missing": stats_dict[col]["completeness"]["missing_percent"] > 20
            }
        }

    return stats_dict


#### 5 Mixed Type Detection
def detect_mixed_type(df):
    """Detect columns with mixed data types"""
    mixed = {}

    for col in df.columns:
        if df[col].isnull().all():
            continue

        # Sample non-null values
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue

        # Check for mixed types
        sample_size = min(len(non_null), 100)
        sample = non_null.sample(sample_size, random_state=42)

        # Get unique types
        unique_types = set()
        for val in sample:
            if pd.isna(val):
                continue
            unique_types.add(type(val).__name__)

        if len(unique_types) > 1:
            mixed[col] = {
                "detected_types": list(unique_types),
                "sample_values": sample.head(5).tolist(),
                "recommendation": "Consider converting to consistent type"
            }

    return mixed


#### 6 Enhanced Correlations
def generate_correlations(df):
    """Generate comprehensive correlation analysis"""
    correlations = {}
    num_cols = df.select_dtypes(include=[np.number])

    if num_cols.shape[1] > 1:
        # Multiple correlation methods
        correlations["pearson"] = num_cols.corr(method="pearson").round(4).to_dict()
        correlations["spearman"] = num_cols.corr(method="spearman").round(4).to_dict()
        correlations["kendall"] = num_cols.corr(method="kendall").round(4).to_dict()

        # Find highly correlated pairs
        corr_matrix = num_cols.corr(method="pearson").abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

        high_corr = []
        moderate_corr = []

        for col in upper.columns:
            for idx in upper.index:
                if pd.notnull(upper.loc[col, idx]):
                    corr_value = upper.loc[col, idx]
                    if corr_value > 0.8:
                        high_corr.append({
                            "feature1": col,
                            "feature2": idx,
                            "correlation": round(corr_value, 4),
                            "type": "high"
                        })
                    elif corr_value > 0.5:
                        moderate_corr.append({
                            "feature1": col,
                            "feature2": idx,
                            "correlation": round(corr_value, 4),
                            "type": "moderate"
                        })

        correlations["high_correlations"] = sorted(high_corr, key=lambda x: x["correlation"], reverse=True)
        correlations["moderate_correlations"] = sorted(moderate_corr, key=lambda x: x["correlation"], reverse=True)

        # Multicollinearity detection using VIF (simplified)
        correlations["multicollinearity_warning"] = len(high_corr) > 0

        # Correlation with target (if specified)
        correlations["recommendations"] = {
            "consider_removing": [pair["feature2"] for pair in high_corr[:3]] if high_corr else [],
            "potential_interactions": [pair for pair in moderate_corr[:5]] if moderate_corr else []
        }

    return correlations


#### VISUALIZATION MODULE

class ModernVisualizer:
    """Modern visualizer with beautiful, dashboard-ready plots"""

    def __init__(self):
        self.colors = MODERN_COLORS
        self.template = "plotly_white"

    def create_distribution_plot(self, df, column, bins=30, figsize=(800, 500)):
        """Create modern distribution plot with multiple views"""
        data = df[column].dropna()

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Histogram with KDE', 'Box Plot', 'Q-Q Plot', 'Violin Plot'),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # Histogram with KDE
        hist_data = [data]
        distplot = ff.create_distplot(hist_data, [column], show_hist=True, show_rug=False, colors=[self.colors[0]])
        for trace in distplot.data:
            fig.add_trace(trace, row=1, col=1)

        # Box plot
        fig.add_trace(go.Box(
            y=data,
            name=column,
            marker_color=self.colors[1],
            boxmean='sd',
            orientation='v'
        ), row=1, col=2)

        # Q-Q Plot
        qq_data = stats.probplot(data, dist="norm")
        x = qq_data[0][0]
        y = qq_data[0][1]

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='markers',
            marker=dict(color=self.colors[2], size=8),
            name='Sample'
        ), row=2, col=1)

        # Add reference line
        fig.add_trace(go.Scatter(
            x=[x.min(), x.max()],
            y=[y.min(), y.max()],
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Normal'
        ), row=2, col=1)

        # Violin plot
        fig.add_trace(go.Violin(
            y=data,
            name=column,
            box_visible=True,
            line_color='black',
            fillcolor=self.colors[3],
            opacity=0.6
        ), row=2, col=2)

        # Update layout
        fig.update_layout(
            title=f'Distribution Analysis: {column}',
            template=self.template,
            showlegend=False,
            height=figsize[1],
            width=figsize[0],
            plot_bgcolor='rgba(240,240,240,0.95)'
        )

        return fig

    def create_categorical_plot(self, df, column, top_n=10, figsize=(900, 600)):
        """Create modern categorical visualization"""
        data = df[column].dropna()
        value_counts = data.value_counts().head(top_n)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Top Categories', 'Pie Chart', 'Donut Chart', 'Treemap'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "pie"}, {"type": "treemap"}]]
        )

        # Bar chart
        fig.add_trace(go.Bar(
            x=value_counts.index,
            y=value_counts.values,
            marker_color=self.colors,
            marker_line_color='black',
            marker_line_width=1,
            opacity=0.8
        ), row=1, col=1)

        # Pie chart
        fig.add_trace(go.Pie(
            labels=value_counts.index,
            values=value_counts.values,
            hole=0.3,
            marker_colors=self.colors
        ), row=1, col=2)

        # Donut chart
        fig.add_trace(go.Pie(
            labels=value_counts.index,
            values=value_counts.values,
            hole=0.6,
            marker_colors=px.colors.sequential.Plasma
        ), row=2, col=1)

        # Treemap
        fig.add_trace(go.Treemap(
            labels=value_counts.index,
            parents=[''] * len(value_counts),
            values=value_counts.values,
            marker=dict(
                colors=px.colors.qualitative.Set3,
                line=dict(width=2, color='white')
            ),
            textinfo="label+value+percent parent"
        ), row=2, col=2)

        # Update layout
        fig.update_layout(
            title=f'Categorical Analysis: {column}',
            template=self.template,
            showlegend=True,
            height=figsize[1],
            width=figsize[0],
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )

        return fig

    def create_correlation_heatmap(self, df, method='pearson', figsize=(800, 700)):
        """Create beautiful correlation heatmap"""
        corr_matrix = df.select_dtypes(include=[np.number]).corr(method=method)

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu_r',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False,
            colorbar=dict(
                title='Correlation',
                titleside='right'
            )
        ))

        # Annotate with correlation values
        annotations = []
        for i, row in enumerate(corr_matrix.values):
            for j, value in enumerate(row):
                annotations.append(
                    dict(
                        x=corr_matrix.columns[j],
                        y=corr_matrix.columns[i],
                        text=str(round(value, 2)),
                        font=dict(color='white' if abs(value) > 0.5 else 'black'),
                        showarrow=False
                    )
                )

        fig.update_layout(
            title=f'Correlation Heatmap ({method.capitalize()})',
            template=self.template,
            height=figsize[1],
            width=figsize[0],
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            annotations=annotations,
            plot_bgcolor='white'
        )

        return fig

    def create_time_series_plot(self, df, date_column, value_column, freq='D', figsize=(1000, 600)):
        """Create modern time series visualization"""
        time_series = df.set_index(date_column)[value_column]
        resampled = time_series.resample(freq).mean()

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Time Series', 'Rolling Average', 'Seasonal Decomposition', 'Distribution Over Time'),
            vertical_spacing=0.15
        )

        # Time series line
        fig.add_trace(go.Scatter(
            x=resampled.index,
            y=resampled.values,
            mode='lines',
            line=dict(color=self.colors[0], width=2),
            name='Value'
        ), row=1, col=1)

        # Rolling average
        rolling = resampled.rolling(window=7).mean()
        fig.add_trace(go.Scatter(
            x=rolling.index,
            y=rolling.values,
            mode='lines',
            line=dict(color=self.colors[1], width=3),
            name='7-day Moving Avg'
        ), row=1, col=2)

        # Seasonal decomposition (simplified)
        if len(resampled) > 30:
            # Simple seasonal pattern detection
            seasonal_pattern = resampled.groupby(resampled.index.month).mean()
            fig.add_trace(go.Bar(
                x=seasonal_pattern.index,
                y=seasonal_pattern.values,
                marker_color=self.colors[2],
                name='Monthly Pattern'
            ), row=2, col=1)

        # Distribution over time (violin by month)
        df['month'] = df[date_column].dt.month
        months = sorted(df['month'].unique())

        for month in months:
            month_data = df[df['month'] == month][value_column].dropna()
            fig.add_trace(go.Violin(
                y=month_data,
                name=f'Month {month}',
                box_visible=True,
                meanline_visible=True,
                marker_color=self.colors[month % len(self.colors)]
            ), row=2, col=2)

        fig.update_layout(
            title=f'Time Series Analysis: {value_column}',
            template=self.template,
            height=figsize[1],
            width=figsize[0],
            showlegend=True
        )

        return fig

    def create_scatter_matrix(self, df, columns=None, color_by=None, figsize=(1000, 800)):
        """Create modern scatter plot matrix"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()[:6]

        if color_by and color_by in df.columns:
            color = df[color_by]
        else:
            color = None

        fig = px.scatter_matrix(
            df,
            dimensions=columns,
            color=color,
            title="Scatter Plot Matrix",
            template=self.template,
            opacity=0.7,
            height=figsize[1]
        )

        # Update marker size and style
        fig.update_traces(
            diagonal_visible=False,
            showupperhalf=False,
            marker=dict(
                size=5,
                line=dict(width=0.5, color='white')
            )
        )

        fig.update_layout(
            width=figsize[0],
            plot_bgcolor='rgba(240,240,240,0.95)'
        )

        return fig


def visualize_columns(df, columns=None, plot_type='distribution', **kwargs):
    """Main visualization function for user-selected columns"""
    visualizer = ModernVisualizer()

    if columns is None:
        if plot_type == 'distribution':
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        elif plot_type == 'categorical':
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

    plots = {}

    for column in columns:
        if column not in df.columns:
            continue

        # Determine appropriate plot type based on data type
        if plot_type == 'auto':
            if pd.api.types.is_numeric_dtype(df[column]):
                plot_type_actual = 'distribution'
            elif pd.api.types.is_categorical_dtype(df[column]) or pd.api.types.is_object_dtype(df[column]):
                plot_type_actual = 'categorical'
            elif pd.api.types.is_datetime64_any_dtype(df[column]):
                plot_type_actual = 'timeseries'
            else:
                continue
        else:
            plot_type_actual = plot_type

        # Generate appropriate plot
        try:
            if plot_type_actual == 'distribution':
                fig = visualizer.create_distribution_plot(df, column, **kwargs)
            elif plot_type_actual == 'categorical':
                fig = visualizer.create_categorical_plot(df, column, **kwargs)
            elif plot_type_actual == 'correlation':
                fig = visualizer.create_correlation_heatmap(df, **kwargs)
                plots['correlation'] = fig
                break  # Only one correlation plot
            elif plot_type_actual == 'timeseries':
                if 'value_column' in kwargs:
                    fig = visualizer.create_time_series_plot(df, column, kwargs['value_column'], **kwargs)
                else:
                    continue
            elif plot_type_actual == 'scatter_matrix':
                fig = visualizer.create_scatter_matrix(df, columns=columns, **kwargs)
                plots['scatter_matrix'] = fig
                break  # Only one scatter matrix
            else:
                continue

            plots[column] = fig

        except Exception as e:
            print(f"Could not create plot for {column}: {str(e)}")
            continue

    return plots


# Main profiling function
def generate_comprehensive_profile(df, include_visuals=False, columns_to_plot=None):
    """Generate comprehensive data profile with optional visualizations"""

    profile = {
        "basic": generate_basic_profile(df),
        "numerical": generate_numerical_profile(df),
        "categorical": generate_categorical_profile(df),
        "datetime": generate_datetime_profile(df),
        "mixed_types": detect_mixed_type(df),
        "correlations": generate_correlations(df),
        "summary": {
            "total_rows": df.shape[0],
            "total_columns": df.shape[1],
            "numerical_columns": len(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(df.select_dtypes(include=['object', 'category', 'string']).columns),
            "datetime_columns": len([col for col in df.columns if pd.api.types.is_datetime64_any_dtype(df[col])]),
            "total_missing": df.isnull().sum().sum(),
            "missing_percentage": round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 3)
        }
    }

    # Generate visualizations if requested
    if include_visuals:
        visualizations = {}

        # Numerical distributions
        num_cols = columns_to_plot if columns_to_plot else df.select_dtypes(include=[np.number]).columns.tolist()
        if num_cols:
            visualizations["numerical_distributions"] = visualize_columns(
                df, columns=num_cols[:5], plot_type='distribution'
            )

        # Categorical distributions
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            visualizations["categorical_distributions"] = visualize_columns(
                df, columns=cat_cols[:3], plot_type='categorical'
            )

        # Correlation heatmap
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            visualizer = ModernVisualizer()
            visualizations["correlation"] = visualizer.create_correlation_heatmap(df)

        profile["visualizations"] = visualizations

    return profile