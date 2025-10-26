// define all html elements as variables based on their ids
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

// modal logic for choosing between taking a photo or uploading one
submitBtn.addEventListener('click', () => modal.style.display = 'flex');
closeModal.addEventListener('click', () => modal.style.display = 'none');
takePhotoBtn.addEventListener('click', () => { modal.style.display = 'none'; cameraInput.click(); });
uploadPhotoBtn.addEventListener('click', () => { modal.style.display = 'none'; uploadInput.click(); });
window.addEventListener('click', e => { if (e.target === modal) modal.style.display = 'none'; });

// handle file upload or photo capture
function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  const imageURL = URL.createObjectURL(file);
  preview.src = imageURL;
  preview.style.display = "block";
  loading.style.display = "block";
  submitBtn.style.display = "none";
  redoBtn.style.display = "none";

  // hide treatment plan first
  treatmentPlan.classList.remove("show");

  // prepare file for sending
  const formData = new FormData();
  formData.append("file", file);

  // send to backend for prediction
  fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    body: formData,
  })
    .then(res => res.json())
    .then(data => {
      loading.style.display = "none";

      // update UI with backend response
      injuryEl.textContent = data.predicted_class || "Unknown injury";
      proceduresEl.textContent = "Apply proper first aid";
      pricingEl.textContent = `$${(Math.random() * 30 + 5).toFixed(2)}`;

      // show animated treatment plan
      treatmentPlan.classList.add("show");
    })
    .catch(err => {
      console.error("Error:", err);
      loading.style.display = "none";
      treatmentPlan.classList.add("show");
      injuryEl.textContent = "Error analyzing image";
      proceduresEl.textContent = "Please try again";
      pricingEl.textContent = "-";
      redoBtn.style.display = "inline-block";
    });
}

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

// event listeners for file uploads
uploadInput.addEventListener('change', handleFile);
cameraInput.addEventListener('change', handleFile);
