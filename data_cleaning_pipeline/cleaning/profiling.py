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
from matplotlib.colors import LinearSegmentedColormap, to_hex
import colorsys

warnings.filterwarnings('ignore')

# Set modern styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Professional color palettes
PROFESSIONAL_COLORS = {
    'primary': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E'],
    'sequential': ['#003f5c', '#2f4b7c', '#665191', '#a05195', '#d45087', '#f95d6a', '#ff7c43', '#ffa600'],
    'diverging': ['#8c510a', '#d8b365', '#f6e8c3', '#c7eae5', '#5ab4ac', '#01665e'],
    'qualitative': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
}

# Create custom colormap
custom_cmap = LinearSegmentedColormap.from_list("modern", ['#2E86AB', '#A23B72', '#F18F01'])


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

        # Normality tests
        if len(col_data) >= 20 and len(col_data) <= 5000:
            try:
                # D'Agostino's K^2 test
                _, dagostino_p = normaltest(col_data)
                stat["normality_pvalue"] = round(dagostino_p, 6)
                stat["is_normal"] = dagostino_p > 0.05

                # Shapiro-Wilk test
                if len(col_data) <= 5000:
                    _, shapiro_p = stats.shapiro(col_data)
                    stat["shapiro_pvalue"] = round(shapiro_p, 6)
            except:
                pass

        # Outlier detection
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers_iqr = col_data[(col_data < lower_bound) | (col_data > upper_bound)]

        # Z-score method
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
                "gini_coefficient": round(1 - sum((value_counts_normalized ** 2)), 6),
                "entropy": round(stats.entropy(value_counts_normalized), 6)
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
                "inconsistent_range": (col_data.max() - col_data.min()).days > 365 * 50,
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

        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue

        sample_size = min(len(non_null), 100)
        sample = non_null.sample(sample_size, random_state=42)

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
        correlations["pearson"] = num_cols.corr(method="pearson").round(4).to_dict()
        correlations["spearman"] = num_cols.corr(method="spearman").round(4).to_dict()
        correlations["kendall"] = num_cols.corr(method="kendall").round(4).to_dict()

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

        correlations["multicollinearity_warning"] = len(high_corr) > 0

        correlations["recommendations"] = {
            "consider_removing": [pair["feature2"] for pair in high_corr[:3]] if high_corr else [],
            "potential_interactions": [pair for pair in moderate_corr[:5]] if moderate_corr else []
        }

    return correlations


#### FIXED VISUALIZATION MODULE
class ProfessionalVisualizer:
    """Professional visualizer with working, downloadable plots"""

    def __init__(self):
        self.colors = PROFESSIONAL_COLORS['primary']
        self.template = "plotly_white"
        self.config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect',
                                    'eraseshape'],
            'modeBarButtonsToRemove': [],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'plot_download',
                'height': 800,
                'width': 1200,
                'scale': 2
            },
            'scrollZoom': True,
            'responsive': True
        }

    def _rgb_to_hex(self, r, g, b):
        """Convert RGB to hex color"""
        return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

    def create_distribution_plot(self, df, column, figsize=(1000, 700)):
        """Create clean distribution analysis plot"""
        data = df[column].dropna()

        if len(data) == 0:
            return None

        # Calculate statistics
        stats_info = {
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'skew': data.skew(),
            'kurtosis': data.kurtosis(),
            'q1': data.quantile(0.25),
            'q3': data.quantile(0.75)
        }

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                f'Distribution Histogram - {column}',
                'Box & Violin Plot',
                'Cumulative Distribution',
                'Statistics Summary'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # 1. Histogram with KDE
        try:
            hist_data = [data.tolist()]
            distplot = ff.create_distplot(hist_data, [column], show_hist=True, show_rug=False,
                                          colors=[self.colors[0]])
            for trace in distplot.data:
                fig.add_trace(trace, row=1, col=1)
        except:
            # Fallback: simple histogram
            fig.add_trace(
                go.Histogram(
                    x=data,
                    name='Histogram',
                    nbinsx=50,
                    marker_color=self.colors[0],
                    opacity=0.7
                ),
                row=1, col=1
            )

        # Add mean and median lines
        fig.add_vline(
            x=stats_info['mean'],
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {stats_info['mean']:.2f}",
            annotation_position="top right",
            row=1, col=1
        )

        fig.add_vline(
            x=stats_info['median'],
            line_dash="dot",
            line_color="green",
            annotation_text=f"Median: {stats_info['median']:.2f}",
            annotation_position="bottom right",
            row=1, col=1
        )

        # 2. Box & Violin Plot
        fig.add_trace(
            go.Box(
                y=data,
                name='Box Plot',
                marker_color=self.colors[1],
                boxmean='sd',
                showlegend=False
            ),
            row=1, col=2
        )

        fig.add_trace(
            go.Violin(
                y=data,
                name='Violin Plot',
                marker_color=self.colors[2],
                box_visible=True,
                meanline_visible=True,
                points=False,
                showlegend=False
            ),
            row=1, col=2
        )

        # 3. Cumulative Distribution
        sorted_data = np.sort(data)
        cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)

        # Use simple hex color for fillcolor
        fig.add_trace(
            go.Scatter(
                x=sorted_data,
                y=cdf,
                mode='lines',
                name='CDF',
                line=dict(color=self.colors[3], width=3),
                fill='tozeroy',
                fillcolor='rgba(46, 134, 171, 0.3)'  # Fixed: Using hex color with alpha
            ),
            row=2, col=1
        )

        # 4. Statistics Summary as a table
        stats_text = f"""
        <b>Statistics Summary:</b><br>
        • Mean: {stats_info['mean']:.2f}<br>
        • Median: {stats_info['median']:.2f}<br>
        • Std Dev: {stats_info['std']:.2f}<br>
        • Skewness: {stats_info['skew']:.2f}<br>
        • Kurtosis: {stats_info['kurtosis']:.2f}<br>
        • IQR: {stats_info['q3'] - stats_info['q1']:.2f}<br>
        • Range: {data.max() - data.min():.2f}
        """

        fig.add_annotation(
            xref="x domain",
            yref="y domain",
            x=0.5,
            y=0.5,
            text=stats_text,
            showarrow=False,
            align="left",
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="black",
            borderwidth=1,
            borderpad=10,
            font=dict(size=12),
            row=2, col=2
        )

        # Add a placeholder trace to enable the subplot
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=0),
                showlegend=False
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title=f'Distribution Analysis: {column}',
            template=self.template,
            showlegend=True,
            height=figsize[1],
            width=figsize[0],
            plot_bgcolor='rgba(245,245,245,0.9)',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            hovermode='x unified'
        )

        # Update axes
        fig.update_xaxes(title_text=column, row=1, col=1)
        fig.update_yaxes(title_text="Density", row=1, col=1)
        fig.update_xaxes(title_text="Value", row=2, col=1)
        fig.update_yaxes(title_text="Cumulative Probability", row=2, col=1)

        # Remove axes for stats table
        fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, row=2, col=2)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=2, col=2)

        return fig

    def create_categorical_plot(self, df, column, top_n=15, figsize=(900, 600)):
        """Create clean categorical visualization"""
        data = df[column].dropna().astype(str)

        if len(data) == 0:
            return None

        value_counts = data.value_counts().head(top_n)
        categories = [str(cat) for cat in value_counts.index]
        counts = value_counts.values.tolist()
        percentages = (value_counts.values / len(data) * 100).round(2)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Bar Chart',
                'Pie Chart',
                'Horizontal Bar Chart',
                'Value Counts'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # 1. Bar Chart
        fig.add_trace(
            go.Bar(
                x=categories,
                y=counts,
                marker_color=self.colors,
                marker_line_color='rgba(0,0,0,0.3)',
                marker_line_width=1,
                text=counts,
                textposition='auto',
                name='Count'
            ),
            row=1, col=1
        )

        # 2. Pie Chart
        fig.add_trace(
            go.Pie(
                labels=categories,
                values=counts,
                hole=0.3,
                marker_colors=px.colors.qualitative.Set3,
                textinfo='label+percent',
                textposition='outside',
                name='Distribution'
            ),
            row=1, col=2
        )

        # 3. Horizontal Bar Chart
        fig.add_trace(
            go.Bar(
                y=categories,
                x=counts,
                orientation='h',
                marker_color=px.colors.sequential.Plasma,
                text=[f'{p}%' for p in percentages],
                textposition='auto',
                name='Horizontal'
            ),
            row=2, col=1
        )

        # 4. Value Counts Table
        table_data = []
        for cat, count, perc in zip(categories, counts, percentages):
            table_data.append([cat, f'{count:,}', f'{perc}%'])

        fig.add_trace(
            go.Table(
                header=dict(
                    values=['Category', 'Count', 'Percentage'],
                    fill_color='#2E86AB',
                    align='left',
                    font=dict(color='white', size=12)
                ),
                cells=dict(
                    values=[[row[0] for row in table_data],
                            [row[1] for row in table_data],
                            [row[2] for row in table_data]],
                    fill_color='white',
                    align='left'
                )
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title=f'Categorical Analysis: {column}',
            template=self.template,
            showlegend=False,
            height=figsize[1],
            width=figsize[0],
            plot_bgcolor='rgba(245,245,245,0.9)',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )

        # Update axes
        fig.update_xaxes(title_text="Count", row=1, col=1)
        fig.update_yaxes(title_text="Categories", row=2, col=1)
        fig.update_xaxes(tickangle=45, row=1, col=1)

        return fig

    def create_correlation_heatmap(self, df, method='pearson', figsize=(800, 700)):
        """Create correlation matrix with fixed parameters"""
        num_cols = df.select_dtypes(include=[np.number])

        if num_cols.shape[1] < 2:
            return None

        corr_matrix = num_cols.corr(method=method)

        # Create heatmap with CORRECT colorbar parameters
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
            hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>',
            colorbar=dict(
                title='Correlation',
                thickness=20,
                len=0.8
            )
        ))

        # Update layout
        fig.update_layout(
            title=f'Correlation Matrix ({method.capitalize()})',
            template=self.template,
            height=figsize[1],
            width=figsize[0],
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            xaxis_tickangle=45,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=100, r=50, t=80, b=100)
        )

        return fig

    def create_data_quality_summary(self, df, figsize=(1000, 600)):
        """Create simple data quality summary"""

        # Calculate metrics
        missing_counts = df.isnull().sum()
        missing_percent = (df.isnull().mean() * 100).round(2)
        duplicates = df.duplicated().sum()
        duplicate_percent = (duplicates / len(df) * 100).round(2)
        total_missing = missing_counts.sum()
        total_missing_percent = (total_missing / (len(df) * len(df.columns)) * 100).round(2)

        # Create figure
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Missing Values by Column',
                'Data Types Distribution',
                'Quality Metrics',
                'Top Issues'
            ),
            specs=[
                [{"type": "bar"}, {"type": "pie"}],
                [{"type": "indicator"}, {"type": "table"}]
            ],
            vertical_spacing=0.2,
            horizontal_spacing=0.2
        )

        # 1. Missing Values Bar Chart
        missing_cols = missing_counts[missing_counts > 0]
        if len(missing_cols) > 0:
            fig.add_trace(
                go.Bar(
                    x=missing_cols.values,
                    y=missing_cols.index,
                    orientation='h',
                    marker_color='#ef4444',
                    name='Missing Values',
                    text=[f'{v:,}' for v in missing_cols.values],
                    textposition='auto'
                ),
                row=1, col=1
            )
        else:
            fig.add_annotation(
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=0.5,
                text="No Missing Values ✓",
                showarrow=False,
                font=dict(size=16, color="green"),
                row=1, col=1
            )

        # 2. Data Types Pie Chart
        dtype_counts = df.dtypes.value_counts()
        fig.add_trace(
            go.Pie(
                labels=[str(d) for d in dtype_counts.index],
                values=dtype_counts.values,
                hole=0.3,
                marker_colors=px.colors.qualitative.Set3,
                name='Data Types'
            ),
            row=1, col=2
        )

        # 3. Quality Metrics Indicator
        quality_score = 100 - (missing_percent.mean() + duplicate_percent)
        quality_score = max(0, min(100, quality_score))

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=quality_score,
                title={'text': "Data Quality Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#2E86AB"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "lightgreen"}
                    ]
                }
            ),
            row=2, col=1
        )

        # 4. Issues Table
        issues = []
        if total_missing_percent > 5:
            issues.append(['Missing Data', f'{total_missing_percent}%', '⚠️'])
        if duplicate_percent > 10:
            issues.append(['Duplicate Rows', f'{duplicate_percent}%', '⚠️'])

        if issues:
            fig.add_trace(
                go.Table(
                    header=dict(
                        values=['Issue', 'Value', 'Status'],
                        fill_color='#2E86AB',
                        font=dict(color='white', size=12)
                    ),
                    cells=dict(
                        values=[[issue[0] for issue in issues],
                                [issue[1] for issue in issues],
                                [issue[2] for issue in issues]],
                        fill_color='white'
                    )
                ),
                row=2, col=2
            )
        else:
            fig.add_annotation(
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=0.5,
                text="No Quality Issues ✓",
                showarrow=False,
                font=dict(size=16, color="green"),
                row=2, col=2
            )

        # Update layout
        fig.update_layout(
            title='Data Quality Summary',
            template=self.template,
            height=figsize[1],
            width=figsize[0],
            showlegend=False,
            plot_bgcolor='rgba(245,245,245,0.9)',
            paper_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )

        return fig

    def get_plot_html(self, fig, title=""):
        """Convert plot to HTML with download capability"""
        if fig is None:
            return None

        # Configure for download
        config = {
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['toImage'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'{title or "plot"}_download',
                'height': 600,
                'width': 800,
                'scale': 2
            }
        }

        # Add title if not present
        if title and not fig.layout.title.text:
            fig.update_layout(title=title)

        # Convert to HTML
        html = fig.to_html(full_html=False, include_plotlyjs='cdn', config=config)

        return {
            'html': html,
            'title': title,
            'config': config
        }


# Main profiling function with SIMPLIFIED visualizations
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
            "missing_percentage": round(df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 3),
            "duplicate_percentage": round(df.duplicated().mean() * 100, 3)
        }
    }

    # Generate SIMPLIFIED visualizations if requested
    if include_visuals:
        visualizations = {}
        visualizer = ProfessionalVisualizer()

        # 1. Data Quality Summary (always create)
        try:
            quality_summary = visualizer.create_data_quality_summary(df)
            if quality_summary:
                visualizations["data_quality_summary"] = quality_summary
                # Also get HTML version
                visualizations["data_quality_html"] = visualizer.get_plot_html(
                    quality_summary, "Data Quality Summary"
                )
        except Exception as e:
            print(f"⚠️ Could not create data quality summary: {str(e)}")

        # 2. Numerical Distributions
        num_cols = []
        if columns_to_plot:
            num_cols = [col for col in columns_to_plot if col in df.select_dtypes(include=[np.number]).columns]
        else:
            # Auto-select: take first 2 numerical columns
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:2]

        num_plots = {}
        for col in num_cols:
            try:
                fig = visualizer.create_distribution_plot(df, col)
                if fig:
                    num_plots[col] = fig
                    # Also store HTML version
                    num_plots[f"{col}_html"] = visualizer.get_plot_html(fig, f"Distribution - {col}")
            except Exception as e:
                print(f"⚠️ Could not create distribution plot for {col}: {str(e)}")

        if num_plots:
            visualizations["numerical_distributions"] = num_plots

        # 3. Categorical Plots
        cat_cols = []
        if columns_to_plot:
            cat_cols = [col for col in columns_to_plot if col not in num_cols and col in df.columns]
        else:
            # Auto-select: take first 2 categorical columns
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()[:2]

        cat_plots = {}
        for col in cat_cols:
            try:
                fig = visualizer.create_categorical_plot(df, col)
                if fig:
                    cat_plots[col] = fig
                    # Also store HTML version
                    cat_plots[f"{col}_html"] = visualizer.get_plot_html(fig, f"Categorical - {col}")
            except Exception as e:
                print(f"⚠️ Could not create categorical plot for {col}: {str(e)}")

        if cat_plots:
            visualizations["categorical_distributions"] = cat_plots

        # 4. Correlation Matrix (if enough numeric columns)
        if len(df.select_dtypes(include=[np.number]).columns) > 1:
            try:
                correlation_plot = visualizer.create_correlation_heatmap(df)
                if correlation_plot:
                    visualizations["correlation_matrix"] = correlation_plot
                    # Also store HTML version
                    visualizations["correlation_html"] = visualizer.get_plot_html(
                        correlation_plot, "Correlation Matrix"
                    )
            except Exception as e:
                print(f"⚠️ Could not create correlation matrix: {str(e)}")

        if visualizations:
            profile["visualizations"] = visualizations

    return profile


# Simple wrapper for frontend usage
def create_simple_visualizations(df, columns=None):
    """Create simple visualizations for frontend display"""
    visualizer = ProfessionalVisualizer()
    result = {}

    # Data Quality Summary
    try:
        quality_fig = visualizer.create_data_quality_summary(df)
        if quality_fig:
            result['quality_summary'] = visualizer.get_plot_html(quality_fig, "Data Quality")
    except:
        pass

    # Distribution plots for numerical columns
    if columns:
        num_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df.get(col, pd.Series(dtype='float')))]
        for col in num_cols[:3]:  # Limit to 3
            try:
                fig = visualizer.create_distribution_plot(df, col)
                if fig:
                    result[f'dist_{col}'] = visualizer.get_plot_html(fig, f"Distribution - {col}")
            except:
                pass

    # Categorical plots
    if columns:
        cat_cols = [col for col in columns if col not in num_cols and col in df.columns]
        for col in cat_cols[:2]:  # Limit to 2
            try:
                fig = visualizer.create_categorical_plot(df, col)
                if fig:
                    result[f'cat_{col}'] = visualizer.get_plot_html(fig, f"Categorical - {col}")
            except:
                pass

    # Correlation matrix
    if len(df.select_dtypes(include=[np.number]).columns) > 1:
        try:
            corr_fig = visualizer.create_correlation_heatmap(df)
            if corr_fig:
                result['correlation'] = visualizer.get_plot_html(corr_fig, "Correlation Matrix")
        except:
            pass

    return result