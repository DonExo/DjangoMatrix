from datetime import timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .models import PackageRepoStats


def get_package_graph(package):
    # Fetch last 9 months of data (approximately 270 days)
    stats = PackageRepoStats.objects.filter(package=package).order_by('-created_at')[:270]

    if not stats:
        return None

    # Reverse to maintain chronological order
    stats = stats[::-1]

    # Group data by week
    weekly_data = {}
    for stat in stats:
        # Get the start of the week (Monday) for each date
        week_start = stat.created_at.date() - timedelta(days=stat.created_at.weekday())

        if week_start not in weekly_data:
            weekly_data[week_start] = {
                'stars': stat.metric_stars,
                'forks': stat.metric_forks,
                'open_issues': stat.metric_open_issues
            }
        else:
            # Use the latest data point for each week
            weekly_data[week_start] = {
                'stars': stat.metric_stars,
                'forks': stat.metric_forks,
                'open_issues': stat.metric_open_issues
            }

    # Sort by date and extract data
    sorted_weeks = sorted(weekly_data.keys())
    days = sorted_weeks
    stars = [weekly_data[week]['stars'] for week in sorted_weeks]
    forks = [weekly_data[week]['forks'] for week in sorted_weeks]
    open_issues = [weekly_data[week]['open_issues'] for week in sorted_weeks]

    def format_hovertemplate(y_label):
        return f"<b>Week of %{{x|%d %b %Y}}</b> - %{{y}}<extra></extra>"

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1)
    fig.add_trace(go.Scatter(x=days, y=stars, mode='lines+markers', name='Stars', line=dict(color='orange'),
                             hovertemplate=format_hovertemplate('')), row=1, col=1)
    fig.add_trace(go.Scatter(x=days, y=forks, mode='lines+markers', name='Forks', line=dict(color='blue'),
                             hovertemplate=format_hovertemplate('')), row=2, col=1)
    fig.add_trace(go.Scatter(x=days, y=open_issues, mode='lines+markers', name='Open Issues', line=dict(color='red'),
                             hovertemplate=format_hovertemplate('')), row=3, col=1)

    fig.update_layout(
        title="Last 9 Months (Weekly)",
        xaxis_title="Weeks",
        template="plotly_white",
        height=500,
        xaxis=dict(
            dtick="W1",  # Show ticks every week
            tickformat="%d %b\n%Y",  # Format: day month, year
        )
    )

    fig.update_yaxes(tickformat=",d", title="Stars", row=1, col=1)
    fig.update_yaxes(tickformat=",d", title="Forks", row=2, col=1)
    fig.update_yaxes(tickformat=",d", title="Open Issues", row=3, col=1)

    # Convert Plotly figure to HTML
    graph_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={'displaylogo': False})
    return graph_html
