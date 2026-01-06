# Deployment Guide for Lead Generation Web Agent

## Quick Start - Deploy to Streamlit Cloud

### Step 1: Push to GitHub

1. Create a new repository on GitHub: https://github.com/new
   - Name: `lead-generation-agent`
   - Description: "Intelligent lead generation and ranking system for 3D in-vitro models"
   - Make it Public

2. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/lead-generation-agent.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `lead-generation-agent`
5. Main file path: `app.py`
6. Click "Deploy"

Your app will be live at: `https://YOUR-APP-NAME.streamlit.app/`

### Step 3: Share the Demo

Send email to akash@euprime.org with:
- GitHub repository link
- Live Streamlit app link
- Google Sheets link (upload `lead_generation_output.xlsx` to Google Drive)

---

## What's Included

✅ **1,217 Leads** from PubMed
✅ **Propensity Scoring** (0-100 scale)
✅ **Interactive Dashboard** with filters
✅ **Excel Export** ready for Google Sheets

---

## Current Implementation

**Stage 1 - Identification:**
- ✅ PubMed scraping for researchers in toxicology, 3D cell culture, liver disease
- ❌ LinkedIn Sales Navigator (planned)
- ❌ Conference lists (planned)

**Stage 2 - Enrichment:**
- ✅ Email generation
- ✅ Company/location extraction
- ❌ Email verification APIs (planned)

**Stage 3 - Ranking:**
- ✅ Full 5-factor propensity scoring
- ✅ Hot/Warm/Cold categorization

This is a working MVP demonstrating the core concept with room for enhancement.
