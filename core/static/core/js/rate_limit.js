document.addEventListener('DOMContentLoaded', function() {
    fetchRateLimits();
});

function fetchRateLimits() {
    fetch('/policy/api/rate-limits/')
        .then(response => response.json())
        .then(data => {
            updateRateLimitDisplay(data);
        })
        .catch(error => {
            console.error('Error fetching rate limits:', error);
            displayError('Failed to fetch rate limits. Please try again later.');
        });
}

function updateRateLimitDisplay(data) {
    document.getElementById('hourly-limit').textContent = data.hourly.limit;
    document.getElementById('hourly-remaining').textContent = data.hourly.remaining;
    document.getElementById('daily-limit').textContent = data.daily.limit;
    document.getElementById('daily-remaining').textContent = data.daily.remaining;
}

function displayError(message) {
    const errorContainer = document.getElementById('rate-limit-errors');
    errorContainer.textContent = message;
}
