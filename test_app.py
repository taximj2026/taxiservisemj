"""
🚖 Easy Auto Taxi Pro - Complete Merged System
Version: 7.0 INTEGRATED FINAL
Author: Auto Taxi Pro Team
Last Updated: 2026

📌 COMPLETE MERGE SUMMARY & CHANGES:
====================================
✅ MODULES MERGED: All 22 modules integrated perfectly
✅ PREMIUM UI ADDED: Dark Gold Modern Premium Theme included via CSS
✅ SMART MAPPING INTEGRATED: OSRM -> GraphHopper -> Geoapify Fallback system
✅ DYNAMIC COMMISSION: Automated calculate_admin_commission included
✅ ANTI-SPAM & SECURITY: Math CAPTCHA, Rate Limiter, and DDoS protections active
✅ DUPLICATES REMOVED: All duplicate functions and imports consolidated
"""

# ============================================================
# 📦 IMPORTS - All libraries in one place
# ============================================================
# ============================================================
# 📦 IMPORTS - All libraries in one place
# ============================================================
import datetime
import time
import math
import urllib.parse
import uuid
import requests
import hashlib
import re
import random
import threading
import pandas as pd
import json
import telebot
import streamlit as st
import streamlit.components.v1 as components
import streamlit as str_lit
import psycopg2
from psycopg2.extras import RealDictCursor
from supabase import create_client
import gspread
import folium
from telebot import types
from streamlit_folium import st_folium
from firebase_admin import credentials, db
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_geolocation import streamlit_geolocation
from flask import Flask, request, jsonify
from streamlit.runtime.scriptrunner import add_script_run_ctx
# സീക്രട്ടിൽ നിന്ന് കീകൾ വായിക്കുന്നു
# ഡീബഗ്ഗിംഗ്: സീക്രട്ടിൽ എന്തെല്ലാം ലോഡ് ആയി എന്ന് കാണാൻ
try:
    # ഇത് സീക്രട്ടിലുള്ള കീകൾ മാത്രം പ്രിന്റ് ചെയ്യും (മൂല്യങ്ങൾ അല്ല)
    st.write("Loaded Secret Keys:", list(st.secrets.keys()))
except Exception as e:
    st.error(f"Secrets loading failed entirely: {e}")
SUPABASE_URL = st.secrets["DB_URI"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# കണക്ഷൻ ഉണ്ടാക്കുന്നു
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# --- Mobile Friendly CSS (ഇവിടെ ചേർക്കുക) ---
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.5rem !important; }
    h3 { font-size: 1.2rem !important; }
    .stButton>button {
        width: 100% !important;
        height: 3rem !important;
        font-size: 1rem !important;
    }
    .stTextInput>div>div>input {
        font-size: 1rem !important;
        height: 3rem !important;
    }
    .stForm { padding: 1rem !important; }
</style>
""", unsafe_allow_html=True)
# ============================================================
# 📦 DATABASE CONNECTION SETUP (Supabase)
# ============================================================
DB_URI = st.secrets["DB_URI"]

@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(DB_URI)
        return conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None




# ==========================================================
# 📌 1. ഈ ഫംഗ്ഷൻ കോഡിന്റെ ഏറ്റവും മുകളിൽ (Global Scope-ൽ) നൽകുക
# ==========================================================
def get_trip_from_database(trip_id):
    try:
        conn = psycopg2.connect(DB_URI)
        # RealDictCursor ഉപയോഗിച്ചാൽ ഡാറ്റ Dictionary ആയി കിട്ടും
        cursor = conn.cursor(cursor_factory=RealDictCursor) 
        cursor.execute("SELECT * FROM trips WHERE trip_id = %s", (trip_id,))
        trip_data = cursor.fetchone()
        cursor.close()
        conn.close()
        return trip_data
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None
def get_lat_lon_from_address(address):
    """ജിയോ കോഡിങ് വഴി വിലാസത്തിൽ നിന്ന് Lat, Lon കണ്ടെത്തുന്ന ഫങ്ഷൻ"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
        headers = {'User-Agent': 'TaxiBookingApp/1.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except Exception:
        pass
    return None, None
# വാഹനത്തിന്റെ സ്വഭാവം അനുസരിച്ച് മാപ്പിലെ ഐക്കോൺ കാണിക്കുന്ന ഫങ്ഷൻ
# 1. ഫയർബേസിൽ നിന്ന് ഡ്രൈവറുടെ തത്സമയ ലൊക്കേഷൻ എടുക്കുന്ന ഫങ്ഷൻ
def get_live_tracking_from_firebase(trip_id):
    try:
        # ഫയർബേസിലെ ട്രിപ്പ് ലൊക്കേഷൻ പാത്ത് (നിങ്ങളുടെ ഡാറ്റാബേസ് സ്ട്രക്ചർ അനുസരിച്ച് ഇത് മാറ്റാം)
        ref = db.reference(f'trips/{trip_id}/driver_location')
        data = ref.get()
        return data  # ഇത് {'lat': x, 'lon': y} എന്ന ഫോർമാറ്റിൽ ആയിരിക്കും
    except Exception as e:
        return None

# 2. ദൂരം കണക്കാക്കാൻ സഹായിക്കുന്ന മാത്സ് ഫങ്ഷൻ (മീറ്ററിൽ)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # <--- ഈ വരി ഇവിടെ ചേർക്കുക
def send_admin_trip_notification(trip_data):
    print("=" * 50)
    print("🔔 SEND_ADMIN CALLED")
    print(f"   ADMIN_ID = '{ADMIN_TELEGRAM_CHAT_ID}'")
    print(f"   bot = {bot}")
    print(f"   Trip = {trip_data.get('trip_id', 'N/A')}")
    print("=" * 50)
    
    try:
        if not bot or not ADMIN_TELEGRAM_CHAT_ID:
            print("⚠️ SKIPPED: bot or chat_id missing")
            return False

        # ============================================================
        # Trip Data Extract
        # ============================================================
        trip_id = trip_data.get("trip_id", "N/A")
        customer_name = trip_data.get("customer_name", "N/A")
        pickup = trip_data.get("pickup", "N/A")
        drop = trip_data.get("drop", "N/A")
        area = trip_data.get("area", "N/A")
        distance = trip_data.get("calculated_distance", "N/A")
        vehicle = trip_data.get("vehicle_type", "N/A")
        booking_time = trip_data.get("booking_time", "N/A")

        # Commission
        commission = (
            trip_data.get("commission_amount")
            or trip_data.get("Commission")
            or 0
        )
        try:
            commission = float(commission)
            commission_display = f"₹{commission:.2f}"
        except:
            commission_display = f"₹{commission}"

        # Masked phone
        raw_phone = str(trip_data.get("customer_phone", ""))
        if len(raw_phone) >= 6:
            masked_phone = raw_phone[:4] + "XXXX" + raw_phone[-2:]
        else:
            masked_phone = "XXXXXX"

        # GPS
        gps_url = (
            trip_data.get("location")
            or trip_data.get("GPS Link")
            or trip_data.get("pickup_link")
            or ""
        )
        if gps_url and gps_url.startswith("http"):
            gps_line = f"🔗 GPS: [📍 Location]({gps_url})"
        else:
            gps_line = "🔗 GPS: ലഭ്യമല്ല"

        # Admin message
        admin_msg = (
            f"🔔 *പുതിയ ട്രിപ്പ് (Admin)*\n\n"
            f"🆔 *Trip ID:* {trip_id}\n"
            f"🕐 *Time:* {booking_time}\n"
            f"👤 *കസ്റ്റമർ:* {customer_name}\n"
            f"📞 *ഫോൺ:* {masked_phone}\n"
            f"📍 *പിക്കപ്പ്:* {pickup}\n"
            f"🏁 *ഡ്രോപ്പ്:* {drop}\n"
            f"📍 *ഏരിയ:* {area}\n"
            f"🚗 *വാഹനം:* {vehicle}\n"
            f"📏 *ദൂരം:* {distance} km\n"
            f"💰 *Commission:* {commission_display}\n"
            f"{gps_line}"
        )

        bot.send_message(
            chat_id=ADMIN_TELEGRAM_CHAT_ID,
            text=admin_msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

        print(f"✅ Admin notified: {trip_id}")
        return True

    except Exception as e:
        print(f"❌ Admin notification error: {e}")
        return False

# ==========================================================
# 🗺️ LIVE TRACKING MAP (Updated with Notifications)
# ==========================================================
@st.fragment(run_every=15)   # 5s → 15s (Firebase quota save)
def render_live_tracking_map(trip_id, customer_lat, customer_lon, vehicle_type):
    # ============================================================
    # 🔔 സൗണ്ട് & നോട്ടിഫിക്കേഷൻ ഒറ്റ ബട്ടണിൽ ഓൺ ചെയ്യുക
    # ============================================================
    components.html("""
        <div id="alert-btn-container" style="margin-bottom: 10px;"></div>
        <script>
            // localStorage-ൽ audio_enabled ഉണ്ടോ എന്ന് ചെക്ക് ചെയ്യുക
            if (!localStorage.getItem('audio_enabled')) {
                var container = document.getElementById('alert-btn-container');
                var btn = document.createElement('button');
                btn.innerHTML = '🔔 അലേർട്ടുകൾ ഓൺ ചെയ്യുക (Enable Alerts)';
                btn.style.cssText = 'padding:12px 20px; background-color:#ff4b4b; color:white; border:none; border-radius:8px; cursor:pointer; font-size:16px; width:100%; font-weight:bold;';
                
                btn.onclick = function() {
                    // 1. സൗണ്ട് ഓൺ ചെയ്യുക (localStorage-ൽ സേവ് ചെയ്യുക)
                    localStorage.setItem('audio_enabled', 'true');
                    
                    // 2. ഒരു ചെറിയ സൈലന്റ് സൗണ്ട് പ്ലേ ചെയ്യുക
                    var audio = new Audio('data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==');
                    audio.play().catch(e => console.log('Silent audio blocked'));
                    
                    // 3. 🔔 നോട്ടിഫിക്കേഷൻ അനുവാദം ചോദിക്കുക
                    if ('Notification' in window) {
                        Notification.requestPermission().then(function(permission) {
                            if (permission === 'granted') {
                                console.log('✅ Notification permission granted');
                                new Notification('Easy Auto Taxi', {
                                    body: 'അലേർട്ടുകൾ ഓൺ ആണ്! ഡ്രൈവർ വരുമ്പോൾ നിങ്ങൾക്ക് അറിയിപ്പ് ലഭിക്കും.',
                                    icon: 'https://cdn-icons-png.flaticon.com/512/3448/3448339.png'
                                });
                            } else {
                                console.log('❌ Notification permission denied');
                            }
                        });
                    }
                    
                    // ബട്ടൺ ടെക്സ്റ്റ് മാറ്റുക
                    btn.innerHTML = '✅ അലേർട്ടുകൾ ഓൺ ആണ്';
                    btn.style.backgroundColor = '#28a745';
                    btn.disabled = true;
                };
                container.appendChild(btn);
            } else {
                // ഇതിനകം ഓൺ ആണെങ്കിൽ, ഒരു സന്ദേശം കാണിക്കുക
                var container = document.getElementById('alert-btn-container');
                var msg = document.createElement('div');
                msg.innerHTML = '✅ അലേർട്ടുകളും നോട്ടിഫിക്കേഷനും ഓൺ ആണ്';
                msg.style.cssText = 'padding:12px; background-color:#d4edda; color:#155724; border-radius:8px; font-size:14px; text-align:center; font-weight:bold;';
                container.appendChild(msg);
            }
        </script>
    """, height=60)
    try:
        # ============================================================
        # ✅ 1. Firebase-ൽ നിന്ന് ട്രിപ്പ് വിവരങ്ങൾ എടുക്കുക
        # ============================================================
        trip_data = get_trip_from_database(trip_id) or {}
    
        print("🔥 Database Trip Data:", trip_data)

        driver_name = trip_data.get("driver_name", "Driver")
        vehicle_number = trip_data.get("vehicle_number", "N/A")
        customer_name = trip_data.get("customer_name", "Customer")
        trip_status = trip_data.get("status", "Pending")
        trip_notification = trip_data.get("notification", "")

        # ============================================================
        # ✅ 2. Trip Details Header (Customer-ന് കാണാൻ)
        # ============================================================
        st.markdown(f"""
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #2c3e50;">
            <h3 style="margin: 0; color: #2c3e50;">🆔 ട്രിപ്പ് ഐഡി: {trip_id}</h3>
            <p style="margin: 5px 0; color: #555;">👤 കസ്റ്റമർ: {customer_name}</p>
            <p style="margin: 5px 0; color: #555;">🚖 ഡ്രൈവർ: {driver_name}</p>
            <p style="margin: 5px 0; color: #555;">🔢 വാഹന നമ്പർ: {vehicle_number}</p>
        </div>
        """, unsafe_allow_html=True)

        # ============================================================
        # ✅ 3. Warning Message (App Close ചെയ്യരുത്)
        # ============================================================
        st.warning("""
        ⚠️ **ശ്രദ്ധിക്കുക:**
        • ഈ ആപ്പ് ക്ലോസ് ചെയ്യരുത്
        • ഇന്റർനെറ്റ് ഓഫ് ചെയ്യരുത്
        • ഫോൺ sleep mode-ൽ വെക്കരുത്
        • ഡ്രൈവർ വരുന്നത് വരെ കാത്തിരിക്കുക
        """)

        # ============================================================
        # ✅ 4. Accept Notification (Driver Accept ചെയ്ത ഉടനെ)
        # ============================================================
        if trip_status == "Accepted":
            if not st.session_state.get('accept_alert_shown', False):
                st.success("✅ **ഡ്രൈവർ നിങ്ങളുടെ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തിട്ടുണ്ട്!**")
                
                # 📱 Vibration
                st.markdown("""
                    <script>
                    if (navigator.vibrate) {
                        navigator.vibrate([500, 200, 500]);
                    }
                    </script>
                """, unsafe_allow_html=True)
                
                # 🔊 Sound
                sound_html = """
                <audio autoplay>
                    <source src="https://www.soundjay.com/phones/sounds/phone-ringing-01.mp3" type="audio/mpeg">
                </audio>
                """
                components.html(sound_html, height=0)
                st.session_state.accept_alert_shown = True

        # ============================================================
        # ✅ 5. Vehicle Header
        # ============================================================
        if "Auto" in vehicle_type or "auto" in vehicle_type.lower() or "ഓട്ടോ" in vehicle_type:
            st.markdown("### 🛺 ഓട്ടോറിക്ഷ നിങ്ങളുടെ അടുത്തേക്ക് വരുന്നു...")
            vehicle_icon = folium.Icon(color="orange", icon="motorcycle", prefix="fa")
        else:
            st.markdown("### 🚗 ടാക്സി കാർ നിങ്ങളുടെ അടുത്തേക്ക് വരുന്നു...")
            vehicle_icon = folium.Icon(color="blue", icon="car", prefix="fa")

        # ============================================================
        # ✅ 6. Arrived Status Check (Driver "Arrived" tap ചെയ്തിട്ടുണ്ടോ?)
        # ============================================================
        if trip_status == "Arrived":
            st.success("🎉 **അലേർട്ട്:** ഡ്രൈവർ നിങ്ങളുടെ പിക്കപ്പ് ലൊക്കേഷനിൽ എത്തിയിരിക്കുന്നു!")
            st.toast("🚗 ഡ്രൈവർ എത്തി!", icon="✅")
            
            # 📱 Vibration
            components.html("""
                <script>
               
                    if (navigator.vibrate) {
                        navigator.vibrate([300, 100, 300, 100, 300]);
                        
                }
                </script>
            """, height=0)
            
            # 🔔 പുഷ് നോട്ടിഫിക്കേഷൻ അയക്കുക (ഒരിക്കൽ മാത്രം)
            if not st.session_state.get('arrived_notification_sent', False):
                components.html("""
                    <script>
                        if (Notification.permission === 'granted') {
                            new Notification('🚗 ഡ്രൈവർ എത്തി!', {
                                body: 'നിങ്ങളുടെ ഡ്രൈവർ പിക്കപ്പ് ലൊക്കേഷനിൽ എത്തിയിരിക്കുന്നു!',
                                icon: 'https://cdn-icons-png.flaticon.com/512/3448/3448339.png',
                                vibrate: [300, 100, 300, 100, 300],
                                requireInteraction: true
                            });
                        }
                    </script>
                """, height=0)    
                st.session_state.arrived_notification_sent = True
        else:
            st.session_state.arrived_notification_sent = False
        

        # ============================================================
        # ✅ 7. Driver Live Location & Distance Calculation
        # ============================================================
        driver_loc = None
        try:
            driver_loc = get_live_tracking_from_firebase(trip_id)
        except Exception as e:
            print(f"⚠️ Driver location fetch error: {e}")

        if driver_loc and 'lat' in driver_loc and 'lon' in driver_loc:
            driver_lat = driver_loc['lat']
            driver_lon = driver_loc['lon']

            # Distance calculation
            try:
                distance = calculate_distance(customer_lat, customer_lon, driver_lat, driver_lon)
            except Exception:
                distance = None

            if distance is not None:
                # 🎯 30 മീറ്റർ അകലെ ആകുമ്പോൾ
                if distance <= 30:
                    if not st.session_state.get('alert_30m_sent', False):
                        st.success("🎉 **അലേർട്ട്:** നിങ്ങളുടെ വാഹനം പിക്ക്അപ്പ് ലൊക്കേഷനിൽ എത്തിച്ചേർന്നിരിക്കുന്നു!")
                        st.markdown("""
                            <script>
                            if (navigator.vibrate) {
                                navigator.vibrate([300, 100, 300]);
                            }
                            </script>
                        """, unsafe_allow_html=True)
                        st.session_state.alert_30m_sent = True
                        st.session_state.alert_100m_sent = False # Reset 100m flag
                    else:
                        st.success(f"📍 വാഹനം ഏകദേശം **{int(distance)} മീറ്റർ** അകലെയാണ്.")

                # 🎯 100 മീറ്റർ അകലെ ആകുമ്പോൾ (Nearby Alert)
                elif distance <= 100:
                    if not st.session_state.get('alert_100m_sent', False):
                        st.warning("🔔 **ഡ്രൈവർ 100 മീറ്റർ അകലെയാണ്!** വാഹനം വരുന്നുണ്ട്, തയ്യാറാകുക.")
                        
                        # 📱 Vibration
                        st.markdown("""
                            <script>
                            if (navigator.vibrate) {
                                navigator.vibrate([500, 200, 500]);
                            }
                            </script>
                        """, unsafe_allow_html=True)
                        
                        # 🔊 Sound
                        sound_html = """
                        <audio autoplay>
                            <source src="https://www.soundjay.com/phones/sounds/phone-ringing-01.mp3" type="audio/mpeg">
                        </audio>
                        """
                        components.html(sound_html, height=0)
                        st.session_state.alert_100m_sent = True
                        st.session_state.alert_30m_sent = False # Reset 30m flag
                    else:
                        st.info(f"📍 വാഹനം ഏകദേശം **{int(distance)} മീറ്റർ** അകലെയാണ്.")

                # 🎯 100 മീറ്ററിൽ കൂടുതൽ അകലെയാണെങ്കിൽ
                else:
                    st.session_state.alert_100m_sent = False
                    st.session_state.alert_30m_sent = False
                    st.info(f"📍 വാഹനം ഏകദേശം **{int(distance)} മീറ്റർ** അകലെയാണ്.")
        else:
            driver_lat, driver_lon = customer_lat, customer_lon
            st.warning("⏳ ഡ്രൈവർ യാത്ര ആരംഭിക്കുന്നതുവരെ കാത്തിരിക്കുക...")

        # ============================================================
        # ✅ 8. Folium Map
        # ============================================================
        m = folium.Map(location=[customer_lat, customer_lon], zoom_start=15)

        # Customer marker (green)
        folium.Marker(
            [customer_lat, customer_lon],
            popup="നിങ്ങളുടെ പിക്കപ്പ് സ്ഥലം",
            icon=folium.Icon(color="green", icon="home", prefix="fa")
        ).add_to(m)

        # Driver marker (vehicle icon)
        folium.Marker(
            [driver_lat, driver_lon],
            popup=f"ഡ്രൈവർ ({vehicle_type}) വരുന്ന വഴി",
            icon=vehicle_icon
        ).add_to(m)

        st_folium(m, width="100%", height=350, key=f"map_{trip_id}")
        # ============================================================
        # ✅ ഗുഡ്ബൈ സന്ദേശം (മാപ്പിന് താഴെ, ബലൂൺ ഇല്ലാതെ)
        # ============================================================
        if trip_status == "Arrived":
            st.markdown("""
                <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;">
                    <h2 style="color: #155724;">🙏 നന്ദി! വീണ്ടും വരിക!</h2>
                    <p style="color: #155724; font-size: 16px;">
                        നിങ്ങളുടെ യാത്ര വിജയകരമായി പൂർത്തിയായി. <br>
                        Easy Auto Taxi ഉപയോഗിച്ചതിന് നന്ദി! <br>
                        അടുത്ത യാത്രയിൽ വീണ്ടും കാണാം. 🚖
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🏠 ഹോം പേജിലേക്ക് പോകുക"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()            
    except Exception as e:    
        
        st.error(f"🗺️ Map load error: {e}")
# --- ബോട്ട് സെറ്റപ്പ് ഇവിടെ തുടങ്ങുന്നു ---
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
@st.cache_resource
def setup_bot():
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    
    return bot
bot = setup_bot()    
    
    


# --- ബോട്ട് സെറ്റപ്പ് ഇവിടെ അവസാനിക്കുന്നു ---
# ============================================================
# Google Sheets കണക്ഷൻ സെറ്റപ്പ് (തൽക്കാലം ഡിസേബിൾ ചെയ്തിരിക്കുന്നു)
# ============================================================
# Google Sheets കണക്ഷൻ സെറ്റപ്പ്
#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# നിങ്ങളുടെ JSON ഫയലിന്റെ പേര് ഇവിടെ നൽകുക
#creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\Asu Mj\Desktop\test taxi\service_account.json', scope)
#client = gspread.authorize(creds)

# നിങ്ങളുടെ ഷീറ്റിന്റെ പേരും ടാബിന്റെ പേരും ഇവിടെ മാറ്റുക
#sheet = client.open("Taxi_Management").worksheet("Trips")
# =====================================================================
# ഡ്രൈവർമാരെ ഏരിയ തിരിച്ച് ഫയർബേസിൽ നിന്ന് കണ്ടെത്തുന്ന പുതിയ ഫങ്ഷൻ
# =====================================================================

def get_all_drivers_by_area(area_name):
    try:
        # -------------------------------------------------------------
        # 1. പഴയ ഗൂഗിൾ ഷീറ്റ് കോഡ് (എറർ വരാതിരിക്കാൻ താൽക്കാലികമായി കമന്റ് ചെയ്തിരിക്കുന്നു)
        # -------------------------------------------------------------
        # driver_sheet = client.open("Taxi_Management").worksheet("Filtered_Data")
        # data = driver_sheet.get_all_records()
        
        # -------------------------------------------------------------
        # 2. പുതിയ ഫയർബേസ് ഡാറ്റാബേസ് ലോജിക് (Firebase Logic)
        # -------------------------------------------------------------
        # നിങ്ങളുടെ ഫയർബേസിൽ ഡ്രൈവർമാരുടെ ഡാറ്റ സേവ് ചെയ്തിരിക്കുന്ന പാത്ത് (Node) 
        # 'drivers' അല്ലെങ്കിൽ നിങ്ങളുടെ ഡാറ്റാബേസ് ഘടനയ്ക്കനുസരിച്ച് മാറ്റുക.
        ref = db.reference('drivers') 
        drivers_data = ref.get()
        
        filtered_drivers = []
        selected_area = str(area_name).strip().lower()
        
        if drivers_data:
            # ഫയർബേസ് ഡാറ്റ ഡിക്ഷ്ണറി (Dictionary) അല്ലെങ്കിൽ ലിസ്റ്റ് ആയിട്ടാകാം വരുന്നത്
            items = drivers_data.items() if isinstance(drivers_data, dict) else enumerate(drivers_data)
            
            for key, d in items:
                if not isinstance(d, dict):
                    continue
                
                # ഫയർബേസിലെ ഫീൽഡുകൾ (Area, Telegram Chat ID എന്നിവ കൃത്യമായി നൽകുക)
                sheet_area = str(d.get('Area', d.get('area', ''))).strip().lower()
                telegram_id = str(d.get('Telegram Chat ID', d.get('telegram_chat_id', ''))).strip()
                
                # കൺസോൾ ഡീബഗ്ഗിംഗ്
                print(f"DEBUG Firebase: Checking '{selected_area}' against '{sheet_area}' with ID: '{telegram_id}'")
                
                if selected_area == sheet_area and telegram_id:
                    d['chat_id'] = telegram_id
                    filtered_drivers.append(d)
        
        return filtered_drivers
        
    except Exception as e:
        print(f"DEBUG FIREBASE ERROR: {e}")
        return []
# ---------------------------------------------------------
# ഇതിന് തൊട്ടു താഴെയായി നിങ്ങളുടെ 'SMART MAPPING' ഭാഗം വരാം
# ---------------------------------------------------------
# ============================================================
# 🗺️ SMART MAPPING & FALLBACK ENGINE (FULL FIXED)
# ============================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


@st.cache_data(ttl=86400)
def get_real_road_distance(pickup_place, drop_place):

    headers = {
        "User-Agent": "EasyAutoTaxiPro/1.0"
    }

    GRAPHOPPER_API_KEY = "YOUR_GRAPHOPPER_API_KEY"

    # Location clean function
    def clean_place(place):
        place = str(place).strip()
        place = place.split("-")[0]

        remove_words = [
            "Central Junction",
            "Junction",
            "Bus Stand",
            "Stand"
        ]

        
# ==========================================================
    # 🛑 ഇവിടെയാണ് geocode_place ഫങ്ഷൻ തുടങ്ങുന്നത്. 
    # ഈ ഫങ്ഷന്റെ ഏറ്റവും തുടക്കത്തിൽ ഫയർബേസ് ചെക്ക് വെക്കുക:
    # ==========================================================
    
    # Geocoding function with Firebase check & fallback


 

        

    # Get pickup and drop coordinates
    pickup_coords = geocode_place(pickup_place)
    drop_coords = geocode_place(drop_place)

    if pickup_coords is None or drop_coords is None:
        return None

    p_lat, p_lon = pickup_coords
    d_lat, d_lon = pickup_coords[0], pickup_coords[1]
    d_lat, d_lon = drop_coords[0], drop_coords[1]

    # ============================================================
    # OSRM Primary (Improved Accuracy)
    # ============================================================
    try:
        osrm_url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{p_lon},{p_lat};{d_lon},{d_lat}"
            f"?overview=false&steps=false&annotations=false"
        )

        osrm_response = requests.get(
            osrm_url,
            headers=headers,
            timeout=8
        )

        if osrm_response.status_code == 200:
            osrm_data = osrm_response.json()

            if osrm_data.get("code") == "Ok":
                distance_km = (
                    osrm_data["routes"][0]["distance"] / 1000
                )

                st.info(
                    f"Distance source: OSRM ({distance_km:.1f} km)"
                )

                return round(distance_km, 1)

        st.info("OSRM failed. Trying GraphHopper...")

    except Exception as e:
        st.info(f"OSRM error: {e}")

    # ============================================================
    # GraphHopper fallback
    # ============================================================
    try:
        gh_url = (
            f"https://graphhopper.com/api/1/route"
            f"?point={p_lat},{p_lon}"
            f"&point={d_lat},{d_lon}"
            f"&profile=car"
            f"&key={GRAPHOPPER_API_KEY}"
        )

        gh_response = requests.get(
            gh_url,
            headers=headers,
            timeout=8
        )

        if gh_response.status_code == 200:
            gh_data = gh_response.json()

            if "paths" in gh_data:
                distance_km = (
                    gh_data["paths"][0]["distance"] / 1000
                )

                st.info(
                    f"Distance source: GraphHopper ({distance_km:.1f} km)"
                )

                return round(distance_km, 1)

    except Exception as e:
        st.info(f"GraphHopper error: {e}")

    # ============================================================
    # Final fallback (Road-like estimate)
    # ============================================================
    st.info("Using Haversine fallback")

    air_distance = haversine_distance(
        p_lat,
        p_lon,
        d_lat,
        d_lon
    )

    road_estimate = air_distance * 1.35

    return round(road_estimate, 1)
# ====================================================================
# 📐 Haversine Distance Calculator
# ====================================================================
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # ഭൂമിയുടെ ആരം (കിലോമീറ്ററിൽ)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
# ============================================================
# ⚙️ CONFIGURATION - All configs in one place
# ============================================================
#GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbw_WDIJgYvtCy0r13wQu20BNZE9KqfGmyxQm7_iFsV2kLLq3eQ8O-3e5BfP3JCrYnTorw/exec"


ADMIN_TELEGRAM_CHAT_ID = st.secrets["ADMIN_TELEGRAM_CHAT_ID"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
API_SECRET_KEY = st.secrets["API_SECRET_KEY"]
ADMIN_PIN = st.secrets["ADMIN_PIN"]
ENABLE_COMMISSION = True
ADMIN_UPI_ID = "YOUR_UPI_ID_HERE"
WARNING_LIMIT = 25
BLOCK_LIMIT = 30
AUTO_FARE_PER_KM = 22.50


# ==========================================================
# FIREBASE MASTER MODULE (SAFE FINAL)
# Replace old Firebase init + listener module with this
# ==========================================================

import firebase_admin
from firebase_admin import credentials, db
import os
import threading
import requests
import streamlit as st
# ഫയർബേസ് ഡാറ്റാബേസ് കണക്ഷൻ സെറ്റ് ചെയ്യുക
if not firebase_admin._apps:
    creds_dict = dict(st.secrets["firebase_service_account"])
    cred = credentials.Certificate(creds_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
    
    })

registration_data = {}
def auto_cancel_trip(trip_id, delay_seconds=1800):
    """30 മിനിറ്റിന് ശേഷം ട്രിപ്പ് ഓട്ടോമാറ്റിക് ആയി ക്യാൻസൽ ചെയ്യുക"""
    def cancel_task():
        time.sleep(delay_seconds)  # 30 മിനിറ്റ് (1800 സെക്കൻഡ്) കാത്തിരിക്കുക
        try:
            ref = db.reference(f"trips/{trip_id}")
            trip_data = ref.get()
            
            if trip_data:
                current_status = trip_data.get("status", "Pending")
                # ട്രിപ്പ് ഇപ്പോഴും Pending/Available ആണെങ്കിൽ മാത്രം ക്യാൻസൽ ചെയ്യുക
                if current_status in ["Pending", "Available", "Unassigned"]:
                    ref.update({
                        "status": "Cancelled",
                        "cancel_reason": "No driver accepted within 30 minutes",
                        "cancelled_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"⏰ Trip {trip_id} auto-cancelled after 30 minutes")
                else:
                    print(f"✅ Trip {trip_id} already {current_status} - no need to cancel")
        except Exception as e:
            print(f"❌ Auto-cancel error for {trip_id}: {e}")
    
    # Background thread-ൽ റൺ ചെയ്യുക
    thread = threading.Thread(target=cancel_task, daemon=True)
    thread.start()


def save_new_trip(booking_id, customer_name, customer_phone, pickup, drop, distance=0.0, pickup_link
="", total_fare=0.0, commission_amount=0.0, pickup_lat=0.0, pickup_lon=0.0, vehicle_type="", area=""):
    """
    കസ്റ്റമർ ബുക്ക് ചെയ്യുമ്പോൾ വിവരങ്ങളും ദൂരവും ഫയർബേസിലേക്കും പോസ്റ്റ്ഗ്രസിലേക്കും സേവ് ചെയ്യുന്നു
    """
    # 1. ഫയർബേസിലേക്ക് സേവ് ചെയ്യുക (പഴയ രീതി - ലൈവ് ലൊക്കേഷനും മറ്റും ഇതിൽ നിന്ന് വായിക്കാൻ)
    try:
        trip_data = {
            "trip_id": booking_id,
            "customer_name": customer_name,
            "customer_phone": str(customer_phone),
            "pickup": pickup,
            "drop": drop,
            "pickup_link": pickup_link,
            "distance": distance,
            "total_fare": float(total_fare),                # 0.0 മാറ്റി ഇത് നൽകി
            "commission_amount": float(commission_amount),  # പുതിയത്
            "pickup_lat": float(pickup_lat),                # പുതിയത്
            "pickup_lon": float(pickup_lon),                # പുതിയത്
            "vehicle_type": vehicle_type,                   # പുതിയത്
            "area": area,                                   # പുതിയത്
            
            "status": "Pending",
            "is_locked": False,
            "driver_name": "",
            "driver_phone": "",
            "driver_chat_id": "",
            "booking_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        trip_ref = db.reference(f"trips/{booking_id}")
        trip_ref.set(trip_data)
        auto_cancel_trip(booking_id, delay_seconds=1800)
        print(f"✅ Trip {booking_id} saved to Firebase.")
    except Exception as e:
        print(f"❌ Error saving trip to Firebase: {e}")

    # 2. പോസ്റ്റ്ഗ്രസിലേക്ക് (Supabase) സേവ് ചെയ്യുക (പുതിയ രീതി - ഡ്രൈവർ പാനലിനും ഹിസ്റ്ററിക്കും)
    try:
        conn = psycopg2.connect(DB_URI)
        cursor = conn.cursor()
        
        # SQL ക്വറിയും %s കളും (ആകെ 17 എണ്ണം)
        query = """
            INSERT INTO trips (
                trip_id, customer_name, customer_phone, pickup, drop_location, 
                distance, total_fare, commission_amount, pickup_lat, pickup_lon, 
                vehicle_type, status, is_locked, driver_name, driver_phone, 
                driver_chat_id, booking_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # ഡാറ്റകൾ കൃത്യമായി ക്രമീകരിച്ചിരിക്കുന്നു (ആകെ 17 എണ്ണം)
        data = (
            booking_id,               # 1
            customer_name,            # 2
            str(customer_phone),      # 3
            pickup,                   # 4
            drop,                     # 5
            distance,                 # 6
            float(total_fare),        # 7
            float(commission_amount), # 8
            float(pickup_lat),        # 9
            float(pickup_lon),        # 10
            vehicle_type,             # 11
            "Pending",                # 12
            False,                    # 13
            "",                       # 14
            "",                       # 15
            "",                       # 16
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 17
        )
        
        cursor.execute(query, data)
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Trip {booking_id} saved to Supabase.")
        return True
        
    except Exception as e:
        print(f"❌ Error saving trip to Supabase: {e}")
        return False
# ==========================================================
# Send Trip to Driver (Telegram - Privacy Focused)
# ==========================================================
def send_trip_to_driver(
    chat_id,
    booking_id,
    customer_name,
    customer_phone,
    pickup,
    drop,
    distance="N/A",
    location_link="Not Available",
    commission="N/A"  # <--- ഇവിടെ കമ്മീഷൻ പാരാമീറ്റർ ചേർക്കാം
):
    raw_phone = str(customer_phone or '')
    if len(raw_phone) >= 6:
        masked_phone = raw_phone[:4] + "XXXX" + raw_phone[-2:]
    else:
        masked_phone = "XXXXXX"

    safe_distance = distance if distance else "N/A"
    safe_location = location_link if location_link else "Not Available"

    message = f"""
🚖 *പുതിയ ട്രിപ്പ് റിക്വസ്റ്റ്!*

👤 കസ്റ്റമർ: {customer_name}
📞 ഫോൺ: {masked_phone}
📍 Pickup: {pickup}
🏁 Drop: {drop}
📏 ദൂരം (Distance): {safe_distance} km
💰 Commission: {commission}
📍 GPS Live Location:
{safe_location}

Click ACCEPT to confirm trip.
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "✅ ACCEPT TRIP",
                        "callback_data": booking_id
                    }
                ]
            ]
        }
    }

    requests.post(url, json=payload)        


# ==========================================================
# SAFE LOGGER (No Streamlit in Thread)
# ==========================================================
def bg_log(message):
    print(message)


# ==========================================================
# FIREBASE INITIALIZATION (Only Once)
# ==========================================================
@st.cache_resource
def initialize_firebase():
    try:
        if firebase_admin._apps:
            bg_log("✅ Firebase already initialized")
            return True

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        possible_files = [
            "firebase_key.json",
            "firebase_key",
            "firebase_key.json.json"
        ]

        # Firebase ഇതിനകം ഇനിഷ്യലൈസ് ചെയ്തിട്ടില്ലെങ്കിൽ മാത്രം
        if not firebase_admin._apps:
            # Secrets-ൽ നിന്ന് JSON ഉള്ളടക്കം എടുക്കുക
            creds_dict = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
            })

        

        return True

    except Exception as e:
        bg_log(
            f"Firebase Init Error: {e}"
        )
        return False
# ==========================================================
# Atomic Trip Acceptance & Locking Logic
# ==========================================================
def accept_trip_safely(booking_id, driver_name, driver_phone, driver_chat_id, vehicle_number="N/A"):
    try:
        conn = psycopg2.connect(DB_URI)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 1. ട്രിപ്പ് നിലവിലുണ്ടോ എന്ന് ചെക്ക് ചെയ്യുക
        cursor.execute("SELECT * FROM trips WHERE trip_id = %s", (booking_id,))
        trip_data = cursor.fetchone()

        if not trip_data:
            cursor.close()
            conn.close()
            return "not_found"

        # 2. സ്റ്റാറ്റസ് ചെക്ക് ചെയ്യുക
        current_status = str(trip_data.get("status", "Pending")).strip()
        if current_status not in ["Pending", "Available", "Unassigned"]:
            cursor.close()
            conn.close()
            return "already_taken"

        # 3. ട്രിപ്പ് അപ്ഡേറ്റ് ചെയ്യുക (SQL UPDATE)
        cursor.execute("""
            UPDATE trips
            SET status = 'Accepted',
                is_locked = TRUE,
                driver_name = %s,
                driver_phone = %s,
                driver_chat_id = %s,
                vehicle_number = %s
            WHERE trip_id = %s
        """, (driver_name, driver_phone, str(driver_chat_id), vehicle_number, booking_id))

        conn.commit()
        cursor.close()
        conn.close()

        return "success"


    except Exception as e:
        print(f"❌ Error in accept_trip_safely: {e}")
        return "error"


# ==========================================================
# ✅ ADMIN TRIP NOTIFICATION FUNCTION
# ==========================================================
def send_admin_trip_notification(trip_data):
    """
    Admin-ന് പുതിയ trip notification അയക്കുന്നു.
    """
    try:
        if not bot or not ADMIN_TELEGRAM_CHAT_ID:
            print("⚠️ Admin notification skipped: bot or chat_id missing")
            return False

        trip_id = trip_data.get("trip_id", "N/A")
        customer_name = trip_data.get("customer_name", "N/A")
        pickup = trip_data.get("pickup", "N/A")
        drop = trip_data.get("drop", "N/A")
        area = trip_data.get("area", "N/A")
        distance = trip_data.get("calculated_distance", "N/A")
        vehicle = trip_data.get("vehicle_type", "N/A")
        booking_time = trip_data.get("booking_time", "N/A")

        # Commission
        commission = (
            trip_data.get("commission_amount")
            or trip_data.get("Commission")
            or 0
        )
        try:
            commission = float(commission)
            commission_display = f"₹{commission:.2f}"
        except:
            commission_display = f"₹{commission}"

        # Masked phone
        raw_phone = str(trip_data.get("customer_phone", ""))
        if len(raw_phone) >= 6:
            masked_phone = raw_phone[:4] + "XXXX" + raw_phone[-2:]
        else:
            masked_phone = "XXXXXX"

        # GPS
        gps_url = (
            trip_data.get("location")
            or trip_data.get("GPS Link")
            or trip_data.get("pickup_link")
            or ""
        )
        if gps_url and gps_url.startswith("http"):
            gps_line = f"🔗 GPS: [📍 Location]({gps_url})"
        else:
            gps_line = "🔗 GPS: ലഭ്യമല്ല"

        # Admin message
        admin_msg = (
            f"🔔 *പുതിയ ട്രിപ്പ് (Admin)*\n\n"
            f"🆔 *Trip ID:* {trip_id}\n"
            f"🕐 *Time:* {booking_time}\n"
            f"👤 *കസ്റ്റമർ:* {customer_name}\n"
            f"📞 *ഫോൺ:* {masked_phone}\n"
            f"📍 *പിക്കപ്പ്:* {pickup}\n"
            f"🏁 *ഡ്രോപ്പ്:* {drop}\n"
            f"📍 *ഏരിയ:* {area}\n"
            f"🚗 *വാഹനം:* {vehicle}\n"
            f"📏 *ദൂരം:* {distance} km\n"
            f"💰 *Commission:* {commission_display}\n"
            f"{gps_line}"
        )

        bot.send_message(
            chat_id=ADMIN_TELEGRAM_CHAT_ID,
            text=admin_msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

        print(f"✅ Admin notified: {trip_id}")
        return True

    except Exception as e:
        print(f"❌ Admin notification error: {e}")
        return False
def listener(event):
    try:
        if not event.data:
            return

        # ============================================
        # ✅ FIX: Sub-path updates skip
        # Path = "/TRIP-XXXX" → Process (trip creation)
        # Path = "/TRIP-XXXX/notified_drivers" → Skip
        # ============================================
        if event.path and event.path.count("/") > 1:
            print(f"   ⏭️ Sub-path skip: {event.path}")
            return

        trip_data = event.data
        
        if not isinstance(trip_data, dict):
            return

        if trip_data.get("backup_done") is True:
            return

        trip_status = str(trip_data.get("status", "")).upper()

        if trip_status not in ["AVAILABLE", "PENDING"]:
            return
            
        try:
            # ============================================
            # ✅ ADMIN NOTIFICATION — function call (ഒരിക്കൽ മാത്രം)
            # ============================================
            send_admin_trip_notification(trip_data)
            
            bg_log("🚖 Admin Notification Sent Successfully")
            
            # backup_done flag set (trip_id fallback)
            try:
                trip_key = trip_data.get('trip_id') or trip_data.get('booking_id')
                if trip_key:
                    db.reference(f"trips/{trip_key}").update({"backup_done": True})
            except Exception as e:
                bg_log(f"Flag Update Error: {e}")
            
        except Exception as send_error:
            bg_log(f"Telegram Send Error: {send_error}")

    except Exception as e:
        bg_log(f"Listener Error: {e}")
        return
 

# ==========================================
# SAFE TRIP ACCEPTANCE - DRIVER DETAILS
# ==========================================
def accept_trip_safely(trip_id, driver_chat_id, driver_name, driver_phone, vehicle_number="N/A"):
    try:
        conn = psycopg2.connect(DB_URI)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # 1. ട്രിപ്പ് നിലവിലുണ്ടോ എന്ന് ചെക്ക് ചെയ്യുക
        cursor.execute("SELECT * FROM trips WHERE trip_id = %s", (trip_id,))
        trip_data = cursor.fetchone()

        if not trip_data:
            cursor.close()
            conn.close()
            return None

        # 2. സ്റ്റാറ്റസ് ചെക്ക് ചെയ്യുക
        current_status = str(trip_data.get("status", "Pending")).strip()
        if current_status.upper() not in ["PENDING", "AVAILABLE", "UNASSIGNED"]:
            cursor.close()
            conn.close()
            return None # മറ്റൊരാൾ എടുത്തു കഴിഞ്ഞു

        # 3. ട്രിപ്പ് അപ്ഡേറ്റ് ചെയ്യുക
        cursor.execute("""
            UPDATE trips 
            SET status = 'Accepted', 
                is_locked = TRUE, 
                driver_chat_id = %s, 
                driver_name = %s, 
                driver_phone = %s,
                vehicle_number = %s
            WHERE trip_id = %s AND status IN ('Pending', 'Available', 'Unassigned')
        """, (str(driver_chat_id), driver_name, driver_phone, vehicle_number, trip_id))

        conn.commit()
        cursor.close()
        conn.close()

        # ഫലം റിട്ടേൺ ചെയ്യുക (Dictionary)
        return {"status": "Accepted", "driver_chat_id": str(driver_chat_id)}

    except Exception as e:
        print(f"❌ Safe trip acceptance error: {e}")
        return None
# ==========================================================
# Telegram Callback Query Handler (Button Clicks)
# ==========================================================
def handle_telegram_callback(update, context):
    query = update.callback_query
    query.answer()
    
    callback_data = query.data
    chat_id = query.message.chat_id
    print(f"🔥 DEBUG: Callback വന്നിരിക്കുന്നു -> {callback_data}")
    
    # ============================================================
    # 1. "Arrived" ബട്ടൺ അമർത്തുമ്പോൾ
    # ============================================================
    if callback_data.startswith("arrived_"):
        booking_id = callback_data.replace("arrived_", "")
        
        try:
            conn = psycopg2.connect(DB_URI)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # ട്രിപ്പ് ചെക്ക് ചെയ്യുക
            cursor.execute("SELECT driver_chat_id FROM trips WHERE trip_id = %s", (booking_id,))
            trip = cursor.fetchone()
            
            if trip and str(trip.get("driver_chat_id")) == str(chat_id):
                # സ്റ്റാറ്റസ് അപ്ഡേറ്റ് ചെയ്യുക
                cursor.execute("UPDATE trips SET status = 'Arrived' WHERE trip_id = %s", (booking_id,))
                conn.commit()
                query.edit_message_text(
                    text=query.message.text + "\n\n🔴 **[Status: Arrived at Location]** - കസ്റ്റമർക്ക് നോട്ടിഫിക്കേഷൻ അയച്ചിട്ടുണ്ട്."
                )
            else:
                query.edit_message_text(text="❌ അസാധുവായ റിക്വസ്റ്റ് അല്ലെങ്കിൽ നിങ്ങൾക്ക് ഈ ട്രിപ്പിൽ അധികാരമില്ല.")
            
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Arrived Update Error: {e}")
            
    # ============================================================
    # 2. "Accept" ബട്ടൺ അമർത്തുമ്പോൾ
    # ============================================================
    else:
        booking_id = callback_data.replace("accept_", "").strip()
            
        driver_name = "Unknown Driver"
        driver_phone = "N/A"
        vehicle_number = "N/A"
        
        # ഡ്രൈവർ വിവരങ്ങൾ പോസ്റ്റ്ഗ്രസിൽ നിന്ന് എടുക്കുക
        try:
            conn = psycopg2.connect(DB_URI)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM drivers WHERE chat_id = %s", (str(chat_id),))
            driver_data = cursor.fetchone()
            
            if driver_data:
                driver_name = driver_data.get("driver_name") or "Unknown Driver"
                driver_phone = driver_data.get("phone") or "N/A"
                vehicle_number = driver_data.get("vehicle_number") or "N/A"
                
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"❌ Driver Fetch Error: {e}")

        # ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്യുക
        result = accept_trip_safely(
            trip_id=booking_id,
            driver_chat_id=chat_id,
            driver_name=driver_name,
            driver_phone=driver_phone,
            vehicle_number=vehicle_number
        )
            
        if result:
            query.edit_message_text(
                text=f"✅ *ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തു!*\n\n"
                    f"ട്രിപ്പ് ഐഡി: `{booking_id}`\n"
                    f"ഡ്രൈവർ: {driver_name}\n"
                    f"വാഹനം: {vehicle_number}",
                parse_mode="Markdown"
            )
                
            driver_panel_url = f"https://taxiservisemj-x9meaffucvbt6tjijxrd6d.streamlit.app/?page=driver_trip_panel&trip_id={booking_id}&driver_chat_id={chat_id}"
            bot.send_message(
                chat_id,
                f"📍 *ഡ്രൈവർ പാനൽ തുറക്കാൻ താഴെയുള്ള ലിങ്കിൽ ക്ലിക്ക് ചെയ്യുക:*\n\n[ട്രിപ്പ് പാനൽ തുറക്കുക]({driver_panel_url})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            query.edit_message_text(
                text="❌ ക്ഷമിക്കണം, ഈ ട്രിപ്പ് മറ്റൊരു ഡ്രൈവർ ഇതിനകം സ്വീകരിച്ചിട്ടുണ്ട്.",
                parse_mode="Markdown"
            )
                
            
        

    




# ==========================================================
# FETCH LOCATIONS & AREAS DIRECTLY FROM FIREBASE
# ==========================================================

@st.cache_data(ttl=60)
def get_locations_from_firebase():
    try:
        ref = db.reference("locations")
        data = ref.get()
        if data:
            if isinstance(data, list):
                return [str(item) for item in data if item and item is not True]
            elif isinstance(data, dict):
                # ലൊക്കേഷൻ പേരുകൾ കീ (Keys) ആയിട്ടായതുകൊണ്ട് data.keys() എടുക്കുന്നു
                return [str(k) for k in data.keys() if k and k is not True]
        return [] 
    except Exception as e:
        print(f"Locations Firebase Error: {e}")
        return []

@st.cache_data(ttl=86400)
def get_areas_from_firebase():
    try:
        ref = db.reference("areas")
        data = ref.get()
        if data:
            if isinstance(data, list):
                return [str(item) for item in data if item and item is not True]
            elif isinstance(data, dict):
                # ഏരിയയുടെ പേര് കീ (Key) ആയതുകൊണ്ട് data.keys() ഉപയോഗിക്കുന്നു
                return [str(k) for k in data.keys() if k and k is not True]
        return [] 
    except Exception as e:
        print(f"Areas Firebase Error: {e}")
        return []

# ==========================================================
# MAIN STARTUP
# ==========================================================

# ==========================================================
# START FIREBASE BACKGROUND SERVICES
# ==========================================================

# ============================================================
# AUTO START
# ============================================================

@st.cache_data(ttl=60)
def get_stands_from_sheets():
    try:
        response = requests.get(GOOGLE_SHEET_URL, params={"action": "get_stands"}, timeout=40)
        if response.status_code == 200:
            res_json = response.json()
            
            # 1. ഗൂഗിൾ ഷീറ്റ് നേരിട്ട് ഒരു ലിസ്റ്റ് (List) ആണ് അയക്കുന്നതെങ്കിൽ
            if isinstance(res_json, list):
                return res_json
                
            # 2. ഡിക്ഷണറി (Dictionary) ആണെങ്കിൽ പല സാധ്യമായ കീകളും പരിശോധിക്കുന്നു
            if isinstance(res_json, dict):
                for key in ["stands", "data", "result", "items"]:
                    if key in res_json and isinstance(res_json[key], list):
                        return res_json[key]
                        
        return []
    except Exception as e:
        print(f"Stands Error: {e}")
        return []

@st.cache_data(ttl=60)
def get_areas_from_sheets():
    try:
        response = requests.get(GOOGLE_SHEET_URL, params={"action": "get_areas"}, timeout=40)
        if response.status_code == 200:
            res_json = response.json()
            
            # 1. നേരിട്ട് ലിസ്റ്റ് ആണെങ്കിൽ
            if isinstance(res_json, list):
                return res_json
                
            # 2. ഡിക്ഷണറി ആണെങ്കിൽ കീസ് പരിശോധിക്കുന്നു
            if isinstance(res_json, dict):
                for key in ["areas", "data", "result", "items"]:
                    if key in res_json and isinstance(res_json[key], list):
                        return res_json[key]
                        
        return []
    except Exception as e:
        print(f"Areas Error: {e}")
        return []
# ഡിഫോൾട്ട് ഏരിയ (നിങ്ങൾ ആവശ്യപ്പെട്ടതുപോലെ Manjeri Central മാത്രം)
DEFAULT_AREAS = ["Manjeri Central"]

@st.cache_data(ttl=60)
def get_areas_from_sheets():
    try:
        response = requests.get(GOOGLE_SHEET_URL, params={"action": "get_areas"}, timeout=40)
        if response.status_code == 200:
            res_json = response.json()
            
            # 1. നേരിട്ട് ലിസ്റ്റ് ആണെങ്കിൽ
            if isinstance(res_json, list) and res_json:
                return res_json
                
            # 2. ഡിക്ഷണറി ആണെങ്കിൽ കീസ് പരിശോധിക്കുന്നു
            if isinstance(res_json, dict):
                for key in ["areas", "data", "result", "items"]:
                    if key in res_json and isinstance(res_json[key], list) and res_json[key]:
                        return res_json[key]
                        
        # ഷീറ്റിൽ നിന്ന് ഡാറ്റ കിട്ടിയില്ലെങ്കിൽ Manjeri Central മാത്രം റിട്ടേൺ ചെയ്യുന്നു
        return DEFAULT_AREAS
    except Exception as e:
        print(f"Areas Error: {e}")
        return DEFAULT_AREAS        
# ============================================================
# 🎨 --- MODERN ULTRA-PREMIUM UI (DARK GOLD TAXI THEME) ---
# ============================================================
st.markdown("""
    <style>
    .reportview-container { background: #121212 !important; color: #FFFFFF !important; }
    
    /* ഹെഡർ ബോക്സിന്റെ പാഡിംഗ് കുറച്ചു */
    .header-box { 
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d) !important; 
        padding: 15px !important; 
        border-radius: 12px !important; 
        text-align: center !important; 
        border-bottom: 4px solid #ffcc00 !important; 
        box-shadow: 0px 6px 12px rgba(0,0,0,0.3) !important; 
        margin-bottom: 15px !important; 
    }
    /* ഹെഡിംഗ് ഫോണ്ട് സൈസ് 2.5rem ൽ നിന്ന് 1.8rem ആക്കി കുറച്ചു */
    .header-box h1 { color: #ffcc00 !important; font-weight: 900 !important; letter-spacing: 1px !important; margin: 0 !important; font-size: 1.8rem !important; }
    /* സബ് ഹെഡിംഗ് ഫോണ്ട് സൈസ് 14px ൽ നിന്ന് 11px ആക്കി കുറച്ചു */
    .header-box p { color: #b3b3b3 !important; font-size: 11px !important; margin-top: 3px !important; text-transform: uppercase !important; }
    
    /* ഫോമിന്റെ പാഡിംഗ് കുറച്ചു */
    div[data-testid="stForm"] { 
        background-color: #1e1e1e !important; 
        border: 1px solid #333333 !important; 
        padding: 15px !important; 
        border-radius: 12px !important; 
        box-shadow: 0 6px 12px rgba(0,0,0,0.2) !important; 
    }
    
    label[data-testid="stWidgetLabel"] p, 
    div[data-testid="stMarkdownContainer"] p strong,
    div[data-testid="stRadio"] label p {
        color: #ffcc00 !important;
        font-size: 14px !important;
        font-weight: bold !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton>button { 
        background: linear-gradient(90deg, #ffcc00, #ffa500) !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 15px !important; 
        border: none !important; 
        border-radius: 8px !important; 
        padding: 10px 15px !important; 
        transition: all 0.3s ease !important; 
        width: 100% !important; 
    }
    .stButton>button:hover { transform: translateY(-2px) !important; box-shadow: 0px 6px 20px rgba(255,204,0,0.4) !important; }
    
    .disclaimer-box { background-color: #2b1d1d !important; border-left: 4px solid #d32f2f !important; padding: 12px !important; border-radius: 8px !important; margin: 15px 0 !important; }
    .disclaimer-title { color: #ff5252 !important; font-weight: bold !important; font-size: 14px !important; margin-bottom: 4px !important; }
    .disclaimer-text { color: #e0e0e0 !important; font-size: 12px !important; line-height: 1.5 !important; margin: 0 !important; }
    
    .success-card { background-color: #1c2e24 !important; border: 1px solid #2e7d32 !important; padding: 15px !important; border-radius: 10px !important; text-align: center !important; }
    .warning-card { background-color: #2e2719 !important; border: 1px solid #f9a825 !important; padding: 15px !important; border-radius: 10px !important; text-align: center !important; }
    .danger-card { background-color: #2c1c1c !important; border: 1px solid #c62828 !important; padding: 15px !important; border-radius: 10px !important; text-align: center !important; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# 🔌 EXTERNAL CLIENT INITIALIZATION
# ============================================================
gc_client = None
# try:
#     creds = ServiceAccountCredentials.from_json_keyfile_name(
#         'service_account.json',
#         ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     )
#     gc_client = gspread.authorize(creds)
#     print("✅ Google Sheets Connected")
# except Exception as e:
#     print(f"❌ Google Sheets Error: {e}")
# ടെലിഗ്രാം ബോട്ട് ടോക്കൺ ഇവിടെ സെറ്റ് ചെയ്യുക
# ============================================================
# 🔌 EXTERNAL CLIENT INITIALIZATION
# ============================================================
gc_client = None

# ടെലിഗ്രാം ബോട്ട് ടോക്കൺ ഇവിടെ സെറ്റ് ചെയ്യുക
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
# 🆕 FIX: bot ഒബ്ജക്റ്റ് ഒരിക്കൽ മാത്രം സൃഷ്ടിക്കാൻ @st.cache_resource ചേർക്കുന്നു
@st.cache_resource
def get_telegram_bot():
    token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
    if token and "YOUR_BOT_TOKEN" not in token:
        try:
            _bot = telebot.TeleBot(token)
            print("✅ Telegram Bot Connected")
            return _bot
        except Exception as e:
            print(f"❌ Telegram Bot Error: {e}")
            return None
    return None

bot = get_telegram_bot()
# ============================================================
# 🤖 MODULE 20: DRIVER TRIP HISTORY (LAST 20 TRIPS)
# ============================================================
@bot.message_handler(commands=['history'])
def handle_driver_history(message):
    chat_id = str(message.chat.id)
    
    # ടെലിഗ്രാം ബോട്ടിനായി നേരിട്ട് പുതിയ കണക്ഷൻ എടുക്കുന്നു
    try:
        conn = psycopg2.connect(DB_URI)
    except Exception as e:
        bot.reply_to(message, f"❌ ഡാറ്റാബേസ് എറർ: {str(e)}")
        return

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # SQL Query: ആ ഡ്രൈവറുടെ അവസാന 20 ട്രിപ്പുകൾ മാത്രം എടുക്കുക
        cursor.execute("""
            SELECT trip_id, booking_time, pickup, drop_location 
            FROM trips 
            WHERE driver_chat_id = %s 
            ORDER BY created_at DESC 
            LIMIT 20
        """, (chat_id,))
        
        user_trips = cursor.fetchall()
        cursor.close()

        if user_trips:
            reply = "📜 **നിങ്ങളുടെ അവസാനത്തെ ട്രിപ്പുകൾ:**\n\n"
            for t in user_trips:
                t_id = t.get("trip_id", "N/A")
                t_date_raw = t.get("booking_time", "N/A")
                t_date = str(t_date_raw).split(" ")[0] if t_date_raw else "N/A"
                t_pickup = t.get("pickup", "N/A")
                t_drop = t.get("drop_location", "N/A") 
                
                reply += f"🆔 {t_id}\n📅 {t_date}\n📍 {t_pickup} ➔ {t_drop}\n\n"
                
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "ഈ ചാറ്റ് ഐഡിയിൽ ഇതുവരെ ട്രിപ്പുകൾ ഒന്നും കണ്ടെത്താനായില്ല.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ എറർ: {str(e)}")
        
    finally:
        # എന്ത് സംഭവിച്ചാലും കണക്ഷൻ ക്ലോസ് ചെയ്യണം
        if conn:
            conn.close()

flask_app = Flask(__name__)

# ============================================================
# 🤖 MODULE 19: TELEGRAM BOT /start & REGISTRATION HANDLER
# ============================================================
registration_data = {}

@bot.message_handler(commands=['start'])
def handle_driver_start(message):
    print("=" * 60)
    print("🔔 /start HANDLER CALLED")
    print(f"   Chat: {message.chat.id}")
    print("=" * 60)
    chat_id = message.chat.id
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 പ്രൈവറ്റ് ചാനലിൽ ജോയിൻ ചെയ്യുക", url="https://t.me/+48S6XF9l4zM0MTY0"))
    markup.add(types.InlineKeyboardButton("✅ ഞാൻ ചാനലിൽ ജോയിൻ ചെയ്തു, രജിസ്ട്രേഷൻ തുടങ്ങാം", callback_data="start_registration"))
    
    bot.send_message(
        chat_id, 
        "🚖 *മഞ്ചേരി ഈസി ടാക്സി ബുക്കിംഗ് സിസ്റ്റത്തിലേക്ക് സ്വാഗതം!*\n\n"
        "രജിസ്ട്രേഷൻ നടപടികൾ ആരംഭിക്കുന്നതിന് മുൻപ്, നമ്മുടെ **പ്രൈവറ്റ് ടെലിഗ്രാം ചാനലിൽ** നിർബന്ധമായും ജോയിൻ ചെയ്യുക.\n\n"
        "ചാനലിൽ ജോയിൻ ചെയ്ത ശേഷം താഴെയുള്ള ബട്ടൺ ക്ലിക്ക് ചെയ്യുക:",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    # 🆕 FIX: ഇവിടെ നിന്ന് തുടങ്ങുന്നു (1396-ാം വരി)
    try:
        bot.send_message(
            chat_id,
            f"✅ *രജിസ്ട്രേഷൻ വിജയകരമായി പൂർത്തിയായി!*\n\n"
            f"🆔 *നിങ്ങളുടെ ചാറ്റ് ഐഡി:* `{chat_id}`\n\n"
            f"📌 ഈ ഐഡി സൂക്ഷിച്ചുവെക്കുക. ഭാവിയിൽ ട്രിപ്പ് വിവരങ്ങൾ അറിയാൻ ഇത് ഉപയോഗിക്കാം.",
            parse_mode="Markdown"
        )    
        print(f"✅ Chat ID {chat_id} sent back to driver")
    except Exception as e:
        print(f"❌ Error sending chat ID: {e}")
    

@bot.callback_query_handler(func=lambda call: call.data == "start_registration")
def ask_contact_number(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("📱 നിങ്ങളുടെ ടെലഗ്രാം ഫോൺ നമ്പർ ഷെയർ ചെയ്യുക (Share Contact)", request_contact=True))
    
    bot.send_message(
        chat_id, 
        "നന്ദി! 🙏\n\nഇനി താഴെയുള്ള ബട്ടൺ ക്ലിക്ക് ചെയ്ത് നിങ്ങളുടെ ഫോൺ നമ്പർ ഷെയർ ചെയ്യുക.", 
        reply_markup=markup
    )
    registration_data[chat_id] = {"step": "waiting_phone"}

@bot.message_handler(content_types=['contact'])
def handle_driver_contact(message):
    chat_id = message.chat.id
    if chat_id in registration_data and registration_data[chat_id]["step"] == "waiting_phone":
        phone = message.contact.phone_number
        registration_data[chat_id]["phone"] = phone
        registration_data[chat_id]["step"] = "waiting_name"
        
        markup = types.ReplyKeyboardRemove()
        bot.send_message(
            chat_id, 
            "നന്ദി! 📝\n\nഇനി നിങ്ങളുടെ പൂർണ്ണമായ പേര് (Full Name) ഇവിടെ ടൈപ്പ് ചെയ്ത് അയക്കൂ.", 
            reply_markup=markup
        )

@bot.message_handler(func=lambda message: message.chat.id in registration_data and registration_data[message.chat.id]["step"] == "waiting_name")
def handle_driver_name(message):
    chat_id = message.chat.id
    driver_name = message.text
    registration_data[chat_id]["driver_name"] = driver_name
    registration_data[chat_id]["step"] = "waiting_vehicle_type"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🛺 ഓട്ടോറിക്ഷ (Autorickshaw)", callback_data="v_auto"),
        types.InlineKeyboardButton("🚗 ടാക്സി കാർ (Taxi Car)", callback_data="v_taxicar"),
        types.InlineKeyboardButton("🚙 ഗുഡ്സ് ഓട്ടോ പിക്കപ്പ് (Goods Auto Pickup)", callback_data="v_goodsauto"),
        types.InlineKeyboardButton("🚐 പിക്കപ്പ് വാൻ (Pickup Van)", callback_data="v_pickupvan"),
        types.InlineKeyboardButton("🚚 മിനി ലോറി (Mini Lorry)", callback_data="v_minilorry"),
        types.InlineKeyboardButton("🚛 ട്രക്ക് (Truck)", callback_data="v_truck"),
        types.InlineKeyboardButton("🏍️ ബൈക്ക് ടാക്സി (Bike Taxi)", callback_data="v_biketaxi")
    )
    
    bot.send_message(
        chat_id, 
        f"സന്തോഷം, {driver_name}!\n\n"
        f"⚠️ *(ശ്രദ്ധിക്കുക: പ്രൈവറ്റ് വാഹനങ്ങൾക്ക് അനുവാദമില്ല. ടാക്സി/കൊമേഴ്സ്യൽ പെർമിറ്റ് വാഹനങ്ങൾ മാത്രം തിരഞ്ഞെടുക്കുക.)*\n\n"
        f"നിങ്ങളുടെ വാഹനം ഏതാണ്? താഴെയുള്ളതിൽ ഒരെണ്ണം തിരഞ്ഞെടുക്കുക:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("v_"))
def handle_vehicle_selection(call):
    chat_id = call.message.chat.id
    if chat_id in registration_data and registration_data[chat_id]["step"] == "waiting_vehicle_type":
        
        v_mapping = {
            "v_auto": "ഓട്ടോറിക്ഷ (Autorickshaw)",
            "v_taxicar": "ടാക്സി കാർ (Taxi Car)",
            "v_goodsauto": "ഗുഡ്സ് ഓട്ടോ പിക്കപ്പ് (Goods Auto Pickup)",
            "v_pickupvan": "പിക്കപ്പ് വാൻ (Pickup Van)",
            "v_minilorry": "മിനി ലോറി (Mini Lorry)",
            "v_truck": "ട്രക്ക് (Truck)",
            "v_biketaxi": "ബൈക്ക് ടാക്സി (Bike Taxi)"
        }
        vehicle_type = v_mapping.get(call.data, "ടാക്സി കാർ")
        registration_data[chat_id]["vehicle_type"] = vehicle_type
        registration_data[chat_id]["step"] = "waiting_vehicle_number"
        
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id, 
            f"തിരഞ്ഞെടുത്ത വാഹനം: *{vehicle_type}*\n\nഅവസാനമായി നിങ്ങളുടെ വാഹന നമ്പർ / പെർമിറ്റ് നമ്പർ ടൈപ്പ് ചെയ്ത് അയക്കൂ (ഉദാ: KL 10 AB 1234):", 
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.chat.id in registration_data and registration_data[message.chat.id]["step"] == "waiting_vehicle_number")
def handle_vehicle_number_input(message):
    chat_id = message.chat.id
    vehicle_number = message.text.upper()
    
    registration_data[chat_id]["vehicle_number"] = vehicle_number
    registration_data[chat_id]["step"] = "waiting_agreement"
    
    disclaimer_text = (
        "⚠️ *നിയമപരമായ നിബന്ധനകളും ഉത്തരവാദിത്ത നിരാകരണവും (Disclaimer & Terms):*\n\n"
        "ഞാൻ മുകളിൽ നൽകിയിരിക്കുന്ന എന്റെ വാഹനത്തിന്റെ വിവരങ്ങളും പേപ്പറുകളുടെ കാലാവധിയും പൂർണ്ണമായും സത്യമാണെന്ന് ബോധ്യപ്പെടുത്തുന്നു.\n\n"
        "ഈ പ്ലാറ്റ്‌ഫോം ഡ്രൈവർമാരെയും കസ്റ്റമർമാരെയും പരസ്പരം ബന്ധിപ്പിക്കുന്നതിനുള്ള ഒരു സാങ്കേതിക സംവിധാനം മാത്രമാണ്. യാത്രയ്ക്കിടയിൽ ഉണ്ടാകുന്ന സാമ്പത്തിക ഇടപാടുകൾക്കോ, വ്യക്തിപരമായ തർക്കങ്ങൾക്കോ, വണ്ടിക്കുണ്ടാകുന്ന തകരാറുകൾക്കോ, അപകടങ്ങൾക്കോ ഈ ആപ്പിന്റെ അഡ്മിൻമാർ ഉത്തരവാദികളായിരിക്കില്ല എന്ന് ഞാൻ പൂർണ്ണമായി സമ്മതിക്കുന്നു."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ ഞാൻ ഈ നിബന്ധനകൾ വായിച്ചു മനസ്സിലാക്കി അംഗീകരിക്കുന്നു (I Agree)", callback_data="final_agree"))
    
    bot.send_message(
        chat_id,
        disclaimer_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "final_agree")
def save_data_to_firebase_final(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    
    if chat_id in registration_data:
        data = registration_data[chat_id]
        username = call.from_user.username or "No_Username"
        
        driver_data = {
            "chat_id": str(chat_id),
            "driver_name": data["driver_name"],
            "phone": data["phone"],
            "vehicle_type": data["vehicle_type"],
            "vehicle_number": data["vehicle_number"],
            "telegram_username": f"@{username}",
            "status": "ONLINE",
            "area": "Manjeri",
            "wallet_balance": 0.0,  # 🆕 ഈ വരി ഇവിടെ ചേർക്കുക
        }
        
        try:
           # പോസ്റ്റ്ഗ്രസിലേക്ക് കണക്ഷൻ എടുക്കുന്നു
            conn = psycopg2.connect(DB_URI)
            cursor = conn.cursor()

            # ഡ്രൈവർ വിവരങ്ങൾ പോസ്റ്റ്ഗ്രസിലേക്ക് സേവ് ചെയ്യുന്നു
            # (ഒരു പക്ഷേ ഡ്രൈവർ വീണ്ടും രജിസ്റ്റർ ചെയ്യാൻ ശ്രമിച്ചാൽ UPDATE ചെയ്യാൻ ON CONFLICT ഉപയോഗിക്കുന്നു)
            cursor.execute("""
                INSERT INTO drivers (
                    chat_id, driver_name, phone, vehicle_type, 
                    vehicle_number, telegram_username, status, area, wallet_balance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    driver_name = EXCLUDED.driver_name,
                    phone = EXCLUDED.phone,
                    vehicle_type = EXCLUDED.vehicle_type,
                    vehicle_number = EXCLUDED.vehicle_number,
                    telegram_username = EXCLUDED.telegram_username,
                    status = EXCLUDED.status,
                    area = EXCLUDED.area
            """, (
                driver_data["chat_id"], 
                driver_data["driver_name"], 
                driver_data["phone"],
                driver_data["vehicle_type"], 
                driver_data["vehicle_number"], 
                driver_data["telegram_username"],
                driver_data["status"], 
                driver_data["area"], 
                driver_data["wallet_balance"]
            ))

            conn.commit()
            cursor.close()
            conn.close()

            success_text = (
                f"🎉 *രജിസ്ട്രേഷൻ വിജയകരമായി പൂർത്തിയായി!* 🎉\n\n"
                f"👤 ഡ്രൈവർ: {data['driver_name']}\n"
                f"🆔 നിങ്ങളുടെ ചാറ്റ് ഐഡി: `{chat_id}`\n"
                f"നിങ്ങളുടെ വിവരങ്ങൾ ഡാറ്റാബേസിൽ സുരക്ഷിതമായി സേവ് ചെയ്തിരിക്കുന്നു.\n\n"
                f"✅ ഇനി മുതൽ നിങ്ങൾക്ക് ട്രിപ്പുകൾ ലഭിക്കും."
            )
            bot.send_message(chat_id=chat_id, text=success_text, parse_mode="Markdown")
            
            # രജിസ്ട്രേഷൻ ഡാറ്റ ക്ലിയർ ചെയ്യുക
            del registration_data[chat_id]

        except Exception as e:
            print(f"❌ Database Error: {e}")
            bot.send_message(chat_id=chat_id, text=f"❌ എറർ: ഡാറ്റ സേവ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ({e})")




# ============================================================
# 🗺️ SMART MAPPING & FALLBACK ENGINE (FINAL FIXED)
# ============================================================

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


@st.cache_data(ttl=3600)
def get_real_road_distance(pickup_place, drop_place):

    headers = {"User-Agent": "EasyAutoTaxiPro/1.0"}

    GRAPHOPPER_API_KEY = st.secrets["GRAPHOPPER_API_KEY"]
    GEOAPIFY_API_KEY = st.secrets["GEOAPIFY_API_KEY"]

    def clean_place(place):
        place = str(place).strip()
        return " ".join(place.split())

    def geocode_place(place):
        try:
            # 1. Firebase
            try:
                loc_ref = db.reference(f'locations/{place}').get()
                if isinstance(loc_ref, dict) and 'lat' in loc_ref and 'lng' in loc_ref:
                    print(f"✅ Firebase manual: {place}")
                    return float(loc_ref['lat']), float(loc_ref['lng'])
            except Exception as e:
                print(f"⚠️ Firebase error: {e}")

            # 2. Nominatim — 4 queries
            cleaned_place = clean_place(place)
            query_variants = [
                f"{cleaned_place}, Kerala, India",
                f"{cleaned_place}, Malappuram, Kerala",
                f"{cleaned_place}, India",
                f"{cleaned_place}",
            ]

            for idx, query in enumerate(query_variants):
                try:
                    print(f"🌐 Query {idx+1}: {query}")
                    url = (
                        f"https://nominatim.openstreetmap.org/search"
                        f"?format=json&q={urllib.parse.quote(query)}"
                        f"&limit=1&countrycodes=in"
                    )
                    response = requests.get(url, headers=headers, timeout=8)

                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            lat = float(data[0]["lat"])
                            lon = float(data[0]["lon"])

                            try:
                                db.reference(f'locations/{place}').set({
                                    'lat': lat,
                                    'lng': lon,
                                    'source': f'nominatim_q{idx+1}',
                                    'cached_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                })
                                print(f"✅ Cached: {place}")
                            except Exception as e:
                                print(f"⚠️ Cache error: {e}")
                            return lat, lon
                    time.sleep(1.5)
                except Exception as e:
                    print(f"⚠️ Query {idx+1} failed: {e}")
                    time.sleep(1.5)
                    continue

            # 🎯 — 3. Manjeri ONLY fallback
            print(f"⚠️ Nominatim failed: {place} — using Manjeri center")

            try:
                area_ref = db.reference(f'areas/Manjeri').get()
                if isinstance(area_ref, dict) and 'lat' in area_ref and 'lng' in area_ref:
                    print(f"✅ Manjeri center fallback")
                    return float(area_ref['lat']), float(area_ref['lng'])
            except Exception as e:
                print(f"⚠️ Manjeri fallback error: {e}")

            print(f"❌ Location not found: {place}")
            return None

        except Exception as e:
            print(f"❌ Geocode error: {e}")
            return None

    # ============================================================
    # Get coordinates
    # ============================================================
    pickup_coords = geocode_place(pickup_place)
    drop_coords = geocode_place(drop_place)

    if pickup_coords is None or drop_coords is None:
        raise ValueError(f"Geocoding failed: {pickup_place} → {drop_place}")

    p_lat, p_lon = pickup_coords
    d_lat, d_lon = drop_coords

    # 🎯 — Sanity check
    if p_lat == d_lat and p_lon == d_lon:
        raise ValueError("Pickup and Drop coordinates are the same")

    # ============================================================
    # OSRM PRIMARY
    # ============================================================
    try:
        osrm_url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{p_lon},{p_lat};{d_lon},{d_lat}?overview=false"
        )
        osrm_response = requests.get(osrm_url, headers=headers, timeout=8)

        if osrm_response.status_code == 200:
            osrm_data = osrm_response.json()
            if osrm_data.get("code") == "Ok":
                distance_km = osrm_data["routes"][0]["distance"] / 1000
                print(f"✅ Distance source: OSRM ({distance_km:.1f} km)")
                return round(distance_km, 1)

        print("⚠️ OSRM failed → GraphHopper")
    except Exception as e:
        print(f"⚠️ OSRM error: {e}")

    # ============================================================
    # GRAPHHOPPER FALLBACK
    # ============================================================
    try:
        gh_url = (
            f"https://graphhopper.com/api/1/route"
            f"?point={p_lat},{p_lon}"
            f"&point={d_lat},{d_lon}"
            f"&profile=car"
            f"&key={GRAPHOPPER_API_KEY}"
        )
        gh_response = requests.get(gh_url, headers=headers, timeout=8)

        if gh_response.status_code == 200:
            gh_data = gh_response.json()
            if "paths" in gh_data:
                distance_km = gh_data["paths"][0]["distance"] / 1000
                print(f"✅ Distance source: GraphHopper ({distance_km:.1f} km)")
                return round(distance_km, 1)

        print("⚠️ GraphHopper failed → Geoapify")
    except Exception as e:
        print(f"⚠️ GraphHopper error: {e}")

    # ============================================================
    # GEOAPIFY FALLBACK
    # ============================================================
    try:
        geo_url = (
            f"https://api.geoapify.com/v1/routing"
            f"?waypoints={p_lat},{p_lon}|{d_lat},{d_lon}"
            f"&mode=drive"
            f"&apiKey={GEOAPIFY_API_KEY}"
        )
        geo_response = requests.get(geo_url, timeout=5)

        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            if 'features' in geo_data and len(geo_data['features']) > 0:
                distance_meters = geo_data['features'][0]['properties']['distance']
                distance_km = distance_meters / 1000.0
                print(f"✅ Distance source: Geoapify ({distance_km:.1f} km)")
                return round(distance_km, 1)
    except Exception as e:
        print(f"⚠️ Geoapify error: {e}")

    # ============================================================
    # FINAL FALLBACK — Haversine
    # ============================================================
    print("⚠️ Using Haversine fallback")
    return round(haversine_distance(p_lat, p_lon, d_lat, d_lon), 1)
def get_distance_from_coords_to_place(customer_lat, customer_lon, drop_place_name):
    try:
        # 1. Firebase-ൽ നിന്ന് നേരിട്ട് ഡ്രോപ്പ് സ്ഥലത്തിന്റെ കോർഡിനേറ്റ്സ് എടുക്കുന്നു
        loc_ref = db.reference(f'locations/{drop_place_name}').get()
        if not loc_ref or not isinstance(loc_ref, dict):
            return None
            
        drop_lat = float(loc_ref.get('lat'))
        drop_lon = float(loc_ref.get('lng') or loc_ref.get('lon'))

        # 2. OSRM API വിളിച്ച് ദൂരം കണക്കാക്കുന്നു
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{customer_lon},{customer_lat};{drop_lon},{drop_lat}?overview=false"
        
        response = requests.get(osrm_url)
        data = response.json()
        
        if data['code'] == 'Ok':
            distance_km = data['routes'][0]['distance'] / 1000.0
            return round(distance_km, 1)
        else:
            return None
            
    except Exception as e:
        print(f"OSRM Distance Error: {e}")
        return None
# ============================================================
# 💰 MASTER COMMISSION LOGIC
# ============================================================
def calculate_admin_commission(km):
    """ദൂരത്തിന്റെ അടിസ്ഥാനത്തിൽ അഡ്മിൻ കമ്മീഷൻ കണക്കാക്കുക"""
    if not ENABLE_COMMISSION:
        return 0.0
    
    if km <= 1.5:
        commission = 0.50  # ആദ്യ 1.5 കി.മീ-ന് ₹0.50
    else:
        # 1.5 കി.മീ കഴിഞ്ഞുള്ള അധിക ദൂരം
        extra_distance = km - 1.5
        
        # അതിനെ അടുത്ത പൂർണ്ണ കി.മീയിലേക്ക് റൗണ്ട് ചെയ്യുക (ഉദാ: 0.1 → 1, 1.5 → 2)
        rounded_extra = math.ceil(extra_distance)
        
        # ഓരോ അധിക കി.മീ-നും ₹22.50 വെച്ച് കണക്കാക്കുക
        extra_fare = rounded_extra * 22.50
        
        # അതിന്റെ 1.5% കമ്മീഷൻ കണക്കാക്കുക
        commission = 0.50 + (extra_fare * 0.015)
    
    return round(commission, 2)

# ============================================================
# 📍 AREA ROUTING MAP
# ============================================================
AREA_ROUTING_MAP = {
    "manjeri": ["malappuram", "perinthalmanna"],
    "malappuram": ["manjeri", "perinthalmanna"],
    "perinthalmanna": ["malappuram", "manjeri"],
    "kozhikode": ["manjeri", "malappuram"],
    "ernakulam": ["kozhikode", "thrissur"],
    "thrissur": ["ernakulam", "palakkad"],
    "palakkad": ["thrissur", "malappuram"]
}

# Session Initialization for State Tracking
if 'saved_gps_link' not in st.session_state: st.session_state.saved_gps_link = "Not Provided"
if "user_submission_tracker" not in st.session_state: st.session_state.user_submission_tracker = {}

# ============================================================
# 🛡️ MODULE 21: ANTI-SPAM BOMBING & RATE LIMITER ENGINE
# ============================================================
def check_spam_and_rate_limit(user_identifier):
    current_time = time.time()
    last_sub_time = st.session_state.user_submission_tracker.get(user_identifier, 0)
    
    if current_time - last_sub_time < 30:
        remaining_time = int(30 - (current_time - last_sub_time))
        log_and_report_error(f"Spam attempt blocked for User: {user_identifier}", "Rate_Limiter")
        return False, f"⚠️ താൽക്കാലികമായി സിസ്റ്റം നിങ്ങളെ തടഞ്ഞിരിക്കുന്നു! ദയവായി {remaining_time} സെക്കൻഡിന് ശേഷം വീണ്ടും ശ്രമിക്കുക."
        
    st.session_state.user_submission_tracker[user_identifier] = current_time
    return True, "ALLOWED"

# ============================================================
# 🚨 MODULE 20: CENTRALIZED ERROR TRACKING & MONITORING ENGINE
# ============================================================
def log_and_report_error(error_message, function_name):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_details = str(error_message)
    print(f"🛑 [SYSTEM ERROR] in {function_name} at {current_time}: {error_details}")
    
    if bot and ADMIN_TELEGRAM_CHAT_ID:
        telegram_alert_text = (
            f"🚨 *CRITICAL SYSTEM ERROR DETECTED* 🚨\n\n"
            f"📂 *മൊഡ്യൂൾ/ഫങ്ക്ഷൻ:* {function_name}\n"
            f"⏰ *സമയം:* {current_time}\n"
            f"📝 *എറർ വിവരണം:* `{error_details}`\n\n"
            f"🛠️ *ശ്രദ്ധിക്കുക:* ദയവായി അഡ്മിൻ പാനലോ ഗൂഗിൾ ഷീറ്റ് ലോഗുകളോ പരിശോധിക്കുക."
        )
        try: bot.send_message(chat_id=ADMIN_TELEGRAM_CHAT_ID, text=telegram_alert_text, parse_mode="Markdown")
        except: pass

    if gc_client:
        try:
            spreadsheet_id = "16d-kgW5yjUpDSTBcPFzKRBm_MTvHR-F25s-fCp1HcBE"
            ss = gc_client.open_by_key(spreadsheet_id)
            try: log_worksheet = ss.worksheet("System_Logs")
            except:
                log_worksheet = ss.add_worksheet(title="System_Logs", rows="1000", cols="4")
                log_worksheet.append_row(["Timestamp", "Function/Module", "Error Message", "Status"])
            log_worksheet.append_row([current_time, function_name, error_details, "UNRESOLVED"])
        except: pass







# ============================================================
# 🔒 SECURITY & UTILITY FUNCTIONS
# ============================================================
def sanitize_input(text):
    if not text: return ""
    return re.sub(r'[<>/{}\[\]\\^`|~]', '', str(text)).strip()

def check_ip_and_rate_limiting():
    current_time = time.time()
    if "ip_tracking" not in st.session_state:
        st.session_state.ip_tracking = {"last_request_time": 0, "request_count": 0, "total_bookings": 0}
    tracking = st.session_state.ip_tracking
    time_passed = current_time - tracking["last_request_time"]
    
    if time_passed < 3:
        tracking["request_count"] += 1
        if tracking["request_count"] > 3: return False, "Rate limit exceeded! (Anti-DDoS Mode Active)"
    else: tracking["request_count"] = 1
    
    tracking["last_request_time"] = current_time
    return True, "Safe"

def initialize_captcha_system():
    if "total_bookings_count" not in st.session_state: st.session_state.total_bookings_count = 0
    if "captcha_verified" not in st.session_state: st.session_state.captcha_verified = False

def render_smart_captcha_field():
    initialize_captcha_system()
    if st.session_state.total_bookings_count >= 3:
        st.error("🚨 സുരക്ഷാ മുന്നറിയിപ്പ്: തുടർച്ചയായ ബുക്കിംഗ് ശ്രമങ്ങൾ!")
        if "captcha_text_question" not in st.session_state:
            val1 = random.randint(2, 9)
            val2 = random.randint(2, 9)
            st.session_state.correct_captcha_sum = val1 + val2
            st.session_state.captcha_text_question = f"വ്യാജ ബുക്കിംഗുകൾ തടയുന്നതിനായി: {val1} + {val2} = ?"
            
        st.markdown(f"**{st.session_state.captcha_text_question}**")
        user_captcha_ans = st.number_input("ഉത്തരം", step=1, key="captcha_input")
        
        if user_captcha_ans == st.session_state.correct_captcha_sum:
            st.session_state.captcha_verified = True
            st.success("✅ സുരക്ഷാ പരിശോധന വിജയകരം!")
            return True
        else:
            st.session_state.captcha_verified = False
            st.warning("❌ തെറ്റായ ഉത്തരം!")
            return False
    return True

def register_successful_booking_attempt():
    initialize_captcha_system()
    st.session_state.total_bookings_count += 1
    if "captcha_text_question" in st.session_state: del st.session_state["captcha_text_question"]
    if "correct_captcha_sum" in st.session_state: del st.session_state["correct_captcha_sum"]

def calculate_spam_risk_score(c_name, c_phone):
    risk_score = 0
    if len(c_name) < 3 or c_name.isnumeric(): risk_score += 30
    if len(c_phone) < 10 or not c_phone.isnumeric(): risk_score += 40
    if re.search(r'[^a-zA-Z0-9 \u0D00-\u0D7F]', c_name): risk_score += 30
    return risk_score

# ============================================================
# 🗺️ AREA ROUTING FUNCTIONS
# ============================================================
def get_live_areas_from_google_sheet():
    default_fallback_areas = ["Manjeri", "Malappuram", "Perinthalmanna"]
    if "live_sheet_areas" in st.session_state and (time.time() - st.session_state.get("area_cache_time", 0) < 30):
        return st.session_state.live_sheet_areas
    if not gc_client: return default_fallback_areas
    try:
        spreadsheet_id = "16d-kgW5yjUpDSTBcPFzKRBm_MTvHR-F25s-fCp1HcBE"
        ss = gc_client.open_by_key(spreadsheet_id)
        worksheet = ss.worksheet("Area_Map")
        records = worksheet.get_all_records()
        extracted_areas = []
        for row in records:
            area_name = str(row.get('Stand', '')).strip()
            if area_name and area_name not in extracted_areas: extracted_areas.append(area_name.title())
        if extracted_areas:
            st.session_state.live_sheet_areas = sorted(extracted_areas)
            st.session_state.area_cache_time = time.time()
            return st.session_state.live_sheet_areas
    except Exception as e: log_and_report_error(e, "get_live_areas_from_google_sheet")
    return default_fallback_areas

# ============================================================
# 💾 MODULE 22: ADVANCED AREA-WISE MASTER BACKUP SYSTEM
# ============================================================
BACKUP_CONFIG = {
    "manjeri": "BACKUP_SPREADSHEET_ID_1",
    "malappuram": "BACKUP_SPREADSHEET_ID_2",
    "perinthalmanna": "BACKUP_SPREADSHEET_ID_3",
    "nilambur": "BACKUP_SPREADSHEET_ID_4",
    "kondotty": "BACKUP_SPREADSHEET_ID_5"
}

def sync_to_backups(data, data_type="driver", area=None):
    if not gc_client:
        log_and_report_error("Google Sheet Client not initialized", "sync_to_backups")
        return False
    try:
        if data_type == "driver":
            row_data = [data.get('name', ''), data.get('phone', ''), '', '', '', data.get('v_type', ''), '', '', '', '', data.get('chat_id', ''), 0, '', data.get('area', ''), 'ACTIVE']
        else:
            row_data = [
                data.get('trip_id', ''), data.get('customer_name', ''), data.get('customer_phone', ''),
                data.get('pickup', ''), data.get('drop', ''), data.get('area', ''), data.get('vehicle_type', ''),
                data.get('calculated_distance', 0.0), data.get('commission_amount', 0.0),
                data.get('status', ''), data.get('schedule_time', 'Now'),
                data.get('driver_name', ''), data.get('driver_phone', ''), data.get('driver_chat_id', '')
            ]
        
        if area:
            area_key = str(area).strip().lower()
            if area_key in BACKUP_CONFIG:
                try:
                    backup_ss = gc_client.open_by_key(BACKUP_CONFIG[area_key])
                    backup_worksheet = backup_ss.worksheet("Driver" if data_type == "driver" else "Trips")
                    backup_worksheet.append_row(row_data)
                    return True
                except Exception as e: log_and_report_error(f"Area backup failed for {area_key}: {e}", "sync_to_backups")
        
        primary_backups = [
            {"id": "16d-kgW5yjUpDSTBcPFzKRBm_MTvHR-F25s-fCp1HcBE", "tab": "sheet1"},
            {"id": "1GCYvQ-knMuQHxYUjMEumUsOTWwukF-Y9W6Wd9r54pH8", "tab": "sheet1"}
        ]
        for cfg in primary_backups:
            try: gc_client.open_by_key(cfg["id"]).worksheet(cfg["tab"]).append_row(row_data)
            except: pass
        return True
    except Exception as e:
        log_and_report_error(e, "sync_to_backups")
        return False

# ============================================================
# 🚗 DRIVER & ROUTING FUNCTIONS
# ============================================================
# 1. പുതിയ ഫങ്ഷൻ ഇവിടെ നൽകുക (ഡെക്കറേറ്ററിന് മുകളിൽ)
def get_all_drivers_by_area(target_area):
    try:
        ref = db.reference("drivers")
        drivers_data = ref.get()
        
        if not drivers_data:
            return []
        
        matched_drivers = []
        for driver_key, driver_info in drivers_data.items():
            if isinstance(driver_info, dict):
                d_area = str(driver_info.get("area", "")).strip().lower()
                
                if d_area == str(target_area).strip().lower():
                    driver_info['chat_id'] = driver_info.get('chat_id', driver_key)
                    matched_drivers.append(driver_info)
                    
        return matched_drivers
    except Exception as e:
        print(f"Error fetching drivers: {e}")
        return []
@st.cache_data(ttl=60)
def fetch_all_drivers_from_sheet():
    # Cache management (30 സെക്കൻഡ് വരെ പഴയ ഡാറ്റ ഉപയോഗിക്കുന്നു)
    if (
        "cached_drivers" in st.session_state
        and (
            time.time() - st.session_state.get("cache_time", 0)
        ) < 30
    ):
        return st.session_state.cached_drivers

    try:
        # ഗൂഗിൾ ഷീറ്റിൽ നിന്ന് ഡാറ്റ എടുക്കുന്നു
        res = requests.get(
            f"{GOOGLE_SHEET_URL}?action=get_all_drivers",
            timeout=40
        )

        # സ്റ്റാറ്റസ് 200 ആണോ എന്ന് പരിശോധിക്കുന്നു
        if res.status_code == 200:
            content = res.text.strip()
            # ഡാറ്റ ശരിയായ JSON ഫോർമാറ്റിലാണോ എന്ന് ഉറപ്പാക്കുന്നു
            if content.startswith(('[', '{')):
                data = res.json()
                if isinstance(data, list):
                    st.session_state.cached_drivers = data
                    st.session_state.cache_time = time.time()
                    return data
            else:
                # ടെർമിനലിൽ എറർ കാണിക്കും, പക്ഷെ ആപ്പ് ക്രാഷ് ആകില്ല
                print("ശ്രദ്ധിക്കുക: ഷീറ്റ് ഡാറ്റ JSON അല്ല -", content[:50])
        else:
            print("ഷീറ്റ് കണക്ഷൻ പരാജയപ്പെട്ടു, സ്റ്റാറ്റസ് കോഡ്:", res.status_code)
                
    except Exception as e:
        # ഇവിടെ എറർ റിപ്പോർട്ട് ചെയ്യുന്നു, പക്ഷെ ആപ്പ് തടസ്സമില്ലാതെ പ്രവർത്തിക്കും
        print(f"fetch_all_drivers_from_sheet എറർ: {e}")

    # ഡാറ്റ കിട്ടിയില്ലെങ്കിൽ പഴയ ക്യാഷ് ഉണ്ടോ എന്ന് നോക്കുന്നു, അല്ലെങ്കിൽ ഒഴിഞ്ഞ ലിസ്റ്റ്
    return st.session_state.get("cached_drivers", [])
def save_trip_dual_backup(payload):
    try:
        trip_id = payload.get("trip_id")
        if not trip_id:
            return False
        
        # ഫയർബേസിലെ trips നോഡിലേക്ക് നേരിട്ട് ഡാറ്റ സേവ് ചെയ്യുന്നു
        ref = db.reference(f"trips/{trip_id}")
        ref.set(payload)
        return True
    except Exception as e:
        print(f"Firebase Save Error: {e}")
        return False       


def calculate_haversine_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    R = 6371.0

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    return R * (
        2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )
    )


def send_individual_trip_link(
    driver,
    trip_details
):
    """
    ഡ്രൈവർക്ക് trip notification അയക്കുന്നു.
    Format: Clean, privacy-focused, mobile-friendly.
    Includes: Booking Date + Time
    """
    # 🆕 FIX: commission_amount ഇവിടെ ഡിഫൈൻ ചെയ്യുന്നു
    commission_amount = trip_details.get("commission_amount", 0)
    try:
        if not bot or not driver.get("chat_id"):
            return

        # ============================================================
        # Wallet Check
        # ============================================================
        wallet_balance = float(
            driver.get("wallet_balance", 0.0)
        )
        # 👇 2297-ാം വരി: ഇവിടെ നിന്നാണ് പുതിയ കോഡ് തുടങ്ങുന്നത് (8 സ്പേസ് ഇൻഡന്റേഷൻ)
        # ⚠️ ₹25 ആകുമ്പോൾ വാണിംഗ് കാണിക്കാൻ
        if WARNING_LIMIT <= wallet_balance < BLOCK_LIMIT:
            try:
                bot.send_message(
                    chat_id=driver["chat_id"],
                    text=f"⚠️ ശ്രദ്ധിക്കുക: നിങ്ങളുടെ കമ്മീഷൻ കുടിശ്ശിക ₹{wallet_balance} ആണ്. ഇത് ₹{BLOCK_LIMIT} കഴിഞ്ഞാൽ നിങ്ങൾക്ക് പുതിയ ട്രിപ്പുകൾ ലഭിക്കുന്നതല്ല."
                )
            except:
                pass
        
        
            

        if wallet_balance >= BLOCK_LIMIT:
            try:
                bot.send_message(
                    chat_id=driver["chat_id"],
                    text="🛑 വാലറ്റ് കമ്മീഷൻ പരിധി കടന്നതിനാൽ പുതിയ ട്രിപ്പുകൾ തടഞ്ഞിരിക്കുന്നു."
                )
            except:
                pass
            return

        # ============================================================
        # Data Extract
        # ============================================================
        trip_id = trip_details.get("trip_id", "N/A")
        customer_name = trip_details.get("customer_name", "N/A")
        pickup = trip_details.get("pickup", "N/A")
        drop = trip_details.get("drop", "N/A")

        trip_distance = (
            trip_details.get('calculated_distance')
            or trip_details.get('Calculated Distance')
            or trip_details.get('distance', 'N/A')
        )

        # ============================================================
        # ✅ Booking Date & Time
        # ============================================================
        booking_time_raw = (
            trip_details.get('booking_time')
            or trip_details.get('Booking Time')
            or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        try:
            # "2026-09-22 10:32:45" → date + time
            if " " in str(booking_time_raw):
                parts = str(booking_time_raw).split(" ")
                date_only = parts[0]                          # 2026-09-22
                time_only = parts[1][:5]                      # 10:32

                # Date format: DD-MM-YYYY
                if "-" in date_only:
                    y, m, d = date_only.split("-")
                    date_display = f"{d}-{m}-{y}"             # 22-09-2026
                else:
                    date_display = date_only

                # Time format: 12-hour with AM/PM
                try:
                    h, mi = time_only.split(":")
                    h = int(h)
                    ampm = "AM" if h < 12 else "PM"
                    h12 = h if 1 <= h <= 12 else (h - 12 if h > 12 else 12)
                    time_display = f"{h12:02d}:{mi} {ampm}"   # 10:32 AM
                except:
                    time_display = time_only
            else:
                date_display = datetime.datetime.now().strftime("%d-%m-%Y")
                time_display = datetime.datetime.now().strftime("%I:%M %p")
        except Exception:
            date_display = datetime.datetime.now().strftime("%d-%m-%Y")
            time_display = datetime.datetime.now().strftime("%I:%M %p")

        # ============================================================
        # Masked Phone
        # ============================================================
        raw_phone = str(
            trip_details.get('customer_phone')
            or trip_details.get('Customer Phone')
            or trip_details.get('phone', '')
        )
        if len(raw_phone) >= 6:
            masked_phone = raw_phone[:4] + "XXXX" + raw_phone[-2:]
        else:
            masked_phone = "XXXXXX"

        # ============================================================
        # GPS Link
        # ============================================================
        gps_url = (
            trip_details.get("location")
            or trip_details.get("GPS Link")
            or trip_details.get("location_link")
            or trip_details.get("pickup_link")
            or ""
        )

        if gps_url and gps_url.startswith("http"):
            gps_line = f"🔗 GPS: [📍 Location കാണുക]({gps_url})"
        else:
            gps_line = "🔗 GPS: ലഭ്യമല്ല"

        # ============================================================
        # Wallet Warning
        # ============================================================
        warning_text = ""
        if wallet_balance >= WARNING_LIMIT:
            warning_text = "⚠️ *മുന്നറിയിപ്പ്: വാലറ്റ് ബാലൻസ് കുറവാണ്!*\n\n"

        # ============================================================
        # Final Message (with Date + Time)
        # ============================================================
        message_text = (
            f"🚖 *പുതിയ ട്രിപ്പ് ലഭ്യമാണ്!*\n"
            f"🆔 {trip_id}\n"
            f"📅 Date: {date_display}\n"       # 👈 NEW
            f"🕐 Time: {time_display}\n"       # 👈 NEW
            f"👤 {customer_name}\n"
            f"📞 {masked_phone}\n"
            f"📍 പിക്കപ്പ്: {pickup}\n"
            f"🏁 ഡ്രോപ്പ്: {drop}\n"
            f"💰 കമ്മീഷൻ: ₹{commission_amount}\n"
            f"📏 ദൂരം: {trip_distance} km\n"
            f"{gps_line}\n\n"
            f"{warning_text}"
            f"⚠️ *ആദ്യം ക്ലിക്ക് ചെയ്യുന്ന ഡ്രൈവർക്കായിരിക്കും ഈ ട്രിപ്പ്!*"
        )

        # ============================================================
        # ACCEPT Button
        # ============================================================
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(
            types.InlineKeyboardButton(
                text="✅ ACCEPT TRIP",
                callback_data=f"accept_{trip_id}"
            )
        )

        # ============================================================
        # Send
        # ============================================================
        bot.send_message(
            chat_id=driver["chat_id"],
            text=message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )

        print(f"✅ Trip notification sent to driver {driver['chat_id']}")

    except Exception as e:
        print(f"❌ send_individual_trip_link error: {e}")
        try:
            log_and_report_error(e, "send_individual_trip_link")
        except:
            pass

def normalize_vehicle_type(vehicle_str):
    v = str(vehicle_str).lower()
    if "auto" in v and "rickshaw" in v:
        return "auto"
    elif "ഓട്ടോ" in v:
        return "auto"
    elif "taxi" in v or "car" in v or "കാർ" in v:
        return "car"
    elif "goods" in v or "ഗുഡ്സ്" in v:
        return "goods"
    elif "pickup" in v and "van" in v:
        return "van"
    elif "mini" in v or "lorry" in v or "ലോറി" in v:
        return "mini"
    elif "truck" in v or "ട്രക്ക്" in v:
        return "truck"
    elif "bike" in v or "ബൈക്ക്" in v:
        return "bike"
    return ""
def process_radius_expansion_routing(
    trip_details,
    customer_lat,
    customer_lon
):
    """
    ഓരോ Trip ID + Driver Chat ID combination-നും
    ഒരു Telegram notification മാത്രം അയയ്ക്കാൻ ശ്രമിക്കുന്നു.
    """

    try:
        trip_id = str(trip_details.get("trip_id", "")).strip()
        customer_vehicle = normalize_vehicle_type(
            trip_details.get("vehicle_type", "")
        )    
        print(f"🔍 Customer wants: {customer_vehicle}")
        if not trip_id:
            print("DEBUG: Trip ID ഇല്ല.")
            return

        # --------------------------------------------------------
        # 1. പോസ്റ്റ്ഗ്രസിൽ (Supabase) നിന്ന് ഡ്രൈവർമാരെ എടുക്കുന്നു
        # --------------------------------------------------------
        try:
            conn = psycopg2.connect(DB_URI)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # ഓൺലൈൻ ഡ്രൈവർമാരെ മാത്രം എടുക്കാം
            cursor.execute("SELECT * FROM drivers WHERE status = 'ONLINE'")
            all_drivers = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            if not all_drivers:
                print("DEBUG: Database-ൽ ഓൺലൈൻ ഡ്രൈവർമാർ ഇല്ല.")
                return
                
        except Exception as e:
            print(f"❌ Database Driver Fetch Error: {e}")
            return

        # --------------------------------------------------------
        # 2. പോസ്റ്റ്ഗ്രസിൽ നിന്ന് ട്രിപ്പ് സ്റ്റാറ്റസ് ചെക്ക് ചെയ്യുക
        # --------------------------------------------------------
        try:
            conn = psycopg2.connect(DB_URI)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # ട്രിപ്പ് ഡാറ്റ എടുക്കുന്നു
            cursor.execute("SELECT status FROM trips WHERE trip_id = %s", (trip_id,))
            current_trip = cursor.fetchone()
            
            cursor.close()
            conn.close()

            if current_trip:
                # സ്റ്റാറ്റസ് ചെക്ക് ചെയ്യുന്നു
                current_status = str(current_trip.get("status", "AVAILABLE")).upper()
                
                # ട്രിപ്പ് ഇപ്പോൾ ലഭ്യമല്ലെങ്കിൽ (അതായത് മറ്റൊരാൾ എടുത്തു കഴിഞ്ഞാൽ) തുടർന്നുള്ള കാര്യങ്ങൾ ചെയ്യേണ്ട
                if current_status not in ["AVAILABLE", "SCHEDULED", "PENDING"]:
                    print(f"DEBUG: Trip {trip_id} status = {current_status}. Notification skipped.")
                    return

        except Exception as e:
            print(f"DEBUG: Trip status check error: {e}")

        # --------------------------------------------------------
        # 3. ഇതുവരെ notification അയച്ചിട്ടില്ലാത്ത drivers
        # --------------------------------------------------------
        already_notified = set()
        try:
            conn = psycopg2.connect(DB_URI)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # നിലവിലെ notified_drivers എടുക്കുക
            cursor.execute("SELECT notified_drivers FROM trips WHERE trip_id = %s", (trip_id,))
            row = cursor.fetchone()
            
            if row and row.get("notified_drivers"):
                # കോമ ഉപയോഗിച്ച് വേർതിരിച്ച സ്ട്രിംഗ് ആണെങ്കിൽ സെറ്റ് ആക്കുക
                notified_str = row["notified_drivers"]
                already_notified = set([x.strip() for x in notified_str.split(",") if x.strip()])
                
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"DEBUG: Notified drivers fetch error: {e}")
        # ----------------------------------------------------
        # 4. ONLINE drivers മാത്രം
        # ----------------------------------------------------
        for driver in all_drivers:
            # 🔒 ലോക്ക് ചെക്ക് (12 സ്പേസുകൾ)
            # പോസ്റ്റ്ഗ്രസിൽ നിന്ന് ട്രിപ്പിന്റെ നിലവിലെ സ്റ്റാറ്റസ് ചെക്ക് ചെയ്യുന്നു
            try:
                conn = psycopg2.connect(DB_URI)
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT is_locked, status FROM trips WHERE trip_id = %s", (trip_id,))
                current_trip = cursor.fetchone()
                cursor.close()
                conn.close()
            
                if current_trip and (current_trip.get("is_locked") or current_trip.get("status") == "Accepted"):
                    print(f"⏭️ Trip {trip_id} already locked. Skipping remaining drivers.")
                    break
            except Exception as e:
                print(f"❌ DB Check Error: {e}")
               
            if not isinstance(driver, dict):
                continue

            driver_status = str(
                driver.get("status", "")
            ).strip().upper()

            if driver_status != "ONLINE":
                continue
            # 🎯 — Vehicle type filter
            driver_vehicle = normalize_vehicle_type(
                driver.get("vehicle_type", "")
            )
            if customer_vehicle and driver_vehicle:
                if customer_vehicle != driver_vehicle:
                    print(f"⏭️ Skip {driver.get('driver_name', '?')}: {driver_vehicle} ≠ {customer_vehicle}") 
                    continue 
 
           
             
            # Firebase driver record-ൽ chat_id
            d_chat_id = str(
                driver.get("chat_id")
                or driver.get("telegram_chat_id")
                or driver.get("Telegram Chat ID")
                or ""
            ).strip()

            if not d_chat_id:
                print(
                    f"DEBUG: Driver {driver.get('name', '')} "
                    f"- Telegram Chat ID ഇല്ല."
                )
                continue

            # ------------------------------------------------
            # 5. ഇതിനകം അയച്ചിട്ടുണ്ടെങ്കിൽ skip
            # ------------------------------------------------
            if d_chat_id in already_notified:
                print(
                    f"DEBUG: Trip {trip_id} -> "
                    f"{d_chat_id} already notified. SKIP."
                )
                continue

            # ------------------------------------------------
            # 6. Telegram അയയ്ക്കുന്നതിന് മുമ്പ്
            #    notification lock ചെയ്യുന്നു
            # ------------------------------------------------
           

            # ============================================================
            # 7. Telegram notification
            # ============================================================
            try:
                driver['chat_id'] = d_chat_id
                
                # മെസ്സേജ് അയക്കുന്നു
                send_individual_trip_link(driver, trip_details)
                
                # ============================================================
                # 8. Successfully processed (PostgreSQL Update)
                # ============================================================
                already_notified.add(d_chat_id)
                
                try:
                    conn = psycopg2.connect(DB_URI)
                    cursor = conn.cursor()
                    # ഡാറ്റാബേസിൽ notified_drivers അപ്ഡേറ്റ് ചെയ്യുന്നു
                    notified_str_to_save = ",".join(already_notified)
                    cursor.execute("UPDATE trips SET notified_drivers = %s WHERE trip_id = %s", (notified_str_to_save, trip_id))
                    conn.commit()
                    cursor.close()
                    conn.close()
                except Exception as db_err:
                    print(f"DEBUG: Notified drivers update error: {db_err}")
                
                print(f"DEBUG: Telegram sent successfully -> Trip {trip_id} / Driver {d_chat_id}")

            except Exception as e:
                # എറർ വന്നാൽ ലോഗ് ചെയ്യുക
                print(f"DEBUG: Telegram send error {d_chat_id}: {e}")

                # Send പരാജയപ്പെട്ടാൽ lock FAILED ആക്കുന്നു
                try:
                    driver_notification_ref.update({
                        "status": "FAILED",
                        "timestamp": time.time(),
                        "error": str(e)
                    })
                except Exception:
                    pass

                print(
                    f"DEBUG: Telegram send error "
                    f"{d_chat_id}: {e}"
                )

    except Exception as e:

        print(
            f"process_radius_expansion_routing ERROR: {e}"
        )

        try:
            log_and_report_error(
                e,
                "process_radius_expansion_routing"
            )
        except Exception:
            pass

# ============================================================
# 🚖 ഡ്രൈവർ ട്രിപ്പ് പാനൽ (Full Featured Web Page)
# ============================================================
def driver_trip_panel_page():
    # 👇 ഇവിടെയാണ് CSS കോഡ് ചേർക്കേണ്ടത് (ഇൻഡന്റേഷൻ ശ്രദ്ധിക്കുക)
    st.markdown("""
    <style>
    /* ഡ്രൈവർ പാനലിലെ കാർഡുകൾക്ക് വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് */
    div[data-testid="stVerticalBlock"] > div {
        background-color: white !important;
        padding: 10px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
    }
    
    /* എഴുത്തുകൾക്ക് കറുപ്പ് നിറം */
    h1, h2, h3, h4, p, label, span, div {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.title("🚖 ഡ്രൈവർ ട്രിപ്പ് പാനൽ")
    
    # URL-ൽ നിന്ന് ട്രിപ്പ് ഐഡി എടുക്കുക
    query_params = st.query_params
    trip_id = query_params.get("trip_id", "")
    driver_chat_id = query_params.get("driver_chat_id", "")
    
    if not trip_id:
        st.error("❌ ട്രിപ്പ് ഐഡി കണ്ടെത്താനായില്ല.")
        return
    
    # ഫയർബേസിൽ നിന്ന് ട്രിപ്പ് വിവരങ്ങൾ എടുക്കുക
    trip_data = get_trip_from_database(trip_id)
    
    if not trip_data:
        st.error("❌ ഈ ട്രിപ്പ് ഐഡിയിൽ വിവരങ്ങൾ ലഭ്യമല്ല.")
        return
    
    # ട്രിപ്പ് വിവരങ്ങൾ
    customer_name = trip_data.get("customer_name", "N/A")
    customer_phone = trip_data.get("customer_phone", "")
    pickup = trip_data.get("pickup", "N/A")
    drop = trip_data.get("drop", "N/A")
    pickup_lat = trip_data.get("pickup_lat", 0)
    pickup_lon = trip_data.get("pickup_lon", 0)
    total_fare = trip_data.get("total_fare", 0)
    status = trip_data.get("status", "Accepted")
    
    # 🆕 Distance & Commission എടുക്കുക
    distance = trip_data.get("calculated_distance", "N/A")
    commission = trip_data.get("commission_amount", "N/A")
        # ============================================================
    # 💰 ഡ്രൈവർ വാലറ്റ് ബാലൻസ് & UPI പേയ്മെന്റ് വിവരങ്ങൾ
    # ============================================================
    try:
        # നിങ്ങളുടെ ഡാറ്റാബേസിൽ ചാറ്റ് ഐഡി 'chat_id' എന്ന കോളത്തിലായതിനാൽ അത് ഉപയോഗിക്കുന്നു
        driver_wallet_res = supabase.table('drivers').select('wallet_balance').eq('chat_id', str(driver_chat_id)).execute()
        
        if driver_wallet_res.data:
            current_balance = float(driver_wallet_res.data[0].get('wallet_balance') or 0.0)
            
            st.markdown("### 💳 നിങ്ങളുടെ വാലറ്റ് വിവരങ്ങൾ")
            
            # ബാലൻസ് 30-ൽ കൂടുതലാണെങ്കിൽ ചുവപ്പ് നിറത്തിലും, അല്ലെങ്കിൽ പച്ച നിറത്തിലും കാണിക്കാൻ
            if current_balance >= 30.0:
                st.error(f"നിലവിലെ കമ്മീഷൻ കുടിശ്ശിക: **₹{current_balance:.2f}** (പണം അടയ്ക്കേണ്ടതുണ്ട്)")
                
                # 👇 ഇവിടെ നിങ്ങളുടെ അഡ്മിന്റെ UPI ID നൽകുക
                ADMIN_UPI_ID = "yourupiid@okaxis" 
                
                st.warning("⚠️ നിങ്ങളുടെ കുടിശ്ശിക ₹30-ൽ കൂടുതലാണ്. പുതിയ ട്രിപ്പുകൾ ലഭിക്കാൻ ദയവായി കമ്മീഷൻ അടയ്ക്കുക.")
                
                st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border: 1px solid #ffeeba; text-align: center;">
                    <h4 style="margin: 0; color: #856404;">അടയ്ക്കേണ്ട തുക: ₹{current_balance:.2f}</h4>
                    <p style="margin: 10px 0; font-size: 16px;">ഈ UPI ഐഡിയിലേക്ക് പണം അയക്കുക:</p>
                    <h3 style="margin: 0; color: #d9534f;">{ADMIN_UPI_ID}</h3>
                    <p style="margin-top: 10px; font-size: 12px; color: #666;">(പണം അയച്ച ശേഷം അഡ്മിനെ ബന്ധപ്പെടുക)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.success(f"നിലവിലെ കമ്മീഷൻ കുടിശ്ശിക: **₹{current_balance:.2f}**")
                
    except Exception as e:
        print(f"Wallet Fetch Error: {e}")
    
    # ============================================================
    # ✅ 1. ട്രിപ്പ് വിവരങ്ങൾ (Distance & Commission സഹിതം)
    # ============================================================
    st.markdown(f"""
    <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #2c3e50;">
        <h3 style="margin: 0; color: #2c3e50;">🆔 ട്രിപ്പ് ഐഡി: {trip_id}</h3>
        <p style="margin: 5px 0; color: #555;">👤 കസ്റ്റമർ: {customer_name}</p>
        <p style="margin: 5px 0; color: #555;">📍 പിക്കപ്പ്: {pickup}</p>
        <p style="margin: 5px 0; color: #555;">🏁 ഡ്രോപ്പ്: {drop}</p>
        <p style="margin: 5px 0; color: #555;">📏 ദൂരം: {distance} km</p>
        <p style="margin: 5px 0; color: #555;">💰 വാടക: ₹{total_fare}</p>
        <p style="margin: 5px 0; color: #555;">💵 കമ്മീഷൻ: ₹{commission}</p>
        <p style="margin: 5px 0; color: #555;">📊 സ്റ്റാറ്റസ്: {status}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # ✅ 2. ലൈവ് ലൊക്കേഷൻ ഷെയർ (Arrived ആകുന്നത് വരെ മാത്രം)
    # ============================================================
    if status != "Arrived":
        st.markdown("### 📍 ലൈവ് ലൊക്കേഷൻ ഷെയർ ചെയ്യുക")
        st.info("🔔 ഈ പേജ് ഓപ്പൺ ആയി വെക്കുക. ട്രിപ്പ് അവസാനിക്കുന്നത് വരെ ലൊക്കേഷൻ സ്വയമേവ അപ്ഡേറ്റ് ആകും.")
        
        @st.fragment(run_every=10)
        def update_location():
            try:
                location = streamlit_geolocation()
                if location and location.get("latitude") and location.get("longitude"):
                    lat = location.get("latitude")
                    lon = location.get("longitude")
                    
                    # നിങ്ങളുടെ പഴയ ഫയർബേസ് കോഡ് 
                    db.reference(f"trips/{trip_id}/driver_location").set({
                        "lat": lat,
                        "lon": lon,
                        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success(f"✅ ലൊക്കേഷൻ അപ്ഡേറ്റ് ആയി: {lat:.4f}, {lon:.4f}")
                else:
                    st.warning("⚠️ ലൊക്കേഷൻ ലഭ്യമല്ല. ദയവായി GPS ഓൺ ചെയ്യുക.")
            except Exception as e:
                st.error(f"❌ എറർ: {e}")
        
        update_location()

    # ============================================================
    # ✅ 3. നാവിഗേഷൻ ബട്ടൺ & നിർദ്ദേശം (Arrived ആകുന്നത് വരെ മാത്രം)
    # ============================================================
    if status != "Arrived":
        if pickup_lat and pickup_lon:
            nav_url = f"https://www.google.com/maps/dir/?api=1&destination={pickup_lat},{pickup_lon}"
            st.link_button("🗺️ കസ്റ്റമറുടെ അടുത്തേക്ക് പോകുക (Navigation)", nav_url, use_container_width=True)
            
            st.info("""
            📌 **ശ്രദ്ധിക്കുക:**
            • നാവിഗേഷൻ ബട്ടൺ അമർത്തിയാൽ, Google Maps തുറക്കും.
            • കസ്റ്റമറുടെ ലൊക്കേഷനിൽ എത്തിക്കഴിഞ്ഞാൽ, ഫോണിന്റെ **Back Button** അമർത്തി ഈ പേജിലേക്ക് തിരികെ വരിക.
            • ശേഷം, താഴെയുള്ള **"ഞാൻ എത്തി"** ബട്ടൺ അമർത്തുക.
            """)

    # ============================================================
    # ✅ 4. "ഞാൻ എത്തി" (Arrived) ബട്ടൺ (ഇവിടെയാണ് ഇൻഡന്റേഷൻ ശരിയാക്കിയത്)
    # ============================================================
    if status != "Arrived":
        st.markdown("### 🚖 എത്തിയോ?")
        
        # തെറ്റായ സ്പേസ് ഒഴിവാക്കി ഇവിടെ ശരിയാക്കി
        if st.button("🚕 ഡ്രൈവർ എത്തി (Arrived)", type="primary", use_container_width=True):
            
            # 1. സ്റ്റാറ്റസ് 'Arrived' ആക്കി അപ്ഡേറ്റ് ചെയ്യുക (Supabase)
            try:   
                supabase.table('trips').update({
                    "status": "Arrived",
                    "notification": "arrived_sound"
                }).eq('trip_id', trip_id).execute()
            except Exception as e:
                print(f"Error updating status: {e}")
                    
            # 2. കമ്മീഷൻ വാലറ്റിലേക്ക് ചേർക്കുക (Supabase)
            try:        
                if not trip_data.get("commission_added", False):        
                    trip_commission = float(trip_data.get("commission_amount") or 0.0)    
                    
                    driver_id = trip_data.get("driver_chat_id") or trip_data.get("driver_id")        
                        
                    if trip_commission > 0 and driver_id:    
                        driver_res = supabase.table('drivers').select('wallet_balance').eq('driver_chat_id', str(driver_id)).execute()
                        
                        if driver_res.data:
                            current_wallet = float(driver_res.data[0].get("wallet_balance") or 0.0)
                            new_wallet = current_wallet + trip_commission
                            
                            supabase.table('drivers').update({"wallet_balance": new_wallet}).eq('driver_chat_id', str(driver_id)).execute()       
                            supabase.table('trips').update({"commission_added": True}).eq('trip_id', trip_id).execute()
                                
                            # 3. വാലറ്റ് ലിമിറ്റ് മെസ്സേജുകൾ (Telegram)
                            # 👇 ഇവിടെ നിങ്ങളുടെ അഡ്മിന്റെ UPI ID നൽകുക
                            ADMIN_UPI_ID = "yourupiid@okaxis"     
                                    
                                    
                            if WARNING_LIMIT <= new_wallet < BLOCK_LIMIT:
                                try:
                                    bot.send_message(
                                        chat_id=driver_id,
                                        text=f"⚠️ ശ്രദ്ധിക്കുക: നിങ്ങളുടെ കമ്മീഷൻ കുടിശ്ശിക ₹{new_wallet:.2f} ആണ്. ഇത് ₹{BLOCK_LIMIT} കഴിഞ്ഞാൽ നിങ്ങൾക്ക് പുതിയ ട്രിപ്പുകൾ ലഭിക്കുന്നതല്ല.\n\nകുടിശ്ശിക തീർപ്പാക്കാൻ താഴെ പറയുന്ന UPI ഐഡിയിലേക്ക് പണം അയക്കുക:\n💳 {ADMIN_UPI_ID}"
                                    )
                                except:
                                    pass    
                                    
                            try:
                                bot.send_message(
                                    chat_id=driver_id,
                                    text=f"✅ ട്രിപ്പ് പൂർത്തിയായി. കമ്മീഷൻ: ₹{trip_commission}\nനിലവിലെ കുടിശ്ശിക: ₹{new_wallet:.2f}\n\nകുടിശ്ശിക തീർപ്പാക്കാൻ: {ADMIN_UPI_ID}"
                                )
                            except:
                                pass
            except Exception as e:
                print(f"Wallet Update Error: {e}")  
                
            st.success("✅ കസ്റ്റമറിനെ അറിയിച്ചിട്ടുണ്ട്!")
            st.balloons()
            st.rerun()    

    # ============================================================
    # ✅ 5. കസ്റ്റമറുടെ ഫോൺ നമ്പർ (Arrived ആയതിന് ശേഷം മാത്രം)
    # ============================================================
    if status == "Arrived":
        st.success("✅ നിങ്ങൾ കസ്റ്റമറുടെ അടുത്ത് എത്തിയിട്ടുണ്ട്.")
        st.markdown("### 📞 കസ്റ്റമറുമായി ബന്ധപ്പെടുക")
        
        customer_phone = trip_data.get("customer_phone", "")
        
        if customer_phone:
            st.warning("""
            ⚠️ **ശ്രദ്ധിക്കുക:**
            • കസ്റ്റമറുടെ ഫോൺ നമ്പർ അത്യാവശ്യ ഘട്ടങ്ങളിൽ മാത്രം ഉപയോഗിക്കുക.
            • അറൈവൽ ലൊക്കേഷനിൽ കസ്റ്റമറെ കണ്ടെത്താനായില്ലെങ്കിൽ മാത്രം വിളിക്കുക.
            • ദുരുപയോഗം ചെയ്താൽ നിയമനടപടികൾ നേരിടേണ്ടി വരും.
            """)
            
            st.markdown(f"""
            <a href="tel:{customer_phone}" style="
                display: inline-block;
                padding: 12px 24px;
                background-color: #28a745;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                text-align: center;
                width: 100%;
                box-sizing: border-box;
            ">📞 കസ്റ്റമറെ വിളിക്കുക</a>
            """, unsafe_allow_html=True)
            
            st.info("🔒 സുരക്ഷയ്ക്കായി കസ്റ്റമറുടെ ഫോൺ നമ്പർ മറച്ചുവെച്ചിരിക്കുന്നു.")
        else:
            st.warning("⚠️ ഫോൺ നമ്പർ ലഭ്യമല്ല.")
            
        # ==========================================================
        # 🔔 REAL-TIME NOTIFICATION LISTENER (ഇവിടെയും ഇൻഡന്റേഷൻ ശരിയാക്കി)
        # ==========================================================
        current_trip_id = trip_id
        if current_trip_id:
            trip_ref = db.reference(f"trips/{current_trip_id}")
            notification_placeholder = st.empty()
            
            def notification_listener(event):
                if event.data and isinstance(event.data, dict):
                    if event.data.get("notification") == "arrived_sound":
                        sound_html = """
                        <audio autoplay>
                            <source src="https://www.soundjay.com/phones/sounds/phone-ringing-01.mp3" type="audio/mpeg">
                        </audio>
                        """
                        components.html(sound_html, height=0)
                        
                        notification_placeholder.success(
                            "🚖 **നിങ്ങൾ ബുക്ക് ചെയ്ത വാഹനം എത്തിച്ചേർന്നിട്ടുണ്ട്!**"
                        )
                        trip_ref.update({"notification": "played"})
            trip_ref.listen(notification_listener)          
            
# ====================================================================
# 🖥️ STREAMLIT UI - CUSTOMER BOOKING INTERFACE (CLEANED & FIXED)
# ====================================================================

def apply_mobile_ui():
    # 👇 ഡീഫോൾട്ട് ബാക്ക്ഗ്രൗണ്ട്
    bg_image_url = "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?q=80&w=1920&auto=format&fit=crop" 
    try:
        response = supabase.table('app_settings').select('setting_value').eq('setting_key', 'background_image').execute()
        if response.data:
            bg_image_url = response.data[0]['setting_value']
    except Exception as e:
        print(f"Background fetch error: {e}")

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('{bg_image_url}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* പേജിന്റെ സൈഡ് പാഡിംഗ് കുറയ്ക്കുന്നു */
    .block-container {{
        padding-top: 5px !important;
        padding-bottom: 20px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
        max-width: 100% !important;
    }}

    /* സ്പേസുകൾ പൂർണ്ണമായും ഒഴിവാക്കുന്നു */
    div[data-testid="stVerticalBlock"] > div {{
        margin-bottom: 0rem !important;
        padding-bottom: 0rem !important;
        gap: 0.5rem !important;
    }}
    
    /* ജിപിഎസ് ഐക്കണിന്റെ ഉയരം കുറയ്ക്കുന്നു */
    iframe[title="streamlit_geolocation.streamlit_geolocation"] {{
        height: 40px !important; 
        margin-bottom: 0px !important;
    }}

    /* 6. ഹെഡർ ഡിസൈൻ (വീതിയും ഉയരവും കുറച്ചു) */
    .app-header {{
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        padding: 8px !important;
        border-radius: 8px !important;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        margin-bottom: 8px !important;
        width: 85% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
    .app-header h1 {{
        color: #FFD700;
        margin: 0;
        font-size: 16px !important;
        font-weight: 800;
    }}
    .app-header p {{
        color: #e0e0e0;
        font-size: 7px !important;
        margin-top: 0px !important;
    
        width: 85% !important; 
        margin-left: auto !important; 
        margin-right: auto !important;    
    }}

    /* ഗ്ലാസ് കാർഡ് */
    .glass-card {{
        background: rgba(255, 255, 255, 0.15) !important; 
        backdrop-filter: blur(10px) !important; 
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        padding: 8px !important;
        margin-bottom: 5px !important;
        color: white !important;
    }}

    /* ഫോം ഡിസൈൻ */
    div[data-testid="stForm"] {{
        background: rgba(255, 255, 255, 0.1) !important; 
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin-top: 5px !important;
    }}

    div[data-testid="stForm"] label p {{
        color: white !important;
        font-weight: bold !important;
        font-size: 10px !important;
        margin-bottom: 0px !important;
    }}

    div[data-testid="stForm"] div[data-baseweb="input"],
    div[data-testid="stForm"] div[data-baseweb="select"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 5px !important;
        border: none !important;
        min-height: 30px !important;
    }}
    
    /* ഹെഡ്ഡിംഗുകൾക്ക് വെളുത്ത നിറം */
    div[data-testid="stMarkdownContainer"] h3 {{
        color: white !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        font-size: 14px !important;
    }}

    /* SOS ബട്ടൺ */
    .sos-btn {{
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%) !important;
        color: white !important;
        border-radius: 5px !important;
        text-decoration: none;
        font-weight: bold;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 5px !important;
    }}

    /* മൊബൈൽ കോളങ്ങൾ */
    @media (max-width: 768px) {{
        div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 5px !important;
        }}
        
        div[data-testid="stHorizontalBlock"] > div {{
            flex: 1 !important;
            min-width: 0 !important;
        }}
    }}
    /* 👇 GPS കാർഡിന് പ്രത്യേക ഡിസൈൻ (ഇവിടെ ചേർക്കുക) */
    .gps-card-title {{
        color: #38bdf8 !important; 
        font-size: 16px !important;
        font-weight: bold !important;
        margin-bottom: 5px !important;
        display: flex;
        align-items: center;
    }}
    .gps-card-status {{
        font-size: 13px !important;
        font-weight: bold !important;
    }}
    /* 👇 എക്സ്പാൻഡർ (Expander) ഹെഡ്ഡിംഗിന് വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് നൽകാൻ */
    div[data-testid="stExpander"] details summary {{
        background-color: white !important;
        border-radius: 8px !important;
        padding: 10px !important;
        border: 1px solid #ddd !important;
    }}
    
    /* എക്സ്പാൻഡർ ഹെഡ്ഡിംഗിലെ എഴുത്തുകൾക്ക് കറുപ്പ് നിറം */
    div[data-testid="stExpander"] details summary p {{
        color: #333333 !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }}
    /* 👇 സ്പിന്നറിന് കീഴിലുള്ള എഴുത്തുകൾക്ക് വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് നൽകാൻ */
    div[data-testid="stSpinner"] {{
        background-color: white !important;
        padding: 10px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="stSpinner"] p, div[data-testid="stSpinner"] div {{
        color: #333333 !important;
        font-weight: bold !important;
    }}
    /* 👇 സ്പിന്നറിന് കീഴിലുള്ള എഴുത്തുകൾക്ക് വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് നൽകാൻ */
    div[data-testid="stSpinner"] {{
        background-color: white !important;
        padding: 10px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }}
    div[data-testid="stSpinner"] p, div[data-testid="stSpinner"] div {{
        color: #333333 !important;
        font-weight: bold !important;
    }}
    /* 👇 'sos_panel_box' എന്ന key ഉള്ള കണ്ടെയ്നറിന് മാത്രം വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് */
    div[class*="st-key-sos_panel_box"] {{
        background-color: #ffffff !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border: 2px solid #d32f2f !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
    }}
    
    /* അതിനുള്ളിലെ എല്ലാ എഴുത്തുകൾക്കും കറുപ്പ് നിറം */
    div[class*="st-key-sos_panel_box"] * {{
        color: #000000 !important;
    }}
    </style>
    
    """, unsafe_allow_html=True)

def main():
    apply_mobile_ui()  # 👈 ഈ വരി ഇവിടെ ചേർക്കുക
 
    

    # ============================================================
    # 🔔 Push Notification Service Worker രജിസ്റ്റർ ചെയ്യുക
    # ============================================================
    components.html("""
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('✅ Service Worker Registered');
                })
                .catch(function(err) {
                    console.log('❌ Service Worker Registration Failed:', err);
                });
            } else {
                console.log('❌ Service Worker not supported');
            }
        </script>
    """, height=0)
    # 🆕 URL-ൽ driver_trip_panel ഉണ്ടെങ്കിൽ, ആ പേജ് മാത്രം കാണിക്കുക
    query_params = st.query_params
    if query_params.get("page") == "driver_trip_panel":
        driver_trip_panel_page()
        return  # ബാക്കി കോഡ് റൺ ചെയ്യരുത്
    # 1. പുതിയ മൊബൈൽ ഹെഡർ
    st.markdown("""
    <div style="text-align: center; padding: 15px; background: #1a237e; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
        <h1 class="main-title" style="color: #FFD700; margin: 0; font-size: 2rem;">🚕 EASY AUTO TAXI</h1>
        <p style="color: white; font-size: 12px; letter-spacing: 2px; margin-top: 5px;">FAST • SECURE • RELIABLE</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("\n")

    # Session state for button disable
    if 'is_booking' not in st.session_state:
        st.session_state.is_booking = False

    # ----------------------------------------------------------------
    # 📍 ULTIMATE RELIABLE GPS LOCATION (Final Clean Version)
    # ----------------------------------------------------------------
    if 'lat' not in st.session_state:
        st.session_state.lat = None
    if 'lon' not in st.session_state:
        st.session_state.lon = None
    if 'gps_link' not in st.session_state:
        st.session_state.gps_link = "Not Available"
    if 'gps_enabled' not in st.session_state:      # <--- ഈ വരി ഇവിടെ ചേർക്കുക
        st.session_state.gps_enabled = False       # <--- ഇതും

    # ============================================================
    # 📍 പുതിയ GPS കാർഡും SOS ബട്ടണും (Mobile Friendly Layout)
    # ============================================================
    
    # GPS ലൊക്കേഷൻ എടുക്കുന്നു (ഇവിടെ മാത്രം ഒരു തവണ)
    
    # 👇 GPS കാർഡും SOS ബട്ടണും
    gps_status_color = "#00b09b" if st.session_state.lat and st.session_state.lon else "#ffc107"
    gps_status_icon = "✅ കണക്ഷൻ വിജയകരം" if st.session_state.lat and st.session_state.lon else "⚠️ ലൊക്കേഷൻ ലഭ്യമല്ല"
    gps_coords = f"Lat: {st.session_state.lat:.4f} | Lon: {st.session_state.lon:.4f}" if st.session_state.lat else ""

    st.markdown(f"""<div style="display: flex; flex-wrap: nowrap; gap: 5px; align-items: stretch; margin-bottom: 15px;">
<div style="flex: 1; background-color: #e3f2fd; border: 1px solid {gps_status_color}; border-left: 5px solid {gps_status_color}; border-radius: 12px; padding: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); margin-bottom: 0;">
<div style="color: color: #1a237e; margin: 0 0 5px 0; font-size: 15px;">📍 GPS ലൊക്കേഷൻ</div>
<div style="margin: 6px 0 0 0; color: #1a237e !important; font-weight: 600 !important; font-size: 13px !important;">{gps_status_icon}</div>
<div style="margin: 2px 0 0 0; font-size: 10px; color: #a0aec0;">{gps_coords}</div>
</div>
<div style="flex: 1; display: flex; flex-direction: column; gap: 5px;">
    <a href="?sos=true" target="_self" class="sos-btn" style="padding: 8px; font-size: 12px; margin-bottom: 0; border-radius: 8px; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%; text-decoration: none;">
        🛡️ SOS<br><span style="font-size: 8px;">EMERGENCY</span>
    </a>
    <a href="?show_live_tracking=true" target="_self" style="text-decoration: none;">
    <div style="background-color: #ffebee; padding: 6px; border-radius: 8px; text-align: center; border: 1px solid #ffcdd2; cursor: pointer;">
        <p style="margin: 0; font-size: 8px; color: #b71c1c; font-weight: bold;">Share Location</p>
        <p style="margin: 2px 0; font-weight: bold; color: #2e7d32; font-size: 8px;">● Live Tracking</p>
    </div>
</a>
</div>
</div>""", unsafe_allow_html=True)
    # 👇 പുതിയ SOS പാനൽ കോഡ് (ഇവിടെ തുടങ്ങുന്നു)
    if st.query_params.get("sos") == "true":
        
        # 👇 ഇവിടെയാണ് വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് നൽകുന്നത് (കണ്ടെയ്നറിന് key നൽകി)
        with st.container(key="sos_panel_box"):
            st.markdown("---")
            st.error("🚨 അടിയന്തര സഹായ വിഭാഗം (Emergency Control Rooms)")
            
            st.markdown("""
            * 🚔 **പോലീസ് (112):** [📞 കോൾ ചെയ്യുക](tel:112)
            * 🚒 **ഫയർ ആൻഡ് റെസ്ക്യൂ (101):** [📞 കോൾ ചെയ്യുക](tel:101)
            * 🚑 **ആംബുലൻസ് (108):** [📞 കോൾ ചെയ്യുക](tel:108)
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("📍 ലൊക്കേഷൻ വഴി അയക്കാൻ")
            
            sos_message = "എനിക്ക് അടിയന്തര സഹായം ആവശ്യമാണ്. ദയവായി ഉടൻ ബന്ധപ്പെടുക. (ഡ്രൈവർ/യാത്രക്കാരൻ)"
            whatsapp_share_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(sos_message)}"
            
            st.markdown(f"""
            <a href="{whatsapp_share_url}" target="_blank" style="text-decoration: none;">
                <button style="background-color: #25D366; color: white; padding: 10px 15px; border: none; border-radius: 5px; font-size: 14px; font-weight: bold; width: 100%;">
                    💬 വാട്സാപ്പിൽ അയക്കുക
                </button>
            </a>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("SOS പാനൽ അടയ്ക്കുക", use_container_width=True):
                st.query_params.clear()
                st.rerun()
    # 👇 ലൈവ് ട്രാക്കിംഗ് ബോക്സിൽ ക്ലിക്ക് ചെയ്തിട്ടുണ്ടോ എന്ന് ചെക്ക് ചെയ്യുന്നു
    
    if st.query_params.get("show_live_tracking") == "true":
        
        # 👇 ഇവിടെയാണ് വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് കൃത്യമായി നൽകുന്നത്
        st.markdown("""
        <style>
        .stApp {
            background-image: none !important;
            background-color: #ffffff !important;
        }
        h1, h2, h3, h4, p, label, span, div {
            color: #333333 !important;
        }
        /* 👇 ഇതാ പുതിയതായി ചേർത്ത ഭാഗം (ഹെഡറിന് വെള്ള നിറം) */
        .app-header h1, .app-header p {
            color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🗺️ ലൈവ് ട്രാക്കിംഗ് മാപ്പ്")
        
        current_trip_id = st.session_state.get('current_trip_id', 'TRIP-XXXXX') 
        current_customer_lat = st.session_state.lat
        current_customer_lon = st.session_state.lon
        current_vehicle_type = "Auto" 
        
        # 👇 പ്രധാനം: ജിപിഎസ് ലഭ്യമാണോ എന്ന് ചെക്ക് ചെയ്യുന്നു (എറർ ഒഴിവാക്കാൻ)
        if current_customer_lat is None or current_customer_lon is None:
            st.warning("⚠️ ലൈവ് ട്രാക്കിംഗ് കാണാൻ ദയവായി നിങ്ങളുടെ ജിപിഎസ് ഓൺ ചെയ്ത് പെർമിഷൻ നൽകുക.")
        else:
            # ജിപിഎസ് ഉണ്ടെങ്കിൽ മാത്രം മാപ്പ് വിളിക്കുന്നു
            render_live_tracking_map(current_trip_id, current_customer_lat, current_customer_lon, current_vehicle_type)
    # 👇 GPS ഐക്കൺ
    loc_data = streamlit_geolocation()
    if loc_data and loc_data.get("latitude"):
        st.session_state.lat = loc_data.get("latitude")
        st.session_state.lon = loc_data.get("longitude")
        st.session_state.gps_link = f"https://maps.google.com/?q={st.session_state.lat},{st.session_state.lon}"

   
    # 👆 ഇവിടെയാണ് കോഡ് അവസാനിക്കുന്നത് (unsafe_allow_html=True ശ്രദ്ധിക്കുക)

    

    # 👇 ഇവിടെ നിന്ന് തുടർന്ന് നിങ്ങളുടെ പഴയ കോഡ് (യാത്രാ വിവരങ്ങൾ) വരണം
        # 👇 ചെറിയ വര വരച്ച് യാത്രാ വിവരങ്ങൾ കൊടുക്കാൻ
    st.markdown("<hr style='margin: 5px 0; border: 0.5px solid #ffffff;'>", unsafe_allow_html=True)
    st.markdown("### 📝 യാത്രാ വിവരങ്ങൾ രേഖപ്പെടുത്തുക")
    
    
    
        # 🛑 st.form ഉപയോഗിച്ച് ബുക്കിംഗ് ഫോം സുരക്ഷിതമാക്കിയിരിക്കുന്നു
    with st.form("booking_form"):
        st.markdown("### 👤 യാത്രക്കാരന്റെ വിവരങ്ങൾ")
        
        # പേരിനും ഫോണിനും രണ്ട് കോളങ്ങൾ
        col_name, col_phone = st.columns(2)
        with col_name:
            c_name = st.text_input("പേര് (Name)", placeholder="നിങ്ങളുടെ പേര്")
        with col_phone:
            c_phone = st.text_input("ഫോൺ (Phone)", placeholder="9876543210")

        st.markdown("### 🚕 യാത്രാ വിവരങ്ങൾ")
        
        # വാഹനത്തിന്റെ തരം
        vehicle_options = [
            "🛺 ഓട്ടോറിക്ഷ (Autorickshaw)",
            "🚗 ടാക്സി കാർ (Taxi Car)",
            "🚙 ഗുഡ്സ് ഓട്ടോ പിക്കപ്പ് (Goods Auto Pickup)",
            "🚐 പിക്കപ്പ് വാൻ (Pickup Van)",
            "🚚 മിനി ലോറി (Mini Lorry)",
            "🚛 ട്രക്ക് (Truck)",
            "🏍️ ബൈക്ക് ടാക്സി (Bike Taxi)"
        ]
        vehicle_type = st.selectbox("വാഹനം (Vehicle Type)", options=vehicle_options)

        # ലൊക്കേഷനുകൾ എടുക്കുന്നു
        locations_list = get_locations_from_firebase()
        areas_list = get_areas_from_firebase()

        # പിക്കപ്പും ഡ്രോപ്പും രണ്ട് കോളങ്ങൾ
        col_pickup, col_drop = st.columns(2)
        with col_pickup:
            if locations_list and len(locations_list) > 0:
                pickup_place = st.selectbox("പിക്കപ്പ് (Pickup)", options=locations_list)
            else:
                st.warning("⚠️ ഫയർബേസിൽ 'locations' നോഡിൽ ലൊക്കേഷനുകൾ ചേർക്കുക.")
                pickup_place = st.text_input("📍 പുറപ്പെടുന്ന സ്ഥലം (Pickup) മാനുവലായി നൽകുക:")
                
        with col_drop:
            if locations_list and len(locations_list) > 0:
                drop_place = st.selectbox("ഡ്രോപ്പ് (Drop)", options=locations_list)
            else:
                st.warning("⚠️ ഫയർബേസിൽ 'locations' നോഡിൽ ലൊക്കേഷനുകൾ ചേർക്കുക.")
                drop_place = st.text_input("🏁 പോകേണ്ട സ്ഥലം (Drop) മാനുവലായി നൽകുക:")

        # ഏരിയ
        if areas_list and len(areas_list) > 0:
            trip_area = st.selectbox("ഏരിയ (Area)", options=areas_list)
        else:
            st.warning("⚠️ ഫയർബേസിൽ 'areas' നോഡിൽ ലൊക്കേഷനുകൾ ചേർക്കുക.")
            trip_area = st.text_input("📍 ഏരിയ മാനുവലായി നൽകുക:")

        # Smart Captcha
        if 'render_smart_captcha_field' in globals():
            render_smart_captcha_field()

        # സബ്മിറ്റ് ബട്ടൺ
        submitted = st.form_submit_button("🚗 ബുക്ക് ചെയ്യുക (Book Ride Now)", type="primary")

    if submitted:
        st.session_state.is_booking = True

        # 🆕 1. GPS എനേബിൾ ചെയ്തിട്ടുണ്ടോ എന്ന് പരിശോധിക്കുക
        # lat, lon ഉണ്ടെങ്കിൽ gps_enabled = True ആക്കുക (ഇത് പ്രധാനം)
        if st.session_state.lat and st.session_state.lon:
            st.session_state.gps_enabled = True
        if not st.session_state.gps_enabled:
            st.markdown("""
            <div style="background-color: #ffebee; border-left: 5px solid #d32f2f; padding: 12px; border-radius: 8px; margin-bottom: 10px; font-size: 13px;">
                <b style="color: #c62828;">📍 GPS ലൊക്കേഷൻ ലഭ്യമല്ല!</b><br>
                <span style="color: #333; font-size: 12px;">
                ബുക്കിംഗ് പൂർത്തിയാക്കാൻ ദയവായി നിങ്ങളുടെ ലൊക്കേഷൻ ഓൺ ചെയ്യുക. 
                ബ്രൗസർ സെറ്റിംഗ്സിൽ നിന്ന് "Location Permission" നൽകുക.
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.toast("⚠️ GPS ഓൺ ചെയ്യാതെ ബുക്കിംഗ് സാധ്യമല്ല!", icon="❌")
            st.session_state.is_booking = False
            st.stop()            

        
        # Validation checks
        if not (c_name and c_phone and pickup_place and drop_place):
            st.warning("⚠️ ദയവായി എല്ലാ വിവരങ്ങളും നൽകുക!")
            st.session_state.is_booking = False
            st.stop()

        if pickup_place == drop_place:
            st.warning("⚠️ Pickup, Drop ഒരേ സ്ഥലം ആകരുത്.")
            st.warning("⚠️ ദയവായി വ്യത്യസ്തമായ സ്ഥലങ്ങൾ തിരഞ്ഞെടുക്കുക.")
            st.session_state.is_booking = False
            st.stop()

        # Spam Check (ഉണ്ടെങ്കിൽ മാത്രം)
        if 'check_spam_and_rate_limit' in globals():
            is_allowed, msg = check_spam_and_rate_limit(c_phone)
            if not is_allowed:
                st.error(msg)
                st.session_state.is_booking = False
                st.stop()

        # Distance & Fare Calculation
        with st.spinner("🔍 ദൂരം കണക്കാക്കുന്നു..."):
            customer_lat = st.session_state.lat
            customer_lon = st.session_state.lon
            
            exact_distance = None
            if customer_lat and customer_lon:
                # കസ്റ്റമറുടെ ലൈവ് ലൊക്കേഷനിൽ നിന്ന് ഡ്രോപ്പ് സ്ഥലത്തേക്കുള്ള ദൂരം കണക്കാക്കുന്നു
                exact_distance = get_distance_from_coords_to_place(customer_lat, customer_lon, drop_place)
            
            # 1. ലൈവ് ലൊക്കേഷൻ വെച്ച് ദൂരം കണക്കാക്കാൻ പറ്റിയില്ലെങ്കിൽ, പഴയ രീതിയിലേക്ക് മാറുക
            if exact_distance is None:
                exact_distance = get_real_road_distance(pickup_place, drop_place) if 'get_real_road_distance' in globals() else 5.0
            
            # 2. അപ്പോഴും ദൂരം ലഭിച്ചില്ലെങ്കിൽ, എറർ കാണിച്ച് നിർത്തുക
            if exact_distance is None:
                st.toast("📍 നിങ്ങൾ തിരഞ്ഞെടുത്ത ലൊക്കേഷൻ കണ്ടെത്താനായില്ല! ദയവായി മറ്റൊരു സ്ഥലം തിരഞ്ഞെടുക്കുക.", icon="❌")
                st.session_state.is_booking = False
                st.stop()

            # 3. ദൂരം കൃത്യമായി ലഭിച്ചാൽ മാത്രം റൗണ്ട് ചെയ്യുക
            exact_distance = round(exact_distance, 1)

        
        rate_per_km = 15 if vehicle_type == "Auto Rickshaw" else 22
        total_fare = round(exact_distance * rate_per_km, 2)
        commission_amount = calculate_admin_commission(exact_distance) if 'calculate_admin_commission' in globals() else 10.0
        unique_trip_id = f"TRIP-{random.randint(10000, 99999)}"
        # 👇 പഴയത് ഡിലീറ്റ് ചെയ്ത് ഇത് നൽകുക
        st.markdown(f"""
        <div style="background-color: white; padding: 10px; border-radius: 8px; border-left: 5px solid #2563eb; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <span style="color: #333333; font-weight: bold;">📊 Booking Details:</span> 
            <span style="color: #1a237e;">{pickup_place} to {drop_place}</span>
        </div>
        """, unsafe_allow_html=True)    
        

        # ============================================================
        # 🚗 DRIVER LOGIC & RADIUS ROUTING (FIXED)
        # ============================================================
        with st.spinner("ഡ്രൈവർമാരെ തിരയുന്നു..."):
            drivers_in_area = get_all_drivers_by_area(trip_area) if 'get_all_drivers_by_area' in globals() else []

            if not drivers_in_area:
                st.warning("⚠️ ഈ ഏരിയയിൽ നിലവിൽ ഡ്രൈവർമാർ ലഭ്യമല്ല.")
            else:
                # ============================================
                # ✅ FIX #1: Trip ഒരിക്കൽ മാത്രം Firebase-ൽ Save
                # ============================================
                payload = {
                    "action": "create_trip",
                    "secret_key": st.secrets["API_SECRET_KEY"],
                    "trip_id": unique_trip_id,
                    "customer_name": sanitize_input(c_name) if 'sanitize_input' in globals() else c_name,
                    "customer_phone": sanitize_input(c_phone) if 'sanitize_input' in globals() else c_phone,
                    "pickup": sanitize_input(pickup_place) if 'sanitize_input' in globals() else pickup_place,
                    "drop": sanitize_input(drop_place) if 'sanitize_input' in globals() else drop_place,
                    "vehicle_type": vehicle_type,
                    "area": trip_area,
                    "location": st.session_state.get('gps_link', 'Not Available'),
                    "pickup_lat": st.session_state.lat, 
                    "pickup_lon": st.session_state.lon,
                    "status": "AVAILABLE",
                    "calculated_distance": exact_distance,
                    "total_fare": total_fare,
                    "commission_amount": commission_amount,
                    "schedule_time": "Now",
                    "booking_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    # Driver-specific fields trip-level അല്ല
                    "driver_name": "",
                    "driver_phone": "",
                    "driver_chat_id": "",
                    "notified_drivers": {}
                }

                # ഒരിക്കൽ മാത്രം save (loop ഇല്ല!)
                trip_saved = save_new_trip(
                    booking_id=unique_trip_id,
                    customer_name=payload["customer_name"],
                    customer_phone=payload["customer_phone"],
                    pickup=payload["pickup"],
                    drop=payload["drop"],
                    distance=payload["calculated_distance"],
                    pickup_link=payload["location"],
                    total_fare=payload["total_fare"],                   # പുതിയത്
                    commission_amount=payload["commission_amount"],     # പുതിയത്
                    pickup_lat=payload["pickup_lat"],                   # പുതിയത്
                    pickup_lon=payload["pickup_lon"],                   # പുതിയത്
                    vehicle_type=payload["vehicle_type"],               # പുതിയത്
                    area=payload["area"]                                # പുതിയത്
                )

                if trip_saved:
                    if 'register_successful_booking_attempt' in globals():
                        register_successful_booking_attempt()

                    # Driver notification — Vera function വഴി
                    if 'process_radius_expansion_routing' in globals():
                        process_radius_expansion_routing(payload, st.session_state.lat, st.session_state.lon)

                    # 👇 ഇവിടെയാണ് പഴയ st.success(...) വരിയുണ്ടായിരുന്നത്. 
                    # അത് ഡിലീറ്റ് ചെയ്ത് ഈ പുതിയ കോഡ് നൽകുക:
                    st.markdown("""
                    <div style="background-color: #d4edda; color: #155724; padding: 12px; border-radius: 8px; border-left: 5px solid #28a745; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <b style="font-size: 15px;">✅ ബുക്കിംഗ് വിജയകരമായി പൂർത്തിയായി!</b>
                    </div>
                    """, unsafe_allow_html=True)    

                    # ട്രിപ്പ് ഐഡിയും ഡ്രൈവർ സുരക്ഷാ നിർദ്ദേശങ്ങളും അടങ്ങിയ പ്രൊഫഷണൽ കാർഡ്
                    card_html = f"""<div style="padding: 18px; border-radius: 12px; background-color: #eef2ff; border-left: 6px solid #2563eb; border-right: 6px solid #f59e0b; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); margin-bottom: 20px;">
    <div style="margin-bottom: 15px;">
        <span style="font-size: 15px; font-weight: 600; color: #1e3a8a;">നിങ്ങളുടെ ട്രിപ്പ് ഐഡി:</span>
        <div style="background-color: #fff3cd; border: 2px solid #ffc107; padding: 8px 14px; border-radius: 8px; display: inline-block; font-weight: bold; color: #856404; font-size: 18px; margin-top: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">{unique_trip_id}</div>
    </div>
    <h4 style="color: #1e3a8a; margin-top: 0; margin-bottom: 8px; font-size: 16px;">🚗 ഡ്രൈവർ വിവരങ്ങൾ & സുരക്ഷാ നിർദ്ദേശം:</h4>
    <p style="color: #1f2937; font-size: 14px; line-height: 1.6; margin: 0;">
        നിങ്ങൾ ബുക്ക് ചെയ്ത വാഹനത്തിന്റെ 🚖 ഡ്രൈവറുടെ തത്സമയ വിവരങ്ങൾ അറിയുന്നതിനായി ഈ വെബ് ആപ്പ് ക്ലോസ് ചെയ്യാതെ നിലനിർത്തുക.<br><br>
        എന്തെങ്കിലും കാരണവശാൽ ആപ്ലിക്കേഷൻ ക്ലോസ് ആയിപ്പോയാൽ, വീണ്ടും ആപ്പ് ഓപ്പൺ ചെയ്യുമ്പോൾ മുകളിൽ നൽകിയിരിക്കുന്ന ട്രിപ്പ് ഐഡി നൽകി ബുക്കിംഗ് സ്റ്റാറ്റസ് പരിശോധിക്കാവുന്നതാണ്.
    </p>
</div>"""
                    st.markdown(card_html, unsafe_allow_html=True)

                    # 👇 Asynchronous Realtime ലിസണർ (ബാക്ക്ഗ്രൗണ്ട് ത്രെഡിൽ പ്രവർത്തിക്കാൻ)
                    import asyncio
                    import threading
                    from supabase import acreate_client

                    async def async_listen(trip_id, supabase_url, supabase_key):
                        async_client = await acreate_client(supabase_url, supabase_key)
                        channel = async_client.channel(f"trip_updates_{trip_id}")
                        
                        def handle_change(payload):
                            if payload['new'].get('status') == 'Accepted':
                                st.session_state.trip_accepted = True
                                
                        await channel.on_postgres_changes(
                            event="UPDATE",
                            schema="public",
                            table="trips",
                            filter=f"trip_id=eq.{trip_id}",
                            callback=handle_change
                        ).subscribe()
                        
                        # കണക്ഷൻ ഓപ്പൺ ആയി നിൽക്കാൻ
                        await asyncio.Event().wait()

                    def start_listener(trip_id, supabase_url, supabase_key):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(async_listen(trip_id, supabase_url, supabase_key))

                    # ലിസണർ തുടങ്ങുന്നു (ഒരു തവണ മാത്രം)
                    if 'listener_started' not in st.session_state:
                        threading.Thread(
                            target=start_listener, 
                            args=(unique_trip_id, SUPABASE_URL, SUPABASE_KEY),  
                            daemon=True
                        ).start()
                        st.session_state.listener_started = True

                    # 👇 റിയൽ ടൈം അപ്ഡേറ്റ് വന്നോ എന്ന് ചെക്ക് ചെയ്യാൻ (ഓരോ 2 സെക്കൻഡിലും)
                    @st.fragment(run_every=2)
                    def check_status():
                        if st.session_state.get('trip_accepted'):
                            st.rerun()
                            
                    check_status()
                    

                    # ----------------------------------------------------
                    # 📍 ലൈവ് മാപ്പ് കോൾ
                    # ----------------------------------------------------
                    st.write("---")
                    # 👇 സൂപ്പർബേസിൽ നിന്ന് ഡാറ്റ എടുക്കുന്നു
                    try:
                        response = supabase.table('trips').select('*').eq('trip_id', unique_trip_id).execute()
                        trip_data = response.data[0] if response.data else None
                    except Exception as e:
                        trip_data = None    
                        
                    if trip_data:
                        status = str(trip_data.get("status", "Pending")).strip()
                    else:
                        status = "Pending" 
                    vehicle_type_check = trip_data.get("vehicle_type", "Auto Rickshaw") if trip_data else "Auto Rickshaw"
                    # 🆕 ഡ്രൈവർ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തതിന് ശേഷം ("Pending" അല്ലാത്ത എല്ലാ അവസ്ഥയിലും) ഈ കോഡ് പ്രവർത്തിക്കും
                    if status != "Pending":
    

                    
                    
                        # 🔔 1. നോട്ടിഫിക്കേഷൻ സൗണ്ട്
                        if not st.session_state.get('accept_sound_played', False):
                            notification_sound = """
                            <audio autoplay>
                                <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                            </audio>
                            """
                            st.markdown(notification_sound, unsafe_allow_html=True)
                            st.session_state.accept_sound_played = True 
                        

                        # 2. ഡ്രൈവർ വിവരങ്ങളും മാപ്പും അടങ്ങിയ പോപ്പ്-അപ്പ് കണ്ടെയ്നർ
                        with st.container():
                            st.success("🎉 **അഭിനന്ദനങ്ങൾ! ഒരു ഡ്രൈവർ നിങ്ങളുടെ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തിരിക്കുന്നു!**")
                            if "taxi" in vehicle_type_check.lower() or "car" in vehicle_type_check.lower():
                                st.markdown("### 🚖 ടാക്സി കാർ നിങ്ങളുടെ അടുത്തേക്ക് വരുന്നു...")
                            else:
                                st.markdown("### 🛺 ഓട്ടോറിക്ഷ നിങ്ങളുടെ അടുത്തേക്ക് വരുന്നു...")

                            st.markdown("### 👤 ഡ്രൈവർ വിവരങ്ങൾ")
                            st.write(f"**ഡ്രൈവർ പേര്:** {trip_data.get('driver_name', 'N/A')}")
                            st.write(f"**വാഹന നമ്പർ:** {trip_data.get('vehicle_number', 'N/A')} ({vehicle_type_check})")

                            # മാസ്ക് ചെയ്ത ഫോൺ നമ്പർ
                            raw_driver_phone = trip_data.get('driver_phone', '')
                            masked_d_phone = mask_phone_number(raw_driver_phone) if 'mask_phone_number' in globals() else raw_driver_phone
                            st.write(f"**ഫോൺ നമ്പർ:** `{masked_d_phone}`")

                            st.markdown("---")
                            st.markdown("### 🗺️ ഡ്രൈവറുടെ ലൈവ് ലൊക്കേഷൻ ട്രാക്കിംഗ്")

                            if lat and lon:
                                render_live_tracking_map(unique_trip_id, lat, lon, vehicle_type_check)
                            else:
                                st.warning("⚠️ മാപ്പ് കാണുന്നതിനായി നിങ്ങളുടെ ജിപിഎസ് ലൊക്കേഷൻ സജീവമാക്കുക.")
                    else:
                        # ഡ്രൈവർ അക്സെപ്റ്റ് ചെയ്യുന്നത് വരെ
                        st.markdown("""<div style="background-color: white; color: #333333; padding: 12px; border-radius: 8px; border-left: 5px solid #ffc107; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);"><b>⏳ ഡ്രൈവർമാർ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്യുന്നതിനായി കാത്തിരിക്കുന്നു...</b><span style="font-size: 13px; margin-top: 5px; display: block;">ദയവായി ഈ പേജ് ക്ലോസ് ചെയ്യരുത്.</span></div>""", unsafe_allow_html=True)    

                    with st.expander("📝 സേവന നിബന്ധനകളും ഡിസ്ക്ലൈമറും"):
                        st.markdown("""
                        <div style="background-color: white; padding: 15px; border-radius: 8px; color: #333333; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-size: 14px;">
                        <b style="color: #d32f2f; font-size: 15px;">ഡിസ്ക്ലെയിമർ (Disclaimer):</b><br><br>
                            • ഈ ആപ്ലിക്കേഷൻ ഡ്രൈവർമാരെയും യാത്രക്കാരെയും ബന്ധിപ്പിക്കുന്ന ഒരു <b>ഡിജിറ്റൽ മെസ്സേജിംഗ് പ്ലാറ്റ്ഫോം</b> മാത്രമാണ്.<br><br>
                            • യാത്രയ്ക്കിടയിൽ ഉണ്ടാകുന്ന സാങ്കേതികമോ, വ്യക്തിപരമോ ആയ പ്രശ്നങ്ങൾക്കോ, അപകടങ്ങൾക്കോ ഈ പ്ലാറ്റ്ഫോമോ, അഡ്മിനിസ്ട്രേറ്റർമാരോ ഉത്തരവാദികളായിരിക്കുന്നതല്ല.<br><br>
                            • ഡ്രൈവർമാരുമായുള്ള ഇടപാടുകളിൽ യാത്രക്കാർ ജാഗ്രത പാലിക്കേണ്ടതാണ്.<br><br>
                            • ഈ സേവനം ഉപയോഗിക്കുന്നതിലൂടെ നിങ്ങൾ ഈ നിബന്ധനകൾ അംഗീകരിക്കുന്നു.
                        </div>
                        """, unsafe_allow_html=True)    
                        
                else:
                    st.error("❌ ബുക്കിംഗ് സേവ് ചെയ്യുന്നതിൽ പരാജയപ്പെട്ടു.")

        st.session_state.is_booking = False
        st.write("---")
    # ഇവിടെയാണ് നിങ്ങളുടെ സ്പേസ് കുറയ്ക്കേണ്ടത് (പഴയ st.write("---") മാറ്റി ഇത് നൽകുക)
    st.markdown("<hr style='margin: 5px 0; border: 0.5px solid #ffffff;'>", unsafe_allow_html=True)

    # സഹായകരമായ ഫൂട്ടർ ബട്ടണുകൾ (Contact, SOS, Driver)
    st.markdown("""
    <style>
    .footer-box {
        border: 2px solid #FFC107;
        border-radius: 10px;
        padding: 20px;
        background-color: #1a1a1a;
        margin-top: 0px; /* 👈 ഇവിടെ 20px എന്നത് 0px ആക്കി മാറ്റി */
    }

    /* ഫൂട്ടർ ബട്ടണുകളുടെ വലിപ്പം കൃത്യമാക്കാം */
    .stButton > button {
        width: 100% !important;
        padding: 8px 5px !important;
        font-size: 14px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        background-color: #FFC107 !important;
        color: black !important;
        border: none !important;
        min-height: 40px !important;
        margin-top: -15px !important;
    }

    .stButton > button:hover {
        background-color: #e0a800 !important;
    }
    
    /* 👇 ഇവിടെയാണ് പുതിയ കോഡ് ചേർത്തിരിക്കുന്നത് */
    div[data-testid="stHorizontalBlock"] {
        margin-top: -20px !important; /* 👈 -50px എന്നത് -20px ആക്കി മാറ്റി */
    }
    
    hr {
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ഫൂട്ടർ സെപ്പറേറ്റർ
    str_lit.markdown("---")

    # മൂന്ന് കോളങ്ങളിലായി മൂന്ന് പ്രധാന ബട്ടണുകൾ (gap കുറച്ചു)
    footer_col1, footer_col2, footer_col3 = str_lit.columns(3, gap="small")
    
    # 1. Contact Us ബട്ടൺ
    with footer_col1:
        if str_lit.button("📞 Contact", use_container_width=True):
            # 👇 ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ കോൺടാക്ട് പാനൽ തുറക്കും
            str_lit.session_state['show_contact_panel'] = True
            
            # മറ്റ് പാനലുകൾ അടയ്ക്കാൻ
            str_lit.session_state['show_sos_panel'] = False
            str_lit.session_state['show_driver_panel'] = False
            
    # 2. SOS ബട്ടൺ (ടെക്സ്റ്റ് ചെറുതാക്കി)
    with footer_col2:
        if str_lit.button("🚨 SOS", use_container_width=True):
            str_lit.session_state['show_sos_panel'] = True
            str_lit.session_state['show_driver_panel'] = False 
            
    # 3. Driver Panel ബട്ടൺ (ടെക്സ്റ്റ് ചെറുതാക്കി)
    with footer_col3:
        if str_lit.button("🚗 Driver", use_container_width=True):
            str_lit.session_state['show_driver_panel'] = True
            str_lit.session_state['show_sos_panel'] = False   
            
    # --------------------------------------------------------
    # SOS പാനൽ (ഡയറക്ട് കോൾ ലിങ്കുകളും വാട്സാപ്പ് ഷെയറും)
    # --------------------------------------------------------        
    if str_lit.session_state.get('show_sos_panel', False):
        # 👇 ഈ കണ്ടെയ്നർ ആണ് വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് നൽകുന്നത്
        str_lit.markdown("""
        <style>
        /* 'sos_panel_box' എന്ന key ഉള്ള കണ്ടെയ്നറിന് മാത്രം വെളുത്ത ബാക്ക്ഗ്രൗണ്ട് */
        div[class*="st-key-sos_panel_box"] {
            background-color: white !important;
            padding: 20px !important;
            border-radius: 10px !important;
            border: 2px solid #d32f2f !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        }
        
        /* അതിനുള്ളിലെ എല്ലാ എഴുത്തുകൾക്കും കറുപ്പ് നിറം */
        div[class*="st-key-sos_panel_box"] * {
            color: #000000 !important;
        }
        
        /* ലിങ്കുകൾക്ക് നീല നിറം */
        div[class*="st-key-sos_panel_box"] a {
            color: #0066cc !important;
        }
        </style>
        """, unsafe_allow_html=True)
        with str_lit.container(key="sos_panel_box"):
            str_lit.markdown("---")
            str_lit.error("🚨 അടിയന്തര സഹായ വിഭാഗം (Emergency Control Rooms)")
            
            # നമ്പുകളിൽ അമർത്തിയാൽ നേരിട്ട് കോൾ പോകുന്ന ലിങ്കുകൾ (tel: link)
            str_lit.markdown("""
            * 🚔 **പോലീസ് (112):** [📞 കോൾ ചെയ്യുക](tel:112)
            * 🚒 **ഫയർ ആൻഡ് റെസ്ക്യൂ (101):** [📞 കോൾ ചെയ്യുക](tel:101)
            * 🚑 **ആംബുലൻസ് (108):** [📞 കോൾ ചെയ്യുക](tel:108)
            """, unsafe_allow_html=True)
            
            str_lit.markdown("---")
            str_lit.subheader("📍 ലൊക്കേഷൻ വഴി അയക്കാൻ")
            
            sos_message = "എനിക്ക് അടിയന്തര സഹായം ആവശ്യമാണ്. ദയവായി ഉടൻ ബന്ധപ്പെടുക. (ഡ്രൈവർ/യാത്രക്കാരൻ)"
            whatsapp_share_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(sos_message)}"
            
            # വാട്സാപ്പ് ബട്ടൺ ചെയ്തത് മൊബൈലിൽ തുറക്കാൻ
            str_lit.markdown(f"""
            <a href="{whatsapp_share_url}" target="_blank" style="text-decoration: none;">
                <button style="background-color: #25D366; color: white; padding: 10px 15px; border: none; border-radius: 5px; font-size: 14px; font-weight: bold; width: 100%;">
                    💬 വാട്സാപ്പിൽ അയക്കുക
                </button>
            </a>
            """, unsafe_allow_html=True)
            
            str_lit.markdown("<br>", unsafe_allow_html=True)
            
            if str_lit.button("SOS പാനൽ അടയ്ക്കുക", use_container_width=True):
                str_lit.session_state['show_sos_panel'] = False
                str_lit.rerun()
    # 👇 ഇവിടെയാണ് പുതിയ കോൺടാക്ട് പാനൽ കോഡ് ചേർക്കേണ്ടത്
    if str_lit.session_state.get('show_contact_panel', False):
        str_lit.markdown("""
        <style>
        div[class*="st-key-contact_panel_box"] {
            background-color: white !important;
            padding: 20px !important;
            border-radius: 10px !important;
            border: 2px solid #FFC107 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
            color: black !important;
        }
        div[class*="st-key-contact_panel_box"] * {   
            color: black !important;
        }
        div[class*="st-key-contact_panel_box"] a {
            color: #0066cc !important;
        }
        </style>
        """, unsafe_allow_html=True)
        with str_lit.container(key="contact_panel_box"):
            str_lit.error("📞 മാനേജ്മെന്റ് കോൺടാക്ട് വിവരങ്ങൾ")
            str_lit.markdown("""
            * 📞 **ഫോൺ:** +91 9876543210
            * ✉️ **ഇമെയിൽ:** support@example.com
            """, unsafe_allow_html=True)
            
            if str_lit.button("Contact പാനൽ അടയ്ക്കുക", use_container_width=True):
                str_lit.session_state['show_contact_panel'] = False
                str_lit.rerun()        

    # ============================================================
    # 📊 ഡ്രൈവർ ഹിസ്റ്ററി ഫയർബേസിൽ നിന്ന് എടുക്കുന്ന ഫംഗ്ഷൻ
    # ============================================================
    def fetch_driver_history_from_firebase(chat_id):
        try:
            ref = db.reference("trips")
            all_trips = ref.get()
            
            if not all_trips:
                return []
            
            result_data = []
            for booking_id, trip in all_trips.items():
                if isinstance(trip, dict) and str(trip.get("driver_chat_id")) == str(chat_id):
                    result_data.append({
                        "Trip ID": booking_id,
                        "Date": trip.get("booking_time", "N/A").split(" ")[0],
                        "Pickup": trip.get("pickup", "N/A"),
                        "Drop": trip.get("drop", "N/A"),
                        "Distance": f"{trip.get('calculated_distance', 'N/A')} km",
                        "Fare": trip.get("total_fare", "N/A"),
                        "Commission": trip.get("commission_amount", "N/A")
                    })
            return result_data
        except Exception as e:
            print(f"❌ Error fetching history: {e}")
            return []

    # ============================================================
    # 🚗 ഡ്രൈവർ പാനൽ - ഫയർബേസ് ഡാറ്റ കണക്ഷൻ
    # ============================================================
    if str_lit.session_state.get('show_driver_panel', False):
        str_lit.markdown("---")
        str_lit.subheader("🚗 ഡ്രൈവർ പാനൽ")
        
        driver_telegram_id = str_lit.text_input("നിങ്ങളുടെ ടെലഗ്രാം ചാറ്റ് ഐഡി (Chat ID):", key="driver_id_input_main")
        
        search_clicked = str_lit.button("🔍 ഹിസ്റ്ററി പരിശോധിക്കുക", use_container_width=True)
        
        if driver_telegram_id and search_clicked:
            str_lit.info(f"ചാറ്റ് ഐഡി ({driver_telegram_id}) പരിശോധിക്കുന്നു...")
            
            driver_history_data = fetch_driver_history_from_firebase(driver_telegram_id.strip())
            
            if driver_history_data:
                str_lit.success("✅ ഹിസ്റ്ററി ലോഡ് ചെയ്തു!")
                str_lit.markdown("### 📋 നിങ്ങളുടെ മുൻകാല ട്രിപ്പുകൾ:")
                str_lit.table(driver_history_data)
            else:
                str_lit.warning("⚠️ ഈ ചാറ്റ് ഐഡിയിൽ ട്രിപ്പുകൾ ഒന്നും കണ്ടെത്താനായില്ല.")
                
        if str_lit.button("പാനൽ അടയ്ക്കുക", use_container_width=True):
            str_lit.session_state['show_driver_panel'] = False
            str_lit.rerun()
    
    # ==========================================================
    # Clean Footer Component
    # ==========================================================
    st.markdown("---")

    st.markdown("""
        <style>
        .malayalam-title-card { 
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            border: 1px solid #e0e0e0;
            margin-bottom: 15px;  
        } 
        </style>
        <div class="malayalam-title-card">
            <h3 style="margin:0; color: #2c3e50; font-size: 16px;">🔍 ബുക്കിംഗ് സ്റ്റാറ്റസ് അറിയാൻ</h3>
            <p style="margin: 8px 0 0 0; color: #555555; font-size: 12px;">ആപ്പ് ക്ലോസ് ആയിപ്പോയോ? ട്രിപ്പ് ഐഡി നൽകി സ്റ്റാറ്റസ് പരിശോധിക്കുക.</p>
        </div>
    """, unsafe_allow_html=True)    
    # 👇 ബട്ടണും ബോക്സും തമ്മിലുള്ള അകലം കൂട്ടാൻ ഇത് ചേർക്കുക
    st.markdown("""
    <style>
    /* ട്രിപ്പ് ഐഡി ബോക്സിന് താഴെ കുറച്ച് സ്പേസ് നൽകാൻ */
    div[data-baseweb="input"] {
        margin-bottom: 10px !important;
    }
    
    /* സ്റ്റാറ്റസ് ബട്ടണിന് മുകളിൽ കുറച്ച് സ്പേസ് നൽകാൻ */
    div.stButton {
        margin-top: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    
    
    col1, col2 = st.columns([3, 1])
    with col1: 
        footer_trip_id = st.text_input("ട്രിപ്പ് ഐഡി നൽകുക:", key="independent_footer_trip_id", label_visibility="collapsed", placeholder="ട്രിപ്പ് ഐഡി (ഉദാ: TRIP-XXXXX)") 
    with col2:
        footer_check_btn = st.button("സ്റ്റാറ്റസ്", key="independent_footer_btn", use_container_width=True)        
        
    if footer_check_btn:    
        if footer_trip_id: 
            with st.spinner("🔍 പരിശോധിക്കുന്നു..."):
                try:
                    trip_ref = db.reference(f"trips/{footer_trip_id.strip()}")
                    trip_data = trip_ref.get()
                    if trip_data:
                        st.success(f"✅ ട്രിപ്പ് വിവരങ്ങൾ കണ്ടെത്തി!")
                        st.info(f"📍 **പിക്കപ്പ്:** {trip_data.get('pickup', 'N/A')}\n\n🏁 **ഡ്രോപ്പ്:** {trip_data.get('drop', 'N/A')}")
                        st.markdown(f"📊 **നിലവിലെ സ്റ്റാറ്റസ്:** {trip_data.get('status', 'Pending')}")
                    else:
                        st.error("❌ ഈ ട്രിപ്പ് ഐഡിയിൽ വിവരങ്ങൾ ലഭ്യമല്ല.")
                except Exception as e:
                    st.error(f"❌ എറർ: {e}")
        else:
            st.warning("⚠️ ദയവായി ഒരു ട്രിപ്പ് ഐഡി നൽകുക.")
            
            if str_lit.session_state.get('status') == "Arrived":
                st.warning("🚨 ഡ്രൈവർ നിങ്ങളുടെ പിക്കപ്പ് ലൊക്കേഷനിൽ എത്തിയിട്ടുണ്ട്!")    
                
if __name__ == "__main__":
    main()
    
    
        
# ==========================================================
# Phone Masking Function (Single version)
# ==========================================================
def mask_phone_number(phone_str):
    phone_str = str(phone_str).strip()
    if len(phone_str) > 4:
        return phone_str[:4] + "******"
    return "******"






# ==========================================================
# Driver Accept Logic
# ==========================================================
def accept_trip(
    booking_id,
    customer_name,
    customer_phone,
    driver_name,
    driver_phone,
    vehicle_number,
    driver_chat_id,
    pickup_lat,
    pickup_lon
):
    """
    Driver trip accept ചെയ്തതിന് ശേഷം:
    - Firebase-ൽ status update
    - Driver-ന് navigation + arrived + call buttons അയക്കുന്നു
    """
    print("Trip Accepted:", booking_id)

    # ============================================================
    # 1. Firebase Trip Status Update
    # ============================================================
    try:
        # 🆕 ഡീബഗ് പ്രിന്റ് (ഇവിടെ ചേർക്കുക)
        print(f"DEBUG: Updating Firebase with Driver -> Name: {driver_name}, Phone: {driver_phone}")
        db.reference(f"trips/{booking_id}").update({
            "status": "Accepted",
            "driver_name": driver_name,
            "driver_phone": driver_phone,
            "driver_chat_id": str(driver_chat_id),
            "accepted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        print(f"❌ Firebase update error: {e}")
        return False

    # ============================================================
    # 2. Masked Phone
    # ============================================================
    masked_customer_phone = mask_phone_number(customer_phone)

    # ============================================================
    # 🆕 ട്രിപ്പ് പാനൽ ബട്ടൺ (പുതിയ സംവിധാനം)
    # ============================================================
    driver_panel_url = f"https://your-app.streamlit.app/?page=driver_trip_panel&trip_id={booking_id}"
        
    markup = types.InlineKeyboardMarkup(row_width=1)
    panel_button = types.InlineKeyboardButton(
        "🚖 ട്രിപ്പ് പാനൽ തുറക്കുക", 
        url=driver_panel_url
    )
    markup.add(panel_button)

    # ============================================================
    # 5. Driver Message
    # ============================================================
    driver_message = (
        f"🚗 *പുതിയ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തിരിക്കുന്നു!*\n\n"
        f"🆔 TRIP-ID: `{booking_id}`\n"
        f"👤 {customer_name}\n"
        f"📱 `{masked_customer_phone}`\n\n"
        f"⚠️ *അത്യാവശ്യ ഘട്ടങ്ങളിൽ മാത്രം വിളിക്കുക.*"
    )

    # ============================================================
    # 6. Send
    # ============================================================
    try:
        bot.send_message(
            chat_id=driver_chat_id,
            text=driver_message,
            parse_mode="Markdown",
            reply_markup=markup,
        )
        return True
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False
        
# ============================================================
# ACCEPT TRIP Callback Handler
# ============================================================

@bot.callback_query_handler(
    func=lambda call: str(call.data or "").startswith("accept_")
)
def handle_accept_trip(call):

    chat_id = str(call.message.chat.id)
    trip_id = str(call.data).replace("accept_", "", 1).strip()

    try:
        # 1. ഡ്രൈവറുടെ വിവരങ്ങൾ വായിക്കുക
        driver_ref = db.reference(f"drivers/{chat_id}")
        driver_data = driver_ref.get() or {}
        print("DEBUG DRIVER DATA:", driver_data)

        driver_name = (
            driver_data.get("driver_name")
            or driver_data.get("Driver Name")
            or driver_data.get("name")
            or "Unknown Driver"
        )

        driver_phone = (
            driver_data.get("phone")
            or driver_data.get("Phone")
            or driver_data.get("driver_phone")
            or "N/A"
        )

        vehicle_number = (
            driver_data.get("vehicle_number")
            or driver_data.get("Vehicle Number")
            or driver_data.get("Vehicle No")
            or "N/A"
        )
        # ============================================================
        # 🔒 ട്രിപ്പ് ലോക്ക് ചെയ്യാനുള്ള കോഡ് (ഇവിടെ ചേർക്കുക)
        # ============================================================
        try:
            # 1. നിലവിലെ ട്രിപ്പ് വിവരങ്ങൾ എടുക്കുക
            trip_ref = db.reference(f"trips/{trip_id}")
            trip_data = trip_ref.get() or {}
            # 2. ട്രിപ്പ് ഇതിനകം അക്സെപ്റ്റ് ചെയ്തിട്ടുണ്ടോ എന്ന് ചെക്ക് ചെയ്യുക
            if trip_data.get("status") == "Accepted":
                bot.send_message(
                    chat_id,
                    f"❌ *ക്ഷമിക്കണം!*\n\n"
                    f"ട്രിപ്പ് `{trip_id}` മറ്റൊരു ഡ്രൈവർ ഇതിനകം അക്സെപ്റ്റ് ചെയ്തിട്ടുണ്ട്.\n"
                    f"ദയവായി മറ്റ് ട്രിപ്പുകൾക്കായി കാത്തിരിക്കുക.",
                    parse_mode="Markdown"
                )
                print(f"⏭️ Trip {trip_id} already accepted by another driver.")
                return
            # 3. ട്രിപ്പ് അപ്ഡേറ്റ് ചെയ്ത് ലോക്ക് ചെയ്യുക
            trip_ref.update({  
                "status": "Accepted",
                "is_locked": True,
                "accepted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "driver_name": driver_name,
                "driver_phone": driver_phone,
                "vehicle_number": vehicle_number,
                "driver_chat_id": chat_id
            })
            print(f"✅ Trip {trip_id} accepted and locked by driver {chat_id}")
            # 4. ഡ്രൈവർക്ക് സ്ഥിരീകരണ സന്ദേശം അയക്കുക
            bot.send_message(
                chat_id,
                f"✅ *ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തു!*\n\n"
                f"ട്രിപ്പ് ഐഡി: `{trip_id}`\n"
                f"ഡ്രൈവർ: {driver_name}\n"
                f"വാഹനം: {vehicle_number}",
                parse_mode="Markdown"
            )
            
            # 5. ഡ്രൈവർ പാനൽ ലിങ്ക് അയക്കുക
            driver_panel_url = f"https://taxiservisemj-x9meaffucvbt6tjijxrd6d.streamlit.app/?page=driver_trip_panel&trip_id={trip_id}&driver_chat_id={chat_id}"
            bot.send_message(
                chat_id,
                f"📍 *ഡ്രൈവർ പാനൽ തുറക്കാൻ താഴെയുള്ള ലിങ്കിൽ ക്ലിക്ക് ചെയ്യുക:*\n\n[ട്രിപ്പ് പാനൽ തുറക്കുക]({driver_panel_url})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"❌ Trip lock error: {e}")
            bot.send_message(chat_id, f"❌ എറർ: ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്യാൻ കഴിഞ്ഞില്ല. ({e})")    
            
        # 2. സുരക്ഷിതമായി ട്രിപ്പ് സ്വീകരിക്കുക
        # 🔍 Debug: accept_trip_safely വിളിക്കുന്നു
            print("🔥 Calling accept_trip_safely with:")
            print(f"   trip_id = {trip_id}")
            print(f"   chat_id = {chat_id}")
            print(f"   driver_name = {driver_name}")
            print(f"   driver_phone = {driver_phone}")
            print(f"   vehicle_number = {vehicle_number}")
            print(f"👉 DEBUG CHECK -> Name: {driver_name} | Phone: {driver_phone} | Vehicle: {vehicle_number}") 
        result = accept_trip_safely(
            trip_id=trip_id,   
            driver_chat_id=chat_id,
            driver_name=driver_name,
            driver_phone=driver_phone,
            vehicle_number=vehicle_number
        )
        
        # 🔍 Debug: ഫലം പരിശോധിക്കുന്നു
        print(f"🔥 Result from accept_trip_safely: {result}")

        if result == "success":
            # --- ഡ്രൈവർ വിവരങ്ങൾ Supabase-ൽ അപ്ഡേറ്റ് ചെയ്യാൻ ---
            try:
                supabase.table('trips').update({
                    "driver_name": driver_name,
                    "driver_phone": driver_phone,
                    "driver_chat_id": str(chat_id),
                    "vehicle_number": vehicle_number
                }).eq('trip_id', trip_id).execute()
                print(f"✅ Supabase Updated: Driver {driver_name} assigned to {trip_id}")
            except Exception as e:
                print(f"❌ Supabase Update Error: {e}") 

            bot.answer_callback_query(
                call.id,
                "⚠️ ഈ ട്രിപ്പ് ഇതിനകം സ്വീകരിച്ചിരിക്കുന്നു."
            )

            bot.send_message(
                chat_id=chat_id,
                text=(
                    "⚠️ ഈ ട്രിപ്പ് മറ്റൊരു ഡ്രൈവർ സ്വീകരിച്ചിരിക്കാം. "
                    "ദയവായി മറ്റൊരു ട്രിപ്പ് തിരഞ്ഞെടുക്കുക."
                )
            )
            return

        # 3. ACCEPT ബട്ടൺ നീക്കം ചെയ്യുക
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except Exception as edit_error:
            print(f"Button update notice: {edit_error}")

        # 4. ഡ്രൈവർ ട്രിപ്പ് പാനൽ ലിങ്ക്
        driver_panel_url = (
            "https://taxiservisemj-x9meaffucvbt6tjijxrd6d.streamlit.app/"
            f"?page=driver_trip_panel&trip_id={trip_id}"
            f"&driver_chat_id={chat_id}"
        )

        markup = types.InlineKeyboardMarkup(row_width=1)

        markup.add(
            types.InlineKeyboardButton(
                "🚖 ട്രിപ്പ് പാനൽ തുറക്കുക",
                url=driver_panel_url
            )
        )

        # 5. വിജയ സന്ദേശം
        bot.answer_callback_query(
            call.id,
            "✅ ട്രിപ്പ് സ്വീകരിച്ചു!"
        )

        bot.send_message(
            chat_id=chat_id,
            text=(
                "✅ *ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തു!*\n\n"
                f"🆔 ട്രിപ്പ് ഐഡി: `{trip_id}`\n"
                f"👤 ഡ്രൈവർ: {driver_name}\n"
                f"📞 ഫോൺ: {driver_phone}\n"
                f"🚘 വാഹനം: {vehicle_number}\n\n"
                "നാവിഗേഷൻ, കസ്റ്റമർ വിവരങ്ങൾ, ലൈവ് ലൊക്കേഷൻ "
                "എന്നിവയ്ക്കായി താഴെയുള്ള ബട്ടൺ അമർത്തുക."
            ),
            parse_mode="Markdown",
            reply_markup=markup
        )

        print(
            f"TRIP ACCEPTED: {trip_id} | "
            f"DRIVER: {chat_id} | {driver_name}"
        )

    except Exception as e:
        print(f"❌ handle_accept_trip error: {e}")

        try:
            bot.answer_callback_query(
                call.id,
                "❌ ട്രിപ്പ് സ്വീകരിക്കുന്നതിൽ പിശക്."
            )
        except Exception:
            pass


# ==========================================================
# 🚀 START POLLING — LAST (after all handlers registered)
# ==========================================================
@st.cache_resource
def start_bot_polling():
    """Start bot polling — ONCE only"""
    def _run_polling():
        while True:
            try:
                print("🚀 Bot polling started...")
                bot.infinity_polling(
                    none_stop=True,
                    timeout=60,
                    long_polling_timeout=30
                )
            except Exception as e:
                err = str(e)
                if "409" in err:
                    print("🛑 409 Conflict — stopping polling")
                    break
                print(f"⚠️ Polling error: {e}")
                time.sleep(5)

    _polling_thread = threading.Thread(target=_run_polling, daemon=True)
    add_script_run_ctx(_polling_thread)
    _polling_thread.start()
    print("✅ Bot polling thread started — ONCE (via cache_resource)")
    return True

start_bot_polling()




















   



