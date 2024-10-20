let chart;

function createChart(pollData, demographicFilters) {
    console.log("Poll Data received:", pollData);
    console.log("Demographic Filters:", demographicFilters);

    const ctx = document.getElementById('resultsChart').getContext('2d');
    
    if (chart) {
        chart.destroy();
    }
    
    // Prepare data for the chart
    const labels = Object.keys(pollData);
    const data = Object.values(pollData);
    
    console.log("Chart Labels:", labels);
    console.log("Chart Data:", data);

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
}

document.addEventListener('DOMContentLoaded', function() {
    const applyFiltersBtn = document.getElementById('apply-filters');
    const pollIdElement = document.querySelector('[data-poll-id]');
    const debugMessageElement = document.getElementById('debug-message');
    
    if (applyFiltersBtn && pollIdElement) {
        const pollId = pollIdElement.dataset.pollId;
        
        applyFiltersBtn.addEventListener('click', function() {
            const demographicFilters = {
                age: document.getElementById('age-filter').value,
                gender: document.getElementById('gender-filter').value,
                education: document.getElementById('education-filter').value
            };
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
                    console.log("Fetched data:", data);
                    if (data.pollData) {
                        debugMessageElement.textContent = 'Data fetched successfully';
                        debugMessageElement.style.display = 'block';
                        createChart(data.pollData, demographicFilters);
                    } else if (data.error) {
                        throw new Error(data.error);
                    } else {
                        throw new Error("Unexpected response format");
                    }
                })
                .catch(error => {
                    console.error('Error fetching poll data:', error);
                    debugMessageElement.textContent = `Error: ${error.message}`;
                    debugMessageElement.style.display = 'block';
                });
        });
    } else {
        console.warn("Apply filters button or poll ID element not found");
    }
    
    // Initial chart creation
    const initialPollData = window.initialPollData;
    if (initialPollData) {
        createChart(initialPollData);
    }
});
