// CONFIGURATION: Ensure this matches your start.sh injected URL or hardcode it
const API_URL = "https://musical-spoon-v995gg9j6grfxj4x-5004.app.github.dev";

let pendingBookingPayload = null;

window.addEventListener('load', () => {
    // 1. Check Login
    const userId = localStorage.getItem('userId');
    if (!userId) {
        window.location.href = 'login.html';
        return;
    }

    // 2. Setup Date Picker
    const dateInput = document.getElementById('selected-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        dateInput.value = today;
    }
});

// --- UPDATED FUNCTION: Accepts roomId as 1st argument ---
async function openBookingModal(roomId, roomName, basePrice, city) {
    const dateInput = document.getElementById('selected-date').value;
    const userId = localStorage.getItem('userId'); 

    if (!dateInput) { alert("Please select a date first"); return; }
    
    // 🗑️ DELETED: The old "if (roomName...)" mapping logic is gone!
    // We now trust the roomId passed directly from the database.

    const payload = {
        user_id: userId, 
        room_id: roomId,  // <--- Using the Real ID
        room_name: roomName,
        date: dateInput,
        preview: true 
    };

    pendingBookingPayload = { ...payload, preview: false }; 

    try {
        const button = event.target; 
        const originalText = button.innerText;
        button.innerText = "Calculating...";
        button.disabled = true;
        
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        button.innerText = originalText; 
        button.disabled = false;

        if (response.ok) {
            document.getElementById('modal-room-name').innerText = `${roomName}, ${city}`;
            document.getElementById('modal-date').innerHTML = `<i class="fa-regular fa-calendar"></i> ${dateInput}`;
            
            document.getElementById('modal-base-price').innerText = `£${data.base_price.toFixed(2)}`;
            document.getElementById('modal-surcharge').innerText = `+£${data.surcharge.toFixed(2)}`;
            document.getElementById('modal-total').innerText = `£${data.total_price.toFixed(2)}`;
            
            // Weather info
            const temp = data.weather_temp !== undefined ? data.weather_temp : 21;
            document.getElementById('modal-temp').innerText = `${temp}°C`;
            
            // Calculate variance for display
            const variance = Math.abs(temp - 21.0);
            document.getElementById('modal-diff').innerText = `${variance.toFixed(1)}°C`;

            document.getElementById('confirm-modal').style.display = 'flex';
        } else {
            alert("Error: " + (data.error || "Unknown error"));
        }

    } catch (error) {
        console.error("Connection Error:", error);
        alert("Could not connect to Backend.");
        if(event.target) {
            event.target.innerText = "Book Now";
            event.target.disabled = false;
        }
    }
}

function closeModal() {
    document.getElementById('confirm-modal').style.display = 'none';
}

async function submitBooking() {
    if (!pendingBookingPayload) return;

    const button = document.querySelector('#confirm-modal button:last-child');
    button.innerText = "Processing...";
    button.disabled = true;

    try {
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pendingBookingPayload)
        });

        const result = await response.json();

        if (response.ok) {
            alert(`✅ BOOKING CONFIRMED!\nReference: #${result.id}\nTotal: £${result.total_price.toFixed(2)}`);
            window.location.href = "dashboard.html";
        } else {
            alert("Booking Failed: " + result.error);
        }
    } catch (error) {
        console.error(error);
        alert("Network Error.");
    } finally {
        button.innerText = "Confirm & Book →";
        button.disabled = false;
    }
}