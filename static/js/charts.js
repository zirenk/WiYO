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
            return;
        }

        const demographicFilters = {
            age: ageFilter.value,
            gender: genderFilter.value,
            education: educationFilter.value
        };

        console.log("Applying filters:", demographicFilters);

        // Show loading message
        if (loadingMessage) {
            loadingMessage.style.display = 'block';
        } else {
            console.warn("Loading message element not found");
        }

        if (debugMessageElement) {
            debugMessageElement.style.display = 'none';
        } else {
            console.warn("Debug message element not found");
        }

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
                if (loadingMessage) {
                    loadingMessage.style.display = 'none';
                }

                console.log("Fetched data:", data);
                if (data.pollData) {
                    if (debugMessageElement) {
                        debugMessageElement.textContent = 'Data fetched successfully';
                        debugMessageElement.style.display = 'block';
                    }
                    createChart(data.pollData, demographicFilters);
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    throw new Error("Unexpected response format");
                }
            })
            .catch(error => {
                // Hide loading message
                if (loadingMessage) {
                    loadingMessage.style.display = 'none';
                }

                console.error('Error fetching poll data:', error);
                if (debugMessageElement) {
                    debugMessageElement.textContent = `Error: ${error.message}`;
                    debugMessageElement.style.display = 'block';
                }
            });
    });
    
    // Initial chart creation
    const initialPollData = window.initialPollData;
    if (initialPollData) {
        createChart(initialPollData);
    } else {
        console.warn("Initial poll data not found");
    }
});
