"""
Smart Campus Resource & Room Booking System
Database Module (SQLite)

This module handles:
1. SQLite database initialization and table schemas.
2. Pre-seeding campus rooms, laboratories, study pods, and hardware kits.
3. Automated Conflict Detection Logic (prevents duplicate / overlapping time slots).
4. Booking management (Create, Read, Approve, Reject, Cancel).
"""

import sqlite3
import datetime
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "campus_booking.db")


def get_connection():
    """Returns a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Creates database tables and seeds initial campus resources."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Resources Table (Rooms, Halls, Makerspaces, Hardware Kits)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            amenities TEXT,
            description TEXT,
            requires_approval INTEGER DEFAULT 1
        )
    """)

    # 2. Bookings Table (Stores reservations and approval status)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_code TEXT UNIQUE NOT NULL,
            resource_id INTEGER NOT NULL,
            user_name TEXT NOT NULL,
            user_role TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            purpose TEXT NOT NULL,
            attendees INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY (resource_id) REFERENCES resources (id)
        )
    """)

    # Seed initial resources if empty
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0:
        seed_resources = [
            (
                "Grand Innovation Auditorium",
                "Auditorium",
                "Block A - 1st Floor",
                350,
                "4K Dual Projector, Dolby Stage Audio, Live Streaming, AC",
                "Tiered auditorium hall for college symposiums, conferences, and department plenaries.",
                1
            ),
            (
                "Edison Robotics & Embedded Systems Lab",
                "Laboratory",
                "Block C - Ground Floor",
                35,
                "Soldering Stations, DSO Oscilloscopes, 3D Printers, ESD Benches",
                "Specialized makerspace for robotics, IoT kits, and electronics development.",
                1
            ),
            (
                "Tesla Acoustic Collaboration Pod 3",
                "Study Pod",
                "Library Commons - 2nd Floor",
                6,
                "55-inch Screen, Acoustic Glass, Magnetic Whiteboard Wall, Fast USB-C",
                "Quiet sound-isolated team pod for student project discussions and code reviews.",
                0  # Instant automated booking (no admin review needed)
            ),
            (
                "Curie Silent Focus Pod 7",
                "Study Pod",
                "Library Commons - 3rd Floor",
                4,
                "Dual Monitors, Sound Dampening Panels, Adjustable Warm Lighting",
                "Small acoustic study pod built for concentrated research and study sessions.",
                0  # Instant automated booking
            ),
            (
                "Ada Lovelace Executive Seminar Hall",
                "Seminar Hall",
                "Block B - 3rd Floor",
                120,
                "Smart Display, Hybrid Zoom Conference Rig, Podium Mics, Surround Audio",
                "Executive presentation hall for thesis defenses and faculty workshops.",
                1
            ),
            (
                "NVIDIA Jetson AGX Orin Edge AI Kit",
                "Hardware Kit",
                "Equipment Depot - Lab C-12",
                1,
                "275 TOPS Compute, Stereo Depth Camera, JetPack OS, Power Adapter",
                "High-performance edge AI developer kit for computer vision and robotics projects.",
                1
            ),
            (
                "Tektronix 4-Channel Mixed Signal DSO",
                "Hardware Kit",
                "Electronics Vault - Block C Rm 104",
                1,
                "200 MHz Bandwidth, 4 Analog Channels, Digital Probes, Calibration Kit",
                "Benchtop precision oscilloscope for waveform debugging and signal integrity analysis.",
                1
            ),
            (
                "IoT Sensor Array & LoRa Gateway Bundle",
                "Hardware Kit",
                "Embedded Systems Lab - Block C Ground",
                1,
                "ESP32-S3 Boards (x3), LoRa Transceivers, Environmental Sensors, Solar Pack",
                "Telemetry and sensor networking kit for smart campus and environmental projects.",
                0
            )
        ]

        cursor.executemany("""
            INSERT INTO resources (name, category, location, capacity, amenities, description, requires_approval)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, seed_resources)

        # Pre-seed realistic bookings for today so the schedule isn't blank
        today = datetime.date.today().strftime("%Y-%m-%d")
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        seed_bookings = [
            (
                "BKG-101",
                1,  # Grand Auditorium
                "Dr. Elena Vance",
                "Professor",
                today,
                "10:00",
                "12:00",
                "Annual IEEE Robotics Keynote & Student Pitch",
                150,
                "Approved",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "BKG-102",
                2,  # Robotics Lab
                "Marcus Chen",
                "Lab Assistant",
                today,
                "14:00",
                "16:30",
                "PCB Soldering & SMD Workshop - Batch B",
                25,
                "Approved",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "BKG-103",
                3,  # Tesla Study Pod
                "Alex Rivera",
                "Student",
                today,
                "15:00",
                "17:00",
                "Senior Capstone Architecture Sprint",
                4,
                "Approved",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            (
                "BKG-104",
                5,  # Seminar Hall
                "Dr. Elena Vance",
                "Professor",
                tomorrow,
                "11:00",
                "13:00",
                "Post-Graduate Research Colloquium",
                60,
                "Pending",
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        ]

        cursor.executemany("""
            INSERT INTO bookings (booking_code, resource_id, user_name, user_role, booking_date, start_time, end_time, purpose, attendees, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_bookings)

    conn.commit()
    conn.close()


def get_all_resources(category=None):
    """Fetch all resources, optionally filtered by category."""
    conn = get_connection()
    cursor = conn.cursor()
    if category and category != "All":
        cursor.execute("SELECT * FROM resources WHERE category = ? ORDER BY name ASC", (category,))
    else:
        cursor.execute("SELECT * FROM resources ORDER BY category ASC, name ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_resource_by_id(resource_id):
    """Fetch a single resource by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_categories():
    """Returns distinct categories available in the system."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM resources ORDER BY category ASC")
    rows = [r["category"] for r in cursor.fetchall()]
    conn.close()
    return ["All"] + rows


# ==============================================================================
# CORE OBJECTIVE: AUTOMATED DOUBLE-BOOKING / CONFLICT DETECTION ENGINE
# ==============================================================================
def check_booking_conflict(resource_id, booking_date, start_time, end_time, exclude_booking_id=None):
    """
    Checks if a requested time slot overlaps with any active (Approved or Pending) booking.
    
    Overlapping logic:
    Two time slots [S1, E1] and [S2, E2] overlap if:
        max(S1, S2) < min(E1, E2)
    In SQL:
        existing.start_time < new_end_time AND existing.end_time > new_start_time

    Returns:
        (has_conflict: bool, conflicting_booking: sqlite3.Row or None, message: str)
    """
    # Basic time validation
    if end_time <= start_time:
        return True, None, "End time must be later than start time."

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT b.*, r.name as resource_name 
        FROM bookings b
        JOIN resources r ON b.resource_id = r.id
        WHERE b.resource_id = ?
          AND b.booking_date = ?
          AND b.status IN ('Approved', 'Pending')
          AND b.start_time < ?
          AND b.end_time > ?
    """
    params = [resource_id, booking_date, end_time, start_time]

    if exclude_booking_id:
        query += " AND b.id != ?"
        params.append(exclude_booking_id)

    cursor.execute(query, params)
    conflict = cursor.fetchone()
    conn.close()

    if conflict:
        msg = (
            f"Double-Booking Blocked!\n"
            f"Time slot clashes with existing reservation:\n"
            f"• Title: {conflict['purpose']}\n"
            f"• Booked By: {conflict['user_name']} ({conflict['user_role']})\n"
            f"• Reserved Slot: {conflict['start_time']} - {conflict['end_time']}\n"
            f"• Status: {conflict['status']}"
        )
        return True, conflict, msg

    return False, None, "Slot is completely available with zero conflicts."


def create_booking(resource_id, user_name, user_role, booking_date, start_time, end_time, purpose, attendees=1):
    """
    Creates a new reservation after validating conflict prevention.
    Returns:
        (success: bool, result_or_message: str, booking_code: str)
    """
    # 1. Run strict double-booking check
    has_conflict, conflict, msg = check_booking_conflict(resource_id, booking_date, start_time, end_time)
    if has_conflict:
        return False, msg, None

    conn = get_connection()
    cursor = conn.cursor()

    # Determine status: Study pods and certain items are instant-approved, others require admin review
    res = get_resource_by_id(resource_id)
    if not res:
        conn.close()
        return False, "Resource not found.", None

    initial_status = "Approved" if res["requires_approval"] == 0 or user_role == "Campus Manager" else "Pending"

    # Generate unique booking code
    cursor.execute("SELECT COUNT(*) FROM bookings")
    next_num = cursor.fetchone()[0] + 101
    booking_code = f"BKG-{next_num}"
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO bookings (
            booking_code, resource_id, user_name, user_role, booking_date, 
            start_time, end_time, purpose, attendees, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        booking_code, resource_id, user_name, user_role, booking_date,
        start_time, end_time, purpose, attendees, initial_status, created_at
    ))

    conn.commit()
    conn.close()

    status_msg = "Confirmed (Instant Approved)" if initial_status == "Approved" else "Submitted for Admin Approval"
    return True, f"Reservation {status_msg}! Code: {booking_code}", booking_code


def get_all_bookings(status_filter=None, user_name_filter=None):
    """Fetch bookings with resource details for display tables."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT b.*, r.name as resource_name, r.category as resource_category, r.location
        FROM bookings b
        JOIN resources r ON b.resource_id = r.id
        WHERE 1=1
    """
    params = []

    if status_filter and status_filter != "All":
        query += " AND b.status = ?"
        params.append(status_filter)

    if user_name_filter:
        query += " AND b.user_name = ?"
        params.append(user_name_filter)

    query += " ORDER BY b.booking_date DESC, b.start_time DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_booking_status(booking_id, new_status):
    """Approve or Reject a reservation."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (new_status, booking_id))
    conn.commit()
    conn.close()


def get_day_schedule_for_resource(resource_id, date_str):
    """Fetch all active bookings for a specific resource on a given day."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM bookings
        WHERE resource_id = ?
          AND booking_date = ?
          AND status IN ('Approved', 'Pending')
        ORDER BY start_time ASC
    """, (resource_id, date_str))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_system_statistics():
    """Calculates summary statistics for display."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM resources")
    total_resources = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Pending'")
    pending_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Approved'")
    approved_count = cursor.fetchone()[0]

    today = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM bookings WHERE booking_date = ? AND status = 'Approved'", (today,))
    today_active = cursor.fetchone()[0]

    conn.close()
    return {
        "total_resources": total_resources,
        "total_bookings": total_bookings,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "today_active": today_active
    }


def reset_database():
    """Resets the database back to clean initial demo state."""
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass
    init_database()


# Initialize database upon import
init_database()
