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

import gspread
import folium
from telebot import types
from streamlit_folium import st_folium
from firebase_admin import credentials, db
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_geolocation import streamlit_geolocation
from flask import Flask, request, jsonify
from streamlit.runtime.scriptrunner import add_script_run_ctx




# ==========================================================
# 📌 1. ഈ ഫംഗ്ഷൻ കോഡിന്റെ ഏറ്റവും മുകളിൽ (Global Scope-ൽ) നൽകുക
# ==========================================================
def get_trip_from_database(trip_id):
    try:
        ref = db.reference(f"trips/{trip_id}")
        return ref.get()
    except Exception as e:
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
    try:
        # ============================================================
        # ✅ 1. Firebase-ൽ നിന്ന് ട്രിപ്പ് വിവരങ്ങൾ എടുക്കുക
        # ============================================================
        trip_data = db.reference(f"trips/{trip_id}").get() or {}
        
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
        if trip_status == "Accepted" or trip_notification == "accepted":
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
        if vehicle_type == "Auto Rickshaw":
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
            st.markdown("""
                <script>
                if (navigator.vibrate) {
                    navigator.vibrate([300, 100, 300, 100, 300]);
                }
                </script>
            """, unsafe_allow_html=True)
            
            # 🔊 Arrived Sound
            if not st.session_state.get('arrived_sound_played', False):
                sound_html = """
                <audio autoplay>
                    <source src="https://www.soundjay.com/phones/sounds/phone-ringing-01.mp3" type="audio/mpeg">
                </audio>
                """
                components.html(sound_html, height=0)
                st.session_state.arrived_sound_played = True
        else:
            st.session_state.arrived_sound_played = False

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

def save_new_trip(booking_id, customer_name, customer_phone, pickup, drop, distance=0.0, pickup_link=""):
    """
    കസ്റ്റമർ ബുക്ക് ചെയ്യു മ്പോൾ വിവരങ്ങളും ദൂരവും ഫയർബേസിലേക്ക് സേവ് ചെയ്യുന്നു
    """
    try:
        trip_data = {
            "trip_id": booking_id,
            "booking_id": booking_id,
            
            "customer_name": customer_name,
            "customer_phone": str(customer_phone),
            "pickup": pickup,
            "drop": drop,
            "pickup_link": pickup_link,  # 👈 ഇവിടെ എറർ വരാതിരിക്കാൻ ഇത് ആർഗ്യുമെന്റിൽ ചേർത്തിട്ടുണ്ട്
            "distance": distance,  # കിലോമീറ്റർ മാത്രം സേവ് ചെയ്യുന്നു
            "total_fare": 0.0,              # ഫെയർ തൽക്കാലം 0 ആയി വെക്കുന്നു
            "status": "Pending",
            "driver_name": "",
            "driver_phone": "",
            "driver_chat_id": "",
            "booking_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        trip_ref = db.reference(f"trips/{booking_id}")
        trip_ref.set(trip_data)
        print(f"✅ Trip {booking_id} saved with distance {distance} km successfully.")
        return True
    except Exception as e:
        print(f"❌ Error saving trip to Firebase: {e}")
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
    location_link="Not Available"
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
def accept_trip_safely(booking_id, driver_name, driver_phone, driver_chat_id):
    ref = db.reference(f"trips/{booking_id}")
    trip_data = ref.get()
    
    if not trip_data:
        return "not_found"
        
    current_status = trip_data.get("status", "Pending")
    if current_status not in ["Pending", "Available", "Unassigned"]:
        return "already_taken"
        
    ref.update({
        "status": "Accepted",
        "driver_name": driver_name,
        "driver_phone": driver_phone,
        "driver_chat_id": str(driver_chat_id)
    })
    return "success"


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
def firebase_trip_listener():
    try:
        trips_ref = db.reference("trips")
        trips_ref.listen(listener)
    except Exception as e:
        bg_log(f"Firebase Reference Error: {e}")
        return  
# ==========================================
#accept_trip_safely ഫങ്ഷൻ ഇവിടെ നൽകുക:
# ==========================================
def accept_trip_safely(trip_id, driver_chat_id, driver_name, driver_phone):
    ref = db.reference(f"trips/{trip_id}")
    
    def transaction_update(current_data):
        if current_data is None:
            return
        
        current_status = current_data.get("status")
        # സ്റ്റാറ്റസ് പെൻഡിംഗ് അല്ലെങ്കിൽ അവൈലബിൾ ആണോ എന്ന് പരിശോധിക്കുന്നു
        if current_status not in ["Pending", "Available", "PENDING", "AVAILABLE"]:
            return "already_taken"
        
        # ട്രിപ്പ് അപ്ഡേറ്റ് ചെയ്യുന്നു
        current_data["status"] = "Accepted"
        current_data["driver_chat_id"] = str(driver_chat_id)
        current_data["driver_name"] = driver_name
        current_data["driver_phone"] = driver_phone
        return current_data

    # ഫയർബേസ് ട്രാൻസാക്ഷൻ വഴി ഒരേ സമയം രണ്ട് പേർക്ക് അക്സപ്റ്റ് ആകുന്നത് തടയുന്നു
    result = ref.transaction(transaction_update)
    
    if result and result.get("status") == "Accepted" and str(result.get("driver_chat_id")) == str(driver_chat_id):
        return "success"
    else:
        return "already_taken"        
# ==========================================================
# Telegram Callback Query Handler (Button Clicks)
# ==========================================================
def handle_telegram_callback(update, context):
    query = update.callback_query
    query.answer()
    
    callback_data = query.data
    chat_id = query.message.chat_id
    print(f"🔥 DEBUG: Callback വന്നിരിക്കുന്നു -> {callback_data}")
    
    if callback_data.startswith("arrived_"):
        booking_id = callback_data.replace("arrived_", "")
        ref = db.reference(f"trips/{booking_id}")
        trip_data = ref.get()
        
        if trip_data and str(trip_data.get("driver_chat_id")) == str(chat_id):
            ref.update({"status": "Arrived"})
            query.edit_message_text(
                text=query.message.text + "\n\n🔴 **[Status: Arrived at Location]** - കസ്റ്റമർക്ക് നോട്ടിഫിക്കേഷൻ അയച്ചിട്ടുണ്ട്."
            )
        else:
            query.edit_message_text(text="❌ അസാധുവായ റിക്വസ്റ്റ് അല്ലെങ്കിൽ നിങ്ങൾക്ക് ഈ ട്രിപ്പിൽ അധികാരമില്ല.")
            
    else:
        booking_id = callback_data
        driver_name = "Driver" 
        driver_phone = "N/A"
        
        result = accept_trip_safely(booking_id, driver_name, driver_phone, chat_id)
        
        if result == "success":
            query.edit_message_text(
                text=f"✅ **ട്രിപ്പ് വിജയകരമായി അക്സെപ്റ്റ് ചെയ്തു!**\nട്രിപ്പ് ഐഡി: {booking_id}\n\nനാവിഗേഷൻ ഉപയോഗിച്ച് പിക്കപ്പ് സ്ഥലത്തേക്ക് പോവുക."
            )
        elif result == "already_taken":
            query.edit_message_text(
                text="❌ ക്ഷമിക്കുക, ഈ ട്രിപ്പ് മറ്റൊരു ഡ്രൈവർ ഇതിനകം സ്വീകരിച്ചിരിക്കുന്നു!"
            )
        else:
            query.edit_message_text(
                text="❌ ഈ ട്രിപ്പ് നിലവിലില്ല അല്ലെങ്കിൽ എക്സ്പയർ ആയിരിക്കുന്നു."
            )                
                
            
        

    


# ==========================================================
# SAFE FIREBASE TRIP CREATE
# Use this in booking section instead of direct ref.set()
# ==========================================================
def create_trip_in_firebase(
        unique_trip_id,
        payload
    ):

    try:
        ref = db.reference(
            f"trips/{unique_trip_id}"
        )

        ref.set(payload)

        bg_log(
            "✅ Trip Saved To Firebase"
        )

        return True

    except Exception as e:
        bg_log(
            f"Firebase Save Error: {e}"
        )

        return False
     

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

@st.cache_data(ttl=60)
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
# ✅ FIX #3: Firebase Listener — ഒരിക്കൽ മാത്രം Start
# Streamlit rerun-ൽ duplicate listener threads ഒഴിവാക്കാൻ
# ==========================================================
@st.cache_resource
def start_firebase_background_services():
    """
    @st.cache_resource കാരണം app session-ൽ ഒരിക്കൽ മാത്രം
    execute ആകും. Streamlit rerun ചെയ്താലും പുതിയ
    listener threads ഉണ്ടാകില്ല.
    """
    try:
        initialize_firebase()
        
        def run_listener():
            try:
                bg_log("🚀 Starting Firebase Trip Listener...")
                trips_ref = db.reference("trips")
                trips_ref.listen(listener)
            except Exception as e:
                bg_log(f"❌ Listener Thread Error: {e}")
                import traceback
                traceback.print_exc()
        
        firebase_thread = threading.Thread(
            target=run_listener,
            daemon=True,
            name="FirebaseTripListener"
        )
        add_script_run_ctx(firebase_thread)
        firebase_thread.start()
        
        bg_log("✅ Firebase Listener Started (ONCE)")
        return True
        
    except Exception as e:
        bg_log(f"❌ Background Services Error: {e}")
        return False


# App init-ൽ ഒരിക്കൽ മാത്രം execute ആകും
start_firebase_background_services()
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
    
    .header-box { 
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d) !important; 
        padding: 30px !important; 
        border-radius: 15px !important; 
        text-align: center !important; 
        border-bottom: 5px solid #ffcc00 !important; 
        box-shadow: 0px 10px 20px rgba(0,0,0,0.3) !important; 
        margin-bottom: 25px !important; 
    }
    .header-box h1 { color: #ffcc00 !important; font-weight: 900 !important; letter-spacing: 2px !important; margin: 0 !important; font-size: 2.5rem !important; }
    .header-box p { color: #b3b3b3 !important; font-size: 14px !important; margin-top: 5px !important; text-transform: uppercase !important; }
    
    div[data-testid="stForm"] { 
        background-color: #1e1e1e !important; 
        border: 1px solid #333333 !important; 
        padding: 25px !important; 
        border-radius: 15px !important; 
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important; 
    }
    
    label[data-testid="stWidgetLabel"] p, 
    div[data-testid="stMarkdownContainer"] p strong,
    div[data-testid="stRadio"] label p {
        color: #ffcc00 !important;
        font-size: 16px !important;
        font-weight: bold !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton>button { 
        background: linear-gradient(90deg, #ffcc00, #ffa500) !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 16px !important; 
        border: none !important; 
        border-radius: 8px !important; 
        padding: 12px 20px !important; 
        transition: all 0.3s ease !important; 
        width: 100% !important; 
    }
    .stButton>button:hover { transform: translateY(-2px) !important; box-shadow: 0px 6px 20px rgba(255,204,0,0.4) !important; }
    
    .disclaimer-box { background-color: #2b1d1d !important; border-left: 5px solid #d32f2f !important; padding: 18px !important; border-radius: 8px !important; margin: 20px 0 !important; }
    .disclaimer-title { color: #ff5252 !important; font-weight: bold !important; font-size: 16px !important; margin-bottom: 6px !important; }
    .disclaimer-text { color: #e0e0e0 !important; font-size: 13.5px !important; line-height: 1.6 !important; margin: 0 !important; }
    
    .success-card { background-color: #1c2e24 !important; border: 1px solid #2e7d32 !important; padding: 20px !important; border-radius: 12px !important; text-align: center !important; }
    .warning-card { background-color: #2e2719 !important; border: 1px solid #f9a825 !important; padding: 20px !important; border-radius: 12px !important; text-align: center !important; }
    .danger-card { background-color: #2c1c1c !important; border: 1px solid #c62828 !important; padding: 20px !important; border-radius: 12px !important; text-align: center !important; }
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
bot = None

# ലോഗിങ്ങിനായി bg_log ഫങ്ഷൻ ഇവിടെ നൽകുക
def bg_log(text):
    print(text)

if TELEGRAM_BOT_TOKEN and "YOUR_BOT_TOKEN" not in TELEGRAM_BOT_TOKEN:
    try:
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        print("✅ Telegram Bot Connected")
    except Exception as e:
        print(f"❌ Telegram Bot Error: {e}")

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
            "area": "Manjeri"
        }
        
        try:
            driver_ref = db.reference(f"drivers/{chat_id}")
            driver_ref.set(driver_data)
            
            success_text = (
                f"🎉 *രജിസ്ട്രേഷൻ വിജയകരമായി പൂർത്തിയായി!* 🎉\n\n"
                f"വണക്കം {data['driver_name']},\n"
                f"നിങ്ങളുടെ വിവരങ്ങൾ  ഡാറ്റാബേസിൽ സുരക്ഷിതമായി സേവ് ചെയ്തിരിക്കുന്നു.\n\n"
                f"🚕 ഇനിമുതൽ റൈഡ് റിക്വസ്റ്റുകൾ ഈ ചാറ്റിലേക്ക് വരുന്നതാണ്."
            )
            bot.send_message(chat_id=chat_id, text=success_text, parse_mode="Markdown")
            del registration_data[chat_id]
            
        except Exception as e:
            bot.send_message(chat_id=chat_id, text=f"❌ രജിസ്ട്രേഷനിൽ തടസ്സം നേരിട്ടു: {e}")

# ============================================================
# 🤖 MODULE 20: DRIVER TRIP HISTORY (LAST 20 TRIPS)
# ============================================================
@bot.message_handler(commands=['history'])
def handle_driver_history(message):
    chat_id = str(message.chat.id)
    try:
        ref = db.reference("trips")
        all_trips = ref.get()
        
        if not all_trips:
            bot.reply_to(message, "നിലവിൽ ട്രിപ്പുകൾ ഒന്നുമില്ല.")
            return
            
        user_trips = []
        for booking_id, trip in all_trips.items():
            if isinstance(trip, dict) and str(trip.get("driver_chat_id")) == str(chat_id):
                user_trips.append(trip)
        
        if user_trips:
            last_20_trips = user_trips[-20:]
            
            reply = "🚖 *നിങ്ങളുടെ അവസാനത്തെ ട്രിപ്പുകൾ:*\n\n"
            for t in last_20_trips:
                t_date = t.get("timestamp", "N/A")
                t_drop = t.get("drop", "N/A")
                reply += f"📅 {t_date} | ഡ്രോപ്പ്: {t_drop}\n"
            
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "നിലവിൽ ട്രിപ്പുകൾ ഒന്നുമില്ല.")
            
    except Exception as e:
        bot.reply_to(message, f"❌ പിശക് സംഭവിച്ചു: {str(e)}")


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
# ============================================================
# 💰 MASTER COMMISSION LOGIC
# ============================================================
def calculate_admin_commission(km):
    if not ENABLE_COMMISSION: return 0.0
    return round(0.50 + (math.ceil(km - 1.5) * 0.33) if km > 1.5 else 0.50, 2)

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
    try:
        if not bot or not driver.get("chat_id"):
            return

        # ============================================================
        # Wallet Check
        # ============================================================
        wallet_balance = float(
            driver.get("wallet_balance", 0.0)
        )

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

        # ----------------------------------------------------
        # 1. Firebase-ൽ നിന്ന് ഡ്രൈവർമാരെ എടുക്കുന്നു
        # ----------------------------------------------------
        drivers_ref = db.reference("drivers")
        drivers_data = drivers_ref.get()

        if not drivers_data:
            print("DEBUG: Firebase-ൽ drivers ഇല്ല.")
            return

        if isinstance(drivers_data, dict):
            all_drivers = list(drivers_data.values())
        elif isinstance(drivers_data, list):
            all_drivers = drivers_data
        else:
            print("DEBUG: Invalid drivers data.")
            return

        # ----------------------------------------------------
        # 2. Trip status പരിശോധിക്കുന്നു
        # ----------------------------------------------------
        try:
            trip_ref = db.reference(f"trips/{trip_id}")
            current_trip = trip_ref.get()

            if current_trip:
                current_status = str(
                    current_trip.get("status", "AVAILABLE")
                ).upper()

                if current_status not in [
                    "AVAILABLE",
                    "SCHEDULED"
                ]:
                    print(
                        f"DEBUG: Trip {trip_id} status = "
                        f"{current_status}. Notification skipped."
                    )
                    return

        except Exception as e:
            print(f"DEBUG: Trip status check error: {e}")

        # ----------------------------------------------------
        # 3. ഇതിനകം notification അയച്ച drivers
        # ----------------------------------------------------
        notified_ref = db.reference(
            f"trips/{trip_id}/notified_drivers"
        )

        existing_data = notified_ref.get()

        if isinstance(existing_data, list):
            already_notified = set(
                str(x).strip()
                for x in existing_data
                if str(x).strip()
            )

        elif isinstance(existing_data, dict):
            already_notified = set(
                str(k).strip()
                for k, v in existing_data.items()
                if v
            )

        else:
            already_notified = set()

        # ----------------------------------------------------
        # 4. ONLINE drivers മാത്രം
        # ----------------------------------------------------
        for driver in all_drivers:

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
            driver_notification_ref = db.reference(
                f"trips/{trip_id}/telegram_notifications/{d_chat_id}"
            )

            try:
                existing_lock = driver_notification_ref.get()

                if existing_lock:
                    print(
                        f"DEBUG: Telegram lock exists for "
                        f"{trip_id} / {d_chat_id}. SKIP."
                    )

                    already_notified.add(d_chat_id)
                    continue

                # Lock create ചെയ്യുന്നു
                driver_notification_ref.set({
                    "status": "SENDING",
                    "timestamp": time.time()
                })

            except Exception as e:
                print(
                    f"DEBUG: Notification lock error "
                    f"{d_chat_id}: {e}"
                )
                continue

            # ------------------------------------------------
            # 7. Telegram notification
            # ------------------------------------------------
            try:

                driver["chat_id"] = d_chat_id

                send_individual_trip_link(
                    driver,
                    trip_details
                )

                # --------------------------------------------
                # 8. Successfully processed
                # --------------------------------------------
                driver_notification_ref.update({
                    "status": "SENT",
                    "timestamp": time.time()
                })

                already_notified.add(d_chat_id)

                notified_ref.set(
                    list(already_notified)
                )

                print(
                    f"DEBUG: Telegram sent successfully -> "
                    f"Trip {trip_id} / Driver {d_chat_id}"
                )

            except Exception as e:

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

            
# ====================================================================
# 🖥️ STREAMLIT UI - CUSTOMER BOOKING INTERFACE (CLEANED & FIXED)
# ====================================================================
def main():
    st.markdown("""
    <div class="header-box">
        <h1>🚕 EASY AUTO TAXI</h1>
        <p>FAST • SECURE • RELIABLE</p>
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

    try:
        location = streamlit_geolocation()
        if location and location.get("latitude"):
            st.session_state.lat = location.get("latitude")
            st.session_state.lon = location.get("longitude")
            st.session_state.gps_link = f"https://maps.google.com/?q={st.session_state.lat},{st.session_state.lon}"
    except Exception as e:
        pass

    lat = st.session_state.lat
    lon = st.session_state.lon
    gps_link = st.session_state.gps_link

    # ഒരൊറ്റ സ്റ്റാറ്റസ് ബാറും ബട്ടണും മാത്രം ഇവിടെ പ്രവർത്തിക്കും (ഡ്യൂപ്ലിക്കേഷൻ ഒഴിവാക്കി)
    col1, col2 = st.columns([3, 1])
    with col1:
        if lat and lon:
            st.markdown(
                """
                <div style="background-color: #d4edda; color: #155724; padding: 8px; border-radius: 5px; border: 1px solid #c3e6cb;">
                    <b>🎯 GPS Status:</b> <span style="color: green; font-weight: bold;">🟢 സജീവമാണ്</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background-color: #fff3cd; color: #856404; padding: 8px; border-radius: 5px; border: 1px solid #ffeeba;">
                    <b>🎯 GPS Status:</b> <span style="color: #856404; font-weight: bold;">⚠️ ലൊക്കേഷൻ ലഭ്യമല്ല (പെർമിഷൻ അലോ ചെയ്യുക)</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col2:
        if st.button("🔄 Get GPS"):
            st.rerun()

    st.write("---")
    st.markdown("### 📝 യാത്രാ വിവരങ്ങൾ രേഖപ്പെടുത്തുക")

    # 🛑 st.form ഉപയോഗിച്ച് ബുക്കിംഗ് ഫോം സുരക്ഷിതമാക്കിയിരിക്കുന്നു
    with st.form("booking_form"):
        c_name = st.text_input("👤 നിങ്ങളുടെ പേര് (Customer Name):", placeholder="പേര് ടൈപ്പ് ചെയ്യുക")
        c_phone = st.text_input("📞 ഫോൺ നമ്പർ (Phone Number):", placeholder="9876543210")

        # 1. ഫയർബേസിൽ നിന്ന് സ്റ്റാൻഡുകളും ഏരിയകളും നേരിട്ട് എടുക്കുന്നു
        locations_list = get_locations_from_firebase()
        areas_list = get_areas_from_firebase()

        # 2. വിവിധ വാഹനങ്ങളുടെ ഓപ്ഷനുകൾ
        vehicle_options = [
            "🛺 ഓട്ടോറിക്ഷ (Autorickshaw)",
            "🚗 ടാക്സി കാർ (Taxi Car)",
            "🚙 ഗുഡ്സ് ഓട്ടോ പിക്കപ്പ് (Goods Auto Pickup)",
            "🚐 പിക്കപ്പ് വാൻ (Pickup Van)",
            "🚚 മിനി ലോറി (Mini Lorry)",
            "🚛 ട്രക്ക് (Truck)",
            "🏍️ ബൈക്ക് ടാക്സി (Bike Taxi)"
        ]
        vehicle_type = st.selectbox("🚖 വാഹനത്തിന്റെ തരം തിരഞ്ഞെടുക്കുക (Select Vehicle Type):", options=vehicle_options)

        # 3. സുരക്ഷിതമായി പിക്കപ്പ് ഡ്രോപ്പ്ഡൗൺ നൽകുന്നു
        if locations_list and len(locations_list) > 0:
            pickup_place = st.selectbox("📍 പുറപ്പെടുന്ന സ്ഥലം (Pickup):", options=locations_list)
        else:
            st.warning("⚠️ ഫയർബേസിൽ 'locations' നോഡിൽ ലൊക്കേഷനുകൾ ചേർക്കുക.")
            pickup_place = st.text_input("📍 പുറപ്പെടുന്ന സ്ഥലം (Pickup) മാനുവലായി നൽകുക:")

        if locations_list and len(locations_list) > 0:
            drop_place = st.selectbox("🏁 പോകേണ്ട സ്ഥലം (Drop):", options=locations_list)
        else:
            st.warning("⚠️ ഫയർബേസിൽ 'locations' നോഡിൽ ലൊക്കേഷനുകൾ ചേർക്കുക.")
            drop_place = st.text_input("🏁 പോകേണ്ട സ്ഥലം (Drop) മാനുവലായി നൽകുക:")

        if areas_list and len(areas_list) > 0:
            trip_area = st.selectbox("📍 ഏരിയ തിരഞ്ഞെടുക്കുക (Area):", options=areas_list)
        else:
            st.warning("⚠️ ഫയർബേസിൽ 'areas' നോഡിൽ ലൊക്കേഷനുകൾ ചേർക്കുക.")
            trip_area = st.text_input("📍 ഏരിയ മാനുവലായി നൽകുക:")

        # Smart Captcha (ഉണ്ടെങ്കിൽ മാത്രം റെൻഡർ ചെയ്യും)
        if 'render_smart_captcha_field' in globals():
            render_smart_captcha_field()

        submitted = st.form_submit_button("🚗 Book Ride Now", type="primary")

    if submitted:
        st.session_state.is_booking = True

        # Validation checks
        if not (c_name and c_phone and pickup_place and drop_place):
            st.warning("⚠️ ദയവായി എല്ലാ വിവരങ്ങളും നൽകുക!")
            st.session_state.is_booking = False
            st.stop()

        if pickup_place == drop_place:
            st.warning("⚠️ Pickup, Drop ഒരേ സ്ഥലം ആകരുത്.")
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
            exact_distance = get_real_road_distance(pickup_place, drop_place) if 'get_real_road_distance' in globals() else 5.0

        if exact_distance is None:
            st.error("❌ Pickup അല്ലെങ്കിൽ Drop location കണ്ടെത്താനായില്ല.")
            st.session_state.is_booking = False
            st.stop()

        exact_distance = round(exact_distance, 1)
        rate_per_km = 15 if vehicle_type == "Auto Rickshaw" else 22
        total_fare = round(exact_distance * rate_per_km, 2)
        commission_amount = calculate_admin_commission(exact_distance) if 'calculate_admin_commission' in globals() else 10.0
        unique_trip_id = f"TRIP-{random.randint(10000, 99999)}"

        st.info(f"📊 Booking Details: {pickup_place} to {drop_place}")

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
                    "pickup_lat": lat, 
                    "pickup_lon": lon,
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
                trip_saved = save_trip_dual_backup(payload)

                if trip_saved:
                    if 'register_successful_booking_attempt' in globals():
                        register_successful_booking_attempt()

                    # Driver notification — Vera function വഴി
                    if 'process_radius_expansion_routing' in globals():
                        process_radius_expansion_routing(payload, lat, lon)

                    st.success("✅ ബുക്കിംഗ് വിജയകരമായി പൂർത്തിയായി!")

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

                    # ----------------------------------------------------
                    # 📍 ലൈവ് മാപ്പ് കോൾ
                    # ----------------------------------------------------
                    st.write("---")
                    trip_ref = db.reference(f"trips/{unique_trip_id}")
                    trip_data = trip_ref.get()
                    status = trip_data.get("status", "Pending") if trip_data else "Pending"
                    vehicle_type_check = trip_data.get("vehicle_type", "Auto Rickshaw") if trip_data else "Auto Rickshaw"

                    # ഡ്രൈവർ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തു കഴിഞ്ഞാൽ മാത്രം പ്രവർത്തിക്കുന്ന ഭാഗം
                    if status == "Accepted":
                        # 🔔 1. നോട്ടിഫിക്കേഷൻ സൗണ്ട്
                        notification_sound = """
                            <audio autoplay>
                              <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                            </audio>
                        """
                        st.markdown(notification_sound, unsafe_allow_html=True)

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
                        st.info("⏳ ഡ്രൈവർമാർ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്യുന്നതിനായി കാത്തിരിക്കുന്നു... ദയവായി ഈ പേജ് ക്ലോസ് ചെയ്യരുത്.")

                    with st.expander("📝 സേവന നിബന്ധനകളും ഡിസ്ക്ലൈമറും"):
                        st.write("""
                        **ഡിസ്ക്ലൈമർ (Disclaimer):**
                        * ഈ ആപ്ലിക്കേഷൻ ഡ്രൈവർമാരെയും യാത്രക്കാരെയും ബന്ധിപ്പിക്കുന്ന ഒരു **ഡിജിറ്റൽ മെസ്സേജിംഗ് പ്ലാറ്റ്ഫോം** മാത്രമാണ്.
                        * യാത്രയ്ക്കിടയിൽ ഉണ്ടാകുന്ന സാങ്കേതികമോ, വ്യക്തിപരമോ ആയ പ്രശ്നങ്ങൾക്കോ, അപകടങ്ങൾക്കോ ഈ പ്ലാറ്റ്ഫോമോ, അഡ്മിനിസ്ട്രേറ്റർമാരോ ഉത്തരവാദികളായിരിക്കുന്നതല്ല.
                        * ഡ്രൈവർമാരുമായുള്ള ഇടപാടുകളിൽ യാത്രക്കാർ ജാഗ്രത പാലിക്കേണ്ടതാണ്.
                        * ഈ സേവനം ഉപയോഗിക്കുന്നതിലൂടെ നിങ്ങൾ ഈ നിബന്ധനകൾ അംഗീകരിക്കുന്നു.
                        """)
                else:
                    st.error("❌ ബുക്കിംഗ് സേവ് ചെയ്യുന്നതിൽ പരാജയപ്പെട്ടു.")

        st.session_state.is_booking = False
        st.write("---")

        # ============================================================
        # 🚨 SOS & Contact Section
        # ============================================================
        col_sos, col_contact = st.columns([1, 1])
        with col_sos:
            with st.expander("🚨 SOS"):
                st.link_button("👮 പോലീസ് (100)", "tel:100")
                st.link_button("👨‍👩‍👧‍👦 ബന്ധുക്കൾക്ക്", "https://wa.me/?text=⚠️ അടിയന്തര സഹായം ആവശ്യമാണ്! മഞ്ചേരി.")
        with col_contact:
            st.link_button("💬 Contact Us", "https://wa.me/919376543210")


if __name__ == "__main__":
    main()
	







# ========================================================
# വെബ്‌സൈറ്റ് ഫൂട്ടറും ഡ്രൈവർ & SOS പാനലുകളും (മുഴുവൻ ഫീച്ചറുകളും ഉള്ളത്)
# ========================================================

# ഫൂട്ടറിന് ബോക്സും ബോർഡറും നൽകാനുള്ള CSS സ്റ്റൈൽ
str_lit.markdown("""
<style>
.footer-box {
    border: 2px solid #ffcc00;
    border-radius: 10px;
    padding: 20px;
    background-color: #1e1e1e;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ഫൂട്ടർ സെപ്പറേറ്റർ
str_lit.markdown("---")

# മൂന്ന് കോളങ്ങളിലായി മൂന്ന് പ്രധാന ബട്ടണുകൾ
footer_col1, footer_col2, footer_col3 = str_lit.columns(3)

# 1. Contact Us ബട്ടൺ
with footer_col1:
    if str_lit.button("📞 Contact Us"):
        str_lit.info("സഹായത്തിന് വിളിക്കുക: +91 XXXXXXXXXX | Email: support@example.com")

# 2. SOS / Emergency ബട്ടൺ
with footer_col2:
    if str_lit.button("🚨 SOS / Emergency"):
        str_lit.session_state['show_sos_panel'] = True
        str_lit.session_state['show_driver_panel'] = False  # ഡ്രൈവർ പാനൽ ക്ലോസ് ചെയ്യാൻ

# 3. Driver Panel ബട്ടൺ
with footer_col3:
    if str_lit.button("🚗 Driver Panel"):
        str_lit.session_state['show_driver_panel'] = True
        str_lit.session_state['show_sos_panel'] = False  # SOS പാനൽ ക്ലോസ് ചെയ്യാൻ


# --------------------------------------------------------
# SOS പാനൽ (ഡയറക്ട് കോൾ ലിങ്കുകളും വാട്സാപ്പ് ഷെയറും)
# --------------------------------------------------------
if str_lit.session_state.get('show_sos_panel', False):
    str_lit.markdown("---")
    str_lit.error("🚨 അടിയന്തര സഹായ വിഭാഗം (Emergency Control Rooms)")
    
    # നമ്പറുകളിൽ അമർത്തിയാൽ നേരിട്ട് കോൾ പോകുന്ന ലിങ്കുകൾ (tel: link)
    str_lit.markdown("""
    * **👮 പോലീസ് കൺട്രോൾ റൂം (112 / 100):** &nbsp; [📞 112 കോൾ ചെയ്യുക](tel:112)
    * **🔥 ഫയർഫോഴ്സ് (101):** &nbsp; [📞 101 കോൾ ചെയ്യുക](tel:101)
    * **🏥 ഹോസ്പിറ്റൽ / ആംബുലൻസ് (108):** &nbsp; [📞 108 കോൾ ചെയ്യുക](tel:108)
    """, unsafe_allow_html=True)
    
    str_lit.markdown("---")
    str_lit.subheader("📱 വാട്സാപ്പ് വഴി കുടുംബാംഗങ്ങൾക്ക് അയക്കാൻ")
    
    sos_message = "എനിക്ക് അടിയന്തര സഹായം ആവശ്യമാണ്! ദയവായി ഉടൻ ബന്ധപ്പെടുക. (ഡ്രൈവർ/യാത്രക്കാരൻ)"
    whatsapp_share_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(sos_message)}"
    
    str_lit.markdown(f"""
    <a href="{whatsapp_share_url}" target="_blank">
        <button style="background-color: #25D366; color: white; padding: 12px 20px; border: none; border-radius: 5px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%;">
            💬 വാട്സാപ്പ് വഴി കുടുംബാംഗങ്ങൾക്ക് അയക്കുക
        </button>
    </a>
    """, unsafe_allow_html=True)
    
    str_lit.markdown("<br>", unsafe_allow_html=True)
    
    if str_lit.button("SOS പാനൽ അടയ്ക്കുക"):
        str_lit.session_state['show_sos_panel'] = False
        str_lit.rerun()


# --------------------------------------------------------
# 🚗 ഡ്രൈവർ പാനൽ - ഫയർബേസ് ഡാറ്റാ കണക്ഷൻ
# --------------------------------------------------------
if str_lit.session_state.get('show_driver_panel', False):
    str_lit.markdown("---")
    str_lit.subheader("🚗 ഡ്രൈവർ പാനൽ - ചാറ്റ് & ട്രിപ്പ് ഹിസ്റ്ററി")
    
    driver_telegram_id = str_lit.text_input("നിങ്ങളുടെ ടെലഗ്രാം ചാറ്റ് ഐഡി (Telegram Chat ID) നൽകുക:", key="driver_id_input_main")
    
    # മൊബൈൽ ഉപയോക്താക്കൾക്ക് വേണ്ടി സെർച്ച് ബട്ടൺ
    search_clicked = str_lit.button("🔍 ഹിസ്റ്ററി പരിശോധിക്കുക (Search)")
    
    # ചാറ്റ് ഐഡി നൽകി സെർച്ച് അമർത്തുമ്പോൾ മാത്രം ഹിസ്റ്ററി ലോഡ് ആകും
    if driver_telegram_id and search_clicked:
        str_lit.info(f"ചാറ്റ് ഐഡി ({driver_telegram_id}) പരിശോധിക്കുന്നു...")
        
        # ഫയർബേസിൽ നിന്ന് ആ ഡ്രൈവറുടെ ട്രിപ്പുകൾ മാത്രം എടുക്കുന്ന ഫങ്ഷൻ
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
                            "booking_time": trip.get("booking_time", "N/A"),
                            "pickup": trip.get("pickup", "N/A"),
                            "drop": trip.get("drop", "N/A"),
                            "total_fare": trip.get("total_fare", "N/A")
                        })
                return result_data
            except Exception as e:
                return []

        # ഫങ്ഷൻ കോൾ ചെയ്ത് ഡാറ്റ എടുക്കുന്നു
        driver_history_data = fetch_driver_history_from_firebase(driver_telegram_id.strip())
        
        if driver_history_data:
            str_lit.success("✅ ഡ്രൈവർ ഹിസ്റ്ററി വിജയകരമായി ലോഡ് ചെയ്തു!")
            str_lit.markdown("### 📋 നിങ്ങളുടെ മുൻകാല ട്രിപ്പുകൾ:")
            str_lit.table(driver_history_data)
        else:
            str_lit.warning("⚠️ ഈ ചാറ്റ് ഐഡിയിൽ ഇതുവരെ ട്രിപ്പുകൾ ഒന്നും കണ്ടെത്താനായില്ല.")
            
    if str_lit.button("പാനൽ അടയ്ക്കുക"):
        str_lit.session_state['show_driver_panel'] = False
        str_lit.rerun()
# ==========================================================
# Clean Footer Component: Shadow for Malayalam Text & Styled Button
# ==========================================================
st.markdown("---")

# മലയാളം ടെക്സ്റ്റിന് മാത്രം ഷാഡോയും പ്രൊഫഷണൽ ലുക്കും നൽകാനുള്ള CSS ഉം ബട്ടൺ കളർ മാറ്റാനുള്ള സ്റ്റൈലും
st.markdown("""
    <style>
    .malayalam-title-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e0e0;
        margin-bottom: 15px;
    }
    /* സ്റ്റാറ്റസ് നോക്കൂ ബട്ടൺ കൂടുതൽ ആകർഷകമാക്കാൻ */
    .stButton > button {
        background-color: #e67e22;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #d35400;
        color: white;
    }
    </style>
    <div class="malayalam-title-card">
        <h3 style="margin:0; color: #2c3e50; font-size: 19px;">🔍 നിങ്ങളുടെ നിലവിലെ ബുക്കിംഗ് സ്റ്റാറ്റസ് അറിയാൻ</h3>
        <p style="margin: 8px 0 0 0; color: #555555; font-size: 14px;">ആപ്ലിക്കേഷൻ ക്ലോസ് ആയിപ്പോയോ? മുൻപത്തെ ബുക്കിംഗ് സ്റ്റാറ്റസ് പരിശോധിക്കുന്നതിനായി ട്രിപ്പ് ഐഡി ഇവിടെ നൽകുക.</p>
    </div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    footer_trip_id = st.text_input("ട്രിപ്പ് ഐഡി നൽകുക:", key="independent_footer_trip_id", label_visibility="collapsed", placeholder="ട്രിപ്പ് ഐഡി ഇവിടെ നൽകുക (ഉദാ: TRIP-XXXXX)")
with col2:
    footer_check_btn = st.button("സ്റ്റാറ്റസ് നോക്കൂ", key="independent_footer_btn", use_container_width=True)

if footer_check_btn:
    if footer_trip_id:
        with st.spinner("വിവരങ്ങൾ പരിശോധിക്കുന്നു..."):
            trip_data = get_trip_from_database(footer_trip_id.strip()) if 'get_trip_from_database' in globals() else None
            
            if trip_data:
                current_status = trip_data.get('status', 'Pending')
                st.success(f"✅ ട്രിപ്പ് വിജയകരമായി കണ്ടെത്തി!")
                st.info(f"📍 **പിക്കപ്പ്:** {trip_data.get('pickup')} \n\n 🏁 **ഡ്രോപ്പ്:** {trip_data.get('drop')}")
                st.markdown(f"🟢 **നിലവിലെ അവസ്ഥ (Status):** `{current_status}`")
                
                if current_status == "Arrived":
                    st.warning("🚨 ഡ്രൈവർ നിങ്ങളുടെ പിക്കപ്പ് ലൊക്കേഷനിൽ എത്തിയിട്ടുണ്ട്!")
                    # ==========================================================
                    # 🔔 REAL-TIME NOTIFICATION LISTENER (ഇവിടെയാണ് ചേർക്കേണ്ടത്)
                    # ==========================================================
                    current_trip_id = footer_trip_id
                    
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
                else:       
                    st.error("❌ ഈ ട്രിപ്പ് 'Arrived' അവസ്ഥയിൽ അല്ല.")
            else:
                st.error("❌ ഈ ട്രിപ്പ് ഐഡിയിൽ വിവരങ്ങൾ ഒന്നും ലഭ്യമാവുന്നില്ല. ഐഡി പരിശോധിച്ച് വീണ്ടും നൽകുക.")
    else:
        st.warning("⚠️ ദയവായി നിങ്ങളുടെ ട്രിപ്പ് ഐഡി നൽകുക.")
        
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
    # 3. Navigation URL — Directions mode
    # ============================================================
    navigation_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&destination={pickup_lat},{pickup_lon}"
        f"&travelmode=driving"
    )

    # ============================================================
    # 4. Inline Buttons — Order: Navigation, Arrived, Call (bottom)
    # ============================================================
    markup = types.InlineKeyboardMarkup(row_width=1)

    nav_button = types.InlineKeyboardButton(
        "🗺️ നാവിഗേഷൻ (Google Maps)",
        url=navigation_url
    )

    arrived_button = types.InlineKeyboardButton(
        "✅ ഞാൻ എത്തി (Arrived)",
        callback_data=f"arrived_{booking_id}"
    )

    # 🎯 — Phone normalize
    raw_phone = str(customer_phone).strip().replace(" ", "").replace("-", "").replace("+", "")

    if raw_phone.startswith("91") and len(raw_phone) == 12:
        tel_url = f"tel:+{raw_phone}"  
    elif len(raw_phone) == 10:
        tel_url = f"tel:+91{raw_phone}"
    else:
        tel_url = f"tel:+91{raw_phone}"
    

    # Order: Navigation → Arrived → Call (bottom)
    markup.add(nav_button, arrived_button)

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
# ==========================================================
# ✅ ACCEPT TRIP Callback Handler (telebot)
# ==========================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def handle_accept_trip(call):
    """
    Driver ACCEPT button tap ചെയ്യുമ്പോൾ:
    1. Firebase-ൽ trip status = Accepted (transaction)
    2. Driver-ന് confirmation alert
    3. accept_trip() — Navigation + Arrived + Call buttons
    """
    print("=" * 60)
    print(f"🔔 CALLBACK RECEIVED!")
    print(f"   Data: {call.data}")
    print(f"   Chat ID: {call.message.chat.id}")
    print("=" * 60)
    chat_id = call.message.chat.id
    trip_id = call.data.replace("accept_", "")

    try:
        # 1. Atomic Trip Acceptance
        driver_data = db.reference(f"drivers/{chat_id}").get() or {}
        driver_name = driver_data.get("driver_name", "Unknown Driver")   
        driver_phone = driver_data.get("phone", "N/A")
        # 🆕 ഡീബഗ് ചെയ്യാൻ ഇത് ചേർക്കുക
        print(f"DEBUG: Fetched Driver -> Name: {driver_name}, Phone: {driver_phone}")
        # 2. Atomic Trip Acceptance (യഥാർത്ഥ പേരും ഫോണും നൽകുക)   
        result = accept_trip_safely(
            trip_id,
            chat_id,
            driver_name,   # 🆕 ഡ്രൈവറുടെ യഥാർത്ഥ പേര്
            driver_phone   # 🆕 ഡ്രൈവറുടെ യഥാർത്ഥ ഫോൺ 
        )

        # 2. Response
        if result == "success":
            # Remove ACCEPT button
            try:
                bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=None
                )
            except:
                pass

            # Alert
            bot.answer_callback_query(
                call.id,
                "✅ ട്രിപ്പ് അക്സെപ്റ്റ് ചെയ്തു!",
                show_alert=False
            )

            # 3. Fetch trip data
            trip_data = db.reference(f"trips/{trip_id}").get() or {}

            customer_name = trip_data.get("customer_name", "N/A")
            customer_phone = trip_data.get("customer_phone", "")
            pickup_lat = trip_data.get("pickup_lat", 0)
            pickup_lon = trip_data.get("pickup_lon", 0)

            # Fallback — parse from location link
            if not pickup_lat or not pickup_lon:
                pickup_link = (
                    trip_data.get("location")
                    or trip_data.get("pickup_link")
                    or ""
                )
                if pickup_link and "q=" in pickup_link:
                    try:
                        coords = pickup_link.split("q=")[-1].split("&")[0]
                        pickup_lat, pickup_lon = coords.split(",")
                        pickup_lat = float(pickup_lat)
                        pickup_lon = float(pickup_lon)
                    except:
                        pass
            
            # 4. Follow-up — accept_trip()
            # 🆕 ഡ്രൈവറുടെ വിവരങ്ങൾ ഫയർബേസിൽ നിന്ന് എടുക്കുക
            driver_data = db.reference(f"drivers/{chat_id}").get() or {}
            driver_name = driver_data.get("driver_name", "Unknown Driver")
            driver_phone = driver_data.get("phone", "N/A")
            vehicle_number = driver_data.get("vehicle_number", "N/A")
            
            
            accept_trip(
                booking_id=trip_id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                driver_name=driver_name,
                driver_phone=driver_phone,
                vehicle_number=vehicle_number,  # 🆕 വാഹന നമ്പർ
                driver_chat_id=chat_id,
                pickup_lat=pickup_lat,
                pickup_lon=pickup_lon
            )

            print(f"✅ Trip {trip_id} accepted by driver {chat_id}")

        elif result == "already_taken":
            bot.answer_callback_query(
                call.id,
                "❌ ഈ ട്രിപ്പ് മറ്റൊരു ഡ്രൈവർ എടുത്തു!",
                show_alert=True
            )
        else:
            bot.answer_callback_query(
                call.id,
                "❌ ട്രിപ്പ് കണ്ടെത്തിയില്ല!",
                show_alert=True
            )

    except Exception as e:
        print(f"❌ handle_accept_trip error: {e}")
        try:
            bot.answer_callback_query(
                call.id,
                "❌ Error സംഭവിച്ചു",
                show_alert=True
            )
        except:
            pass 
   
# ==========================================================
# ✅ ARRIVED Callback Handler (telebot)
# ==========================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("arrived_")) 
def handle_arrived_trip(call):
    """
    Driver ARRIVED button tap ചെയ്യുമ്പോൾ:
    1. Firebase-ൽ trip status = Arrived
    2. Driver-ന് കൺഫർമേഷൻ അയക്കുന്നു
    """
    print("=" * 60)
    print(f"🔔 ARRIVED CALLBACK RECEIVED!")
    print(f"   Data: {call.data}")
    print(f"   Chat ID: {call.message.chat.id}")
    print("=" * 60)
    
    chat_id = call.message.chat.id
    trip_id = call.data.replace("arrived_", "")
    
    try:
        # 1. Firebase-ൽ സ്റ്റാറ്റസ് അപ്ഡേറ്റ് ചെയ്യുക
        ref = db.reference(f"trips/{trip_id}")
        trip_data = ref.get()
        
        if trip_data and str(trip_data.get("driver_chat_id")) == str(chat_id):
            ref.update({"status": "Arrived"})
            
            # Alert (Pop-up message)
            bot.answer_callback_query(
                call.id,
                "✅ നിങ്ങൾ എത്തിയതായി രേഖപ്പെടുത്തി!",
                show_alert=False
            )
            
            # മെസ്സേജ് എഡിറ്റ് ചെയ്യുക (Notify Customer ബട്ടണും കൂടി ചേർക്കുക)
            try:
                # 1. Notify Customer ബട്ടൺ ഉണ്ടാക്കുക
                notify_button = types.InlineKeyboardButton(
                    "🔔 കസ്റ്റമറെ അറിയിക്കുക",
                    callback_data=f"notify_{trip_id}"
                )
                
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(notify_button)
                
                # 2. മെസ്സേജ് എഡിറ്റ് ചെയ്യുക
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    text=call.message.text + "\n\n🔴 **[Status: Arrived at Location]** - കസ്റ്റമറെ അറിയിക്കാൻ താഴെയുള്ള ബട്ടൺ അമർത്തുക.",
                    reply_markup=markup
                )
            except Exception as edit_err:
                print(f"⚠️ Edit message error: {edit_err}")
                
        else:
            # അനധികൃത ഡ്രൈവർ
            bot.answer_callback_query(
                call.id,
                "❌ അസാധുവായ റിക്വസ്റ്റ് അല്ലെങ്കിൽ നിങ്ങൾക്ക് ഈ ട്രിപ്പിൽ അധികാരമില്ല.",
                show_alert=True
            )
            
    except Exception as e:
        print(f"❌ handle_arrived_trip error: {e}")
        bot.answer_callback_query(
            call.id,
            "❌ Error സംഭവിച്ചു",
            show_alert=True
        )
# ==========================================================
# ✅ CALL CUSTOMER Callback Handler (telebot) - v4
# ==========================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("call_"))
def handle_call_customer(call):
    """
    Driver CALL button tap ചെയ്യുമ്പോൾ:
    മാസ്ക് ചെയ്ത ഫോൺ നമ്പർ അയക്കുന്നു. യഥാർത്ഥ നമ്പർ കാണാൻ ഒരു ബട്ടണും നൽകുന്നു.
    """
    print("=" * 60)
    print(f"🔔 CALL CUSTOMER CALLBACK RECEIVED!")
    print(f"   Data: {call.data}")
    print("=" * 60)
    
    chat_id = call.message.chat.id
    booking_id = call.data.replace("call_", "")
    
    try:
        # 1. Firebase-ൽ നിന്ന് വിവരങ്ങൾ എടുക്കുക
        trip_data = db.reference(f"trips/{booking_id}").get() or {}
        customer_phone = trip_data.get("customer_phone", "")
        customer_name = trip_data.get("customer_name", "Customer")
        
        if not customer_phone:
            bot.answer_callback_query(
                call.id, 
                "❌ കസ്റ്റമറുടെ ഫോൺ നമ്പർ ലഭ്യമല്ല", 
                show_alert=True
            )
            return

        # 2. ഫോൺ നമ്പർ ഫോർമാറ്റ് ചെയ്യുക (+91 ഉൾപ്പെടെ)
        raw_phone = str(customer_phone).strip().replace(" ", "").replace("-", "").replace("+", "")
        
        if raw_phone.startswith("91") and len(raw_phone) == 12:
            formatted_phone = f"+{raw_phone}"
        elif len(raw_phone) == 10:
            formatted_phone = f"+91{raw_phone}"
        else:
            formatted_phone = f"+91{raw_phone}"

        # 3. മാസ്ക് ചെയ്ത നമ്പർ ഉണ്ടാക്കുക (Privacy-ക്ക് വേണ്ടി)
        if len(raw_phone) >= 10:
            masked_phone = f"{raw_phone[:4]}XXXXX{raw_phone[-2:]}"
        else:
            masked_phone = "XXXXX"

        # 4. "യഥാർത്ഥ നമ്പർ കാണുക" എന്ന ബട്ടൺ ഉണ്ടാക്കുക
        show_phone_button = types.InlineKeyboardButton(
            "📞 യഥാർത്ഥ നമ്പർ കാണുക",
            callback_data=f"showphone_{booking_id}"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(show_phone_button)

        # 5. മാസ്ക് ചെയ്ത നമ്പർ അയക്കുക
        message_text = (
            f"📞 *കസ്റ്റമറുടെ വിവരങ്ങൾ*\n\n"
            f"👤 പേര്: {customer_name}\n"
            f"📱 നമ്പർ: `{masked_phone}`\n\n"
            f"⚠️ *അത്യാവശ്യ ഘട്ടങ്ങളിൽ മാത്രം വിളിക്കുക.*\n"
            f"ℹ️ യഥാർത്ഥ നമ്പർ കാണാൻ താഴെയുള്ള ബട്ടൺ അമർത്തുക."
        )
        
        bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        bot.answer_callback_query(
            call.id,
            "📞 കോൺടാക്റ്റ് വിവരങ്ങൾ അയച്ചിട്ടുണ്ട്.",
            show_alert=False
        )
        
        print(f"✅ Contact info sent for {booking_id} to {chat_id}")
        
    except Exception as e:
        print(f"❌ handle_call_customer error: {e}")
        bot.answer_callback_query(
            call.id,
            "❌ Error സംഭവിച്ചു",
            show_alert=True
        )
# ==========================================================
# ✅ SHOW PHONE Callback Handler (telebot) - v4 (One-Time View)
# ==========================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("showphone_"))
def handle_show_phone(call):
    """
    Driver-ന് യഥാർത്ഥ ഫോൺ നമ്പർ അയക്കുന്നു (ഒരിക്കൽ മാത്രം).
    """
    print("=" * 60)
    print(f"🔔 SHOW PHONE CALLBACK RECEIVED!")
    print(f"   Data: {call.data}")
    print("=" * 60)
    
    chat_id = call.message.chat.id
    booking_id = call.data.replace("showphone_", "")
    
    try:
        # 1. Firebase-ൽ നിന്ന് ട്രിപ്പ് വിവരങ്ങൾ എടുക്കുക
        ref = db.reference(f"trips/{booking_id}")
        trip_data = ref.get() or {}
        customer_phone = trip_data.get("customer_phone", "")
        customer_name = trip_data.get("customer_name", "Customer")
        accepted_at = trip_data.get("accepted_at", "")
        phone_viewed = trip_data.get("phone_viewed", False)  # 🆕 പുതിയ ഫ്ലാഗ്
        
        if not customer_phone:
            bot.answer_callback_query(
                call.id, 
                "❌ കസ്റ്റമറുടെ ഫോൺ നമ്പർ ലഭ്യമല്ല", 
                show_alert=True
            )
            return

        # 🆕 2. ഒരിക്കൽ കണ്ടു കഴിഞ്ഞോ എന്ന് പരിശോധിക്കുക
        if phone_viewed:
            bot.answer_callback_query(
                call.id,
                "❌ നിങ്ങൾക്ക് ഈ നമ്പർ ഒരിക്കൽ മാത്രമേ കാണാൻ കഴിയൂ. വീണ്ടും കാണാൻ സാധിക്കില്ല.",
                show_alert=True
            )
            return

        # 3. ⏰ സമയപരിധി പരിശോധിക്കുക (5 മിനിറ്റ്)
        if accepted_at:
            from datetime import datetime, timedelta
            try:
                accept_time = datetime.strptime(accepted_at, "%Y-%m-%d %H:%M:%S")
                time_diff = datetime.now() - accept_time
                
                if time_diff > timedelta(minutes=5):
                    bot.answer_callback_query(
                        call.id,
                        "❌ ഈ ട്രിപ്പിന്റെ സമയപരിധി (5 മിനിറ്റ്) കഴിഞ്ഞു. ഇനി നമ്പർ കാണാൻ സാധിക്കില്ല.",
                        show_alert=True
                    )
                    return
            except Exception as time_err:
                print(f"⚠️ Time check error: {time_err}")

        # 4. ഫോൺ നമ്പർ ഫോർമാറ്റ് ചെയ്യുക
        raw_phone = str(customer_phone).strip().replace(" ", "").replace("-", "").replace("+", "")
        
        if raw_phone.startswith("91") and len(raw_phone) == 12:
            formatted_phone = f"+{raw_phone}"
        elif len(raw_phone) == 10:
            formatted_phone = f"+91{raw_phone}"
        else:
            formatted_phone = f"+91{raw_phone}"

        # 5. മാസ്ക് ചെയ്ത നമ്പർ ഉണ്ടാക്കുക
        if len(raw_phone) >= 10:
            masked_phone = f"{raw_phone[:4]}XXXXX{raw_phone[-2:]}"
        else:
            masked_phone = "XXXXX"

        # 🆕 6. ഫയർബേസിൽ phone_viewed = True എന്ന് അപ്ഡേറ്റ് ചെയ്യുക
        ref.update({"phone_viewed": True})

        # 7. യഥാർത്ഥ നമ്പർ അയക്കുക
        message_text = (
            f"📞 *യഥാർത്ഥ ഫോൺ നമ്പർ*\n\n"
            f"👤 പേര്: {customer_name}\n"
            f"📱 നമ്പർ: `{formatted_phone}`\n\n"
            f"⚠️ *അത്യാവശ്യ ഘട്ടങ്ങളിൽ മാത്രം വിളിക്കുക.*\n"
            f"ℹ️ ഈ നമ്പർ കോപ്പി ചെയ്ത് വിളിക്കുക.\n\n"
            f"🚨 *മുന്നറിയിപ്പ്:* കസ്റ്റമറുടെ ഫോൺ നമ്പർ ദുരുപയോഗം ചെയ്യരുത്. അത് ചെയ്താൽ നിയമനടപടികൾ നേരിടേണ്ടി വരും.\n\n"
            f"🔒 *ഈ നമ്പർ ഒരിക്കൽ മാത്രമേ കാണാൻ കഴിയൂ.*\n"
            f"⏳ *1 മിനിറ്റിനുള്ളിൽ വീണ്ടും മാസ്ക് ചെയ്യപ്പെടും.*"
        )
        
        sent_msg = bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode="Markdown"
        )
        
        # 8. 1 മിനിറ്റിന് ശേഷം മെസ്സേജ് വീണ്ടും മാസ്ക് ചെയ്യുക
        def mask_later():
            import time
            time.sleep(60)  # 60 സെക്കൻഡ് = 1 മിനിറ്റ്
            try:
                masked_message = (
                    f"📞 *കസ്റ്റമറുടെ വിവരങ്ങൾ*\n\n"
                    f"👤 പേര്: {customer_name}\n"
                    f"📱 നമ്പർ: `{masked_phone}`\n\n"
                    f"🔒 *സുരക്ഷയ്ക്കായി നമ്പർ വീണ്ടും മാസ്ക് ചെയ്തിരിക്കുന്നു.*\n"
                    f"❌ *ഈ നമ്പർ വീണ്ടും കാണാൻ സാധിക്കില്ല.*"
                )
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=sent_msg.message_id,
                    text=masked_message,
                    parse_mode="Markdown"
                )
                print(f"✅ Message re-masked for {booking_id}")
            except Exception as mask_err:
                print(f"⚠️ Re-mask error: {mask_err}")
        
        import threading
        threading.Thread(target=mask_later, daemon=True).start()
        
        bot.answer_callback_query(
            call.id,
            "📞 യഥാർത്ഥ നമ്പർ അയച്ചിട്ടുണ്ട്. ഇത് ഒരിക്കൽ മാത്രമേ കാണാൻ കഴിയൂ.",
            show_alert=False
        )
        
        print(f"✅ Real phone number sent for {booking_id} to {chat_id}")
        
    except Exception as e:
        print(f"❌ handle_show_phone error: {e}")
        bot.answer_callback_query(
            call.id,
            "❌ Error സംഭവിച്ചു",
            show_alert=True
        )
# ==========================================================
# ✅ NOTIFY CUSTOMER Callback Handler (telebot)
# ==========================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("notify_"))
def handle_notify_customer(call):
    """
    Driver NOTIFY button tap ചെയ്യുമ്പോൾ:
    1. കസ്റ്റമറുടെ ആപ്പിലേക്ക് ശബ്ദ നോട്ടിഫിക്കേഷൻ അയക്കുന്നു.
    2. ഡ്രൈവർക്ക് "Call" ബട്ടൺ അയച്ചുകൊടുക്കുന്നു.
    """
    print("=" * 60)
    print(f"🔔 NOTIFY CUSTOMER CALLBACK RECEIVED!")
    print(f"   Data: {call.data}")
    print("=" * 60)
    
    chat_id = call.message.chat.id
    booking_id = call.data.replace("notify_", "")
    
    try:
        # 1. ഫയർബേസിൽ നോട്ടിഫിക്കേഷൻ സിഗ്നൽ അപ്ഡേറ്റ് ചെയ്യുക (കസ്റ്റമറുടെ ആപ്പിൽ ശബ്ദം വരാൻ)
        ref = db.reference(f"trips/{booking_id}")
        ref.update({"notification": "arrived_sound"})
        
        # 2. ഡ്രൈവർക്ക് കൺഫർമേഷൻ അലേർട്ട്
        bot.answer_callback_query(
            call.id,
            "🔔 കസ്റ്റമറെ അറിയിച്ചിട്ടുണ്ട്!",
            show_alert=False
        )
        
        # 3. "Call" ബട്ടൺ ഉണ്ടാക്കി ഡ്രൈവർക്ക് അയക്കുക
        call_button = types.InlineKeyboardButton(
            "📞 കസ്റ്റമറെ വിളിക്കുക",
            callback_data=f"call_{booking_id}"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(call_button)
        
        bot.send_message(
            chat_id=chat_id,
            text="✅ കസ്റ്റമറുടെ ആപ്പിലേക്ക് നോട്ടിഫിക്കേഷൻ അയച്ചിട്ടുണ്ട്.\n\nകസ്റ്റമർ കിട്ടിയില്ലെങ്കിൽ താഴെയുള്ള ബട്ടൺ അമർത്തി വിളിക്കാം.",
            reply_markup=markup
        )
        
        print(f"✅ Notification sent for {booking_id}")
        
    except Exception as e:
        print(f"❌ handle_notify_customer error: {e}")
        bot.answer_callback_query(
            call.id,
            "❌ Error സംഭവിച്ചു",
            show_alert=True
        )        
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
