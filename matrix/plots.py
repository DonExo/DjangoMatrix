import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import HttpResponse
from datetime import datetime, timedelta


def metrics_plot(request):
    # Generate data for 30 days
    start_date = datetime(2025, 1, 1)
    days = [start_date + timedelta(days=i) for i in range(30)]
    stars = [100 + i * 5 for i in range(30)]
    forks = [20 + i for i in range(30)]
    open_issues = [10 + (i % 3 - 1) for i in range(30)]

    # plt.style.use('seaborn-v0_8-bright')

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(days, stars, label="Stars", marker="o")
    plt.plot(days, forks, label="Forks", marker="o")
    plt.plot(days, open_issues, label="Open Issues", marker="o")
    plt.xlabel("Days")
    plt.ylabel("Count")
    plt.title("GitHub Repository Metrics")
    plt.legend()
    plt.grid(True)

    # Save plot to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # Return image as response
    return HttpResponse(buffer, content_type="image/png")