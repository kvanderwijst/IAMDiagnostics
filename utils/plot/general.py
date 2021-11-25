"""
General utils
 - add_legend_item: Adds Plotly legend item manually
"""

import numpy as np


import plotly.io as pio

pio.templates.default = "none"
try:
    # Bugfix for Plotly default export size
    pio.kaleido.scope.default_width = None
    pio.kaleido.scope.default_height = None
except:
    pass


GRIDCOLOR = "rgba(.2,.2,.2,.1)"


def add_model_comparison(
    fig,
    meta,
    models,
    fig_col,
    meta_col,
    label_posx=None,
    label_width=None,
    narrative_left=None,
    narrative_right=None,
    shared_yaxes=False,
    showlegendlines=True,
    labelshift=1,
    exclude_models=None,
):
    """
    Used to create the right part of each figure: the indicator comparison.
    This is shared code for each indicator.
                        
    fig:            Plotly subplot figure
    fig_col:        typically will be 2 if the right subplot is used
    meta_col:       column from meta df used to get the indicator values
    label_posx [None]: by default, the position (relative to the x-axis of col fig_col)
            is calculated automatically based on the spread of indicator values. This can
            be overrided manually if this calculation doesn't work properly.
    narrative_left: string for arrow pointing left of median value of indicators
    narrative_right: same for right
    shared_yaxes:   if the left subplot has to share the same y-axis, set to True
    showlegendlines: while the legend is always shown, the coloured lines are not always
            necessary. Setting this to False hides these lines.
    labelshift:     shift the labels a bit more ( > 1) or less ( < 1) to the left.
    exclude_models: list of model names that should be excluded from this plot
    models:         by default the normal `models` dataframe, but can be used as override.
    """

    if exclude_models is not None:
        models = models[~models["Full model"].str.contains(exclude_models)].copy()
        models["i"] = np.arange(len(models))

    n = models["i"].max()
    meta_selection = meta[meta["Stripped model"].isin(models.index)]

    # Add legend items
    for name, symbol, size in [("Newest", "star", 8), ("Older version", "circle", 4)]:
        add_legend_item(
            fig,
            name,
            marker={"symbol": symbol, "size": size, "color": "black"},
            legendgroup="Age",
        )

    # Add shade for 1-sigma range
    q0, median, q1 = meta_selection[meta_col].quantile([0.16, 0.5, 0.84])
    # mean = meta_selection[meta_col].mean()
    fig.add_scatter(
        x=[q0, q0, q1, q1],
        y=[-1, n + 1, n + 1, -1],
        fill="toself",
        fillcolor="rgba(0,0,0,.1)",
        line_width=0,
        mode="lines",
        name="16-84th perc.",
        row=1,
        col=fig_col,
    )

    # Add lines for median and mean
    fig.add_scatter(
        x=[median, median],
        y=[-1, n + 1],
        mode="lines",
        line={"color": "#888", "width": 2},
        name="Median",
        row=1,
        col=fig_col,
    )

    # Calculate position of legend items
    vmin, vmax = meta_selection[meta_col].min(), meta_selection[meta_col].max()
    label_posx = (
        vmin - 0.66 * labelshift * (vmax - vmin) if label_posx is None else label_posx
    )
    label_width = 0.15 * (vmax - vmin) if label_width is None else label_width

    for model, (modeltype, fullmodel, i, color) in models.iterrows():

        selection = meta_selection[meta_selection["Stripped model"] == model]

        # Add dots and stars
        fig.add_scatter(
            x=selection[meta_col],
            y=[i] * len(selection),
            marker={
                "color": color,
                "opacity": 1,
                "symbol": [
                    "star" if is_newest else "circle"
                    for is_newest in selection["Newest"]
                ],
                "size": [12 if is_newest else 7 for is_newest in selection["Newest"]],
                "line": {"color": "#FFF", "width": 1},
            },
            mode="markers",
            showlegend=False,
            row=1,
            col=fig_col,
        )

        # Add legend line
        if showlegendlines:
            fig.add_scatter(
                x=[label_posx - label_width, label_posx],
                y=[i, i],
                mode="lines",
                line={"color": color, "width": 3},
                row=1,
                col=fig_col,
                showlegend=False,
            )

        # Name of model
        fig.add_annotation(
            text=model,
            x=label_posx,
            y=i,
            xanchor="left",
            row=1,
            col=fig_col,
            bgcolor="#FFF",
            showarrow=False,
        )

    # Add model type brackets
    x_max = meta_selection[meta_col].max()
    dx = x_max - meta_selection[meta_col].min()

    x_right = 0.05 * dx + x_max  # 6% to the right of the most right point
    x_width = 0.03 * dx
    for modeltype, selection in models.groupby("Type"):
        first, last = selection["i"].min(), selection["i"].max()
        # Bracket itself
        dy = 0.3
        fig.add_scatter(
            x=[x_right, x_right + x_width, x_right + x_width, x_right],
            y=[first - dy, first - dy, last + dy, last + dy],
            mode="lines",
            line_color="#999",
            showlegend=False,
            row=1,
            col=fig_col,
        )
        # Name of model type
        fig.add_annotation(
            x=x_right + 1.25 * x_width,
            y=(first + last) / 2,
            text=modeltype,
            textangle=90,
            bgcolor="#FFF",
            showarrow=False,
            yanchor="middle",
            xanchor="left",
            row=1,
            col=fig_col,
        )

    # Add narrative arrows
    for label, toLeft in [(narrative_left, True), (narrative_right, False)]:
        if label is None:
            continue
        arrowlength = 65
        multiplier = -1 if toLeft else 1
        fig.add_annotation(
            xref=f"x{fig_col}",
            yref="paper",
            xanchor="center",
            yanchor="top",
            x=median,
            y=-0.08,
            ax=arrowlength * multiplier,
            ay=0,
            xshift=multiplier * 5,
            width=arrowlength * 2,
            align="right" if toLeft else "left",
            text=label,
            showarrow=True,
            arrowside="start",
        )

    # Update layout
    fig.update_yaxes(
        col=None if shared_yaxes else fig_col,
        gridcolor=GRIDCOLOR,
        tickvals=models["i"],
        range=[n + 1, -1],
        zeroline=False,
        showticklabels=False,
    ).update_layout(legend={"tracegroupgap": 0, "y": 0.5},)


def add_legend_item(fig, name="", mode="markers", **kwargs):
    """
    In Plotly, a legend item can be added manually by adding an empty trace
    """
    fig.add_scatter(x=[None], y=[None], name=name, mode=mode, **kwargs)


##################
## Functions required to generate confidence ellipse
##################


def ellipse(a, b, npoints):
    x = np.linspace(-a, a, npoints)
    y1 = b * np.sqrt(1 - (x / a) ** 2)
    y2 = -y1
    return np.concatenate([x, x[::-1]]), np.concatenate([y1, y2[::-1]])


def rotate(x, y, theta):
    return x * np.cos(theta) - y * np.sin(theta), x * np.sin(theta) + y * np.cos(theta)


def confidence_ellipse(x_values, y_values, nsigma, npoints=300):
    # Calculate center of confidence ellipse
    mu_x, mu_y = np.mean(x_values), np.mean(y_values)

    # Calculate correlation coefficient and covariances
    cov_matrix = np.cov([x_values, y_values])
    cov_xy = cov_matrix[0, 1]
    sigma_x, sigma_y = np.sqrt(cov_matrix[0, 0]), np.sqrt(cov_matrix[1, 1])
    rho = cov_xy / (sigma_x * sigma_y)

    # Get the x-y points for the default ellipse with a=sqrt(1+rho), b=sqrt(1-rho)
    ellipse_x, ellipse_y = ellipse(np.sqrt(1 + rho), np.sqrt(1 - rho), npoints)

    # Rotate ellipse 45 degrees counter-clockwise
    ellipse_x, ellipse_y = rotate(ellipse_x, ellipse_y, np.pi / 4)

    # Scale ellipse horizontally by (2*n*sigma_x) and vertically by (2*n*sigma_y)
    # Note: scaling by 2*n*sigma_x means that the x_values (centered around 0) should
    # be multiplied by n*sigma_x, not 2*n*sigma_x
    ellipse_x = nsigma * sigma_x * ellipse_x
    ellipse_y = nsigma * sigma_y * ellipse_y

    # Shift ellipse such that its center is situated at the point mu_x, mu_y
    ellipse_x += mu_x
    ellipse_y += mu_y

    return ellipse_x, ellipse_y
