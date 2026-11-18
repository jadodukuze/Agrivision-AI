const API_BASE = window.AGRIVISION_API_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "agrivision_access_token";
const $ = (id) => document.getElementById(id);
const yearElement = $("year");
if (yearElement) yearElement.textContent = new Date().getFullYear();

const authForm = $("authForm");
const authMode = $("authMode");
const authButton = $("authButton");
const authStatus = $("authStatus");
const accountPanel = $("accountPanel");
const roleWorkspace = $("roleWorkspace");
const caseForm = $("caseForm");
const formStatus = $("formStatus");
const caseButton = $("caseButton");
const preview = $("imagePreview");

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function authHeaders() { return { Authorization: `Bearer ${getToken()}` }; }
function setStatus(element, message, kind = "info") {
  element.textContent = message;
  element.className = `status status--${kind}`;
}
async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  });
  const body = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body?.detail || `Request failed (${response.status}).`);
  return body;
}
function updateAuthMode() {
  const registering = authMode.value === "register";
  $("fullNameField").hidden = !registering;
  $("fullName").required = registering;
  $("password").autocomplete = registering ? "new-password" : "current-password";
  authButton.textContent = registering ? "Create account" : "Sign in";
}
authMode.addEventListener("change", updateAuthMode);
updateAuthMode();

function makeText(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text ?? "";
  return element;
}

async function loadCaseHistory() {
  const target = $("caseHistory");
  target.replaceChildren(makeText("p", "muted", "Loading your cases…"));
  try {
    const cases = await apiRequest("/api/v1/cases/mine");
    target.replaceChildren();
    if (!cases.length) {
      target.append(makeText("p", "muted", "You have not submitted a crop case yet."));
      return;
    }
    cases.forEach((item) => {
      const card = makeText("article", "case-card", "");
      card.append(makeText("h4", "", item.crop_name));
      card.append(makeText("p", "", `Status: ${item.status} · ${new Date(item.created_at).toLocaleString()}`));
      if (item.location) card.append(makeText("p", "", `Location: ${item.location}`));
      target.append(card);
    });
  } catch (error) {
    target.replaceChildren(makeText("p", "status--error", error.message));
  }
}

async function renderPrivateImage(caseId, parent) {
  try {
    const response = await fetch(`${API_BASE}/api/v1/cases/${encodeURIComponent(caseId)}/image`, { headers: authHeaders() });
    if (!response.ok) return;
    const blob = await response.blob();
    const image = document.createElement("img");
    image.className = "preview";
    image.alt = "Crop photo submitted for this case";
    image.src = URL.createObjectURL(blob);
    parent.append(image);
  } catch {
    // The text case record remains available if image retrieval fails.
  }
}

async function loadExpertQueue() {
  const target = $("expertQueue");
  target.replaceChildren(makeText("p", "muted", "Loading crop cases…"));
  try {
    const cases = await apiRequest("/api/v1/expert/cases");
    target.replaceChildren();
    if (!cases.length) {
      target.append(makeText("p", "muted", "There are no crop cases to review."));
      return;
    }
    for (const item of cases) {
      const card = makeText("article", "case-card", "");
      card.append(makeText("h3", "", `${item.crop_name} · ${item.status}`));
      card.append(makeText("p", "", `Farmer: ${item.farmer_name || "Farmer"}`));
      if (item.location) card.append(makeText("p", "", `Location: ${item.location}`));
      if (item.description) card.append(makeText("p", "", item.description));
      await renderPrivateImage(item.id, card);
      const form = document.createElement("form");
      form.className = "review-form";
      const assessmentLabel = makeText("label", "", "Expert assessment");
      const assessment = document.createElement("textarea");
      assessment.required = true;
      assessment.minLength = 5;
      assessment.maxLength = 5000;
      assessment.rows = 3;
      assessmentLabel.append(assessment);
      const nextLabel = makeText("label", "", "Suggested next steps (optional)");
      const nextSteps = document.createElement("textarea");
      nextSteps.maxLength = 5000;
      nextSteps.rows = 2;
      nextLabel.append(nextSteps);
      const submit = makeText("button", "submit-button", "Save expert review");
      submit.type = "submit";
      const status = makeText("p", "status", "");
      form.append(assessmentLabel, nextLabel, submit, status);
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        submit.disabled = true;
        setStatus(status, "Saving review…");
        try {
          await apiRequest(`/api/v1/expert/cases/${encodeURIComponent(item.id)}/review`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ assessment: assessment.value.trim(), recommended_next_steps: nextSteps.value.trim() || null }),
          });
          setStatus(status, "Expert review saved.", "success");
          await loadExpertQueue();
        } catch (error) {
          setStatus(status, error.message, "error");
          submit.disabled = false;
        }
      });
      card.append(form);
      target.append(card);
    }
  } catch (error) {
    target.replaceChildren(makeText("p", "status--error", error.message));
  }
}

async function loadAdminDashboard() {
  try {
    const summary = await apiRequest("/api/v1/admin/summary");
    const metrics = $("adminSummary");
    metrics.replaceChildren();
    Object.entries(summary).forEach(([label, value]) => {
      const card = makeText("div", "metric-card", "");
      card.append(makeText("span", "", label.replaceAll("_", " ")));
      card.append(makeText("strong", "", String(value)));
      metrics.append(card);
    });
    const users = await apiRequest("/api/v1/admin/users");
    const list = $("userList");
    list.replaceChildren();
    users.forEach((user) => {
      const card = makeText("article", "case-card", "");
      card.append(makeText("strong", "", user.full_name));
      card.append(makeText("p", "", `${user.email} · ${user.role} · ${user.is_active ? "Active" : "Inactive"}`));
      list.append(card);
    });
  } catch (error) {
    setStatus(authStatus, error.message, "error");
  }
}

async function loadRoleWorkspace(role) {
  roleWorkspace.hidden = role === "farmer";
  $("expertWorkspace").hidden = !["expert", "admin"].includes(role);
  $("adminWorkspace").hidden = role !== "admin";
  if (["expert", "admin"].includes(role)) await loadExpertQueue();
  if (role === "admin") await loadAdminDashboard();
}

async function loadAccount() {
  const token = getToken();
  if (!token) {
    accountPanel.hidden = true;
    roleWorkspace.hidden = true;
    caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = true; });
    return;
  }
  try {
    const user = await apiRequest("/api/v1/auth/me");
    accountPanel.hidden = false;
    $("welcomeText").textContent = `Welcome, ${user.full_name}`;
    $("roleText").textContent = `Account role: ${user.role}`;
    caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = user.role !== "farmer"; });
    if (user.role === "farmer") await loadCaseHistory();
    else $("caseHistory").replaceChildren(makeText("p", "muted", "The crop submission form is for farmer accounts."));
    await loadRoleWorkspace(user.role);
  } catch (error) {
    localStorage.removeItem(TOKEN_KEY);
    accountPanel.hidden = true;
    roleWorkspace.hidden = true;
    caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = true; });
    setStatus(authStatus, error.message, "error");
  }
}

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(authStatus, "Please wait…");
  authButton.disabled = true;
  const registering = authMode.value === "register";
  const payload = { email: $("email").value.trim(), password: $("password").value };
  if (registering) {
    payload.full_name = $("fullName").value.trim();
    payload.preferred_language = "en";
  }
  try {
    if (registering) {
      const registration = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      });
      const result = await registration.json().catch(() => ({}));
      if (!registration.ok) throw new Error(result.detail || "Could not create account.");
    }
    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: payload.email, password: payload.password }),
    });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || "Sign in failed.");
    localStorage.setItem(TOKEN_KEY, result.access_token);
    authForm.reset();
    authMode.value = "login";
    updateAuthMode();
    setStatus(authStatus, registering ? "Account created. You are signed in." : "Signed in successfully.", "success");
    await loadAccount();
  } catch (error) {
    setStatus(authStatus, error.message, "error");
  } finally {
    authButton.disabled = false;
  }
});

$("logoutButton").addEventListener("click", () => {
  localStorage.removeItem(TOKEN_KEY);
  accountPanel.hidden = true;
  roleWorkspace.hidden = true;
  caseForm.reset();
  caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = true; });
  setStatus(authStatus, "You have signed out.", "success");
});

$("cropImage").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) { preview.hidden = true; preview.removeAttribute("src"); return; }
  if (!["image/jpeg", "image/png", "image/webp"].includes(file.type) || file.size > 5 * 1024 * 1024) {
    event.target.value = "";
    preview.hidden = true;
    setStatus(formStatus, "Choose a JPG, PNG, or WebP image no larger than 5 MB.", "error");
    return;
  }
  if (preview.dataset.objectUrl) URL.revokeObjectURL(preview.dataset.objectUrl);
  preview.dataset.objectUrl = URL.createObjectURL(file);
  preview.src = preview.dataset.objectUrl;
  preview.hidden = false;
});

caseForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!getToken()) { setStatus(formStatus, "Please sign in before submitting a case.", "error"); return; }
  if (!$("cropImage").files[0]) { setStatus(formStatus, "Please choose a crop photo.", "error"); return; }
  caseButton.disabled = true;
  setStatus(formStatus, "Uploading your crop case…");
  try {
    const response = await fetch(`${API_BASE}/api/v1/cases`, { method: "POST", headers: authHeaders(), body: new FormData(caseForm) });
    const result = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(result.detail || "Could not submit your case.");
    setStatus(formStatus, `Case submitted successfully. Reference: ${result.id}. It is awaiting expert review; no AI diagnosis has been made.`, "success");
    caseForm.reset();
    preview.hidden = true;
    preview.removeAttribute("src");
    await loadCaseHistory();
  } catch (error) {
    setStatus(formStatus, error.message, "error");
  } finally {
    caseButton.disabled = false;
  }
});

$("staffForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  button.disabled = true;
  setStatus($("staffStatus"), "Creating account…");
  try {
    await apiRequest("/api/v1/admin/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        full_name: $("staffName").value.trim(),
        email: $("staffEmail").value.trim(),
        password: $("staffPassword").value,
        role: $("staffRole").value,
      }),
    });
    event.currentTarget.reset();
    setStatus($("staffStatus"), "Staff account created.", "success");
    await loadAdminDashboard();
  } catch (error) {
    setStatus($("staffStatus"), error.message, "error");
  } finally {
    button.disabled = false;
  }
});

loadAccount();
