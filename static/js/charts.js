let chart;

function createChart(pollData, demographicFilters) {
    console.log("Poll Data received:", pollData);
    console.log("Demographic Filters:", demographicFilters);

    const ctx = document.getElementById('resultsChart');
    if (!ctx) {
        console.error("Canvas element 'resultsChart' not found");
        return;
    }

    if (chart) {
        chart.destroy();
    }
    
    // Prepare data for the chart
    const labels = Object.keys(pollData);
    const data = Object.values(pollData);
    
    console.log("Chart Labels:", labels);
    console.log("Chart Data:", data);

    try {
        chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Responses',
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Responses'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error("Error creating chart:", error);
        showError("An error occurred while creating the chart. Please try again.");
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const applyFiltersBtn = document.getElementById('apply-filters');
    const pollIdElement = document.querySelector('[data-poll-id]');
    const debugMessageElement = document.getElementById('debug-message');
    const loadingMessage = document.getElementById('loading-message');
    
    if (!applyFiltersBtn) {
        console.error("Apply filters button not found");
        return;
    }

    if (!pollIdElement) {
        console.error("Poll ID element not found");
        return;
    }

    const pollId = pollIdElement.dataset.pollId;
    
    applyFiltersBtn.addEventListener('click', function() {
        const ageFilter = document.getElementById('age-filter');
        const genderFilter = document.getElementById('gender-filter');
        const educationFilter = document.getElementById('education-filter');

        if (!ageFilter || !genderFilter || !educationFilter) {
            console.error("One or more filter elements not found");
            showError("An error occurred while applying filters. Please try again.");
            return;
        }

        const demographicFilters = {
            age: ageFilter.value,
            gender: genderFilter.value,
            education: educationFilter.value
        };

        console.log("Applying filters:", demographicFilters);

        // Show loading message and spinner
        showLoadingMessage();
        console.log("showLoadingMessage called");

        // Fetch updated poll data with filters
        fetch(`/results/${pollId}?${new URLSearchParams(demographicFilters)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Hide loading message
                hideLoadingMessage();
                console.log("hideLoadingMessage called");

                console.log("Fetched data:", data);
                if (data.pollData) {
                    showDebugMessage('Data fetched successfully');
                    setTimeout(() => {
                        hideDebugMessage();
                    }, 3000); // Hide after 3 seconds
                    createChart(data.pollData, demographicFilters);
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    throw new Error("Unexpected response format");
                }
            })
            .catch(error => {
                // Hide loading message
                hideLoadingMessage();
                console.log("hideLoadingMessage called");

                console.error('Error fetching poll data:', error);
                showError(`Error: ${error.message}`);
            });
    });
    
    // Initial chart creation
    const initialPollData = window.initialPollData;
    if (initialPollData) {
        createChart(initialPollData);
    } else {
        console.warn("Initial poll data not found");
        showError("Initial poll data not found. Please try refreshing the page.");
    }
});

function showLoadingMessage() {
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.classList.remove('d-none');
        loadingMessage.classList.add('d-block');
        
        const loadingProgress = document.getElementById('loading-progress');
        const loadingText = document.getElementById('loading-text');
        
        if (loadingProgress && loadingText) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += 10;
                if (progress <= 100) {
                    loadingProgress.style.width = `${progress}%`;
                    loadingProgress.setAttribute('aria-valuenow', progress);
                    
                    if (progress < 30) {
                        loadingText.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Applying demographic filters...';
                    } else if (progress < 60) {
                        loadingText.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Fetching filtered poll results...';
                    } else if (progress < 90) {
                        loadingText.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Preparing chart data...';
                    } else {
                        loadingText.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Finalizing results...';
                    }
                } else {
                    clearInterval(interval);
                }
            }, 200);
        }
    } else {
        console.error("Loading message element not found");
    }
}

function hideLoadingMessage() {
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.classList.add('d-none');
        loadingMessage.classList.remove('d-block');
    } else {
        console.error("Loading message element not found");
    }
}

function showDebugMessage(message) {
    const debugMessageElement = document.getElementById('debug-message');
    if (debugMessageElement) {
        debugMessageElement.textContent = message;
        debugMessageElement.classList.remove('d-none');
        debugMessageElement.classList.add('d-block');
    } else {
        console.warn("Debug message element not found");
    }
}

function hideDebugMessage() {
    const debugMessageElement = document.getElementById('debug-message');
    if (debugMessageElement) {
        debugMessageElement.classList.remove('d-block');
        debugMessageElement.classList.add('d-none');
    }
}

function showError(message) {
    const errorMessageElement = document.getElementById('error-message');
    if (errorMessageElement) {
        errorMessageElement.textContent = message;
        errorMessageElement.classList.remove('d-none');
        errorMessageElement.classList.add('d-block');
    } else {
        console.warn("Error message element not found");
        alert(message); // Fallback to alert if error message element is not found
    }
}
