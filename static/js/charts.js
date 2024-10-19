function createChart(pollData, demographicFilters) {
    const ctx = document.getElementById('resultsChart').getContext('2d');
    
    // Filter data based on demographic filters
    const filteredData = filterData(pollData, demographicFilters);
    
    // Prepare data for the chart
    const labels = Object.keys(filteredData);
    const data = Object.values(filteredData);
    
    new Chart(ctx, {
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

function filterData(pollData, demographicFilters) {
    // Implement filtering logic based on demographic criteria
    // This is a placeholder and should be replaced with actual filtering logic
    return pollData;
}

document.addEventListener('DOMContentLoaded', function() {
    const applyFiltersBtn = document.getElementById('apply-filters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            const demographicFilters = {
                age: document.getElementById('age-filter').value,
                gender: document.getElementById('gender-filter').value,
                education: document.getElementById('education-filter').value
            };
            // Fetch updated poll data with filters
            fetch(`/results/${pollId}?${new URLSearchParams(demographicFilters)}`)
                .then(response => response.json())
                .then(data => {
                    createChart(data.pollData, demographicFilters);
                });
        });
    }
});
