import numpy as np
from plotly.subplots import make_subplots
from utils.plot.general import add_model_comparison, GRIDCOLOR


def create_fig(
    meta,
    models,
    year: str,
    var_label="CO2 FFI",
    narrative_left="Less CO<sub>2</sub> reduction",
    narrative_right="More CO<sub>2</sub> reduction",
    xrange=None,
    **kwargs,
):

    # Calculate indicators
    col_c30_RAI = f"RAI c30 {year} {var_label}"
    col_c80_RAI = f"RAI c80 {year} {var_label}"
    col_c30_cprice = f"Carbon price c30 {year}"
    col_c80_cprice = f"Carbon price c80 {year}"

    # Create figure
    fig_RAI = make_subplots(
        1,
        2,
        horizontal_spacing=0.02,
        column_widths=[0.4, 0.6],
        subplot_titles=(
            "<b>a.</b> Carbon price vs RAI<br> ",
            "<b>b.</b> RAI per model<br> ",
        ),
    )
    col_RAI_vs_cprice = 1
    col_RAI = 2

    ##############
    # 1a: RAI vs cprice for c30 and c80
    ##############

    curr_cols = [col_c30_RAI, col_c80_RAI, col_c30_cprice, col_c80_cprice]

    for is_newest, selection in meta[~meta[curr_cols].isna().any(axis=1)].groupby(
        "Newest"
    ):
        for i, (model, info) in enumerate(selection.iterrows()):
            stripped_model = info["Stripped model"]

            if stripped_model not in models.index:
                # Ignore entries that are not in `models`
                continue

            color = models.loc[stripped_model, "Color"] if is_newest else "#DDD"
            label = info["Stripped model"] if is_newest else "Older model version"
            dash = "solid"

            fig_RAI.add_scatter(
                x=[0, info[col_c30_RAI], info[col_c80_RAI]],
                # y=[0, info[col_c30_cprice], info[col_c80_cprice]],
                # Hardcoded carbon price:
                y=[0, 48.86, 130.31],
                line={"color": color, "dash": dash},
                mode="lines",
                name=label,
                legendgroup=label,
                showlegend=False,
                row=1,
                col=col_RAI_vs_cprice,
            )

    ##############
    # 1b: RAI based on c80
    ##############

    add_model_comparison(
        fig_RAI,
        meta,
        models,
        col_RAI,
        col_c80_RAI,
        narrative_left=narrative_left,
        narrative_right=narrative_right,
        **kwargs,
    )

    # Update layout

    (
        fig_RAI.update_xaxes(
            title=f"Relative Abatement Index in {year}",
            gridcolor=GRIDCOLOR,
            tickvals=np.arange(0, 2, 0.2),
            zeroline=True,
            title_standoff=40,
        )
        .update_xaxes(col=col_RAI, range=xrange)
        .update_yaxes(
            col=col_RAI_vs_cprice,
            title=f"Carbon price in {year} (2010$/tCO<sub>2</sub>)",
        )
        .update_layout(
            width=860,
            height=400,
            margin={"l": 60, "r": 30, "t": 50, "b": 70},
            hovermode="closest",
        )
    )
    return fig_RAI
