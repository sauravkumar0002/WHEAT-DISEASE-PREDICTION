// ========== DRAG & DROP FUNCTIONALITY ==========
const dragDropZone = document.getElementById('dragDropZone');
const imageInput = document.getElementById('imageInput');
const previewContainer = document.getElementById('previewContainer');
const previewImage = document.getElementById('previewImage');
const uploadForm = document.getElementById('uploadForm');

// Prevent default drag behaviors
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dragDropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight drop area when item is dragged over it
['dragenter', 'dragover'].forEach(eventName => {
    dragDropZone.addEventListener(eventName, () => {
        dragDropZone.classList.add('drag-over');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dragDropZone.addEventListener(eventName, () => {
        dragDropZone.classList.remove('drag-over');
    }, false);
});

// Handle dropped files
dragDropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    imageInput.files = files;
    handleFileSelect(files);
}, false);

// Handle file input change
imageInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files);
});

// Handle file selection and preview
function handleFileSelect(files) {
    if (files.length > 0) {
        const file = files[0];

        // Validate file type
        if (!file.type.match('image.*')) {
            alert('Please select a valid image file (PNG or JPEG)');
            return;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('File size exceeds 10MB. Please select a smaller file.');
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewContainer.style.display = 'block';
            dragDropZone.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
}

// Reset upload
function resetUpload() {
    imageInput.value = '';
    previewContainer.style.display = 'none';
    dragDropZone.style.display = 'block';
}

// Add smooth scroll animation on page load
document.addEventListener('DOMContentLoaded', () => {
    // Animate hero section
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '0';
        heroContent.style.animation = 'fadeInDown 0.8s ease-out 0.2s forwards';
    }

    // Smooth scroll for any internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Add form submission validation
if (uploadForm) {
    uploadForm.addEventListener('submit', (e) => {
        if (!imageInput.files || imageInput.files.length === 0) {
            e.preventDefault();
            alert('Please select an image before uploading');
        }
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Alt + U for upload (when focused on drag zone)
    if (e.altKey && e.key === 'u' && dragDropZone && dragDropZone.style.display !== 'none') {
        imageInput.click();
    }
});
