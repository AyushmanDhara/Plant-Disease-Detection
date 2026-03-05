/**
 * PlantGuard - Main JavaScript
 * Handles all frontend functionality
 */

// Global Variables
let currentFile = null;
let diseaseData = [];
let currentFilter = 'all';
let currentSearch = '';

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadDiseaseData();
    setupUploadZone();
    setupEventListeners();
    // Set Home as active nav on load
    document.querySelectorAll('[data-section="home"]').forEach(l => l.classList.add('nav-active'));
});

// Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Update active nav links (desktop + mobile)
    document.querySelectorAll('[data-section]').forEach(link => {
        link.classList.remove('nav-active');
        if (link.getAttribute('data-section') === sectionId) {
            link.classList.add('nav-active');
        }
    });

    // Close mobile menu if open
    document.getElementById('mobileMenu').classList.add('hidden');
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// Mobile Menu Toggle
function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    menu.classList.toggle('hidden');
}

// Setup Event Listeners
function setupEventListeners() {
    // Upload zone click
    document.getElementById('uploadZone').addEventListener('click', function() {
        document.getElementById('fileInput').click();
    });
    
    // Drag and drop
    const uploadZone = document.getElementById('uploadZone');
    
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', function() {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', debounce(searchDiseases, 300));
    }
}

// Setup Upload Zone
function setupUploadZone() {
    console.log('Upload zone initialized');
}

// Handle File Selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Process Selected File
function handleFile(file) {
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a valid image file (PNG, JPG, JPEG, or WebP)');
        return;
    }
    
    // Validate file size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
    }
    
    currentFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('uploadPlaceholder').classList.add('hidden');
        document.getElementById('previewContainer').classList.remove('hidden');
        document.getElementById('analyzeBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

// Remove Selected Image
function removeImage() {
    currentFile = null;
    document.getElementById('fileInput').value = '';
    
    const previewContainer = document.getElementById('previewContainer');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (previewContainer) previewContainer.classList.add('hidden');
    if (uploadPlaceholder) uploadPlaceholder.classList.remove('hidden');
    if (analyzeBtn) analyzeBtn.disabled = true;
}

// Analyze Image
async function analyzeImage() {
    if (!currentFile) return;
    
    // Show loading state
    document.getElementById('initialState').classList.add('hidden');
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('resultsContainer').classList.add('hidden');
    
    // Create form data
    const formData = new FormData();
    formData.append('image', currentFile);
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            // Check if it's a leaf validation error
            if (data.is_leaf === false) {
                displayLeafError(data);
            } else {
                alert('Error: ' + data.error);
                resetDetection();
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while analyzing the image');
        resetDetection();
    }
}

// Display Leaf Validation Error in Results Section
function displayLeafError(data) {
    // Hide loading state
    document.getElementById('loadingState').classList.add('hidden');
    
    // Show results container
    document.getElementById('resultsContainer').classList.remove('hidden');
    
    // Get or create error state element
    let errorState = document.getElementById('errorState');
    
    if (!errorState) {
        // Create error state element dynamically
        errorState = document.createElement('div');
        errorState.id = 'errorState';
        errorState.className = 'hidden';
        errorState.innerHTML = `
            <div class="bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-2xl p-8 mb-6 text-center">
                <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-500"></i>
                </div>
                <h4 class="font-poppins text-2xl font-bold text-white mb-2">Not a Leaf Image!</h4>
                <p id="errorMessage" class="text-dark-300 mb-4">The uploaded image does not appear to be a plant leaf.</p>
                <p id="leafConfidence" class="text-dark-400 text-sm mb-4">Leaf Confidence: 0%</p>
                <div class="bg-dark-800 rounded-xl p-4">
                    <p class="text-dark-300 text-sm">
                        <i class="fas fa-info-circle text-primary mr-2"></i>
                        Please upload a clear photo of a plant leaf for disease detection.
                    </p>
                </div>
            </div>
            <button onclick="resetDetection()" class="w-full py-3 rounded-xl border-2 border-primary text-primary hover:bg-primary hover:text-white transition-all">
                <i class="fas fa-redo mr-2"></i> Try Again
            </button>
        `;
        
        // Insert into results container
        const resultsContainer = document.getElementById('resultsContainer');
        resultsContainer.insertBefore(errorState, resultsContainer.firstChild);
    }
    
    // Show error state, hide other elements
    errorState.classList.remove('hidden');
    
    // Hide prediction and disease details if they exist
    const predictionCard = document.getElementById('predictionCard');
    const diseaseDetails = document.getElementById('diseaseDetails');
    if (predictionCard) predictionCard.classList.add('hidden');
    if (diseaseDetails) diseaseDetails.classList.add('hidden');
    
    // Update error message
    const errorMsgEl = document.getElementById('errorMessage');
    const leafConfEl = document.getElementById('leafConfidence');
    if (errorMsgEl) errorMsgEl.textContent = data.error || 'The uploaded image does not appear to be a plant leaf.';
    if (leafConfEl) leafConfEl.textContent = 'Leaf Confidence: ' + (data.leaf_confidence ? data.leaf_confidence.toFixed(1) : '0') + '%';
}

// Display Results
function displayResults(data) {
    // Hide loading, show results
    document.getElementById('loadingState').classList.add('hidden');
    document.getElementById('resultsContainer').classList.remove('hidden');
    
    // Hide error state if visible
    const errorState = document.getElementById('errorState');
    if (errorState) {
        errorState.classList.add('hidden');
    }
    
    // Show prediction card and disease details
    const predictionCard = document.getElementById('predictionCard');
    const diseaseDetails = document.getElementById('diseaseDetails');
    if (predictionCard) predictionCard.classList.remove('hidden');
    if (diseaseDetails) diseaseDetails.classList.remove('hidden');
    
    const prediction = data.predictions[0];
    const disease = data.disease_info;
    
    // Update prediction card
    document.getElementById('diseaseName').textContent = disease.name;
    document.getElementById('plantType').textContent = 'Affected Plant: ' + disease.plant;
    
    // Confidence badge
    const confidence = prediction.confidence.toFixed(1);
    const confidenceBadge = document.getElementById('confidenceBadge');
    confidenceBadge.textContent = confidence + '% Confidence';
    
    // Severity badge
    const severityBadge = document.getElementById('severityBadge');
    const severityClass = 'severity-' + disease.severity.toLowerCase();
    severityBadge.className = 'px-4 py-2 rounded-lg text-white font-medium ' + severityClass;
    severityBadge.textContent = disease.severity;
    
    // Update tab content
    document.getElementById('symptomsText').textContent = disease.symptoms;
    document.getElementById('causesText').textContent = disease.causes;
    document.getElementById('treatmentOrganic').textContent = disease.treatment_organic;
    document.getElementById('treatmentChemical').textContent = disease.treatment_chemical;
    document.getElementById('preventionText').textContent = disease.prevention;
    
    // Switch to symptoms tab by default
    switchTab('symptoms');
}

// Tab Switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active', 'text-white', 'border-primary');
        btn.classList.add('text-dark-400', 'border-transparent');
    });
    
    const activeBtn = document.getElementById('tab-' + tabName);
    activeBtn.classList.add('active', 'text-white', 'border-primary');
    activeBtn.classList.remove('text-dark-400', 'border-transparent');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    document.getElementById('content-' + tabName).classList.remove('hidden');
}

// Reset Detection
function resetDetection() {
    removeImage();
    document.getElementById('resultsContainer').classList.add('hidden');
    document.getElementById('initialState').classList.remove('hidden');
}

// Load Disease Data
async function loadDiseaseData() {
    try {
        const response = await fetch('/api/diseases');
        const data = await response.json();
        
        if (data.success) {
            diseaseData = data.diseases;
            renderDiseaseCards(diseaseData);
        }
    } catch (error) {
        console.error('Error loading disease data:', error);
    }
}

// Render Disease Cards
function renderDiseaseCards(diseases) {
    const grid = document.getElementById('diseaseGrid');
    const noResults = document.getElementById('noResults');
    
    if (diseases.length === 0) {
        grid.classList.add('hidden');
        noResults.classList.remove('hidden');
        return;
    }
    
    grid.classList.remove('hidden');
    noResults.classList.add('hidden');
    
    grid.innerHTML = diseases.map(disease => {
        const severityClass = 'severity-' + (disease.severity === 'None' ? 'none' : disease.severity.toLowerCase());
        const plantIcon = getPlantIcon(disease.plant);
        
        return `
            <div class="disease-card glass-card rounded-2xl p-6" onclick="showDiseaseDetail('${disease.class}')">
                <div class="flex items-start justify-between mb-4">
                    <div class="disease-icon-container ${severityClass}">
                        <i class="fas ${plantIcon}"></i>
                    </div>
                    <span class="px-3 py-1 rounded-full text-xs font-medium text-white ${severityClass}">
                        ${disease.severity}
                    </span>
                </div>
                <h4 class="font-poppins text-lg font-semibold text-white mb-1">${disease.name}</h4>
                <p class="text-primary text-sm mb-3">${disease.plant}</p>
                <p class="text-dark-400 text-sm line-clamp-2">${disease.symptoms}</p>
            </div>
        `;
    }).join('');
}

// Get Plant Icon
function getPlantIcon(plant) {
    const icons = {
        'Apple': 'fa-apple-alt',
        'Blueberry': 'fa-seedling',
        'Cherry': 'fa-heart',
        'Corn': 'fa-seedling',
        'Grape': 'fa-wine-glass',
        'Orange': 'fa-lemon',
        'Peach': 'fa-leaf',
        'Pepper': 'fa-pepper-hot',
        'Potato': 'fa-carrot',
        'Raspberry': 'fa-heart',
        'Soybean': 'fa-seedling',
        'Squash': 'fa-leaf',
        'Strawberry': 'fa-heart',
        'Tomato': 'fa-apple-whole'
    };
    return icons[plant] || 'fa-leaf';
}

// Search Diseases
function searchDiseases() {
    currentSearch = document.getElementById('searchInput').value.toLowerCase();
    filterDiseases();
}

// Filter by Plant
function filterByPlant(plant) {
    currentFilter = plant;
    
    // Update active button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('bg-primary', 'text-white');
        btn.classList.add('bg-dark-700', 'text-dark-300');
    });
    
    event.target.classList.remove('bg-dark-700', 'text-dark-300');
    event.target.classList.add('bg-primary', 'text-white');
    
    filterDiseases();
}

// Filter Diseases
function filterDiseases() {
    let filtered = diseaseData;
    
    // Apply plant filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(d => d.plant === currentFilter);
    }
    
    // Apply search filter
    if (currentSearch) {
        filtered = filtered.filter(d => 
            d.name.toLowerCase().includes(currentSearch) ||
            d.plant.toLowerCase().includes(currentSearch) ||
            d.class.toLowerCase().includes(currentSearch)
        );
    }
    
    renderDiseaseCards(filtered);
}

// Show Disease Detail
async function showDiseaseDetail(diseaseClass) {
    try {
        const response = await fetch('/api/disease/' + encodeURIComponent(diseaseClass));
        const data = await response.json();
        
        if (data.success) {
            // Could open a modal or navigate to detail page
            // For now, show alert with basic info
            const disease = data.disease;
            alert(`${disease.name}\n\nPlant: ${disease.plant}\nSeverity: ${disease.severity}\n\nSymptoms: ${disease.symptoms.substring(0, 200)}...`);
        }
    } catch (error) {
        console.error('Error loading disease detail:', error);
    }
}

// Debounce Function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Utility: Format Confidence
function formatConfidence(confidence) {
    return confidence.toFixed(1) + '%';
}

// Utility: Get Severity Color
function getSeverityColor(severity) {
    const colors = {
        'None': 'text-green-500',
        'Low': 'text-green-400',
        'Medium': 'text-yellow-500',
        'High': 'text-orange-500',
        'Critical': 'text-red-500'
    };
    return colors[severity] || 'text-gray-500';
}