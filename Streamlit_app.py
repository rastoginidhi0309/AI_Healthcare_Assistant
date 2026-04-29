import streamlit as st
from models import train_models, predict_proba, FEATURES
import pathlib, pandas as pd, smtplib, os
from email.mime.text import MIMEText
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
from datetime import timezone      # streamlit run Streamlit_app.py
import io
import base64

st.set_page_config(page_title="AI Healthcare Assistant", page_icon="🩺", layout="centered")

# ---------------- Local Audio Alert Function ----------------
def autoplay_audio(file_path: str):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Could not play alert sound: {e}")

# ---------------- Language dictionary ----------------
LANGS = {"en": "English", "hi": "हिन्दी"}
T = {
    "title": {"en": "AI Healthcare Assistant", "hi": "एआई हेल्थकेयर असिस्टेंट"},
    "caption": {
        "en": "Educational demo for disease risk screening (Diabetes, Heart Disease, CKD). Not medical advice.",
        "hi": "यह एक शैक्षिक डेमो है जो (डायबिटीज, हृदय रोग, सीकेडी) के जोखिम की स्क्रीनिंग दिखाता है। यह चिकित्सा सलाह नहीं है।"
    },
    "settings": {"en": "Settings", "hi": "सेटिंग्स"},
    "threshold": {"en": "Alert threshold", "hi": "अलर्ट थ्रेशहोल्ड"},
    "darknote": {"en": "Dark mode is enabled in theme config.", "hi": "डार्क मोड थीम कॉन्फ़िग में सक्षम है।"},
    "smtp": {"en": "Email Alert (optional SMTP)", "hi": "ईमेल अलर्ट (वैकल्पिक SMTP)"},
    "smtp_help": {"en": "Fill to send email when risk ≥ threshold.", "hi": "जब जोखिम ≥ थ्रेशहोल्ड हो तो ईमेल भेजने के लिए भरें।"},
    "email_to": {"en": "Send To (email)", "hi": "प्राप्तकर्ता (ईमेल)"},
    "email_from": {"en": "From (email)", "hi": "प्रेषक (ईमेल)"},
    "smtp_host": {"en": "SMTP Host", "hi": "SMTP होस्ट"},
    "smtp_port": {"en": "SMTP Port", "hi": "SMTP पोर्ट"},
    "smtp_user": {"en": "SMTP User", "hi": "SMTP उपयोगकर्ता"},
    "smtp_pass": {"en": "SMTP Password", "hi": "SMTP पासवर्ड"},
    "metrics": {"en": "Enter Patient Metrics", "hi": "रोगी मेट्रिक्स दर्ज करें"},
    "age": {"en": "Age (years)", "hi": "उम्र (वर्ष)"},
    "bmi": {"en": "BMI (kg/m²)", "hi": "बीएमआई (किग्रा/मी²)"},
    "glucose": {"en": "Fasting Glucose (mg/dL)", "hi": "फास्टिंग ग्लूकोज़ (mg/dL)"},
    "smoker": {"en": "Smoker", "hi": "धूम्रपान करने वाला"},
    "yes": {"en": "Yes", "hi": "हाँ"},
    "no": {"en": "No", "hi": "नहीं"},
    "sys_bp": {"en": "Systolic BP (mmHg)", "hi": "सिस्टोलिक BP (mmHg)"},
    "chol": {"en": "Total Cholesterol (mg/dL)", "hi": "कुल कोलेस्ट्रॉल (mg/dL)"},
    "steps": {"en": "Daily Steps (thousands)", "hi": "दैनिक कदम (हज़ार)"},
    "predict": {"en": "Predict Risk", "hi": "जोखिम का अनुमान"},
    "results": {"en": "Results", "hi": "परिणाम"},
    "diabetes": {"en": "Diabetes Risk", "hi": "डायबिटीज जोखिम"},
    "heart": {"en": "Heart Disease Risk", "hi": "हृदय रोग जोखिम"},
    "ckd": {"en": "CKD Risk", "hi": "सीकेडी जोखिम"},
    "alert_triggered": {"en": "Alert triggered: One or more risks exceed the threshold.", "hi": "अलर्ट चालू: एक या अधिक जोखिम थ्रेशहोल्ड से अधिक हैं।"},
    "no_alert": {"en": "No alerts triggered. Risks below threshold.", "hi": "कोई अलर्ट नहीं। जोखिम थ्रेशहोल्ड से कम हैं।"},
    "download": {"en": "Download Report", "hi": "रिपोर्ट डाउनलोड करें"},
    "csv": {"en": "CSV Summary", "hi": "CSV सारांश"},
    "pdf": {"en": "PDF Report", "hi": "PDF रिपोर्ट"},
    "about": {"en": "About this App", "hi": "ऐप के बारे में"},
    "about_text": {
        "en": "This is an educational prototype demonstrating screening for potential health risks using synthetic data. Not a medical device.",
        "hi": "यह एक शैक्षिक प्रोटोटाइप है जो सिंथेटिक डेटा का उपयोग करके संभावित स्वास्थ्य जोखिमों की स्क्रीनिंग दिखाता है। यह कोई चिकित्सीय उपकरण नहीं है।"
    }
}

def tr(key, lang):
    return T.get(key, {}).get(lang, key)

# ---------------- Sidebar settings ----------------
lang = st.sidebar.selectbox("Language / भाषा", list(LANGS.keys()), format_func=lambda k: LANGS[k])

st.title("🩺 " + tr("title", lang))
st.caption(tr("caption", lang))

with st.sidebar:
    st.header(tr("settings", lang))
    threshold = st.slider(tr("threshold", lang), 0.5, 0.95, 0.7, 0.01)
    st.markdown("---")
    st.subheader(tr("smtp", lang))
    st.caption(tr("smtp_help", lang))
    email_to = st.text_input(tr("email_to", lang), value="")
    email_from = st.text_input(tr("email_from", lang), value="")
    smtp_host = st.text_input(tr("smtp_host", lang), value="")
    smtp_port = st.number_input(tr("smtp_port", lang), 1, 65535, 587)
    smtp_user = st.text_input(tr("smtp_user", lang), value="")
    smtp_pass = st.text_input(tr("smtp_pass", lang), type="password", value="")
    st.markdown("---")
    st.markdown(tr("darknote", lang))

# ---------------- Patient Inputs ----------------
st.subheader(tr("metrics", lang))
col1, col2 = st.columns(2)
with col1:
    age = st.number_input(tr("age", lang), 18, 100, 35)
    bmi = st.number_input(tr("bmi", lang), 10.0, 60.0, 24.0, step=0.1)
    glucose = st.number_input(tr("glucose", lang), 60, 300, 95)
    smoker = st.selectbox(tr("smoker", lang), [tr("no", lang), tr("yes", lang)])
with col2:
    sys_bp = st.number_input(tr("sys_bp", lang), 80, 240, 120)
    chol = st.number_input(tr("chol", lang), 100, 400, 180)
    steps = st.number_input(tr("steps", lang), 0.0, 30.0, 5.0, step=0.1)

from datetime import timezone

# ---------------- Prediction ----------------
if st.button(tr("predict", lang), use_container_width=True):
    models = train_models()
    
    # Define features dictionary
    features = {
        "age": age,
        "bmi": bmi,
        "glucose": glucose,
        "sys_bp": sys_bp,
        "chol": chol,
        "smoker": 1 if smoker == tr("yes", lang) else 0,
        "steps": steps
    }
    
    # Get predicted probabilities
    probs = predict_proba(models, features)
    diab, heart, ckd = probs["diabetes"], probs["heart"], probs["ckd"]

    # Risk badge function
    def risk_badge(p):
        if p >= 0.80:
            style = "background-color:#ef4444; color:white; padding:6px 10px; border-radius:999px;"
            label = "High" if lang=="en" else "उच्च"
        elif p >= 0.50:
            style = "background-color:#f59e0b; color:black; padding:6px 10px; border-radius:999px;"
            label = "Moderate" if lang=="en" else "मध्यम"
        else:
            style = "background-color:#22c55e; color:black; padding:6px 10px; border-radius:999px;"
            label = "Low" if lang=="en" else "निम्न"
        return f"<span style='{style}'>{label}</span>"

        # Display results
    st.markdown("### " + tr("results", lang))
    st.markdown(f"**{tr('diabetes', lang)}:** {diab:.2%} {risk_badge(diab)}", unsafe_allow_html=True)
    st.markdown(f"**{tr('heart', lang)}:** {heart:.2%} {risk_badge(heart)}", unsafe_allow_html=True)
    st.markdown(f"**{tr('ckd', lang)}:** {ckd:.2%} {risk_badge(ckd)}", unsafe_allow_html=True)

    
    # ---------------- Alert Check ----------------
    if diab >= threshold or heart >= threshold or ckd >= threshold:
        st.error(tr("alert_triggered", lang))

        # 🔊 Play alert sound (embed base64 or online link)
        st.markdown(
            """
            <audio autoplay>
                <source src="https://www.soundjay.com/button/sounds/beep-07.mp3" type="audio/mpeg">
            </audio>
            """,
            unsafe_allow_html=True
        )
    else:
        st.success(tr("no_alert", lang))


    # ---------------- Downloads ----------------
    df = pd.DataFrame([{
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "age": age, "bmi": bmi, "glucose": glucose,
        "sys_bp": sys_bp, "chol": chol,
        "smoker": tr("yes", lang) if features["smoker"] else tr("no", lang),
        "steps": steps,
        "diabetes_prob": diab, "heart_prob": heart, "ckd_prob": ckd,
        "threshold": threshold
    }])
    st.download_button(tr("csv", lang), df.to_csv(index=False).encode("utf-8"),
                       file_name="risk_summary.csv", mime="text/csv")

    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=A4)
    w, h = A4
    y = h - 50
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "AI Healthcare Assistant — Risk Report")
    y -= 20
    c.setFont("Helvetica", 10)
    lines = [
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"Age: {age}    BMI: {bmi}    Steps(k): {steps}",
        f"Glucose: {glucose} mg/dL   Systolic BP: {sys_bp} mmHg   Chol: {chol} mg/dL   Smoker: {tr('yes', lang) if features['smoker'] else tr('no', lang)}",
        f"Diabetes Risk: {diab:.1%}",
        f"Heart Disease Risk: {heart:.1%}",
        f"CKD Risk: {ckd:.1%}",
        f"Alert Threshold: {threshold}"
    ]
    for line in lines:
        y -= 18
        c.drawString(40, y, line)
    c.showPage()
    c.save()
    pdf_buf.seek(0)
    st.download_button(tr("pdf", lang), pdf_buf, file_name="risk_report.pdf", mime="application/pdf")

# ---------------- About ----------------
st.markdown("---")
with st.expander(tr("about", lang)):
    st.write(tr("about_text", lang))
