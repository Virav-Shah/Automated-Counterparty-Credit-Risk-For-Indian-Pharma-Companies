"""Reproduce Cipla-only project stress scenarios and audited benchmark checks.

Project-input scenarios use the simulated FY25 row in
``data/pharma_financials_5yr.csv``. Official FY25/FY26 comparator values are
transcribed from Cipla's consolidated annual reports and are kept separate.
The scenario outputs are deterministic sensitivities, not forecasts.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "pharma_financials_5yr.csv"
MODEL = json.loads((ROOT / "config" / "model.json").read_text())
OUT_JSON = ROOT / "reports" / "cipla_stress_results.json"
OUT_CSV = ROOT / "reports" / "cipla_stress_scenarios.csv"


def point(value: float, bounds: list[float], points: list[int], inclusive: list[bool] | None = None) -> int:
    """Return the configured band's risk points."""
    for i, bound in enumerate(bounds):
        if value < bound or (inclusive and inclusive[i] and value <= bound):
            return points[i]
    return points[-1]


def read_cipla_rows() -> dict[str, dict[str, float]]:
    with INPUT.open(newline="", encoding="utf-8-sig") as stream:
        rows = csv.DictReader(stream)
        result = {}
        for row in rows:
            if row["company_id"] == "Cipla" and row["fiscal_year"] in {"FY24", "FY25"}:
                result[row["fiscal_year"]] = {key: float(row[key]) for key in (
                    "revenue", "ebitda", "ebit", "interest_expense", "cash",
                    "total_debt", "current_assets", "current_liabilities",
                    "receivables", "inventory", "operating_cash_flow", "capex",
                )}
    if set(result) != {"FY24", "FY25"}:
        raise ValueError("Cipla FY24 and FY25 rows are required in project input")
    return result


SCENARIOS = [
    {"scenario": "Project FY25 base", "revenue_change": 0.0, "margin_change_pp": 0.0,
     "interest_cost_increase": 0.0, "receivables_increase": 0.0,
     "inventory_increase": 0.0, "capex_increase": 0.0},
    {"scenario": "Moderate downside", "revenue_change": -0.10, "margin_change_pp": -0.03,
     "interest_cost_increase": 0.25, "receivables_increase": 0.10,
     "inventory_increase": 0.10, "capex_increase": 0.10},
    {"scenario": "Severe combined downside", "revenue_change": -0.20, "margin_change_pp": -0.06,
     "interest_cost_increase": 0.50, "receivables_increase": 0.20,
     "inventory_increase": 0.20, "capex_increase": 0.25},
]


def score_row(row: dict[str, float], revenue_change: float,
              receivables_growth: float, inventory_growth: float) -> dict[str, int | float | str]:
    debt_ebitda = row["total_debt"] / row["ebitda"] if row["ebitda"] else float("inf")
    coverage = row["ebit"] / row["interest_expense"] if row["interest_expense"] else float("inf")
    fcf = row["operating_cash_flow"] - row["capex"]
    fcf_debt = fcf / row["total_debt"] if row["total_debt"] else float("inf")
    current_ratio = row["current_assets"] / row["current_liabilities"] if row["current_liabilities"] else float("inf")
    gap = max(receivables_growth - revenue_change, inventory_growth - revenue_change, 0.0)
    parts = {
        "leverage_points": point(debt_ebitda, MODEL["leverage"]["upper_bounds"], MODEL["leverage"]["points"], MODEL["leverage"]["upper_inclusive"]),
        "servicing_points": point(coverage, MODEL["coverage"]["upper_bounds"], MODEL["coverage"]["points"], MODEL["coverage"]["upper_inclusive"]),
        "cash_flow_points": point(fcf_debt, MODEL["cash_flow"]["upper_bounds"], MODEL["cash_flow"]["points"], MODEL["cash_flow"]["upper_inclusive"]),
        "liquidity_points": point(current_ratio, MODEL["liquidity"]["upper_bounds"], MODEL["liquidity"]["points"], MODEL["liquidity"]["upper_inclusive"]),
        "earnings_points": point(revenue_change, MODEL["earnings"]["upper_bounds"], MODEL["earnings"]["points"]),
        "working_capital_points": (0 if gap <= 0 else 2 if gap <= .05 else 5 if gap <= .10 else 8 if gap <= .20 else 10),
    }
    total = sum(parts.values())
    bounds = MODEL["rating_upper_bounds"]
    labels = MODEL["rating_labels"]
    label = next((labels[i] for i, bound in enumerate(bounds) if total < bound), labels[-1])
    return {**parts, "working_capital_gap_pp": 100 * gap, "score": total, "band": label,
            "debt_ebitda": debt_ebitda, "interest_coverage": coverage,
            "fcf_debt": fcf_debt, "current_ratio": current_ratio, "free_cash_flow": fcf}


def build_scenarios(base: dict[str, float], prior: dict[str, float]) -> list[dict[str, float | int | str]]:
    base_margin = base["ebitda"] / base["revenue"]
    da_proxy = base["ebitda"] - base["ebit"]
    results = []
    for assumption in SCENARIOS:
        revenue_growth = assumption["revenue_change"]
        revenue = base["revenue"] * (1 + revenue_growth)
        ebitda_margin = base_margin + assumption["margin_change_pp"]
        ebitda = revenue * ebitda_margin
        ebit = ebitda - da_proxy
        interest = base["interest_expense"] * (1 + assumption["interest_cost_increase"])
        ar_delta = base["receivables"] * assumption["receivables_increase"]
        inventory_delta = base["inventory"] * assumption["inventory_increase"]
        working_capital_cash_use = ar_delta + inventory_delta
        capex = base["capex"] * (1 + assumption["capex_increase"])
        # Preserve the base OCF/EBITDA conversion, then subtract incremental
        # working-capital investment and interest cost explicitly.
        ocf_before_sensitivities = base["operating_cash_flow"] * (ebitda / base["ebitda"])
        ocf = ocf_before_sensitivities - working_capital_cash_use - (interest - base["interest_expense"])
        fcf = ocf - capex
        row = {**base, "revenue": revenue, "ebitda": ebitda, "ebit": ebit,
               "interest_expense": interest, "operating_cash_flow": ocf,
               "capex": capex}
        score_revenue_growth = revenue_growth if assumption["scenario"] != "Project FY25 base" else base["revenue"] / prior["revenue"] - 1
        score_receivables_growth = assumption["receivables_increase"] if assumption["scenario"] != "Project FY25 base" else base["receivables"] / prior["receivables"] - 1
        score_inventory_growth = assumption["inventory_increase"] if assumption["scenario"] != "Project FY25 base" else base["inventory"] / prior["inventory"] - 1
        scored = score_row(row, score_revenue_growth, score_receivables_growth, score_inventory_growth)
        results.append({
            **assumption,
            "revenue": revenue,
            "ebitda_margin_pct": ebitda_margin * 100,
            "ebitda": ebitda,
            "ebit": ebit,
            "interest_expense": interest,
            "interest_coverage_x": scored["interest_coverage"],
            "debt_ebitda_x": scored["debt_ebitda"],
            "receivables_inventory_cash_use": working_capital_cash_use,
            "operating_cash_flow": ocf,
            "capex": capex,
            "free_cash_flow": fcf,
            "fcf_debt_pct": scored["fcf_debt"] * 100,
            "current_ratio_x": scored["current_ratio"],
            **scored,
        })
    return results


def main() -> None:
    project_rows = read_cipla_rows()
    prior, base = project_rows["FY24"], project_rows["FY25"]
    scenarios = build_scenarios(base, prior)
    benchmark = {
        "currency": "INR crore",
        "consolidated": True,
        "source": "Cipla Limited Integrated Annual Report FY2025-26, consolidated financial statements, comparative FY25 and FY26 columns; year ended 31 March 2026; approved 13 May 2026",
        "fy25": {"revenue": 27547.62, "ebitda": 7128.0, "finance_costs": 62.01,
                 "borrowings_current": 80.12, "borrowings_noncurrent": 11.98,
                 "cash_equivalents": 588.69, "current_assets": 23248.97,
                 "current_liabilities": 5483.96, "receivables": 5506.37,
                 "inventory": 5642.11, "operating_cash_flow": 5004.98,
                 "ppe_purchases": 1162.16, "intangible_purchases": 386.04,
                 "depreciation_amortisation": 1106.95},
        "fy26": {"revenue": 28162.59, "ebitda": 5925.0, "finance_costs": 54.39,
                 "borrowings_current": 140.50, "borrowings_noncurrent": 117.47,
                 "cash_equivalents": 1018.22, "current_assets": 24145.86,
                 "current_liabilities": 7013.59, "receivables": 5620.05,
                 "inventory": 6596.72, "operating_cash_flow": 3940.02,
                 "ppe_purchases": 1599.33, "intangible_purchases": 1479.98,
                 "depreciation_amortisation": 1210.98},
        "cautions": [
            "Audited issuer data are a separate reality-check series and do not validate the simulated project inputs.",
            "Gross borrowings exclude lease liabilities; finance costs and EBIT proxy definitions differ from the project input extract.",
            "EBIT proxy is EBITDA less depreciation, impairment and amortisation; this does not exactly equal reported operating EBIT.",
            "Post-investment cash flow is defined here as net cash from operating activities less purchases of PPE and intangible assets; it is not the project's FCF definition."
        ]
    }
    fy25, fy26 = benchmark["fy25"], benchmark["fy26"]
    for period in (fy25, fy26):
        period["gross_borrowings"] = period["borrowings_current"] + period["borrowings_noncurrent"]
        period["ebitda_margin_pct"] = period["ebitda"] / period["revenue"] * 100
        period["ebit_proxy"] = period["ebitda"] - period["depreciation_amortisation"]
        period["ebit_proxy_interest_coverage_x"] = period["ebit_proxy"] / period["finance_costs"]
        period["gross_debt_ebitda_x"] = period["gross_borrowings"] / period["ebitda"]
        period["current_ratio_x"] = period["current_assets"] / period["current_liabilities"]
        period["post_investment_cash_flow"] = period["operating_cash_flow"] - period["ppe_purchases"] - period["intangible_purchases"]
        period["post_investment_cash_flow_debt_pct"] = period["post_investment_cash_flow"] / period["gross_borrowings"] * 100
        period["ocf_ebitda_pct"] = period["operating_cash_flow"] / period["ebitda"] * 100
    changes = {}
    for key in ("revenue", "ebitda", "finance_costs", "gross_borrowings", "operating_cash_flow",
                "post_investment_cash_flow", "current_ratio_x"):
        changes[f"{key}_change_pct"] = (fy26[key] / fy25[key] - 1) * 100
    capex_fy25 = fy25["ppe_purchases"] + fy25["intangible_purchases"]
    capex_fy26 = fy26["ppe_purchases"] + fy26["intangible_purchases"]
    changes["capex_total_change_pct"] = (capex_fy26 / capex_fy25 - 1) * 100
    changes["ebitda_margin_change_pp"] = fy26["ebitda_margin_pct"] - fy25["ebitda_margin_pct"]
    changes["inventory_growth_pct"] = (fy26["inventory"] / fy25["inventory"] - 1) * 100
    changes["receivables_growth_pct"] = (fy26["receivables"] / fy25["receivables"] - 1) * 100
    changes["revenue_growth_pct"] = changes["revenue_change_pct"]
    changes["working_capital_gap_pp"] = max(changes["inventory_growth_pct"] - changes["revenue_growth_pct"],
                                             changes["receivables_growth_pct"] - changes["revenue_growth_pct"], 0)
    payload = {"project_input_base": base, "project_scenarios": scenarios,
               "official_benchmark": benchmark, "official_fy25_to_fy26_changes": changes}
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    columns = list(scenarios[0])
    with OUT_CSV.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(scenarios)
    print(json.dumps({"json": str(OUT_JSON), "csv": str(OUT_CSV), "scenarios": scenarios,
                      "official_fy25_to_fy26_changes": changes}, indent=2))


if __name__ == "__main__":
    main()
