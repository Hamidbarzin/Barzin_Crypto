// نسخه ساده شده اسکریپت منوی کشویی 
document.addEventListener('DOMContentLoaded', function() {
    // When the toggle button is clicked
    document.querySelector('.navbar-toggler').addEventListener('click', function() {
        // Toggle the 'show' class on the navbar collapse element
        document.querySelector('#navbarNavDropdown').classList.toggle('show');
    });

    // When a nav-link is clicked (e.g. a menu item)
    document.querySelectorAll('.nav-link').forEach(function(link) {
        link.addEventListener('click', function() {
            // If the navbar is expanded and we're on mobile
            if (window.innerWidth < 992 && document.querySelector('#navbarNavDropdown').classList.contains('show')) {
                // Collapse the navbar
                document.querySelector('#navbarNavDropdown').classList.remove('show');
            }
        });
    });

    // When clicking outside the navbar
    document.addEventListener('click', function(event) {
        // Only take action if navbar is expanded
        if (document.querySelector('#navbarNavDropdown').classList.contains('show')) {
            // Check if the click was outside the navbar
            if (!event.target.closest('.navbar')) {
                // Collapse the navbar
                document.querySelector('#navbarNavDropdown').classList.remove('show');
            }
        }
    });

    console.log('Navbar JavaScript initialized');
});