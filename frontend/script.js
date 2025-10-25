const submitBtn = document.getElementById('submitInjury');
const uploadInput = document.getElementById('uploadInput');
const cameraInput = document.getElementById('cameraInput');
const preview = document.getElementById('preview');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const injuryEl = document.getElementById('injury');
const proceduresEl = document.getElementById('procedures');
const pricingEl = document.getElementById('pricing');

const modal = document.getElementById('photoModal');
const takePhotoBtn = document.getElementById('takePhotoBtn');
const uploadPhotoBtn = document.getElementById('uploadPhotoBtn');
const closeModal = document.getElementById('closeModal');

// Open modal
submitBtn.addEventListener('click', () => modal.style.display = 'flex');
// Close modal
closeModal.addEventListener('click', () => modal.style.display = 'none');
// Take photo
takePhotoBtn.addEventListener('click', () => { modal.style.display = 'none'; cameraInput.click(); });
// Upload photo
uploadPhotoBtn.addEventListener('click', () => { modal.style.display = 'none'; uploadInput.click(); });

// Handle image selection
function handleFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  const imageURL = URL.createObjectURL(file);
  preview.src = imageURL;
  preview.style.display = "block";
  loading.style.display = "block";
  submitBtn.style.display = "none";

  // Ensure results are hidden first
  results.classList.remove("show");

  const formData = new FormData();
  formData.append("file", file);

  fetch("http://127.0.0.1:8000/predict", {  // your FastAPI URL
    method: "POST",
    body: formData,
  })
    .then(res => res.json())
    .then(data => {
      loading.style.display = "none";

      // Fill results with backend response
      injuryEl.textContent = data.predicted_class;
      proceduresEl.textContent = "Apply proper first aid"; // optional static field
      pricingEl.textContent = `$${(Math.random() * 30 + 5).toFixed(2)}`; // mock price

      results.classList.add("show");
    })
    .catch(err => {
      loading.style.display = "none";
      alert("Error connecting to backend: " + err.message);
    });

}

uploadInput.addEventListener('change', handleFile);
cameraInput.addEventListener('change', handleFile);

// Optional: close modal when clicking outside
window.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });



