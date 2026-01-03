// Chart Configuration and Initialization

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts on the page
    initExpensePieChart();
    initMonthlyTrendChart();
    initBudgetProgressChart();
});

function initExpensePieChart() {
    const pieChartCanvas = document.getElementById('expensePieChart');
    if (!pieChartCanvas) return;
    
    const ctx = pieChartCanvas.getContext('2d');
    const chartData = JSON.parse(pieChartCanvas.getAttribute('data-chart') || '{}');
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.labels || [],
            datasets: [{
                data: chartData.data || [],
                backgroundColor: chartData.colors || [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '₹' + context.raw.toFixed(2);
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function initMonthlyTrendChart() {
    const trendChartCanvas = document.getElementById('monthlyTrendChart');
    if (!trendChartCanvas) return;
    
    const ctx = trendChartCanvas.getContext('2d');
    const chartData = JSON.parse(trendChartCanvas.getAttribute('data-chart') || '{}');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels || [],
            datasets: [
                {
                    label: 'Salary',
                    data: chartData.salary_data || [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Expenses',
                    data: chartData.expense_data || [],
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += '₹' + context.raw.toFixed(2);
                            return label;
                        }
                    }
                }
            }
        }
    });
}

function initBudgetProgressChart() {
    const budgetBars = document.querySelectorAll('.budget-progress-bar');
    
    budgetBars.forEach(bar => {
        const percentage = parseFloat(bar.getAttribute('data-percentage')) || 0;
        const ctx = bar.getContext('2d');
        
        // Determine color based on percentage
        let color;
        if (percentage >= 90) {
            color = '#dc3545'; // Red
        } else if (percentage >= 70) {
            color = '#ffc107'; // Yellow
        } else {
            color = '#28a745'; // Green
        }
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [''],
                datasets: [{
                    data: [percentage],
                    backgroundColor: color,
                    borderColor: color,
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    y: {
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.raw.toFixed(1) + '% used';
                            }
                        }
                    }
                }
            }
        });
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Update dashboard stats in real-time
function updateDashboardStats(stats) {
    if (stats.salary) {
        document.getElementById('current-salary').textContent = formatCurrency(stats.salary);
    }
    if (stats.expenses) {
        document.getElementById('total-expenses').textContent = formatCurrency(stats.expenses);
    }
    if (stats.balance) {
        document.getElementById('remaining-balance').textContent = formatCurrency(stats.balance);
    }
    if (stats.savingsRate) {
        document.getElementById('savings-rate').textContent = stats.savingsRate + '%';
    }
}

// AJAX function to add expense
function addExpense(formData) {
    return fetch('/expenses/add/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Expense added successfully!', 'success');
            updateDashboardStats(data.stats);
            return true;
        } else {
            showNotification('Error adding expense: ' + data.error, 'error');
            return false;
        }
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid') || document.querySelector('.container');
    if (container) {
        container.insertBefore(notification, container.firstChild);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Export data function
function exportToCSV(data, filename) {
    const csv = convertToCSV(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

function convertToCSV(data) {
    const headers = Object.keys(data[0]);
    const rows = data.map(row => 
        headers.map(header => JSON.stringify(row[header])).join(',')
    );
    return [headers.join(','), ...rows].join('\n');
}