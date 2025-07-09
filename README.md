# Nepal Cricket Database Project 🏏

A comprehensive database system for analyzing Nepal's ODI cricket matches with PostgreSQL backend and Python analytics. This project contains match data for Nepal's international ODI matches, providing ball-by-ball analysis and statistics.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Setup PostgreSQL Database

#### Install PostgreSQL (macOS)

```bash
brew install postgresql
brew services start postgresql
```

#### Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE cricket_nepal;
CREATE USER cricket_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cricket_nepal TO cricket_user;
\q
```

### 3. Configure Environment

```bash
# Run the setup script
python setup.py
```

This will:

- Install Python dependencies
- Create `.env` file for database configuration
- Test database connection
- Create database tables

### 4. Process Nepal ODI Data

```bash
# Process all Nepal ODI JSON files into database
python code/process_nepal_odi.py
```

This will import all Nepal ODI match data (72+ matches) into your database with ball-by-ball details.

## 📊 Database Schema

### Tables

#### `cricket_matches`

- Nepal match metadata (teams, venue, toss, result)
- One record per Nepal ODI match

#### `cricket_deliveries`

- Ball-by-ball delivery data for Nepal matches
- Runs, wickets, extras, players
- Links to match via `match_id`

### Key Columns

- `match_id`: Unique identifier from JSON filename
- `innings_number`: 0 (first innings) or 1 (second innings)
- `overs`, `balls`: Ball identification (1.1, 1.2, etc.)
- `is_wicket`: Binary flag (0/1) for wicket deliveries
- `runs_total`, `runs_batter`, `runs_extras`: Run breakdown

## 🔍 Usage Examples

### Basic Nepal Match Analysis

```python
from code.exploring_json_data_struct import extract_match_data

# Load single Nepal match
match = extract_match_data("data/Nepal/ODI/1154649.json")
innings_1 = match.convert_json_to_df(0)
innings_2 = match.convert_json_to_df(1)

# Quick scorecard
print(f"1st innings: {innings_1['runs.total'].sum()}/{innings_1['is_wicket'].sum()}")
print(f"2nd innings: {innings_2['runs.total'].sum()}/{innings_2['is_wicket'].sum()}")
```

### Database Queries for Nepal Players

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine("postgresql://cricket_user:password@localhost/cricket_nepal")

# Top Nepal run scorers
top_nepal_scorers = pd.read_sql("""
    SELECT batter, SUM(runs_batter) as total_runs, COUNT(*) as deliveries_faced
    FROM cricket_deliveries
    GROUP BY batter
    ORDER BY total_runs DESC
    LIMIT 10
""", engine)

# Nepal bowling figures
nepal_bowling_stats = pd.read_sql("""
    SELECT bowler,
           COUNT(*) as deliveries_bowled,
           SUM(runs_total) as runs_conceded,
           SUM(is_wicket) as wickets_taken
    FROM cricket_deliveries
    GROUP BY bowler
    ORDER BY wickets_taken DESC
""", engine)
```

## 📁 Project Structure

```
cricket_nepal/
├── code/
│   ├── exploring_json_data_struct.py  # JSON parsing class
│   ├── database_model.py              # SQLAlchemy models
│   ├── process_nepal_odi.py           # Batch data processor
│   └── EDA.py                         # Analysis examples
├── data/
│   └── Nepal/ODI/                     # Nepal ODI JSON match files (72+ matches)
├── setup.py                          # Setup script
├── pyproject.toml                    # uv dependencies
├── uv.lock                           # uv lock file
└── README.md                         # This file
```

## 🎯 Features

### Current

- ✅ Robust JSON parsing for Nepal cricket data with missing column handling
- ✅ PostgreSQL database with proper schema for Nepal matches
- ✅ Ball-by-ball delivery tracking for all Nepal ODI matches
- ✅ Wicket detection and classification
- ✅ Runs and extras breakdown
- ✅ Batch processing of all Nepal ODI matches (72+ matches)
- ✅ Cross-platform path handling

### Planned

- 🔄 Nepal player statistics dashboard
- 🔄 Over-by-over analysis for Nepal matches
- 🔄 Partnership tracking for Nepal players
- 🔄 Nepal match visualization
- 🔄 Ball-by-ball pitch maps for Nepal matches
- 🔄 DRS and umpire call analysis

## 🛠️ Development

### Adding New Features

1. Update database models in `database_model.py`
2. Modify JSON parsing in `exploring_json_data_struct.py`
3. Update batch processor in `process_nepal_odi.py`
4. Run migrations: `python setup.py`

### Database Migrations

The system automatically creates/updates tables on startup.

## 📈 Analytics Possibilities

With this Nepal cricket database, you can analyze:

- **Nepal Player Performance**: Runs, strike rates, partnerships
- **Bowling Analysis**: Economy rates, wicket patterns for Nepal bowlers
- **Match Patterns**: Nepal's winning trends, venue effects
- **Team Statistics**: Nepal vs opponents comparisons
- **Historical Trends**: Nepal's performance over time
- **Tournament Analysis**: Nepal's performance in different series/tournaments

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add your analysis or improvements
4. Submit pull request

---

Built with ❤️ for Nepal Cricket Analytics
