// Define all HTML elements
const submitBtn = document.getElementById('submitInjury');
const uploadInput = document.getElementById('uploadInput');
const cameraInput = document.getElementById('cameraInput');
const preview = document.getElementById('preview');
const loading = document.getElementById('loading');
const modal = document.getElementById('photoModal');
const takePhotoBtn = document.getElementById('takePhotoBtn');
const uploadPhotoBtn = document.getElementById('uploadPhotoBtn');
const closeModal = document.getElementById('closeModal');
const treatmentPlan = document.getElementById('treatmentPlan');
const injuryEl = document.getElementById('injury');
const proceduresEl = document.getElementById('procedures');
const pricingEl = document.getElementById('pricing');
const redoBtn = document.getElementById('redoBtn');

// Modal logic for choosing between taking a photo or uploading one
submitBtn.addEventListener('click', () => modal.style.display = 'flex');
closeModal.addEventListener('click', () => modal.style.display = 'none');
takePhotoBtn.addEventListener('click', () => { modal.style.display = 'none'; cameraInput.click(); });
uploadPhotoBtn.addEventListener('click', () => { modal.style.display = 'none'; uploadInput.click(); });
window.addEventListener('click', e => { if (e.target === modal) modal.style.display = 'none'; });

// Handle file upload or photo capture
function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  const imageURL = URL.createObjectURL(file);
  preview.src = imageURL;
  preview.style.display = "block";
  loading.style.display = "block";
  submitBtn.style.display = "none";
  redoBtn.style.display = "none";
  treatmentPlan.classList.remove("show");

  // Prepare file for sending
  const formData = new FormData();
  formData.append("file", file);

  // Send to Flask backend for classification
  fetch("http://127.0.0.1:5005/predict", {
    method: "POST",
    body: formData,
  })
    .then(res => res.json())
    .then(data => {
      loading.style.display = "none";
      const lastPrediction = data.predicted_class || "Unknown injury";

      // Show preliminary result
      injuryEl.textContent = lastPrediction;
      proceduresEl.textContent = "Fetching hospital pricing...";
      pricingEl.textContent = "...";

      // Chain second API call → fetch hospital pricing
      fetch(`http://localhost:5001/api/pricing?wound_type=${encodeURIComponent(lastPrediction)}`)
        .then(res => res.json())
        .then(priceData => {
          console.log("Full pricing API response:", priceData);
          const fullResponseText = JSON.stringify(priceData, null, 2);

          proceduresEl.textContent = fullResponseText;
          pricingEl.textContent = "See console for full details";

          treatmentPlan.classList.add("show");
          redoBtn.style.display = "inline-block"; // <-- add this line
        })
        .catch(err => {
          console.error("Pricing API error:", err);
          proceduresEl.textContent = "Failed to fetch pricing data.";
          pricingEl.textContent = "N/A";
          treatmentPlan.classList.add("show");
        });
    })
    .catch(err => {
      console.error("Classification API error:", err);
      loading.style.display = "none";
      treatmentPlan.classList.add("show");
      injuryEl.textContent = "Error analyzing image";
      proceduresEl.textContent = "Please try again";
      pricingEl.textContent = "-";
      redoBtn.style.display = "inline-block";
    });
}

// Redo button resets the UI
redoBtn.addEventListener('click', () => {
  preview.style.display = "none";
  preview.src = "";
  submitBtn.style.display = "inline-block";
  redoBtn.style.display = "none";
  treatmentPlan.classList.remove("show");
  injuryEl.textContent = "-";
  proceduresEl.textContent = "-";
  pricingEl.textContent = "-";
});

// Event listeners for upload/camera
uploadInput.addEventListener('change', handleFile);
cameraInput.addEventListener('change', handleFile);
