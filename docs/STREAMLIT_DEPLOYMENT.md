# Public Streamlit dashboard

The repository root `app.py` presents the generated, interactive finance dashboard in Streamlit Community Cloud and offers the analyst report as a download. Its financial and narrative company information is simulated. The project uses historical public market-price observations; their dates and limitations are shown in the dashboard and report.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py --as-of 2026-10-04
streamlit run app.py
```

`run.py` uses checked-in financial and market inputs and does not need a market API key. Do not add Streamlit secrets, account tokens or other credentials to Git.

## Publish on Streamlit Community Cloud

The Community Cloud deployment is linked to GitHub. After this repository has been pushed, sign in at <https://share.streamlit.io/>, connect the GitHub account that owns this repository, and create an app with:

- Repository: `Virav-Shah/Automated-Counterparty-Credit-Risk-For-Indian-Pharma-Companies`
- Branch: `main`
- Main file: `app.py`

Community Cloud builds the app from the repository and uses `requirements.txt` for the pinned Streamlit version. Future commits to the selected branch trigger app updates. The app is public when shared through a public repository and public deployment; do not include personal information or credentials in repository files.

See the [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), [repository layout guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization) and [dependency guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
