# AI Startups Tracker

Track promising AI startups, their founders, ARR, funding, and news. Includes a leaderboard to rank and prioritize companies.

## Commands

- `/ai-startups-tracker` - Default: sync all companies (gather latest news and update profiles)
- `/ai-startups-tracker discover` - Find new promising startups from news sources
- `/ai-startups-tracker leaderboard` - Generate/update rankings
- `/ai-startups-tracker company:<name>` - Deep dive on specific company (e.g., `company:anthropic`)
- `/ai-startups-tracker add:<name>` - Add new company to tracking list
- `/ai-startups-tracker remove:<name>` - Remove company from tracking and add to blocklist
- `/ai-startups-tracker flagged` - Review companies flagged for potential removal (declining signals)

## Output Directory

All data is stored in `research/ai-startups/`:
- `companies/` - Company JSON profiles and markdown summaries
- `news/` - Monthly news aggregates
- `leaderboards/` - Historical ranking snapshots
- `discovery/` - New company candidates
- `.tracker_state.json` - Sync state and deduplication
- `LEADERBOARD.md` - Current rankings
- `README.md` - Quick stats overview

## Workflow

### Default Sync (`/ai-startups-tracker`)

1. Load tracker state from `research/ai-startups/.tracker_state.json`

2. **MCP News Scan** (run in parallel):
   - English: NYTimes Technology + Business, BBC Business + Technology, The Verge, InfoQ
   - Chinese: 36kr, Zhihu, Tencent News, ThePaper
   - Filter for AI/startup/funding related headlines

3. **Community Signals**:
   - `mcp__hacker-news__getTopStories`, `mcp__hacker-news__getBestStories` - search for company mentions
   - `mcp__reddit__get_subreddit_hot_posts` for r/LocalLLaMA, r/MachineLearning, r/singularity

4. For each tracked company in `research/ai-startups/companies/*.json`:
   a. **Targeted WebSearch** (use site: filters for quality):
      - `"<company>" funding OR valuation site:cnbc.com OR site:bloomberg.com OR site:reuters.com`
      - `"<company>" ARR OR revenue site:theinformation.com OR site:techcrunch.com`
      - `"<company>" customers OR partnership site:techcrunch.com OR site:venturebeat.com`
   b. Check MCP news results for company mentions
   c. Filter out URLs already in `seen_urls` (deduplication)
   d. Extract relevant data: funding rounds, ARR estimates, product launches, partnerships
   e. **Collect new scoring data**:
      - Check GitHub API for open source project stars (if applicable)
      - Search for customer announcements and enterprise logos
      - Track partnership news (strategic investors, tech partnerships)
      - Monitor community metrics (Discord size, Twitter followers)
      - Check for benchmark results and leaderboard positions
      - Assess market position (category rank, competitor movements, moat signals)
      - Track compute partnerships and cloud provider deals
   f. Update company JSON profile with new data (including new score fields)
   g. Add new URLs to `seen_urls` with timestamp and company slug

5. Save updated tracker state
6. **Red Flag Scan**: For each company, check recent news for red flag signals
   - If red_flag_score >= 40: Add to `flagged_companies`
   - If red_flag_score >= 70: Alert user immediately
   - Report at end: "⚠️ X companies flagged for review. Run `/ai-startups-tracker flagged`"
7. Generate `LEADERBOARD.md` with current rankings
8. Update `README.md` with summary stats

### Discover (`/ai-startups-tracker discover`)

1. **Funding News Scan** (WebSearch with site: filters):
   - `"AI startup" "raised" OR "funding" site:cnbc.com`
   - `"AI startup" "series" site:techcrunch.com`
   - `"AI company" "valuation" site:bloomberg.com`
   - `"seed round" AI site:venturebeat.com`
   - `"AI investment" 2026 site:crunchbase.com`

2. **MCP Trending News** (run in parallel):
   - English: NYTimes Technology, BBC Technology, The Verge, InfoQ
   - Chinese: 36kr (China AI startups), Zhihu (discussions about new companies), ThePaper

3. **Community Discovery**:
   - `mcp__hacker-news__getShowHNStories` - Look for AI/ML related launches
   - `mcp__hacker-news__getNewStories` - Emerging AI companies
   - `mcp__reddit__get_subreddit_new_posts` for r/LocalLLaMA, r/MachineLearning, r/singularity

4. **VC/Investment Sources**:
   - WebSearch: "AI startup funding 2026", "new AI company launch 2026", "AI seed round 2026"
   - WebSearch: `"raised" "million" AI site:fortune.com OR site:reuters.com`

5. Extract company mentions with signals:
   - Funding signals: "raised", "valuation", "series", "seed"
   - Founder signals: "ex-Google", "ex-OpenAI", "PhD", "founded"
   - Product signals: "launched", "released", "beta"

6. Score candidates by:
   - Mention count across sources (each source = 10 points)
   - Funding signal detected (+20 points)
   - Notable founder signal (+20 points)
   - Product launch signal (+10 points)

7. **Auto-add** companies with discovery_priority >= 70:
   - Check blocklist first - skip if company is blocklisted
   - Create new company JSON in `companies/`
   - Initialize with discovered data

8. Log ALL discoveries to `discovery/candidates.json` with scores
9. Report: "Found X new candidates, auto-added Y companies"

### Leaderboard (`/ai-startups-tracker leaderboard`)

1. Load all company profiles from `research/ai-startups/companies/*.json`
2. Calculate composite scores for each company:

**Scoring Components (8 Components):**

| Component | Weight | Description |
|-----------|--------|-------------|
| Founder Score | 15% | Education, experience, achievements, research output |
| Financial Health Score | 12% | ARR, revenue growth, burn rate, runway, margins, unit economics |
| Funding Score | 12% | Valuation + total raised + investor quality |
| Momentum Score | 8% | News frequency, sentiment, growth signals |
| Product Score | 15% | Shipped product, benchmarks, open source, API, time to ship |
| Traction Score | 13% | Enterprise customers, user growth, strategic partnerships |
| Community Score | 10% | GitHub stars, Discord size, developer adoption, HN/Reddit sentiment |
| Market Position Score | 15% | Category leadership, competitive moats, TAM, market dynamics |

**Composite Score** = (Founder * 0.15) + (Financial * 0.12) + (Funding * 0.12) + (Momentum * 0.08) + (Product * 0.15) + (Traction * 0.13) + (Community * 0.10) + (Market * 0.15)

---

### Score Calculation Details

#### Founder Score (15%)

| Signal | Points | Condition |
|--------|--------|-----------|
| Tier-1 PhD | +30 | Stanford, MIT, CMU, Berkeley, etc. |
| Tier-2 PhD | +20 | Other top-50 CS programs |
| FAANG experience | +25 | Google, Meta, Apple, Amazon, Microsoft, OpenAI, DeepMind, Anthropic |
| Prior exit | +30 | Founded and exited company |
| Research output | +15 | Papers at top venues (NeurIPS, ICML, ICLR) |
| Key hires | +10 each | Senior from FAANG/labs (max 30) |
| Technical advisors | +10 | Notable AI researchers |

#### Financial Health Score (12%)

| Signal | Points | Condition |
|--------|--------|-----------|
| **Revenue Signals** | | |
| ARR base | varies | `min(40, (ARR / 500) * 40)` where ARR in millions |
| Confidence weight | 0.7x | If ARR is estimated (not confirmed) |
| Revenue growth >100% YoY | +15 | `financials.revenue_growth_yoy > 100` |
| Revenue growth 50-100% YoY | +10 | `financials.revenue_growth_yoy > 50` |
| **Efficiency Signals** | | |
| Runway >24 months | +15 | `financials.runway_months > 24` |
| Runway 12-24 months | +8 | `financials.runway_months > 12` |
| Gross margin >70% | +15 | `financials.gross_margin > 70` |
| Gross margin 50-70% | +10 | `financials.gross_margin > 50` |
| Positive cash flow | +20 | `financials.cash_flow_positive == true` |
| Improving unit economics | +10 | LTV/CAC improving quarter over quarter |
| Path to profitability | +5 | Stated timeline to profitability |
| **Red Flags (Negative)** | | |
| Runway <6 months | -20 | `financials.runway_months < 6` |
| Burn multiple >3x | -15 | Burning >3x ARR annually |
| Declining gross margin | -10 | Margin dropped >5% YoY |

*Max: 100 points. Efficiency signals reward sustainable growth over growth-at-all-costs.*

**Data Sources:**
- ARR/Revenue: The Information, news leaks, interviews
- Burn rate/Runway: Calculated from funding raised and estimated burn
- Margins: Investor presentations, interviews, industry benchmarks
- Unit economics: Rarely public, infer from hiring patterns and news

#### Funding Score (12%)

| Signal | Points | Condition |
|--------|--------|-----------|
| Valuation base | varies | `min(50, (valuation / 50) * 50)` where valuation in billions |
| Total raised base | varies | `min(50, (total_raised / 5000) * 50)` where raised in millions |
| Tier-1 VC lead | +15 | Sequoia, a16z, Benchmark, Founders Fund, etc. |
| Strategic investor | +20 | NVIDIA, Microsoft, Google, Amazon |
| Multiple tier-1 VCs | +5 each | Additional tier-1 investors (max 15) |

#### Momentum Score (8%)

| Signal | Points | Condition |
|--------|--------|-----------|
| News frequency | varies | `min(40, articles_per_month * 5)` |
| Positive sentiment | +20 | Majority positive news coverage |
| Growth signals | +20 | Hiring, expansion, product launches |
| Declining momentum | -20 | Score dropped 20+ points in 3 months |

#### Product Score (15%)

| Signal | Points | Condition |
|--------|--------|-----------|
| Shipped product | +25 | `product.launched == true` |
| Top benchmark | +25 | Top 10 on major AI benchmark (MMLU, HumanEval, etc.) |
| GitHub stars >10k | +20 | `product.github.stars > 10000` |
| API available | +15 | `product.api_available == true` |
| Fast time to ship | +15 | `product.time_to_ship_months < 18` |

*Max: 100 points*

#### Traction Score (13%)

| Signal | Points | Condition |
|--------|--------|-----------|
| Fortune 500 customer | +15 each | Up to 3 logos (max 45) |
| Revenue growth >100% YoY | +25 | `traction.revenue_growth_yoy > 100` |
| Strategic partnership | +20 | Major tech company partnership |
| User count >10M | +15 | `traction.user_count.value > 10000000` |
| User count >1M | +10 | `traction.user_count.value > 1000000` |

*Max: 100 points (with diminishing returns)*

#### Community Score (10%)

| Signal | Points | Condition |
|--------|--------|-----------|
| GitHub stars >10k | +30 | `community.github_stars > 10000` |
| Discord >50k members | +20 | `community.discord_members > 50000` |
| Positive HN sentiment | +25 | `community.hn_mentions > 10` + positive sentiment |
| Twitter >100k followers | +15 | `community.twitter_followers > 100000` |
| Reddit presence | +10 | Active discussion in AI subreddits |

*Max: 100 points*

#### Market Position Score (15%)

| Signal | Points | Condition |
|--------|--------|-----------|
| Category leader | +25 | Top 3 in market segment |
| Large TAM | +15 | TAM >$10B addressable market |
| Unique data moat | +20 | Proprietary data advantage competitors can't replicate |
| Compute partnership | +15 | Cloud credits, dedicated GPU capacity (NVIDIA, cloud providers) |
| Distribution advantage | +15 | Existing user base, enterprise channels, platform integrations |
| First-mover advantage | +10 | First to market in category with meaningful lead |
| Regulatory moat | +10 | Favorable regulation or compliance barrier to entry |
| Patent portfolio | +5 | >10 AI-related patents |

*Max: 100 points (typically 40-70 achievable)*

**Data Sources for Market Position:**
- Category leadership: Industry reports (CB Insights, Gartner), news analysis
- TAM: Market research reports, investor presentations
- Data moat: Product analysis, news, competitive research
- Compute partnerships: News announcements, cloud provider partnerships
- Distribution: Integration announcements, platform presence

3. Generate `LEADERBOARD.md`:
```markdown
# AI Startups Leaderboard

*Last updated: YYYY-MM-DD*

## Top 10 Overall

| Rank | Company | Category | Composite | Founder | Financial | Funding | Momentum | Product | Traction | Community | Market |
|------|---------|----------|-----------|---------|-----------|---------|----------|---------|----------|-----------|--------|
| 1 | OpenAI | Foundation Model | 92 | 95 | 85 | 98 | 90 | 95 | 90 | 85 | 95 |
...

## By Category

### Foundation Models
...

### AI Agents
...
```

4. Save historical snapshot to `leaderboards/YYYY-MM-DD.json`
5. Update scores in each company's JSON profile

### Company Deep Dive (`/ai-startups-tracker company:<name>`)

1. Find company JSON in `companies/` (match by slug or fuzzy name match)

2. **Deep Research** (if available):
   - Use `mcp__deep-research__deep_research` for comprehensive company profile, founder backgrounds, competitive landscape

3. **Targeted WebSearch** (with site: filters for quality):
   - Funding: `"<company>" funding valuation site:techcrunch.com OR site:crunchbase.com`
   - Revenue: `"<company>" ARR revenue site:theinformation.com OR site:bloomberg.com`
   - Founders: `"<company>" founders CEO CTO site:linkedin.com OR site:crunchbase.com`
   - Product: `"<company>" launch product site:theverge.com OR site:venturebeat.com`

4. **MCP News Check** (search for company mentions in recent news):
   - NYTimes, BBC, The Verge for English coverage
   - 36kr, Zhihu for Chinese coverage (if relevant)

5. **Community Signals**:
   - Search Hacker News for company discussions
   - Check Reddit r/LocalLLaMA, r/MachineLearning for mentions

6. Update company JSON with all discovered data
7. Generate/update `companies/<slug>.md` human-readable profile:
```markdown
# Company Name

**Category:** Foundation Model | **Stage:** Series D | **Founded:** 2021

## Overview
Brief description...

## Founders
- **Name** (Role) - Education, Experience

## Financials
- **ARR:** $X million (estimated/confirmed)
- **Revenue Growth:** X% YoY
- **Total Raised:** $X million
- **Valuation:** $X billion
- **Runway:** X months
- **Gross Margin:** X%
- **Cash Flow:** Positive/Negative
- **Unit Economics:** Improving/Stable/Declining

## Product & Traction
- **Product:** Launched (YYYY-MM)
- **Key Customers:** Customer1, Customer2, Customer3
- **Users:** X MAU
- **Partnerships:** Partner1, Partner2

## Community
- **GitHub:** X stars
- **Discord:** X members
- **Twitter:** X followers

## Recent News
- [Title](url) - Date
...

## Market Position
- **Category Rank:** #X in [category]
- **Key Competitors:** Competitor1, Competitor2
- **Moats:** Data, Distribution, Compute
- **TAM:** $XB

## Scores
| Component | Score | Weight |
|-----------|-------|--------|
| Founder | X | 15% |
| Financial Health | X | 12% |
| Funding | X | 12% |
| Momentum | X | 8% |
| Product | X | 15% |
| Traction | X | 13% |
| Community | X | 10% |
| Market | X | 15% |
| **Composite** | **X** | **100%** |
```

### Add Company (`/ai-startups-tracker add:<name>`)

1. Check if company already exists in `companies/`
2. If exists, report and offer to run deep dive instead
3. If new:
   a. Create slug from name (lowercase, hyphenated)
   b. Perform initial research via WebSearch
   c. Create company JSON with discovered data
   d. Run scoring calculation
   e. Report: "Added <name> with composite score X"

### Remove Company (`/ai-startups-tracker remove:<name>`)

1. Find company by name/slug in `companies/`
2. Move company JSON to `archive/<slug>.json`
3. Add to blocklist in `.tracker_state.json`:
   ```json
   "blocklist": {
     "scale-ai": {
       "removed_date": "2026-01-29",
       "reason": "Founder joined Meta, company declining",
       "final_composite_score": 74
     }
   }
   ```
4. Remove from `tracked_companies` list
5. Update `LEADERBOARD.md` to exclude company
6. Report: "Removed <name> from tracking. Added to blocklist."

### Review Flagged Companies (`/ai-startups-tracker flagged`)

1. Load all company profiles
2. Run red flag detection on each company (see Red Flag Detection below)
3. Generate report of flagged companies with reasons:
   ```
   ## Companies Flagged for Review

   | Company | Red Flags | Score | Action |
   |---------|-----------|-------|--------|
   | Scale AI | Founder departure (Meta) | 74 | Consider removal |
   | Inflection | Acqui-hired by Microsoft | 47 | Consider removal |
   ```
4. For each flagged company, offer: Keep / Remove / Deep Dive

## Red Flag Detection (Auto-Detection)

During sync and discovery, automatically detect companies showing decline signals:

### Red Flag Triggers

| Red Flag | Detection Method | Points |
|----------|------------------|--------|
| **Founder Departure** | News contains "CEO left", "founder joins", "departed" | +40 |
| **Acqui-hire** | News contains "acqui-hired", "team joins", "acquired by" + skeleton crew | +50 |
| **Key Talent Exodus** | Multiple executives leaving in short period | +30 |
| **Layoffs** | News contains "layoffs", "workforce reduction", "downsizing" | +25 |
| **Funding Stagnation** | No funding round in 18+ months AND stage < Series C | +20 |
| **Valuation Down Round** | Current valuation < previous valuation | +35 |
| **Internal Turmoil** | News contains "turmoil", "exodus", "departures", "controversy" | +25 |
| **Pivot Away from AI** | Company pivoting to non-AI focus | +50 |
| **No Product After 2 Years** | Founded 2+ years ago, still no product | +15 |
| **Declining Momentum** | Momentum score dropped 20+ points in 3 months | +20 |

### Flagging Threshold

- **Red Flag Score >= 40**: Flag for review, add to `flagged_companies` in tracker state
- **Red Flag Score >= 70**: Auto-flag with high priority, notify user during sync

### Tracker State Schema Update

```json
{
  "last_sync": "2026-01-29T10:30:00Z",
  "seen_urls": {...},
  "tracked_companies": ["openai", "anthropic", ...],
  "blocklist": {
    "scale-ai": {
      "removed_date": "2026-01-29",
      "reason": "Founder joined Meta",
      "final_composite_score": 74
    }
  },
  "flagged_companies": {
    "inflection": {
      "flagged_date": "2026-01-29",
      "red_flag_score": 50,
      "reasons": ["Acqui-hired by Microsoft", "Team to Microsoft AI"]
    }
  }
}
```

### Sync Workflow Update

During default sync (`/ai-startups-tracker`), add step:

6. **Red Flag Scan**: For each company, check recent news for red flag signals
   - If red_flag_score >= 40: Add to `flagged_companies`
   - If red_flag_score >= 70: Alert user immediately
   - Report at end: "⚠️ X companies flagged for review. Run `/ai-startups-tracker flagged`"

### Discovery Blocklist Check

During discovery, automatically skip companies in blocklist:
1. Before adding any new company, check if slug exists in `blocklist`
2. If blocklisted, skip and log: "Skipped <name> (blocklisted)"

## Company Profile Schema

```json
{
  "name": "Company Name",
  "slug": "company-name",
  "stage": "seed|series-a|series-b|series-c|series-d|public",
  "category": "foundation-model|ai-agent|vertical-ai|ai-infrastructure|ai-application",
  "founded": 2021,
  "hq": "San Francisco, CA",
  "website": "https://company.com",
  "description": "Brief description",
  "founders": [
    {
      "name": "Founder Name",
      "role": "CEO",
      "linkedin": "url",
      "education": [
        {"institution": "Stanford", "degree": "PhD", "field": "CS", "tier": "tier-1"}
      ],
      "experience": [
        {"company": "Google", "role": "Research Scientist", "years": "2015-2020", "tier": "faang"}
      ],
      "achievements": ["Notable achievement"],
      "research_output": [
        {"title": "Paper Title", "venue": "NeurIPS", "year": 2024, "citations": 500}
      ],
      "founder_score": 95
    }
  ],
  "funding": {
    "total_raised": 1000,
    "latest_valuation": 10,
    "rounds": [
      {"type": "Series A", "amount": 100, "date": "2022-03", "lead": "Sequoia"}
    ]
  },
  "financials": {
    "arr": {"value": 100, "confidence": "estimated|confirmed", "as_of": "2025-12"},
    "revenue_growth_yoy": 120,
    "burn_rate_monthly": 15,
    "runway_months": 30,
    "gross_margin": 75,
    "cash_flow_positive": false,
    "ltv_cac_ratio": 3.5,
    "unit_economics_trend": "improving|stable|declining",
    "path_to_profitability": {"stated": true, "target_date": "2027-Q4"},
    "employees": {"value": 500, "as_of": "2025-12"}
  },
  "products": ["Product 1", "Product 2"],
  "product": {
    "launched": true,
    "launch_date": "2024-06",
    "benchmarks": [
      {"name": "MMLU", "rank": 3, "score": 89.5, "date": "2026-01"}
    ],
    "github": {
      "repo": "company/model",
      "stars": 45000,
      "as_of": "2026-01"
    },
    "api_available": true,
    "time_to_ship_months": 14
  },
  "traction": {
    "enterprise_customers": ["Microsoft", "Salesforce", "Stripe"],
    "user_count": {"value": 100000000, "type": "MAU", "as_of": "2026-01"},
    "partnerships": [
      {"partner": "Microsoft", "type": "strategic", "date": "2023-01", "details": "$10B investment"}
    ],
    "revenue_growth_yoy": 150
  },
  "investors": {
    "lead_investors": ["Sequoia", "a16z"],
    "strategic_investors": ["Microsoft", "NVIDIA"],
    "investor_tier": "tier-1"
  },
  "community": {
    "discord_members": 150000,
    "github_stars": 45000,
    "twitter_followers": 500000,
    "hn_mentions": 45,
    "reddit_sentiment": "positive"
  },
  "market_position": {
    "category_rank": 2,
    "competitors": ["OpenAI", "Google", "Meta"],
    "tam_estimate": "$50B",
    "moats": ["data", "distribution", "talent"],
    "compute_partnership": {"partner": "Google Cloud", "details": "Strategic cloud partnership"},
    "first_mover": false,
    "regulatory_advantage": false,
    "patent_count": 25
  },
  "recent_news": [
    {"title": "News Title", "url": "https://...", "date": "2026-01-15", "sentiment": "positive"}
  ],
  "scores": {
    "founder_score": 85,
    "financial_health_score": 70,
    "funding_score": 90,
    "momentum_score": 75,
    "product_score": 80,
    "traction_score": 85,
    "community_score": 70,
    "market_position_score": 75,
    "composite_score": 79
  },
  "last_updated": "2026-01-28"
}
```

## Tier Definitions

**Education Tiers:**
- tier-1: Stanford, MIT, CMU, Berkeley, Princeton, Harvard, Caltech, Oxford, Cambridge (PhD = 30 points, MS = 20)
- tier-2: Other top-50 CS programs (PhD = 20 points, MS = 15)
- tier-3: Other (PhD = 15 points, MS = 10)

**Experience Tiers:**
- faang: Google, Meta, Apple, Amazon, Microsoft, OpenAI, DeepMind, Anthropic (25 points)
- tier-1: Netflix, Nvidia, Tesla, Stripe, top AI labs (20 points)
- tier-2: Other notable tech companies (15 points)
- prior-exit: Founded and exited company (30 points)

**Investor Tiers:**

*Tier-1 VCs (15 points as lead):*
- Sequoia Capital
- Andreessen Horowitz (a16z)
- Benchmark
- Founders Fund
- Greylock Partners
- Lightspeed Venture Partners
- Index Ventures
- Accel
- General Catalyst
- Khosla Ventures
- Thrive Capital
- Tiger Global
- Coatue Management
- DST Global
- Spark Capital

*Strategic Investors (20 points):*
- NVIDIA
- Microsoft
- Google / Alphabet / GV
- Amazon / AWS
- Salesforce / Salesforce Ventures
- Oracle
- Meta
- Apple
- Intel Capital
- AMD
- Qualcomm Ventures

*Multiple tier-1 VCs: +5 points each additional (max 15 points)*

## Data Sources

### Primary Sources (MCP Tools)

**English News:**
- `mcp__trends-hub__get-nytimes-news` (section: "Technology", "Business") - Major business and tech coverage
- `mcp__trends-hub__get-bbc-news` (category: "business", "technology") - International business news
- `mcp__trends-hub__get-theverge-news` - Tech industry news and analysis
- `mcp__trends-hub__get-infoq-news` (region: "global") - Enterprise tech and AI developments
- `mcp__hacker-news__getTopStories`, `mcp__hacker-news__getBestStories`, `mcp__hacker-news__getShowHNStories` - Tech community signals

**Chinese News:**
- `mcp__trends-hub__get-36kr-trending` - China AI startup ecosystem
- `mcp__trends-hub__get-zhihu-trending` - Tech discussions, insider information
- `mcp__trends-hub__get-tencent-news-trending` - Business and tech news
- `mcp__trends-hub__get-thepaper-trending` - Quality journalism, business coverage
- `mcp__trends-hub__get-juejin-article-rank` (category: AI) - AI technical articles

**Community:**
- `mcp__reddit__get_subreddit_hot_posts`, `mcp__reddit__get_subreddit_new_posts` - r/LocalLLaMA, r/MachineLearning, r/singularity

**Deep Research:**
- `mcp__deep-research__deep_research` - For company deep dives, founder backgrounds, comprehensive research

### Secondary Sources (WebSearch with site: filters)

**Investment/VC News:**
- CNBC: `"AI startup" site:cnbc.com`
- Bloomberg: `"AI funding" site:bloomberg.com`
- Reuters: `"AI investment" site:reuters.com`
- Fortune: `"AI company" site:fortune.com`
- WSJ: `"AI startup" site:wsj.com`

**Startup Data:**
- TechCrunch: `"<company>" site:techcrunch.com`
- Crunchbase: `"<company>" funding site:crunchbase.com`
- The Information: `"<company>" site:theinformation.com`
- PitchBook: `"<company>" site:pitchbook.com`
- CB Insights: `"AI report" site:cbinsights.com`

**AI-Specific:**
- VentureBeat: `"AI startup" site:venturebeat.com`
- AI Business: `"AI company" site:aibusiness.com`
- AI News: `"AI startup" site:artificialintelligence-news.com`

## Deduplication

The `.tracker_state.json` file tracks processed URLs:
```json
{
  "last_sync": "2026-01-28T10:30:00Z",
  "seen_urls": {
    "https://techcrunch.com/article-url": {
      "first_seen": "2026-01-25",
      "company_slug": "anthropic"
    }
  },
  "tracked_companies": ["openai", "anthropic", ...]
}
```

Before processing any news URL:
1. Check if URL exists in `seen_urls`
2. If exists, skip processing
3. If new, process and add to `seen_urls`

## Notes

- ARR estimates are often from leaks/reports - mark confidence level
- Valuations change frequently - always note the date
- Some companies (DeepMind, Microsoft AI) are subsidiaries - track as separate entities
- Discovery auto-adds promising companies to reduce manual work

## Automatic Skill Updates (Self-Improving)

This skill automatically updates itself when new patterns, companies, or terminology are discovered during sync and discovery operations. No explicit user request is needed.

### Auto-Update Triggers

| Trigger | Action | Update Location |
|---------|--------|-----------------|
| **New company auto-added** | Add to "Tracked Companies" list | This skill file |
| **Company blocklisted** | Add to blocklist documentation | This skill file |
| **New investor tier detected** | Add to investor tier lists | This skill file |
| **New scoring signal discovered** | Propose addition to scoring tables | This skill file |
| **New data source becomes relevant** | Add to data sources section | This skill file |
| **New category emerges** | Add to category definitions | This skill file |

### Self-Update Workflow

During **sync** and **discover** operations, automatically perform these updates:

1. **Tracked Companies List Update**
   - When discovery auto-adds a new company (score >= 70), also update the "Tracked Companies" section in this skill file
   - Add to appropriate category (Foundation Models, AI Agents, Vertical AI, etc.)
   - Format: `CompanyName (product/focus)`

2. **Blocklist Documentation Update**
   - When a company is removed via `/ai-startups-tracker remove:<name>`, update blocklist examples in this skill file
   - Keep as reference for future discovery (prevents re-adding blocklisted companies)

3. **Investor Tier Updates**
   - When a new tier-1 VC or strategic investor is seen leading multiple deals, propose adding to tier definitions
   - Example: If "New VC X" leads 3+ tracked company rounds, add to Tier-1 VCs list

4. **New Scoring Signals**
   - When news reveals a new relevant signal (e.g., "government contracts", "defense partnerships"), log for potential addition
   - Store in `.tracker_state.json` under `proposed_signals`:
   ```json
   {
     "proposed_signals": [
       {"signal": "government_contracts", "seen_count": 3, "companies": ["anduril", "palantir"]}
     ]
   }
   ```
   - When a signal is seen 3+ times, auto-add to relevant scoring section

5. **Category Evolution**
   - If 3+ companies don't fit existing categories, propose new category
   - Examples: "AI Robotics", "AI Hardware", "AI Security"

### Implementation

After each sync/discover operation, check for skill updates:

```python
# Pseudo-code for skill self-update
def check_skill_updates():
    state = load_tracker_state()
    skill_content = read_skill_file()
    updates_made = []

    # 1. Check if tracked companies list needs update
    current_tracked = parse_tracked_from_skill(skill_content)
    new_companies = [c for c in state.tracked_companies if c not in current_tracked]
    if new_companies:
        update_tracked_companies_section(skill_content, new_companies)
        updates_made.append(f"Added {len(new_companies)} companies to tracked list")

    # 2. Check for new investor tiers
    new_investors = detect_new_tier1_investors(state)
    if new_investors:
        update_investor_tiers(skill_content, new_investors)
        updates_made.append(f"Added {len(new_investors)} investors to tier definitions")

    # 3. Check for proposed signals reaching threshold
    mature_signals = [s for s in state.proposed_signals if s.seen_count >= 3]
    if mature_signals:
        update_scoring_tables(skill_content, mature_signals)
        updates_made.append(f"Added {len(mature_signals)} new scoring signals")

    if updates_made:
        write_skill_file(skill_content)
        report(f"Skill auto-updated: {', '.join(updates_made)}")
```

### Update Report

At the end of sync/discover, report any skill updates:

```
Sync complete.
- Updated 5 company profiles
- Added 2 new companies (auto-discovered)
- Skill auto-updated: Added 2 companies to tracked list, Added 1 investor to tier definitions
```

### Manual Skill Updates

Some updates still require manual review:
- **Scoring weight rebalancing** - Weights should remain stable unless explicitly requested
- **Removing scoring signals** - Only remove if proven unreliable
- **Major structural changes** - New sections, workflow changes

### Tracked Companies List (Auto-Updated)

This list is automatically maintained during sync/discover operations:

**Foundation Models:** OpenAI, Anthropic, xAI, DeepMind, Microsoft AI, Mistral, Cohere, Poolside, Sakana, SSI, Thinking Machines Lab, Reflection AI, Moonshot AI (Kimi)

**AI Agents:** Sierra, Cognition (Devin), Magic AI, Anysphere (Cursor), Decagon (customer support)

**Vertical AI:** Harvey (legal), Glean (enterprise search), Mercor (hiring), Harmattan AI (defense)

**AI Infrastructure:** Fireworks, Hugging Face, Databricks, Baseten, Etched

**AI Applications:** ElevenLabs, Perplexity, Runway, Humans&

**Robotics/Embodied AI:** Skild AI, Physical Intelligence

### Blocklist (Auto-Updated)

Companies removed from tracking (prevents re-discovery):
- Scale AI - Founder joined Meta (2026-01)
- Inflection - Acqui-hired by Microsoft (2026-01)
- Adept - Acqui-hired by Amazon (2026-01)
- Character AI - Acqui-hired by Google (2026-01)
