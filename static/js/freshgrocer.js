// freshgrocer-script.js

// Wait for DOM to load
window.addEventListener('DOMContentLoaded', () => {
  setupSearch();
  setupSidebarToggle();
  highlightActiveLink();
  handleResponsiveResize();
  setupHeaderHover();
  initHeroSlider();  // Initialize hero slider here
});

function setupSearch() {
  const searchBtn = document.querySelector('.search-btn');
  const searchInput = document.querySelector('.search-bar');
  if (!searchBtn || !searchInput) return;

  searchBtn.addEventListener('click', () => {
    const query = searchInput.value.trim();
    if (query) {
      alert(`Searching for: "${query}"`);
    } else {
      alert("Please enter a product name to search.");
    }
  });
}

function setupSidebarToggle() {
  const sidebar = document.querySelector('.sidebar');
  const sidebarToggle = document.querySelector('.sidebar-toggle');

  if (!sidebar || !sidebarToggle) return;

  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
}

function highlightActiveLink() {
  const navLinks = document.querySelectorAll('.nav-links a');
  const currentURL = window.location.href;
  navLinks.forEach(link => {
    if (currentURL.includes(link.href)) {
      link.classList.add('active');
    }
  });
}

function handleResponsiveResize() {
  const resizeElements = document.querySelectorAll('.responsive');
  window.addEventListener('resize', () => {
    const width = window.innerWidth;
    resizeElements.forEach(el => {
      if (width < 768) {
        el.classList.add('mobile');
      } else {
        el.classList.remove('mobile');
      }
    });
  });
}

function setupHeaderHover() {
  const headerIcons = document.querySelectorAll('.header-icon');
  headerIcons.forEach(icon => {
    icon.addEventListener('mouseenter', () => {
      icon.classList.add('hovered');
    });
    icon.addEventListener('mouseleave', () => {
      icon.classList.remove('hovered');
    });
  });
}

// HERO SLIDER AUTO + MANUAL + RESPONSIVE HEIGHT
function initHeroSlider() {
  const slides = document.querySelectorAll('.slide');
  const prevBtn = document.querySelector('.slider-controls .prev');
  const nextBtn = document.querySelector('.slider-controls .next');
  let currentIndex = 0;
  let slideInterval;

  function adjustSliderHeight() {
    const slider = document.querySelector('.hero-slider');
    const activeSlide = document.querySelector('.slide.active');
    if (!slider || !activeSlide) return;
    slider.style.height = activeSlide.offsetHeight + 'px';
  }

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle('active', i === index);
    });
    adjustSliderHeight();
  }

  function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
  }

  function prevSlide() {
    currentIndex = (currentIndex - 1 + slides.length) % slides.length;
    showSlide(currentIndex);
  }

  function startAutoSlide() {
    slideInterval = setInterval(nextSlide, 2000); // change slide every 2 seconds
  }

  function stopAutoSlide() {
    clearInterval(slideInterval);
  }

  // Initialize
  showSlide(currentIndex);
  startAutoSlide();

  // Adjust slider height on window resize
  window.addEventListener('resize', adjustSliderHeight);

  // Manual controls
  if (prevBtn && nextBtn) {
    prevBtn.addEventListener('click', () => {
      stopAutoSlide();
      prevSlide();
      startAutoSlide();
    });

    nextBtn.addEventListener('click', () => {
      stopAutoSlide();
      nextSlide();
      startAutoSlide();
    });
  }
}
