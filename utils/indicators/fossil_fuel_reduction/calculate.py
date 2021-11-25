from utils.data.handling import get

VARIABLES = [
    "Fossil|w/o CCS",
    "Fossil|w/ CCS",
    "Nuclear",
    "Biomass|w/o CCS",
    "Biomass|w/ CCS",
    "Non-Biomass Renewables",
]
LABELS = [
    "Fossil<br>w/o CCS",
    "Fossil<br>w. CCS",
    "Nuclear",
    "Biomass<br>w/o CCS",
    "Biomass<br>w. CCS",
    "Renewables",
]


def calc_fossil_fuel_reduction(
    data, year, pol, base="diag-base", var="Primary Energy|Fossil"
):

    prim_energy_fossil_2020 = get(data, base, var, "2020")
    prim_energy_fossil_pol = get(data, pol, var, year)

    return (prim_energy_fossil_2020 - prim_energy_fossil_pol) / prim_energy_fossil_2020


def create_columns(data, meta, years=["2050", "2100"], mute=False):

    policy_scenario = "diag-c80-gr5"
    new_meta = meta.copy()
    created_columns = []

    for year in years:

        ### First calculate fossil fuel energy values

        for var_suffix in VARIABLES:
            var = f"Primary Energy|{var_suffix}"
            col = f"{var} {year}"
            new_meta[col] = get(data, policy_scenario, var, year)
            created_columns += [col]

        # Replace w/o CCS variables by full variable if w/ CCS data is missing:
        for fuel in ["Fossil", "Biomass"]:
            var = f"Primary Energy|{fuel}"
            col = f"{var} {year}"
            new_meta[col] = get(data, policy_scenario, var, year)
            missing = new_meta[f"{var}|w/ CCS {year}"].isna()
            new_meta.loc[missing, f"{var}|w/o CCS {year}"] = new_meta.loc[missing, col]
            created_columns += [col]

        ### Then calculate fossil fuel reduction
        col_FFR = f"FFR {year}"
        new_meta[col_FFR] = calc_fossil_fuel_reduction(data, year, policy_scenario)
        created_columns += [col_FFR]

    if not mute:
        print(f"Created columns: {created_columns}\n")

    return new_meta

