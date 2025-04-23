document.addEventListener('DOMContentLoaded', function() {
    fetchRateLimits();
    // Set up regular polling every 60 seconds
    setInterval(fetchRateLimits, 60000);
});

function fetchRateLimits() {
    fetch('/policy/api/rate-limits/')
        .then(response => response.json())
        .then(data => {
            updateRateLimitDisplay(data);
        })
        .catch(error => {
            console.error('Error fetching rate limits:', error);
        });
}

function updateRateLimitDisplay(data) {
    // Update the compact displays for embedded rate limit bars
    const hourlyRemainingDisplay = document.getElementById('hourly-remaining-display');
    const dailyRemainingDisplay = document.getElementById('daily-remaining-display');
    
    if (hourlyRemainingDisplay) hourlyRemainingDisplay.textContent = `${data.hourly.remaining}/${data.hourly.limit}`;
    if (dailyRemainingDisplay) dailyRemainingDisplay.textContent = `${data.daily.remaining}/${data.daily.limit}`;
}
