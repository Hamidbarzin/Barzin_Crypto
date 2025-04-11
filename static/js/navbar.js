// اسکریپت ساده‌تر منوی کشویی بوت‌استرپ
document.addEventListener('DOMContentLoaded', function() {
    console.log('Navbar JavaScript initializing');
    
    // Check if Bootstrap is initialized
    if (typeof bootstrap !== 'undefined') {
        console.log('Bootstrap JS is detected');
        
        // مقداردهی اولیه همه منوهای کشویی
        var navbarToggler = document.querySelector('.navbar-toggler');
        var navbarCollapse = document.getElementById('navbarNavDropdown');
        
        if (navbarToggler && navbarCollapse) {
            // روش اول: استفاده از کلاس‌های Bootstrap
            try {
                console.log('Trying Bootstrap initialization');
                var bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                    toggle: false
                });
                
                navbarToggler.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    bsCollapse.toggle();
                    console.log('Toggled using Bootstrap');
                });
                
                console.log('Bootstrap initialization successful');
            } catch (e) {
                // روش دوم: تغییر دستی کلاس‌ها
                console.log('Using manual toggle as fallback');
                navbarToggler.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    navbarCollapse.classList.toggle('show');
                    console.log('Toggled manually (classList)');
                });
            }
            
            // بستن منو هنگام کلیک روی لینک‌ها
            document.querySelectorAll('.nav-link').forEach(function(link) {
                link.addEventListener('click', function() {
                    if (window.innerWidth < 992) {
                        try {
                            bsCollapse.hide();
                        } catch (e) {
                            navbarCollapse.classList.remove('show');
                        }
                    }
                });
            });
            
            // بستن منو هنگام کلیک خارج از منو
            document.addEventListener('click', function(e) {
                if (window.innerWidth < 992 && 
                    !e.target.closest('.navbar-collapse') && 
                    !e.target.closest('.navbar-toggler') && 
                    navbarCollapse.classList.contains('show')) {
                    try {
                        bsCollapse.hide();
                    } catch (e) {
                        navbarCollapse.classList.remove('show');
                    }
                }
            });
        } else {
            console.warn('Navbar elements not found!');
            if (!navbarToggler) console.warn('Missing: .navbar-toggler');
            if (!navbarCollapse) console.warn('Missing: #navbarNavDropdown');
        }
    } else {
        console.error('Bootstrap JS not loaded!');
        // پلن B: تغییر دستی کلاس‌ها در صورت نبود بوت‌استرپ
        var navbarToggler = document.querySelector('.navbar-toggler');
        var navbarCollapse = document.getElementById('navbarNavDropdown');
        
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', function(e) {
                e.preventDefault();
                navbarCollapse.classList.toggle('show');
                console.log('Toggled manually in fallback mode');
            });
        }
    }
    
    console.log('Navbar JavaScript initialized');
});