import numpy as np

from utils.data.handling import set_value_from_var_column


def create_columns(
    data,
    prev_meta,
    years=["2050", "2100"],
    cprices=[130.3, 1441.3],
    policy_scenario="diag-c80-gr5",
    mute=False,
):

    meta = prev_meta.copy()
    created_columns = []

    ## Calculate policy cost for each model
    for year, cprice in zip(years, cprices):
        col_costs = f"Policy cost {year}"
        col_emiss = f"Emissions CAV {year}"
        col_emiss_base = f"{col_emiss} base"
        set_value_from_var_column(
            data, meta, "Policy cost variable", col_costs, year, policy_scenario
        )
        set_value_from_var_column(
            data, meta, "Emissions_for_CAV", col_emiss, year, policy_scenario
        )
        set_value_from_var_column(
            data, meta, "Emissions_for_CAV", col_emiss_base, year, "diag-base"
        )

        # Make all costs positive
        meta[col_costs] = meta[col_costs].abs()

        # Cost per GDP
        col_per_GDP = f"{col_costs} per GDP"

        GDP_column = f"GDP {year} {policy_scenario}"
        # Check if GDP column already exists
        if GDP_column not in meta.columns:
            set_value_from_var_column(
                data, meta, "GDP_metric", GDP_column, year, policy_scenario
            )

        meta[col_per_GDP] = meta[col_costs] / meta[GDP_column]

        # Using this information, calculate CAV
        col_CAV = f"CAV {year}"
        GHG_reduction_absolute = (
            meta[col_emiss_base] - meta[col_emiss]
        ) / 1000  # Convert Mt to Gt
        # cprice = meta[f'Carbon price c80 {year}'] ## Use hardcoded c-price
        meta[col_CAV] = meta[col_costs] / (GHG_reduction_absolute * cprice)

        # CAV < 0 or CAV > 2.5 is a mistake, exclude those
        meta.loc[
            ~meta[col_CAV].between(0, 2.5)
            | (meta[col_per_GDP] > 0.15)
            | (meta[col_costs] > 50000),
            [col_costs, col_per_GDP, col_CAV, col_per_GDP],
        ] = np.nan

        created_columns += [col_costs, col_emiss, col_emiss_base, col_per_GDP, col_CAV]

    if not mute:
        print(f"Created columns: {created_columns}\n")

    return meta
