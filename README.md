# master-thesis

This repository simulates fleets of flex-offers and aggregated flex-offers across day-ahead, reserve, and activation markets, then summarizes performance metrics.

## Environment setup
1. Create/activate a Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Data prerequisites
- **Location:** By default, market and SmartCharging CSVs are loaded from `../SmartCharging_2020_to_2032` (see `config.DATA_FILEPATH`). Adjust this path in `config.py` if you store data elsewhere.
- **Files needed:**
  - SmartCharging simulation outputs: `Household data.csv` and `EV Models.csv`.
  - Market data (hourly) for the chosen resolution: `ElspotPrices.csv`, `mFRR.csv`, and `Regulating.csv`.
  - 15-minute variants (`ElspotPrices_15min.csv`, `mFRR_15min.csv`, `Regulating_15min.csv`) if you switch to 15-minute resolution.
- **Resolution alignment:** Set `TIME_RESOLUTION = 3600` for hourly data or `TIME_RESOLUTION = 900` for 15-minute data; the loader automatically picks the matching CSVs.
- **Relative paths:** All data paths are resolved relative to the repository root, so `../SmartCharging_2020_to_2032/Household data.csv` should exist when running scripts from the repo root.

## Configuration reference (`config.py`)
Key toggles you can adjust before running simulations:

- **Simulation scope:**
  - `NUM_EVS`, `NUM_CLUSTERS`, `SIMULATION_DAYS`, and `SIMULATION_START_DATE` set the fleet size, cluster count, and horizon.
  - `USE_SYNTHETIC` selects between synthetic SmartCharging data and external datasets.
  - `TYPE`: `"FO"` for flex-offers or `"DFO"` for dynamic flex-offers.
- **Market switches:**
  - `MODE`: `"joint"` or `"sequential_reserve_first"` to control how reserve/activation are scheduled.
  - `RUN_SPOT`, `RUN_RESERVE`, `RUN_ACTIVATION`: enable/disable spot, reserve, and activation markets.
  - `TIME_RESOLUTION` and `RESOLUTION` configure slot length (hourly vs 15-minute) and derived pandas frequency.
  - `PENALTY` sets the imbalance penalty used during settlement.
- **Clustering & aggregation:**
  - `ALIGNMENT` (`"balance_fast"`, `"start"`, etc.) controls alignment of aggregated offers.
  - `CLUSTER_METHOD`, `CLUSTER_PARAMS`, `CLUSTER_FEATURE_SET`, `CLUSTER_DISTANCE_METRIC`, `CLUSTER_LINKAGE`, and `CLUSTER_THRESHOLD*` tune clustering behavior.
  - `DYNAMIC_CLUSTERING` plus `CLUSTER_K_MIN`/`CLUSTER_K_MAX` let the simulator pick the cluster count automatically.

Adjust these values directly in `config.py` or override them programmatically (see `evaluation/evaluation_pipeline.get_scenarios`).

## Running simulations
Run the evaluation pipeline from the repository root:
```bash
python main.py
```
This evaluates every scenario returned by `get_scenarios()` and writes a summary CSV to `evaluation/results/summary.csv`. Each scenario overrides the base configuration (e.g., `TYPE`, `MODE`, `RUN_SPOT`, `RUN_RESERVE`, `RUN_ACTIVATION`, cluster settings, and `NUM_EVS`) before simulating the fleet and computing market profits.

To run a single custom scenario, either edit `get_scenarios()` or call `config.apply_override(...)` before invoking `evaluate_configurations()` in your own script.

## Dashboard (new)
After `evaluation/results/summary.csv` exists, generate a compact overview of savings, market contributions, runtimes, and optimality:
```bash
python -m evaluation.dashboard --output evaluation/results/dashboard_overview.png --show
```
- `--output` controls where the PNG is saved (defaults to `evaluation/results/dashboard_overview.png`).
- Add `--show` to pop up an interactive matplotlib window; omit it for headless environments.

## Expected artifacts
- `evaluation/results/summary.csv`: One row per scenario with runtime breakdowns, percent savings vs the greedy baseline, market contributions (spot/reserve/activation), and percent of theoretical optimum.
- `evaluation/results/dashboard_overview.png`: 2×2 matplotlib grid summarizing the metrics above for quick inspection.
- Additional analysis plots can be created with the helper scripts in `evaluation/utils/` if you export or adapt their CSV inputs.

## Troubleshooting
- **File not found:** Verify `config.DATA_FILEPATH` points to the folder containing the SmartCharging and market CSVs. Ensure the filenames match the expected hourly or 15-minute variants.
- **Resolution mismatch:** If you switch `TIME_RESOLUTION`, provide the corresponding market CSVs (hourly vs 15-minute) and rerun.
- **Scenario validation:** `get_scenarios()` skips invalid combinations (e.g., activation without reserve), so update it if you need additional modes.
- **Empty plots:** The dashboard reads `evaluation/results/summary.csv`. Delete the file or rerun `python main.py` if the dashboard complains about missing columns or empty data.
## Local setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the CLI prototype (original):
   ```bash
   python3 main.py
   ```
3. Launch the Streamlit demo:
   ```bash
   streamlit run webapp/streamlit_app.py
   ```
   The page loads sample scenarios from `evaluation/results/sample_scenarios.json` and reuses evaluation outputs in `evaluation/results/summary.csv`.

## Deployment tips
The Streamlit demo is intentionally lightweight so it can be deployed to a free tier platform and shared via URL.

### Streamlit Community Cloud
1. Push this repository to GitHub.
2. Create a new Streamlit app at https://share.streamlit.io and point it to `webapp/streamlit_app.py`.
3. Set the Python version to match your local environment (e.g., 3.11) and keep the default settings (it will install `requirements.txt`).
4. After the app boots you can share the public URL with stakeholders.

### Heroku
1. Install the Heroku CLI and log in: `heroku login`.
2. Create an app: `heroku create your-app-name`.
3. Push the code: `git push heroku work:main` (replace `work`/`main` with your branch setup).
4. Scale the web dyno: `heroku ps:scale web=1`.
5. Open the app: `heroku open`.

The included `Procfile` starts Streamlit with the correct host/port binding for Heroku. Ensure the `evaluation/results` directory is committed so the sample data and evaluation summary are available at runtime.

## To-Do
- Læg nyt data i database
- Hook spotmarket op på nyt data
- Skrive funktioner der henter data ud
  - get_spot_price
  - get_spot_prices
