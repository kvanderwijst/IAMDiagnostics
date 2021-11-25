"""
Contains functions for basic data manipulation
"""

import numpy as np


def get(data, scenario, variable, year=None):
    selection = data[
        (data["Scenario"] == scenario) & (data["Variable"] == variable)
    ].set_index("Model")
    if year is None:
        return selection.loc[:, "2010":]
    else:
        return selection[year]


def set_value_from_var_column(data, meta, metacol, col, year, scenario):
    """
    Adds a column to the meta df using the `data` df. Which variable to use
    is taken from a `metacol` column in the meta df. For example, the GDP
    metric is sometimes GDP|PPP and sometimes GDP|MER, depending on the model.
    
    In this example, metacol would be 'GDP_metric'.
    """
    meta[col] = np.nan
    for model, info in meta.iterrows():
        var = info[metacol]
        selection = data[
            (data["Variable"] == var)
            & (data["Model"] == model)
            & (data["Scenario"] == scenario)
        ]
        if len(selection) > 0:
            meta.loc[model, col] = selection.iloc[0][year]
