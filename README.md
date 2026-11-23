# 📏 A Better Ruler: Four-Pillar Economic Dashboard

> *"We do not need one more magic number. We need four related sets of measures."*

**A Better Ruler** is an open-source, interactive Streamlit economic dashboard powered by official US Government and academic data. It replaces traditional single-aggregate "magic numbers" (like national GDP or average national unemployment) with a grounded, four-pillar framework of economic well-being and household reality.

---

## 🏛️ The Four-Pillar Framework

1. **⚙️ Capacity (What can the economy produce?)**
   - *Indicators*: Real Gross Domestic Product (`GDPC1`), Nonfarm Business Sector Labor Productivity (`OPHNFB`).
   - *Data Sources*: Bureau of Economic Analysis (BEA), Bureau of Labor Statistics (BLS).

2. **📊 Distribution (Who receives the income and wealth generated?)**
   - *Indicators*: Aggregate GDP ($1/Vote) vs. Democratic Domestic Product (DDP, 1 Person/Vote), Gini Index (`GINIALLRH`), Top 1% vs. Bottom 50% Wealth Shares.
   - *Data Sources*: Federal Reserve Distributional Financial Accounts (DFA), Census Bureau, Adamou et al. (2020) framework.

3. **🛡️ Resilience (Can families absorb a setback without losing economic footing?)**
   - *Indicators*: Household Debt Service Ratio (`TDSP`), Commercial Bank Credit Card Delinquency Rates (`DRCLACBS`), Balance Sheet Financial Obligations.
   - *Data Sources*: Federal Reserve Board of Governors, Survey of Consumer Finances (SCF).

4. **📍 Participation (What does it cost locally to remain attached to work & ordinary life?)**
   - *Indicators*: MIT Living Wage Benchmarks (50 States + 50 Major Cities), ALICE (Asset Limited, Income Constrained, Employed) Household Essentials Index, Interactive Benefit-Cliff Simulator.
   - *Data Sources*: MIT Living Wage Calculator, United for ALICE Project, Census ACS.

---

## ✨ Features & Capabilities

- 🗺️ **Interactive 50-State US Choropleth Map**: Color-code states by Living Wage Deficit ($), ALICE Household Stress (%), Annual Basic Needs Budget, or Median Household Income.
- 🎛️ **Interactive Benefit-Cliff Simulator**: Model how incremental hourly wage gains ($15–$35/hr) interact with public subsidy thresholds (childcare, SNAP), exposing net resource drops.
- 👤 **Personal Household Reality Calculator**: Benchmark your household's income and family structure against your state's living wage, ALICE threshold, and national distribution.
- 📈 **Custom Time-Horizon Slider**: Filter 50 years of quarterly macro series (1975–2024) with dynamically normalized 2000=100 baseline indexing.
- 🛡️ **Zero-Crash Resilience**: Built-in HTTP validation and automated fallback data generation to guarantee 100% uptime on cloud environments.

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.9+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/a-better-ruler-dashboard.git
cd a-better-ruler-dashboard
