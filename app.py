"""Streamlit Community Cloud entry point for the existing finance dashboard."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components


ROOT = Path(__file__).resolve().parent
DASHBOARD = ROOT / "outputs" / "dashboard.html"
REPORT = ROOT / "reports" / "Indian_Pharma_Counterparty_Credit_Report.docx"

st.set_page_config(
    page_title="Indian Pharma Counterparty Credit Monitor",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Indian Pharma Counterparty Credit Monitor")
st.caption(
    "Finance project using simulated company financial and narrative data. "
    "Internal screening outputs are educational and are not external credit ratings."
)

if not DASHBOARD.exists():
    st.error("The generated dashboard is missing. Run `python run.py --as-of 2026-10-04` from the project root.")
    st.stop()

with st.expander("About the project data and results"):
    st.write(
        "The financial extract covers 20 companies over FY21-FY25. Narrative research "
        "is preserved without qualitative scoring. Market observations are historical "
        "public prices, shown with their dates. Financial input units and statement "
        "scope have not been fully reconciled to issuer disclosures."
    )
    st.write(
        "The FY25 results are historical screening outputs. The accompanying report "
        "documents source differences, independent calculation checks, peer and "
        "market benchmarks, and limits on interpreting the internal risk score."
    )

if REPORT.exists():
    st.download_button(
        "Download the 15-page analyst report",
        data=REPORT.read_bytes(),
        file_name=REPORT.name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

components.html(DASHBOARD.read_text(encoding="utf-8"), height=1800, scrolling=True)
