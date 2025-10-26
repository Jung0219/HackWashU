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

// Insurance elements
const insuranceSection = document.getElementById('insuranceSection');
const insurancePlan = document.getElementById('insurancePlan');
const coveragePercentage = document.getElementById('coveragePercentage');
const coveragePercentageValue = document.getElementById('coveragePercentageValue');
const deductible = document.getElementById('deductible');
const copay = document.getElementById('copay');
const updateInsuranceBtn = document.getElementById('updateInsurance');
const insuranceNotice = document.getElementById('insuranceNotice');
const insuranceNoticeText = document.getElementById('insuranceNoticeText');

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

// Insurance data
let insuranceData = {
  plan: '',
  coverage: 90,
  deductible: 500,
  copay: 50,
  hasInsurance: true
};

// Store hospital pricing data
let hospitalPricingData = {
  barnes_jewish: null,
  lincoln: null
};

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

// Initialize Mapbox
function initMapbox() {
  if (mapInitialized) return;
  
  // Set your Mapbox access token
  mapboxgl.accessToken = 'pk.eyJ1IjoiZWQwODI3IiwiYSI6ImNtaDc4eGNldjBvczAybXB6ZW5lZ3BzdWEifQ.rRf3regcDzFGfLKgdIxnMQ';
  
  // Center between the two hospitals
  map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [-90.8, 38.88],
    zoom: 10
  });

  // Add hospital markers
  hospitals.forEach((hospital, index) => {
    // Create a marker element
    const el = document.createElement('div');
    el.className = 'hospital-marker-mapbox';
    el.style.backgroundImage = `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40"><circle cx="20" cy="20" r="18" fill="%230ea5e9" stroke="white" stroke-width="2"/><text x="20" y="25" text-anchor="middle" font-size="18" fill="white" font-weight="bold">${index + 1}</text></svg>')`;
    el.style.backgroundSize = '100%';
    el.style.width = '40px';
    el.style.height = '40px';
    el.style.cursor = 'pointer';
    el.style.backgroundRepeat = 'no-repeat';
    el.style.transition = 'transform 0.3s ease';
    
    // Add hover effect
    el.addEventListener('mouseenter', () => {
      el.style.transform = 'scale(1.3)';
    });
    el.addEventListener('mouseleave', () => {
      el.style.transform = 'scale(1)';
    });

    // Create popup
    const popupContent = document.createElement('div');
    popupContent.innerHTML = `
      <div class="hospital-popup-title">${hospital.name}</div>
      <div class="hospital-popup-address">${hospital.location}</div>
    `;

    const popup = new mapboxgl.Popup({ offset: 25 }).setDOMContent(popupContent);

    // Create marker
    const marker = new mapboxgl.Marker(el)
      .setLngLat([hospital.lng, hospital.lat])
      .setPopup(popup)
      .addTo(map);

    // Click marker to highlight hospital card
    el.addEventListener('click', () => {
      const card = document.getElementById(hospital.cardId);
      card.classList.add('active');
      const otherCard = index === 0 ? hospital2Card : hospital1Card;
      otherCard.classList.remove('active');
    });

    markers.push(marker);
  });

  mapInitialized = true;
}

// Setup marker click handlers (for non-Mapbox compatibility)
function setupMarkerClickHandlers() {
  // Mapbox markers are handled in initMapbox
  // This function kept for compatibility
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
  insuranceSection.style.display = "none";
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

// Coverage percentage slider event
coveragePercentage.addEventListener('input', (e) => {
  coveragePercentageValue.textContent = e.target.value + '%';
});

// Update insurance button
updateInsuranceBtn.addEventListener('click', () => {
  insuranceData.plan = insurancePlan.value;
  insuranceData.coverage = parseInt(coveragePercentage.value);
  insuranceData.deductible = parseInt(deductible.value) || 0;
  insuranceData.copay = parseInt(copay.value) || 0;
  insuranceData.hasInsurance = insurancePlan.value !== '';

  // Show confirmation
  if (insuranceData.hasInsurance) {
    insuranceNoticeText.innerHTML = `
      ✓ <strong>${insurancePlan.options[insurancePlan.selectedIndex].text}</strong> 
      (${insuranceData.coverage}% coverage)<br>
      Deductible: $${insuranceData.deductible} | Co-pay: $${insuranceData.copay}
    `;
  } else {
    insuranceNoticeText.innerHTML = '✓ Self-pay mode - showing full hospital charges';
  }
  insuranceNotice.style.display = 'block';

  // Recalculate and update hospital pricing display
  if (hospitalPricingData.barnes_jewish || hospitalPricingData.lincoln) {
    updateHospitalCardsWithInsurance();
  }
});

// Calculate patient cost based on insurance
function calculatePatientCost(hospitalCost) {
  if (!insuranceData.hasInsurance) {
    return {
      hospitalCharge: hospitalCost,
      insurancePays: 0,
      deductibleApplied: 0,
      copayApplied: 0,
      patientOwes: hospitalCost
    };
  }

  const insuranceCoverageAmount = hospitalCost * (insuranceData.coverage / 100);
  const hospitalResponsibility = hospitalCost - insuranceCoverageAmount;
  
  // Deductible applies first
  const deductibleApplied = Math.min(insuranceData.deductible, hospitalResponsibility);
  const afterDeductible = hospitalResponsibility - deductibleApplied;
  
  // Co-pay applies after deductible
  const copayApplied = insuranceData.copay;
  
  return {
    hospitalCharge: hospitalCost,
    insurancePays: insuranceCoverageAmount,
    deductibleApplied: deductibleApplied,
    copayApplied: copayApplied,
    patientOwes: afterDeductible + copayApplied
  };
}

// Display pricing with insurance breakdown
function displayHospitalPricingWithInsurance(card, hospitalData) {
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

  // Calculate totals
  const totalHospitalCharge = hospitalData.total_estimate || 0;
  
  if (totalHospitalCharge > 0) {
    const costs = calculatePatientCost(totalHospitalCharge);
    
    html += `<div class="pricing-breakdown">`;
    html += `<div class="price-row">
      <span class="price-label">Hospital Charge:</span>
      <span class="price-value">$${costs.hospitalCharge.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
    </div>`;
    
    if (insuranceData.hasInsurance) {
      html += `<div class="price-row">
        <span class="price-label">Insurance Covers (${insuranceData.coverage}%):</span>
        <span class="price-value" style="color: #10b981;">-$${costs.insurancePays.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
      </div>`;
      
      if (costs.deductibleApplied > 0) {
        html += `<div class="price-row">
          <span class="price-label">Your Deductible:</span>
          <span class="price-value">$${costs.deductibleApplied.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
        </div>`;
      }
      
      if (costs.copayApplied > 0) {
        html += `<div class="price-row">
          <span class="price-label">Co-pay:</span>
          <span class="price-value">$${costs.copayApplied.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
        </div>`;
      }
    }
    
    html += `<div class="price-row">
      <span class="price-label" style="font-size: 15px;">YOU PAY:</span>
      <span class="price-value" style="font-size: 18px;">$${costs.patientOwes.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
    </div>`;
    html += `</div>`;
  }

  body.innerHTML = html;
}

// Update hospital cards with insurance calculations
function updateHospitalCardsWithInsurance() {
  if (hospitalPricingData.barnes_jewish) {
    displayHospitalPricingWithInsurance(hospital1Card, hospitalPricingData.barnes_jewish);
  }
  if (hospitalPricingData.lincoln) {
    displayHospitalPricingWithInsurance(hospital2Card, hospitalPricingData.lincoln);
  }
}

// Update comparison pricing to include insurance
function loadComparisonPricingWithInsurance() {
  fetch(`http://localhost:5001/api/pricing/compare?wound_type=${encodeURIComponent(currentWoundType)}`)
    .then(res => res.json())
    .then(data => {
      console.log('Comparison data:', data);
      
      if (data.comparison && data.comparison.length >= 2) {
        hospitalPricingData.barnes_jewish = data.comparison[0];
        hospitalPricingData.lincoln = data.comparison[1];
        
        displayHospitalPricingWithInsurance(hospital1Card, data.comparison[0]);
        displayHospitalPricingWithInsurance(hospital2Card, data.comparison[1]);

        // Show savings if available
        if (data.savings) {
          const savings = data.savings;
          const barnes1Cost = calculatePatientCost(data.comparison[0].total_estimate || 0);
          const lincolnCost = calculatePatientCost(data.comparison[1].total_estimate || 0);
          const patientSavings = barnes1Cost.patientOwes - lincolnCost.patientOwes;
          const percentSaved = barnes1Cost.patientOwes > 0 
            ? ((patientSavings / barnes1Cost.patientOwes) * 100).toFixed(1)
            : 0;

          savingsText.innerHTML = `
            <strong>Save $${Math.abs(patientSavings).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} 
            (${percentSaved}%)</strong><br>
            on your out-of-pocket costs by choosing ${savings.cheaper_hospital === 'Lincoln' ? 'Mercy Hospital Lincoln' : 'Barnes Jewish St. Peters'}!
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

// Search for hospitals
searchHospitalsBtn.addEventListener('click', () => {
  const zipCode = zipInput.value.trim();
  
  if (zipCode.length !== 5) {
    alert('Please enter a valid 5-digit ZIP code');
    return;
  }

  // Show insurance section
  insuranceSection.style.display = "block";

  // Show map section
  mapSection.style.display = "block";
  
  // Initialize Mapbox after display
  setTimeout(() => {
    initMapbox();
    insuranceSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }, 100);

  // Reset hospital cards
  resetHospitalCards();
  
  // Load comparison pricing
  loadComparisonPricingWithInsurance();
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

// Hospital card click handlers
hospital1Card.addEventListener('click', () => {
  hospital1Card.classList.add('active');
  hospital2Card.classList.remove('active');
});

hospital2Card.addEventListener('click', () => {
  hospital2Card.classList.add('active');
  hospital1Card.classList.remove('active');
});

// Redo button resets the UI
redoBtn.addEventListener('click', () => {
  preview.style.display = "none";
  preview.src = "";
  submitBtn.style.display = "inline-block";
  redoBtn.style.display = "none";
  zipSection.style.display = "none";
  injuryInfo.style.display = "none";
  insuranceSection.style.display = "none";
  mapSection.style.display = "none";
  insuranceNotice.style.display = "none";
  currentWoundType = '';
  detectedInjury.textContent = "-";
  zipInput.value = "";
  mapInitialized = false;
  
  // Remove Mapbox markers
  markers.forEach(marker => marker.remove());
  markers = [];
  
  insuranceData = {
    plan: '',
    coverage: 90,
    deductible: 500,
    copay: 50,
    hasInsurance: true
  };
  hospitalPricingData = {
    barnes_jewish: null,
    lincoln: null
  };
  insurancePlan.value = '';
  coveragePercentage.value = 90;
  deductible.value = 500;
  copay.value = 50;
});

// Event listeners for upload/camera
uploadInput.addEventListener('change', handleFile);
cameraInput.addEventListener('change', handleFile);
