# Pro-grammerzzz-sdg4-dsa
<h2>Project Title and SDG Goal</h2>
Student Performance Tracker
SDG 4 – Quality Education

This project addresses the challenge of tracking student performance efficiently and accurately. Many schools still rely on manual grade recording, which leads to errors, lost data, and difficulty monitoring progress. Our system provides a digital, structured, and accessible way to record, update, and analyze student scores — supporting inclusive and equitable quality education.

<h1>Project Description</h1>
The Student Performance Tracker is a Python-based web application built with Streamlit. It allows educators to:
Add and manage student records,
Record scores across grading periods
View rankings and performance summaries
Undo recent score actions
Persist data using JSON files

Justification of Data Structures Used

Linked List - it's purpose is to Stores student records. linked list is used because it Allows dynamic addition/removal of students without array resizing.

Stack - it's purpose is to Stores recent score attempts. stack is used because it Enables “Undo Last Attempt” using LIFO behavior.

Sorting (Custom) - it's purpose is to Ranks students by score. Sorting is used becuase it Allows dynamic ranking based on selected score type and grading period.

JSON Files library - it's purpose is for Persistent storage. json is used because it is Lightweight, readable, and ideal for local data saving.

<h1>Installation and Setup and Run locally</h1>

Step 1: Clone the Repository
Open Git Bash or CMD and run:
git clone https://github.com/karasmaiAS/Pro-grammerzzz-sdg4-dsa.git
cd Pro-grammerzzz-sdg4-dsa/CODE

Step 2: Install Python (if not yet installed)
Download and install Python from:
https://www.python.org/downloads
Make sure to check “Add Python to PATH” during installation.

Step 3: Install Required Libraries
Run this in your terminal:
pip install streamlit pandas altair

This installs:
streamlit → for the web interface
pandas → for data handling
altair → for charts and rankings

Step 4: Prepare JSON Files
Inside INPUT_DATA/, create two files:

students.json → with content: []

attempts.json → with content: []

These will store student records and score attempts.

<h1>Usage Instructions</h1>

Step 1: Run the App
Inside the CODE folder or open it in vscode and in terminal type:
streamlit run main.py

Step 2: Login
Password: Adminadmin
Recovery Word: reset

Step 3: Use the Sidebar Menu
Add Student
Enter Student ID and Name
Click Add
Data is saved to students.json

Add Score
Select student
Choose grading period
Enter score type and value
Score is saved and logged in the attempts stack

Update Score
Select student
Choose period and score type
Enter new value

📌 Remove Student / Score
Remove entire student record or specific score entry

📌 Display Students
Shows all students, scores, and total performance

📌 Display Rankings
Sorts students by total score
Filter by score type and grading period
Includes bar chart visualization

📌 Recent Score Attempts + Undo
Shows last 5 actions
Undo the most recent score entry

<h2>Contributors</h2>

Abdul, Muhammad Siddiq M. as (karasmaiAS) contributed (Github Repository Submission), (75% of Documentation), (Midterm, Final DSA Code Implementation),(Academic Format Document Implementation), (Power Point Presentation)

DOMINGO, JAYSON B. as (vorn440) (25% of Documentation), (Prelim DSA Code Implementation)


<h3>Additonal Information</h3>
Folder Structure

Pro-grammerzzz-sdg4-dsa/

│

├── CODE/

│     ├── main.py

│     ├── auth.json

│

├── INPUT_DATA/

│     ├── students.json

│     ├── attempts.json

│
├── DOCUMENTATION/

│     ├── SDG_Report.pdf

│     

│     

│

└── README.md
