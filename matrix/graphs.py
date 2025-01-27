import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .models import PackageRepoStats


def get_package_graph(package):
    stats = PackageRepoStats.objects.filter(package=package).order_by('-created_at')[:30]

    if not stats:
        return None

    days = [stat.created_at.date() for stat in stats][::-1]  # Reverse to maintain chronological order
    stars = [stat.metric_stars for stat in stats][::-1]
    forks = [stat.metric_forks for stat in stats][::-1]
    open_issues = [stat.metric_open_issues for stat in stats][::-1]

    def format_hovertemplate(y_label):
        return f"<b>%{{x|%d %b %Y}}</b> - %{{y}}<extra></extra>"

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    fig.add_trace(go.Scatter(x=days, y=stars, mode='lines+markers', name='Stars', line=dict(color='orange'), hovertemplate=format_hovertemplate('')), row=1, col=1)
    fig.add_trace(go.Scatter(x=days, y=forks, mode='lines+markers', name='Forks', line=dict(color='blue'), hovertemplate=format_hovertemplate('')), row=2, col=1)
    fig.add_trace(go.Scatter(x=days, y=open_issues, mode='lines+markers', name='Open Issues', line=dict(color='red'), hovertemplate=format_hovertemplate('')), row=3, col=1)

    fig.update_layout(
        title="GitHub Repository Metrics",
        xaxis_title="Days",
        template="plotly_white",
        height=500,
    )

    fig.update_yaxes(tickformat="K", title="Stars", row=1, col=1)
    fig.update_yaxes(title="Forks", row=2, col=1)
    fig.update_yaxes(tickformat=",d", title="Open Issues", row=3, col=1)

    # Convert Plotly figure to HTML
    graph_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={'displaylogo': False})
    return graph_html
