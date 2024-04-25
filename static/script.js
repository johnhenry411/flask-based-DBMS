// Function to add a parrot
function addParrot(parrotData) {
    fetch('/add_parrot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(parrotData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to add parrot');
    })
    .then(data => {
        console.log(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to update a parrot
function updateParrot(parrotId, newData) {
    fetch(`/update_parrot/${parrotId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(newData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to update parrot');
    })
    .then(data => {
        console.log(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to search for parrots
function searchParrot(criteria) {
    const queryString = Object.entries(criteria).map(([key, value]) => `${key}=${value}`).join('&');
    fetch(`/search_parrot?${queryString}`)
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to search for parrots');
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to get all parrots
function getParrots() {
    fetch('/parrots')
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to get parrots');
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
