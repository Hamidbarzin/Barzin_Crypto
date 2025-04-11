// اسکریپت ساده برای منوی ثابت
document.addEventListener('DOMContentLoaded', function() {
    console.log('Navbar JavaScript initializing');
    
    // در این نسخه جدید، دیگر به منوی کشویی نیازی نیست
    // فقط برای تطبیق با استایل‌های مختلف بوت‌استرپ، بررسی می‌کنیم که آیا بوت‌استرپ لود شده است
    if (typeof bootstrap !== 'undefined') {
        console.log('Bootstrap JS is detected');
        console.log('Using fixed menu design - no dropdown needed');
    } else {
        console.log('Bootstrap JS not loaded, but not needed for the fixed menu');
    }
    
    // اضافه کردن افکت‌های هاور برای لینک‌های منو
    document.querySelectorAll('.nav-link').forEach(function(link) {
        link.addEventListener('mouseenter', function() {
            this.style.transition = 'color 0.3s ease';
        });
    });
    
    console.log('Navbar JavaScript initialized');
});