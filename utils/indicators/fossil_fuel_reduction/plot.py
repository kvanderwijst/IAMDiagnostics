import numpy as np
from plotly.subplots import make_subplots
from utils.plot.general import add_model_comparison
from .calculate import VARIABLES, LABELS


def create_fig(meta, models, year: str, xrange=None, exclude_models=None):

    if exclude_models is not None:
        models = models[~models["Full model"].str.contains(exclude_models)].copy()
        models["i"] = np.arange(len(models))

    fig_FFR = make_subplots(
        1,
        2,
        horizontal_spacing=0.0,
        column_widths=[0.45, 0.55],
        subplot_titles=(
            f"<b>a.</b> Primary Energy decomposition ({year}) <br> ",
            f"<b>b.</b> FFR per model ({year})<br> ",
        ),
        shared_yaxes=True,
    )

    ##############
    # 3a:
    ##############

    energy_colors = ["#d62728", "#d67a7a", "#ff7f0e", "#2ca02c", "#96d096", "#1f77b4"]

    xpos = -0.05
    for var_suffix, label, color, labelwidth in zip(
        VARIABLES, LABELS, energy_colors, [0.09, 0.09, 0.1, 0.11, 0.11, 0.1]
    ):
        col = f"Primary Energy|{var_suffix} {year}"
        energy_values = meta[col]

        var_values = models.merge(
            energy_values.reset_index(),
            how="left",
            left_on="Full model",
            right_on="Model",
        )
        fig_FFR.add_bar(
            y=var_values["i"],
            x=var_values[col],
            orientation="h",
            name=label,
            marker_color=color,
            showlegend=False,
        )

        # Add legend
        height, width = 0.04, 0.04 * 400 / 840
        ypos = -0.1
        fig_FFR.add_shape(
            type="rect",
            xref="paper",
            yref="paper",
            x0=xpos - width / 2,
            x1=xpos + width / 2,
            y0=ypos - height / 2,
            y1=ypos + height / 2,
            fillcolor=color,
            line_width=0,
        )
        fig_FFR.add_annotation(
            xref="paper",
            yref="paper",
            x=xpos + 0.6 * width,
            y=ypos,
            yanchor="top",
            yshift=12,
            xanchor="left",
            align="left",
            showarrow=False,
            text=label,
        )
        xpos += labelwidth

    # check_values = models.merge(
    #     get(data, policy_scenario, 'Primary Energy', year).reset_index(),
    #     how='left', left_on='Full model', right_on='Model'
    # )
    # fig_FFR.add_scatter(
    #     x=check_values[year], y=check_values['i'],
    #     mode='markers', marker={'symbol': 'x', 'color': '#BBB'},
    #     showlegend=False
    # )

    ##############
    # 3b: FFR
    ##############

    col_FFR = f"FFR {year}"

    add_model_comparison(
        fig_FFR,
        meta,
        models,
        2,
        col_FFR,
        narrative_left="Small fossil fuel red.",
        narrative_right="Large fossil fuel red.",
        shared_yaxes=True,
        showlegendlines=False,
        exclude_models=exclude_models,
    )

    # Update layout
    (
        fig_FFR.update_xaxes(
            col=1, title=f"Primary Energy (EJ in {year})", title_standoff=40
        )
        .update_xaxes(
            col=2,
            tickvals=np.arange(-0.2, 2, 0.2),
            title="FFR",
            range=xrange,
            title_standoff=40,
        )
        .update_layout(
            barmode="stack",
            width=860,
            height=400,
            margin={"l": 60, "r": 30, "t": 50, "b": 70},
            hovermode="closest",
        )
    )
    return fig_FFR
