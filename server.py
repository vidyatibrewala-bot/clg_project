"""
Smart Campus Resource & Room Booking System
Flask Web Server for Localhost Access

Provides RESTful API endpoints and serves modern web UI.
Runs on http://localhost:5000 / http://127.0.0.1:5000
"""

import os
import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
import database

app = Flask(__name__, template_folder="templates", static_folder="static")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@app.route("/")
def index():
    """Serves the main single-page web application."""
    return render_template("index.html")


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    """Directly serves images and media assets from the assets directory."""
    return send_from_directory(ASSETS_DIR, filename)


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Returns real-time campus room & reservation statistics."""
    try:
        stats = database.get_system_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/categories", methods=["GET"])
def api_categories():
    """Returns distinct resource categories."""
    try:
        cats = database.get_all_categories()
        return jsonify(cats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/resources", methods=["GET"])
def api_resources():
    """Returns all campus resources, optionally filtered by category."""
    try:
        category = request.args.get("category", "All")
        rows = database.get_all_resources(category if category != "All" else None)
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/resources/<int:resource_id>", methods=["GET"])
def api_resource_detail(resource_id):
    """Returns single resource information."""
    try:
        row = database.get_resource_by_id(resource_id)
        if row:
            return jsonify(dict(row))
        return jsonify({"error": "Resource not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/schedule/<int:resource_id>", methods=["GET"])
def api_schedule(resource_id):
    """Returns day schedule for a resource on a specific date."""
    try:
        date_str = request.args.get("date", datetime.date.today().strftime("%Y-%m-%d"))
        rows = database.get_day_schedule_for_resource(resource_id, date_str)
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/check-conflict", methods=["POST"])
def api_check_conflict():
    """
    Evaluates requested time slot against existing reservations
    using mathematical interval testing: (Start_A < End_B AND End_A > Start_B).
    """
    try:
        data = request.json or {}
        resource_id = int(data.get("resource_id", 0))
        booking_date = data.get("booking_date", "")
        start_time = data.get("start_time", "")
        end_time = data.get("end_time", "")
        exclude_id = data.get("exclude_booking_id")

        if not resource_id or not booking_date or not start_time or not end_time:
            return jsonify({"has_conflict": True, "message": "Missing required booking fields.", "conflict": None}), 400

        has_conflict, conflict_row, msg = database.check_booking_conflict(
            resource_id, booking_date, start_time, end_time, exclude_id
        )

        return jsonify({
            "has_conflict": has_conflict,
            "message": msg,
            "conflict": dict(conflict_row) if conflict_row else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings", methods=["GET"])
def api_get_bookings():
    """Returns list of reservations with optional status or user filtering."""
    try:
        status_filter = request.args.get("status", "All")
        user_filter = request.args.get("user", None)
        rows = database.get_all_bookings(
            status_filter if status_filter != "All" else None,
            user_filter if user_filter else None
        )
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bookings", methods=["POST"])
def api_create_booking():
    """Submits a reservation with automated conflict blocking."""
    try:
        data = request.json or {}
        resource_id = int(data.get("resource_id", 0))
        user_name = data.get("user_name", "").strip()
        user_role = data.get("user_role", "Student").strip()
        booking_date = data.get("booking_date", "").strip()
        start_time = data.get("start_time", "").strip()
        end_time = data.get("end_time", "").strip()
        purpose = data.get("purpose", "").strip()
        attendees = int(data.get("attendees", 1))

        if not resource_id or not user_name or not booking_date or not start_time or not end_time or not purpose:
            return jsonify({
                "success": False,
                "message": "All fields (Resource, Name, Date, Times, Purpose) are required."
            }), 400

        success, msg, booking_code = database.create_booking(
            resource_id, user_name, user_role, booking_date, start_time, end_time, purpose, attendees
        )

        status_code = 201 if success else 409
        return jsonify({
            "success": success,
            "message": msg,
            "booking_code": booking_code
        }), status_code

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/bookings/<int:booking_id>/status", methods=["POST"])
def api_update_status(booking_id):
    """Approve or reject a reservation (Admin Governance)."""
    try:
        data = request.json or {}
        new_status = data.get("status")
        if new_status not in ["Approved", "Rejected", "Pending", "Cancelled"]:
            return jsonify({"success": False, "message": "Invalid status value."}), 400

        database.update_booking_status(booking_id, new_status)
        return jsonify({"success": True, "new_status": new_status})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Resets system database to initial clean presentation state."""
    try:
        database.reset_database()
        return jsonify({"success": True, "message": "Database reset to initial demo state."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    import sys
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("=" * 65)
    print(">> Smart Campus Resource Booking System is running on Localhost:")
    print("   -> Open in browser: http://localhost:5000 or http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5000, debug=False)
