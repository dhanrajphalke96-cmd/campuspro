/* ─── Chart.js Dark Theme Defaults ─── */
document.addEventListener('DOMContentLoaded', function() {
    // Set Chart.js defaults for dark theme
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = '#a0a3ab';
        Chart.defaults.borderColor = '#2d3039';
        Chart.defaults.plugins.legend.labels.padding = 16;
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
    }

    // ─── Sidebar Toggle ───
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    const mobileToggle = document.getElementById('mobile-toggle');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
        });
    }

    if (mobileToggle) {
        mobileToggle.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
        });
    }

    // Restore sidebar state
    if (localStorage.getItem('sidebar-collapsed') === 'true' && window.innerWidth > 992) {
        sidebar?.classList.add('collapsed');
    }

    // Close mobile sidebar on outside click
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 992 && sidebar?.classList.contains('mobile-open')) {
            if (!sidebar.contains(e.target) && !mobileToggle?.contains(e.target)) {
                sidebar.classList.remove('mobile-open');
            }
        }
    });

    // ─── Auto-dismiss alerts ───
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'all 0.3s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });

    // ─── Notification mark as read ───
    document.querySelectorAll('.notif-mark-read').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const pk = this.dataset.pk;
            fetch(`/notifications/${pk}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            }).then(res => {
                if (res.ok) {
                    this.closest('.notif-item')?.classList.add('read');
                    updateNotifBadge();
                }
            });
        });
    });

    // ─── Active nav link ───
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/dashboard/' && currentPath === '/dashboard/') {
            link.classList.add('active');
        }
    });

    // ─── Tooltips ───
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
    }
});

// ─── Helpers ───
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateNotifBadge() {
    const badge = document.querySelector('.notif-badge');
    if (badge) {
        let count = parseInt(badge.textContent) - 1;
        if (count <= 0) {
            badge.style.display = 'none';
        } else {
            badge.textContent = count;
        }
    }
}

// ─── Dashboard Chart helper ───
function createChart(canvasId, type, labels, datasets, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: type,
        data: { labels: labels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            ...options
        }
    });
}
