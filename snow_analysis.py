import pandas as pd


# The first four NOAA description rows have fewer columns than the data,
# so header=None and names=range(37) are needed to read the entire file first.
df_2022 = pd.read_csv("2022.csv", header=None, names=range(37))
df_2023 = pd.read_csv("2023.csv", header=None, names=range(37))
df_2024 = pd.read_csv("2024.csv", header=None, names=range(37))
df_2025 = pd.read_csv("2025.csv", header=None, names=range(37))

df_2022 = df_2022[4:]
df_2023 = df_2023[4:]
df_2024 = df_2024[4:]
df_2025 = df_2025[4:]

df_2022.columns = df_2022.iloc[0]
df_2023.columns = df_2023.iloc[0]
df_2024.columns = df_2024.iloc[0]
df_2025.columns = df_2025.iloc[0]

df_2022 = df_2022[1:].reset_index(drop=True)
df_2023 = df_2023[1:].reset_index(drop=True)
df_2024 = df_2024[1:].reset_index(drop=True)
df_2025 = df_2025[1:].reset_index(drop=True)

day_columns = [
    "Nov 11",
    "Nov 12",
    "Nov 13",
    "Nov 14",
    "Nov 15",
    "Nov 16",
    "Nov 17",
    "Nov 18",
]

columns_to_keep = ["Station Name", "County"] + day_columns

df_2022 = df_2022[columns_to_keep].copy()
df_2023 = df_2023[columns_to_keep].copy()
df_2024 = df_2024[columns_to_keep].copy()
df_2025 = df_2025[columns_to_keep].copy()

dataframes = {
    2022: df_2022,
    2023: df_2023,
    2024: df_2024,
    2025: df_2025,
}

yearly_data = []

for year, df in dataframes.items():
    df = df.rename(columns={"Station Name": "Station"})

    # T means a trace amount, so it is changed to 0. M is missing data, so it
    # is filled with the county median because stations in one county are nearby.
    # If a county has no data, the statewide median and then 0 are used so the values can be summed.
    df[day_columns] = (
        df[day_columns]
        .replace({"T": 0, "M": pd.NA})
        .apply(pd.to_numeric, errors="coerce")
    )

    for column in day_columns:
        county_median = df.groupby("County")[column].transform("median")
        df[column] = df[column].fillna(county_median)

        df[column] = df[column].fillna(df[column].median())

        df[column] = df[column].fillna(0)

    df = df.set_index(["County", "Station"])

    df.columns = [
        [year, year, year, year, year, year, year, year],
        [11, 12, 13, 14, 15, 16, 17, 18],
    ]
    df.columns.names = ["Year", "Day"]

    yearly_data.append(df)

merged_df = yearly_data[0]

for df in yearly_data[1:]:
    merged_df = pd.merge(
        merged_df,
        df,
        on=["County", "Station"],
        how="inner",
    )

merged_df = merged_df.sort_index()

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

print(merged_df)
