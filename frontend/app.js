// CONFIGURATION: Ensure this matches your forwarded Codespaces URL (No trailing slash!)
// Example: "https://studious-space-waddle-5004.app.github.dev"
const API_URL = "https://musical-spoon-v995gg9j6grfxj4x-5004.app.github.dev"
// Global variable to store the payload for the final step
let pendingBookingPayload = null;

async function openBookingModal(roomName, basePrice, city) {
    const dateInput = document.getElementById('selected-date').value;
    if (!dateInput) { alert("Please select a date first"); return; }
    
    // 1. Prepare Payload with PREVIEW flag
    const payload = {
        user_id: 1,
        room_id: roomName.includes("Mitte") || roomName.includes("Westminster") || roomName.includes("Louvre") ? 1 : 2, 
        room_name: roomName,
        date: dateInput,
        preview: true  // <--- THIS TELLS BACKEND: "DON'T SAVE YET!"
    };

    // Save this for later (when user clicks Confirm)
    pendingBookingPayload = { ...payload, preview: false }; // Prepare the real version

    try {
        console.log("Fetching price preview...");
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            // 2. Update Modal with PREVIEW Data
            document.getElementById('modal-room-name').innerText = `${roomName}, ${city}`;
            document.getElementById('modal-date').innerHTML = `<i class="fa-regular fa-calendar"></i> ${dateInput}`;
            
            document.getElementById('modal-base-price').innerText = `£${data.base_price.toFixed(2)}`;
            document.getElementById('modal-surcharge').innerText = `+£${data.surcharge.toFixed(2)}`;
            document.getElementById('modal-total').innerText = `£${data.total_price.toFixed(2)}`;
            document.getElementById('modal-temp').innerText = `${data.weather_temp}°C`;
            
            const variance = Math.abs(data.weather_temp - 21);
            document.getElementById('modal-diff').innerText = `${variance}°C`;

            // Show the Modal
            document.getElementById('confirm-modal').style.display = 'flex';
        } else {
            alert("Error calculating price: " + (data.error || "Unknown error"));
        }

    } catch (error) {
        console.error("Connection Error:", error);
        alert("Could not connect to Backend.");
    }
}

function closeModal() {
    document.getElementById('confirm-modal').style.display = 'none';
}

async function submitBooking() {
    // 3. The REAL Booking Step
    if (!pendingBookingPayload) return;

    const button = event.target;
    button.innerText = "Processing...";
    button.disabled = true;

    try {
        // Send the REAL request (preview: false)
        const response = await fetch(`${API_URL}/bookings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pendingBookingPayload)
        });

        const result = await response.json();

        if (response.ok) {
            alert(`✅ BOOKING CONFIRMED!\n\nReference: #${result.id}\nTotal: £${result.total_price.toFixed(2)}`);
            window.location.href = "dashboard.html";
        } else {
            alert("Booking Failed: " + result.error);
        }
    } catch (error) {
        alert("Network Error: Could not confirm booking.");
    } finally {
        button.innerText = "Confirm & Book →";
        button.disabled = false;
    }
        // --- AUTOMATICALLY SET DATE TO TODAY & BLOCK PAST ---
    window.addEventListener('load', () => {
        const dateInput = document.getElementById('selected-date');
        
        if (dateInput) {
            // 1. Get Today's Date in YYYY-MM-DD format
            const today = new Date().toISOString().split('T')[0];
            
            // 2. Set the "min" attribute (Blocks past dates selection)
            dateInput.setAttribute('min', today);
            
            // 3. FORCE THE VALUE TO TODAY (This fixes the "blank" input)
            dateInput.value = today;

            console.log(`Date picker defaulted to: ${today}`);
        }
    });
}