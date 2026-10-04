"""Replace the broad company cases in the original report with the Cipla analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from zipfile import ZIP_DEFLATED, ZipFile
from tempfile import NamedTemporaryFile


ROOT = Path(__file__).resolve().parents[1]
RESULTS = json.loads((ROOT / "reports" / "cipla_stress_results.json").read_text())
PROJECT_ROWS = json.loads((ROOT / "outputs" / "dashboard_data.json").read_text())["rows"]
OUTPUT = ROOT / "reports" / "Indian_Pharma_Counterparty_Credit_Report.docx"
# A fresh checkout includes the report package that carries the retained source
# styles. Fall back to the user's original file only for the initial build.
REFERENCE = OUTPUT if OUTPUT.exists() else Path("/Users/viravshah/Desktop/Indian_Pharma_Counterparty_Credit_Report.docx")
NAVY = "18324B"
BLUE = "DCEAF4"
PALE = "F2F6F9"
INK = "000000"
MID = "4A5A68"


def shade(cell, fill: str) -> None:
    pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    pr.append(shd)


def cell_margins(cell, top=90, start=105, bottom=90, end=105) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def keep_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_borders(cell, color="D9D9D9") -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    keep_table_header(row)


def setup(doc: Document) -> None:
    sec = doc.sections[0]
    sec.top_margin = Inches(.62)
    sec.bottom_margin = Inches(.60)
    sec.left_margin = Inches(.70)
    sec.right_margin = Inches(.70)
    sec.header_distance = Inches(.28)
    sec.footer_distance = Inches(.28)
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(9.4)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.05
    for name, size in (("Heading 1", 15), ("Heading 2", 11.2), ("Heading 3", 10)):
        style = doc.styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(INK)
        style.paragraph_format.space_before = Pt(6 if name != "Heading 1" else 0)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.keep_with_next = True
    title = doc.styles["Title"]
    title.font.name = "Aptos Display"
    title.font.size = Pt(27)
    title.font.bold = True
    title.font.color.rgb = RGBColor.from_string(INK)
    title.paragraph_format.space_after = Pt(9)
    # The built-in Word Title style can carry a theme bottom rule; remove it.
    title_ppr = title._element.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)

    header = sec.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = header.add_run("CIPLA  |  COUNTERPARTY CREDIT REVIEW")
    r.font.name = "Aptos"
    r.font.size = Pt(8)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(INK)
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr = footer.add_run("Virav Shah  ·  October 2026  ·  Page ")
    rr.font.name = "Aptos"
    rr.font.size = Pt(8)
    rr.font.color.rgb = RGBColor.from_string(MID)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    footer._p.append(fld)


def para(doc, text: str, *, bold_lead: str | None = None, italic=False, after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_together = True
    if bold_lead and text.startswith(bold_lead):
        a = p.add_run(bold_lead)
        a.bold = True
        p.add_run(text[len(bold_lead):])
    else:
        r = p.add_run(text)
        r.italic = italic
    return p


def heading(doc, text: str, level=1):
    return doc.add_heading(text, level=level)


def bullet(doc, text: str, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_together = True
    p.add_run(text)
    return p


def table(doc, headers, rows, widths=None, font=8.0, shade_first_col=False):
    t = doc.add_table(rows=1, cols=len(headers))
    t.autofit = False
    t.style = "Table Grid"
    if widths:
        for col, width in zip(t.columns, widths):
            col.width = Inches(width)
    for j, text in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.text = str(text)
        shade(cell, NAVY)
        cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in cell.paragraphs:
            p.paragraph_format.space_after = Pt(0)
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(font)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
        set_cell_borders(cell)
    set_repeat_table_header(t.rows[0])
    for i, values in enumerate(rows):
        cells = t.add_row().cells
        for j, value in enumerate(values):
            cells[j].text = str(value)
            cell_margins(cells[j])
            cells[j].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if i % 2 == 1 or (shade_first_col and j == 0):
                shade(cells[j], PALE if i % 2 else BLUE)
            for p in cells[j].paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.keep_together = True
                for run in p.runs:
                    run.font.name = "Calibri"
                    run.font.size = Pt(font)
                    run.font.color.rgb = RGBColor.from_string(INK)
                    if shade_first_col and j == 0:
                        run.font.bold = True
            set_cell_borders(cells[j])
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t


def callout(doc, title: str, body: str):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.cell(0, 0)
    shade(c, BLUE)
    cell_margins(c, 150, 180, 150, 180)
    c.text = ""
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p2 = c.add_paragraph(body)
    p2.paragraph_format.space_after = Pt(0)
    for run in p2.runs:
        run.font.size = Pt(9.1)
    set_cell_borders(c)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def page_break(doc):
    doc.add_page_break()


def pct(v, digits=1):
    return f"{v:.{digits}f}%"


def money(v):
    return f"{v:,.0f}"


def make_document() -> None:
    scenarios = RESULTS["project_scenarios"]
    base, moderate, severe = scenarios
    actual = RESULTS["official_benchmark"]
    actual25, actual26 = actual["fy25"], actual["fy26"]
    changes = RESULTS["official_fy25_to_fy26_changes"]
    peer = next(r for r in PROJECT_ROWS if r["company_id"] == "Cipla" and r["fiscal_year"] == "FY25")
    others = [r for r in PROJECT_ROWS if r["fiscal_year"] == "FY25" and r["peer_group"] == peer["peer_group"] and r["company_id"] != "Cipla"]
    import statistics
    medians = {k: statistics.median(float(r[k]) for r in others if r[k] is not None)
               for k in ("debt_ebitda", "interest_coverage", "current_ratio", "fcf_debt", "financial_risk_score")}
    actual_historical_fcf_change = changes["post_investment_cash_flow_change_pct"]
    if not REFERENCE.exists():
        raise FileNotFoundError(f"Report template package not found: {REFERENCE}")
    doc = Document(REFERENCE)
    body = doc._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)
    doc.core_properties.title = "Counterparty Credit Analysis of Indian Pharmaceutical Companies"
    doc.core_properties.subject = "Indian pharma credit analysis with a detailed Cipla case study"
    doc.core_properties.author = "Virav Shah"
    doc.core_properties.keywords = "Indian pharma, Cipla, counterparty credit risk, peer benchmarking, stress testing"

    # Cover and executive assessment follow the original report structure.
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(60)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("VIRAV SHAH  |  CREDIT ANALYSIS")
    r.font.name = "Calibri"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(NAVY)
    title = doc.add_paragraph(style="Title")
    title.add_run("Counterparty Credit Analysis of Indian Pharmaceutical Companies")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(22)
    r = p.add_run("Professional analyst report | Financial years FY21 to FY25 | Review date 5 October 2026")
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor.from_string(MID)
    table(doc, ["Author", "Review date", "Detailed issuer scope"], [["Virav Shah", "5 October 2026", "Cipla Limited"]], [2.1, 1.7, 2.9], 9)
    heading(doc, "Executive assessment", 1)
    callout(doc, "Cipla's simulated FY25 baseline is strong; downside analysis reveals a sharper cash-flow risk than leverage ratios suggest.",
            "The model’s FY25 baseline is 7/100 (VERY LOW). Under a combined severe shock, the modeled score rises to 25/100 (LOW), free cash flow falls from 4,900 to about 59 source units, and the receivables-plus-inventory funding requirement reaches about 2,002 units. This shows why a benign leverage ratio alone is not enough to set counterparty terms.")
    para(doc, "A separate check against Cipla’s audited FY25 and FY26 consolidated reports finds a real-world parallel: FY26 revenue increased 2.2%, while EBITDA declined 16.9%, margin contracted 4.8 percentage points and post-investment operating cash flow fell 75.1%. The reported business remained profitable and net cash from operations stayed positive. The value of the stress test is therefore in detecting shrinking cash headroom early, not in claiming distress or predicting default [2, 3].")
    para(doc, "Project financial data are simulated and their units and statement scope are not established. Project ratios and scenario scores are analytical demonstrations, not actual Cipla ratings. Audited issuer results are presented separately as a retrospective benchmark.", italic=True, after=0)
    heading(doc, "Reading guide", 1)
    table(doc, ["Section", "Coverage"], [
        ["Sector and peer framework", "Indian pharmaceutical sector context and four operating-model peer groups"],
        ["Financial analysis", "P&L, balance-sheet and cash-flow methods; five-year Cipla case"],
        ["Benchmarking and stress", "Global-generics peers, downside scenarios and FY26 actual-results challenge"],
        ["Credit application", "Counterparty review, credit-limit monitoring and evidence requirements"],
    ], [2.0, 4.7], 9)

    # Scope and index.
    page_break(doc)
    heading(doc, "Scope and index", 1)
    table(doc, ["Page", "Section"], [
        ["1", "Cover, executive assessment and reading guide"],
        ["2", "Scope, index and sector economics"],
        ["3", "Business-model peer groups"],
        ["4", "P&L, balance-sheet and cash-flow analysis method"],
        ["5", "Credit ratings and early warnings"],
        ["6", "Cipla five-year financial case study"],
        ["7", "Peer benchmarks and stress-test results"],
        ["8", "Stress interpretation and downside funding sensitivity"],
        ["9", "Audited-results benchmark and validation"],
        ["10", "Counterparty assessment and credit-limit monitoring"],
        ["11", "Evidence standards, limitations and references"],
    ], [0.75, 5.95], 9, shade_first_col=True)
    heading(doc, "Purpose and scope", 2)
    para(doc, "This report tests whether a financial-screening workflow identifies how operating weakness could pass through to earnings, debt service, working capital and counterparty capacity. It covers Cipla only. The project dataset supplies simulated FY21-FY25 figures; public audited issuer figures are used as a separate external reference for FY25 and FY26.")
    heading(doc, "What the reader should take away", 2)
    bullet(doc, "The five-year simulated history shows improving margins, leverage, interest coverage and free cash flow, with a small FY25 increase in the rule-based risk score.")
    bullet(doc, "Within the simulated global-generics peer set, Cipla has much lower leverage and stronger coverage than the other-company medians, but its score is above the peer median because of earnings and working-capital points.")
    bullet(doc, "A severe combined shock reduces modeled free cash flow to near zero while the score remains in LOW. Cash conversion, working-capital funding and data freshness need analyst review alongside the score.")
    bullet(doc, "Audited FY26 provides a useful ex-post stress benchmark: earnings and post-investment cash generation weakened while revenue grew. It does not validate the simulated inputs or establish rating accuracy.")
    heading(doc, "Sector economics and credit transmission", 2)
    para(doc, "Indian pharmaceutical companies convert research, regulatory approvals, manufacturing capacity, product portfolios and distribution into domestic and export revenues. Credit capacity depends on earnings durability, the cash needed to fund inventory and receivables, capital expenditure, regulatory remediation, and access to refinancing. Product or facility disruption can affect revenue and margins before it appears in annual ratios; customer concentration, geography, currency and product mix influence the timing and scale of that pressure.")
    para(doc, "The analysis connects the P&L to the balance sheet and cash flow: a revenue or margin shock changes operating profit; payment delays and inventory build consume liquidity; lower operating cash after investment can reduce repayment flexibility even when reported leverage remains low. These channels affect counterparty capacity but do not independently establish willingness to pay.")

    # Business-model peer groups and selection rationale.
    page_break(doc)
    heading(doc, "Peer groups and selection rationale", 1)
    para(doc, "The four peer groups are defined by business model and operating characteristics, not market capitalization or credit score. Members share meaningful features of revenue generation, geographic exposure, regulatory environment, working-capital patterns and business risks. Credit risk is the outcome compared within a group; it is not the basis used to define the group [1].")
    table(doc, ["Peer group", "Companies", "Operating rationale"], [
        ["Global Generics & Diversified", "Sun Pharma, Dr. Reddy's, Cipla, Zydus, Lupin, Aurobindo, Glenmark, Torrent", "Diversified pharma businesses with significant international/generics exposure across markets and products."],
        ["India-Focused / Branded Formulations", "Mankind, Alkem, Abbott India, JB Chemicals, Ipca, Ajanta", "Stronger domestic branded-formulation orientation and related commercial characteristics."],
        ["API / CDMO / Contract Manufacturing", "Divi's, Laurus, Piramal Pharma", "Greater exposure to API manufacturing, CDMO and related B2B operations."],
        ["Complex / Specialty / Healthcare Platforms", "Biocon, Gland Pharma, Jubilant Pharmova", "Specialized models involving biologics, specialty products, injectables or diversified healthcare platforms."],
    ], [1.55, 2.5, 2.65], 8)
    para(doc, "Cipla is benchmarked primarily against Sun Pharma, Dr. Reddy's, Zydus, Lupin, Aurobindo, Glenmark and Torrent. Membership remains an analyst-defined operating framework; individual companies still differ in scale, product mix, geography and legal structure.")

    # Financial statement analysis method.
    page_break(doc)
    heading(doc, "P&L, balance-sheet and cash-flow analysis", 1)
    para(doc, "The review links profitability, funding and cash conversion across the three primary statements. Ratios are calculated consistently for each company-year, then read as a trajectory and compared with business-model peers. The supplied financial CSV is the source for project calculations. Because its currency, monetary scale and statement scope are not verified, absolute amounts remain in source units and require reconciliation before credit sizing [1].")
    table(doc, ["Statement", "Analysis performed", "Credit question"], [
        ["P&L", "Revenue growth, EBITDA and margin, EBIT, interest expense and EBIT/interest coverage.", "Are sales and operating earnings durable enough to service financing costs?"],
        ["Balance sheet", "Gross debt, cash, net debt, debt/EBITDA, current assets/liabilities, current ratio, receivables and inventory.", "What leverage and near-term funding pressure exist, and how available is liquidity?"],
        ["Cash flow", "Operating cash flow, capital expenditure and project FCF (OCF less capex); FCF/debt.", "Do earnings convert into cash after investment, and can cash support repayment?"],
    ], [1.0, 3.1, 2.6], 8.5)
    heading(doc, "Ratio interpretation", 2)
    para(doc, "Debt/EBITDA approximates gross leverage but can move because debt changes, earnings change, or both. EBIT/interest tests a simplified servicing cushion and is sensitive to small interest denominators. The current ratio compares current assets with current liabilities but does not establish asset quality or availability. FCF/debt compares internally generated post-capex cash with gross debt; when debt is small, the ratio can appear unusually high. Trend, cash balances, maturities and working-capital composition should be read alongside each ratio.")
    para(doc, "For Cipla, the income statement traces revenue and margin resilience; the balance sheet tests borrowing and liquidity; cash flow shows whether operations fund investment. This is standardized screening, not a line-by-line audit or complete cash-conversion-cycle reconstruction.")

    # Credit scoring methodology.
    page_break(doc)
    heading(doc, "Credit ratings and early warnings", 1)
    para(doc, "The project score allocates 100 possible points across six financial dimensions. Higher scores indicate greater measured financial risk. It is transparent rule-based screening rather than a statistically calibrated probability of default or external rating [1].")
    table(doc, ["Dimension", "Weight", "Scoring principle"], [
        ["Leverage", "25", "Debt/EBITDA rises through 1x, 2x, 3x and 4x thresholds."],
        ["Debt servicing", "20", "EBIT/interest weakens through 8x, 5x, 3x and 2x thresholds."],
        ["Cash flow", "20", "FCF/debt weakens through 20%, 10%, 5% and zero."],
        ["Liquidity", "15", "Current ratio weakens through 1.5x, 1.2x, 1x and 0.8x."],
        ["Earnings resilience", "10", "Revenue growth slows through 10%, 5%, zero and −10%."],
        ["Working capital", "10", "Receivables/inventory growth increasingly exceeds sales growth."],
    ], [1.45, .7, 4.55], 8.5)
    para(doc, "Bands are VERY LOW 0–14; LOW 15–29; MODERATE 30–49; HIGH 50–69; CRITICAL 70–100. Alerts include leverage above 3x, coverage below 3x, current ratio below 1x, negative FCF, revenue decline, receivables growing faster than sales and a material score increase. Alerts prompt investigation; they do not prove default. No qualitative score is used in the financial or market layer.")
    para(doc, "A valid comparison requires aligned periods, consistent definitions, issuer and peer scope, and explanation of score components. Points organize inquiry; analyst judgment, legal-entity identity, payment experience, documentation and actual exposure remain necessary for a credit decision.")

    # Cipla five-year company analysis.
    page_break(doc)
    heading(doc, "Detailed case study: Cipla", 1)
    para(doc, "Cipla's audited FY26 report identifies North America as 24% of consolidated revenue and a key strategic market, which makes product launches, pricing and execution relevant earnings sensitivities [2]. The project peer register compares Cipla with global generics and diversified businesses on operating characteristics, rather than size or credit score [1].")
    para(doc, "The P&L review tracks revenue growth, EBITDA margin, EBIT and interest cover; the balance-sheet review tests debt/EBITDA, net debt, current assets and working-capital growth; the cash-flow review compares operating cash flow with capex. These are screening ratios, not a reconstruction of the underlying statements. In the simulated series, revenue grew at a 10.1% four-year CAGR from FY21 to FY25. EBITDA margin increased from 22.2% to 24.7%, gross debt/EBITDA fell from 0.66x to 0.07x and EBIT/interest increased from 19.8x to 76.3x [1].")
    years = [r for r in PROJECT_ROWS if r["company_id"] == "Cipla"]
    history = []
    for y in years:
        history.append([y["fiscal_year"], money(y["revenue"]), f"{100*y['ebitda']/y['revenue']:.1f}%",
                        f"{y['debt_ebitda']:.2f}x", f"{y['interest_coverage']:.1f}x",
                        money(y["free_cash_flow"]), str(y["financial_risk_score"] if y["financial_risk_score"] is not None else "n/a")])
    table(doc, ["FY", "Revenue", "EBITDA margin", "Debt/EBITDA", "EBIT/interest", "FCF", "Score"], history,
          [0.48, 1.02, 1.02, 0.92, 0.95, 0.85, 0.48], 7.6)
    para(doc, "Source units are retained from the simulated project file because currency, scale and consolidated/standalone basis are unspecified. FY21 is not fully rated because prior-year growth inputs are absent. FY22-FY25 scores are 0, 12, 5 and 7 respectively [1].", italic=True)
    heading(doc, "FY25 peer benchmark", 2)
    para(doc, "Cipla is grouped with Global Generics & Diversified companies on business model and operating characteristics. The benchmark below uses the median of the seven other companies in that group, not market-capitalization or score-based peers [1].")
    benchmark_rows = [
        ["Debt / EBITDA", f"{peer['debt_ebitda']:.2f}x", f"{medians['debt_ebitda']:.2f}x", "Lower risk than peers"],
        ["EBIT / interest", f"{peer['interest_coverage']:.1f}x", f"{medians['interest_coverage']:.1f}x", "Stronger coverage"],
        ["Current ratio", f"{peer['current_ratio']:.2f}x", f"{medians['current_ratio']:.2f}x", "Higher total-current-asset cover"],
        ["FCF / debt", f"{peer['fcf_debt']:.2f}x", f"{medians['fcf_debt']:.2f}x", "Strong; denominator is small"],
        ["Financial score", f"{peer['financial_risk_score']}/100", f"{medians['financial_risk_score']:.0f}/100", "Above peer median risk score"],
    ]
    table(doc, ["Metric", "Cipla FY25", "7-peer median", "Reading"], benchmark_rows, [1.3, 1.0, 1.15, 2.25], 8)
    para(doc, "The 7/100 score is higher than the peer median of 0 because Cipla receives 2 earnings points and 5 working-capital points. Its low leverage and strong coverage offset those points. FCF/debt is an unusually high 10.2x partly because debt is only 480 source units; it should not be treated as an achievable peer target.")

    # Page 4: methodology and scenario outputs.
    page_break(doc)
    heading(doc, "Stress scenario design and results", 1)
    para(doc, "The one-year sensitivities begin with simulated Cipla FY25. EBITDA equals revenue multiplied by the stressed EBITDA margin; the EBITDA-to-EBIT gap is held constant. Interest expense, receivables, inventory and capex are shocked as specified. Operating cash flow is scaled by the baseline OCF/EBITDA conversion, then reduced by incremental receivable and inventory investment and higher interest cost. FCF is stressed operating cash flow less capex.")
    table(doc, ["Case", "Revenue", "Margin change", "Interest cost", "AR / inventory", "Capex"], [
        ["Moderate downside", "−10%", "−3 pp", "+25%", "+10% / +10%", "+10%"],
        ["Severe combined", "−20%", "−6 pp", "+50%", "+20% / +20%", "+25%"],
    ], [1.35, .85, .95, .95, 1.15, .9], 8)
    para(doc, "These shocks are transparent analyst sensitivities, not probability-weighted forecasts. Interest expense rises as a percentage of the simulated base; no exact floating-rate debt schedule was supplied. Gross debt is held flat in the main ratio case. No market-price shock is translated into accounting revenue.")
    rows = []
    for r in scenarios:
        rows.append([r["scenario"], money(r["revenue"]), money(r["ebitda"]), f"{r['ebitda_margin_pct']:.1f}%",
                     f"{r['interest_coverage_x']:.1f}x", f"{r['debt_ebitda_x']:.2f}x",
                     money(r["free_cash_flow"]), f"{r['score']} / {r['band']}"])
    table(doc, ["Case", "Revenue", "EBITDA", "Margin", "Coverage", "Debt/EBITDA", "FCF", "Score / band"], rows,
          [1.25, .78, .8, .7, .72, .8, .72, 1.1], 7.1)
    para(doc, "Amounts are in project source units. The model's baseline FCF is 4,900; it falls to 2,438 in the moderate case and 59 in the severe case. Modeled gross leverage remains below 0.12x because the starting debt balance is very low. The severity is expressed more clearly through margin compression, cash trapped in working capital and the fall in FCF.")
    callout(doc, "Scenario output is a stress signal, not a predicted credit grade.",
            "The rule-based score moves from 7/100 (VERY LOW) to 15/100 (LOW) and 25/100 (LOW). The severe case is close to the LOW/MODERATE boundary at 30. A further 5-point increase from any additional cash-flow, liquidity, or working-capital deterioration would move the result to MODERATE.")

    # Page 5: interpretation and downside capacity.
    page_break(doc)
    heading(doc, "What the scenarios reveal", 1)
    heading(doc, "Earnings absorb the first shock; cash absorbs the combined shock", 2)
    para(doc, "In the moderate case, 10% lower revenue and a 3-point margin decline reduce EBITDA by 20.9%. A 25% rise in interest expense lowers coverage from 76.3x to 45.5x, still strong on this simplified measure. However, 10% increases in both receivables and inventory require around 1,001 source units of additional working-capital funding. FCF falls about 50% from baseline.")
    para(doc, "The severe case cuts revenue 20% and margin 6 points. EBITDA falls 39.4%, EBIT/interest falls to 26.5x and gross debt/EBITDA rises to 0.11x. The combined 20% receivables and inventory build absorbs about 2,002 units. With capex 25% higher, only about 59 units of FCF remain. The score reaches 25/100; a further deterioration can cross the 30-point MODERATE threshold.")
    heading(doc, "Conditional funding sensitivity", 2)
    para(doc, "If the entire incremental working-capital requirement were funded with additional debt rather than existing cash, gross debt would rise from 480 to about 1,481 in the moderate case and 2,482 in the severe case. Debt/EBITDA would be about 0.27x and 0.59x, respectively. These are conditional arithmetic sensitivities; they do not assume that cash is unrestricted, that suppliers extend terms, or that a lender will fund the gap.")
    table(doc, ["Funding choice", "Moderate", "Severe", "Credit implication"], [
        ["Incremental AR + inventory", "1,001", "2,002", "Cash tied up in slower collections / stock"],
        ["Debt if fully funded by borrowing", "1,481 total", "2,482 total", "0.27x / 0.59x stressed debt-to-EBITDA"],
        ["Model score", "15 / LOW", "25 / LOW", "Score may lag a sharp cash squeeze"],
    ], [1.55, 1.1, 1.1, 2.35], 8)
    heading(doc, "Reverse-stress trigger", 2)
    para(doc, "For monitoring, treat a score reaching 30, negative FCF, an actual limit breach, or repeated operating cash flow below planned capex as an escalation trigger. Since leverage starts low, working-capital drag and investment commitments are more informative near-term stress channels than gross debt alone. The threshold is a proposed review trigger, not a calibrated probability of default.")
    callout(doc, "Analyst judgment matters where the score is least sensitive.",
            "The project model holds current ratio constant in the stress cases because it lacks a reliable way to distinguish immediately available cash from receivables and inventory. The output therefore shows incremental working-capital cash use separately; a strong current ratio must not be read as proof that those assets can be collected or liquidated on time.")

    # Page 6: actual results as ex-post benchmark.
    page_break(doc)
    heading(doc, "Audited benchmark and retrospective check", 1)
    para(doc, "Cipla's FY26 consolidated annual report gives an observed downside period to compare with the hypothetical stress design. From FY25 to FY26, revenue grew 2.2%, but the company-reported EBITDA margin declined from 25.9% to 21.0%. This 4.8-point contraction sits between the report's moderate and severe margin shocks [2, 3].")
    arows = []
    for label, key, fmt in [
        ("Revenue from operations", "revenue", "money"),
        ("EBITDA", "ebitda", "money"),
        ("EBITDA margin", "ebitda_margin_pct", "pct"),
        ("Finance costs", "finance_costs", "money"),
        ("Gross borrowings", "gross_borrowings", "money"),
        ("Operating cash flow", "operating_cash_flow", "money"),
        ("PPE + intangible purchases", "capex_total", "money"),
        ("Post-investment cash flow", "post_investment_cash_flow", "money"),
        ("Current ratio", "current_ratio_x", "x"),
    ]:
        v25 = actual25.get(key, actual25.get("ppe_purchases", 0) + actual25.get("intangible_purchases", 0) if key == "capex_total" else None)
        v26 = actual26.get(key, actual26.get("ppe_purchases", 0) + actual26.get("intangible_purchases", 0) if key == "capex_total" else None)
        if fmt == "money":
            f25, f26 = f"₹{v25:,.0f}", f"₹{v26:,.0f}"
        elif fmt == "pct":
            f25, f26 = f"{v25:.1f}%", f"{v26:.1f}%"
        else:
            f25, f26 = f"{v25:.2f}x", f"{v26:.2f}x"
        change = f"{changes.get(key + '_change_pct', 0):+.1f}%" if key != "ebitda_margin_pct" else f"{changes['ebitda_margin_change_pp']:+.1f} pp"
        arows.append([label, f25, f26, change])
    table(doc, ["Consolidated measure", "FY25 actual", "FY26 actual", "Change"], arows,
          [2.15, 1.35, 1.35, 1.3], 8)
    para(doc, "All rupee amounts are INR crore. Gross borrowings are current plus non-current borrowings and exclude lease liabilities. Post-investment cash flow is net cash from operating activities less cash purchases of property, plant and equipment and intangible assets. This definition is broader than the project dataset's operating cash flow less capex field.")
    heading(doc, "What this validates", 2)
    bullet(doc, "Direction and scale: actual EBITDA margin compression of 4.8 points demonstrates that a 3-6 point stress band is plausible as a sensitivity range; it is not proof that the scenario caused the change.")
    bullet(doc, f"Cash-flow relevance: actual post-investment cash flow fell {abs(actual_historical_fcf_change):.1f}% while revenue grew. This confirms that growth alone can conceal materially lower cash available after investment.")
    bullet(doc, "Risk-model challenge: debt/EBITDA remained very low in audited results, so a leverage-led model can remain calm while FCF and liquidity headroom weaken. Working-capital, investment and score-migration triggers should sit beside leverage tests.")
    para(doc, "The FY26 comparison is an ex-post challenge to the framework, not an out-of-sample prediction: the project model was built on simulated numbers and was not calibrated or run against these audited values before the outcome occurred.", italic=True)

    # Page 7: practical credit decision.
    page_break(doc)
    heading(doc, "Counterparty review and limit-monitoring actions", 1)
    heading(doc, "Credit view", 2)
    para(doc, "On the simulated FY25 evidence alone, Cipla would screen as VERY LOW risk with low gross leverage, strong coverage, positive FCF and broad current-asset cover. The severe scenario remains within the LOW band but nearly exhausts annual FCF. This supports a conditional historical screening view, not an approved limit or a current credit recommendation for the real issuer.")
    heading(doc, "Before setting a limit", 2)
    bullet(doc, "Confirm the contracting legal entity, group relationship, currency, payment terms, guarantee and governing law. Do not assume the listed parent supports an affiliate's obligation.")
    bullet(doc, "Replace the simulated series with audited, same-scope financial statements and reconcile revenue, EBITDA, borrowings, finance costs, cash and cash-flow classifications.")
    bullet(doc, "Obtain debt and lease maturities, interest-rate exposure, covenant headroom, unrestricted cash and committed capital expenditure. Separate scheduled funding needs from discretionary expansion.")
    bullet(doc, "Collect customer and product concentration, receivable ageing, overdue disputes, inventory ageing/obsolescence, supplier terms and cash forecasts before increasing exposure.")
    heading(doc, "Proposed monitoring controls", 2)
    table(doc, ["Control", "Operating test", "Escalation"], [
        ["Exposure and limit", "Aggregate drawn + policy-defined committed exposure by legal entity and group", "Review at 80%; escalate any amount above approved limit"],
        ["Payment performance", "Age invoices, disputes, deductions and missed contractual dates", "Escalate repeated overdue or disputed balances"],
        ["Financial refresh", "Reconcile quarterly/annual figures to statements; rerun ratios and scenarios", "Review on margin, FCF, leverage or working-capital trigger"],
        ["Approval governance", "Record limit owner, amount, currency, expiry, exceptions and review date", "No undocumented override; set owner and expiry for each exception"],
    ], [1.25, 3.1, 2.35], 7.7)
    para(doc, "An 80% utilization threshold is a proposed internal early-warning level, not a regulatory standard. Actual approved limits, receivables, payment records and obligor-level exposures were not supplied; the project has not measured real utilization, overdue balances or a breach.")
    heading(doc, "Recommended analyst conclusion", 2)
    callout(doc, "Use the historical score to prioritize review, and make the decision on the verified obligor and exposure.",
            "For the project case, record Cipla as a strong simulated baseline with meaningful downside sensitivity to margin and working-capital shocks. Do not translate the screen into a real-company rating or monetary limit until the source data and exposure records are reconciled.")

    # Page 8: definitions and sources.
    page_break(doc)
    heading(doc, "Evidence standards, definitions and limitations", 1)
    heading(doc, "Key definitions", 2)
    table(doc, ["Measure", "Definition used here"], [
        ["Debt / EBITDA", "Total debt divided by EBITDA; stress holds project debt flat unless a separate funding sensitivity is stated."],
        ["Interest coverage", "EBIT divided by interest expense. The scenario holds the FY25 EBITDA-to-EBIT gap constant."],
        ["Free cash flow", "Project scenarios: operating cash flow less supplied capex. Official benchmark: operating cash flow less cash purchases of PPE and intangible assets."],
        ["Working-capital cash use", "Increase in receivables plus increase in inventory under the stated scenario percentages."],
        ["Financial score", "Existing six-factor rule-based score out of 100; higher is worse. It is not a PD or agency rating."],
    ], [1.55, 5.15], 8)
    heading(doc, "Important limitations", 2)
    bullet(doc, "Project financial and narrative company data are simulated. Source currency, monetary scale, statement scope and reporting provenance are not confirmed.")
    bullet(doc, "Scenario results are one-year static sensitivities. They do not model tax, dividends, acquisition spending, debt maturity, FX, price/volume interactions, covenant definitions or an endogenous change to supplier financing.")
    bullet(doc, "The stress score keeps the current ratio at its FY25 base because the available data cannot reliably split cash from working-capital asset quality under stress. Incremental AR/inventory cash demand is therefore shown separately.")
    bullet(doc, "FY26 issuer data are audited disclosures, but they do not make the simulated FY25 project extract authentic. Differences in definitions and scope prevent direct ratio substitution without full reconciliation.")
    bullet(doc, "No default outcome, credit loss, external rating migration or counterparty exposure was available. Predictive accuracy and an appropriate actual credit limit are not established.")
    heading(doc, "References", 2)
    refs = [
        "[1] Project input: data/pharma_financials_5yr.csv (simulated); Cipla peer group: config/peer_groups.csv; score rules: config/model.json and docs/METHODOLOGY.md; peer comparison: outputs/dashboard_data.json.",
        "[2] Cipla Limited, Integrated Annual Report FY2025-26, audited consolidated financial statements and FY25 comparatives; approved 13 May 2026. https://www.cipla.com/sites/default/files/Cipla-Annual-Report-FY2025-26.pdf",
        "[3] Cipla Limited, Audited consolidated financial results for year ended 31 March 2026, 13 May 2026. https://www.cipla.com/sites/default/files/SignedFinancialResults13052026Signed.pdf",
        "[4] Cipla Limited, Integrated Annual Report FY2024-25, audited consolidated FY25 statements and operating discussion. https://www.cipla.com/sites/default/files/Cipla-AR-2024-25.pdf",
        "[5] Reproducible scenario calculations: scripts/cipla_stress_test.py; outputs: reports/cipla_stress_results.json and reports/cipla_stress_scenarios.csv. Prepared 5 October 2026.",
    ]
    for item in refs:
        para(doc, item, after=3)
    para(doc, "Prepared by Virav Shah | 5 October 2026 | Cipla-only analysis", italic=True, after=0)
    with NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        working_docx = Path(tmp.name)
    doc.save(working_docx)
    # Transplant only the authored body into an exact copy of the retained
    # template package. This preserves every other package member byte-for-byte.
    with NamedTemporaryFile(suffix=".docx", dir=OUTPUT.parent, delete=False) as tmp:
        packaged = Path(tmp.name)
    with ZipFile(REFERENCE, "r") as original, ZipFile(working_docx, "r") as edited, ZipFile(packaged, "w", ZIP_DEFLATED) as final:
        edited_document_xml = edited.read("word/document.xml")
        for item in original.infolist():
            data = edited_document_xml if item.filename == "word/document.xml" else original.read(item.filename)
            final.writestr(item, data)
    packaged.replace(OUTPUT)
    working_docx.unlink(missing_ok=True)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    make_document()
