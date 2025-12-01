import streamlit as st
import json
from datetime import datetime as dt, date
import base64

# -------------------- Config --------------------
st.set_page_config(page_title="🎄 Ultimate Christmas To-Do App 📝", layout="wide")

# -------------------- Dark Mode --------------------
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False)
if dark_mode:
    BG = "#1c1c1c"
    CARD_BG = "#2c2f33"
    TEXT = "#e4e6eb"
    PROG_FILL = "#4caf50"
else:
    BG = "linear-gradient(135deg, #ff4b4b, #28a745)"
    CARD_BG = "rgba(255,255,255,0.9)"
    TEXT = "#111"
    PROG_FILL = "#ff4b4b"

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
    color: #111;
    padding: 18px;
    border-radius: 18px;
    margin-bottom: 15px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
}}
.task-card:hover {{
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}}
.task-card.new {{
    animation: slideFade 0.7s ease-out;
}}
@keyframes slideFade {{
    0% {{opacity: 0; transform: translateX(50px);}}
    100% {{opacity: 1; transform: translateX(0);}}
}}
.priority-high {{background-color:#ff0000; color:white;}}
.priority-medium {{background-color:#28a745; color:white;}}
.priority-low {{background-color:#FFD700; color:black;}}
.deadline-text {{font-weight: 700; color:#d40000;}}
.progress-bar {{height: 10px; border-radius: 10px; background: #eee;}}
.progress-fill {{height: 10px; border-radius: 10px; background: {PROG_FILL};}}
.popup {{
    position: fixed;
    top: 20px;
    right: 20px;
    background: #28a745;
    color: white;
    padding: 15px 25px;
    border-radius: 12px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
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
    transform: scale(1.1) rotate(-2deg);
    transition: transform 0.2s;
}}

/* Snowfall Animation */
.snowflake {{
  position: fixed;
  top: -10px;
  z-index: 9999;
  user-select: none;
  pointer-events: none;
  color: white;
  font-size: 1.2em;
  animation-name: fall;
  animation-duration: 10s;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  opacity: 0.8;
}}
@keyframes fall {{
  0% {{transform: translateY(0) translateX(0);}}
  100% {{transform: translateY(100vh) translateX(50px);}}
}}
</style>
<script>
const count = 50;
for(let i=0; i<count; i++){{
    const snow = document.createElement('div');
    snow.className = 'snowflake';
    snow.style.left = Math.random() * window.innerWidth + 'px';
    snow.style.animationDuration = 5 + Math.random() * 5 + 's';
    snow.style.fontSize = 12 + Math.random() * 24 + 'px';
    snow.innerHTML = '❄️';
    document.body.appendChild(snow);
}}
</script>
""", unsafe_allow_html=True)

# -------------------- Session State --------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "sound_played" not in st.session_state:
    st.session_state.sound_played = set()

# -------------------- Title --------------------
st.title("🎄 Ultimate Christmas To-Do App 📝")

# -------------------- Add Task --------------------
st.subheader("➕ เพิ่มงานใหม่")
col1, col2, col3, col4 = st.columns([3,3,3,3])
with col1:
    task_name = st.text_input("ชื่องาน 🎁")
with col2:
    deadline = st.date_input("เดดไลน์", value=date.today())
with col3:
    category = st.text_input("หมวดหมู่ 🎄")
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
    st.markdown("<div class='popup'>เพิ่มงานสำเร็จ! 🎉🎄</div>", unsafe_allow_html=True)

# -------------------- Filter --------------------
st.subheader("🔎 กรองงาน")
filter_category = st.text_input("กรองตามหมวดหมู่")
filter_priority = st.selectbox("กรองตาม Priority", ["All","High","Medium","Low"])

# -------------------- Progress Summary --------------------
total = len(st.session_state.tasks)
done = sum(1 for t in st.session_state.tasks if t["completed"])
if total > 0:
    st.progress(done / total)
    st.write(f"✔ งานเสร็จแล้ว {done}/{total} งาน 🎅")
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

    if task["subtasks"]:
        completed_sub = sum(1 for s in task["subtasks"] if s["completed"])
        progress = int(completed_sub / len(task["subtasks"]) * 100)
    else:
        progress = 0 if not task["completed"] else 100

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
            f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width:{progress}%"></div>
            </div>
            """,
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
            st.warning(f"⏰ งานนี้ใกล้ถึงเดดไลน์แล้ว! 🎅")
            st.session_state.sound_played.add(task["name"])

    with colB:
        if st.button("✔", key=f"done{i}"):
            for sub in task["subtasks"]:
                sub["completed"] = True
            task["completed"] = True
            st.success("งานเสร็จแล้ว! 🎄")
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

# -------------------- Share Tasks --------------------
st.subheader("📤 แชร์งานให้เพื่อน")
export_data = json.dumps(st.session_state.tasks, ensure_ascii=False, indent=2)
st.code(export_data, language="json")
b64 = base64.b64encode(export_data.encode()).decode()
st.markdown(f'<a href="data:application/json;base64,{b64}" download="tasks.json">Download JSON 🎁</a>', unsafe_allow_html=True)
