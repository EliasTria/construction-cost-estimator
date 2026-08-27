document.getElementById('estimate-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        project_type: document.getElementById('project-type').value,
        sq_meters: parseFloat(document.getElementById('sq-meters').value),
        budget: parseFloat(document.getElementById('budget').value)
    };
    
    try {
        const response = await fetch('/estimate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        // 🔍 Log the response to see what's coming back
        console.log('Response from server:', result);
        
        // ✅ Check if the response contains what we expect
        if (result.total_cost === undefined) {
            document.getElementById('results').innerHTML = `
                <h2>⚠️ Error</h2>
                <p>Something went wrong. The server returned:</p>
                <pre>${JSON.stringify(result, null, 2)}</pre>
            `;
            return;
        }
        
        // ✅ Display the results
        document.getElementById('results').innerHTML = `
            <h2>📊 Results</h2>
            <p><strong>Total Cost:</strong> €${result.total_cost.toFixed(2)}</p>
            <p><strong>Surplus:</strong> €${result.surplus.toFixed(2)}</p>
            <p><strong>Needs Loan:</strong> ${result.needs_loan ? '⚠️ Yes' : '✅ No'}</p>
            <p><strong>Can Build:</strong> ${result.can_build ? '✅ Yes' : '❌ No'}</p>
        `;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results').innerHTML = `
            <h2>❌ Error</h2>
            <p>Failed to connect to the server. Make sure FastAPI is running.</p>
            <p>Error: ${error.message}</p>
        `;
    }
});