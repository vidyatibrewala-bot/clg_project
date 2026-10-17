/**
 * Smart Campus Resource & Room Booking System
 * Frontend Application Controller (Vanilla JS)
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    currentUser: {
      name: "Alex Rivera",
      role: "Student"
    },
    resources: [],
    bookings: [],
    selectedResourceForSchedule: null,
    activeCategory: "All",
    activePassbookStatus: "All"
  };

  // DOM Elements
  const personaSelect = document.getElementById("personaSelect");
  const tabLinks = document.querySelectorAll(".tab-link");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const resourceGrid = document.getElementById("resourceGrid");
  const categoryChips = document.getElementById("categoryChips");
  const catalogSearch = document.getElementById("catalogSearch");

  // Booking Form Elements
  const reservationForm = document.getElementById("reservationForm");
  const bookingResourceSelect = document.getElementById("bookingResourceSelect");
  const bookingDate = document.getElementById("bookingDate");
  const bookingStartTime = document.getElementById("bookingStartTime");
  const bookingEndTime = document.getElementById("bookingEndTime");
  const bookingAttendees = document.getElementById("bookingAttendees");
  const bookingPurpose = document.getElementById("bookingPurpose");
  const bookingFormUserBadge = document.getElementById("bookingFormUserBadge");
  const btnCheckConflict = document.getElementById("btnCheckConflict");
  const diagnosticStatusBox = document.getElementById("diagnosticStatusBox");
  const diagnosticIndicator = document.getElementById("diagnosticIndicator");

  // Header Fast Actions
  const btnQuickConflictDemo = document.getElementById("btnQuickConflictDemo");
  const btnResetDemoData = document.getElementById("btnResetDemoData");
  const btnDateToday = document.getElementById("btnDateToday");
  const btnDateTomorrow = document.getElementById("btnDateTomorrow");
  const slotPresetButtons = document.querySelectorAll(".btn-slot-preset");

  // Modals
  const scheduleModal = document.getElementById("scheduleModal");
  const btnCloseScheduleModal = document.getElementById("btnCloseScheduleModal");
  const btnCloseScheduleModalFooter = document.getElementById("btnCloseScheduleModalFooter");
  const btnBookFromSchedule = document.getElementById("btnBookFromSchedule");

  const passModal = document.getElementById("passModal");
  const btnClosePassModal = document.getElementById("btnClosePassModal");
  const btnClosePassModalFooter = document.getElementById("btnClosePassModalFooter");

  // Passbook & Admin
  const passbookTableBody = document.getElementById("passbookTableBody");
  const passbookStatusFilter = document.getElementById("passbookStatusFilter");
  const btnRefreshBookings = document.getElementById("btnRefreshBookings");
  const adminQueueList = document.getElementById("adminQueueList");
  const adminPendingCount = document.getElementById("adminPendingCount");
  const adminPendingBadge = document.getElementById("adminPendingBadge");

  // Format Helper: Today's date string YYYY-MM-DD
  const getTodayStr = () => {
    const d = new Date();
    return d.toISOString().split("T")[0];
  };

  const getTomorrowStr = () => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split("T")[0];
  };

  // Image mapper for resources
  const getResourceImage = (resource) => {
    const cat = resource.category ? resource.category.toLowerCase() : "";
    const name = resource.name ? resource.name.toLowerCase() : "";

    if (cat.includes("auditorium") || name.includes("auditorium")) {
      return "/assets/auditorium.jpg";
    }
    if (cat.includes("seminar") || name.includes("seminar")) {
      return "/assets/auditorium.jpg";
    }
    if (cat.includes("study") || cat.includes("pod") || name.includes("pod")) {
      return "/assets/study_pods.jpg";
    }
    return "/assets/hardware_lab.jpg";
  };

  // Generate 4-digit PIN deterministically from booking ID
  const generatePin = (bookingId) => {
    const seed = (bookingId * 179 + 3481) % 10000;
    return String(seed).padStart(4, "0");
  };

  // ============================================================================
  // Initialization & Data Loading
  // ============================================================================
  const initApp = async () => {
    bookingDate.value = getTodayStr();

    setupEventListeners();
    await loadStats();
    await loadResources();
    await loadBookings();
  };

  // Load real-time system stats
  const loadStats = async () => {
    try {
      const res = await fetch("/api/stats");
      const stats = await res.json();

      document.getElementById("statTotalResources").textContent = stats.total_resources || 0;
      document.getElementById("statTodayActive").textContent = stats.today_active || 0;
      document.getElementById("statPending").textContent = stats.pending_count || 0;

      // Tab 5 counters
      document.getElementById("analyticTotalVenues").textContent = stats.total_resources || 0;
      document.getElementById("analyticApprovedCount").textContent = stats.approved_count || 0;
      document.getElementById("analyticPendingCount").textContent = stats.pending_count || 0;

      // Admin badge
      adminPendingBadge.textContent = stats.pending_count || 0;
      adminPendingCount.textContent = `${stats.pending_count || 0} Pending`;
    } catch (err) {
      console.error("Failed to load stats:", err);
    }
  };

  // Load campus resources
  const loadResources = async () => {
    try {
      const url = state.activeCategory === "All"
        ? "/api/resources"
        : `/api/resources?category=${encodeURIComponent(state.activeCategory)}`;

      const res = await fetch(url);
      state.resources = await res.json();
      renderResourceGrid();
      populateResourceDropdown();
    } catch (err) {
      console.error("Failed to load resources:", err);
      resourceGrid.innerHTML = `<div class="error-state">Failed to load facilities. Check server connection.</div>`;
    }
  };

  // Populate Resource Dropdown in Booking Tab
  const populateResourceDropdown = () => {
    bookingResourceSelect.innerHTML = "";
    state.resources.forEach((r) => {
      const opt = document.createElement("option");
      opt.value = r.id;
      opt.textContent = `${r.name} (${r.category} - ${r.location})`;
      bookingResourceSelect.appendChild(opt);
    });
  };

  // Render Resource Cards Grid
  const renderResourceGrid = () => {
    const searchTerm = catalogSearch.value.trim().toLowerCase();
    const filtered = state.resources.filter((r) => {
      if (!searchTerm) return true;
      return (
        r.name.toLowerCase().includes(searchTerm) ||
        r.category.toLowerCase().includes(searchTerm) ||
        r.location.toLowerCase().includes(searchTerm) ||
        (r.amenities && r.amenities.toLowerCase().includes(searchTerm))
      );
    });

    if (filtered.length === 0) {
      resourceGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
          <h3>No campus facilities match your search criteria.</h3>
        </div>
      `;
      return;
    }

    resourceGrid.innerHTML = filtered.map((r) => {
      const imgPath = getResourceImage(r);
      const isInstant = r.requires_approval === 0;
      const approvalBadge = isInstant
        ? `<span class="approval-badge badge-instant">Instant Booking</span>`
        : `<span class="approval-badge badge-review">Staff Review Required</span>`;

      const amenitiesList = (r.amenities || "")
        .split(",")
        .filter(Boolean)
        .map((a) => `<span class="amenity-pill">${a.trim()}</span>`)
        .join("");

      return `
        <div class="resource-card" data-id="${r.id}">
          <div class="card-img-wrap">
            <img src="${imgPath}" alt="${r.name}" class="card-img" loading="lazy">
            <div class="card-overlay-badges">
              <span class="category-tag">${r.category}</span>
              ${approvalBadge}
            </div>
          </div>
          <div class="card-content">
            <h3 class="resource-name">${r.name}</h3>
            <div class="resource-meta">
              <span class="meta-item">📍 ${r.location}</span>
              <span class="meta-item">👥 Capacity: ${r.capacity}</span>
            </div>
            <p class="resource-desc">${r.description || ""}</p>
            <div class="amenities-list">
              ${amenitiesList}
            </div>
            <div class="card-footer">
              <button class="btn btn-secondary btn-inspect-schedule" data-id="${r.id}">
                Day Schedule
              </button>
              <button class="btn btn-primary btn-book-direct" data-id="${r.id}">
                Reserve Venue
              </button>
            </div>
          </div>
        </div>
      `;
    }).join("");

    // Attach card action listeners
    document.querySelectorAll(".btn-inspect-schedule").forEach((btn) => {
      btn.addEventListener("click", () => openScheduleModal(btn.dataset.id));
    });

    document.querySelectorAll(".btn-book-direct").forEach((btn) => {
      btn.addEventListener("click", () => {
        selectResourceAndSwitchToBooking(btn.dataset.id);
      });
    });
  };

  // Load bookings and render Passbook + Admin queue
  const loadBookings = async () => {
    try {
      const url = state.activePassbookStatus === "All"
        ? "/api/bookings"
        : `/api/bookings?status=${encodeURIComponent(state.activePassbookStatus)}`;

      const res = await fetch(url);
      state.bookings = await res.json();

      renderPassbookTable();
      renderAdminQueue();
    } catch (err) {
      console.error("Failed to load bookings:", err);
    }
  };

  // Render Passbook Table
  const renderPassbookTable = () => {
    if (state.bookings.length === 0) {
      passbookTableBody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">
            No reservations found for current filter.
          </td>
        </tr>
      `;
      return;
    }

    passbookTableBody.innerHTML = state.bookings.map((b) => {
      let statusClass = "status-pending";
      if (b.status === "Approved") statusClass = "status-approved";
      if (b.status === "Rejected") statusClass = "status-rejected";

      return `
        <tr>
          <td><span class="booking-code-pill">${b.booking_code}</span></td>
          <td>
            <strong>${b.resource_name || "Facility"}</strong>
            <div style="font-size: 0.78rem; color: var(--text-muted);">${b.location || ""}</div>
          </td>
          <td>
            <div style="font-weight: 600;">${b.booking_date}</div>
            <div style="font-family: var(--font-mono); font-size: 0.8rem; color: var(--text-secondary);">${b.start_time} - ${b.end_time}</div>
          </td>
          <td>
            <div style="font-weight: 600;">${b.user_name}</div>
            <div style="font-size: 0.75rem; color: var(--brand-primary);">${b.user_role}</div>
          </td>
          <td style="max-width: 220px;">
            <div style="font-size: 0.84rem; color: var(--text-main);">${b.purpose}</div>
            <div style="font-size: 0.72rem; color: var(--text-muted);">${b.attendees} persons</div>
          </td>
          <td>
            <span class="status-badge ${statusClass}">${b.status}</span>
          </td>
          <td>
            <button class="btn btn-micro btn-view-pass" data-code="${b.booking_code}">
              View Pass
            </button>
          </td>
        </tr>
      `;
    }).join("");

    document.querySelectorAll(".btn-view-pass").forEach((btn) => {
      btn.addEventListener("click", () => {
        const code = btn.dataset.code;
        const booking = state.bookings.find((x) => x.booking_code === code);
        if (booking) openPassModal(booking);
      });
    });
  };

  // Render Admin Approvals Queue
  const renderAdminQueue = () => {
    const pendingList = state.bookings.filter((b) => b.status === "Pending");
    adminPendingCount.textContent = `${pendingList.length} Pending`;
    adminPendingBadge.textContent = pendingList.length;

    if (pendingList.length === 0) {
      adminQueueList.innerHTML = `
        <div style="text-align: center; padding: 40px; color: var(--text-muted); background: var(--bg-canvas); border: 1px dashed var(--border-subtle); border-radius: var(--radius-md);">
          <div style="font-size: 1.8rem; margin-bottom: 8px;">✓</div>
          <h4 style="color: var(--text-main);">Zero Pending Requests</h4>
          <p style="font-size: 0.82rem;">All facility booking requests have been reviewed and processed.</p>
        </div>
      `;
      return;
    }

    adminQueueList.innerHTML = pendingList.map((b) => `
      <div class="admin-item-card" data-id="${b.id}">
        <div class="admin-item-header">
          <span class="booking-code-pill">${b.booking_code}</span>
          <span class="status-badge status-pending">Pending Review</span>
        </div>
        <h4 style="font-size: 1.05rem; color: var(--text-main);">${b.resource_name}</h4>
        <div class="admin-item-details">
          <div><span class="detail-label">Requested By:</span> <span class="detail-val">${b.user_name} (${b.user_role})</span></div>
          <div><span class="detail-label">Date & Time:</span> <span class="detail-val">${b.booking_date} (${b.start_time} - ${b.end_time})</span></div>
          <div><span class="detail-label">Attendees:</span> <span class="detail-val">${b.attendees} persons</span></div>
          <div><span class="detail-label">Purpose:</span> <span class="detail-val">${b.purpose}</span></div>
        </div>
        <div class="admin-item-actions">
          <button class="btn btn-approve btn-action-status" data-id="${b.id}" data-status="Approved">
            Approve Reservation
          </button>
          <button class="btn btn-reject btn-action-status" data-id="${b.id}" data-status="Rejected">
            Reject
          </button>
        </div>
      </div>
    `).join("");

    document.querySelectorAll(".btn-action-status").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        const status = btn.dataset.status;
        await updateBookingStatus(id, status);
      });
    });
  };

  // Update Booking Status via Admin API
  const updateBookingStatus = async (bookingId, newStatus) => {
    try {
      const res = await fetch(`/api/bookings/${bookingId}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
      });
      const data = await res.json();
      if (data.success) {
        showToast(`Reservation marked as ${newStatus}!`, "success");
        await loadBookings();
        await loadStats();
      } else {
        showToast(data.message || "Failed to update status", "error");
      }
    } catch (err) {
      showToast("Network error updating status", "error");
    }
  };

  // Switch tab helper
  const switchTab = (tabId) => {
    tabLinks.forEach((link) => {
      link.classList.toggle("active", link.dataset.tab === tabId);
    });
    tabPanes.forEach((pane) => {
      pane.classList.toggle("active", pane.id === tabId);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const selectResourceAndSwitchToBooking = (resourceId) => {
    bookingResourceSelect.value = resourceId;
    switchTab("tab-booking");
  };

  // ============================================================================
  // Automated Conflict Prevention Engine Check
  // ============================================================================
  const runConflictCheck = async () => {
    const resourceId = bookingResourceSelect.value;
    const dateStr = bookingDate.value;
    const startTime = bookingStartTime.value;
    const endTime = bookingEndTime.value;

    if (!resourceId || !dateStr || !startTime || !endTime) {
      showToast("Please select a resource, date, and valid times first.", "warning");
      return;
    }

    if (endTime <= startTime) {
      renderConflictResult(true, "End time must be strictly later than start time.", null);
      return;
    }

    try {
      const res = await fetch("/api/check-conflict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resource_id: resourceId,
          booking_date: dateStr,
          start_time: startTime,
          end_time: endTime
        })
      });
      const data = await res.json();
      renderConflictResult(data.has_conflict, data.message, data.conflict);
    } catch (err) {
      console.error("Conflict check error:", err);
      showToast("Error checking conflicts with server.", "error");
    }
  };

  // Render Real-Time Diagnostic Box
  const renderConflictResult = (hasConflict, message, conflict) => {
    if (hasConflict) {
      diagnosticIndicator.className = "diagnostic-indicator conflict";
      diagnosticIndicator.textContent = "Status: Conflict Blocked";

      diagnosticStatusBox.innerHTML = `
        <div class="conflict-alert-card">
          <div class="alert-header">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
            <span>DOUBLE-BOOKING DETECTED & BLOCKED</span>
          </div>
          <ul class="conflict-details-list">
            <li><strong>Conflict Reason:</strong> <span>Time interval overlaps existing booking</span></li>
            ${conflict ? `
              <li><strong>Reserved Title:</strong> <span>${conflict.purpose || "Academic Session"}</span></li>
              <li><strong>Booked By:</strong> <span>${conflict.user_name} (${conflict.user_role})</span></li>
              <li><strong>Existing Slot:</strong> <span style="color: var(--rejected-color); font-weight: 700; font-family: var(--font-mono);">${conflict.start_time} - ${conflict.end_time}</span></li>
              <li><strong>Status:</strong> <span>${conflict.status}</span></li>
            ` : `<li><strong>Detail:</strong> <span>${message}</span></li>`}
          </ul>
          <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 8px;">
            System strictly blocks overlapping reservations to protect campus space integrity.
          </p>
        </div>
      `;
      showToast("Conflict detected! Double booking blocked.", "error");
    } else {
      diagnosticIndicator.className = "diagnostic-indicator clear";
      diagnosticIndicator.textContent = "Status: 100% Available";

      diagnosticStatusBox.innerHTML = `
        <div class="slot-clear-card">
          <div class="clear-header">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            <span>ZERO CONFLICTS - TIME SLOT CLEAR</span>
          </div>
          <p>The requested interval does not intersect with any confirmed or pending reservation. Ready to reserve!</p>
        </div>
      `;
      showToast("Time slot is available with zero conflicts!", "success");
    }
  };

  // ============================================================================
  // Submit Reservation
  // ============================================================================
  reservationForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const resourceId = bookingResourceSelect.value;
    const dateStr = bookingDate.value;
    const startTime = bookingStartTime.value;
    const endTime = bookingEndTime.value;
    const attendees = bookingAttendees.value;
    const purpose = bookingPurpose.value.trim();

    if (endTime <= startTime) {
      showToast("End time must be later than start time.", "error");
      return;
    }

    try {
      const res = await fetch("/api/bookings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resource_id: resourceId,
          user_name: state.currentUser.name,
          user_role: state.currentUser.role,
          booking_date: dateStr,
          start_time: startTime,
          end_time: endTime,
          purpose: purpose,
          attendees: attendees
        })
      });

      const data = await res.json();

      if (res.status === 201) {
        showToast(data.message, "success");
        await loadBookings();
        await loadStats();

        // Find the new booking and open Digital Pass modal
        const newBooking = state.bookings.find((b) => b.booking_code === data.booking_code);
        if (newBooking) {
          openPassModal(newBooking);
        } else {
          switchTab("tab-passbook");
        }
      } else {
        showToast(data.message || "Reservation blocked", "error");
        // Run conflict check to show diagnostic card
        runConflictCheck();
      }
    } catch (err) {
      console.error("Booking error:", err);
      showToast("Error connecting to server.", "error");
    }
  });

  // ============================================================================
  // Day Schedule Modal
  // ============================================================================
  const openScheduleModal = async (resourceId) => {
    state.selectedResourceForSchedule = resourceId;
    const resource = state.resources.find((r) => String(r.id) === String(resourceId));
    if (!resource) return;

    document.getElementById("scheduleModalTitle").textContent = `${resource.name} Schedule`;
    const today = getTodayStr();
    document.getElementById("scheduleModalSubtitle").textContent = `Location: ${resource.location} | Date: ${today}`;

    try {
      const res = await fetch(`/api/schedule/${resourceId}?date=${today}`);
      const bookingsForDay = await res.json();

      renderScheduleTimeline(bookingsForDay);
      scheduleModal.classList.add("active");
    } catch (err) {
      console.error("Schedule error:", err);
    }
  };

  const renderScheduleTimeline = (dayBookings) => {
    const visual = document.getElementById("scheduleTimelineVisual");
    const list = document.getElementById("scheduleBookedList");

    // Hours from 08:00 to 20:00 (12 slots)
    const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19];

    visual.innerHTML = hours.map((hour) => {
      const hStr = String(hour).padStart(2, "0") + ":00";
      const nextHStr = String(hour + 1).padStart(2, "0") + ":00";

      // Check if slot falls in any booking
      const isOccupied = dayBookings.some((b) => {
        return b.start_time < nextHStr && b.end_time > hStr;
      });

      const slotClass = isOccupied ? "slot-booked" : "slot-free";
      const slotText = isOccupied ? "Booked" : "Free";

      return `
        <div class="timeline-slot ${slotClass}">
          <span class="slot-hour">${hour}:00</span>
          <span class="slot-state">${slotText}</span>
        </div>
      `;
    }).join("");

    if (dayBookings.length === 0) {
      list.innerHTML = `
        <p style="text-align: center; color: var(--text-muted); padding: 12px;">
          No reservations scheduled for today. Entire day is completely open!
        </p>
      `;
    } else {
      list.innerHTML = dayBookings.map((b) => `
        <div class="schedule-booking-row">
          <div>
            <strong>${b.start_time} - ${b.end_time}</strong>: ${b.purpose}
            <div style="font-size: 0.75rem; color: var(--text-muted);">By ${b.user_name} (${b.user_role})</div>
          </div>
          <span class="booking-code-pill">${b.booking_code}</span>
        </div>
      `).join("");
    }
  };

  // ============================================================================
  // Digital Room Access Pass Modal
  // ============================================================================
  const openPassModal = (booking) => {
    document.getElementById("ticketBookingCode").textContent = booking.booking_code;
    document.getElementById("ticketRoomName").textContent = booking.resource_name || "Campus Space";
    document.getElementById("ticketRoomLoc").textContent = booking.location || "Academic Complex";
    document.getElementById("ticketDate").textContent = booking.booking_date;
    document.getElementById("ticketTime").textContent = `${booking.start_time} - ${booking.end_time}`;
    document.getElementById("ticketUser").textContent = booking.user_name;
    document.getElementById("ticketRole").textContent = booking.user_role;
    document.getElementById("ticketPurpose").textContent = booking.purpose;

    const stamp = document.getElementById("ticketStatusStamp");
    stamp.textContent = booking.status.toUpperCase();
    if (booking.status === "Approved") {
      stamp.style.color = "var(--approved-color)";
    } else if (booking.status === "Pending") {
      stamp.style.color = "var(--pending-color)";
    } else {
      stamp.style.color = "var(--rejected-color)";
    }

    document.getElementById("ticketPinDigits").textContent = generatePin(booking.id || 101);
    passModal.classList.add("active");
  };

  // Toast Notification Helper
  const showToast = (message, type = "info") => {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let icon = "💡";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "❌";
    if (type === "warning") icon = "⚠️";

    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  };

  // ============================================================================
  // Event Listeners Setup
  // ============================================================================
  const setupEventListeners = () => {
    // Tab Switching
    tabLinks.forEach((link) => {
      link.addEventListener("click", () => switchTab(link.dataset.tab));
    });

    // Persona Selector
    personaSelect.addEventListener("change", (e) => {
      const [name, role] = e.target.value.split("|");
      state.currentUser = { name, role };
      bookingFormUserBadge.textContent = `${name} (${role})`;

      const notice = document.getElementById("adminRoleNotice");
      if (role === "Campus Manager") {
        notice.textContent = `Logged in as ${name} (Campus Manager - Full Admin Clearance)`;
        notice.style.color = "var(--approved-color)";
      } else {
        notice.textContent = `Logged in as ${name} (${role}). Switch to Campus Manager for Admin Actions.`;
        notice.style.color = "var(--pending-color)";
      }

      showToast(`Switched active persona to ${name} (${role})`, "info");
    });

    // Quick Conflict Blocker Test Demo Button
    btnQuickConflictDemo.addEventListener("click", () => {
      switchTab("tab-booking");

      // Set to Grand Innovation Auditorium (ID 1)
      bookingResourceSelect.value = "1";
      bookingDate.value = getTodayStr();

      // Slot 10:30 - 11:30 collides with Dr. Vance's 10:00 - 12:00 booking
      bookingStartTime.value = "10:30";
      bookingEndTime.value = "11:30";
      bookingPurpose.value = "Viva Demonstration: Intentional Collision Test";
      bookingAttendees.value = "20";

      showToast("Pre-filled colliding slot (10:30 - 11:30). Running conflict check...", "warning");
      runConflictCheck();
    });

    // Reset Demo Database
    btnResetDemoData.addEventListener("click", async () => {
      if (!confirm("Reset database back to the clean initial demo state?")) return;
      try {
        const res = await fetch("/api/reset", { method: "POST" });
        const data = await res.json();
        showToast(data.message, "success");
        await loadStats();
        await loadResources();
        await loadBookings();
      } catch (err) {
        showToast("Error resetting database", "error");
      }
    });

    // Category filter chips in Catalog
    categoryChips.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        categoryChips.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        state.activeCategory = chip.dataset.category;
        loadResources();
      });
    });

    // Search input
    catalogSearch.addEventListener("input", () => {
      renderResourceGrid();
    });

    // Quick Date chips
    btnDateToday.addEventListener("click", () => {
      bookingDate.value = getTodayStr();
    });
    btnDateTomorrow.addEventListener("click", () => {
      bookingDate.value = getTomorrowStr();
    });

    // Quick Slot Preset Buttons
    slotPresetButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        bookingStartTime.value = btn.dataset.start;
        bookingEndTime.value = btn.dataset.end;
        slotPresetButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });

    // Live Conflict Checker Button
    btnCheckConflict.addEventListener("click", runConflictCheck);

    // Passbook filter chips
    passbookStatusFilter.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        passbookStatusFilter.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        state.activePassbookStatus = chip.dataset.status;
        loadBookings();
      });
    });

    btnRefreshBookings.addEventListener("click", async () => {
      await loadBookings();
      await loadStats();
      showToast("Bookings refreshed", "info");
    });

    // Modal Close buttons
    btnCloseScheduleModal.addEventListener("click", () => scheduleModal.classList.remove("active"));
    btnCloseScheduleModalFooter.addEventListener("click", () => scheduleModal.classList.remove("active"));
    scheduleModal.addEventListener("click", (e) => {
      if (e.target === scheduleModal) scheduleModal.classList.remove("active");
    });

    btnBookFromSchedule.addEventListener("click", () => {
      scheduleModal.classList.remove("active");
      if (state.selectedResourceForSchedule) {
        selectResourceAndSwitchToBooking(state.selectedResourceForSchedule);
      }
    });

    btnClosePassModal.addEventListener("click", () => passModal.classList.remove("active"));
    btnClosePassModalFooter.addEventListener("click", () => passModal.classList.remove("active"));
    passModal.addEventListener("click", (e) => {
      if (e.target === passModal) passModal.classList.remove("active");
    });
  };

  // Run the application
  initApp();
});
