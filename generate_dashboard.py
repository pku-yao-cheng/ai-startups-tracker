#!/usr/bin/env python3
"""Generate HTML dashboard from company JSON files."""

import json
import os
from pathlib import Path

COMPANIES_DIR = Path(__file__).parent / "companies"
OUTPUT_FILE = Path(__file__).parent / "dashboard.html"

def load_companies():
    """Load all company JSON files."""
    companies = []
    for json_file in COMPANIES_DIR.glob("*.json"):
        with open(json_file, 'r') as f:
            try:
                company = json.load(f)
                companies.append(company)
            except json.JSONDecodeError as e:
                print(f"Error loading {json_file}: {e}")
    return sorted(companies, key=lambda x: x.get('scores', {}).get('composite_score', 0), reverse=True)

def generate_html(companies):
    """Generate the HTML dashboard."""
    companies_json = json.dumps(companies, ensure_ascii=False, indent=2)

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
        @media (max-width: 768px) {{
            .filters {{ flex-direction: column; }}
            th, td {{ padding: 6px 8px; font-size: 0.8rem; }}
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
    </div>
    <div class="modal" id="companyModal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>
    <script>
const companies = {companies_json};

let currentSort = {{ field: 'score', direction: 'desc' }};
let filters = {{ search: '', category: '', stage: '', tier: '' }};

document.addEventListener('DOMContentLoaded', () => {{
    renderStats();
    renderTable();
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
            <td class="company-name ${{c.flagged ? 'flagged' : ''}}">${{c.name}}</td>
            <td><span class="category-tag">${{fmtCat(c.category)}}</span></td>
            <td><span class="stage-tag">${{fmtStage(c.stage)}}</span></td>
            <td><span class="score-badge ${{getScoreClass(getScore(c))}}">${{getScore(c)}}</span></td>
            <td>${{fmtVal(c.funding?.latest_valuation)}}</td>
            <td>${{fmtARR(c.financials?.arr?.value)}}</td>
            <td style="max-width:200px;font-size:0.85rem;color:var(--text-secondary)">${{getFounderSignal(c)}}</td>
        </tr>
    `).join('');
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
    companies = load_companies()
    print(f"Loaded {len(companies)} companies")

    print("Generating dashboard...")
    html = generate_html(companies)

    with open(OUTPUT_FILE, 'w') as f:
        f.write(html)
    print(f"Dashboard saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
