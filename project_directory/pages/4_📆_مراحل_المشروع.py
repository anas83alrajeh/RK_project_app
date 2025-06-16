import streamlit as st
import pandas as pd
import os

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

    # هنا checkbox مع ربطه بالـ session_state للتحديث الفوري
    done = st.checkbox("✅ تم التنفيذ", key=f"done_{idx}")
    df.at[idx, "تم التنفيذ"] = done

    st.markdown("</div>", unsafe_allow_html=True)

# حساب نسبة الإنجاز بناءً على checkboxes مباشرة
completed_count = sum([st.session_state[f"done_{i}"] for i in range(len(df))])
progress_percent = completed_count * 10

# عرض نسبة الإنجاز أعلى الصفحة
st.markdown(f"<h4 style='text-align: right; direction: rtl;'>🚀 نسبة إنجاز المشروع: {progress_percent}%</h4>", unsafe_allow_html=True)
st.progress(progress_percent / 100)

# زر حفظ البيانات فقط
if st.button("💾 حفظ المراحل"):
    # تحديث عمود تم التنفيذ في df من session_state قبل الحفظ
    for i in range(len(df)):
        df.at[i, "تم التنفيذ"] = st.session_state[f"done_{i}"]
    save_data(df)
    st.success("✅ تم حفظ البيانات وتحديث نسبة الإنجاز.")

import io

# ... باقي كودك كما هو ...

# تحويل DataFrame إلى CSV داخل ذاكرة وليس ملف
def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding="utf-8")

csv_data = convert_df_to_csv(df)

# زر تحميل ملف CSV
st.download_button(
    label="⬇️ تنزيل بيانات المشروع (CSV)",
    data=csv_data,
    file_name="project_phases.csv",
    mime="text/csv"
)

