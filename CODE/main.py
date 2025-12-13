import streamlit as st
import pandas as pd
import altair as alt
import json, os
from datetime import datetime

st.set_page_config(page_title="Student Tracker", layout="wide")
st.title("Student Performance Tracker")

AUTH_FILE = "auth.json"
PASSWORD = "Adminadmin"
RECOVERY_PASS = "reset"

# Point to JSON files inside INPUT_DATA
STUDENTS_FILE = "../INPUT_DATA/students.json"
ATTEMPTS_FILE = "../INPUT_DATA/attempts.json"


# ---------- AUTH FUNCTIONS ----------

def save_auth(state: bool):
    try:
        with open(AUTH_FILE, "w") as f:
            json.dump({"auth": state}, f)
    except Exception:
        pass

def load_auth() -> bool:
    try:
        if os.path.exists(AUTH_FILE):
            with open(AUTH_FILE, "r") as f:
                return bool(json.load(f).get("auth", False))
    except Exception:
        return False
    return False


# ---------- DATA STRUCTURES ----------

class Student:
    def __init__(self, sid: int, name: str, timestamp: str = None):
        self.sid = sid
        self.name = name
        self.scores = []  
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.next = None  

class StudentList:
    def __init__(self):
        self.head = None

    def add(self, sid: int, name: str, timestamp: str = None):
        if self.find(sid):
            return False, "Student ID already exists."
        node = Student(sid, name.strip(), timestamp)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        return True, "Student added."

    def find(self, sid: int):
        cur = self.head
        while cur:
            if cur.sid == sid:
                return cur
            cur = cur.next
        return None

    def remove(self, sid: int):
        cur, prev = self.head, None
        while cur:
            if cur.sid == sid:
                if prev:
                    prev.next = cur.next
                else:
                    self.head = cur.next
                return True
            prev, cur = cur, cur.next
        return False

    def to_list(self):
        cur, out = self.head, []
        while cur:
            out.append(cur)
            cur = cur.next
        return out

    def display(self):
        data = []
        cur = self.head
        while cur:
            total = sum(s["score"] for s in cur.scores)
            score_labels = [f"{s['period']} - {s['type']}: {s['score']}" for s in cur.scores]
            data.append({
                "Student Id": cur.sid,
                "Name": cur.name,
                "Scores": score_labels,
                "Total": total,
                "Added At": cur.timestamp
            })
            cur = cur.next

        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No students to display yet.")


class Stack:
    def __init__(self, limit=5):
        self.data = []
        self.limit = limit

    def push(self, item: dict):
        if len(self.data) >= self.limit:
            self.data.pop(0)
        self.data.append(item)

    def pop(self):
        return self.data.pop() if self.data else None

    def display(self):
        st.subheader("Recent Attempts")
        df = pd.DataFrame(self.data)
        if df.empty:
            st.info("No attempts yet.")
        else:
            st.table(df)


# ---------- SAVE / LOAD FUNCTIONS ----------

def save_students(lst: StudentList):
    payload = []
    for s in lst.to_list():
        payload.append({
            "Student id": s.sid,
            "name": s.name,
            "timestamp": s.timestamp,
            "scores": s.scores
        })
    try:
        with open(STUDENTS_FILE, "w") as f:
            json.dump(payload, f)
    except Exception:
        pass

def load_students() -> StudentList:
    lst = StudentList()
    try:
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r") as f:
                raw = json.load(f)
                for s in raw:
                    # Note: JSON uses "Student id" key
                    ok, _ = lst.add(s["Student id"], s.get("name", ""), s.get("timestamp"))
                    if ok:
                        found = lst.find(s["Student id"])
                        found.scores = []
                        for sc in s.get("scores", []):
                            if isinstance(sc, dict):
                                if "period" not in sc:
                                    sc["period"] = "Prelim"
                                if "type" not in sc:
                                    sc["type"] = "Activity"
                                if "timestamp" not in sc:
                                    sc["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                if "score" not in sc:
                                    sc["score"] = 0.0
                                found.scores.append(sc)
                            else:
                                found.scores.append({
                                    "period": "Prelim",
                                    "type": "Activity",
                                    "score": sc if isinstance(sc, (int, float)) else 0.0,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
    except Exception:
        pass
    return lst

def save_attempts(stack: Stack):
    try:
        with open(ATTEMPTS_FILE, "w") as f:
            json.dump(stack.data, f)
    except Exception:
        pass

def load_attempts() -> Stack:
    stck = Stack()
    try:
        if os.path.exists(ATTEMPTS_FILE):
            with open(ATTEMPTS_FILE, "r") as f:
                for a in json.load(f):
                    stck.push(a)
    except Exception:
        pass
    return stck


# ---------- AUTH / SESSION INITIALIZATION ----------

if "auth" not in st.session_state:
    st.session_state.auth = load_auth()

if not st.session_state.auth:   
    pw = st.text_input("Enter Password", type="password", autocomplete="off")
    if st.button("Login"):
        if pw == PASSWORD:
            st.session_state.auth = True
            save_auth(True)
            # Force reload data from JSON after login
            st.session_state.students = load_students()
            st.session_state.attempts = load_attempts()
            st.success("Access granted!")
            st.rerun()
        else:
            st.error("Wrong password!")

    st.subheader("Forgot Password?")
    recovery_input = st.text_input("Enter recovery word")
    if st.button("Recover"):
        if recovery_input == RECOVERY_PASS:
            st.info(f"Your password is: {PASSWORD}")
        else:   
            st.error("Invalid recovery word!")
    st.stop()

# Load data into session state if not present
if "students" not in st.session_state:
    st.session_state.students = load_students()
if "attempts" not in st.session_state:
    st.session_state.attempts = load_attempts()


# ---------- SIDEBAR MENU ----------

st.sidebar.header("Menu")
with st.sidebar.expander("Student Management", expanded=True):
    action = st.radio("Choose Action", [
        "Add Student",
        "Add Score",
        "Update Score",
        "Remove Student",
        "Remove Score"
    ])
with st.sidebar.expander("Performance", expanded=True):
    view = st.radio("View Data", [
        "Display Students",
        "Display Rankings",
        "Recent Attempts"
    ])


if st.sidebar.button("Log Out"):
    st.session_state.auth = False
    save_auth(False)
    st.success("You have logged out.")
    st.rerun()


# ---------- ACTION: STUDENT MANAGEMENT ----------

if action == "Add Student":
    st.subheader("Add Student")
    sid = st.number_input("Student ID", min_value=1, step=1)
    name = st.text_input("Student Name")
    if st.button("Add"):
        if not name.strip():
            st.error("Name cannot be empty.")
        else:
            ok, msg = st.session_state.students.add(sid, name.strip())
            if ok:
                save_students(st.session_state.students)
                st.success(msg)
            else:
                st.error(msg)

elif action == "Add Score":
    st.subheader("Add Score")
    sid = st.number_input("Student ID", min_value=1, step=1)
    period = st.selectbox("Grading Period", ["Prelim", "Midterm", "Finals"])
    typ = st.text_input("Score Type (ex Quiz 1, Exam)")
    val = st.number_input("Score", step=1.0)

    if st.button("Add Score"):
        if val < 0:
            st.error("Score cannot be negative!")
        elif not typ.strip():
            st.error("Score type cannot be empty!")
        else:
            stu = st.session_state.students.find(sid)
            if not stu:
                st.error("Student not found!")
            else:
                exists = next((
                    s for s in stu.scores
                    if s["period"].strip().lower() == period.strip().lower()
                    and s["type"].strip().lower() == typ.strip().lower()
                ), None)
                if exists:
                    st.error(f"Score '{typ}' already exists in {period} for {stu.name}.")
                else:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_score = {
                        "period": period,
                        "type": typ.strip(),
                        "score": val,
                        "timestamp": ts
                    }
                    stu.scores.append(new_score)
                    st.session_state.attempts.push({
                        "sid": sid,
                        "name": stu.name,
                        "period": period,
                        "type": typ.strip(),
                        "score": val,
                        "timestamp": ts
                    })
                    save_students(st.session_state.students)
                    save_attempts(st.session_state.attempts)
                    st.success(f"{period} - {typ} score {val} added for {stu.name}")

elif action == "Update Score":
    st.subheader("Update Score")
    sid = st.number_input("Student ID", min_value=1, step=1)
    stu = st.session_state.students.find(sid)
    if stu and stu.scores:
        periods = sorted({s["period"] for s in stu.scores})
        chosen_period = st.selectbox("Grading Period", periods)
        types = [s["type"] for s in stu.scores if s["period"] == chosen_period]
        if not types:
            st.info(f"No scores in {chosen_period}.")
        else:
            chosen_type = st.selectbox("Score Type", types)
            new_val = st.number_input("New Score", step=1.0)
            if st.button("Update"):
                if new_val < 0:
                    st.error("Score cannot be negative!")
                else:
                    for s in stu.scores:
                        if (
                            s["period"].strip().lower() == chosen_period.strip().lower()
                            and s["type"].strip().lower() == chosen_type.strip().lower()
                        ):
                            s["score"] = new_val
                            s["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            save_students(st.session_state.students)
                            st.success(f"Updated {chosen_period} - {chosen_type} to {new_val}")
                            break
    elif stu:
        st.info("No scores to update.")
    else:
        st.error("Student not found!")

elif action == "Remove Student":
    st.subheader("Remove Student")
    sid = st.number_input("Student ID", min_value=1, step=1)
    if st.button("Remove"):
        removed = st.session_state.students.remove(sid)
        if removed:
            save_students(st.session_state.students)
            st.success(f"Removed student with ID {sid}.")
        else:
            st.error("Student not found!")

elif action == "Remove Score":
    st.subheader("Remove Score")
    sid = st.number_input("Student ID", min_value=1, step=1)
    stu = st.session_state.students.find(sid)
    if stu and stu.scores:
        labels = [
            f"{s['period']} - {s['type']} ({s['score']}) @ {s['timestamp']}"
            for s in stu.scores
        ]
        choice = st.selectbox("Select score to remove", labels)
        if st.button("Remove Selected"):
            idx = labels.index(choice)
            removed = stu.scores.pop(idx)
            save_students(st.session_state.students)
            st.success(
                f"Removed {removed['period']} - {removed['type']} score {removed['score']}"
            )
    elif stu:
        st.info("No scores to remove.")
    else:
        st.error("Student not found!")


# ---------- VIEW: PERFORMANCE / RANKINGS / RECENT ATTEMPTS ----------

if view == "Display Students":
    st.session_state.students.display()

elif view == "Display Rankings":
    students = st.session_state.students.to_list()
    all_types = sorted({s["type"] for stu in students for s in stu.scores})
    chosen_type = st.selectbox("Score type for ranking", ["All"] + all_types)
    chosen_period = st.selectbox("Filter by Grading Period", ["All", "Prelim", "Midterm", "Finals"])

    rows = []
    for stu in students:
        def type_match(sc):
            return True if chosen_type == "All" else sc["type"].strip().lower() == chosen_type.strip().lower()
        def period_match(sc):
            return True if chosen_period == "All" else sc["period"].strip().lower() == chosen_period.strip().lower()
        total = sum(sc["score"] for sc in stu.scores if type_match(sc) and period_match(sc))
        rows.append({"Name": stu.name, "Total": total})

    if rows:
        df = pd.DataFrame(sorted(rows, key=lambda x: x["Total"], reverse=True))
        df.insert(0, "Rank", range(1, len(df) + 1))
        st.subheader(f"Rankings ({chosen_type}, Period: {chosen_period})")
        st.table(df)

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("Name:N", title="Student"),
            y=alt.Y("Total:Q", title=f"Total Score ({chosen_type}, {chosen_period})"),
            color="Name:N"
        ).properties(title=f"Student Rankings ({chosen_type}, {chosen_period})")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No students or scores to rank yet.")

elif view == "Recent Attempts":
    st.session_state.attempts.display()
    if st.button("Undo Last Attempt"):
        last = st.session_state.attempts.pop()
        if last:
            stu = st.session_state.students.find(last["sid"])
            if stu:
                idx_to_remove = None
                for i in range(len(stu.scores) - 1, -1, -1):
                    s = stu.scores[i]
                    if (
                        s.get("period") == last.get("period")
                        and s.get("type") == last.get("type")
                        and s.get("score") == last.get("score")
                        and s.get("timestamp") == last.get("timestamp")
                    ):
                        idx_to_remove = i
                        break
                if idx_to_remove is not None:
                    stu.scores.pop(idx_to_remove)
                    save_students(st.session_state.students)
                    save_attempts(st.session_state.attempts)
                    st.success(
                        f"Undid {last['period']} - {last['type']} score {last['score']} for {stu.name}"
                    )
                else:
                    st.warning("Could not undo — matching score entry not found.")
            else:
                st.warning("Could not undo — student not found.")
        else:
            st.info("No attempts to undo.")
