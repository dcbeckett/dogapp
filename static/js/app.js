// Dog Voting Platform - Swipe Edition JavaScript

let currentCardIndex = 0;
let isAnimating = false;
let swipeStartX = 0;
let swipeStartY = 0;
let currentX = 0;
let currentY = 0;
let isDragging = false;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize swipe functionality
    initializeSwipe();
    
    // Initialize upload functionality
    initializeUpload();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Initialize swipe functionality
function initializeSwipe() {
    const swipeCards = document.getElementById('swipe-cards');
    if (!swipeCards) return;

    const cards = swipeCards.querySelectorAll('.swipe-card');
    if (cards.length === 0) {
        showNoMoreDogs();
        return;
    }

    // Add event listeners to the current card
    addSwipeListeners(cards[currentCardIndex]);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyDown);
}

function addSwipeListeners(card) {
    if (!card) return;

    // Mouse events
    card.addEventListener('mousedown', handleStart);
    document.addEventListener('mousemove', handleMove);
    document.addEventListener('mouseup', handleEnd);

    // Touch events
    card.addEventListener('touchstart', handleStart, { passive: false });
    document.addEventListener('touchmove', handleMove, { passive: false });
    document.addEventListener('touchend', handleEnd);
}

function handleStart(e) {
    if (isAnimating) return;
    
    e.preventDefault();
    isDragging = true;
    
    const clientX = e.clientX || e.touches[0].clientX;
    const clientY = e.clientY || e.touches[0].clientY;
    
    swipeStartX = clientX;
    swipeStartY = clientY;
    currentX = clientX;
    currentY = clientY;
    
    const card = getCurrentCard();
    if (card) {
        card.style.transition = 'none';
    }
}

function handleMove(e) {
    if (!isDragging || isAnimating) return;
    
    e.preventDefault();
    
    const clientX = e.clientX || e.touches[0].clientX;
    const clientY = e.clientY || e.touches[0].clientY;
    
    currentX = clientX;
    currentY = clientY;
    
    const deltaX = currentX - swipeStartX;
    const deltaY = currentY - swipeStartY;
    
    updateCardPosition(deltaX, deltaY);
}

function handleEnd(e) {
    if (!isDragging || isAnimating) return;
    
    isDragging = false;
    
    const deltaX = currentX - swipeStartX;
    const deltaY = currentY - swipeStartY;
    
    // Determine swipe direction and threshold
    const threshold = 100;
    const card = getCurrentCard();
    
    if (Math.abs(deltaX) > threshold) {
        if (deltaX > 0) {
            // Swipe right - love
            swipeRight();
        } else {
            // Swipe left - skip
            swipeLeft();
        }
    } else {
        // Return to center
        if (card) {
            card.style.transition = 'all 0.3s ease-out';
            card.style.transform = 'translateX(0) translateY(0) rotate(0deg)';
            card.classList.remove('swiping-left', 'swiping-right');
            hideSwipeIndicators(card);
        }
    }
}

function updateCardPosition(deltaX, deltaY) {
    const card = getCurrentCard();
    if (!card) return;
    
    const rotation = deltaX * 0.1; // Rotation based on horizontal movement
    const opacity = Math.max(0.7, 1 - Math.abs(deltaX) / 300);
    
    card.style.transform = `translateX(${deltaX}px) translateY(${deltaY * 0.3}px) rotate(${rotation}deg)`;
    card.style.opacity = opacity;
    
    // Show appropriate indicator
    const leftIndicator = card.querySelector('.left-indicator');
    const rightIndicator = card.querySelector('.right-indicator');
    
    if (deltaX > 50) {
        card.classList.add('swiping-right');
        card.classList.remove('swiping-left');
        if (rightIndicator) rightIndicator.style.opacity = Math.min(1, deltaX / 150);
        if (leftIndicator) leftIndicator.style.opacity = 0;
    } else if (deltaX < -50) {
        card.classList.add('swiping-left');
        card.classList.remove('swiping-right');
        if (leftIndicator) leftIndicator.style.opacity = Math.min(1, Math.abs(deltaX) / 150);
        if (rightIndicator) rightIndicator.style.opacity = 0;
    } else {
        card.classList.remove('swiping-left', 'swiping-right');
        if (leftIndicator) leftIndicator.style.opacity = 0;
        if (rightIndicator) rightIndicator.style.opacity = 0;
    }
}

function getCurrentCard() {
    const swipeCards = document.getElementById('swipe-cards');
    if (!swipeCards) return null;
    
    const cards = swipeCards.querySelectorAll('.swipe-card');
    return cards[currentCardIndex] || null;
}

function swipeLeft() {
    const card = getCurrentCard();
    if (!card || isAnimating) return;
    
    isAnimating = true;
    card.classList.add('swipe-left');
    card.style.transition = 'all 0.6s ease-out';
    
    // Don't vote, just move to next card
    setTimeout(() => {
        moveToNextCard();
    }, 600);
}

function swipeRight() {
    const card = getCurrentCard();
    if (!card || isAnimating) return;
    
    const dogId = card.dataset.dogId;
    
    isAnimating = true;
    card.classList.add('swipe-right');
    card.style.transition = 'all 0.6s ease-out';
    
    // Vote for the dog
    voteForDog(dogId);
    
    setTimeout(() => {
        moveToNextCard();
    }, 600);
}

function moveToNextCard() {
    const swipeCards = document.getElementById('swipe-cards');
    if (!swipeCards) return;
    
    const cards = swipeCards.querySelectorAll('.swipe-card');
    
    // Remove the current card from DOM
    if (cards[currentCardIndex]) {
        cards[currentCardIndex].remove();
    }
    
    // Update remaining cards' z-index and scaling
    const remainingCards = swipeCards.querySelectorAll('.swipe-card');
    remainingCards.forEach((card, index) => {
        card.style.transition = 'all 0.3s ease';
        if (index === 0) {
            card.style.zIndex = 5;
            card.style.transform = 'scale(1) translateY(0)';
            card.style.opacity = 1;
            addSwipeListeners(card);
        } else if (index === 1) {
            card.style.zIndex = 4;
            card.style.transform = 'scale(0.95) translateY(-10px)';
            card.style.opacity = 0.8;
        } else if (index === 2) {
            card.style.zIndex = 3;
            card.style.transform = 'scale(0.9) translateY(-20px)';
            card.style.opacity = 0.6;
        } else {
            card.style.zIndex = 2;
            card.style.transform = 'scale(0.85) translateY(-30px)';
            card.style.opacity = 0.4;
        }
    });
    
    isAnimating = false;
    
    // Check if there are more cards
    if (remainingCards.length === 0) {
        showNoMoreDogs();
    }
}

// Desktop button functions
function skipDog() {
    if (!isAnimating) {
        swipeLeft();
    }
}

function loveDog() {
    if (!isAnimating) {
        swipeRight();
    }
}

// Keyboard shortcuts
function handleKeyDown(e) {
    if (isAnimating) return;
    
    switch(e.key) {
        case 'ArrowLeft':
            e.preventDefault();
            skipDog();
            break;
        case 'ArrowRight':
            e.preventDefault();
            loveDog();
            break;
        case ' ':
            e.preventDefault();
            loveDog();
            break;
    }
}

// Voting functionality (now used for swipe right)
function voteForDog(dogId) {
    fetch(`/api/vote/${dogId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update vote count in current card
            const card = getCurrentCard();
            if (card) {
                const voteCountSpan = card.querySelector('.vote-count');
                if (voteCountSpan) {
                    voteCountSpan.textContent = data.votes;
                }
            }
            
            // Handle cat vs dog differently
            if (data.is_cat) {
                // Show cat caught animation and message
                createCatCaughtAnimation();
                setTimeout(() => {
                    showCatMessage(data.message, data.cat_name);
                }, 500);
            } else {
                // Show normal heart animation for dogs
                createHeartAnimation();
            }
        }
    })
    .catch(error => {
        console.error('Error voting:', error);
    });
}

function createHeartAnimation() {
    const container = document.querySelector('.swipe-container');
    if (!container) return;
    
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            const heart = document.createElement('div');
            heart.innerHTML = '❤️';
            heart.style.position = 'absolute';
            heart.style.left = '50%';
            heart.style.top = '50%';
            heart.style.transform = 'translate(-50%, -50%)';
            heart.style.fontSize = '2rem';
            heart.style.pointerEvents = 'none';
            heart.style.zIndex = '1000';
            heart.style.animation = `heartFloat ${1.5 + Math.random()}s ease-out forwards`;
            
            // Random direction
            const randomX = (Math.random() - 0.5) * 200;
            const randomY = (Math.random() - 0.5) * 200;
            heart.style.setProperty('--random-x', randomX + 'px');
            heart.style.setProperty('--random-y', randomY + 'px');
            
            container.appendChild(heart);
            
            setTimeout(() => heart.remove(), 2000);
        }, i * 100);
    }
}

function createCatCaughtAnimation() {
    const container = document.querySelector('.swipe-container');
    if (!container) return;
    
    // Create surprise cats
    const catEmojis = ['😸', '😹', '😺', '😻', '🙀', '😾', '😿'];
    
    for (let i = 0; i < 8; i++) {
        setTimeout(() => {
            const cat = document.createElement('div');
            cat.innerHTML = catEmojis[Math.floor(Math.random() * catEmojis.length)];
            cat.style.position = 'absolute';
            cat.style.left = '50%';
            cat.style.top = '50%';
            cat.style.transform = 'translate(-50%, -50%)';
            cat.style.fontSize = '2.5rem';
            cat.style.pointerEvents = 'none';
            cat.style.zIndex = '1000';
            cat.style.animation = `catFloat ${2 + Math.random()}s ease-out forwards`;
            
            // Random direction for cats
            const randomX = (Math.random() - 0.5) * 300;
            const randomY = (Math.random() - 0.5) * 300;
            cat.style.setProperty('--random-x', randomX + 'px');
            cat.style.setProperty('--random-y', randomY + 'px');
            
            container.appendChild(cat);
            
            setTimeout(() => cat.remove(), 2500);
        }, i * 80);
    }
}

function showCatMessage(message, catName) {
    // Create modal-like message
    const modal = document.createElement('div');
    modal.className = 'cat-message-modal';
    modal.innerHTML = `
        <div class="cat-message-content">
            <div class="cat-message-header">
                <h3>😹 Gotcha!</h3>
            </div>
            <div class="cat-message-body">
                <div class="cat-icon">🐱</div>
                <h4>${catName}</h4>
                <p>${message}</p>
                <p class="small text-muted">
                    This was an attention test! We randomly mix in cats to see if you're really looking at the photos.
                </p>
            </div>
            <div class="cat-message-footer">
                <button class="btn btn-primary" onclick="closeCatMessage()">
                    Got it! 😸
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-close after 8 seconds
    setTimeout(() => {
        if (document.body.contains(modal)) {
            closeCatMessage();
        }
    }, 8000);
}

function closeCatMessage() {
    const modal = document.querySelector('.cat-message-modal');
    if (modal) {
        modal.remove();
    }
}

function hideSwipeIndicators(card) {
    const leftIndicator = card.querySelector('.left-indicator');
    const rightIndicator = card.querySelector('.right-indicator');
    
    if (leftIndicator) leftIndicator.style.opacity = 0;
    if (rightIndicator) rightIndicator.style.opacity = 0;
}

function showNoMoreDogs() {
    const swipeContainer = document.getElementById('swipe-container');
    const noMoreDogs = document.getElementById('no-more-dogs');
    
    if (swipeContainer) swipeContainer.style.display = 'none';
    if (noMoreDogs) noMoreDogs.style.display = 'block';
}

// Create heart animation for voting
function createHeartAnimation(button) {
    const heart = document.createElement('div');
    heart.innerHTML = '❤️';
    heart.style.position = 'absolute';
    heart.style.left = '50%';
    heart.style.top = '50%';
    heart.style.transform = 'translate(-50%, -50%)';
    heart.style.fontSize = '1.5rem';
    heart.style.pointerEvents = 'none';
    heart.style.zIndex = '1000';
    heart.style.animation = 'heartFloat 1.5s ease-out forwards';
    
    button.style.position = 'relative';
    button.appendChild(heart);
    
    // Remove heart after animation
    setTimeout(() => {
        heart.remove();
    }, 1500);
}

// Add CSS for heart animation
const style = document.createElement('style');
style.textContent = `
    @keyframes heartFloat {
        0% {
            opacity: 1;
            transform: translate(-50%, -50%) scale(1);
        }
        100% {
            opacity: 0;
            transform: translate(-50%, -150%) scale(1.5);
        }
    }
`;
document.head.appendChild(style);

// Upload functionality
function initializeUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const uploadForm = document.getElementById('upload-form');
    
    if (!uploadArea || !fileInput) return;
    
    // Click to select file
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Form submission with progress
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFormSubmit);
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        validateAndPreviewFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = document.getElementById('file');
        fileInput.files = files;
        validateAndPreviewFile(files[0]);
    }
}

function validateAndPreviewFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp'];
    
    // Validate file type
    if (!allowedTypes.includes(file.type)) {
        alert('Please select a valid image file (PNG, JPG, JPEG, GIF, or WebP).');
        return;
    }
    
    // Validate file size
    if (file.size > maxSize) {
        alert('File size must be less than 16MB.');
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const previewImg = document.getElementById('preview-img');
        const imagePreview = document.getElementById('image-preview');
        
        if (previewImg && imagePreview) {
            previewImg.src = e.target.result;
            imagePreview.style.display = 'block';
        }
    };
    reader.readAsDataURL(file);
}

function clearPreview() {
    const fileInput = document.getElementById('file');
    const imagePreview = document.getElementById('image-preview');
    
    if (fileInput) fileInput.value = '';
    if (imagePreview) imagePreview.style.display = 'none';
}

function handleFormSubmit(event) {
    const submitBtn = document.getElementById('submit-btn');
    const fileInput = document.getElementById('file');
    
    if (!fileInput.files.length) {
        event.preventDefault();
        alert('Please select a file to upload.');
        return;
    }
    
    // Show loading state
    if (submitBtn) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
        submitBtn.disabled = true;
    }
}

// Utility functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Smooth scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button
document.addEventListener('scroll', function() {
    const scrollBtn = document.getElementById('scroll-top-btn');
    if (window.scrollY > 300) {
        if (scrollBtn) scrollBtn.style.display = 'block';
    } else {
        if (scrollBtn) scrollBtn.style.display = 'none';
    }
});

// Lazy loading for images (if needed)
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
} 