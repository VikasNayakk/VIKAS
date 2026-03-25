/* Dashboard JavaScript - Handle user interactions */

// Send command when button clicked or Enter pressed
document.getElementById('send-btn').addEventListener('click', sendCommand);
document.getElementById('command-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendCommand();
});

// Send command to server
async function sendCommand() {
    const input = document.getElementById('command-input');
    const command = input.value.trim();
    
    if (!command) return;
    
    try {
        // Show loading state
        const btn = document.getElementById('send-btn');
        btn.disabled = true;
        btn.textContent = '⏳ Processing...';
        
        // Send to server
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command })
        });
        
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Add to history
        addToHistory(command);
        
        // Clear input
        input.value = '';
        
        // Show success message
        btn.textContent = '✅ Sent!';
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = '🚀 Send';
        }, 1500);
        
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
        const btn = document.getElementById('send-btn');
        btn.disabled = false;
        btn.textContent = '🚀 Send';
    }
}

// Add command to history display
function addToHistory(command) {
    const historyList = document.getElementById('history-list');
    
    // Remove empty message if exists
    const empty = historyList.querySelector('.empty');
    if (empty) empty.remove();
    
    // Create new history item
    const now = new Date().toLocaleTimeString();
    const item = document.createElement('div');
    item.className = 'history-item';
    item.innerHTML = `
        <span>${command}</span>
        <span class="history-time">${now}</span>
    `;
    
    // Add to top
    historyList.insertBefore(item, historyList.firstChild);
    
    // Keep only last 20 items
    while (historyList.children.length > 20) {
        historyList.removeChild(historyList.lastChild);
    }
}

// Set command from hint tag
function setCommand(cmd) {
    document.getElementById('command-input').value = cmd;
    document.getElementById('command-input').focus();
}

// Load initial history
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        if (data.history.length === 0) {
            historyList.innerHTML = `
                <div class="history-item empty">
                    No commands yet. Start by typing a command above!
                </div>
            `;
            return;
        }
        
        // Add history items in reverse order (newest first)
        data.history.reverse().forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            const time = new Date(item.timestamp).toLocaleTimeString();
            historyItem.innerHTML = `
                <span>${item.command}</span>
                <span class="history-time">${time}</span>
            `;
            historyList.appendChild(historyItem);
        });
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

// Load status on page load
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update status badge
        const statusText = document.getElementById('status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (data.status === 'online') {
            statusText.textContent = 'Online';
            statusDot.style.background = '#00ff88';
        } else {
            statusText.textContent = 'Offline';
            statusDot.style.background = '#ff3333';
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadHistory();
    updateStatus();
    
    // Update status every 5 seconds
    setInterval(updateStatus, 5000);
    
    // Focus on input field
    document.getElementById('command-input').focus();
});
