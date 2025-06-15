import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="centered")
st.title("🗓️ مراحل إنجاز المشروع")

DATA_PATH = "data/project_phases.csv"
os.makedirs("data", exist_ok=True)

# جدول المراحل مع الأعمدة التي سيدخلها المستخدم
default_phases = [
    {
        "رقم المرحلة": 1,
        "اسم المرحلة": "التحضير والتخطيط",
        "الوصف": "تحديد الأرض، استخراج التراخيص، التصميم الهندسي والمعماري",
        "المهام المرتبطة بالمرحلة": "- رفع المساحة- استخراج رخصة البناء- تصميم مخططات",
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": ""
    },
    {
        "رقم المرحلة": 2,
        "اسم المرحلة": "الحفر والأساسات",
        "الوصف": "أعمال الحفر وصب القواعد والأساسات",
        "المهام المرتبطة بالمرحلة": "- أعمال الحفر- صب القواعد- العزل الأرضي",
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": ""
    },
    {
        "رقم المرحلة": 3,
        "اسم المرحلة": "الهيكل الإنشائي (الخرسانة)",
        "الوصف": "صب الأعمدة والأسقف والجدران الحاملة",
        "المهام المرتبطة بالمرحلة": "- صب الأعمدة- صب السقف الأول- بناء الجدران",
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": ""
    },
    {
        "رقم المرحلة": 4,
        "اسم المرحلة": "البناء بالطوب والبلوك",
        "الوصف": "إغلاق الهيكل بالجدران الداخلية والخارجية",
        "المهام المرتبطة بالمرحلة": "- بناء الحوائط- تجهيز الفتحات للنوافذ والأبواب",
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": ""
    },
    {
        "رقم المرحلة": 5,
        "اسم المرحلة": "التمديدات الأولية",
        "الوصف": "كهرباء وسباكة وتكييف قبل التشطيبات",
        "المهام المرتبطة بالمرحلة": "- تمديد كهرباء- تمديد صرف صحي ومياه- تكييف",
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": ""
    },
    {
        "رقم المرحلة": 6,
        "اسم المرحلة": "التشطيبات الخارجية",
        "الوصف": "واجهات، عزل، دهان خارجي، بوابات",
        "المهام المرتبطة بالمرحلة": "- دهان الواجهات- تركيب الإنارة الخارجية",
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": ""
    },
    {
        "رقم المرحلة": 7,
        "اسم المرحلة": "الاختبارات والتسليم",
        "الوصف": "فحص الأنظمة، التأكد من الجاهزية، إعداد تقرير التسليم",
        "المهام المرتبطة بالمرحلة": "- فحص الكهرباء- فحص المياه- تنظيف وتسليم",
        "تاريخ البدء": "",
        "تاريخ النهاية": "",
        "المدة الزمنية": ""
    }
]

def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(default_phases)

def save_data(df):
    df.to_csv(DATA_PATH, index=False, encoding="utf-8")

df = load_data()

# عرض الجدول مع الإدخال للمستخدم فقط في تواريخ البداية والنهاية
st.markdown(
    """
    <style>
        .phase-box {
            background-color: #e0e0e0;
            color: #000000;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            font-size: 14px;
            direction: ltr;
            text-align: left;
        }
        .phase-title {
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

for idx, row in df.iterrows():
    st.markdown(f'<div class="phase-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="phase-title">المرحلة {row["رقم المرحلة"]}: {row["اسم المرحلة"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<b>الوصف:</b> {row['الوصف']}<br><b>المهام المرتبطة:</b> {row['المهام المرتبطة بالمرحلة']}", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        df.at[idx, "تاريخ البدء"] = st.date_input(f"تاريخ البدء للمرحلة {row['رقم المرحلة']}", 
                                                 value=pd.to_datetime(row["تاريخ البدء"]) if row["تاريخ البدء"] else None,
                                                 key=f"start_{idx}")
    with col2:
        df.at[idx, "تاريخ النهاية"] = st.date_input(f"تاريخ النهاية للمرحلة {row['رقم المرحلة']}", 
                                                    value=pd.to_datetime(row["تاريخ النهاية"]) if row["تاريخ النهاية"] else None,
                                                    key=f"end_{idx}")
    with col3:
        # حساب المدة تلقائياً
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
        st.text_input(f"المدة الزمنية (بالأيام)", value=str(df.at[idx, "المدة الزمنية"]), disabled=True, key=f"duration_{idx}")

    st.markdown("</div>", unsafe_allow_html=True)

if st.button("💾 حفظ المراحل"):
    save_data(df)
    st.success("تم حفظ البيانات بنجاح.")
