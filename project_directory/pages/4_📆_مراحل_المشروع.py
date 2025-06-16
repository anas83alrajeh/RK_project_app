import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF

st.set_page_config(layout="centered")

DATA_PATH = "data/project_phases.csv"
os.makedirs("data", exist_ok=True)

phase_names = [
    "تحديد الأرض",
    "استخراج التراخيص",
    "التصميم الهندسي والمعماري",
    "أعمال الحفر",
    "صب القواعد والأساسات",
    "صب الأعمدة والأسقف والجدران الحاملة",
    "إغلاق الهيكل بالجدران الداخلية والخارجية",
    "كهرباء وسباكة",
    "تركيب المصعد والتأكد من الجاهزية",
    "إعداد تقرير التسليم"
]

default_phases = [
    {
        "رقم المرحلة": i + 1,
        "اسم المرحلة": name,
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": "",
        "تم التنفيذ": False
    } for i, name in enumerate(phase_names)
]

def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        if "تم التنفيذ" in df.columns:
            df["تم التنفيذ"] = df["تم التنفيذ"].astype(str).str.lower().isin(["true", "1"])
        else:
            df["تم التنفيذ"] = False
        if len(df) < 10:
            return pd.DataFrame(default_phases)
        return df
    else:
        return pd.DataFrame(default_phases)

def save_data(df):
    df.to_csv(DATA_PATH, index=False, encoding="utf-8")

def safe_to_date(value):
    try:
        if pd.isna(value) or value == "" or value is None:
            return None
        dt = pd.to_datetime(value)
        return dt.date()
    except Exception:
        return None

# دالة لتحويل DataFrame إلى ملف Excel في الذاكرة
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Project Phases')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

# دالة لتوليد ملف PDF يحتوي على جدول البيانات (نسخة مبسطة)
def to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "تقرير مراحل المشروع", ln=True, align='C')

    col_widths = [15, 50, 30, 30, 30, 30]  # عرض الأعمدة تقريبًا

    # رؤوس الأعمدة (بالعربي)
    headers = ["رقم", "اسم المرحلة", "تاريخ البدء", "تاريخ النهاية", "المدة الزمنية", "تم التنفيذ"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align='C')
    pdf.ln()

    # البيانات
    for idx, row in df.iterrows():
        pdf.cell(col_widths[0], 10, str(row["رقم المرحلة"]), border=1)
        pdf.cell(col_widths[1], 10, str(row["اسم المرحلة"]), border=1)
        pdf.cell(col_widths[2], 10, str(row["تاريخ البدء"]), border=1)
        pdf.cell(col_widths[3], 10, str(row["تاريخ النهاية"]), border=1)
        pdf.cell(col_widths[4], 10, str(row["المدة الزمنية"]), border=1)
        done_text = "نعم" if row["تم التنفيذ"] else "لا"
        pdf.cell(col_widths[5], 10, done_text, border=1)
        pdf.ln()

    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output

df = load_data()

# تنسيق RTL
st.markdown("""
<style>
    body, div, input, label, textarea, select, button {
        direction: rtl !important;
        text-align: right !important;
    }
    .phase-box {
        background-color: #f0f0f0;
        color: #000000;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        font-size: 14px;
        direction: rtl;
        text-align: right;
    }
    .phase-title {
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# تهيئة قيم الحالة داخل session_state إذا لم تكن موجودة
for idx, row in df.iterrows():
    key = f"done_{idx}"
    if key not in st.session_state:
        st.session_state[key] = row.get("تم التنفيذ", False)

# زر تحميل Excel و PDF في الأعلى
col_down1, col_down2 = st.columns(2)
with col_down1:
    excel_data = to_excel(df)
    st.download_button(
        label="⬇️ تحميل البيانات كملف Excel",
        data=excel_data,
        file_name="project_phases.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
with col_down2:
    pdf_data = to_pdf(df)
    st.download_button(
        label="⬇️ تحميل البيانات كملف PDF",
        data=pdf_data,
        file_name="project_phases.pdf",
        mime="application/pdf"
    )

# عرض مراحل المشروع مع تحديث القيمة مباشرة من session_state
for idx, row in df.iterrows():
    st.markdown(f'<div class="phase-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="phase-title">المرحلة {row["رقم المرحلة"]}: {row["اسم المرحلة"]}</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        df.at[idx, "تاريخ البدء"] = st.date_input(
            f"تاريخ البدء للمرحلة {row['رقم المرحلة']}",
            value=safe_to_date(row["تاريخ البدء"]),
            key=f"start_{idx}"
        )
    with col2:
        df.at[idx, "تاريخ النهاية"] = st.date_input(
            f"تاريخ النهاية للمرحلة {row['رقم المرحلة']}",
            value=safe_to_date(row["تاريخ النهاية"]),
            key=f"end_{idx}"
        )
    with col3:
        try:
            start = pd.to_datetime(df.at[idx, "تاريخ البدء"])
            end = pd.to_datetime(df.at[idx, "تاريخ النهاية"])
            if pd.notnull(start) and pd.notnull(end) and end >= start:
                duration = (end - start).days
                df.at[idx, "المدة الزمنية"] = duration
            else:
                df.at[idx, "المدة الزمنية"] = ""
        except Exception:
            df.at[idx, "المدة الزمنية"] = ""

        st.text_input(
            "المدة الزمنية (بالأيام)",
            value=str(df.at[idx, "المدة الزمنية"]),
            disabled=True,
            key=f"duration_{idx}"
        )

    done = st.checkbox("✅ تم التنفيذ", key=f"done_{idx}")
    df.at[idx, "تم التنفيذ"] = done

    st.markdown("</div>", unsafe_allow_html=True)

completed_count = sum([st.session_state[f"done_{i}"] for i in range(len(df))])
progress_percent = completed_count * 10

st.markdown(f"<h4 style='text-align: right; direction: rtl;'>🚀 نسبة إنجاز المشروع: {progress_percent}%</h4>", unsafe_allow_html=True)
st.progress(progress_percent / 100)

if st.button("💾 حفظ المراحل"):
    for i in range(len(df)):
        df.at[i, "تم التنفيذ"] = st.session_state[f"done_{i}"]
    save_data(df)
    st.success("✅ تم حفظ البيانات وتحديث نسبة الإنجاز.")
