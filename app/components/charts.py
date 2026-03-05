import plotly.express as px
import plotly.graph_objects as go

# Mudric Lab Theme Constants
THEME = {
    "bg": "#0F1117",
    "paper_bg": "#1A1A2E",
    "text": "#F3F4F6",
    "primary": "#D4A017",
    "grid": "#262730",
    "positive": "#28a745",
    "negative": "#dc3545"
}

def apply_theme(fig):
    """Apply Mudric Lab styling to a plotly figure"""
    fig.update_layout(
        plot_bgcolor=THEME["paper_bg"],
        paper_bgcolor=THEME["paper_bg"],
        font_color=THEME["text"],
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=THEME["grid"], zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    # Add subtle watermark
    fig.add_annotation(
        text="Mudric Lab",
        xref="paper", yref="paper",
        x=0.98, y=0.02,
        showarrow=False,
        font=dict(size=14, color=THEME["text"]),
        opacity=0.15
    )
    return fig

def plot_price_history(df, x_col="Date", y_cols=["Close"], title="Price History"):
    """Plotly line/area chart for price history"""
    fig = go.Figure()
    
    # Primary line
    fig.add_trace(go.Scatter(
        x=df.index if df.index.name == x_col else df[x_col],
        y=df[y_cols[0]],
        mode='lines',
        name=y_cols[0],
        line=dict(color=THEME["primary"], width=2),
        fill='tozeroy',
        fillcolor='rgba(212, 160, 23, 0.1)'
    ))
    
    # Additional lines (e.g., benchmark comparison)
    if len(y_cols) > 1:
        colors = ["#4D5360", "#94A3B8", "#64748B"]
        for i, col in enumerate(y_cols[1:]):
            c = colors[i % len(colors)]
            fig.add_trace(go.Scatter(
                x=df.index if df.index.name == x_col else df[x_col],
                y=df[col],
                mode='lines',
                name=col,
                line=dict(color=c, width=1.5)
            ))

    fig.update_layout(title=title)
    return apply_theme(fig)

def plot_allocation_donut(df, names_col, values_col, title="Allocation"):
    """Plotly donut chart for holdings or sector allocation"""
    fig = px.pie(
        df, 
        values=values_col, 
        names=names_col, 
        hole=0.4,
        color_discrete_sequence=[
            THEME["primary"], "#E8B838", "#F2CD5C", "#BA8A0F", "#9A730D", 
            "#7A5C0A", "#57606f", "#747d8c", "#a4b0be", "#dfe4ea"
        ]
    )
    fig.update_layout(title=title)
    fig.update_traces(textposition='inside', textinfo='percent+label')
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
        yaxis={'categoryorder':'total ascending'}
    )
    return apply_theme(fig)

def plot_choropleth(df, locations_col, values_col, title="Geographic Exposure"):
    """World map for geographic exposure"""
    fig = px.choropleth(
        df,
        locations=locations_col,
        locationmode="country names", # Fallback, assumes mostly readable country names
        color=values_col,
        color_continuous_scale=[THEME["paper_bg"], THEME["primary"]],
        title=title
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor=THEME["grid"],
            projection_type='equirectangular',
            bgcolor=THEME["bg"]
        ),
        paper_bgcolor=THEME["paper_bg"],
        font_color=THEME["text"],
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def plot_drawdown_chart(drawdown_series, title="Historical Drawdowns"):
    """Area chart showing negative drawdowns over time"""
    fig = go.Figure()
    
    # Convert series to percent for display
    dd_pct = drawdown_series * 100
    
    fig.add_trace(go.Scatter(
        x=dd_pct.index,
        y=dd_pct.values,
        mode='lines',
        name='Drawdown',
        line=dict(color=THEME["negative"], width=1.5),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.2)' # Bootstrap danger red with opacity
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
    
    # Returns to percentage
    ret_pct = returns_series * 100
    var_pct = var_95 * 100 if var_95 < 0 else -abs(var_95) * 100 # Ensure negative representation
    cvar_pct = cvar_95 * 100 if cvar_95 < 0 else -abs(cvar_95) * 100
    
    fig.add_trace(go.Histogram(
        x=ret_pct,
        nbinsx=50,
        name='Returns',
        marker_color=THEME["primary"],
        opacity=0.7
    ))
    
    # Add vertical lines for VaR and CVaR
    fig.add_vline(x=var_pct, line_width=2, line_dash="dash", line_color=THEME["negative"], annotation_text="VaR (95%)")
    fig.add_vline(x=cvar_pct, line_width=2, line_dash="dot", line_color=THEME["negative"], annotation_text="CVaR (95%)", annotation_position="top left")
    
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
    
    # Plot a subset of paths so the browser doesn't crash (max 100)
    num_paths_to_plot = min(100, paths_df.shape[1])
    
    for i in range(num_paths_to_plot):
        fig.add_trace(go.Scatter(
            x=paths_df.index,
            y=paths_df.iloc[:, i],
            mode='lines',
            line=dict(color=THEME["primary"], width=1),
            opacity=0.05, # Very transparent lines
            showlegend=False
        ))
        
    # Highlight the median path and the 5th/95th percentiles if we have enough paths
    if paths_df.shape[1] > 1:
        percentiles = paths_df.quantile([0.05, 0.5, 0.95], axis=1)
        
        # Median path
        fig.add_trace(go.Scatter(
            x=percentiles.columns,
            y=percentiles.loc[0.5],
            mode='lines',
            name='Median Path',
            line=dict(color=THEME["text"], width=2)
        ))
        # Top 5% bound
        fig.add_trace(go.Scatter(
            x=percentiles.columns,
            y=percentiles.loc[0.95],
            mode='lines',
            name='95th Percentile',
            line=dict(color=THEME["positive"], width=2, dash='dash')
        ))
        # Bottom 5% bound
        fig.add_trace(go.Scatter(
            x=percentiles.columns,
            y=percentiles.loc[0.05],
            mode='lines',
            name='5th Percentile',
            line=dict(color=THEME["negative"], width=2, dash='dash')
        ))
        
    fig.update_layout(
         title=title,
         xaxis_title="Days",
         yaxis_title="Projected Value"
    )
    return apply_theme(fig)
