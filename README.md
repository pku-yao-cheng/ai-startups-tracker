# AI Startups Tracker

Track and rank the most promising AI startups by founders, revenue, funding, and momentum.

## Quick Stats

| Metric | Value |
|--------|-------|
| Companies Tracked | 59 |
| Last Sync | 2026-01-31 |
| Last Discovery | 2026-01-31 (Run 3) |
| Total Funding (Jan 2026) | $60B+ |
| Flagged Companies | 1 |
| Blocklisted | 4 |

## January 2026 Headlines

| Company | News | Impact |
|---------|------|--------|
| Anthropic | $20B raise at $350B valuation, $9B ARR | Major |
| xAI | $20B Series E at $230B valuation | Major |
| OpenAI | $500B valuation, $20B+ ARR | Major |
| Anysphere | $2.3B Series D at $29.3B, $1B ARR | Major |
| Moonshot AI | Kimi K2.5 release - best open coding model | Major |
| Physical Intelligence | $600M Series B for robot foundation models | Major |
| Skild AI | $1.4B raise, $14B valuation | Major |
| Mercor | $350M at $10B valuation | Major |
| Harmattan AI | European defense AI unicorn | Emerging |
| Meta | Doubling AI spending in 2026 | Market Signal |

## Top 5 by Composite Score (8-Factor Model)

| Rank | Company | Score | Valuation | ARR |
|------|---------|-------|-----------|-----|
| 1 | OpenAI | 99 | $500B | $20B |
| 2 | Anthropic | 99 | $350B | $9B |
| 3 | Databricks | 98 | $134B | $4.8B |
| 4 | Anysphere (Cursor) | 91 | $29.3B | $1B |
| 5 | xAI | 84 | $230B | $500M |

## Latest Additions: Notable Founder Startups (Jan 30)

| Company | Score | Valuation | Founder Signal |
|---------|-------|-----------|----------------|
| **Wayve** | 70 | $2.3B | Alex Kendall (Cambridge PhD, OBE), SoftBank/Microsoft/NVIDIA |
| **Pika Labs** | 67 | $470M | Demi Guo (Stanford PhD, IOI Silver), 14.5M users |
| **Liquid AI** | 63 | $2.4B | Daniela Rus (MIT CSAIL Director), novel architecture |
| **Periodic Labs** | 58 | $1.5B | Liam Fedus (created ChatGPT), $300M seed |
| **/dev/agents** | 51 | $500M | David Singleton (Stripe CTO, Google Android VP) |
| **Imbue** | 45 | $1B | Kanjun Qiu (Dropbox Chief of Staff), woman-led unicorn |
| **Hologen** | 44 | $850M | Eric Schmidt (ex-Google CEO), AI biotech |

## Discovery Run 3 (Jan 31)

| Company | Score | Valuation | Key Signal |
|---------|-------|-----------|------------|
| **LMArena** | 78 | $1.7B | Chatbot Arena creators, fastest unicorn |
| **Synthesia** | 73 | $4B | AI video leader, 50K+ enterprise customers |
| **Luma AI** | 71 | $4B | Dream Machine video AI, $900M Series C |
| **Moonshot AI** | 68 | $3B | Kimi K2.5 - best open coding model |
| **Gamma** | 67 | $2.1B | AI presentations, a16z backed |
| **OpenEvidence** | 67 | $12B | "ChatGPT for doctors", Kensho founder |
| **Lovable** | 67 | $6.6B | Vibe coding platform, viral growth |
| **Deepgram** | 61 | $1.3B | Voice AI, enterprise customers |
| **Rogo** | 58 | $500M | AI finance, Sequoia-led |
| **Main Func** | 56 | $1.25B | AI workflow automation |
| **Serval** | 55 | $1B | IT AI agents, Khosla-backed |
| **Articul8** | 54 | $500M | Intel spinout, enterprise AI |
| **Chai Discovery** | 51 | $1.3B | AI drug discovery, Meta AI founder |

## Discovery Run 2 (Jan 29)

| Company | Score | Valuation | Key Signal |
|---------|-------|-----------|------------|
| **World Labs** | 67 | $5B | Fei-Fei Li's spatial AI, Marble product launched |
| **Lila Sciences** | 63 | $1.3B | Autonomous AI labs, NVIDIA backing |
| **Ricursive Intelligence** | 58 | $4B | AlphaChip founders, AI chip design |
| **Unconventional AI** | 57 | $4.5B | Naveen Rao (MosaicML), neuromorphic |
| **AMI Labs** | 57 | $3B | Yann LeCun's world model startup |

## Scoring Model (8 Components)

| Component | Weight |
|-----------|--------|
| Founder Score | 15% |
| Financial Health Score | 12% |
| Funding Score | 12% |
| Momentum Score | 8% |
| Product Score | 15% |
| Traction Score | 13% |
| Community Score | 10% |
| Market Position Score | 15% |

## Categories

| Category | Count | Top Company |
|----------|-------|-------------|
| Foundation Models | 17 | OpenAI ($500B) |
| AI Agents | 10 | Anysphere ($29.3B) |
| Vertical AI | 11 | OpenEvidence ($12B) |
| AI Infrastructure | 11 | Databricks ($134B) |
| AI Applications | 8 | Perplexity ($20B) |
| AI Robotics | 3 | Skild AI ($14B) |

## Red Flags / Flagged Companies

| Company | Reason | Score |
|---------|--------|-------|
| Thinking Machines Lab | Internal turmoil, employees considering return to OpenAI | 40 |

## Blocklist (Removed)

| Company | Reason | Date |
|---------|--------|------|
| Scale AI | Founder joined Meta | 2026-01 |
| Inflection | Acqui-hired by Microsoft | 2026-01 |
| Adept | Acqui-hired by Amazon | 2026-01 |
| Character AI | Acqui-hired by Google | 2026-01 |

## Community Highlights (Jan 29)

- **Kimi K2.5** trending on r/LocalLLaMA - AMA with Moonshot AI team
- **LM Studio 0.4** released - new local inference capabilities
- **API pricing in freefall** - debate on local vs cloud economics
- **BitMamba-2-1B** - 1.58-bit Mamba model running 50+ tok/s on CPU

## Usage

```bash
/ai-startups-tracker              # Sync all companies
/ai-startups-tracker discover     # Find new startups
/ai-startups-tracker leaderboard  # Generate rankings
/ai-startups-tracker company:X    # Deep dive on company X
/ai-startups-tracker add:X        # Add company X to tracking
/ai-startups-tracker flagged      # Review flagged companies
```

## Directory Structure

```
LearnLLM/ai-startups/
├── .tracker_state.json    # Sync state (59 companies tracked)
├── README.md              # This file
├── LEADERBOARD.md         # Current rankings
├── dashboard.html         # Interactive dashboard
├── companies/             # 59 company profiles
├── news/                  # Monthly news
├── leaderboards/          # Historical snapshots
└── discovery/             # New candidates
```

## Data Sources

- WebSearch: TechCrunch, The Information, Bloomberg, Crunchbase
- Hacker News: Top/Best/Show stories
- Reddit: r/LocalLLaMA, r/MachineLearning, r/singularity
- 36Kr, Zhihu: China AI ecosystem
