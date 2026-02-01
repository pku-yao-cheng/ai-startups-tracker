#!/usr/bin/env python3
"""Generate HTML dashboard from company JSON files."""

import json
import os
from pathlib import Path

COMPANIES_DIR = Path(__file__).parent / "companies"
OUTPUT_FILE = Path(__file__).parent / "dashboard.html"

def load_companies():
    """Load all company JSON files, separating startups from reference companies."""
    startups = []
    reference_companies = []
    for json_file in COMPANIES_DIR.glob("*.json"):
        with open(json_file, 'r') as f:
            try:
                company = json.load(f)
                if company.get('company_type') == 'public-reference':
                    reference_companies.append(company)
                else:
                    startups.append(company)
            except json.JSONDecodeError as e:
                print(f"Error loading {json_file}: {e}")
    # Sort startups by composite score, reference companies by market cap
    startups = sorted(startups, key=lambda x: x.get('scores', {}).get('composite_score', 0), reverse=True)
    reference_companies = sorted(reference_companies, key=lambda x: x.get('financials', {}).get('market_cap', 0), reverse=True)
    return startups, reference_companies

def generate_html(companies, reference_companies):
    """Generate the HTML dashboard."""
    companies_json = json.dumps(companies, ensure_ascii=False, indent=2)
    reference_json = json.dumps(reference_companies, ensure_ascii=False, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Startups Tracker</title>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --border-color: #30363d;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-yellow: #d29922;
            --accent-red: #f85149;
            --accent-purple: #a371f7;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; padding: 20px; }}
        header {{ text-align: center; padding: 40px 20px; border-bottom: 1px solid var(--border-color); margin-bottom: 30px; }}
        header h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        header p {{ color: var(--text-secondary); }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .stat-card {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 10px; padding: 15px; text-align: center; }}
        .stat-card .value {{ font-size: 1.8rem; font-weight: bold; color: var(--accent-blue); }}
        .stat-card .label {{ color: var(--text-secondary); font-size: 0.85rem; }}
        .filters {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
        }}
        .filter-group {{ display: flex; flex-direction: column; gap: 4px; }}
        .filter-group label {{ font-size: 0.8rem; color: var(--text-secondary); }}
        .filter-group select, .filter-group input {{
            background: var(--bg-tertiary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 12px;
            color: var(--text-primary);
            min-width: 140px;
        }}
        .search-box {{ flex: 1; min-width: 200px; }}
        .search-box input {{ width: 100%; }}
        .tier-badges {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .tier-badge {{
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            border: 2px solid transparent;
        }}
        .tier-badge:hover, .tier-badge.active {{ transform: scale(1.05); }}
        .tier-badge.tier-s {{ background: rgba(255,215,0,0.2); color: #ffd700; }}
        .tier-badge.tier-s.active {{ border-color: #ffd700; }}
        .tier-badge.tier-a {{ background: rgba(63,185,80,0.2); color: #3fb950; }}
        .tier-badge.tier-a.active {{ border-color: #3fb950; }}
        .tier-badge.tier-b {{ background: rgba(88,166,255,0.2); color: #58a6ff; }}
        .tier-badge.tier-b.active {{ border-color: #58a6ff; }}
        .tier-badge.tier-c {{ background: rgba(210,153,34,0.2); color: #d29922; }}
        .tier-badge.tier-c.active {{ border-color: #d29922; }}
        .tier-badge.tier-d {{ background: rgba(248,81,73,0.2); color: #f85149; }}
        .tier-badge.tier-d.active {{ border-color: #f85149; }}
        .tier-badge.tier-all {{ background: rgba(139,148,158,0.2); color: var(--text-secondary); }}
        .tier-badge.tier-all.active {{ border-color: var(--text-secondary); }}
        .table-container {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border-color); }}
        th {{
            background: var(--bg-tertiary);
            font-weight: 600;
            color: var(--text-secondary);
            cursor: pointer;
            position: sticky;
            top: 0;
            white-space: nowrap;
        }}
        th:hover {{ background: var(--border-color); }}
        tr:hover {{ background: var(--bg-tertiary); cursor: pointer; }}
        .company-name {{ font-weight: 600; color: var(--accent-blue); }}
        .company-name a {{ color: inherit; text-decoration: none; }}
        .company-name a:hover {{ text-decoration: underline; }}
        .score-badge {{ display: inline-block; padding: 3px 8px; border-radius: 10px; font-weight: 600; font-size: 0.85rem; }}
        .score-s {{ background: rgba(255,215,0,0.2); color: #ffd700; }}
        .score-a {{ background: rgba(63,185,80,0.2); color: #3fb950; }}
        .score-b {{ background: rgba(88,166,255,0.2); color: #58a6ff; }}
        .score-c {{ background: rgba(210,153,34,0.2); color: #d29922; }}
        .score-d {{ background: rgba(248,81,73,0.2); color: #f85149; }}
        .category-tag {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; background: var(--bg-tertiary); color: var(--text-secondary); }}
        .stage-tag {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; background: rgba(163,113,247,0.2); color: var(--accent-purple); }}
        .flagged {{ color: var(--accent-yellow); }}
        .flagged::before {{ content: "⚠️ "; }}
        .results-count {{ padding: 8px 14px; color: var(--text-secondary); font-size: 0.85rem; border-bottom: 1px solid var(--border-color); }}
        /* Risk Badges */
        .risk-badge {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 600; margin-left: 4px; vertical-align: middle; }}
        .risk-legal {{ background: rgba(248,81,73,0.2); color: #f85149; }}
        .risk-overvalued {{ background: rgba(210,153,34,0.2); color: #d29922; }}
        .risk-execution {{ background: rgba(163,113,247,0.2); color: #a371f7; }}
        .risk-competition {{ background: rgba(88,166,255,0.2); color: #58a6ff; }}
        .risk-funding {{ background: rgba(248,81,73,0.2); color: #f85149; }}
        .risk-product {{ background: rgba(210,153,34,0.2); color: #d29922; }}
        .risks-cell {{ max-width: 150px; }}
        .risks-section {{ margin-top: 15px; padding: 12px; background: rgba(248,81,73,0.1); border: 1px solid rgba(248,81,73,0.3); border-radius: 8px; }}
        .risks-section .section-title {{ color: #f85149; border-bottom-color: rgba(248,81,73,0.3); }}
        .risk-item {{ display: flex; align-items: flex-start; gap: 8px; margin-bottom: 8px; }}
        .risk-item:last-child {{ margin-bottom: 0; }}
        .risk-item .risk-type {{ min-width: 80px; }}
        .risk-item .risk-desc {{ font-size: 0.85rem; color: var(--text-secondary); }}

        /* Modal Styles */
        .modal {{
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.85);
            z-index: 1000;
            overflow-y: auto;
        }}
        .modal.active {{ display: block; }}
        .modal-content {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            max-width: 900px;
            margin: 30px auto;
            padding: 25px;
            position: relative;
        }}
        .modal-close {{
            position: absolute;
            top: 15px; right: 20px;
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-secondary);
        }}
        .modal-close:hover {{ color: var(--text-primary); }}
        .modal-header {{ margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid var(--border-color); }}
        .modal-header h2 {{ font-size: 1.6rem; margin-bottom: 8px; }}
        .modal-header .desc {{ color: var(--text-secondary); font-size: 0.95rem; }}
        .modal-header .tags {{ margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }}
        .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 20px; }}
        .meta-item {{ background: var(--bg-tertiary); padding: 12px; border-radius: 8px; }}
        .meta-item .label {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 3px; }}
        .meta-item .value {{ font-size: 1.1rem; font-weight: 600; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-size: 1rem; color: var(--text-secondary); margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 5px; }}
        .score-bars {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; }}
        .score-bar-item {{ display: flex; align-items: center; gap: 8px; }}
        .score-bar-label {{ width: 100px; font-size: 0.8rem; color: var(--text-secondary); }}
        .score-bar-container {{ flex: 1; height: 8px; background: var(--bg-primary); border-radius: 4px; overflow: hidden; }}
        .score-bar {{ height: 100%; border-radius: 4px; }}
        .score-bar-value {{ width: 30px; font-size: 0.8rem; text-align: right; }}
        .founder-cards {{ display: flex; flex-direction: column; gap: 10px; }}
        .founder-card {{ background: var(--bg-tertiary); padding: 12px; border-radius: 8px; }}
        .founder-name {{ font-weight: 600; margin-bottom: 4px; }}
        .founder-role {{ font-size: 0.85rem; color: var(--accent-purple); margin-bottom: 6px; }}
        .founder-detail {{ font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 3px; }}
        .funding-timeline {{ display: flex; flex-direction: column; gap: 8px; }}
        .funding-round {{ display: flex; align-items: center; gap: 12px; background: var(--bg-tertiary); padding: 10px; border-radius: 8px; }}
        .funding-round .round-type {{ font-weight: 600; min-width: 80px; }}
        .funding-round .round-amount {{ color: var(--accent-green); min-width: 80px; }}
        .funding-round .round-date {{ color: var(--text-secondary); font-size: 0.85rem; }}
        .funding-round .round-lead {{ color: var(--text-secondary); font-size: 0.85rem; }}
        .investors-section {{ display: flex; flex-wrap: wrap; gap: 6px; }}
        .investor-tag {{ background: var(--bg-tertiary); padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; }}
        .investor-tag.lead {{ background: rgba(63,185,80,0.2); color: var(--accent-green); }}
        .investor-tag.strategic {{ background: rgba(163,113,247,0.2); color: var(--accent-purple); }}
        .news-list {{ display: flex; flex-direction: column; gap: 8px; }}
        .news-item {{ background: var(--bg-tertiary); padding: 10px; border-radius: 8px; }}
        .news-item a {{ color: var(--accent-blue); text-decoration: none; }}
        .news-item a:hover {{ text-decoration: underline; }}
        .news-date {{ font-size: 0.8rem; color: var(--text-secondary); margin-top: 4px; }}
        .products-list, .customers-list {{ display: flex; flex-wrap: wrap; gap: 6px; }}
        .product-tag, .customer-tag {{ background: var(--bg-tertiary); padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; }}
        .community-stats {{ display: flex; flex-wrap: wrap; gap: 12px; }}
        .community-stat {{ display: flex; align-items: center; gap: 6px; }}
        .community-stat .icon {{ font-size: 1.2rem; }}
        .market-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
        .market-item {{ background: var(--bg-tertiary); padding: 10px; border-radius: 8px; }}
        .market-item .label {{ font-size: 0.75rem; color: var(--text-secondary); }}
        .market-item .value {{ font-size: 0.9rem; margin-top: 3px; }}
        /* Financial Charts Styles */
        .arr-chart {{ display: flex; flex-direction: column; gap: 6px; }}
        .arr-bar-row {{ display: flex; align-items: center; gap: 10px; }}
        .arr-bar-date {{ width: 60px; font-size: 0.75rem; color: var(--text-secondary); }}
        .arr-bar-wrapper {{ flex: 1; height: 20px; background: var(--bg-primary); border-radius: 4px; overflow: hidden; position: relative; }}
        .arr-bar {{ height: 100%; background: linear-gradient(90deg, var(--accent-green) 0%, var(--accent-blue) 100%); border-radius: 4px; transition: width 0.3s; }}
        .arr-bar-value {{ min-width: 60px; font-size: 0.8rem; text-align: right; }}
        .arr-bar-notes {{ font-size: 0.7rem; color: var(--text-secondary); margin-left: 8px; }}
        .product-breakdown {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 10px; }}
        .product-item {{ background: var(--bg-tertiary); padding: 12px; border-radius: 8px; }}
        .product-item .name {{ font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px; }}
        .product-item .value {{ font-size: 1.1rem; font-weight: 600; color: var(--accent-green); }}
        .cost-breakdown {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; }}
        .cost-item {{ background: var(--bg-tertiary); padding: 10px; border-radius: 8px; text-align: center; }}
        .cost-item .label {{ font-size: 0.7rem; color: var(--text-secondary); margin-bottom: 4px; }}
        .cost-item .value {{ font-size: 1rem; font-weight: 600; color: var(--accent-red); }}
        .cost-item.total {{ border: 1px solid var(--accent-red); }}
        .projections-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 10px; }}
        .projection-item {{ background: var(--bg-tertiary); padding: 12px; border-radius: 8px; text-align: center; }}
        .projection-item .year {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 4px; }}
        .projection-item .value {{ font-size: 1.1rem; font-weight: 600; color: var(--accent-purple); }}
        .financial-metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 8px; margin-top: 10px; }}
        .metric-item {{ background: var(--bg-tertiary); padding: 8px; border-radius: 6px; text-align: center; }}
        .metric-item .label {{ font-size: 0.7rem; color: var(--text-secondary); }}
        .metric-item .value {{ font-size: 0.9rem; font-weight: 600; }}
        .metric-item .value.positive {{ color: var(--accent-green); }}
        .metric-item .value.negative {{ color: var(--accent-red); }}
        .metric-item .value.neutral {{ color: var(--accent-yellow); }}
        @media (max-width: 768px) {{
            .filters {{ flex-direction: column; }}
            th, td {{ padding: 6px 8px; font-size: 0.8rem; }}
        }}
        /* Reference Companies Section */
        .reference-section {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid var(--border-color);
        }}
        .reference-header {{
            margin-bottom: 20px;
        }}
        .reference-header h2 {{
            font-size: 1.4rem;
            color: var(--text-secondary);
            margin-bottom: 5px;
        }}
        .reference-header p {{
            font-size: 0.9rem;
            color: var(--text-secondary);
        }}
        .reference-table-container {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
            opacity: 0.9;
        }}
        .reference-table-container table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .reference-table-container th {{
            background: var(--bg-tertiary);
            font-weight: 600;
            color: var(--text-secondary);
            padding: 10px 14px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        .reference-table-container td {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-secondary);
        }}
        .reference-table-container tr:hover {{
            background: var(--bg-tertiary);
            cursor: pointer;
        }}
        .reference-company-name {{
            font-weight: 600;
            color: var(--text-secondary);
        }}
        .ticker-badge {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.7rem;
            background: rgba(139,148,158,0.2);
            color: var(--text-secondary);
            margin-left: 6px;
        }}
        .market-cap {{
            color: var(--text-primary);
            font-weight: 500;
        }}
        .ai-revenue {{
            color: var(--accent-green);
            font-weight: 500;
        }}
        .ai-products-cell {{
            max-width: 200px;
            font-size: 0.85rem;
        }}
        .ai-investment-cell {{
            font-size: 0.85rem;
        }}
        .ai-investment-cell a {{
            color: var(--accent-blue);
            text-decoration: none;
        }}
        .ai-investment-cell a:hover {{
            text-decoration: underline;
        }}
        /* Reference modal specific styles */
        .ai-products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 12px;
            margin-top: 10px;
        }}
        .ai-product-card {{
            background: var(--bg-tertiary);
            padding: 12px;
            border-radius: 8px;
        }}
        .ai-product-card .name {{
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}
        .ai-product-card .desc {{
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}
        .ai-product-card .status {{
            font-size: 0.75rem;
            margin-top: 6px;
            padding: 2px 6px;
            border-radius: 10px;
            display: inline-block;
        }}
        .ai-product-card .status.launched {{
            background: rgba(63,185,80,0.2);
            color: var(--accent-green);
        }}
        .ai-product-card .status.research {{
            background: rgba(163,113,247,0.2);
            color: var(--accent-purple);
        }}
        .ai-investments-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 10px;
        }}
        .ai-investment-item {{
            background: var(--bg-tertiary);
            padding: 12px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .ai-investment-item .company {{
            font-weight: 600;
            color: var(--accent-blue);
            min-width: 100px;
        }}
        .ai-investment-item .amount {{
            color: var(--accent-green);
            font-weight: 500;
        }}
        .ai-investment-item .date {{
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        .ai-investment-item .notes {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            flex: 1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AI Startups Tracker</h1>
            <p>Tracking {len(companies)} promising AI companies | Last updated: 2026-01-31</p>
        </header>
        <div class="stats-grid" id="statsGrid"></div>
        <div class="filters">
            <div class="filter-group search-box">
                <input type="text" id="searchInput" placeholder="Search companies, founders, keywords...">
            </div>
            <div class="filter-group">
                <label>Category</label>
                <select id="categoryFilter">
                    <option value="">All Categories</option>
                    <option value="foundation-model">Foundation Models</option>
                    <option value="ai-agent">AI Agents</option>
                    <option value="vertical-ai">Vertical AI</option>
                    <option value="ai-infrastructure">AI Infrastructure</option>
                    <option value="ai-application">AI Applications</option>
                    <option value="ai-robotics">Robotics</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Stage</label>
                <select id="stageFilter">
                    <option value="">All Stages</option>
                    <option value="seed">Seed</option>
                    <option value="series-a">Series A</option>
                    <option value="series-b">Series B</option>
                    <option value="series-c">Series C</option>
                    <option value="series-d+">Series D+</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Tier</label>
                <div class="tier-badges">
                    <span class="tier-badge tier-all active" data-tier="">All</span>
                    <span class="tier-badge tier-s" data-tier="s">S</span>
                    <span class="tier-badge tier-a" data-tier="a">A</span>
                    <span class="tier-badge tier-b" data-tier="b">B</span>
                    <span class="tier-badge tier-c" data-tier="c">C</span>
                    <span class="tier-badge tier-d" data-tier="d">D</span>
                </div>
            </div>
        </div>
        <div class="table-container">
            <div class="results-count" id="resultsCount"></div>
            <table>
                <thead>
                    <tr>
                        <th data-sort="rank">#</th>
                        <th data-sort="name">Company</th>
                        <th data-sort="category">Category</th>
                        <th data-sort="stage">Stage</th>
                        <th data-sort="score">Score</th>
                        <th data-sort="valuation">Valuation</th>
                        <th data-sort="arr">ARR</th>
                        <th>Founder</th>
                    </tr>
                </thead>
                <tbody id="companiesBody"></tbody>
            </table>
        </div>

        <!-- Reference Companies Section -->
        <div class="reference-section">
            <div class="reference-header">
                <h2>Reference Companies (Public Benchmarks)</h2>
                <p>Major tech companies for benchmarking AI startups. Click for AI products and investment details.</p>
            </div>
            <div class="reference-table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Company</th>
                            <th>Market Cap</th>
                            <th>AI Revenue</th>
                            <th>AI Products</th>
                            <th>AI Investments</th>
                        </tr>
                    </thead>
                    <tbody id="referenceBody"></tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="modal" id="companyModal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>
    <script>
const companies = {companies_json};
const referenceCompanies = {reference_json};

let currentSort = {{ field: 'score', direction: 'desc' }};
let filters = {{ search: '', category: '', stage: '', tier: '' }};

document.addEventListener('DOMContentLoaded', () => {{
    renderStats();
    renderTable();
    renderReferenceTable();
    setupEventListeners();
}});

function renderStats() {{
    const totalVal = companies.reduce((s, c) => s + (c.funding?.latest_valuation || 0), 0);
    const totalARR = companies.reduce((s, c) => s + (c.financials?.arr?.value || 0), 0);
    const avgScore = Math.round(companies.reduce((s, c) => s + (c.scores?.composite_score || 0), 0) / companies.length);
    const stats = [
        {{ value: companies.length, label: 'Companies' }},
        {{ value: '$' + totalVal.toFixed(0) + 'B', label: 'Total Valuation' }},
        {{ value: '$' + (totalARR/1000).toFixed(1) + 'B', label: 'Total ARR' }},
        {{ value: avgScore, label: 'Avg Score' }},
        {{ value: companies.filter(c => (c.scores?.composite_score || 0) >= 90).length, label: 'S-Tier' }},
        {{ value: companies.filter(c => (c.scores?.composite_score || 0) >= 70 && (c.scores?.composite_score || 0) < 90).length, label: 'A-Tier' }}
    ];
    document.getElementById('statsGrid').innerHTML = stats.map(s =>
        `<div class="stat-card"><div class="value">${{s.value}}</div><div class="label">${{s.label}}</div></div>`
    ).join('');
}}

function getScore(c) {{ return c.scores?.composite_score || 0; }}
function getScoreClass(score) {{
    if (score >= 90) return 'score-s';
    if (score >= 70) return 'score-a';
    if (score >= 60) return 'score-b';
    if (score >= 50) return 'score-c';
    return 'score-d';
}}
function getTier(score) {{
    if (score >= 90) return 's';
    if (score >= 70) return 'a';
    if (score >= 60) return 'b';
    if (score >= 50) return 'c';
    return 'd';
}}
function fmtVal(v) {{ return !v ? '—' : v >= 1 ? '$' + v + 'B' : '$' + (v*1000).toFixed(0) + 'M'; }}
function fmtARR(a) {{ return !a ? '—' : a >= 1000 ? '$' + (a/1000).toFixed(1) + 'B' : '$' + a + 'M'; }}
function fmtCat(c) {{ return {{'foundation-model':'Foundation Model','ai-agent':'AI Agent','vertical-ai':'Vertical AI','ai-infrastructure':'Infrastructure','ai-application':'Application','ai-robotics':'Robotics'}}[c] || c; }}
function fmtStage(s) {{ return s ? s.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : '—'; }}

function getFounderSignal(c) {{
    if (!c.founders || c.founders.length === 0) return '—';
    const f = c.founders[0];
    let signal = f.name;
    if (f.experience && f.experience.length > 0) {{
        signal += ' (' + f.experience.map(e => e.company).join(', ') + ')';
    }}
    return signal;
}}

function filterCompanies() {{
    return companies.filter(c => {{
        const score = getScore(c);
        if (filters.search) {{
            const s = filters.search.toLowerCase();
            const text = (c.name + ' ' + c.description + ' ' + JSON.stringify(c.founders)).toLowerCase();
            if (!text.includes(s)) return false;
        }}
        if (filters.category && c.category !== filters.category) return false;
        if (filters.stage) {{
            if (filters.stage === 'series-d+') {{
                if (!['series-d','series-e','series-f','series-l','pre-ipo'].some(x => c.stage?.includes(x))) return false;
            }} else if (c.stage !== filters.stage) return false;
        }}
        if (filters.tier && getTier(score) !== filters.tier) return false;
        return true;
    }});
}}

function sortCompanies(data) {{
    return [...data].sort((a, b) => {{
        let av, bv;
        switch(currentSort.field) {{
            case 'name': av = a.name.toLowerCase(); bv = b.name.toLowerCase(); break;
            case 'score': case 'rank': av = getScore(a); bv = getScore(b); break;
            case 'valuation': av = a.funding?.latest_valuation || 0; bv = b.funding?.latest_valuation || 0; break;
            case 'arr': av = a.financials?.arr?.value || 0; bv = b.financials?.arr?.value || 0; break;
            case 'category': av = a.category || ''; bv = b.category || ''; break;
            case 'stage': av = a.stage || ''; bv = b.stage || ''; break;
            default: av = getScore(a); bv = getScore(b);
        }}
        if (av === bv) return 0;
        if (av == null || av === 0) return 1;
        if (bv == null || bv === 0) return -1;
        const cmp = av < bv ? -1 : 1;
        return currentSort.direction === 'asc' ? cmp : -cmp;
    }});
}}

function renderTable() {{
    const filtered = filterCompanies();
    const sorted = sortCompanies(filtered);
    document.getElementById('resultsCount').textContent = `Showing ${{sorted.length}} of ${{companies.length}} companies`;
    document.getElementById('companiesBody').innerHTML = sorted.map((c, i) => `
        <tr onclick="showDetails('${{c.slug}}')">
            <td>${{i + 1}}</td>
            <td class="company-name ${{c.flagged ? 'flagged' : ''}}">${{c.name}}${{getRiskBadges(c)}}</td>
            <td><span class="category-tag">${{fmtCat(c.category)}}</span></td>
            <td><span class="stage-tag">${{fmtStage(c.stage)}}</span></td>
            <td><span class="score-badge ${{getScoreClass(getScore(c))}}">${{getScore(c)}}</span></td>
            <td>${{fmtVal(c.funding?.latest_valuation)}}</td>
            <td>${{fmtARR(c.financials?.arr?.value)}}</td>
            <td style="max-width:200px;font-size:0.85rem;color:var(--text-secondary)">${{getFounderSignal(c)}}</td>
        </tr>
    `).join('');
}}

const riskLabels = {{
    'legal': 'Legal',
    'overvalued': 'Overvalued',
    'execution': 'Execution',
    'competition': 'Competition',
    'funding': 'Funding',
    'product': 'Product'
}};

function getRiskBadges(c) {{
    if (!c.risks || c.risks.length === 0) return '';
    return c.risks.map(r => {{
        const type = typeof r === 'string' ? r : r.type;
        const label = riskLabels[type] || type;
        return `<span class="risk-badge risk-${{type}}">${{label}}</span>`;
    }}).join('');
}}

function getRiskSection(c) {{
    if (!c.risks || c.risks.length === 0) return '';
    let html = `<div class="risks-section"><div class="section-title">⚠️ Risk Factors</div>`;
    c.risks.forEach(r => {{
        const type = typeof r === 'string' ? r : r.type;
        const desc = typeof r === 'object' ? r.description : '';
        const label = riskLabels[type] || type;
        html += `<div class="risk-item">
            <span class="risk-badge risk-${{type}} risk-type">${{label}}</span>
            <span class="risk-desc">${{desc || ''}}</span>
        </div>`;
    }});
    html += `</div>`;
    return html;
}}

function fmtMarketCap(v) {{
    if (!v) return '—';
    if (v >= 1000) return '$' + (v/1000).toFixed(1) + 'T';
    return '$' + v + 'B';
}}

function fmtAIRevenue(fin) {{
    if (!fin?.ai_revenue) return '—';
    const v = typeof fin.ai_revenue === 'object' ? fin.ai_revenue.value : fin.ai_revenue;
    if (!v) return '—';
    if (v >= 1000) return '$' + (v/1000).toFixed(0) + 'B';
    return '$' + v + 'B';
}}

function getTopAIProducts(c, limit = 3) {{
    if (!c.ai_products || c.ai_products.length === 0) return '—';
    const products = c.ai_products.slice(0, limit);
    return products.map(p => typeof p === 'string' ? p : p.name).join(', ');
}}

function getAIInvestments(c) {{
    if (!c.ai_investments || c.ai_investments.length === 0) return '—';
    return c.ai_investments.map(inv => {{
        const amount = inv.amount ? '$' + (inv.amount >= 1000 ? (inv.amount/1000).toFixed(1) + 'B' : inv.amount + 'M') : '';
        const startup = companies.find(s => s.name.toLowerCase() === inv.company.toLowerCase());
        if (startup) {{
            return `<a href="#" onclick="event.stopPropagation(); showDetails('${{startup.slug}}')">${{inv.company}}</a> ${{amount}}`;
        }}
        return `${{inv.company}} ${{amount}}`;
    }}).join(', ');
}}

function renderReferenceTable() {{
    document.getElementById('referenceBody').innerHTML = referenceCompanies.map(c => `
        <tr onclick="showReferenceDetails('${{c.slug}}')">
            <td>
                <span class="reference-company-name">${{c.name}}</span>
                ${{c.ticker ? `<span class="ticker-badge">${{c.ticker}}</span>` : ''}}
            </td>
            <td class="market-cap">${{fmtMarketCap(c.financials?.market_cap)}}</td>
            <td class="ai-revenue">${{fmtAIRevenue(c.financials)}}</td>
            <td class="ai-products-cell">${{getTopAIProducts(c)}}</td>
            <td class="ai-investment-cell">${{getAIInvestments(c)}}</td>
        </tr>
    `).join('');
}}

function showReferenceDetails(slug) {{
    const c = referenceCompanies.find(x => x.slug === slug);
    if (!c) return;
    const fin = c.financials || {{}};

    let html = `
        <div class="modal-header">
            <h2>${{c.name}} ${{c.ticker ? `<span class="ticker-badge" style="font-size:0.9rem">${{c.ticker}}</span>` : ''}}</h2>
            <div class="desc">${{c.description || ''}}</div>
            <div class="tags">
                <span class="category-tag">Public Company</span>
                ${{c.website ? `<a href="${{c.website}}" target="_blank" style="color:var(--accent-blue);font-size:0.85rem">🔗 Website</a>` : ''}}
            </div>
        </div>
        <div class="meta-grid">
            <div class="meta-item"><div class="label">Market Cap</div><div class="value">${{fmtMarketCap(fin.market_cap)}}</div></div>
            <div class="meta-item"><div class="label">Annual Revenue</div><div class="value">${{fin.annual_revenue ? '$' + (fin.annual_revenue/1000).toFixed(0) + 'B' : '—'}}</div></div>
            <div class="meta-item"><div class="label">AI Revenue</div><div class="value" style="color:var(--accent-green)">${{fmtAIRevenue(fin)}}</div></div>
            <div class="meta-item"><div class="label">AI Growth YoY</div><div class="value" style="color:var(--accent-green)">${{fin.ai_revenue_growth_yoy ? fin.ai_revenue_growth_yoy + '%' : '—'}}</div></div>
            <div class="meta-item"><div class="label">Founded</div><div class="value">${{c.founded || '—'}}</div></div>
            <div class="meta-item"><div class="label">Employees</div><div class="value">${{fin.employees?.value ? fin.employees.value.toLocaleString() : '—'}}</div></div>
            <div class="meta-item"><div class="label">AI Employees</div><div class="value">${{fin.employees?.ai_employees ? fin.employees.ai_employees.toLocaleString() + '+' : '—'}}</div></div>
        </div>`;

    // AI Revenue Breakdown
    if (fin.ai_revenue && typeof fin.ai_revenue === 'object') {{
        html += `<div class="section"><div class="section-title">AI Revenue Details</div>`;
        if (fin.ai_revenue.breakdown) {{
            html += `<div class="product-breakdown">`;
            Object.entries(fin.ai_revenue.breakdown).forEach(([name, value]) => {{
                const displayName = name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                const fmtV = value >= 1000 ? '$' + (value/1000).toFixed(0) + 'B' : '$' + value + 'B';
                html += `<div class="product-item">
                    <div class="name">${{displayName}}</div>
                    <div class="value">${{fmtV}}</div>
                </div>`;
            }});
            html += `</div>`;
        }}
        if (fin.ai_revenue.notes) {{
            html += `<div style="font-size:0.85rem;color:var(--text-secondary);margin-top:10px">${{fin.ai_revenue.notes}}</div>`;
        }}
        html += `</div>`;
    }}

    // AI Products
    if (c.ai_products && c.ai_products.length > 0) {{
        html += `<div class="section"><div class="section-title">AI Products</div><div class="ai-products-grid">`;
        c.ai_products.forEach(p => {{
            const name = typeof p === 'string' ? p : p.name;
            const desc = typeof p === 'object' ? p.description : '';
            const status = typeof p === 'object' ? p.status : '';
            html += `<div class="ai-product-card">
                <div class="name">${{name}}</div>
                ${{desc ? `<div class="desc">${{desc}}</div>` : ''}}
                ${{status ? `<span class="status ${{status}}">${{status}}</span>` : ''}}
            </div>`;
        }});
        html += `</div></div>`;
    }}

    // AI Investments
    if (c.ai_investments && c.ai_investments.length > 0) {{
        html += `<div class="section"><div class="section-title">AI Investments in Startups</div><div class="ai-investments-list">`;
        c.ai_investments.forEach(inv => {{
            const amount = inv.amount ? '$' + (inv.amount >= 1000 ? (inv.amount/1000).toFixed(1) + 'B' : inv.amount + 'M') : '';
            const startup = companies.find(s => s.name.toLowerCase() === inv.company.toLowerCase());
            html += `<div class="ai-investment-item">
                <span class="company">${{startup ? `<a href="#" onclick="event.stopPropagation(); showDetails('${{startup.slug}}')">${{inv.company}}</a>` : inv.company}}</span>
                <span class="amount">${{amount}}</span>
                <span class="date">${{inv.date || ''}}</span>
                <span class="notes">${{inv.notes || ''}}</span>
            </div>`;
        }});
        html += `</div></div>`;
    }}

    // AI Research
    if (c.ai_research) {{
        html += `<div class="section"><div class="section-title">AI Research</div><div class="market-info">`;
        if (c.ai_research.labs) {{
            html += `<div class="market-item"><div class="label">Research Labs</div><div class="value">${{c.ai_research.labs.join(', ')}}</div></div>`;
        }}
        if (c.ai_research.papers_2024) {{
            html += `<div class="market-item"><div class="label">Papers (2024)</div><div class="value">${{c.ai_research.papers_2024}}+</div></div>`;
        }}
        if (c.ai_research.notable_contributions) {{
            html += `<div class="market-item" style="grid-column: span 2"><div class="label">Notable Contributions</div><div class="value">${{c.ai_research.notable_contributions.join(', ')}}</div></div>`;
        }}
        html += `</div></div>`;
    }}

    // Market Position
    if (c.market_position) {{
        html += `<div class="section"><div class="section-title">AI Market Position</div><div class="market-info">`;
        if (c.market_position.ai_ranking) html += `<div class="market-item"><div class="label">AI Ranking</div><div class="value">#${{c.market_position.ai_ranking}}</div></div>`;
        if (c.market_position.moats) html += `<div class="market-item" style="grid-column: span 2"><div class="label">Moats</div><div class="value">${{c.market_position.moats.join(', ')}}</div></div>`;
        if (c.market_position.ai_strategy) html += `<div class="market-item" style="grid-column: span 2"><div class="label">AI Strategy</div><div class="value">${{c.market_position.ai_strategy}}</div></div>`;
        if (c.market_position.competitors) html += `<div class="market-item"><div class="label">Competitors</div><div class="value">${{c.market_position.competitors.join(', ')}}</div></div>`;
        html += `</div></div>`;
    }}

    // News
    if (c.recent_news && c.recent_news.length > 0) {{
        html += `<div class="section"><div class="section-title">Recent AI News</div><div class="news-list">`;
        c.recent_news.slice(0, 5).forEach(n => {{
            html += `<div class="news-item"><a href="${{n.url}}" target="_blank">${{n.title}}</a><div class="news-date">${{n.date || ''}}</div></div>`;
        }});
        html += `</div></div>`;
    }}

    document.getElementById('modalContent').innerHTML = html;
    document.getElementById('companyModal').classList.add('active');
}}

function showDetails(slug) {{
    const c = companies.find(x => x.slug === slug);
    if (!c) return;
    const scores = c.scores || {{}};
    const scoreFields = [
        ['founder_score', 'Founder'],
        ['financial_health_score', 'Financial'],
        ['funding_score', 'Funding'],
        ['momentum_score', 'Momentum'],
        ['product_score', 'Product'],
        ['traction_score', 'Traction'],
        ['community_score', 'Community'],
        ['market_position_score', 'Market']
    ];

    let html = `
        <div class="modal-header">
            <h2>${{c.name}}</h2>
            <div class="desc">${{c.description || ''}}</div>
            <div class="tags">
                <span class="category-tag">${{fmtCat(c.category)}}</span>
                <span class="stage-tag">${{fmtStage(c.stage)}}</span>
                <span class="score-badge ${{getScoreClass(getScore(c))}}">${{getScore(c)}}</span>
                ${{c.website ? `<a href="${{c.website}}" target="_blank" style="color:var(--accent-blue);font-size:0.85rem">🔗 Website</a>` : ''}}
            </div>
        </div>
        <div class="meta-grid">
            <div class="meta-item"><div class="label">Valuation</div><div class="value">${{fmtVal(c.funding?.latest_valuation)}}</div></div>
            <div class="meta-item"><div class="label">ARR</div><div class="value">${{fmtARR(c.financials?.arr?.value)}}</div></div>
            <div class="meta-item"><div class="label">Total Raised</div><div class="value">${{c.funding?.total_raised ? '$' + (c.funding.total_raised >= 1000 ? (c.funding.total_raised/1000).toFixed(1) + 'B' : c.funding.total_raised + 'M') : '—'}}</div></div>
            <div class="meta-item"><div class="label">Founded</div><div class="value">${{c.founded || '—'}}</div></div>
            <div class="meta-item"><div class="label">HQ</div><div class="value">${{c.hq || '—'}}</div></div>
            <div class="meta-item"><div class="label">Employees</div><div class="value">${{c.financials?.employees?.value || '—'}}</div></div>
        </div>`;

    // Score breakdown
    html += `<div class="section"><div class="section-title">Score Breakdown</div><div class="score-bars">`;
    scoreFields.forEach(([key, label]) => {{
        const val = scores[key] || 0;
        const color = val >= 80 ? 'var(--accent-green)' : val >= 60 ? 'var(--accent-blue)' : val >= 40 ? 'var(--accent-yellow)' : 'var(--accent-red)';
        html += `<div class="score-bar-item">
            <div class="score-bar-label">${{label}}</div>
            <div class="score-bar-container"><div class="score-bar" style="width:${{val}}%;background:${{color}}"></div></div>
            <div class="score-bar-value">${{val}}</div>
        </div>`;
    }});
    html += `</div></div>`;

    // Financials Section - ARR Trend, Cost Structure, Projections
    const fin = c.financials || {{}};
    const hasFinancials = fin.arr_history || fin.arr_by_product || fin.cost_structure || fin.projections;

    if (hasFinancials) {{
        html += `<div class="section"><div class="section-title">Financial Details</div>`;

        // ARR Growth Trend Chart
        if (fin.arr_history && fin.arr_history.length > 0) {{
            const maxARR = Math.max(...fin.arr_history.map(h => h.value));
            html += `<div style="margin-bottom:15px"><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:8px">📈 ARR Growth Trend</div><div class="arr-chart">`;
            fin.arr_history.forEach(h => {{
                const pct = (h.value / maxARR) * 100;
                const fmtV = h.value >= 1000 ? '$' + (h.value/1000).toFixed(1) + 'B' : '$' + h.value + 'M';
                html += `<div class="arr-bar-row">
                    <span class="arr-bar-date">${{h.date}}</span>
                    <div class="arr-bar-wrapper"><div class="arr-bar" style="width:${{pct}}%"></div></div>
                    <span class="arr-bar-value">${{fmtV}}</span>
                    ${{h.notes ? `<span class="arr-bar-notes">${{h.notes}}</span>` : ''}}
                </div>`;
            }});
            html += `</div></div>`;
        }}

        // ARR by Product breakdown
        if (fin.arr_by_product) {{
            html += `<div style="margin-bottom:15px"><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:8px">📦 ARR by Product</div><div class="product-breakdown">`;
            Object.entries(fin.arr_by_product).forEach(([name, data]) => {{
                const val = typeof data === 'object' ? data.value : data;
                const fmtV = val >= 1000 ? '$' + (val/1000).toFixed(1) + 'B' : '$' + val + 'M';
                const displayName = name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                html += `<div class="product-item">
                    <div class="name">${{displayName}}</div>
                    <div class="value">${{fmtV}}</div>
                    ${{data.notes ? `<div style="font-size:0.7rem;color:var(--text-secondary);margin-top:4px">${{data.notes}}</div>` : ''}}
                </div>`;
            }});
            html += `</div></div>`;
        }}

        // Cost Structure
        if (fin.cost_structure) {{
            const cs = fin.cost_structure;
            html += `<div style="margin-bottom:15px"><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:8px">💰 Annual Cost Structure</div><div class="cost-breakdown">`;
            if (cs.compute_annual) html += `<div class="cost-item"><div class="label">Compute</div><div class="value">$${{cs.compute_annual >= 1000 ? (cs.compute_annual/1000).toFixed(1) + 'B' : cs.compute_annual + 'M'}}</div></div>`;
            if (cs.research_annual) html += `<div class="cost-item"><div class="label">Research</div><div class="value">$${{cs.research_annual >= 1000 ? (cs.research_annual/1000).toFixed(1) + 'B' : cs.research_annual + 'M'}}</div></div>`;
            if (cs.personnel_annual) html += `<div class="cost-item"><div class="label">Personnel</div><div class="value">$${{cs.personnel_annual >= 1000 ? (cs.personnel_annual/1000).toFixed(1) + 'B' : cs.personnel_annual + 'M'}}</div></div>`;
            if (cs.other_annual) html += `<div class="cost-item"><div class="label">Other</div><div class="value">$${{cs.other_annual >= 1000 ? (cs.other_annual/1000).toFixed(1) + 'B' : cs.other_annual + 'M'}}</div></div>`;
            if (cs.total_annual) html += `<div class="cost-item total"><div class="label">Total Annual</div><div class="value">$${{cs.total_annual >= 1000 ? (cs.total_annual/1000).toFixed(1) + 'B' : cs.total_annual + 'M'}}</div></div>`;
            html += `</div>`;
            if (cs.notes) html += `<div style="font-size:0.75rem;color:var(--text-secondary);margin-top:6px">${{cs.notes}}</div>`;
            html += `</div>`;
        }}

        // Projections
        if (fin.projections) {{
            const proj = fin.projections;
            html += `<div style="margin-bottom:15px"><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:8px">🔮 Revenue Projections</div><div class="projections-grid">`;
            if (proj.arr_2026) html += `<div class="projection-item"><div class="year">2026</div><div class="value">$${{proj.arr_2026 >= 1000 ? (proj.arr_2026/1000).toFixed(0) + 'B' : proj.arr_2026 + 'M'}}</div></div>`;
            if (proj.arr_2027) html += `<div class="projection-item"><div class="year">2027</div><div class="value">$${{proj.arr_2027 >= 1000 ? (proj.arr_2027/1000).toFixed(0) + 'B' : proj.arr_2027 + 'M'}}</div></div>`;
            if (proj.arr_2028) html += `<div class="projection-item"><div class="year">2028</div><div class="value">$${{proj.arr_2028 >= 1000 ? (proj.arr_2028/1000).toFixed(0) + 'B' : proj.arr_2028 + 'M'}}</div></div>`;
            html += `</div>`;
            if (proj.notes) html += `<div style="font-size:0.75rem;color:var(--text-secondary);margin-top:6px">${{proj.notes}}</div>`;
            html += `</div>`;
        }}

        // Key Financial Metrics
        html += `<div style="margin-bottom:10px"><div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:8px">📊 Key Metrics</div><div class="financial-metrics">`;
        if (fin.revenue_growth_yoy) html += `<div class="metric-item"><div class="label">YoY Growth</div><div class="value positive">${{fin.revenue_growth_yoy}}%</div></div>`;
        if (fin.gross_margin) html += `<div class="metric-item"><div class="label">Gross Margin</div><div class="value ${{fin.gross_margin >= 50 ? 'positive' : 'neutral'}}">${{fin.gross_margin}}%</div></div>`;
        if (fin.burn_rate_monthly) html += `<div class="metric-item"><div class="label">Burn/Month</div><div class="value negative">$${{fin.burn_rate_monthly >= 1000 ? (fin.burn_rate_monthly/1000).toFixed(1) + 'B' : fin.burn_rate_monthly + 'M'}}</div></div>`;
        if (fin.runway_months) html += `<div class="metric-item"><div class="label">Runway</div><div class="value ${{fin.runway_months >= 24 ? 'positive' : 'neutral'}}">${{fin.runway_months}} mo</div></div>`;
        if (fin.cash_flow_positive !== undefined) html += `<div class="metric-item"><div class="label">Cash Flow+</div><div class="value ${{fin.cash_flow_positive ? 'positive' : 'negative'}}">${{fin.cash_flow_positive ? 'Yes' : 'No'}}</div></div>`;
        if (fin.path_to_profitability?.target_date) html += `<div class="metric-item"><div class="label">Profitable By</div><div class="value neutral">${{fin.path_to_profitability.target_date}}</div></div>`;
        html += `</div></div>`;

        html += `</div>`;
    }}

    // Founders
    if (c.founders && c.founders.length > 0) {{
        html += `<div class="section"><div class="section-title">Founders</div><div class="founder-cards">`;
        c.founders.forEach(f => {{
            html += `<div class="founder-card">
                <div class="founder-name">${{f.name}}</div>
                <div class="founder-role">${{f.role || ''}}</div>`;
            if (f.education && f.education.length > 0) {{
                html += `<div class="founder-detail">🎓 ${{f.education.map(e => e.degree + ' ' + e.field + ', ' + e.institution).join('; ')}}</div>`;
            }}
            if (f.experience && f.experience.length > 0) {{
                html += `<div class="founder-detail">💼 ${{f.experience.map(e => e.role + ' @ ' + e.company).join('; ')}}</div>`;
            }}
            if (f.achievements && f.achievements.length > 0) {{
                html += `<div class="founder-detail">🏆 ${{f.achievements.join(', ')}}</div>`;
            }}
            html += `</div>`;
        }});
        html += `</div></div>`;
    }}

    // Funding rounds
    if (c.funding?.rounds && c.funding.rounds.length > 0) {{
        html += `<div class="section"><div class="section-title">Funding History</div><div class="funding-timeline">`;
        c.funding.rounds.forEach(r => {{
            html += `<div class="funding-round">
                <span class="round-type">${{r.type}}</span>
                <span class="round-amount">${{r.amount ? '$' + (r.amount >= 1000 ? (r.amount/1000).toFixed(1) + 'B' : r.amount + 'M') : '—'}}</span>
                <span class="round-date">${{r.date || ''}}</span>
                <span class="round-lead">${{r.lead ? '📍 ' + r.lead : ''}}</span>
            </div>`;
        }});
        html += `</div></div>`;
    }}

    // Investors
    if (c.investors) {{
        html += `<div class="section"><div class="section-title">Investors</div><div class="investors-section">`;
        (c.investors.lead_investors || []).forEach(i => html += `<span class="investor-tag lead">${{i}}</span>`);
        (c.investors.strategic_investors || []).forEach(i => html += `<span class="investor-tag strategic">${{i}}</span>`);
        (c.investors.other_investors || []).forEach(i => html += `<span class="investor-tag">${{i}}</span>`);
        html += `</div></div>`;
    }}

    // Products
    if (c.products && c.products.length > 0) {{
        html += `<div class="section"><div class="section-title">Products</div><div class="products-list">`;
        c.products.forEach(p => html += `<span class="product-tag">${{p}}</span>`);
        html += `</div></div>`;
    }}

    // Customers
    const customers = c.customers || c.traction?.enterprise_customers || [];
    if (customers.length > 0) {{
        html += `<div class="section"><div class="section-title">Customers</div><div class="customers-list">`;
        customers.forEach(cu => html += `<span class="customer-tag">${{cu}}</span>`);
        html += `</div></div>`;
    }}

    // Community
    if (c.community) {{
        html += `<div class="section"><div class="section-title">Community</div><div class="community-stats">`;
        if (c.community.github_stars) html += `<div class="community-stat"><span class="icon">⭐</span>${{(c.community.github_stars/1000).toFixed(0)}}k GitHub</div>`;
        if (c.community.discord_members) html += `<div class="community-stat"><span class="icon">💬</span>${{(c.community.discord_members/1000).toFixed(0)}}k Discord</div>`;
        if (c.community.twitter_followers) html += `<div class="community-stat"><span class="icon">🐦</span>${{(c.community.twitter_followers/1000).toFixed(0)}}k Twitter</div>`;
        html += `</div></div>`;
    }}

    // Market Position
    if (c.market_position) {{
        html += `<div class="section"><div class="section-title">Market Position</div><div class="market-info">`;
        if (c.market_position.category_rank) html += `<div class="market-item"><div class="label">Category Rank</div><div class="value">#${{c.market_position.category_rank}}</div></div>`;
        if (c.market_position.tam_estimate) html += `<div class="market-item"><div class="label">TAM</div><div class="value">${{c.market_position.tam_estimate}}</div></div>`;
        if (c.market_position.competitors) html += `<div class="market-item"><div class="label">Competitors</div><div class="value">${{c.market_position.competitors.slice(0,3).join(', ')}}</div></div>`;
        if (c.market_position.moats) html += `<div class="market-item"><div class="label">Moats</div><div class="value">${{(Array.isArray(c.market_position.moats) ? c.market_position.moats : []).join(', ')}}</div></div>`;
        html += `</div></div>`;
    }}

    // News
    if (c.recent_news && c.recent_news.length > 0) {{
        html += `<div class="section"><div class="section-title">Recent News</div><div class="news-list">`;
        c.recent_news.slice(0, 5).forEach(n => {{
            html += `<div class="news-item"><a href="${{n.url}}" target="_blank">${{n.title}}</a><div class="news-date">${{n.date || ''}}</div></div>`;
        }});
        html += `</div></div>`;
    }}

    // Risk factors
    html += getRiskSection(c);

    document.getElementById('modalContent').innerHTML = html;
    document.getElementById('companyModal').classList.add('active');
}}

function closeModal() {{ document.getElementById('companyModal').classList.remove('active'); }}

function setupEventListeners() {{
    document.getElementById('searchInput').addEventListener('input', e => {{ filters.search = e.target.value; renderTable(); }});
    document.getElementById('categoryFilter').addEventListener('change', e => {{ filters.category = e.target.value; renderTable(); }});
    document.getElementById('stageFilter').addEventListener('change', e => {{ filters.stage = e.target.value; renderTable(); }});
    document.querySelectorAll('.tier-badge').forEach(b => {{
        b.addEventListener('click', () => {{
            document.querySelectorAll('.tier-badge').forEach(x => x.classList.remove('active'));
            b.classList.add('active');
            filters.tier = b.dataset.tier;
            renderTable();
        }});
    }});
    document.querySelectorAll('th[data-sort]').forEach(th => {{
        th.addEventListener('click', () => {{
            const f = th.dataset.sort;
            currentSort = {{ field: f, direction: currentSort.field === f && currentSort.direction === 'desc' ? 'asc' : 'desc' }};
            renderTable();
        }});
    }});
    document.getElementById('companyModal').addEventListener('click', e => {{ if (e.target.id === 'companyModal') closeModal(); }});
    document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});
}}
    </script>
</body>
</html>'''
    return html

def main():
    print("Loading companies...")
    startups, reference_companies = load_companies()
    print(f"Loaded {len(startups)} startups and {len(reference_companies)} reference companies")

    print("Generating dashboard...")
    html = generate_html(startups, reference_companies)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    print(f"Dashboard saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
