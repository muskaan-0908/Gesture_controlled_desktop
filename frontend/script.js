const API_URL = "http://127.0.0.1:8000";

let lastAction = null;
let activityLog = [];
let isToggling = false;

document.addEventListener("DOMContentLoaded", () => {
    fetchGestures();
    startStatusPolling();
});

async function fetchGestures() {
    const list = document.getElementById("gestureList");
    const countEl = document.getElementById("totalGestures");

    try {
        const response = await fetch(`${API_URL}/gestures`);
        const data = await response.json();

        list.innerHTML = "";
        const gestureCount = Object.keys(data).length;
        if (countEl) countEl.textContent = gestureCount;

        if (gestureCount === 0) {
            list.innerHTML = '<div class="text-muted text-center p-3">No gestures found. Add one!</div>';
            return;
        }

        for (const [name, action] of Object.entries(data)) {
            const item = document.createElement("div");
            item.className = "gesture-item neon-border-hover";
            item.innerHTML = `
                <span class="gesture-name">${name}</span>
                <span class="gesture-action">${action}</span>
                <i class="fas fa-trash gesture-delete" onclick="deleteGesture('${name}')" title="Delete"></i>
            `;
            list.appendChild(item);
        }
    } catch (error) {
        console.error("Error fetching gestures:", error);
        list.innerHTML = '<div class="text-danger p-3">Failed to load gestures. Backend offline?</div>';
    }
}

async function startRecording() {
    const name = document.getElementById("gname").value;
    const btn = document.querySelector("#addGestureModal button[onclick='startRecording()']");
    const progress = document.getElementById("recordProgress");

    if (!name) {
        showToast("Please enter a gesture name!", "error");
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Requesting...';

    try {
        const response = await fetch(`${API_URL}/start_recording`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name })
        });

        if (response.ok) {
            showToast(`Recording started for '${name}'`, "success");
            progress.textContent = "Recording in progress... Watch camera feed.";
            progress.className = "text-warning small";
        } else {
            showToast("Failed to start recording.", "error");
        }
    } catch (error) {
        console.error("Error:", error);
        showToast("Backend connection failed.", "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-video"></i> Start Recording';
    }
}

async function saveGestureMappings() {
    const name = document.getElementById("gname").value;
    const action = document.getElementById("gaction").value;

    if (!name) {
        showToast("Please enter a gesture name.", "error");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/save_gesture`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name, action: action })
        });

        if (response.ok) {
            showToast("Gesture saved successfully!", "success");
            fetchGestures();

            const modalEl = document.getElementById('addGestureModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();

            document.getElementById("gname").value = "";
        } else {
            showToast("Failed to save gesture.", "error");
        }
    } catch (error) {
        showToast("Backend error.", "error");
    }
}

async function deleteGesture(name) {
    if (!confirm(`Delete gesture '${name}'?`)) return;

    try {
        await fetch(`${API_URL}/delete_gesture`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: name })
        });
        fetchGestures();
        showToast("Gesture deleted.", "success");
    } catch (e) {
        showToast("Error deleting gesture.", "error");
    }
}

async function retrainModel() {
    showToast("Starting training...", "info");
    try {
        const res = await fetch(`${API_URL}/retrain`, { method: "POST" });
        if (res.ok) {
            showToast("Training complete!", "success");
        } else {
            showToast("Training failed.", "error");
        }
    } catch (e) {
        showToast("Error connecting to backend.", "error");
    }
}

async function toggleSystem() {
    const btn = document.getElementById("powerBtn");
    const isRunning = btn.classList.contains("active");
    const endpoint = isRunning ? "/system/stop" : "/system/start";

    try {
        await fetch(`${API_URL}${endpoint}`, { method: "POST" });
    } catch (e) {
        showToast("Failed to toggle system", "error");
    }
}

async function toggleControlMode(event) {
    const checkbox = document.getElementById("controlToggle");
    let newMode;

    if (event && event.target === checkbox) {
        newMode = checkbox.checked;
    } else {
        newMode = !checkbox.checked;
        checkbox.checked = newMode;
    }

    updateControlUI(newMode);
    isToggling = true;

    try {
        await fetch(`${API_URL}/system/mode`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: newMode ? "control" : "passive" })
        });
        setTimeout(() => { isToggling = false; }, 1000);
    } catch (e) {
        showToast("Failed to set mode", "error");
        checkbox.checked = !newMode;
        updateControlUI(!newMode);
        isToggling = false;
    }
}

function updateControlUI(active) {
    const text = document.getElementById("controlStatusText");
    const container = document.getElementById("controlCard");

    if (active) {
        text.textContent = "Enabled";
        text.style.color = "var(--neon-cyan)";
        container.style.borderColor = "var(--neon-cyan)";
        container.style.boxShadow = "0 0 15px rgba(0, 243, 255, 0.1)";
    } else {
        text.textContent = "Disabled";
        text.style.color = "var(--text-secondary)";
        container.style.borderColor = "var(--border-color)";
        container.style.boxShadow = "none";
    }
}

function startStatusPolling() {
    setInterval(async () => {
        try {
            const res = await fetch(`${API_URL}/status`);
            if (res.ok) {
                const status = await res.json();
                updateDashboard(status);
                updateSystemStatus(true, status.camera_on);
            } else {
                updateSystemStatus(false, false);
            }
        } catch (e) {
            updateSystemStatus(false, false);
        }
    }, 1000);
}

function updateSystemStatus(isOnline, isCameraOn) {
    const el = document.getElementById("systemStatus");
    const btn = document.getElementById("powerBtn");
    const controls = document.getElementById("controlToggleContainer");

    if (isOnline) {
        if (isCameraOn) {
            el.innerHTML = '<span class="dot online"></span> Camera Active';
            el.style.borderColor = "var(--neon-green)";

            btn.innerHTML = '<i class="fas fa-power-off"></i> Stop System';
            btn.classList.add("active");
            controls.style.display = "flex";
        } else {
            el.innerHTML = '<span class="dot offline"></span> Camera Idle';
            el.style.borderColor = "var(--border-color)";

            btn.innerHTML = '<i class="fas fa-power-off"></i> Start System';
            btn.classList.remove("active");
            controls.style.display = "none";
        }
    } else {
        el.innerHTML = '<span class="dot offline"></span> Backend Offline';
        el.style.borderColor = "var(--border-color)";
    }
}

function updateDashboard(status) {
    const toggle = document.getElementById("controlToggle");
    if (toggle && status.control_active !== undefined && !isToggling) {
        toggle.checked = status.control_active;
        if (typeof updateControlUI === "function") {
            updateControlUI(status.control_active);
        }
    }

    const statusEl = document.getElementById("modelStatus");
    const accContainer = document.getElementById("accuracyContainer");
    const accBar = document.getElementById("accuracyBar");

    if (status.camera_on) {
        if (status.model_loaded) {
            if (status.confidence > 0) {
                const pct = Math.round(status.confidence * 100);
                statusEl.textContent = `Active (${pct}%)`;
                statusEl.style.color = "var(--neon-green)";

                if (accContainer) accContainer.style.display = "block";
                if (accBar) {
                    accBar.style.width = `${pct}%`;
                    if (pct > 80) accBar.className = "progress-bar bg-success";
                    else if (pct > 50) accBar.className = "progress-bar bg-warning";
                    else accBar.className = "progress-bar bg-danger";
                }
            } else {
                statusEl.textContent = "Listening...";
                statusEl.style.color = "var(--neon-cyan)";
                if (accContainer) accContainer.style.display = "none";
            }
        } else {
            statusEl.textContent = "Model Missing";
            statusEl.style.color = "var(--neon-pink)";
            if (accContainer) accContainer.style.display = "none";
        }
    } else {
        statusEl.textContent = "Offline";
        statusEl.style.color = "var(--text-secondary)";
        if (accContainer) accContainer.style.display = "none";
    }

    const recEl = document.getElementById("recordingStatus");
    if (status.recording) {
        recEl.textContent = "Recording...";
        recEl.style.color = "var(--neon-pink)";
        recEl.classList.add("blink");
    } else {
        recEl.textContent = "Idle";
        recEl.style.color = "var(--text-primary)";
    }

    if (status.action_log && Array.isArray(status.action_log)) {
        updateActivityLog(status.action_log);
    }

    const actionEl = document.getElementById("lastAction");
    if (status.action_log && status.action_log.length > 0) {
        const last = status.action_log[status.action_log.length - 1];
        actionEl.textContent = last.name;
    } else {
        actionEl.textContent = "None";
    }
}

function updateActivityLog(logs) {
    const logEl = document.getElementById("activityLog");

    logEl.innerHTML = "";

    if (logs.length === 0) {
        logEl.innerHTML = '<li class="empty-log">No recent activity</li>';
        return;
    }

    [...logs].reverse().forEach(log => {
        const item = document.createElement("li");
        item.className = "activity-item";
        item.innerHTML = `
            <span class="activity-name">Detected: ${log.name}</span>
            <span class="activity-time">${log.time}</span>
        `;
        logEl.appendChild(item);
    });
}

function showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");

    let colorClass = "bg-dark";
    if (type === "success") colorClass = "bg-success";
    if (type === "error") colorClass = "bg-danger";
    if (type === "info") colorClass = "bg-info";

    toast.className = `toast align-items-center text-white ${colorClass} border-0 show`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
