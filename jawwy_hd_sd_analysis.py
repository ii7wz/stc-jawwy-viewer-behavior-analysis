"""
stc Jawwy TV - Viewer Behavior Analysis (Task 1: HD vs SD)

Virtual job experience. The dataset belongs to stc and is NOT included in this repository.
Set DATA_PATH to your local copy of the .xlsb file before running.
"""
import numpy as np
import pandas as pd
import plotly.express as px
from scipy import stats

DATA_PATH = "stc TV Data Set_T1.xlsb"  # place the dataset here (not included)

# ---------------------------------------------------------------------------
# 1. Load the data (xlsb requires the pyxlsb engine)
# ---------------------------------------------------------------------------
dataframe = pd.read_excel(DATA_PATH, sheet_name="Final_Dataset", engine="pyxlsb")
print(dataframe.shape)
print(dataframe.head())

# ---------------------------------------------------------------------------
# 2. Cleaning and type conversion
# ---------------------------------------------------------------------------
dataframe = dataframe.drop(columns=["Column1"])
dataframe["program_name"] = dataframe["program_name"].str.strip()
# Excel serial date -> real datetime
dataframe["date_"] = pd.to_datetime("1899-12-30") + pd.to_timedelta(
    dataframe["date_"].astype(float), unit="D"
)
num_cols = ["duration_seconds", "season", "episode", "series_title", "hd"]
str_cols = ["user_id_maped", "program_name", "program_class",
            "program_desc", "program_genre", "original_name"]
dataframe[num_cols] = dataframe[num_cols].apply(pd.to_numeric)
dataframe[str_cols] = dataframe[str_cols].astype(str)

print(dataframe.describe())
print(dataframe.isnull().any())

# ---------------------------------------------------------------------------
# 3. Most watched programs (episodes of a series are kept separate)
# ---------------------------------------------------------------------------
df = dataframe.copy()
grouped = df.copy()
is_series = grouped["program_class"] == "SERIES/EPISODES"
grouped.loc[is_series, "program_name"] = (
    grouped["program_name"] + "_SE" + grouped["season"].astype(str)
    + "_EP" + grouped["episode"].astype(str)
)
grouped = (
    grouped.groupby(["program_name", "program_class"])
    .agg(users=("user_id_maped", "nunique"),
         watches=("user_id_maped", "count"),
         seconds=("duration_seconds", "sum"))
    .reset_index()
)
grouped["watch_hours"] = grouped["seconds"] / 3600
grouped = grouped.drop(columns=["seconds"]).sort_values(
    ["watch_hours", "watches", "users"], ascending=False
).reset_index(drop=True)
print(grouped.head(35))
px.pie(grouped.head(10), values="watch_hours", names="program_name",
       hover_data=["program_class"],
       title="Top 10 programs by total watch hours").show()

# ---------------------------------------------------------------------------
# 4. Behavior by program class
# ---------------------------------------------------------------------------
by_class = (
    df.groupby("program_class")
    .agg(users=("user_id_maped", "nunique"),
         watches=("user_id_maped", "count"),
         seconds=("duration_seconds", "sum"))
    .reset_index()
)
by_class["watch_hours"] = by_class["seconds"] / 3600
px.pie(by_class, values="watch_hours", names="program_class",
       title="Total watch hours by program class").show()
px.pie(by_class, values="users", names="program_class",
       title="Users by program class").show()

# ---------------------------------------------------------------------------
# 5. HD vs SD
# ---------------------------------------------------------------------------
print(df["hd"].value_counts())
print((df["hd"].value_counts(normalize=True) * 100).round(1))

hd_summary = df.groupby("hd").agg(
    users=("user_id_maped", "nunique"),
    watches=("user_id_maped", "count"),
    total_hours=("duration_seconds", lambda x: x.sum() / 3600),
    avg_minutes=("duration_seconds", lambda x: x.mean() / 60),
).reset_index()
hd_summary["hd"] = hd_summary["hd"].map({1: "HD", 0: "SD"})
print(hd_summary)

# HD / SD share inside each program class
ct = pd.crosstab(df["program_class"], df["hd"], normalize="index") * 100
ct.columns = ["SD" if c == 0 else "HD" for c in ct.columns]
print(ct.round(1))
px.bar(ct.reset_index().melt(id_vars="program_class"),
       x="program_class", y="value", color="variable", barmode="stack",
       title="HD vs SD share by program class").show()

# HD share by genre (ignore genres with <= 1000 watches)
g = df.groupby("program_genre").agg(hd_pct=("hd", "mean"), watches=("hd", "count"))
g = g[g["watches"] > 1000]
g["hd_pct"] = (g["hd_pct"] * 100).round(1)
print(g.sort_values("hd_pct", ascending=False).head(10))

# ---------------------------------------------------------------------------
# 6. User segments by HD ratio
# ---------------------------------------------------------------------------
user_hd = df.groupby("user_id_maped").agg(
    hd_ratio=("hd", "mean"),
    total_hours=("duration_seconds", lambda x: x.sum() / 3600),
    watches=("hd", "count"),
).reset_index()


def segment(ratio):
    if ratio >= 0.8:
        return "HD"
    if ratio <= 0.2:
        return "SD"
    return "Mixed"


user_hd["segment"] = user_hd["hd_ratio"].apply(segment)
print(user_hd["segment"].value_counts())
print(user_hd.groupby("segment")[["total_hours", "watches"]].mean().round(2))

# ---------------------------------------------------------------------------
# 7. HD share by weekday
# ---------------------------------------------------------------------------
df["weekday"] = df["date_"].dt.day_name()
wk = (df.groupby("weekday")["hd"].mean() * 100).round(1).reset_index()
px.bar(wk, x="weekday", y="hd", title="HD share by weekday").show()

# ---------------------------------------------------------------------------
# 8. Is the session-length difference real? (Welch t-test on 10,000-row samples)
# ---------------------------------------------------------------------------
hd_dur = df[df["hd"] == 1]["duration_seconds"].sample(10000, random_state=1)
sd_dur = df[df["hd"] == 0]["duration_seconds"].sample(10000, random_state=1)
t, p = stats.ttest_ind(hd_dur, sd_dur, equal_var=False)
print("p-value =", p)

# Findings (from the notebook notes)
# 1. 61.4% of views are SD and 38.6% are HD.
# 2. SD sessions are longer (avg 25 min vs 13.4 min for HD); 268K watch hours (SD) vs 90K (HD); p < 0.001.
# 3. Movies are mostly watched in HD (67.9%), series mostly in SD (86.9%).
# 4. HD is highest in Documentary, Biography and Crime; lowest in Drama, Horror and Animation.
# 5. 6,235 users mostly HD, 1,619 mostly SD, 3,724 mixed.
# Recommendation: improve HD availability for series.
