// Hero Carousel Logic
const slides = document.querySelectorAll('.carousel-slide');
const dots = document.querySelectorAll('.carousel-dot');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
let currentSlide = 0;
let autoplayInterval;

function showSlide(index) {
  slides.forEach((slide, i) => {
    slide.style.opacity = i === index ? '1' : '0';
  });
  dots.forEach((dot, i) => {
    if (i === index) {
      dot.classList.add('bg-white');
      dot.classList.remove('bg-white/50');
    } else {
      dot.classList.remove('bg-white');
      dot.classList.add('bg-white/50');
    }
  });
  currentSlide = index;
}

function nextSlide() {
  currentSlide = (currentSlide + 1) % slides.length;
  showSlide(currentSlide);
}

function prevSlide() {
  currentSlide = (currentSlide - 1 + slides.length) % slides.length;
  showSlide(currentSlide);
}

function startAutoplay() {
  autoplayInterval = setInterval(nextSlide, 5000);
}

function stopAutoplay() {
  clearInterval(autoplayInterval);
}

// Event Listeners
nextBtn.addEventListener('click', () => {
  nextSlide();
  stopAutoplay();
  startAutoplay();
});

prevBtn.addEventListener('click', () => {
  prevSlide();
  stopAutoplay();
  startAutoplay();
});

dots.forEach((dot, index) => {
  dot.addEventListener('click', () => {
    showSlide(index);
    stopAutoplay();
    startAutoplay();
  });
});

// Pause on hover
document
  .getElementById('heroCarousel')
  .addEventListener('mouseenter', stopAutoplay);
document
  .getElementById('heroCarousel')
  .addEventListener('mouseleave', startAutoplay);

// Touch support for mobile
let touchStartX = 0;
let touchEndX = 0;

document.getElementById('heroCarousel').addEventListener('touchstart', (e) => {
  touchStartX = e.changedTouches[0].screenX;
});

document.getElementById('heroCarousel').addEventListener('touchend', (e) => {
  touchEndX = e.changedTouches[0].screenX;
  if (touchStartX - touchEndX > 50) {
    nextSlide();
    stopAutoplay();
    startAutoplay();
  }
  if (touchEndX - touchStartX > 50) {
    prevSlide();
    stopAutoplay();
    startAutoplay();
  }
});

// Initialize
showSlide(0);
startAutoplay();
