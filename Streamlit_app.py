import streamlit as st
import json
from datetime import datetime as dt, date
import pandas as pd
import plotly.express as px
import pdfkit
import base64

# -------------------- Config --------------------
st.set_page_config(page_title="Ultimate Mobile To-Do App", page_icon="📝", layout="wide")

# -------------------- Dark Mode --------------------
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
if dark_mode:
    BG = "#1c1c1c"
    CARD_BG = "#2c2f33"
    TEXT = "#e4e6eb"
    PROG_FILL = "#4caf50"
else:
    BG = "linear-gradient(120deg, #f6f9fc, #eef2f3)"
    CARD_BG = "white"
    TEXT = "#111"
    PROG_FILL = "#4caf50"

# -------------------- CSS --------------------
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
    border-radius: 18px;
    margin-bottom: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}}
.task-card:hover {{
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
}}
.task-card.new {{
    animation: slideFade 0.7s ease-out;
}}
@keyframes slideFade {{
    0% {{opacity: 0; transform: translateX(50px);}}
    100% {{opacity: 1; transform: translateX(0);}}
}}
.priority-high {{background-color:#ff4b4b; color:white;}}
.priority-medium {{background-color:#ffffff; color:black;}}
.priority-low {{background-color:#111; color:white;}}
.deadline-text {{font-weight: 600;}}
.progress-bar {{height: 10px; border-radius: 10px; background: #e5e5e5;}}
.progress-fill {{height: 10px; border-radius: 10px; background: {PROG_FILL};}}
.popup {{
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 25px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    opacity: 0;
    transform: translateY(-20px);
    animation: popupShow 0.5s forwards, popupFadeOut 0.5s 2.5s forwards;
    z-index:999;
}}
@keyframes popupShow {{
    from {{opacity: 0; transform: translateY(-20px);}}
    to {{opacity: 1; transform: translateY(0);}}
}}
@keyframes popupFadeOut {{
    from {{opacity:1;}}
    to {{opacity:0; transform: translateY(-20px);}}
}}
button:hover {{
    transform: scale(1.1);
    transition: transform 0.2s;
}}
</style>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "sound_played" not in st.session_state:
    st.session_state.sound_played = set()

# -------------------- Title --------------------
st.title("📝 Ultimate Mobile To-Do App")

# -------------------- Add Task --------------------
st.subheader("➕ เพิ่มงานใหม่")
col1, col2, col3, col4 = st.columns([3,3,3,3])
with col1:
    task_name = st.text_input("ชื่องาน")
with col2:
    deadline = st.date_input("เดดไลน์", value=date.today())
with col3:
    category = st.text_input("หมวดหมู่")
with col4:
    priority = st.selectbox("Priority", ["High","Medium","Low"])
num_sub = st.number_input("จำนวนงานย่อย", min_value=0, max_value=10, value=0, step=1)

subtasks = []
for i in range(num_sub):
    sub_name = st.text_input(f"งานย่อย {i+1} ชื่อ", key=f"sub{i}")
    subtasks.append({"name": sub_name, "completed": False})

if st.button("เพิ่มงาน"):
    st.session_state.tasks.append({
        "name": task_name,
        "deadline": str(deadline),
        "category": category.strip(),
        "priority": priority,
        "subtasks": subtasks,
        "completed": False,
        "new": True
    })
    st.markdown("<div class='popup'>เพิ่มงานสำเร็จ! 🎉</div>", unsafe_allow_html=True)

# -------------------- Filter --------------------
st.subheader("🔎 กรองงาน")
filter_category = st.text_input("กรองตามหมวดหมู่")
filter_priority = st.selectbox("กรองตาม Priority", ["All","High","Medium","Low"])

# -------------------- Progress Summary --------------------
total = len(st.session_state.tasks)
done = sum(1 for t in st.session_state.tasks if t["completed"])
if total > 0:
    st.progress(done / total)
    st.write(f"✔ งานเสร็จแล้ว {done}/{total} งาน")
else:
    st.write("ยังไม่มีงาน")

# -------------------- Show Tasks --------------------
st.subheader("📌 รายการงาน")
today = dt.now().date()
for i, task in enumerate(st.session_state.tasks):
    if filter_category and task["category"] != filter_category:
        continue
    if filter_priority != "All" and task["priority"] != filter_priority:
        continue

    # Progress จากงานย่อย
    if task["subtasks"]:
        completed_sub = sum(1 for s in task["subtasks"] if s["completed"])
        progress = int(completed_sub / len(task["subtasks"]) * 100)
    else:
        progress = 0 if not task["completed"] else 100

    # Priority color
    if task["priority"]=="High":
        card_class = "task-card new priority-high"
    elif task["priority"]=="Medium":
        card_class = "task-card new priority-medium"
    else:
        card_class = "task-card new priority-low"

    st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)

    colA, colB = st.columns([6,1])
    with colA:
        st.markdown(f"### {task['name']}")
        st.markdown(f"🗓 เดดไลน์: <span class='deadline-text'>{task['deadline']}</span>", unsafe_allow_html=True)
        if task["category"]:
            st.markdown(f"📂 หมวดหมู่: {task['category']}")
        st.markdown(f"🔹 Priority: {task['priority']}")
        st.markdown("ความคืบหน้า:")
        st.markdown(
            f"<div class='progress-bar'><div class='progress-fill' style='width:{progress}%'></div></div>",
            unsafe_allow_html=True
        )

        # Sub-task
        if task["subtasks"]:
            st.markdown("**งานย่อย:**")
            for j, sub in enumerate(task["subtasks"]):
                col1, col2 = st.columns([8,2])
                with col1:
                    st.write(sub["name"])
                with col2:
                    if st.checkbox("✔", key=f"{i}_sub_{j}", value=sub["completed"]):
                        sub["completed"] = True
                    else:
                        sub["completed"] = False

        # แจ้งเตือนเสียง
        deadline_date = dt.strptime(task["deadline"], "%Y-%m-%d").date()
        remaining_days = (deadline_date - today).days
        if remaining_days <= 1 and not task["completed"] and task["name"] not in st.session_state.sound_played:
            st.audio("https://upload.wikimedia.org/wikipedia/commons/c/cf/Alert-tone.mp3")
            st.warning(f"⏰ งานนี้ใกล้ถึงเดดไลน์แล้ว!")
            st.session_state.sound_played.add(task["name"])

    with colB:
        if st.button("✔", key=f"done{i}"):
            for sub in task["subtasks"]:
                sub["completed"] = True
            task["completed"] = True
            st.success("งานเสร็จแล้ว!")
        st.write(" ")
        if st.button("🗑", key=f"delete{i}"):
            st.session_state.tasks.pop(i)
            st.rerun()

    task["new"] = False
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Calendar --------------------
st.subheader("📅 ปฏิทินงาน")
calendar_date = st.date_input("เลือกวันที่เพื่อดูงานของวันนั้น", value=today)
day_tasks = [t for t in st.session_state.tasks if t["deadline"] == str(calendar_date)]
if day_tasks:
    st.write("งานของวันนั้น:")
    for t in day_tasks:
        st.write(f"- {t['name']} (หมวดหมู่: {t['category']}, ความคืบหน้า: {progress}%)")
else:
    st.info("ไม่มีงานในวันนี้")

# -------------------- Dashboard --------------------
st.subheader("📊 Dashboard สรุปงาน")
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    progress_list = []
    for idx, task in df.iterrows():
        subs = task["subtasks"]
        if subs:
            completed_sub = sum(1 for s in subs if s["completed"])
            progress = int(completed_sub / len(subs) * 100)
        else:
            progress = 100 if task["completed"] else 0
        progress_list.append(progress)
    df["Progress"] = progress_list
    df["Completed"] = df["Progress"]==100

    # Pie Chart
    pie_fig = px.pie(df, names="Completed", title="งานเสร็จ/งานคงเหลือ")
    st.plotly_chart(pie_fig, use_container_width=True)

    # Bar Chart Category
    if df["category"].notnull().any():
        cat_count = df.groupby("category")["name"].count().reset_index()
        bar_fig = px.bar(cat_count, x="category", y="name", title="จำนวนงานตาม Category", text="name")
        st.plotly_chart(bar_fig, use_container_width=True)

    # Export Excel
    excel_file = "tasks_export.xlsx"
    df_export = df.drop(columns=["subtasks","new"])
    df_export.to_excel(excel_file, index=False)
    with open(excel_file, "rb") as f:
        st.download_button("📥 Export Excel", f, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("ยังไม่มีงานเพื่อแสดง Dashboard")

# -------------------- Heatmap Calendar --------------------
st.subheader("📅 Heatmap Calendar")
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    df['count'] = 1
    heatmap_data = df.groupby('deadline')['count'].sum().reset_index()
    heatmap_data['deadline'] = pd.to_datetime(heatmap_data['deadline'])
    heatmap_fig = px.density_heatmap(
        heatmap_data,
        x=heatmap_data['deadline'].dt.day,
        y=heatmap_data['deadline'].dt.month,
        z='count',
        labels={'x':'Day','y':'Month','z':'จำนวนงาน'},
        title="จำนวนงานต่อวัน (Heatmap)"
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)
else:
    st.info("ยังไม่มีงานสำหรับ Heatmap Calendar")

# -------------------- Export PDF --------------------
st.subheader("📄 Export PDF รายงาน")

def generate_html_pdf(tasks):
    html = f"<h1>รายงานงาน To-Do App</h1><ul>"
    for t in tasks:
        html += f"<li><b>{t['name']}</b> (เดดไลน์: {t['deadline']}, Category: {t['category']}, Priority: {t['priority']}, Progress: "
        if t['subtasks']:
            completed_sub = sum(1 for s in t['subtasks'] if s["completed"])
            progress = int(completed_sub / len(t['subtasks']) * 100)
        else:
            progress = 100 if t['completed'] else 0
        html += f"{progress}%)<ul>"
        for sub in t['subtasks']:
            html += f"<li>{sub['name']} - {'✔' if sub['completed'] else '❌'}</li>"
        html += "</ul></li>"
    html += "</ul>"
    return html

if st.button("📥 Export PDF"):
    html_content = generate_html_pdf(st.session_state.tasks)
    pdf_file = "tasks_report.pdf"
    pdfkit.from_string(html_content, pdf_file)
    with open(pdf_file, "rb") as f:
        pdf_bytes = f.read()
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{pdf_file}">Download PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

# -------------------- Share Tasks --------------------
st.subheader("📤 แชร์งานให้เพื่อน")
export_data = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
st.code(export_data, language="json")
st.info("เพื่อนนำ JSON นี้ไปวางในแอปเพื่อโหลดงานเข้าไปได้เลย")
