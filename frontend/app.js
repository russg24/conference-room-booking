// CONFIGURATION: Check Port 5004 URL (No trailing slash)
const API_URL = "https://musical-spoon-v995gg9j6grfxj4x-5004.app.github.dev";

let pendingBookingPayload = null;

// 1. INITIALIZATION: Run immediately on load
window.addEventListener('load', () => {
    // Check Login
    const userId = localStorage.getItem('userId');
    if (!userId) {
        window.location.href = 'login.html';
        return;
    }

    // Set Date Picker to Today
    const dateInput = document.getElementById('selected-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        dateInput.value = today;
    }
});

// 2. OPEN PREVIEW MODAL
async function openBookingModal(roomName, basePrice, city) {
    const dateInput = document.getElementById('selected-date').value;
    const userId = localStorage.getItem('userId'); // FIX: Use Real User ID

    if (!dateInput) { alert("Please select a date first"); return; }
    
    // Simple Mapping for demo purposes
    let roomId = 1; 
    if (roomName.includes("Alexanderplatz") || roomName.includes("Big Ben") || roomName.includes("Eiffel")) {
        roomId = 2;
    }

    const payload = {
        user_id: userId, 
        room_id: roomId, 
        room_name: roomName,
        date: dateInput,
        preview: true 
    };

    pendingBookingPayload = { ...payload, preview: false }; 

    try {
        const button = event.target; 
        button.innerText = "Calculating...";
        
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        button.innerText = "Book Now"; 

        if (response.ok) {
            document.getElementById('modal-room-name').innerText = `${roomName}, ${city}`;
            document.getElementById('modal-date').innerHTML = `<i class="fa-regular fa-calendar"></i> ${dateInput}`;
            document.getElementById('modal-base-price').innerText = `£${data.base_price.toFixed(2)}`;
            document.getElementById('modal-surcharge').innerText = `+£${data.surcharge.toFixed(2)}`;
            document.getElementById('modal-total').innerText = `£${data.total_price.toFixed(2)}`;
            
            // Show Modal
            document.getElementById('confirm-modal').style.display = 'flex';
        } else {
            alert("Error: " + data.error);
        }

    } catch (error) {
        console.error("Connection Error:", error);
        alert("Could not connect to Backend.");
        event.target.innerText = "Book Now";
    }
}

// 3. CLOSE MODAL
function closeModal() {
    document.getElementById('confirm-modal').style.display = 'none';
}

// 4. SUBMIT REAL BOOKING
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
            alert(`✅ BOOKING CONFIRMED!\nReference: #${result.id}`);
            window.location.href = "dashboard.html";
        } else {
            alert("Booking Failed: " + result.error);
        }
    } catch (error) {
        alert("Network Error.");
    } finally {
        button.innerText = "Confirm & Book →";
        button.disabled = false;
    }
}