
# 🩺 AI Healthcare Assistant (Disease Prediction) — v2

**New in v2**
- **Hindi/English toggle** (i18n)
- **CSV & PDF report downloads**
- **Optional Email alert (SMTP)** when risk ≥ threshold
- Adds **CKD risk** model (along with Diabetes & Heart Disease)
- Keeps **dark mode** and **alert sound**

## Quick Start
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Email Alert Setup (optional)
Fill SMTP fields in the sidebar (host/port/user/pass, from, to). Uses STARTTLS on given port.

> ⚠️ Educational demo with synthetic data. Not a medical device or medical advice.
