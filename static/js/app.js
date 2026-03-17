document.addEventListener('DOMContentLoaded', () => {
    console.log("WeatherMate app initialized.");
    
    // Check if weather condition is exposed via meta tag or script variable
    // We will inject a variable in base.html from Jinja
    if (typeof window.weatherId !== 'undefined') {
        applyWeatherAnimation(window.weatherId);
    }
});

function applyWeatherAnimation(weatherId) {
    const bgContainer = document.getElementById('weather-background');
    if (!bgContainer) return;
    
    bgContainer.innerHTML = ''; // Clear previous
    let html = '';
    
    // Conditions based on OpenWeatherMap codes
    if (weatherId >= 200 && weatherId <= 531) {
        // Rain / Drizzle / Thunderstorm
        bgContainer.style.background = 'rgba(0, 0, 0, 0.4)'; // Darken a bit more for rain
        for(let i=0; i<40; i++) {
            let left = Math.floor(Math.random() * 100);
            let delay = Math.random() * 2;
            let duration = Math.random() * 1 + 0.5;
            html += `<div class="rain-drop" style="left: ${left}%; animation-delay: ${delay}s; animation-duration: ${duration}s;"></div>`;
        }
    } 
    else if (weatherId >= 600 && weatherId <= 622) {
        // Snow
        for(let i=0; i<50; i++) {
            let left = Math.floor(Math.random() * 100);
            let delay = Math.random() * 3;
            let duration = Math.random() * 3 + 2;
            let size = Math.random() * 5 + 3;
            html += `<div class="snowflake" style="left: ${left}%; width: ${size}px; height: ${size}px; animation-delay: ${delay}s; animation-duration: ${duration}s;"></div>`;
        }
    }
    if (weatherId === 800 || weatherId === 801 || weatherId === 802) {
        // Clear / Sunny / Few Clouds
        if (typeof window.weatherIcon !== 'undefined' && window.weatherIcon.includes('n')) {
             // Night - stars
             for(let i=0; i<30; i++) {
                let left = Math.floor(Math.random() * 100);
                let top = Math.floor(Math.random() * 100);
                let delay = Math.random() * 5;
                html += `<div class="star" style="left: ${left}%; top: ${top}%; animation-delay: ${delay}s;"></div>`;
             }
        } else {
             // Sun
             html += `<div class="sun-orb"></div><div class="sun-ray"></div>`;
        }
    }
    
    if (weatherId >= 801 && weatherId <= 804) {
        // Clouds
        bgContainer.style.background = 'rgba(255, 255, 255, 0.05)';
        html += '<div class="cloud"></div><div class="cloud" style="animation-delay: -15s; top: 30%; opacity: 0.3;"></div>';
    }

    bgContainer.innerHTML = html;
}
