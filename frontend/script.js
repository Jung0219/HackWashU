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
const redoBtn = document.getElementById('redoBtn');
const zipSection = document.getElementById('zipSection');
const zipInput = document.getElementById('zipInput');
const searchHospitalsBtn = document.getElementById('searchHospitals');
const injuryInfo = document.getElementById('injuryInfo');
const detectedInjury = document.getElementById('detectedInjury');
const mapSection = document.getElementById('mapSection');
const hospital1Card = document.getElementById('hospital1Card');
const hospital2Card = document.getElementById('hospital2Card');
const savingsSummary = document.getElementById('savingsSummary');
const savingsText = document.getElementById('savingsText');

// Webcam elements
const webcamModal = document.getElementById('webcamModal');
const webcamVideo = document.getElementById('webcamVideo');
const webcamCanvas = document.getElementById('webcamCanvas');
const capturePhotoBtn = document.getElementById('capturePhotoBtn');
const retakePhotoBtn = document.getElementById('retakePhotoBtn');
const confirmPhotoBtn = document.getElementById('confirmPhotoBtn');
const closeWebcamModal = document.getElementById('closeWebcamModal');

// Store wound type globally
let currentWoundType = '';
let map = null;
let markers = [];
let mapInitialized = false;
let webcamStream = null;

// Hospital data
const hospitals = [
  {
    name: "Barnes Jewish St. Peters Hospital",
    location: "St. Peters, MO 63376",
    lat: 38.7881,
    lng: -90.6298,
    api_id: "barnes_jewish",
    cardId: "hospital1Card"
  },
  {
    name: "Mercy Hospital Lincoln",
    location: "Troy, MO 63379",
    lat: 38.9728,
    lng: -90.9768,
    api_id: "lincoln",
    cardId: "hospital2Card"
  }
];

// Setup custom marker click handlers (no Google Maps needed)
function setupMarkerClickHandlers() {
  const markerElements = document.querySelectorAll('.hospital-marker');
  markerElements.forEach((marker, index) => {
    marker.addEventListener('click', () => {
      const cardId = hospitals[index].cardId;
      const card = document.getElementById(cardId);
      card.classList.add('active');
      
      // Remove active from the other card
      const otherCard = index === 0 ? hospital2Card : hospital1Card;
      otherCard.classList.remove('active');
    });
  });
}

// Modal logic for choosing between taking a photo or uploading one
submitBtn.addEventListener('click', () => modal.style.display = 'flex');
closeModal.addEventListener('click', () => modal.style.display = 'none');
takePhotoBtn.addEventListener('click', () => {
  modal.style.display = 'none';
  webcamModal.style.display = 'flex';
  startWebcam();
});
uploadPhotoBtn.addEventListener('click', () => { modal.style.display = 'none'; uploadInput.click(); });
window.addEventListener('click', e => { if (e.target === modal) modal.style.display = 'none'; });

// Webcam modal logic
closeWebcamModal.addEventListener('click', () => {
  stopWebcam();
  webcamModal.style.display = 'none';
});

window.addEventListener('click', e => {
  if (e.target === webcamModal) {
    stopWebcam();
    webcamModal.style.display = 'none';
  }
});

// Start webcam stream
function startWebcam() {
  const constraints = {
    video: {
      facingMode: 'environment',
      width: { ideal: 1280 },
      height: { ideal: 720 }
    },
    audio: false
  };

  navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
      webcamStream = stream;
      webcamVideo.srcObject = stream;
      webcamVideo.style.display = 'block';
      
      // Reset buttons
      capturePhotoBtn.style.display = 'inline-block';
      retakePhotoBtn.style.display = 'none';
      confirmPhotoBtn.style.display = 'none';
    })
    .catch(err => {
      console.error('Error accessing webcam:', err);
      alert('Unable to access webcam. Please check permissions and try again.');
      webcamModal.style.display = 'none';
      modal.style.display = 'flex';
    });
}

// Stop webcam stream
function stopWebcam() {
  if (webcamStream) {
    webcamStream.getTracks().forEach(track => track.stop());
    webcamStream = null;
  }
  webcamVideo.srcObject = null;
}

// Capture photo from webcam
capturePhotoBtn.addEventListener('click', () => {
  const context = webcamCanvas.getContext('2d');
  webcamCanvas.width = webcamVideo.videoWidth;
  webcamCanvas.height = webcamVideo.videoHeight;
  
  context.drawImage(webcamVideo, 0, 0);
  
  // Display captured image in video area
  webcamVideo.style.display = 'none';
  webcamCanvas.style.display = 'block';
  
  // Show retake and confirm buttons
  capturePhotoBtn.style.display = 'none';
  retakePhotoBtn.style.display = 'inline-block';
  confirmPhotoBtn.style.display = 'inline-block';
});

// Retake photo (go back to live stream)
retakePhotoBtn.addEventListener('click', () => {
  webcamVideo.style.display = 'block';
  webcamCanvas.style.display = 'none';
  
  capturePhotoBtn.style.display = 'inline-block';
  retakePhotoBtn.style.display = 'none';
  confirmPhotoBtn.style.display = 'none';
});

// Confirm and use photo
confirmPhotoBtn.addEventListener('click', () => {
  webcamCanvas.toBlob(blob => {
    const file = new File([blob], 'webcam-photo.jpg', { type: 'image/jpeg' });
    
    stopWebcam();
    webcamModal.style.display = 'none';
    
    // Process the captured image
    const event = {
      target: {
        files: [file]
      }
    };
    handleFile(event);
  }, 'image/jpeg', 0.95);
});

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
  zipSection.style.display = "none";
  injuryInfo.style.display = "none";
  mapSection.style.display = "none";

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
      currentWoundType = data.predicted_class || "Unknown injury";

      // Show wound type and ZIP section
      detectedInjury.textContent = currentWoundType;
      injuryInfo.style.display = "block";
      zipSection.style.display = "block";
      redoBtn.style.display = "inline-block";
    })
    .catch(err => {
      console.error("Classification API error:", err);
      loading.style.display = "none";
      detectedInjury.textContent = "Error analyzing image";
      injuryInfo.style.display = "block";
      redoBtn.style.display = "inline-block";
    });
}

// Search for hospitals
searchHospitalsBtn.addEventListener('click', () => {
  const zipCode = zipInput.value.trim();
  
  if (zipCode.length !== 5) {
    alert('Please enter a valid 5-digit ZIP code');
    return;
  }

  // Show map section
  mapSection.style.display = "block";
  
  // Setup marker click handlers
  setTimeout(() => {
    setupMarkerClickHandlers();
    mapSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);

  // Reset hospital cards
  resetHospitalCards();
  
  // Load comparison pricing
  loadComparisonPricing();
});

// Reset hospital cards
function resetHospitalCards() {
  [hospital1Card, hospital2Card].forEach(card => {
    card.classList.remove('active');
    const body = card.querySelector('.hospital-body');
    body.innerHTML = '<p class="loading-text">Click hospital card to view pricing details...</p>';
  });
  savingsSummary.style.display = 'none';
}

// Load hospital data when card is clicked
function loadHospitalData(cardId) {
  const card = document.getElementById(cardId);
  card.classList.add('active');
  
  // Just highlight - data already loaded via loadComparisonPricing
  // This function is for visual feedback on click
}

// Display pricing in hospital card
function displayHospitalPricing(card, hospitalData) {
  const body = card.querySelector('.hospital-body');
  const procedures = hospitalData.procedures || [];

  if (procedures.length === 0) {
    body.innerHTML = '<p>No procedures found for this injury type.</p>';
    return;
  }

  let html = '<h4 style="margin: 0 0 10px 0; color: #1e3a8a;">Available Procedures:</h4>';
  html += '<ul class="procedures-list">';

  procedures.forEach(proc => {
    const estimate = proc.pricing?.estimate || 0;
    html += `
      <li>
        <span class="procedure-name">${proc.name}</span>
        <span class="procedure-price">$${estimate.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
      </li>
    `;
  });

  html += '</ul>';

  // Always show total estimate if available
  const total = hospitalData.total_estimate || 0;
  if (total > 0) {
    html += `
      <div class="total-estimate">
        <h4>Total Estimated Cost:</h4>
        <p>$${total.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
      </div>
    `;
  }

  body.innerHTML = html;
}

// Load comparison pricing (both hospitals)
function loadComparisonPricing() {
  fetch(`http://localhost:5001/api/pricing/compare?wound_type=${encodeURIComponent(currentWoundType)}`)
    .then(res => res.json())
    .then(data => {
      console.log('Comparison data:', data);
      
      // Display pricing for each hospital
      if (data.comparison && data.comparison.length >= 2) {
        // Barnes Jewish (first hospital)
        displayHospitalPricing(hospital1Card, data.comparison[0]);
        
        // Lincoln (second hospital)
        displayHospitalPricing(hospital2Card, data.comparison[1]);

        // Show savings if available
        if (data.savings) {
          const savings = data.savings;
          savingsText.innerHTML = `
            <strong>Save $${savings.amount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} 
            (${savings.percentage.toFixed(1)}%)</strong><br>
            by choosing ${savings.cheaper_hospital === 'Lincoln' ? 'Mercy Hospital Lincoln' : 'Barnes Jewish St. Peters'}!
          `;
          savingsSummary.style.display = 'block';
        }
      }
    })
    .catch(err => {
      console.error('Error loading comparison:', err);
      alert('Failed to load hospital pricing. Make sure backend is running on localhost:5001');
    });
}

// Hospital card click handlers
hospital1Card.addEventListener('click', () => {
  hospital1Card.classList.add('active');
  hospital2Card.classList.remove('active');
  loadHospitalData('hospital1Card');
});

hospital2Card.addEventListener('click', () => {
  hospital2Card.classList.add('active');
  hospital1Card.classList.remove('active');
  loadHospitalData('hospital2Card');
});

// Redo button resets the UI
redoBtn.addEventListener('click', () => {
  preview.style.display = "none";
  preview.src = "";
  submitBtn.style.display = "inline-block";
  redoBtn.style.display = "none";
  zipSection.style.display = "none";
  injuryInfo.style.display = "none";
  mapSection.style.display = "none";
  currentWoundType = '';
  detectedInjury.textContent = "-";
  zipInput.value = "";
  mapInitialized = false;
  markers = [];
});

// Event listeners for upload/camera
uploadInput.addEventListener('change', handleFile);
cameraInput.addEventListener('change', handleFile);
