# Smart Campus Resource & Room Booking System
> **College Project**: Streamlining university space management and preventing scheduling conflicts.

---

## 📌 Project Overview
Manual campus scheduling causes overlapping slots, double-booked rooms, and zero visibility for students.  
This project delivers both a modern **Web Portal (Flask + HTML/CSS/JS)** and a standalone **Python Desktop GUI Application (Tkinter + SQLite3)** with an executive **White & Greenish** design:

1. **Resource Catalog**: Browse Auditoriums, Computer/Robotics Labs, Acoustic Study Pods, Seminar Halls, and Hardware Kits.
2. **Automated Conflict Engine**: Mathematical interval testing `(Start_A < End_B AND End_A > Start_B)` that automatically detects and blocks duplicate / overlapping reservations in real time.
3. **Multi-Role Governance**: Tailored access for **Students**, **Professors**, **Lab Assistants**, and **Campus Managers**.
4. **Admin Approval Console**: One-click **Approve** and **Reject** controls for facility administrators.
5. **Digital Room Access Pass**: Generates dynamic booking reference codes and keypad access PINs.

---

## 🚀 How to Run the Project

### 1. Web Portal (Flask)
```bash
python server.py
```
Open in browser: `http://127.0.0.1:5000`

### 2. Desktop GUI (Tkinter)
```bash
python app.py
```

---

## 🗂️ Project Structure

```
clg project/
│
├── app.py              # Main Tkinter Desktop Application UI & Event Controller
├── server.py           # Flask Web Server providing REST APIs & serving Web UI
├── database.py         # SQLite Database Handler & Conflict Prevention Logic
├── campus_booking.db   # Auto-created SQLite Database
├── static/             # CSS stylesheets and Frontend JavaScript
│   ├── css/style.css   # Executive White & Greenish Design System
│   └── js/main.js      # Single-Page App controller & dynamic DOM logic
├── templates/          # HTML Templates
│   └── index.html      # Single-Page Web Portal
├── assets/             # Campus facility photos & media
└── README.md           # Documentation & Viva Explanation Guide
```

---

## 🎯 Key Capabilities & Presentation Highlights

### 1. 🛡️ Automated Double-Booking Prevention Logic
- **Objective**: When reserving a room, the system checks whether the requested `[start_time, end_time]` intersects with any active reservation for that room on the chosen date.
- If an overlap is detected, the submission is **blocked immediately**, and an alert displays who booked the conflicting slot and the exact time window.
- **Viva Demo Shortcut**: Click the **`Conflict Simulation`** button in the header toolbar to test the conflict blocker in action!

### 2. 🏛️ Resource Catalog & Schedule Inspector
- Filter campus resources by category (Auditoriums, Labs, Study Pods, Seminar Halls, Hardware Kits).
- Inspect all occupied and free slots for any space with the real-time hourly visualizer.

### 3. 👥 Multi-Role Persona Switcher
- Switch between roles right from the header dropdown:
  - **Alex Rivera (Student)**: Quick booking for study pods and collaborative labs.
  - **Dr. Elena Vance (Professor)**: Plenary auditorium and seminar hall bookings.
  - **Marcus Chen (Lab Assistant)**: Hardware kit and electronics testbench tracking.
  - **Sarah Jenkins (Campus Manager)**: Administrative oversight and approval authority.

### 4. 🛡️ Admin Approval Workflow
- Campus managers can navigate to the **`Admin Approvals`** tab to view pending requests.
- One-click buttons to **`Approve Reservation`** or **`Reject`**.

### 5. 🎟️ Digital Room Pass
- In the **`Reservation Passbook`** tab, click **`View Pass`** to open the access credentials pass featuring the reference code, door keypad PIN, and verification barcode.

---

## 📊 Database Schema (SQLite)

- **`resources` Table**: `id`, `name`, `category`, `location`, `capacity`, `amenities`, `description`, `requires_approval`
- **`bookings` Table**: `id`, `booking_code`, `resource_id`, `user_name`, `user_role`, `booking_date`, `start_time`, `end_time`, `purpose`, `attendees`, `status`, `created_at`