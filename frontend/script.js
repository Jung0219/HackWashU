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

  setTimeout(() => {
    loading.style.display = "none";

    // Fill results
    injuryEl.textContent = "Knee Scrape";
    proceduresEl.textContent = "Bandaid";
    pricingEl.textContent = "$2";

    // Animate results
    results.classList.add("show");
  }, 2000);
}



uploadInput.addEventListener('change', handleFile);
cameraInput.addEventListener('change', handleFile);

// Optional: close modal when clicking outside
window.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });



