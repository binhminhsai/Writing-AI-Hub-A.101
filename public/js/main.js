// Main JavaScript file for Writing AI Hub

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return; // Skip if it's just "#"
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70, // 70px offset for header
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add active class to current nav link
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Feature cards hover animation enhancement
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add coming soon tooltip functionality
    const comingSoonElements = document.querySelectorAll('.coming-soon');
    comingSoonElements.forEach(element => {
        element.setAttribute('title', 'This feature will be available soon. Stay tuned!');
    });
    
    // Premium section animation
    const premiumSection = document.querySelector('.premium');
    if (premiumSection) {
        const premiumObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = 1;
                    entry.target.style.transform = 'translateY(0)';
                    premiumObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        
        premiumSection.style.opacity = 0;
        premiumSection.style.transform = 'translateY(20px)';
        premiumSection.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        premiumObserver.observe(premiumSection);
    }
    
    // Initialize any tooltips or popovers if using Bootstrap
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    console.log('Writing AI Hub initialized successfully!');
});