const API_BASE = document.getElementById("caseForm")?.dataset.apiBase || "http://127.0.0.1:8000";
const TOKEN_KEY = "agrivision_access_token";
const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

const $ = (id) => document.getElementById(id);
const yearElement = $("year");
const registerForm = $("registerForm");
const loginForm = $("loginForm");
const authForms = $("authForms");
const signedInPanel = $("signedInPanel");
const signedInText = $("signedInText");
const logoutButton = $("logoutButton");
const accountStatus = $("accountStatus");
const signInPrompt = $("signInPrompt");
const farmerWorkspace = $("farmerWorkspace");
const expertWorkspace = $("expertWorkspace");
const adminWorkspace = $("adminWorkspace");
const caseForm = $("caseForm");
const imageInput = $("cropImage");
const imagePreview = $("imagePreview");
const formStatus = $("formStatus");
const caseHistory = $("caseHistory");
const expertCases = $("expertCases");

if (yearElement) yearElement.textContent = new Date().getFullYear();

function token() {
  return sessionStorage.getItem(TOKEN_KEY);
}

function showStatus(element, message, kind = "info") {
  if (!element) return;
  element.textContent = message;
  element.className = `status status--${kind}`;
}

async function api(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (token()) headers.set("Authorization", `Bearer ${token()}`);
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(typeof payload.detail === "string" ? payload.detail : "The request could not be completed.");
  }
  return payload;
}

function showWorkspace(user) {
  authForms.hidden = true;
  signedInPanel.hidden = false;
  signedInText.textContent = `Signed in as ${user.full_name} (${user.role}).`;
  signInPrompt.hidden = true;
  farmerWorkspace.hidden = user.role !== "farmer";
  expertWorkspace.hidden = !["expert", "admin"].includes(user.role);
  adminWorkspace.hidden = user.role !== "admin";

  if (user.role === "farmer") loadFarmerCases();
  if (["expert", "admin"].includes(user.role)) loadExpertCases();
  if (user.role === "admin") loadAdminSummary();
}

function clearSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  authForms.hidden = false;
  signedInPanel.hidden = true;
  signInPrompt.hidden = false;
  farmerWorkspace.hidden = true;
  expertWorkspace.hidden = true;
  adminWorkspace.hidden = true;
  if (caseHistory) caseHistory.replaceChildren();
  if (expertCases) expertCases.replaceChildren();
}

async function verifySession() {
  if (!token()) return;
  try {
    const user = await api("/api/v1/auth/me");
    showWorkspace(user);
  } catch {
    clearSession();
    showStatus(accountStatus, "Your session expired. Please sign in again.", "error");
  }
}

if (registerForm) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!registerForm.reportValidity()) return;
    const button = registerForm.querySelector('button[type="submit"]');
    button.disabled = true;
    showStatus(accountStatus, "Creating your farmer account…");
    try {
      const data = Object.fromEntries(new FormData(registerForm).entries());
      await api("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      loginForm.elements.email.value = data.email;
      registerForm.reset();
      showStatus(accountStatus, "Account created. Sign in with your email and password.", "success");
    } catch (error) {
      showStatus(accountStatus, error.message, "error");
    } finally {
      button.disabled = false;
    }
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!loginForm.reportValidity()) return;
    const button = loginForm.querySelector('button[type="submit"]');
    button.disabled = true;
    showStatus(accountStatus, "Signing in…");
    try {
      const data = Object.fromEntries(new FormData(loginForm).entries());
      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(payload.detail || "Sign in failed.");
      sessionStorage.setItem(TOKEN_KEY, payload.access_token);
      showWorkspace(payload.user);
      loginForm.reset();
      showStatus(accountStatus, "You are signed in.", "success");
    } catch (error) {
      showStatus(accountStatus, error.message, "error");
    } finally {
      button.disabled = false;
    }
  });
}

if (logoutButton) {
  logoutButton.addEventListener("click", () => {
    clearSession();
    showStatus(accountStatus, "You have signed out.", "info");
  });
}

if (imageInput && imagePreview) {
  imageInput.addEventListener("change", () => {
    const file = imageInput.files?.[0];
    imagePreview.removeAttribute("src");
    imagePreview.hidden = true;
    if (!file) return;
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      imageInput.value = "";
      showStatus(formStatus, "Please choose a JPG, PNG, or WebP image.", "error");
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      imageInput.value = "";
      showStatus(formStatus, "The image must be 5 MB or smaller.", "error");
      return;
    }
    imagePreview.src = URL.createObjectURL(file);
    imagePreview.hidden = false;
    showStatus(formStatus, "Image selected. Check that it clearly shows the crop concern.", "info");
  });
}

if (caseForm) {
  caseForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!caseForm.reportValidity()) return;
    if (!token()) {
      showStatus(formStatus, "Please sign in before submitting a case.", "error");
      return;
    }
    const button = caseForm.querySelector('button[type="submit"]');
    button.disabled = true;
    showStatus(formStatus, "Submitting your crop photo…");
    try {
      const payload = await api("/api/v1/cases", {
        method: "POST",
        body: new FormData(caseForm),
      });
      showStatus(formStatus, `Case #${payload.id} received and waiting for expert review. This is not an AI diagnosis.`, "success");
      caseForm.reset();
      imagePreview.removeAttribute("src");
      imagePreview.hidden = true;
      await loadFarmerCases();
    } catch (error) {
      showStatus(formStatus, error.message, "error");
    } finally {
      button.disabled = false;
    }
  });
}

function makeTextElement(tag, text, className = "") {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) element.className = className;
  return element;
}

async function loadFarmerCases() {
  if (!caseHistory || !token()) return;
  caseHistory.replaceChildren(makeTextElement("p", "Loading your cases…", "muted"));
  try {
    const cases = await api("/api/v1/cases/mine");
    caseHistory.replaceChildren();
    if (!cases.length) {
      caseHistory.append(makeTextElement("p", "You have not submitted any cases yet.", "muted"));
      return;
    }
    for (const item of cases) {
      const card = document.createElement("article");
      card.className = "case-card";
      card.append(
        makeTextElement("h4", `Case #${item.id} · ${item.crop_name}`),
        makeTextElement("p", `Status: ${item.status.replaceAll("_", " ")}`),
        makeTextElement("p", `Submitted: ${new Date(item.created_at).toLocaleString()}`)
      );
      for (const review of item.reviews || []) {
        card.append(makeTextElement("p", `Expert assessment: ${review.assessment}`));
        if (review.recommended_next_steps) card.append(makeTextElement("p", `Next steps: ${review.recommended_next_steps}`));
      }
      caseHistory.append(card);
    }
  } catch (error) {
    caseHistory.replaceChildren(makeTextElement("p", error.message, "status--error"));
  }
}

async function loadExpertCases() {
  if (!expertCases || !token()) return;
  expertCases.replaceChildren(makeTextElement("p", "Loading cases…", "muted"));
  try {
    const cases = await api("/api/v1/expert/cases");
    expertCases.replaceChildren();
    if (!cases.length) {
      expertCases.append(makeTextElement("p", "There are no submitted cases yet.", "muted"));
      return;
    }
    for (const item of cases) {
      const card = document.createElement("article");
      card.className = "case-card";
      card.append(
        makeTextElement("h3", `Case #${item.id} · ${item.crop_name}`),
        makeTextElement("p", `Farmer: ${item.farmer_name}`),
        makeTextElement("p", `Location: ${item.location || "Not provided"}`),
        makeTextElement("p", `Concern: ${item.description || "Not provided"}`),
        makeTextElement("p", `Status: ${item.status.replaceAll("_", " ")}`)
      );
      if (item.status !== "reviewed") {
        const form = document.createElement("form");
        form.className = "review-form";
        const assessmentLabel = makeTextElement("label", "Expert assessment");
        const assessment = document.createElement("textarea");
        assessment.required = true;
        assessment.minLength = 5;
        assessment.maxLength = 5000;
        assessment.rows = 3;
        assessmentLabel.append(assessment);
        const nextLabel = makeTextElement("label", "Recommended next steps (optional)");
        const next = document.createElement("textarea");
        next.maxLength = 3000;
        next.rows = 2;
        nextLabel.append(next);
        const submit = makeTextElement("button", "Save expert review", "submit-button");
        submit.type = "submit";
        form.append(assessmentLabel, nextLabel, submit);
        form.addEventListener("submit", async (event) => {
          event.preventDefault();
          if (!form.reportValidity()) return;
          submit.disabled = true;
          try {
            await api(`/api/v1/expert/cases/${item.id}/review`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                assessment: assessment.value,
                recommended_next_steps: next.value || null,
              }),
            });
            await loadExpertCases();
          } catch (error) {
            card.append(makeTextElement("p", error.message, "status--error"));
            submit.disabled = false;
          }
        });
        card.append(form);
      }
      for (const review of item.reviews || []) {
        card.append(makeTextElement("p", `Previous assessment: ${review.assessment}`));
      }
      expertCases.append(card);
    }
  } catch (error) {
    expertCases.replaceChildren(makeTextElement("p", error.message, "status--error"));
  }
}

async function loadAdminSummary() {
  const target = $("adminSummary");
  if (!target) return;
  target.replaceChildren(makeTextElement("p", "Loading summary…", "muted"));
  try {
    const summary = await api("/api/v1/admin/summary");
    target.replaceChildren();
    for (const [label, value] of Object.entries(summary)) {
      const card = document.createElement("article");
      card.className = "metric-card";
      card.append(makeTextElement("span", label.replaceAll("_", " ")), makeTextElement("strong", String(value)));
      target.append(card);
    }
  } catch (error) {
    target.replaceChildren(makeTextElement("p", error.message, "status--error"));
  }
}

const staffForm = $("staffForm");
if (staffForm) {
  staffForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!staffForm.reportValidity()) return;
    const button = staffForm.querySelector('button[type="submit"]');
    button.disabled = true;
    showStatus($("staffStatus"), "Creating staff account…");
    try {
      const data = Object.fromEntries(new FormData(staffForm).entries());
      const created = await api("/api/v1/admin/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      staffForm.reset();
      showStatus($("staffStatus"), `Created ${created.role} account for ${created.full_name}.`, "success");
      await loadAdminSummary();
    } catch (error) {
      showStatus($("staffStatus"), error.message, "error");
    } finally {
      button.disabled = false;
    }
  });
}

$("refreshHistory")?.addEventListener("click", loadFarmerCases);
$("refreshExpertCases")?.addEventListener("click", loadExpertCases);
verifySession();
