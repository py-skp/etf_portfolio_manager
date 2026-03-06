import plotly.express as px
import plotly.graph_objects as go

# Mudric Lab Theme Constants — v2.0 (Teal / Navy)
THEME = {
    "bg": "#0B0E14",
    "paper_bg": "#131722",
    "text": "#E8EAED",
    "text_secondary": "#9CA3AF",
    "primary": "#00D4AA",
    "secondary": "#3B82F6",
    "tertiary": "#8B5CF6",
    "grid": "rgba(255, 255, 255, 0.05)",
    "positive": "#00D4AA",
    "negative": "#EF4444",
    "warning": "#F59E0B",
}

# Multi-series color cycle
SERIES_COLORS = ["#00D4AA", "#3B82F6", "#8B5CF6", "#F59E0B", "#EF4444", "#EC4899", "#06B6D4", "#84CC16"]

def apply_theme(fig):
    """Apply Mudric Lab v2 styling to a Plotly figure"""
    fig.update_layout(
        plot_bgcolor=THEME["paper_bg"],
        paper_bgcolor=THEME["paper_bg"],
        font=dict(family="Inter, -apple-system, sans-serif", color=THEME["text"], size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, linecolor=THEME["grid"]),
        yaxis=dict(showgrid=True, gridcolor=THEME["grid"], zeroline=False, linecolor=THEME["grid"]),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02, xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color=THEME["text_secondary"])
        ),
        hoverlabel=dict(
            bgcolor="#1E2330",
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor=THEME["primary"]
        )
    )
    # Subtle watermark
    fig.add_annotation(
        text="Mudric Lab",
        xref="paper", yref="paper",
        x=0.98, y=0.02,
        showarrow=False,
        font=dict(size=13, color=THEME["text_secondary"]),
        opacity=0.1
    )
    return fig

def plot_price_history(df, x_col="Date", y_cols=["Close"], title="Price History"):
    """Plotly line/area chart for price history.
    x_col: name of a column to use for x-axis, or anything else to use the index.
    """
    fig = go.Figure()
    x_values = df[x_col] if (isinstance(x_col, str) and x_col in df.columns) else df.index

    # Primary line
    fig.add_trace(go.Scatter(
        x=x_values,
        y=df[y_cols[0]],
        mode='lines',
        name=y_cols[0],
        line=dict(color=THEME["primary"], width=2.5),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 170, 0.06)'
    ))

    # Additional lines
    if len(y_cols) > 1:
        for i, col in enumerate(y_cols[1:]):
            c = SERIES_COLORS[(i + 1) % len(SERIES_COLORS)]
            fig.add_trace(go.Scatter(
                x=x_values,
                y=df[col],
                mode='lines',
                name=col,
                line=dict(color=c, width=2)
            ))

    fig.update_layout(title=title)
    return apply_theme(fig)

def plot_allocation_donut(df, names_col, values_col, title="Allocation"):
    """Plotly donut chart for holdings or sector allocation"""
    fig = px.pie(
        df,
        values=values_col,
        names=names_col,
        hole=0.5,
        color_discrete_sequence=SERIES_COLORS
    )
    fig.update_layout(title=title)
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=11,
        marker=dict(line=dict(color=THEME["bg"], width=2))
    )
    return apply_theme(fig)

def plot_horizontal_bar(df, x_col, y_col, title="Bar Chart"):
    """Horizontal bar chart for top holdings or sectors"""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        orientation='h',
        color_discrete_sequence=[THEME["primary"]]
    )
    fig.update_layout(
        title=title,
        yaxis={'categoryorder': 'total ascending'}
    )
    fig.update_traces(marker=dict(line=dict(width=0), cornerradius=4))
    return apply_theme(fig)

def plot_choropleth(df, locations_col, values_col, title="Geographic Exposure"):
    """World map for geographic exposure"""
    fig = px.choropleth(
        df,
        locations=locations_col,
        locationmode="country names",
        color=values_col,
        color_continuous_scale=[[0, THEME["paper_bg"]], [1, THEME["primary"]]],
        title=title
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="rgba(255,255,255,0.1)",
            projection_type='equirectangular',
            bgcolor=THEME["bg"],
            landcolor=THEME["paper_bg"],
            lakecolor=THEME["bg"]
        ),
        paper_bgcolor=THEME["paper_bg"],
        font=dict(family="Inter, sans-serif", color=THEME["text"]),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def plot_drawdown_chart(drawdown_series, title="Historical Drawdowns"):
    """Area chart showing negative drawdowns over time"""
    fig = go.Figure()
    dd_pct = drawdown_series * 100

    fig.add_trace(go.Scatter(
        x=dd_pct.index,
        y=dd_pct.values,
        mode='lines',
        name='Drawdown',
        line=dict(color=THEME["negative"], width=1.5),
        fill='tozeroy',
        fillcolor='rgba(239, 68, 68, 0.12)'
    ))

    fig.update_layout(
        title=title,
        yaxis_title="Drawdown (%)",
        yaxis=dict(zeroline=True, zerolinecolor=THEME["grid"], zerolinewidth=2)
    )
    return apply_theme(fig)

def plot_var_histogram(returns_series, var_95, cvar_95, title="Return Distribution & Tail Risk"):
    """Histogram of returns with vertical lines for VaR and CVaR"""
    fig = go.Figure()
    ret_pct = returns_series * 100
    var_pct = var_95 * 100 if var_95 < 0 else -abs(var_95) * 100
    cvar_pct = cvar_95 * 100 if cvar_95 < 0 else -abs(cvar_95) * 100

    fig.add_trace(go.Histogram(
        x=ret_pct,
        nbinsx=50,
        name='Returns',
        marker_color=THEME["primary"],
        opacity=0.65
    ))

    fig.add_vline(x=var_pct, line_width=2, line_dash="dash", line_color=THEME["negative"],
                  annotation_text="VaR (95%)", annotation_font_color=THEME["negative"])
    fig.add_vline(x=cvar_pct, line_width=2, line_dash="dot", line_color=THEME["warning"],
                  annotation_text="CVaR (95%)", annotation_position="top left",
                  annotation_font_color=THEME["warning"])

    fig.update_layout(
        title=title,
        xaxis_title="Daily Return (%)",
        yaxis_title="Frequency",
        barmode='overlay'
    )
    return apply_theme(fig)

def plot_monte_carlo(paths_df, title="Monte Carlo Simulation (1-Year)"):
    """Spaghetti chart showing multiple return paths"""
    fig = go.Figure()
    num_paths_to_plot = min(100, paths_df.shape[1])

    for i in range(num_paths_to_plot):
        fig.add_trace(go.Scatter(
            x=paths_df.index,
            y=paths_df.iloc[:, i],
            mode='lines',
            line=dict(color=THEME["primary"], width=1),
            opacity=0.04,
            showlegend=False
        ))

    if paths_df.shape[1] > 1:
        percentiles = paths_df.quantile([0.05, 0.5, 0.95], axis=1)
        fig.add_trace(go.Scatter(
            x=percentiles.columns, y=percentiles.loc[0.5],
            mode='lines', name='Median Path',
            line=dict(color=THEME["text"], width=2.5)
        ))
        fig.add_trace(go.Scatter(
            x=percentiles.columns, y=percentiles.loc[0.95],
            mode='lines', name='95th Percentile',
            line=dict(color=THEME["positive"], width=2, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=percentiles.columns, y=percentiles.loc[0.05],
            mode='lines', name='5th Percentile',
            line=dict(color=THEME["negative"], width=2, dash='dash')
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Days",
        yaxis_title="Projected Value"
    )
    return apply_theme(fig)
