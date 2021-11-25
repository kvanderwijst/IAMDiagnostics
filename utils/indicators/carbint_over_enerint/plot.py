import numpy as np
from plotly.subplots import make_subplots
from utils.plot.general import confidence_ellipse, add_model_comparison, GRIDCOLOR


def create_fig(meta, models, year: str, xrange=None, **kwargs):

    fig_CoEI = make_subplots(
        1,
        2,
        horizontal_spacing=0.02,
        column_widths=[0.4, 0.6],
        subplot_titles=(
            "<b>a.</b> Energy Intensity vs Carbon Intensity<br> ",
            f"<b>b.</b> ERT per model ({year})<br> ",
        ),
    )

    col_CI_2050 = "Carbon intensity 2050"
    col_CI_2100 = "Carbon intensity 2100"
    col_EI_2050 = "Energy intensity 2050"
    col_EI_2100 = "Energy intensity 2100"

    ##############
    # 2a: CI vs EI scatter for C80-gr5 (2050 and 2100)
    ##############

    # Add background shape for 2050 and 2100
    for col_CI, col_EI, col_year in [
        (col_CI_2050, col_EI_2050, 2050),
        (col_CI_2100, col_EI_2100, 2100),
    ]:
        selection = meta[~meta[[col_CI, col_EI]].isna().any(axis=1)]
        x_ellipse, y_ellipse = confidence_ellipse(
            selection[col_CI], selection[col_EI], 2
        )
        fig_CoEI.add_scatter(
            x=x_ellipse,
            y=y_ellipse,
            fill="toself",
            showlegend=False,
            fillcolor="rgba(0,0,0,.08)",
            line_width=0,
        )
        fig_CoEI.add_annotation(
            text=col_year,
            x=max(x_ellipse),
            y=min(y_ellipse),
            font_color="#999",
            showarrow=False,
        )

    # Create connected dots for 2050 and 2100 values
    for is_newest, selection in meta.groupby("Newest"):
        for model, info in selection.iterrows():
            stripped_model = info["Stripped model"]

            if stripped_model not in models.index:
                # Ignore entries that are not in `models`
                continue

            color = models.loc[stripped_model, "Color"] if is_newest else "#BBB"

            fig_CoEI.add_scatter(
                x=info[[col_CI_2050, col_CI_2100]],
                y=info[[col_EI_2050, col_EI_2100]],
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
    # 2b: CoEI
    ##############

    add_model_comparison(
        fig_CoEI,
        meta,
        models,
        2,
        f"CoEI {year}",
        narrative_left="More via demand red.",
        narrative_right="More via decarbon.",
        labelshift=1.2,
        **kwargs,
    )

    fig_CoEI.add_scatter(
        x=[0, 0.4490],
        y=[0, 0.4490],
        showlegend=False,
        mode="lines",
        line={"dash": "dot", "color": "#DDD"},
    ).add_annotation(
        x=0.35,
        y=0.35,
        showarrow=False,
        textangle=-75,
        text="Demand red. dominant",
        xshift=-12,
        font_color="#888",
    ).add_annotation(
        x=0.35,
        y=0.35,
        showarrow=False,
        textangle=-75,
        text="Decarb. dominant",
        xshift=10,
        font_color="#888",
    )

    # Update layout
    (
        fig_CoEI.update_xaxes(
            col=1,
            gridcolor=GRIDCOLOR,
            title="Carbon intensity (red. from baseline)",
            title_standoff=40,
        )
        .update_yaxes(
            col=1,
            gridcolor=GRIDCOLOR,
            title="Energy intensity (red. from baseline)",
            range=[-0.0113, 0.4490],
        )
        .update_xaxes(
            col=2,
            tickvals=np.arange(0.5, 0.901, 0.1),
            range=xrange,
            title="CI over (EI+CI) (red. from baseline)",
            title_standoff=40,
        )
        .update_layout(
            width=860,
            height=400,
            margin={"l": 60, "r": 30, "t": 50, "b": 70},
            hovermode="closest",
        )
    )

    return fig_CoEI
