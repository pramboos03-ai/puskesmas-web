// SIK PUSKESMAS - Main Javascript

document.addEventListener('DOMContentLoaded', function () {
  // Toggle sidebar on mobile
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.app-sidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      sidebar.classList.toggle('show');
    });

    // Close when clicking outside on mobile
    document.addEventListener('click', function (event) {
      if (window.innerWidth < 992) {
        if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
          sidebar.classList.remove('show');
        }
      }
    });
  }

  // Auto hide flash alerts after 6 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {
        // Fallback
        alert.style.display = 'none';
      }
    }, 6000);
  });
});
