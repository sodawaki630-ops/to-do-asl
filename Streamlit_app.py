import streamlit as st
import pandas as pd
import json
from datetime import datetime as dt, date
from streamlit_sortable import sortable_grid
from fpdf import FPDF
import plotly.express as px

# ---------------- Config ----------------
st.set_page_config(page_title="To-Do Ultimate Pro", page_icon="📝", layout="wide")

# ---------------- Dark / Light Mode ----------------
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
if dark_mode:
    BG = "#2c2f33"
    CARD_BG = "#3b3f46"
    TEXT = "#e4e6eb"
    PROG_FILL = "#4caf50"
else:
    BG = "linear-gradient(120deg, #f6f9fc, #eef2f3)"
    CARD_BG = "#ffffff"
    TEXT = "#111"
    PROG_FILL = "#4caf50"

# ---------------- CSS Styling ----------------
st.markdown(f"""
<style>
body {{
    background: {BG};
    color: {TEXT};
    font-family: 'Segoe UI', sans-serif;
}}
.task-card {{
    background: {CARD_BG};
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}}
.task-card:hover {{
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}}
.task-card.new {{
    animation: slideFade 0.6s ease-out;
}}
.task-card.remove {{
    animation: slideOut 0.5s forwards;
}}
@keyframes slideFade {{
    0% {{opacity:0; transform: translateX(40px);}}
    100% {{opacity:1; transform: translateX(0);}}
}}
@keyframes slideOut {{
    0% {{opacity:1; transform: translateX(0);}}
    100% {{opacity:0; transform: translateX(50px);}}
}}
.deadline-text {{
    color: #ff4b4b;
    font-weight: 600;
}}
.progress-bar {{
    height: 10px;
    width: 100%;
    background: #e5e5e5;
    border-radius: 10px;
}}
.progress-fill {{
    height: 10px;
    background: {PROG_FILL};
    border-radius: 10px;
}}
.popup {{
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4caf50;
    color: white;
    padding: 14px 22px;
    border-radius: 10px;
    opacity: 0;
    transform: translateY(-20px);
    animation: popupShow 0.4s forwards, popupFade 0.4s 2.4s forwards;
    z-index: 9999;
}}
@keyframes popupShow {{
    from {{ opacity: 0; transform: translateY(-20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes popupFade {{
    from {{ opacity: 1; }}
    to {{ opacity: 0; transform: translateY(-20px); }}
}}
button:hover {{
    transform: scale(1.1);
    transition: transform 0.2s;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ---------------- Title ----------------
st.title("📝 To-Do Ultimate Pro")

# ---------------- Sidebar ----------------
st.sidebar.header("📤 Export / Import / Filter")
with st.sidebar.expander("แชร์ / นำเข้า JSON"):
    exported = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
    st.code(exported, language='json')
    uploaded = st.file_uploader("อัปโหลด JSON เพื่อโหลดงานใหม่", type=['json'])
    if uploaded:
        try:
            data = json.load(uploaded)
            st.session_state.tasks = data
            st.success("โหลดงานจาก JSON เรียบร้อย!")
        except:
            st.error("ไฟล์ JSON ไม่ถูกต้อง")

# Export PDF / Excel / CSV
st.sidebar.markdown("---")
if st.sidebar.button("Export → PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for t in st.session_state.tasks:
        pdf.cell(0, 8, f"{t.get('name')} | {t.get('deadline')} | {t.get('category','-')} | {t.get('progress',0)}%", ln=True)
    pdf.output("todo_report.pdf")
    st.success("Exported todo_report.pdf")
if st.sidebar.button("Export → Excel"):
    df = pd.DataFrame(st.session_state.tasks)
    df.to_excel("todo_export.xlsx", index=False)
    st.success("Exported todo_export.xlsx")
if st.sidebar.button("Export → CSV"):
    df = pd.DataFrame(st.session_state.tasks)
    df.to_csv("todo_export.csv", index=False)
    st.success("Exported todo_export.csv")

# Filter
filter_done = st.sidebar.selectbox("แสดงงาน:", options=["ทั้งหมด","งานที่ยังไม่เสร็จ","งานที่เสร็จแล้ว"])
filter_category = st.sidebar.text_input("Filter หมวดหมู่ (ใส่ชื่อ)")

# ---------------- Add Task ----------------
st.header("➕ เพิ่มงานใหม่")
with st.form("form_new_task", clear_on_submit=True):
    name = st.text_input("ชื่องาน")
    deadline = st.date_input("เดดไลน์", value=date.today())
    category = st.text_input("หมวดหมู่")
    progress = st.slider("ความคืบหน้า (%)", 0, 100, 0)
    submitted = st.form_submit_button("เพิ่มงาน")
    if submitted and name.strip() != "":
        st.session_state.tasks.append({
            "name": name,
            "deadline": str(deadline),
            "category": category.strip(),
            "progress": progress,
            "completed": False,
            "new": True,
            "remove": False
        })
        st.markdown("<div class='popup'>เพิ่มงานสำเร็จ! 🎉</div>", unsafe_allow_html=True)

# ---------------- Task List ----------------
st.header("📋 รายการงาน (ลากเพื่อจัดลำดับ)")

tasks_list = st.session_state.tasks.copy()
# Filter by status / category
if filter_done=="งานที่ยังไม่เสร็จ":
    tasks_list = [t for t in tasks_list if not t.get("completed")]
elif filter_done=="งานที่เสร็จแล้ว":
    tasks_list = [t for t in tasks_list if t.get("completed")]
if filter_category:
    tasks_list = [t for t in tasks_list if t.get("category") == filter_category]

new_order = sortable_grid(tasks_list, key="sortable-1")
if new_order:
    st.session_state.tasks = new_order

today = dt.now().date()
for i, task in enumerate(st.session_state.tasks):
    # Skip if filtered
    if filter_done=="งานที่ยังไม่เสร็จ" and task.get("completed"): continue
    if filter_done=="งานที่เสร็จแล้ว" and not task.get("completed"): continue
    if filter_category and task.get("category") != filter_category: continue

    card_class = "task-card new" if task.get("new") else "task-card"
    if task.get("remove"):
        card_class += " remove"
    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
    col1, col2 = st.columns([6,1])
    with col1:
        st.markdown(f"### {task.get('name')}")
        st.markdown(f"🗓 <span class='deadline-text'>{task.get('deadline')}</span>", unsafe_allow_html=True)
        if task.get("category"):
            st.markdown(f"📂 {task.get('category')}")
        st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width:{task.get('progress',0)}%"></div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("✔", key=f"done_{i}"):
            task["completed"] = True
            st.session_state.tasks[i] = task
            st.success("✅ ทำเสร็จแล้ว")
        if st.button("🗑", key=f"del_{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()
    task["new"] = False
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Calendar ----------------
st.header("📅 ปฏิทินงาน")
select_date = st.date_input("เลือกวัน", value=today)
st.subheader(f"งานวันที่ {select_date}")
day_tasks = [t for t in st.session_state.tasks if t.get("deadline")==str(select_date)]
if day_tasks:
    for t in day_tasks:
        st.write(f"- {t.get('name')} ({t.get('category','-')}, ความคืบหน้า {t.get('progress',0)}%)")
else:
    st.info("ไม่พบงาน")

# ---------------- Dashboard Charts ----------------
st.header("📊 Dashboard สรุปงาน")
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    df['completed'] = df['completed'].apply(lambda x: 1 if x else 0)
    fig = px.pie(df, names='category', values='progress', title="ความคืบหน้าแยกตามหมวดหมู่")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Summary ----------------
total = len(st.session_state.tasks)
done = sum(1 for t in st.session_state.tasks if t.get("completed"))
if total>0:
    st.progress(done/total)
    st.write(f"✔ เสร็จแล้ว {done} / {total} งาน")
else:
    st.write("ยังไม่มีงาน")
