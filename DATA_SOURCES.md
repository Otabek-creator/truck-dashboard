# 📊 Dashboard — Data Source Documentation

> Every metric, chart, and table in the dashboard is powered by a specific sheet  
> from the `KPI BOARD.xlsx` Excel workbook. This document maps each component  
> to its source sheet, columns used, and calculation logic.

---

## Row 1 — KPI Metric Cards

| # | Card | Sheet | Column(s) | Logic |
|---|------|-------|-----------|-------|
| 1 | **Active Trucks** | `data_fleet` | `FLEET STATUS` | Count rows where `FLEET STATUS == "Active"`. Total rows: 190 |
| 2 | **Total Trailers** | `data_trailers` | — | Total row count (211 trailers) |
| 3 | **Open Issues** | `OPERATIONS` | 1st & 2nd columns | Find row where col 0 = `"Open"`, read value from col 1 |
| 4 | **Open Claims** | `data_claims` | `STATUS` | Count rows where `STATUS == "Open"` |
| 5 | **Total Accidents** | `data_accidents` | — | Total row count (55 accidents) |
| 6 | **Employees** | `data_employees` | — | Total row count (99 employees) |

---

## Row 2 — Fleet & Trailer Status

### 🚛 Fleet Status (Donut Chart)
- **Sheet:** `data_fleet`
- **Column:** `FLEET STATUS`
- **Logic:** `value_counts()` on the `FLEET STATUS` column
- **Categories:** Active, Hometime, In Service, Need Driver, Need to tow, Not in use

### 📦 Trailer Status (Donut Chart)
- **Sheet:** `data_trailers`
- **Column:** `Status`
- **Logic:** `value_counts()` on the `Status` column
- **Categories:** Active, Dropped, Yard, Dropped loaded, Line Load, Total loss, Broken, LOT

---

## Row 3 — Operations & Maintenance

### 🔧 Urgent Maintenance (Table)
- **Sheet:** `data_pmservice`
- **Columns displayed:** `Truck Number`, `PM Mileage`, `Next PM`, `Left`, `STATUS`
- **Logic:** Filter rows where `Left < 0` (overdue PM), sort by `Left` ascending (most overdue first)
- **`Left` column:** Calculated as `Next PM mileage − Current mileage`. Negative = overdue.
- **`STATUS` values:** "Urgent oil change", "Oil change", "GOOD"

### ⚠️ Top Issue Categories (Horizontal Bar Chart)
- **Sheet:** `Data_Oper`
- **Column:** `Issue`
- **Logic:** `value_counts().head(7)` — top 7 most frequent issue types
- **Example issues:** trailer mud flap, truck's not starting, trailer tire, Coolant reservoir, etc.

---

## Row 4 — Safety & Accidents

### 🚦 Safety Violations (Horizontal Bar Chart)
- **Sheet:** `data_safety` *(header=row 1)*
- **Column:** `Violation`
- **Logic:** `value_counts().head(7)` — top 7 violation types
- **Example values:** CLEAN 3, CLEAN 2, VEHICLE, VE & UN, VE & LOG, UNSAFE, LOG

### 💥 Accident Vehicle Condition (Vertical Bar Chart)
- **Sheet:** `data_accidents`
- **Column:** `Truck Condition`
- **Logic:** `value_counts()` — count per condition category
- **Categories:** Repairable, No damage, Total loss

---

## Row 5 — Claims & Dispatch

### 📋 Claims by Type (Donut Chart)
- **Sheet:** `data_claims`
- **Column:** `Type of claim`
- **Logic:** `value_counts()` — distribution of claim types
- **Categories:** Physical Damage, Trailer Interchange, Liability: Not-At-Fault, Cargo Claim, Liability: At-Fault

### 🚚 Dispatch Status by Team (Stacked Bar Chart)
- **Sheet:** `data_load`
- **Columns:** `Team`, `Status - UPDATE TEAM`
- **Logic:** `groupby(["Team", "Status - UPDATE TEAM"]).size()` — count per team per status
- **Teams:** DOMINATORS, WEST COAST, WARRIORS, AVENGERS, MIDFORCE
- **Statuses:** COVERED, HOMETIME, DRIVER RESTING, EMPTY, REPAIR

---

## Row 6 — Hiring

### 👥 Driver Status (Vertical Bar Chart)
- **Sheet:** `data_hiring`
- **Column:** `Status`
- **Logic:** `value_counts()` — count per employment status
- **Categories:** Active, Terminated, Vacation

### 📈 Monthly Hiring Trend (Area Chart)
- **Sheet:** `data_hiring`
- **Column:** `Hired Date`
- **Logic:** Convert to datetime → extract month period → `groupby("Month").size()`
- **Visualization:** Smoothed area chart showing hiring volume over time

---

## Excluded Sheets (Not Used)

| Sheet | Reason |
|-------|--------|
| `MAIN_DASHBOARD` | Contains only text labels (no numeric data) |
| `HIRING` | Summary view; raw data already in `data_hiring` |
| `DAILY UPDATES` | Informational text (Birthday, Anniversary, etc.) |
| `DISPATCH` | Empty (0 rows, 0 columns) |
| `data_dispatch` | Empty (0 rows, 0 columns) |
