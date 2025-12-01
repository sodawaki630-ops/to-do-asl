import streamlit as st
import json
from datetime import datetime as dt, date
import pandas as pd
import plotly.express as px
import base64

st.set_page_config(page_title="Ultimate Mobile To-Do App", layout="wide")

# -------------------- Session State --------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("📝 Ultimate To-Do App (Safe Version)")

# -------------------- Add Task --------------------
task_name = st.text_input("ชื่องาน")
deadline = st.date_input("เดดไลน์", value=date.today())
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
        "priority": priority,
        "subtasks": subtasks,
        "completed": False,
        "new": True
    })
    st.success("เพิ่มงานสำเร็จ!")

# -------------------- Show Tasks --------------------
st.subheader("📌 รายการงาน")
for i, task in enumerate(st.session_state.tasks):
    # Progress จาก sub-task
    if task["subtasks"]:
        completed_sub = sum(1 for s in task["subtasks"] if s["completed"])
        progress = int(completed_sub / len(task["subtasks"]) * 100)
    else:
        progress = 100 if task["completed"] else 0

    st.markdown(f"### {task['name']} (Priority: {task['priority']})")
    st.markdown(f"🗓 เดดไลน์: {task['deadline']}")
    st.progress(progress)

    for j, sub in enumerate(task["subtasks"]):
        if st.checkbox(sub["name"], key=f"{i}_sub_{j}", value=sub["completed"]):
            sub["completed"] = True

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✔", key=f"done{i}"):
            task["completed"] = True
    with col2:
        if st.button("🗑", key=f"delete{i}"):
            st.session_state.tasks.pop(i)
            st.experimental_rerun()

# -------------------- Heatmap Calendar --------------------
st.subheader("📅 Heatmap Calendar")
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    df['count'] = 1
    df['deadline'] = pd.to_datetime(df['deadline'])
    heatmap_data = df.groupby(df['deadline'].dt.date)['count'].sum().reset_index()
    heatmap_data.rename(columns={'deadline':'Date','count':'Tasks'}, inplace=True)
    heatmap_fig = px.density_heatmap(
        heatmap_data,
        x=heatmap_data['Date'],
        y=['Tasks']*len(heatmap_data),
        z='Tasks',
        labels={'x':'Date','y':'Tasks','z':'จำนวนงาน'},
        title="จำนวนงานต่อวัน"
    )
    st.plotly_chart(heatmap_fig, use_container_width=True)

# -------------------- Share Tasks / Export JSON --------------------
st.subheader("📤 แชร์งาน")
export_data = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
st.code(export_data, language="json")
b64 = base64.b64encode(export_data.encode()).decode()
st.markdown(f'<a href="data:application/json;base64,{b64}" download="tasks.json">Download JSON</a>', unsafe_allow_html=True)
