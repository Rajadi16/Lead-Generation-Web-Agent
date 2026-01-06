# Scoring Methodology

## Overview

The Lead Generation Web Agent uses a multi-factor propensity scoring algorithm to rank potential leads from 0-100. The algorithm evaluates five key dimensions that indicate a prospect's likelihood to purchase 3D in-vitro models.

## Scoring Components

### 1. Role Fit Score (Max 30 points)

Evaluates how well the person's job title aligns with our target buyer personas.

**Keyword Matching:**
- "Toxicology" or "Toxicologist": 30 points
- "Safety": 30 points
- "Hepatic": 25 points
- "Liver": 25 points
- "3D": 30 points
- "In Vitro": 30 points

**Seniority Bonus:**
- Director/Head/VP: +20 points
- Principal: +16 points
- Scientist: +10 points

**Rationale:** Decision-makers in toxicology and safety assessment are primary buyers. Those working specifically with hepatic/liver models or already using 3D/in vitro methods are highly qualified.

**Example:**
- "Director of Toxicology" = 30 (toxicology) + 20 (director) = 50 points → capped at 30
- "Research Scientist" = 10 points

---

### 2. Company Intent Score (Max 20 points)

Measures the company's readiness to invest based on funding and grants.

**Funding Stage:**
- Series A/B (last 12 months): 20 points
- Series A/B (older): 10 points
- Series C+/IPO/Public: 15 points
- Bootstrapped: 5 points

**Grant Indicators:**
- NIH grant received: +15 points

**Rationale:** Recently funded companies (Series A/B) have capital to invest in new technologies. NIH grants indicate active research programs that may need advanced models.

**Example:**
- Series B funded 6 months ago + NIH grant = 20 + 15 = 35 → capped at 20
- Public company, no grants = 15 points

---

### 3. Technographic Signals (Max 25 points)

Identifies companies already using or interested in relevant technologies.

**Website/Content Analysis:**
- Mentions "3D models" or "3D cell culture": 15 points
- Mentions "NAMs" or "alternative methods": 10 points
- Focus on "liver disease" or "hepatology": 15 points
- Job postings for "in vitro models": 20 points

**Company Name Indicators:**
- Contains liver/hepat/organ/organoid/biotech: +5 points

**Rationale:** Companies already discussing these technologies are warm leads. Job postings indicate immediate need.

**Example:**
- Website mentions "3D models" and "NAMs" = 15 + 10 = 25 points
- No tech signals found = 0 points

---

### 4. Location Hub Score (Max 10 points)

Prioritizes leads in key biotech/pharma geographic clusters.

**Hub Scoring:**
- Boston/Cambridge, MA: 10 points
- San Francisco Bay Area: 10 points
- Basel, Switzerland: 10 points
- Cambridge/Oxford, UK: 10 points
- San Diego, CA: 8 points
- Other locations: 3 points

**Rationale:** These hubs have high concentrations of biotech/pharma companies and easier access for in-person meetings and support.

**Example:**
- Lead in Boston = 10 points
- Lead in Austin = 3 points

---

### 5. Scientific Intent Score (Max 40 points)

Evaluates active research and thought leadership in relevant areas.

**Publication Recency:**
- Published with DILI keywords (last 12 months): 40 points
- Published with DILI keywords (12-24 months): 25 points
- Published on 3D cell culture (last 24 months): 30 points

**Conference Activity:**
- Presenting at SOT/AACR/ISSX this year: 35 points

**Rationale:** Recent publications indicate active research programs. Conference presenters are thought leaders and early adopters.

**Example:**
- DILI paper in 2025 + SOT presenter = 40 + 35 = 75 → capped at 40
- No publications = 0 points

---

## Total Score Calculation

**Raw Score Formula:**
```
Raw Score = Role Fit + Company Intent + Technographic + Location + Scientific Intent
Max Raw Score = 30 + 20 + 25 + 10 + 40 = 125 points
```

**Normalization to 0-100:**
```
Final Score = (Raw Score / 125) × 100
```

**Lead Categories:**
- 🟢 **Hot Lead**: 80-100 points
- 🟡 **Warm Lead**: 50-79 points
- ⚪ **Cold Lead**: 0-49 points

---

## Example Calculations

### Example 1: Hot Lead (Score: 88/100)

**Profile:**
- Name: Dr. Jane Smith
- Title: Director of Toxicology
- Company: BioTech Innovations (Series B, funded 6 months ago)
- Location: Boston, MA
- Publications: 2 DILI papers in 2025, 1 on 3D hepatic spheroids
- Conference: SOT 2025 Speaker
- Website: Mentions "3D models" and "NAMs"

**Scoring:**
- Role Fit: 30 (toxicology + director, capped)
- Company Intent: 20 (Series B recent, capped)
- Technographic: 25 (3D models + NAMs, capped)
- Location: 10 (Boston)
- Scientific Intent: 40 (recent DILI pub, capped)

**Total:** (30+20+25+10+40)/125 × 100 = **88/100** 🟢

---

### Example 2: Warm Lead (Score: 56/100)

**Profile:**
- Name: Dr. John Doe
- Title: Research Scientist - In Vitro Models
- Company: Pharma Corp (Public)
- Location: San Diego, CA
- Publications: 1 paper on drug metabolism (2023)
- No conference activity
- No specific tech signals

**Scoring:**
- Role Fit: 30 (in vitro, capped)
- Company Intent: 15 (public company)
- Technographic: 0 (no signals)
- Location: 8 (San Diego)
- Scientific Intent: 25 (older publication)

**Total:** (30+15+0+8+17)/125 × 100 = **56/100** 🟡

---

### Example 3: Cold Lead (Score: 28/100)

**Profile:**
- Name: Dr. Alice Johnson
- Title: Postdoctoral Fellow
- Company: University Research Lab
- Location: Other
- Publications: None found
- No funding data
- No tech signals

**Scoring:**
- Role Fit: 10 (scientist level)
- Company Intent: 5 (bootstrapped/academic)
- Technographic: 0
- Location: 3 (other)
- Scientific Intent: 0

**Total:** (10+5+0+3+0)/125 × 100 = **14/100** ⚪

---

## Tuning Recommendations

### Increasing Precision (Fewer, Higher Quality Leads)
- Raise minimum score threshold to 70+
- Increase weight on Scientific Intent (publications)
- Require multiple factors to score

### Increasing Recall (More Leads, Broader Net)
- Lower minimum score threshold to 40+
- Increase weight on Role Fit
- Add bonus for any publication activity

### Industry-Specific Tuning
- **Pharma Focus**: Increase Company Intent weight
- **Academic Focus**: Increase Scientific Intent weight
- **Startup Focus**: Increase Technographic weight

---

## Validation Metrics

To validate scoring effectiveness, track:

1. **Conversion Rate by Score Band**
   - Hot leads → meeting rate
   - Warm leads → meeting rate
   - Cold leads → meeting rate

2. **Score Distribution**
   - Aim for normal distribution
   - Avoid clustering at extremes

3. **False Positives/Negatives**
   - High-scoring leads that don't convert
   - Low-scoring leads that do convert

Adjust weights based on actual conversion data.

---

## Implementation Notes

- Scores are calculated in `scoring/propensity_scorer.py`
- Weights are configurable in `config.py`
- Each component has a maximum cap to prevent over-weighting
- Normalization ensures scores are always 0-100 regardless of weight changes
