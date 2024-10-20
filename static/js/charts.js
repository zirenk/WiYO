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

function showLoadingMessage() {
    const loadingMessage = document.getElementById('loading-message');
    console.log("Loading message element:", loadingMessage);
    if (loadingMessage) {
        loadingMessage.classList.remove('d-none');
        loadingMessage.classList.add('d-block');
        console.log('Loading message shown');
    } else {
        console.error('Loading message element not found');
    }
}

function hideLoadingMessage() {
    const loadingMessage = document.getElementById('loading-message');
    console.log("Loading message element:", loadingMessage);
    if (loadingMessage) {
        loadingMessage.classList.add('d-none');
        loadingMessage.classList.remove('d-block');
        console.log('Loading message hidden');
    } else {
        console.error('Loading message element not found');
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
        alert(message);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded");
    const applyFiltersBtn = document.getElementById('apply-filters');
    const pollIdElement = document.querySelector('[data-poll-id]');
    const loadingMessageElement = document.getElementById('loading-message');
    
    console.log("Apply filters button:", applyFiltersBtn);
    console.log("Poll ID element:", pollIdElement);
    console.log("Loading message element:", loadingMessageElement);

    if (!applyFiltersBtn) {
        console.error("Apply filters button not found");
        return;
    }

    if (!pollIdElement) {
        console.error("Poll ID element not found");
        return;
    }

    if (!loadingMessageElement) {
        console.error("Loading message element not found");
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

        showLoadingMessage();

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
                hideLoadingMessage();

                console.log("Fetched data:", data);
                if (data.pollData) {
                    showDebugMessage('Data fetched successfully');
                    setTimeout(() => {
                        hideDebugMessage();
                    }, 3000);
                    createChart(data.pollData, demographicFilters);
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    throw new Error("Unexpected response format");
                }
            })
            .catch(error => {
                hideLoadingMessage();

                console.error('Error fetching poll data:', error);
                showError(`Error: ${error.message}`);
            });
    });
    
    const initialPollData = window.initialPollData;
    if (initialPollData) {
        createChart(initialPollData);
    } else {
        console.warn("Initial poll data not found");
        showError("Initial poll data not found. Please try refreshing the page.");
    }
});
