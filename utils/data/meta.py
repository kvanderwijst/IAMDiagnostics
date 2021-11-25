"""
Create the meta dataframe

Contains for each model+version some meta information
(which metrics to use, etc). More columns are added for
each indicators value.
"""

import pandas as pd
from ..constants import COLORS_PBL


def create_meta_df(data: pd.DataFrame, model_versions_filename: str):
    # Model versions and types
    versions = pd.read_excel(model_versions_filename)

    meta = versions.rename(
        columns={
            "Model_versionname": "Model",
            "Model_name": "Stripped model",
            "Age (1 = newest)": "Age",
        }
    ).set_index("Model")
    meta["Newest"] = meta["Age"] == 1

    # Check if all models from `data` are in `meta`:
    in_meta = set(meta.index)
    in_data = set(data["Model"].unique())
    if len(in_meta - in_data):
        print("In meta, but not in data:", in_meta - in_data)
    if len(in_data - in_meta):
        print("In data, but not in meta:", in_data - in_meta)

    # Only keep those models which are present in the data
    meta = meta[meta.index.isin(data["Model"])]

    return meta


def create_model_df(meta: pd.DataFrame):  # TODO: Move to plotting
    """
    The models dataframe is used for plotting.
    It contains one row per model (not for each version)
    and has an associated color for consistency between
    the plots.
    """

    models = (
        meta.reset_index()
        .groupby(["Type", "Stripped model"])
        .first()["Model"]
        .reset_index()
        .rename(columns={"Model": "Full model"})
    )

    # all_colors = ['#0c2c84', '#225ea8', '#1d91c0', '#41b6c4', '#7fcdbb', '#c7e9b4'] + ['#86469c', '#bc7fcd', '#fbcfe8', '#ed66b2'] +['#FF7F0E','#FBE426']+['rgb(248, 156, 116)', '#D62728', '#AF0033', '#E48F72'] + COLORS_PBL
    all_colors = [
        COLORS_PBL[j] if type(j) == int else j
        for j in [
            11,
            "#bc7fcd",
            2,
            6,
            4,
            15,
            0,
            5,
            13,
            7,
            1,
            "#BCBD22",
            12,
            8,
            10,
            3,
            14,
        ]
    ]

    models["i"] = models.index
    models["Color"] = [all_colors[i] for i in models["i"]]

    models = models.set_index("Stripped model")

    return models
