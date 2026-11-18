const yearElement = document.getElementById("year");
if (yearElement) yearElement.textContent = new Date().getFullYear();

const caseForm = document.getElementById("caseForm");
const imageInput = document.getElementById("cropImage");
const imagePreview = document.getElementById("imagePreview");
const formStatus = document.getElementById("formStatus");

const MAX_IMAGE_BYTES = 5 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

function showStatus(message, kind = "info") {
  if (!formStatus) return;
  formStatus.textContent = message;
  formStatus.className = `status status--${kind}`;
}

if (imageInput && imagePreview) {
  imageInput.addEventListener("change", () => {
    const file = imageInput.files?.[0];
    imagePreview.removeAttribute("src");
    imagePreview.hidden = true;

    if (!file) return;
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      imageInput.value = "";
      showStatus("Please choose a JPG, PNG, or WebP image.", "error");
      return;
    }
    if (file.size > MAX_IMAGE_BYTES) {
      imageInput.value = "";
      showStatus("The image must be 5 MB or smaller.", "error");
      return;
    }

    imagePreview.src = URL.createObjectURL(file);
    imagePreview.hidden = false;
    showStatus("Image selected. Check that it clearly shows the crop concern.", "info");
  });
}

if (caseForm) {
  caseForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!caseForm.reportValidity()) return;

    const submitButton = caseForm.querySelector('button[type="submit"]');
    const apiUrl = caseForm.dataset.api;
    const formData = new FormData(caseForm);

    if (!apiUrl) {
      showStatus("The API address is not configured for this page.", "error");
      return;
    }

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Submitting…";
    }
    showStatus("Sending your crop photo securely to the development API…", "info");

    try {
      const response = await fetch(apiUrl, { method: "POST", body: formData });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = typeof payload.detail === "string" ? payload.detail : "The server could not accept this submission.";
        throw new Error(detail);
      }

      showStatus(
        `Photo received. Reference: ${payload.case_id}. This is not an AI diagnosis; an agricultural expert must assess the case.`,
        "success"
      );
      caseForm.reset();
      if (imagePreview) {
        imagePreview.removeAttribute("src");
        imagePreview.hidden = true;
      }
    } catch (error) {
      showStatus(error.message || "Could not contact the API. Check that the backend is running.", "error");
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.textContent = "Submit crop case";
      }
    }
  });
}
