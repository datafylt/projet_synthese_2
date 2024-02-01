document.addEventListener("DOMContentLoaded", function () {

    document.getElementById('rerunPipelineButton').addEventListener('click', function() {
        fetch('/rerun-pipeline', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Include additional headers as required
            },
            // No body is needed unless you want to send additional data to the server
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to trigger the pipeline');
            }
            return response.json();
        })
        .then(data => {
            console.log('Pipeline re-run successfully triggered:', data);
            // Optional: Display a success message or handle response further
        })
        .catch(error => {
            console.error('Error:', error);
            // Optional: Display an error message
        });
    });

     document.getElementById('retrieveWorkflow').addEventListener('click', function() {
        // Make an AJAX GET request to the Flask route
        fetch('/get-workflows')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Workflows retrieved:', data);
                // Here you can handle the workflow data, e.g., display it in your HTML
                // For demonstration, let's just log it to the console
            })
            .catch(error => {
                console.error('Error retrieving workflows:', error);
                // Optionally, handle the error, e.g., show an error message to the user
            });
    });
});
