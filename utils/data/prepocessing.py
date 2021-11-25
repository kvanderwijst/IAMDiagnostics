"""
General functions to import data and perform basic pre-processing
"""

from typing import Optional
import numpy as np
import pandas as pd


def import_data(data_filename: str, manual_model_renames: Optional[dict] = None):
    data = _prepare_data(
        data_filename,
        sep=";",
        onlyworld=False,
        manual_model_renames=manual_model_renames,
    )

    # Check for different regions
    if len(data["Region"].unique()) > 1:
        print("Careful, more than 1 region present:")
        print(dict(data.groupby("Region").count().iloc[:, 0]))

    # Check for problems:
    double_check = data.groupby(["Name", "Variable"]).count()["2050"]
    problems = double_check[double_check > 1].reset_index().groupby(["Name"]).count()
    if len(problems) > 0:
        print(problems["Variable"].rename("# duplicated variables").to_frame())

    # Transform Kt to Mt CO2/yr
    data.loc[data["Unit"] == "Kt", "2010":] /= 1000
    data.loc[data["Unit"] == "Kt", "Unit"] = "Mt CO2/yr"

    # Remove duplicate pairs of name-variable
    data = pd.concat(
        [
            data[~data["Name"].isin(problems.index)],
            data[data["Name"].isin(problems.index)]
            .groupby(["Name", "Variable"])
            .first()
            .reset_index(),
        ],
        sort=False,
    )

    # Add missing 5 year timesteps
    _interpolate_missing_5years(data)

    return data


def _prepare_data(
    database, startyear=2010, dt=10, onlyworld=True, manual_model_renames=None, **kwargs
):
    data_raw = pd.read_csv(database, **kwargs)

    # Choose only decadal data
    data = data_raw.loc[
        :,
        ["Model", "Scenario", "Region", "Variable", "Unit"]
        + [str(y) for y in np.arange(startyear, 2101, dt)],
    ]

    # Choose only region == World
    if onlyworld:
        data = data[data["Region"] == "World"]

    # Set all scenario names to lowercase
    data["Scenario"] = data["Scenario"].str.lower()

    # Manually rename a few models to match version file
    if manual_model_renames is not None:
        data["Model"] = data["Model"].replace(manual_model_renames)

    # Add column Name, equal to Model + Scenario
    data.insert(2, "Name", data["Model"] + " " + data["Scenario"])

    return data


def _interpolate_missing_5years(data: pd.DataFrame):
    col_2010 = list(data.columns).index("2010")
    for i, year in enumerate(range(2015, 2105, 10)):
        data.insert(
            col_2010 + 2 * i + 1,
            str(year),
            data[[str(year - 5), str(year + 5)]].mean(axis=1),
        )

