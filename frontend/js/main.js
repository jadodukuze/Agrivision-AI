const API_BASE = window.AGRIVISION_API_URL || "http://127.0.0.1:8000";
const TOKEN_KEY = "agrivision_access_token";
const yearElement = document.getElementById("year");
if (yearElement) yearElement.textContent = new Date().getFullYear();

const authForm = document.getElementById("authForm");
const authMode = document.getElementById("authMode");
const fullNameField = document.getElementById("fullNameField");
const authButton = document.getElementById("authButton");
const authStatus = document.getElementById("authStatus");
const accountPanel = document.getElementById("accountPanel");
const caseForm = document.getElementById("caseForm");
const formStatus = document.getElementById("formStatus");
const caseButton = document.getElementById("caseButton");
const preview = document.getElementById("imagePreview");

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
}
function authHeaders() {
  return { Authorization: `Bearer ${getToken()}` };
}
function updateAuthMode() {
  const registering = authMode.value === "register";
  fullNameField.hidden = !registering;
  document.getElementById("fullName").required = registering;
  document.getElementById("password").autocomplete = registering ? "new-password" : "current-password";
  authButton.textContent = registering ? "Create account" : "Sign in";
}
authMode.addEventListener("change", updateAuthMode);
updateAuthMode();

async function loadAccount() {
  const token = getToken();
  if (!token) {
    accountPanel.hidden = true;
    caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = true; });
    return;
  }
  try {
    const response = await fetch(`${API_BASE}/api/v1/auth/me`, { headers: authHeaders() });
    if (!response.ok) throw new Error("Your session has expired. Please sign in again.");
    const user = await response.json();
    accountPanel.hidden = false;
    document.getElementById("welcomeText").textContent = `Welcome, ${user.full_name}`;
    document.getElementById("roleText").textContent = `Account role: ${user.role}`;
    caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = user.role !== "farmer"; });
    if (user.role !== "farmer") setStatus(formStatus, "Crop case submission is available to farmer accounts.");
    await loadCaseHistory();
  } catch (error) {
    localStorage.removeItem(TOKEN_KEY);
    accountPanel.hidden = true;
    caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = true; });
    setStatus(authStatus, error.message, true);
  }
}

async function loadCaseHistory() {
  const target = document.getElementById("caseHistory");
  target.textContent = "Loading your cases…";
  try {
    const response = await fetch(`${API_BASE}/api/v1/cases/mine`, { headers: authHeaders() });
    if (!response.ok) throw new Error("Could not load case history.");
    const cases = await response.json();
    target.replaceChildren();
    if (!cases.length) {
      target.textContent = "You have not submitted a crop case yet.";
      return;
    }
    cases.forEach((item) => {
      const card = document.createElement("article");
      card.className = "case-item";
      const title = document.createElement("strong");
      title.textContent = item.crop_name;
      const details = document.createElement("p");
      details.textContent = `Status: ${item.status} · ${new Date(item.created_at).toLocaleString()}`;
      card.append(title, details);
      target.append(card);
    });
  } catch (error) {
    target.textContent = error.message;
  }
}

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(authStatus, "Please wait…");
  authButton.disabled = true;
  const registering = authMode.value === "register";
  const payload = {
    email: document.getElementById("email").value.trim(),
    password: document.getElementById("password").value,
  };
  if (registering) {
    payload.full_name = document.getElementById("fullName").value.trim();
    payload.preferred_language = "en";
  }
  try {
    if (registering) {
      const registration = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      });
      if (!registration.ok) {
        const problem = await registration.json();
        throw new Error(problem.detail || "Could not create account.");
      }
    }
    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Sign in failed.");
    localStorage.setItem(TOKEN_KEY, result.access_token);
    authForm.reset();
    authMode.value = "login";
    updateAuthMode();
    setStatus(authStatus, registering ? "Account created. You are signed in." : "Signed in successfully.");
    await loadAccount();
  } catch (error) {
    setStatus(authStatus, error.message, true);
  } finally {
    authButton.disabled = false;
  }
});

document.getElementById("logoutButton").addEventListener("click", () => {
  localStorage.removeItem(TOKEN_KEY);
  accountPanel.hidden = true;
  caseForm.reset();
  caseForm.querySelectorAll("input,select,textarea,button").forEach((item) => { item.disabled = true; });
  setStatus(authStatus, "You have signed out.");
});

document.getElementById("cropImage").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) { preview.hidden = true; preview.removeAttribute("src"); return; }
  const allowed = ["image/jpeg", "image/png", "image/webp"];
  if (!allowed.includes(file.type) || file.size > 5 * 1024 * 1024) {
    event.target.value = "";
    preview.hidden = true;
    setStatus(formStatus, "Choose a JPG, PNG, or WebP image no larger than 5 MB.", true);
    return;
  }
  preview.src = URL.createObjectURL(file);
  preview.hidden = false;
});

caseForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!getToken()) { setStatus(formStatus, "Please sign in before submitting a case.", true); return; }
  const file = document.getElementById("cropImage").files[0];
  if (!file) { setStatus(formStatus, "Please choose a crop photo.", true); return; }
  caseButton.disabled = true;
  setStatus(formStatus, "Uploading your crop case…");
  try {
    const response = await fetch(`${API_BASE}/api/v1/cases`, {
      method: "POST", headers: authHeaders(), body: new FormData(caseForm),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Could not submit your case.");
    setStatus(formStatus, `Case submitted successfully. Reference: ${result.id}. It is awaiting review; no AI diagnosis has been made.`);
    caseForm.reset();
    preview.hidden = true;
    preview.removeAttribute("src");
    await loadCaseHistory();
  } catch (error) {
    setStatus(formStatus, error.message, true);
  } finally {
    caseButton.disabled = false;
  }
});

loadAccount();
