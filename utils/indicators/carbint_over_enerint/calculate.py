import numpy as np
from utils.data.handling import get, set_value_from_var_column


def calc_carbon_and_energy_intensity(data, meta, year, scenario):

    # For each model, get either GDP|PPP or GDP|MER (depending on column `GDP_metric`)
    GDP_column = f"GDP {year} {scenario}"
    set_value_from_var_column(data, meta, "GDP_metric", GDP_column, year, scenario)

    CO2_FFI = get(data, scenario, "Emissions|CO2|Energy and Industrial Processes", year)
    final_energy = get(data, scenario, "Final Energy", year)
    GDP_PPP = meta[GDP_column]

    carbon_intensity = CO2_FFI / final_energy
    energy_intensity = final_energy / GDP_PPP

    return carbon_intensity, energy_intensity


def calc_normalised_carbon_and_energy_intensity(data, meta, year):
    CI_pol, EI_pol = calc_carbon_and_energy_intensity(data, meta, year, "diag-c80-gr5")
    CI_baseline, EI_baseline = calc_carbon_and_energy_intensity(
        data, meta, year, "diag-base"
    )
    return CI_pol / CI_baseline, EI_pol / EI_baseline


def create_columns(data, meta, years=["2050", "2100"], mute=False):

    new_meta = meta.copy()

    created_columns = []

    for year in years:
        col_CI = f"Carbon intensity {year}"
        col_EI = f"Energy intensity {year}"
        col_CI_over_EI = f"CoEI {year}"

        (
            CI_over_baseline,
            EI_over_baseline,
        ) = calc_normalised_carbon_and_energy_intensity(data, meta, year)

        new_meta[col_CI], new_meta[col_EI] = 1 - CI_over_baseline, 1 - EI_over_baseline
        new_meta[col_CI_over_EI] = (1 - CI_over_baseline) / (
            1 - CI_over_baseline + 1 - EI_over_baseline
        )
        created_columns += [col_CI, col_EI, col_CI_over_EI]

    if not mute:
        print(f"Created columns: {created_columns}\n")

    return new_meta

