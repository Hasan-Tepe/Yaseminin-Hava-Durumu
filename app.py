from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from database import get_db_connection, init_db
import urllib.parse

load_dotenv()

app = Flask(__name__)
app.secret_key = "super_secret_weather_key_for_flask_flash"

# Ensure DB is initialized
init_db()

def get_advice(weather_id, temp, wind_speed):
    # Weather condition codes: https://openweathermap.org/weather-conditions
    # 2xx: Thunderstorm, 3xx: Drizzle, 5xx: Rain, 6xx: Snow, 7xx: Atmosphere, 800: Clear, 80x: Clouds
    
    advice = "Bugün senin için harika bir gün olsun! ❤️" # Default
    
    # Temperature based conditions
    if temp < 5:
        advice = "Hava dışarıda buz gibi. Lütfen çok kalın giyin, atkını ve bereni takmayı sakın unutma! ❄️"
    elif temp < 15:
        advice = "Hava biraz serin, dışarı çıkarken bir ceket veya hırka alsan iyi olur tatlım. 🧥"
    elif temp > 30:
        advice = "Hava çok sıcak! Bol bol su içmeyi ve güneş kremini sürmeyi sakın unutma. ☀️"
        
    # Weather conditions (Overrides temp based a bit or adds to it)
    if 200 <= weather_id <= 232:
        advice = "Dışarıda fırtına var gibi görünüyor, eğer mecbur değilsen lütfen evde, sıcakta kal. ⛈️"
    elif 300 <= weather_id <= 531:
        advice = "Yağmur yağıyor veya yağmak üzere. Yanına şemsiyeni almayı sakın unutma bitanem. ☔"
    elif 600 <= weather_id <= 622:
        advice = "Kar yağıyor! Çok sıkı giyin ve adımlarına dikkat et, yerler kaygan olabilir. ⛄"
    elif weather_id == 800 and temp > 20:
        advice = "Bugün pırıl pırıl bir güneş var! Güneş kremini unutma, enerjin de güneş gibi parlasın. 🌞"
    elif 801 <= weather_id <= 804:
        advice = "Hava biraz kapalı. Bu modunu düşürmesin, akşam eve gelince sıcak bir kahve yap kendine. ☕"
        
    if wind_speed > 25:
        advice += " Rüzgar da epey sert esiyor, dikkatli ol! 🌬️"
        
    advice += "\n\nDikkatli ol, Seni Seviyorum ❤️"
        
    return advice

@app.route('/')
def index():
    conn = get_db_connection()
    settings = conn.execute('SELECT * FROM user_settings LIMIT 1').fetchone()
    
    # Get default location
    default_loc = None
    city = None
    location_name = "Konum Yok"

    default_loc_tuple = conn.execute('SELECT * FROM locations WHERE is_default = 1 LIMIT 1').fetchone()
    if not default_loc_tuple:
        default_loc_tuple = conn.execute('SELECT * FROM locations LIMIT 1').fetchone()
        
    if default_loc_tuple:
        default_loc = {
            'id': default_loc_tuple[0],
            'alias': default_loc_tuple[1],
            'city_name': default_loc_tuple[2],
            'is_default': default_loc_tuple[3],
            'image_type': default_loc_tuple[4] if len(default_loc_tuple) > 4 and default_loc_tuple[4] else 'location_home'
        }
        city = default_loc['city_name']
        location_name = default_loc['alias']
        
    # Special tags check format DD-MM
    today_str = datetime.now().strftime('%d-%m')
    today_str_formatted = datetime.now().strftime('%Y-%m-%d')
    special_tag = conn.execute('SELECT * FROM special_tags WHERE date = ?', (today_str,)).fetchone()
    special_message = special_tag['custom_message'] if special_tag else None

    conn.close()
    
    # Pretty Date Format
    months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    
    # Weather API logic
    weather_data = None
    advice_message = None
    hourly_forecast = []
    daily_forecast = []
    
    if settings and settings['api_key'] and default_loc:
        api_key = settings['api_key']
        
        # Append ,TR if no comma is provided by user to prevent matching random foreign cities
        city_query = city.split('/')[0].strip() if city else ""
        if city_query and ',' not in city_query:
            api_query_string = f"{city_query},TR"
        else:
            api_query_string = city_query
            
        url = f"http://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(api_query_string)}&appid={api_key}&units=metric&lang=tr"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                weather_data = {
                    'id': data['weather'][0]['id'],
                    'temp': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': round(data['wind']['speed'] * 3.6, 1) # m/s to km/h
                }
                advice_message = get_advice(data['weather'][0]['id'], weather_data['temp'], weather_data['wind_speed'])

            # Forecast API
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={urllib.parse.quote(api_query_string)}&appid={api_key}&units=metric&lang=tr"
            r_f = requests.get(forecast_url, timeout=5)
            if r_f.status_code == 200:
                f_data = r_f.json()
                for item in f_data['list']:
                    dt_txt = item['dt_txt']
                    date_part, time_part = dt_txt.split(' ')
                    
                    # Hourly
                    if len(hourly_forecast) < 6: # Next 18 hours approx
                        hourly_forecast.append({
                            'time': time_part[:5],
                            'temp': round(item['main']['temp']),
                            'icon': item['weather'][0]['icon']
                        })
                    
                    # Daily (grab first available time for the next days)
                    if date_part != today_str_formatted:
                        date_obj = datetime.strptime(date_part, '%Y-%m-%d')
                        day_name = days[date_obj.weekday()]
                        if not any(d['day'] == day_name for d in daily_forecast) and len(daily_forecast) < 4:
                            daily_forecast.append({
                                'day': day_name,
                                'temp': round(item['main']['temp']),
                                'icon': item['weather'][0]['icon'],
                                'desc': item['weather'][0]['description']
                            })

        except Exception as e:
            print("Weather API error:", e)
    
    current_date = f"{datetime.now().day} {months[datetime.now().month-1]}, {days[datetime.now().weekday()]}"

    return render_template(
        'index.html', 
        settings=settings, 
        weather=weather_data, 
        advice_message=advice_message,
        location_name=location_name,
        current_date=current_date,
        special_message=special_message,
        hourly_forecast=hourly_forecast,
        daily_forecast=daily_forecast,
        default_loc=default_loc
    )

@app.route('/add_location', methods=['POST'])
def add_location():
    conn = get_db_connection()
    new_loc_alias = request.form.get('new_loc_alias', '').strip()
    new_loc_city = request.form.get('new_loc_city', '').strip()
    image_type = request.form.get('image_type', 'location_home')
    
    settings = conn.execute('SELECT * FROM user_settings LIMIT 1').fetchone()
    api_key = settings['api_key'] if settings else ""
    
    if new_loc_alias and new_loc_city:
        # Validate City
        city_query = new_loc_city.split('/')[0].strip()
        if ',' not in city_query:
            api_query_string = f"{city_query},TR"
        else:
            api_query_string = city_query
            
        validate_url = f"http://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(api_query_string)}&appid={api_key}&units=metric"
        try:
            r = requests.get(validate_url, timeout=5)
            if r.status_code == 200:
                data = r.json()
                resolved_city_name = f"{data['name']}, {data['sys']['country']}"
                conn.execute('INSERT INTO locations (alias, city_name, is_default, image_type) VALUES (?, ?, 0, ?)', (new_loc_alias, resolved_city_name, image_type))
                conn.commit()
                flash(f"Konum başarıyla eklendi! ({resolved_city_name})", "success")
            else:
                flash("Girdiğiniz şehir Hava Durumu sisteminde bulunamadı. Lütfen geçerli bir şehir adı girin (Örn: Konya veya Konya, TR).", "error")
        except:
            flash("Bağlantı hatası oluştu, konum doğrulanamadı.", "error")
            
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_location/<int:loc_id>', methods=['POST'])
def delete_location(loc_id):
    conn = get_db_connection()
    # Check if we are deleting the default location
    loc = conn.execute('SELECT is_default FROM locations WHERE id = ?', (loc_id,)).fetchone()
    if loc:
        conn.execute('DELETE FROM locations WHERE id = ?', (loc_id,))
        if loc['is_default']:
            # Assign a new default location if possible
            new_default = conn.execute('SELECT id FROM locations LIMIT 1').fetchone()
            if new_default:
                conn.execute('UPDATE locations SET is_default = 1 WHERE id = ?', (new_default['id'],))
        conn.commit()
    conn.close()
    return redirect(url_for('settings_page'))

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Handle settings update
        user_name = request.form.get('user_name', '').strip()
        api_key = request.form.get('api_key', '').strip()
        default_loc_id = request.form.get('default_location')
        
        # New location logic
        new_loc_alias = request.form.get('new_loc_alias', '').strip()
        new_loc_city = request.form.get('new_loc_city', '').strip()
        
        # Update user settings
        conn.execute('UPDATE user_settings SET user_name = ?, api_key = ? WHERE id = (SELECT id FROM user_settings LIMIT 1)', 
                     (user_name, api_key))
        
        # Add new location if provided
        if new_loc_alias and new_loc_city:
            city_query = new_loc_city.split('/')[0].strip()
            if ',' not in city_query:
                api_query_string = f"{city_query},TR"
            else:
                api_query_string = city_query
                
            validate_url = f"http://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(api_query_string)}&appid={api_key}&units=metric"
            try:
                r = requests.get(validate_url, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    resolved_city_name = f"{data['name']}, {data['sys']['country']}"
                    conn.execute('INSERT INTO locations (alias, city_name, is_default, image_type) VALUES (?, ?, 0, ?)', (new_loc_alias, resolved_city_name, 'location_home'))
                    flash(f"Konum eklendi! ({resolved_city_name})", "success")
                else:
                    flash("Girdiğiniz şehir bulunamadı. Sadece geçerli güncellemeler yapıldı.", "error")
            except:
                flash("Şehir doğrulanırken hata oluştu.", "error")
            
        # Update default location
        if default_loc_id:
            conn.execute('UPDATE locations SET is_default = 0')
            conn.execute('UPDATE locations SET is_default = 1 WHERE id = ?', (default_loc_id,))
            
        conn.commit()
        conn.close()
        return redirect(url_for('settings_page'))
    
    settings = conn.execute('SELECT * FROM user_settings LIMIT 1').fetchone()
    locations = conn.execute('SELECT * FROM locations').fetchall()
    conn.close()
    
    return render_template('settings.html', settings=settings, locations=locations)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
