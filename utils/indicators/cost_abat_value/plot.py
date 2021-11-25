import numpy as np
from plotly.subplots import make_subplots
from utils.plot.general import add_model_comparison, confidence_ellipse, GRIDCOLOR


def create_fig(meta, models, year: str, xrange=None, **kwargs):
    fig_CAV = make_subplots(
        1,
        2,
        horizontal_spacing=0.02,
        column_widths=[0.4, 0.6],
        subplot_titles=(
            "<b>a.</b> Costs vs abatement<br> ",
            f"<b>b.</b> CAV per model ({year})<br> ",
        ),
    )

    ##############
    # 5a:
    ##############

    cols_x = ["Policy cost 2050 per GDP", "Policy cost 2100 per GDP"]
    cols_y = ["RAI c80 2050 CO2 FFI", "RAI c80 2100 CO2 FFI"]

    # Add background shape for 2050 and 2100
    for col_x, col_y, col_year in [
        (cols_x[0], cols_y[0], 2050),
        (cols_x[1], cols_y[1], 2100),
    ]:
        selection = meta[~meta[[col_x, col_y]].isna().any(axis=1)]
        x_ellipse, y_ellipse = confidence_ellipse(selection[col_x], selection[col_y], 2)
        fig_CAV.add_scatter(
            x=x_ellipse,
            y=y_ellipse,
            fill="toself",
            showlegend=False,
            fillcolor="rgba(0,0,0,.08)",
            line_width=0,
        )
        fig_CAV.add_annotation(
            text=col_year,
            x=max(x_ellipse),
            y=max(y_ellipse) if col_year == 2100 else min(y_ellipse),
            font_color="#999",
            showarrow=False,
        )

    for is_newest, selection in meta[~meta[cols_x + cols_y].isna().any(axis=1)].groupby(
        "Newest"
    ):
        for model, info in selection.iterrows():
            stripped_model = info["Stripped model"]

            if stripped_model not in models.index:
                # Ignore entries that are not in `models`
                continue

            color = models.loc[stripped_model, "Color"] if is_newest else "#BBB"

            fig_CAV.add_scatter(
                x=info[cols_x],
                y=info[cols_y],
                marker={
                    "color": [color, "#FFF"],
                    "size": 8,
                    "line": {"color": color, "width": 2},
                },
                line={"color": color, "width": 1, "dash": "solid"},
                mode="markers+lines",
                name=stripped_model,
                showlegend=False,
            )

    ##############
    # 5b: CAV
    ##############

    add_model_comparison(
        fig_CAV,
        meta,
        models,
        2,
        f"CAV {year}",
        narrative_left="Less expensive",
        narrative_right="More expensive",
        **kwargs,
    )

    # Update layout
    (
        fig_CAV.update_xaxes(
            col=1,
            gridcolor=GRIDCOLOR,
            title="Policy cost (% of GDP)",
            rangemode="tozero",
            tickformat=".0%",
        )
        .update_yaxes(
            col=1,
            gridcolor=GRIDCOLOR,
            title="Rel. abatement index",
            title_standoff=40,
            rangemode="tozero",
        )
        .update_xaxes(
            col=2,
            tickvals=np.arange(0, 1.81, 0.4),
            title="CAV",
            range=xrange,
            # title='CI over EI (rel. to baseline)',
            title_standoff=40,
        )
        .update_layout(
            width=860,
            height=400,
            margin={"l": 60, "r": 30, "t": 50, "b": 70},
            hovermode="closest",
        )
    )
    return fig_CAV
