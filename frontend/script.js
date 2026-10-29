// Backend address (FastAPI running locally)
const API_BASE = "http://127.0.0.1:8000";

// GitHub Pages par backend nahi chalta, is liye wahan demo mode (localStorage) use hoga
const DEMO_MODE = window.location.hostname.endsWith("github.io");
const STORAGE_KEY = "lab-mid-term-submissions";

const FIELDS = {
  name: "Name",
  registration_number: "Registration number",
  assignment_title: "Assignment title",
  submission_url: "Submission URL",
};

const form = document.getElementById("submission-form");
const submitBtn = document.getElementById("submit-btn");
const btnText = submitBtn.querySelector(".btn-text");
const formMessage = document.getElementById("form-message");
const badge = document.getElementById("mode-badge");
const modeText = document.getElementById("mode-text");
const table = document.getElementById("submissions-table");
const tbody = document.getElementById("submissions-body");
const emptyState = document.getElementById("empty-state");
const countEl = document.getElementById("count");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");

// ---------- Validation (same rules as backend) ----------
function isValidUrl(value) {
  if (/\s/.test(value)) return false;
  try {
    const url = new URL(value);
    return (url.protocol === "http:" || url.protocol === "https:") && url.hostname !== "";
  } catch {
    return false;
  }
}

function validate(data) {
  const errors = {};
  for (const field in FIELDS) {
    if (!data[field]) {
      errors[field] = `${FIELDS[field]} is required`;
    }
  }
  if (data.name && !/^[A-Za-z][A-Za-z .'-]*$/.test(data.name)) {
    errors.name = "Name must contain only letters";
  }
  if (data.assignment_title && !/[A-Za-z]/.test(data.assignment_title)) {
    errors.assignment_title = "Assignment title must contain letters";
  }
  if (data.submission_url && !isValidUrl(data.submission_url)) {
    errors.submission_url = "Submission URL must be a valid http or https URL";
  }
  return errors;
}

// ---------- UI helpers ----------
function clearFieldError(field) {
  document.getElementById(field).classList.remove("invalid");
  document.getElementById(`${field}-error`).textContent = "";
}

function clearErrors() {
  for (const field in FIELDS) {
    clearFieldError(field);
  }
  formMessage.className = "message";
  formMessage.textContent = "";
}

function showFieldErrors(errors) {
  for (const field in errors) {
    document.getElementById(field).classList.add("invalid");
    document.getElementById(`${field}-error`).textContent = errors[field];
  }
}

function showMessage(text, type) {
  formMessage.textContent = text;
  formMessage.className = type === "success" ? "message success" : "message error-msg";
}

function setBadge(text, state) {
  modeText.textContent = text;
  badge.className = `status ${state}`;
}

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle("loading", isLoading);
  btnText.textContent = isLoading ? "Submitting..." : "Submit Assignment";
}

function updateProgress() {
  const total = Object.keys(FIELDS).length;
  let filled = 0;
  for (const field in FIELDS) {
    if (document.getElementById(field).value.trim()) filled++;
  }
  progressBar.style.width = `${(filled / total) * 100}%`;
  progressText.textContent = `${filled}/${total}`;
}

// Typing par progress update ho aur us field ka error hat jaye
for (const field in FIELDS) {
  document.getElementById(field).addEventListener("input", () => {
    clearFieldError(field);
    updateProgress();
  });
}

// ---------- Demo mode storage ----------
function getLocal() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
}

function saveLocal(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
}

// ---------- Render list ----------
function initials(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

function addCell(row, label, content) {
  const td = document.createElement("td");
  td.setAttribute("data-label", label);
  if (content instanceof Node) {
    td.appendChild(content);
  } else {
    td.textContent = content;
  }
  row.appendChild(td);
}

function render(submissions) {
  tbody.innerHTML = "";
  countEl.textContent = submissions.length;
  const hasData = submissions.length > 0;
  table.hidden = !hasData;
  emptyState.hidden = hasData;

  submissions.forEach((s, index) => {
    const row = document.createElement("tr");
    row.style.animationDelay = `${index * 0.05}s`;

    const person = document.createElement("div");
    person.className = "person";
    const avatar = document.createElement("span");
    avatar.className = "avatar";
    avatar.textContent = initials(s.name);
    const nameText = document.createElement("span");
    nameText.textContent = s.name;
    person.append(avatar, nameText);

    const reg = document.createElement("span");
    reg.className = "reg";
    reg.textContent = s.registration_number;

    const link = document.createElement("a");
    link.href = s.submission_url;
    link.textContent = s.submission_url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";

    addCell(row, "#", index + 1);
    addCell(row, "Student", person);
    addCell(row, "Reg. No", reg);
    addCell(row, "Title", s.assignment_title);
    addCell(row, "URL", link);
    addCell(row, "Submitted At", new Date(s.submitted_at).toLocaleString());
    tbody.appendChild(row);
  });
}

// ---------- Load submissions ----------
async function loadSubmissions() {
  if (DEMO_MODE) {
    setBadge("Demo Mode (GitHub Pages)", "demo");
    render(getLocal());
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/submissions`);
    if (!response.ok) throw new Error("Request failed");
    render(await response.json());
    setBadge("Connected to API", "online");
  } catch {
    setBadge("Backend Offline", "offline");
    showMessage("Cannot connect to backend. Start it with: uvicorn backend.main:app --reload", "error");
  }
}

// ---------- Submit ----------
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearErrors();

  const data = {};
  for (const field in FIELDS) {
    data[field] = document.getElementById(field).value.trim();
  }

  const errors = validate(data);
  if (Object.keys(errors).length > 0) {
    showFieldErrors(errors);
    showMessage("Submission rejected. Please fix the highlighted fields.", "error");
    document.getElementById(Object.keys(errors)[0]).focus();
    return;
  }

  setLoading(true);

  if (DEMO_MODE) {
    const list = getLocal();
    list.push({ ...data, id: list.length + 1, submitted_at: new Date().toISOString() });
    saveLocal(list);
    form.reset();
    updateProgress();
    showMessage("Submission saved successfully (demo mode)", "success");
    render(list);
    setLoading(false);
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/submissions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const result = await response.json();

    if (response.status === 201) {
      form.reset();
      updateProgress();
      showMessage(result.message, "success");
      await loadSubmissions();
    } else if (response.status === 422) {
      showMessage(result.errors.join(". "), "error");
    } else {
      showMessage("Unexpected error. Please try again.", "error");
    }
  } catch {
    showMessage("Cannot connect to backend. Is the server running?", "error");
  } finally {
    setLoading(false);
  }
});

// ---------- 3D interaction (sirf mouse wale devices par) ----------
const canAnimate =
  window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (canAnimate) {
  const stack = document.getElementById("stack");
  const formCard = document.getElementById("form-card");

  // 3D stack mouse ke saath ghoomta hai
  window.addEventListener("mousemove", (e) => {
    const x = e.clientX / window.innerWidth - 0.5;
    const y = e.clientY / window.innerHeight - 0.5;
    stack.style.transform =
      `rotateX(${(55 - y * 14).toFixed(2)}deg) rotateZ(${(-35 + x * 18).toFixed(2)}deg)`;
  });

  // Form card halka sa tilt hota hai
  formCard.addEventListener("mousemove", (e) => {
    const rect = formCard.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    formCard.style.transform =
      `perspective(1200px) rotateX(${(-y * 4).toFixed(2)}deg) rotateY(${(x * 4).toFixed(2)}deg)`;
  });
  formCard.addEventListener("mouseleave", () => {
    formCard.style.transform = "";
  });
}

updateProgress();
loadSubmissions();