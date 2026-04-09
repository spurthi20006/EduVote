# 🗳️ EduVote

> **“One Student, One Vote — Secure, Transparent, and Tamper-Proof.”**

EduVote is a role-based digital voting platform for School, PU, and Engineering college elections. Powered by Django and Blockchain technology to ensure absolute voter integrity.

---

## 📌 Key Features

- **Multi-Tenant Administration**: Dedicated admins for School, PU, and Engineering.
- **Role-Based Isolation**: Admins can only see and manage their own institution's data.
- **Student Data Management**:
    - Manual one-by-one entry.
    - Bulk upload via Excel spreadsheets (`.xlsx`).
- **Secure Voting**:
    - One vote per student (Roll No / Reg No / USN).
    - Immutable blockchain storage.
    - Green checkmark (✔) confirmation.
    - Duplicate voting prevention with active warnings.
- **Result Security**: No public tally for students; results are visible only to authorized Admins.

---

## 👥 User Types

### School Students
- Roll Number
- Name
- Class

### PU Students
- Registration Number
- Name
- Year

### Engineering Students
- USN (Reg No)
- Name
- Branch
- Year

---

## ⚙️ Administrative Setup

1. **Main Admin (Super User)**: Oversees all sub-admins and global system stats.
2. **Institutional Admins**: Can Sign Up and Sign In via the landing page to manage their respective elections.

---

## 🛠️ How to Run

1. **Install dependencies**:
   `pip install -r requirements.txt`

2. **Run server**:
   `python manage.py runserver`

3. **Open**:
   `http://127.0.0.1:8000`

---

## ⛓️ Blockchain Integrity
Each vote is stored as a cryptographic block:
- Voter Hash (SHA-256)
- Candidate Name
- Timestamp
- Previous Hash

---

## 🧠 Conclusion
EduVote provides a secure, easy-to-manage voting environment for educational institutions, ensuring that every vote is counted fairly and transparently.
