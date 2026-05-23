# Data Bakery by Hassan Absar

**Powered by STT Solutions**

Data Bakery is an ultra-modern Streamlit web application for generating realistic, intentionally dirty CSV datasets for Power BI learning, data cleaning practice, and meaningful visualization exercises.

Target deployment URL:

```text
databakerybyhassanabsarsttsolutions.streamlit.app
```

## Final Product Decisions Implemented

- Product name: **Data Bakery by Hassan Absar**
- Institutional engine: **STT Solutions**
- Support line: **Powered by STT Solutions**
- Web app framework: **Streamlit**
- Visual language: sharp-edged, Gen-Z-friendly, funky-professional, red/cyan/lime/violet on dark graphite
- Branding assets: Hassan Absar portrait/avatar and STT Solutions banner included in the UI and PDF headers
- Output delivery: downloadable ZIP package
- Dataset output: CSV only
- Documentation output: PDF only
- No JSON, Markdown, Excel, Parquet, SQLite, or database output in generated packages
- Row range: **500,000 to 550,000**
- Column recipe limit: **5 to 25**
- Dataset types: all 32 categories from the final PRD
- Files are generated in temporary session folders and cleanup utilities remove generated packages after download or session expiry

## Output Package

The downloaded ZIP contains:

```text
Data_Bakery_Output/
├── dataset.csv
├── data_dictionary.pdf
├── cleaning_challenges.pdf
├── suggested_powerbi_dashboard.pdf
└── generation_summary.pdf
```

For the **Relational Multi-Table Databases** dataset type, the package contains multiple CSV files plus the same PDF documentation set:

```text
Data_Bakery_Output/
├── customers.csv
├── products.csv
├── orders.csv
├── order_items.csv
├── payments.csv
├── data_dictionary.pdf
├── cleaning_challenges.pdf
├── suggested_powerbi_dashboard.pdf
└── generation_summary.pdf
```

## Local Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Streamlit Cloud Deployment

1. Push this repository to GitHub.
2. Create a Streamlit Community Cloud app from the GitHub repo.
3. Set the app file to `streamlit_app.py`.
4. Configure the custom subdomain as:

```text
databakerybyhassanabsarsttsolutions.streamlit.app
```

## Important Operational Note

Streamlit does not expose a guaranteed browser-level event confirming that a download has fully completed. The app therefore uses a practical cleanup model: generated files are stored temporarily, offered for immediate download, and removed through explicit cleanup actions plus automatic cleanup of stale temporary files.

For stronger production guarantees, deploy behind a production server with signed temporary download links and a job cleanup worker.

## Suggested Production Upgrade

For heavy classroom usage or concurrent generation, deploy the same app on a stronger host such as Cloud Run, Azure App Service, Render, Railway, DigitalOcean, or an STT-controlled VPS. Streamlit Community Cloud is excellent for demos and moderate use, but it is not ideal for high-concurrency large file generation.
