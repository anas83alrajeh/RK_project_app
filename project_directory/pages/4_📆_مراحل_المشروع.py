import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="centered")

DATA_PATH = "data/project_phases.csv"
os.makedirs("data", exist_ok=True)

phase_names = [
    "تحديد الأرض 2 ",
    "المرحلة الثانية: استخراج التراخيص الرخص من البلدية والكهرباء والماء",
    "المرحلة الثالثة: التصميم الهندسي والمعماري (المخططات المعمارية والإنشائية والكهرباء)",
    "المرحلة الرابعة: أعمال الحفر (حفر القواعد، والقبو)",
    "المرحلة الخامسة: صب القواعد والأساسات (قواعد، رقاب، جدران قبو)",
    "المرحلة السادسة: صب الأعمدة والأسقف والجدران الحاملة (طوابق + أعمدة + جدران حاملة)",
    "المرحلة السابعة: إغلاق الهيكل بالجدران الداخلية والخارجية (بلوك داخلي وخارجي)",
    "المرحلة الثامنة: تأسيس كهرباء وسباكة (تمديدات أولية، تأسيس المواسير والكابلات)",
    "المرحلة التاسعة: تركيب المصعد والتأكد من الجاهزية (تجهيز البئر، التركيب، التشغيل)",
    "المرحلة العاشرة: إعداد تقرير التسليم (تقرير المهندس، الموافقة النهائية)"
]

phase_weights = [2, 3, 5, 8, 10, 25, 12, 10, 8, 2]

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

for idx, row in df.iterrows():
    key = f"done_{idx}"
    if key not in st.session_state:
        st.session_state[key] = row.get("تم التنفيذ", False)

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

completed_percent = 0
for i in range(len(df)):
    if st.session_state[f"done_{i}"]:
        completed_percent += phase_weights[i]

st.markdown(f"<h4 style='text-align: right; direction: rtl;'>🚀 نسبة إنجاز المشروع: {completed_percent}%</h4>", unsafe_allow_html=True)
st.progress(completed_percent / 100)

if st.button("💾 حفظ المراحل"):
    for i in range(len(df)):
        df.at[i, "تم التنفيذ"] = st.session_state[f"done_{i}"]
    save_data(df)
    st.success("✅ تم حفظ البيانات وتحديث نسبة الإنجاز.")

def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding="utf-8")

csv_data = convert_df_to_csv(df)

st.download_button(
    label="⬇️ تنزيل بيانات المشروع (CSV)",
    data=csv_data,
    file_name="project_phases.csv",
    mime="text/csv"
)
