import numpy as np
from utils.data.handling import get


def calc_relative_abatement_index(
    data, year, var, pol="diag-c80-gr5", base="diag-base",
):

    # Get CO2 FFI Base and Pol
    CO2_FFI_base = get(data, base, var, year)
    CO2_FFI_pol = get(data, pol, var, year)

    return (CO2_FFI_base - CO2_FFI_pol) / CO2_FFI_base


def create_columns(
    data,
    meta,
    years=["2050", "2100"],
    vars={
        "Emissions|CO2|Energy and Industrial Processes": "CO2 FFI",
        "Emissions|Kyoto Gases": "Kyoto",
    },
    mute=False,
):

    new_meta = meta.copy()

    created_columns = []

    for var_name, var_label in vars.items():

        for year in years:
            # Calculate indicators
            col_c30_RAI = f"RAI c30 {year} {var_label}"
            col_c80_RAI = f"RAI c80 {year} {var_label}"
            col_c30_cprice = f"Carbon price c30 {year}"
            col_c80_cprice = f"Carbon price c80 {year}"

            new_meta[col_c30_RAI] = calc_relative_abatement_index(
                data, year, var_name, pol="diag-c30-gr5"
            )
            new_meta[col_c80_RAI] = calc_relative_abatement_index(
                data, year, var_name, pol="diag-c80-gr5"
            )
            new_meta[col_c30_cprice] = get(data, "diag-c30-gr5", "Price|Carbon", year)
            new_meta[col_c80_cprice] = get(data, "diag-c80-gr5", "Price|Carbon", year)
            new_meta.loc[new_meta[col_c30_cprice] == 0, col_c30_cprice] = np.nan
            new_meta.loc[new_meta[col_c80_cprice] == 0, col_c80_cprice] = np.nan

            created_columns += [
                col_c30_RAI,
                col_c80_RAI,
                col_c30_cprice,
                col_c80_cprice,
            ]

    if not mute:
        print(f"Created columns: {created_columns}\n")

    return new_meta
