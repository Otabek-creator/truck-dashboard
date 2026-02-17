# 📊 KPI Dashboard

Interactive operational dashboard built with **Streamlit**, **Pandas**, and **Altair**.

## Features

| Section | Visualization | Data Source |
|---------|--------------|-------------|
| KPI Cards | 6 metric cards | Multiple sheets |
| Fleet & Trailers | Vertical bar charts | `data_fleet`, `data_trailers` |
| Maintenance | Data table + horizontal bar | `data_pmservice`, `Data_Oper` |
| Safety & Accidents | Bar charts | `data_safety`, `data_accidents` |
| Claims & Dispatch | Bar + stacked bar | `data_claims`, `data_load` |
| Hiring | Bar + area trend | `data_hiring` |

## Quick Start

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Deployment (Streamlit Cloud)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Select this repo → set **Main file** to `dashboard.py`
4. Deploy 🚀

## Data

All data is sourced from `KPI BOARD.xlsx` (11 of 16 sheets used).  
See [DATA_SOURCES.md](DATA_SOURCES.md) for a detailed mapping of every component to its source sheet.

## Tech Stack

- **Streamlit** — UI framework
- **Pandas** — data wrangling
- **Altair** — declarative charts
- **openpyxl** — Excel reader
