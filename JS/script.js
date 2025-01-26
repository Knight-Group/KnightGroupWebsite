// Slideshow Functionality
const slides = document.querySelectorAll('.slide');
let currentSlide = 0;

// Function to show the active slide immediately on page load
function showSlide(index) {
    slides.forEach((slide, i) => {
        slide.classList.remove('active'); // Hide all slides
        if (i === index) {
            slide.classList.add('active'); // Show the current slide
        }
    });
}

// Show the first slide immediately on page load
showSlide(currentSlide);

function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length; // Loop back to the first slide
    showSlide(currentSlide);
}

// Automatically switch slides every 5 seconds
setInterval(nextSlide, 8500);

// Mobile Menu Toggle
function toggleMenu() {
    var mobileMenu = document.querySelector('.mobile-menu');
    mobileMenu.classList.toggle('active');
}

// 404 Redirect to Homepage
// Check if the current URL contains "404" or if the 404 page has loaded
window.addEventListener('load', function() {
    if (document.title.includes("404")) {
        window.location.href = "https://KnightGroup.com";
    }
});

// Function to open the modal
function openModal(imageSrc) {
    document.getElementById("imageModal").style.display = "block";
    document.getElementById("modalImage").src = imageSrc;
}

// Function to close the modal
function closeModal() {
    document.getElementById("imageModal").style.display = "none";
}

// Close modal when clicking outside of the image
window.onclick = function(event) {
    let modal = document.getElementById("imageModal");
    if (event.target === modal) {
        closeModal();
    }
}
