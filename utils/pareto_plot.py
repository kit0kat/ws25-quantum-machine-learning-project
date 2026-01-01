import numpy as np
import pandas as pd
from adjustText import adjust_text
from typing import Callable


def pareto_plot(data: pd.DataFrame, x: str, y: str, label: Callable[[pd.Series], str], title: str) -> None:
    data = data.copy().dropna(subset=[x, y])
    data = data.sort_values(by=[x, y], ascending=[True, False])
    data["pareto_front"] = data[y] > data[y].cummax().shift(1, fill_value=-1)
    pareto_mask = data["pareto_front"]
    ax = data[pareto_mask].plot(
        kind="line",
        x=x,
        xlim=(0, data[x].max() * 1.1),
        xlabel=x,
        y=y,
        ylim=(0, 1),
        yticks=np.arange(0, 1.1, 0.1),
        ylabel=y,
        figsize=(16, 10),
        grid=True,
        linestyle="--",
        title=title,
        legend=True,
        label="Pareto Front",
    )
    data[~data["pareto_front"]].plot(kind="scatter", x=x, xlabel=x, y=y, ylabel=y, grid=True, alpha=0.25, s=30, ax=ax)
    data[data["pareto_front"]].plot(kind="scatter", x=x, xlabel=x, y=y, ylabel=y, grid=True, alpha=1.0, ax=ax)
    texts = [ax.text(x=row[x], y=row[y], s=label(row), fontsize=10) for _, row in data[data["pareto_front"]].iterrows()]
    adjust_text(texts, arrowprops={"arrowstyle": "->", "alpha": 0.25})
