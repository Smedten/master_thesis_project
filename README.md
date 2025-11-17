# master-thesis

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
