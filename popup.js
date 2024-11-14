// popup.js

// Function to call the Python server to perform SQL injection scanning
function scanForSQLInjection(url) {
    fetch('http://127.0.0.1:5000/scan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('results').innerText = JSON.stringify(data.results, null, 2);
    })
    .catch(error => console.error("Error during scan:", error));
}

// Get the active tab URL and start scanning
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    let activeTab = tabs[0];
    scanForSQLInjection(activeTab.url);
});
