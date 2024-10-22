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
    const labels = Object.keys(pollData.results);
    const data = Object.values(pollData.results);
    
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
                },
                plugins: {
                    title: {
                        display: true,
                        text: pollData.question
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

        // Show loading message
        showLoadingMessage();

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

                console.log("Fetched data:", data);
                if (data.poll_data) {
                    showDebugMessage('Data fetched successfully');
                    setTimeout(() => {
                        hideDebugMessage();
                    }, 3000); // Hide after 3 seconds
                    createChart(data.poll_data, demographicFilters);
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    throw new Error("Unexpected response format");
                }
            })
            .catch(error => {
                // Hide loading message
                hideLoadingMessage();

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
    const loadingProgress = document.getElementById('loading-progress');
    const loadingText = document.getElementById('loading-text');
    if (loadingMessage && loadingProgress && loadingText) {
        loadingMessage.classList.remove('d-none');
        loadingMessage.classList.add('d-block');
        
        let progress = 0;
        const interval = setInterval(() => {
            progress += 10;
            if (progress <= 100) {
                loadingProgress.style.width = `${progress}%`;
                loadingProgress.setAttribute('aria-valuenow', progress);
                
                if (progress < 30) {
                    loadingText.textContent = 'Applying demographic filters...';
                } else if (progress < 60) {
                    loadingText.textContent = 'Fetching filtered poll results...';
                } else if (progress < 90) {
                    loadingText.textContent = 'Preparing chart data...';
                } else {
                    loadingText.textContent = 'Finalizing results...';
                }
            } else {
                clearInterval(interval);
            }
        }, 200);
    } else {
        console.warn("Loading message elements not found");
    }
}

function hideLoadingMessage() {
    const loadingMessage = document.getElementById('loading-message');
    if (loadingMessage) {
        loadingMessage.classList.remove('d-block');
        loadingMessage.classList.add('d-none');
    } else {
        console.warn("Loading message element not found");
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
