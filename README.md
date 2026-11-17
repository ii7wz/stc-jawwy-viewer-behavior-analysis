# stc Jawwy TV: Viewer Behavior Analysis (HD vs SD)

Analysis of viewing behavior on the Jawwy TV platform, completed as part of a virtual job experience program with stc. This repository covers **Task 1: studying the HD flag** (high definition vs standard definition viewing).

The dataset belongs to stc and is **not included** in this repository. Set `DATA_PATH` in the script to your own local copy to reproduce the results.

## Question
Does streaming quality (HD vs SD) relate to how people watch: which content, how long, and which kind of users?

## Tools
Python, Pandas, NumPy, SciPy, Plotly (the `.xlsb` file is read with `pyxlsb`).

## Method
1. Loaded the Excel binary (`.xlsb`) data and inspected it (`shape`, `head`, `describe`, null checks).
2. Cleaned the data: dropped an unused column, trimmed program names, converted Excel serial dates to real dates, and fixed column types.
3. Ranked programs by total watch hours (series episodes kept separate by season and episode).
4. Compared behavior by program class (movies vs series).
5. Compared HD vs SD: views, users, total hours, average minutes per session, and HD share per program class and genre.
6. Segmented users by HD ratio: HD (80% or more HD views), SD (20% or less), Mixed.
7. Checked HD share by weekday.
8. Tested whether the session-length difference is real using a Welch t-test on random samples of 10,000 sessions per group.

## Findings
- 61.4% of views were SD and 38.6% HD.
- SD sessions were longer: average 25 min vs 13.4 min for HD. Total watch time was about 268K hours (SD) vs 90K hours (HD). The difference is statistically significant (p < 0.001).
- Movies were mostly watched in HD (67.9%); series mostly in SD (86.9%).
- HD share was highest in Documentary, Biography and Crime, and lowest in Drama, Horror and Animation.
- 6,235 users watched mostly in HD, 1,619 mostly in SD, and 3,724 were mixed. Mostly-SD users were the heaviest viewers.

## Recommendation
Improve HD availability for series, since they drive most of the watch time but are mostly streamed in SD.

## Limitations
- The results show association, not causation. Series tend to be both longer and more often in SD, so quality alone does not explain session length.
- The t-test used samples of 10,000 sessions per group, not the full dataset.
- Only Task 1 is covered here.

## Files
- `jawwy_hd_sd_analysis.py`: the full analysis script.
