$(document).ready(function() {
    // Initialize scheduler status
    updateSchedulerStatus();

    // Form submission
    $('#notification-settings-form').submit(function(e) {
        e.preventDefault();
        
        // Get form values
        var formData = {
            telegram_enabled: $('#telegram_enabled').is(':checked'),
            telegram_chat_id: $('#telegram_chat_id').val(),
            email_enabled: $('#email_enabled').is(':checked'),
            email_address: $('#email_address').val(),
            sms_enabled: $('#sms_enabled').is(':checked'),
            phone_number: $('#phone_number').val(),
            price_alerts_enabled: $('#price_alerts_enabled').is(':checked'),
            price_change_threshold: $('#price_change_threshold').val(),
            signals_enabled: $('#signals_enabled').is(':checked'),
            signals_frequency: $('#signals_frequency').val(),
            news_alerts_enabled: $('#news_alerts_enabled').is(':checked'),
            news_sources: $('#news_sources').val(),
            daily_report_enabled: $('#daily_report_enabled').is(':checked'),
            daily_report_time: $('#daily_report_time').val(),
            weekly_report_enabled: $('#weekly_report_enabled').is(':checked'),
            weekly_report_day: $('#weekly_report_day').val(),
            realtime_updates_enabled: $('#realtime_updates_enabled').is(':checked'),
            update_frequency: $('#update_frequency').val(),
            system_monitor_enabled: $('#system_monitor_enabled').is(':checked')
        };
        
        // Send data to server
        $.ajax({
            type: 'POST',
            url: '/update_notification_settings',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                // Show success message
                showAlert('success', 'تنظیمات با موفقیت ذخیره شد');
            },
            error: function(error) {
                // Show error message
                showAlert('danger', 'خطا در ذخیره‌سازی تنظیمات');
                console.error('Error saving settings:', error);
            }
        });
    });
    
    // Scheduler control buttons
    $('#start-scheduler-button').click(function() {
        // Show loading state
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال راه‌اندازی...');
        
        // Start scheduler
        $.ajax({
            type: 'GET',
            url: '/start_scheduler',
            success: function(response) {
                showAlert('success', 'زمان‌بندی خودکار با موفقیت راه‌اندازی شد');
                // Reset button and update status
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-play me-2"></i> راه‌اندازی زمان‌بندی خودکار');
                updateSchedulerStatus();
            },
            error: function(error) {
                showAlert('danger', 'خطا در راه‌اندازی زمان‌بندی خودکار');
                console.error('Error starting scheduler:', error);
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-play me-2"></i> راه‌اندازی زمان‌بندی خودکار');
            }
        });
    });
    
    $('#stop-scheduler-button').click(function() {
        // Show loading state
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال توقف...');
        
        // Stop scheduler
        $.ajax({
            type: 'GET',
            url: '/stop_scheduler',
            success: function(response) {
                showAlert('success', 'زمان‌بندی خودکار با موفقیت متوقف شد');
                // Reset button and update status
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-stop me-2"></i> توقف زمان‌بندی خودکار');
                updateSchedulerStatus();
            },
            error: function(error) {
                showAlert('danger', 'خطا در توقف زمان‌بندی خودکار');
                console.error('Error stopping scheduler:', error);
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-stop me-2"></i> توقف زمان‌بندی خودکار');
            }
        });
    });
    
    // Test notification buttons
    $('#test-telegram-button').click(function() {
        // Show loading state
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال ارسال...');
        
        // Send test message
        $.ajax({
            type: 'GET',
            url: '/test_telegram',
            success: function(response) {
                showAlert('success', 'پیام تست با موفقیت به تلگرام ارسال شد');
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fab fa-telegram me-2"></i> تست تلگرام');
            },
            error: function(error) {
                showAlert('danger', 'خطا در ارسال پیام تست به تلگرام');
                console.error('Error sending test telegram:', error);
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fab fa-telegram me-2"></i> تست تلگرام');
            }
        });
    });
    
    $('#test-email-button').click(function() {
        // Show loading state
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال ارسال...');
        
        // Send test email
        $.ajax({
            type: 'GET',
            url: '/test_email',
            success: function(response) {
                showAlert('success', 'ایمیل تست با موفقیت ارسال شد');
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-envelope me-2"></i> تست ایمیل');
            },
            error: function(error) {
                showAlert('danger', 'خطا در ارسال ایمیل تست');
                console.error('Error sending test email:', error);
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-envelope me-2"></i> تست ایمیل');
            }
        });
    });
    
    $('#test-sms-button').click(function() {
        // Show loading state
        var $btn = $(this);
        $btn.prop('disabled', true);
        $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> در حال ارسال...');
        
        // Send test SMS
        $.ajax({
            type: 'GET',
            url: '/test_notification',
            success: function(response) {
                showAlert('success', 'پیامک تست با موفقیت ارسال شد');
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-sms me-2"></i> تست پیامک');
            },
            error: function(error) {
                showAlert('danger', 'خطا در ارسال پیامک تست');
                console.error('Error sending test SMS:', error);
                // Reset button
                $btn.prop('disabled', false);
                $btn.html('<i class="fas fa-sms me-2"></i> تست پیامک');
            }
        });
    });
    
    // Update scheduler status
    function updateSchedulerStatus() {
        $.ajax({
            type: 'GET',
            url: '/scheduler_status',
            success: function(response) {
                // Update UI based on scheduler status
                if (response.running) {
                    $('#start-scheduler-button').addClass('disabled');
                    $('#stop-scheduler-button').removeClass('disabled');
                    // Update status badge
                    $('.list-group-item:contains("وضعیت ربات")').find('.badge').removeClass('bg-danger').addClass('bg-success').text('فعال');
                } else {
                    $('#start-scheduler-button').removeClass('disabled');
                    $('#stop-scheduler-button').addClass('disabled');
                    // Update status badge
                    $('.list-group-item:contains("وضعیت ربات")').find('.badge').removeClass('bg-success').addClass('bg-danger').text('غیرفعال');
                }
            },
            error: function(error) {
                console.error('Error getting scheduler status:', error);
            }
        });
    }
    
    // Poll for status updates every 30 seconds
    setInterval(updateSchedulerStatus, 30000);
    
    // Helper function to show alerts
    function showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Add alert to notification area
        $('#notification-area').html(alertHtml);
        
        // Auto dismiss after 5 seconds
        setTimeout(function() {
            $('.alert').alert('close');
        }, 5000);
    }
});