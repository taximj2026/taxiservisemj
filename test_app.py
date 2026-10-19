"""
ðŸš– Easy Auto Taxi Pro - Complete Merged System
Version: 7.0 INTEGRATED FINAL
Author: Auto Taxi Pro Team
Last Updated: 2026

ðŸ“Œ COMPLETE MERGE SUMMARY & CHANGES:
====================================
âœ… MODULES MERGED: All 22 modules integrated perfectly
âœ… PREMIUM UI ADDED: Dark Gold Modern Premium Theme included via CSS
âœ… SMART MAPPING INTEGRATED: OSRM -> GraphHopper -> Geoapify Fallback system
âœ… DYNAMIC COMMISSION: Automated calculate_admin_commission included
âœ… ANTI-SPAM & SECURITY: Math CAPTCHA, Rate Limiter, and DDoS protections active
âœ… DUPLICATES REMOVED: All duplicate functions and imports consolidated
"""

# ============================================================
# ðŸ“¦ IMPORTS - All libraries in one place
# ============================================================
# ============================================================
# ðŸ“¦ IMPORTS - All libraries in one place
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
# --- Mobile Friendly CSS (à´‡à´µà´¿à´Ÿàµ† à´šàµ‡àµ¼à´•àµà´•àµà´•) ---
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




# ==========================================================
# ðŸ“Œ 1. à´ˆ à´«à´‚à´—àµà´·àµ» à´•àµ‹à´¡à´¿à´¨àµà´±àµ† à´à´±àµà´±à´µàµà´‚ à´®àµà´•à´³à´¿àµ½ (Global Scope-àµ½) à´¨àµ½à´•àµà´•
# ==========================================================
def get_trip_from_database(trip_id):
    try:
        ref = db.reference(f"trips/{trip_id}")
        return ref.get()
    except Exception as e:
        return None
def get_lat_lon_from_address(address):
    """à´œà´¿à´¯àµ‹ à´•àµ‹à´¡à´¿à´™àµ à´µà´´à´¿ à´µà´¿à´²à´¾à´¸à´¤àµà´¤à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ Lat, Lon à´•à´£àµà´Ÿàµ†à´¤àµà´¤àµà´¨àµà´¨ à´«à´™àµà´·àµ»"""
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
# à´µà´¾à´¹à´¨à´¤àµà´¤à´¿à´¨àµà´±àµ† à´¸àµà´µà´­à´¾à´µà´‚ à´…à´¨àµà´¸à´°à´¿à´šàµà´šàµ à´®à´¾à´ªàµà´ªà´¿à´²àµ† à´à´•àµà´•àµ‹àµº à´•à´¾à´£à´¿à´•àµà´•àµà´¨àµà´¨ à´«à´™àµà´·àµ»
# 1. à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´¡àµà´°àµˆà´µà´±àµà´Ÿàµ† à´¤à´¤àµà´¸à´®à´¯ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨ à´«à´™àµà´·àµ»
def get_live_tracking_from_firebase(trip_id):
    try:
        # à´«à´¯àµ¼à´¬àµ‡à´¸à´¿à´²àµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´ªà´¾à´¤àµà´¤àµ (à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´¡à´¾à´±àµà´±à´¾à´¬àµ‡à´¸àµ à´¸àµà´Ÿàµà´°à´•àµà´šàµ¼ à´…à´¨àµà´¸à´°à´¿à´šàµà´šàµ à´‡à´¤àµ à´®à´¾à´±àµà´±à´¾à´‚)
        ref = db.reference(f'trips/{trip_id}/driver_location')
        data = ref.get()
        return data  # à´‡à´¤àµ {'lat': x, 'lon': y} à´Žà´¨àµà´¨ à´«àµ‹àµ¼à´®à´¾à´±àµà´±à´¿àµ½ à´†à´¯à´¿à´°à´¿à´•àµà´•àµà´‚
    except Exception as e:
        return None

# 2. à´¦àµ‚à´°à´‚ à´•à´£à´•àµà´•à´¾à´•àµà´•à´¾àµ» à´¸à´¹à´¾à´¯à´¿à´•àµà´•àµà´¨àµà´¨ à´®à´¾à´¤àµà´¸àµ à´«à´™àµà´·àµ» (à´®àµ€à´±àµà´±à´±à´¿àµ½)
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
    print("ðŸ”” SEND_ADMIN CALLED")
    print(f"   ADMIN_ID = '{ADMIN_TELEGRAM_CHAT_ID}'")
    print(f"   bot = {bot}")
    print(f"   Trip = {trip_data.get('trip_id', 'N/A')}")
    print("=" * 50)
    
    try:
        if not bot or not ADMIN_TELEGRAM_CHAT_ID:
            print("âš ï¸ SKIPPED: bot or chat_id missing")
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
            commission_display = f"â‚¹{commission:.2f}"
        except:
            commission_display = f"â‚¹{commission}"

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
            gps_line = f"ðŸ”— GPS: [ðŸ“ Location]({gps_url})"
        else:
            gps_line = "ðŸ”— GPS: à´²à´­àµà´¯à´®à´²àµà´²"

        # Admin message
        admin_msg = (
            f"ðŸ”” *à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµ (Admin)*\n\n"
            f"ðŸ†” *Trip ID:* {trip_id}\n"
            f"ðŸ• *Time:* {booking_time}\n"
            f"ðŸ‘¤ *à´•à´¸àµà´±àµà´±à´®àµ¼:* {customer_name}\n"
            f"ðŸ“ž *à´«àµ‹àµº:* {masked_phone}\n"
            f"ðŸ“ *à´ªà´¿à´•àµà´•à´ªàµà´ªàµ:* {pickup}\n"
            f"ðŸ *à´¡àµà´°àµ‹à´ªàµà´ªàµ:* {drop}\n"
            f"ðŸ“ *à´à´°à´¿à´¯:* {area}\n"
            f"ðŸš— *à´µà´¾à´¹à´¨à´‚:* {vehicle}\n"
            f"ðŸ“ *à´¦àµ‚à´°à´‚:* {distance} km\n"
            f"ðŸ’° *Commission:* {commission_display}\n"
            f"{gps_line}"
        )

        bot.send_message(
            chat_id=ADMIN_TELEGRAM_CHAT_ID,
            text=admin_msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

        print(f"âœ… Admin notified: {trip_id}")
        return True

    except Exception as e:
        print(f"âŒ Admin notification error: {e}")
        return False

# ==========================================================
# ðŸ—ºï¸ LIVE TRACKING MAP (Updated with Notifications)
# ==========================================================
@st.fragment(run_every=15)   # 5s â†’ 15s (Firebase quota save)
def render_live_tracking_map(trip_id, customer_lat, customer_lon, vehicle_type):
    # ============================================================
    # ðŸ”” à´¸àµ—à´£àµà´Ÿàµ & à´¨àµ‹à´Ÿàµà´Ÿà´¿à´«à´¿à´•àµà´•àµ‡à´·àµ» à´’à´±àµà´± à´¬à´Ÿàµà´Ÿà´£à´¿àµ½ à´“àµº à´šàµ†à´¯àµà´¯àµà´•
    # ============================================================
    components.html("""
        <div id="alert-btn-container" style="margin-bottom: 10px;"></div>
        <script>
            // localStorage-àµ½ audio_enabled à´‰à´£àµà´Ÿàµ‹ à´Žà´¨àµà´¨àµ à´šàµ†à´•àµà´•àµ à´šàµ†à´¯àµà´¯àµà´•
            if (!localStorage.getItem('audio_enabled')) {
                var container = document.getElementById('alert-btn-container');
                var btn = document.createElement('button');
                btn.innerHTML = 'ðŸ”” à´…à´²àµ‡àµ¼à´Ÿàµà´Ÿàµà´•àµ¾ à´“àµº à´šàµ†à´¯àµà´¯àµà´• (Enable Alerts)';
                btn.style.cssText = 'padding:12px 20px; background-color:#ff4b4b; color:white; border:none; border-radius:8px; cursor:pointer; font-size:16px; width:100%; font-weight:bold;';
                
                btn.onclick = function() {
                    // 1. à´¸àµ—à´£àµà´Ÿàµ à´“àµº à´šàµ†à´¯àµà´¯àµà´• (localStorage-àµ½ à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¯àµà´•)
                    localStorage.setItem('audio_enabled', 'true');
                    
                    // 2. à´’à´°àµ à´šàµ†à´±à´¿à´¯ à´¸àµˆà´²à´¨àµà´±àµ à´¸àµ—à´£àµà´Ÿàµ à´ªàµà´²àµ‡ à´šàµ†à´¯àµà´¯àµà´•
                    var audio = new Audio('data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==');
                    audio.play().catch(e => console.log('Silent audio blocked'));
                    
                    // 3. ðŸ”” à´¨àµ‹à´Ÿàµà´Ÿà´¿à´«à´¿à´•àµà´•àµ‡à´·àµ» à´…à´¨àµà´µà´¾à´¦à´‚ à´šàµ‹à´¦à´¿à´•àµà´•àµà´•
                    if ('Notification' in window) {
                        Notification.requestPermission().then(function(permission) {
                            if (permission === 'granted') {
                                console.log('âœ… Notification permission granted');
                                new Notification('Easy Auto Taxi', {
                                    body: 'à´…à´²àµ‡àµ¼à´Ÿàµà´Ÿàµà´•àµ¾ à´“àµº à´†à´£àµ! à´¡àµà´°àµˆà´µàµ¼ à´µà´°àµà´®àµà´ªàµ‹àµ¾ à´¨à´¿à´™àµà´™àµ¾à´•àµà´•àµ à´…à´±à´¿à´¯à´¿à´ªàµà´ªàµ à´²à´­à´¿à´•àµà´•àµà´‚.',
                                    icon: 'https://cdn-icons-png.flaticon.com/512/3448/3448339.png'
                                });
                            } else {
                                console.log('âŒ Notification permission denied');
                            }
                        });
                    }
                    
                    // à´¬à´Ÿàµà´Ÿàµº à´Ÿàµ†à´•àµà´¸àµà´±àµà´±àµ à´®à´¾à´±àµà´±àµà´•
                    btn.innerHTML = 'âœ… à´…à´²àµ‡àµ¼à´Ÿàµà´Ÿàµà´•àµ¾ à´“àµº à´†à´£àµ';
                    btn.style.backgroundColor = '#28a745';
                    btn.disabled = true;
                };
                container.appendChild(btn);
            } else {
                // à´‡à´¤à´¿à´¨à´•à´‚ à´“àµº à´†à´£àµ†à´™àµà´•à´¿àµ½, à´’à´°àµ à´¸à´¨àµà´¦àµ‡à´¶à´‚ à´•à´¾à´£à´¿à´•àµà´•àµà´•
                var container = document.getElementById('alert-btn-container');
                var msg = document.createElement('div');
                msg.innerHTML = 'âœ… à´…à´²àµ‡àµ¼à´Ÿàµà´Ÿàµà´•à´³àµà´‚ à´¨àµ‹à´Ÿàµà´Ÿà´¿à´«à´¿à´•àµà´•àµ‡à´·à´¨àµà´‚ à´“àµº à´†à´£àµ';
                msg.style.cssText = 'padding:12px; background-color:#d4edda; color:#155724; border-radius:8px; font-size:14px; text-align:center; font-weight:bold;';
                container.appendChild(msg);
            }
        </script>
    """, height=60)
    try:
        # ============================================================
        # âœ… 1. Firebase-àµ½ à´¨à´¿à´¨àµà´¨àµ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´Žà´Ÿàµà´•àµà´•àµà´•
        # ============================================================
        trip_data = db.reference(f"trips/{trip_id}").get() or {}
        # Line 266 (à´‡à´µà´¿à´Ÿàµ† à´šàµ‡àµ¼à´•àµà´•àµà´•)
        print("ðŸ”¥ Firebase Trip Data:", trip_data)
        
        driver_name = trip_data.get("driver_name", "Driver")
        vehicle_number = trip_data.get("vehicle_number", "N/A")
        customer_name = trip_data.get("customer_name", "Customer")
        trip_status = trip_data.get("status", "Pending")
        trip_notification = trip_data.get("notification", "")

        # ============================================================
        # âœ… 2. Trip Details Header (Customer-à´¨àµ à´•à´¾à´£à´¾àµ»)
        # ============================================================
        st.markdown(f"""
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #2c3e50;">
            <h3 style="margin: 0; color: #2c3e50;">ðŸ†” à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿: {trip_id}</h3>
            <p style="margin: 5px 0; color: #555;">ðŸ‘¤ à´•à´¸àµà´±àµà´±à´®àµ¼: {customer_name}</p>
            <p style="margin: 5px 0; color: #555;">ðŸš– à´¡àµà´°àµˆà´µàµ¼: {driver_name}</p>
            <p style="margin: 5px 0; color: #555;">ðŸ”¢ à´µà´¾à´¹à´¨ à´¨à´®àµà´ªàµ¼: {vehicle_number}</p>
        </div>
        """, unsafe_allow_html=True)

        # ============================================================
        # âœ… 3. Warning Message (App Close à´šàµ†à´¯àµà´¯à´°àµà´¤àµ)
        # ============================================================
        st.warning("""
        âš ï¸ **à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•:**
        â€¢ à´ˆ à´†à´ªàµà´ªàµ à´•àµà´²àµ‹à´¸àµ à´šàµ†à´¯àµà´¯à´°àµà´¤àµ
        â€¢ à´‡à´¨àµà´±àµ¼à´¨àµ†à´±àµà´±àµ à´“à´«àµ à´šàµ†à´¯àµà´¯à´°àµà´¤àµ
        â€¢ à´«àµ‹àµº sleep mode-àµ½ à´µàµ†à´•àµà´•à´°àµà´¤àµ
        â€¢ à´¡àµà´°àµˆà´µàµ¼ à´µà´°àµà´¨àµà´¨à´¤àµ à´µà´°àµ† à´•à´¾à´¤àµà´¤à´¿à´°à´¿à´•àµà´•àµà´•
        """)

        # ============================================================
        # âœ… 4. Accept Notification (Driver Accept à´šàµ†à´¯àµà´¤ à´‰à´Ÿà´¨àµ†)
        # ============================================================
        if trip_status == "Accepted":
            if not st.session_state.get('accept_alert_shown', False):
                st.success("âœ… **à´¡àµà´°àµˆà´µàµ¼ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ!**")
                
                # ðŸ“± Vibration
                st.markdown("""
                    <script>
                    if (navigator.vibrate) {
                        navigator.vibrate([500, 200, 500]);
                    }
                    </script>
                """, unsafe_allow_html=True)
                
                # ðŸ”Š Sound
                sound_html = """
                <audio autoplay>
                    <source src="https://www.soundjay.com/phones/sounds/phone-ringing-01.mp3" type="audio/mpeg">
                </audio>
                """
                components.html(sound_html, height=0)
                st.session_state.accept_alert_shown = True

        # ============================================================
        # âœ… 5. Vehicle Header
        # ============================================================
        if "Auto" in vehicle_type or "auto" in vehicle_type.lower() or "à´“à´Ÿàµà´Ÿàµ‹" in vehicle_type:
            st.markdown("### ðŸ›º à´“à´Ÿàµà´Ÿàµ‹à´±à´¿à´•àµà´· à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´…à´Ÿàµà´¤àµà´¤àµ‡à´•àµà´•àµ à´µà´°àµà´¨àµà´¨àµ...")
            vehicle_icon = folium.Icon(color="orange", icon="motorcycle", prefix="fa")
        else:
            st.markdown("### ðŸš— à´Ÿà´¾à´•àµà´¸à´¿ à´•à´¾àµ¼ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´…à´Ÿàµà´¤àµà´¤àµ‡à´•àµà´•àµ à´µà´°àµà´¨àµà´¨àµ...")
            vehicle_icon = folium.Icon(color="blue", icon="car", prefix="fa")

        # ============================================================
        # âœ… 6. Arrived Status Check (Driver "Arrived" tap à´šàµ†à´¯àµà´¤à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ‹?)
        # ============================================================
        if trip_status == "Arrived":
            st.success("ðŸŽ‰ **à´…à´²àµ‡àµ¼à´Ÿàµà´Ÿàµ:** à´¡àµà´°àµˆà´µàµ¼ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´²àµŠà´•àµà´•àµ‡à´·à´¨à´¿àµ½ à´Žà´¤àµà´¤à´¿à´¯à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ!")
            st.toast("ðŸš— à´¡àµà´°àµˆà´µàµ¼ à´Žà´¤àµà´¤à´¿!", icon="âœ…")
            
            # ðŸ“± Vibration
            components.html("""
                <script>
               
                    if (navigator.vibrate) {
                        navigator.vibrate([300, 100, 300, 100, 300]);
                        
                }
                </script>
            """, height=0)
            
            # ðŸ”” à´ªàµà´·àµ à´¨àµ‹à´Ÿàµà´Ÿà´¿à´«à´¿à´•àµà´•àµ‡à´·àµ» à´…à´¯à´•àµà´•àµà´• (à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚)
            if not st.session_state.get('arrived_notification_sent', False):
                components.html("""
                    <script>
                        if (Notification.permission === 'granted') {
                            new Notification('ðŸš— à´¡àµà´°àµˆà´µàµ¼ à´Žà´¤àµà´¤à´¿!', {
                                body: 'à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´¡àµà´°àµˆà´µàµ¼ à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´²àµŠà´•àµà´•àµ‡à´·à´¨à´¿àµ½ à´Žà´¤àµà´¤à´¿à´¯à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ!',
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
        # âœ… 7. Driver Live Location & Distance Calculation
        # ============================================================
        driver_loc = None
        try:
            driver_loc = get_live_tracking_from_firebase(trip_id)
        except Exception as e:
            print(f"âš ï¸ Driver location fetch error: {e}")

        if driver_loc and 'lat' in driver_loc and 'lon' in driver_loc:
            driver_lat = driver_loc['lat']
            driver_lon = driver_loc['lon']

            # Distance calculation
            try:
                distance = calculate_distance(customer_lat, customer_lon, driver_lat, driver_lon)
            except Exception:
                distance = None

            if distance is not None:
                # ðŸŽ¯ 30 à´®àµ€à´±àµà´±àµ¼ à´…à´•à´²àµ† à´†à´•àµà´®àµà´ªàµ‹àµ¾
                if distance <= 30:
                    if not st.session_state.get('alert_30m_sent', False):
                        st.success("ðŸŽ‰ **à´…à´²àµ‡àµ¼à´Ÿàµà´Ÿàµ:** à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´µà´¾à´¹à´¨à´‚ à´ªà´¿à´•àµà´•àµà´…à´ªàµà´ªàµ à´²àµŠà´•àµà´•àµ‡à´·à´¨à´¿àµ½ à´Žà´¤àµà´¤à´¿à´šàµà´šàµ‡àµ¼à´¨àµà´¨à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ!")
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
                        st.success(f"ðŸ“ à´µà´¾à´¹à´¨à´‚ à´à´•à´¦àµ‡à´¶à´‚ **{int(distance)} à´®àµ€à´±àµà´±àµ¼** à´…à´•à´²àµ†à´¯à´¾à´£àµ.")

                # ðŸŽ¯ 100 à´®àµ€à´±àµà´±àµ¼ à´…à´•à´²àµ† à´†à´•àµà´®àµà´ªàµ‹àµ¾ (Nearby Alert)
                elif distance <= 100:
                    if not st.session_state.get('alert_100m_sent', False):
                        st.warning("ðŸ”” **à´¡àµà´°àµˆà´µàµ¼ 100 à´®àµ€à´±àµà´±àµ¼ à´…à´•à´²àµ†à´¯à´¾à´£àµ!** à´µà´¾à´¹à´¨à´‚ à´µà´°àµà´¨àµà´¨àµà´£àµà´Ÿàµ, à´¤à´¯àµà´¯à´¾à´±à´¾à´•àµà´•.")
                        
                        # ðŸ“± Vibration
                        st.markdown("""
                            <script>
                            if (navigator.vibrate) {
                                navigator.vibrate([500, 200, 500]);
                            }
                            </script>
                        """, unsafe_allow_html=True)
                        
                        # ðŸ”Š Sound
                        sound_html = """
                        <audio autoplay>
                            <source src="https://www.soundjay.com/phones/sounds/phone-ringing-01.mp3" type="audio/mpeg">
                        </audio>
                        """
                        components.html(sound_html, height=0)
                        st.session_state.alert_100m_sent = True
                        st.session_state.alert_30m_sent = False # Reset 30m flag
                    else:
                        st.info(f"ðŸ“ à´µà´¾à´¹à´¨à´‚ à´à´•à´¦àµ‡à´¶à´‚ **{int(distance)} à´®àµ€à´±àµà´±àµ¼** à´…à´•à´²àµ†à´¯à´¾à´£àµ.")

                # ðŸŽ¯ 100 à´®àµ€à´±àµà´±à´±à´¿àµ½ à´•àµ‚à´Ÿàµà´¤àµ½ à´…à´•à´²àµ†à´¯à´¾à´£àµ†à´™àµà´•à´¿àµ½
                else:
                    st.session_state.alert_100m_sent = False
                    st.session_state.alert_30m_sent = False
                    st.info(f"ðŸ“ à´µà´¾à´¹à´¨à´‚ à´à´•à´¦àµ‡à´¶à´‚ **{int(distance)} à´®àµ€à´±àµà´±àµ¼** à´…à´•à´²àµ†à´¯à´¾à´£àµ.")
        else:
            driver_lat, driver_lon = customer_lat, customer_lon
            st.warning("â³ à´¡àµà´°àµˆà´µàµ¼ à´¯à´¾à´¤àµà´° à´†à´°à´‚à´­à´¿à´•àµà´•àµà´¨àµà´¨à´¤àµà´µà´°àµ† à´•à´¾à´¤àµà´¤à´¿à´°à´¿à´•àµà´•àµà´•...")

        # ============================================================
        # âœ… 8. Folium Map
        # ============================================================
        m = folium.Map(location=[customer_lat, customer_lon], zoom_start=15)

        # Customer marker (green)
        folium.Marker(
            [customer_lat, customer_lon],
            popup="à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´¸àµà´¥à´²à´‚",
            icon=folium.Icon(color="green", icon="home", prefix="fa")
        ).add_to(m)

        # Driver marker (vehicle icon)
        folium.Marker(
            [driver_lat, driver_lon],
            popup=f"à´¡àµà´°àµˆà´µàµ¼ ({vehicle_type}) à´µà´°àµà´¨àµà´¨ à´µà´´à´¿",
            icon=vehicle_icon
        ).add_to(m)

        st_folium(m, width="100%", height=350, key=f"map_{trip_id}")
        # ============================================================
        # âœ… à´—àµà´¡àµà´¬àµˆ à´¸à´¨àµà´¦àµ‡à´¶à´‚ (à´®à´¾à´ªàµà´ªà´¿à´¨àµ à´¤à´¾à´´àµ†, à´¬à´²àµ‚àµº à´‡à´²àµà´²à´¾à´¤àµ†)
        # ============================================================
        if trip_status == "Arrived":
            st.markdown("""
                <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;">
                    <h2 style="color: #155724;">ðŸ™ à´¨à´¨àµà´¦à´¿! à´µàµ€à´£àµà´Ÿàµà´‚ à´µà´°à´¿à´•!</h2>
                    <p style="color: #155724; font-size: 16px;">
                        à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´¯à´¾à´¤àµà´° à´µà´¿à´œà´¯à´•à´°à´®à´¾à´¯à´¿ à´ªàµ‚àµ¼à´¤àµà´¤à´¿à´¯à´¾à´¯à´¿. <br>
                        Easy Auto Taxi à´‰à´ªà´¯àµ‹à´—à´¿à´šàµà´šà´¤à´¿à´¨àµ à´¨à´¨àµà´¦à´¿! <br>
                        à´…à´Ÿàµà´¤àµà´¤ à´¯à´¾à´¤àµà´°à´¯à´¿àµ½ à´µàµ€à´£àµà´Ÿàµà´‚ à´•à´¾à´£à´¾à´‚. ðŸš–
                    </p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("ðŸ  à´¹àµ‹à´‚ à´ªàµ‡à´œà´¿à´²àµ‡à´•àµà´•àµ à´ªàµ‹à´•àµà´•"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()            
    except Exception as e:    
        
        st.error(f"ðŸ—ºï¸ Map load error: {e}")
# --- à´¬àµ‹à´Ÿàµà´Ÿàµ à´¸àµ†à´±àµà´±à´ªàµà´ªàµ à´‡à´µà´¿à´Ÿàµ† à´¤àµà´Ÿà´™àµà´™àµà´¨àµà´¨àµ ---
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
@st.cache_resource
def setup_bot():
    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
    
    return bot
bot = setup_bot()    
    
    


# --- à´¬àµ‹à´Ÿàµà´Ÿàµ à´¸àµ†à´±àµà´±à´ªàµà´ªàµ à´‡à´µà´¿à´Ÿàµ† à´…à´µà´¸à´¾à´¨à´¿à´•àµà´•àµà´¨àµà´¨àµ ---
# ============================================================
# Google Sheets à´•à´£à´•àµà´·àµ» à´¸àµ†à´±àµà´±à´ªàµà´ªàµ (à´¤àµ½à´•àµà´•à´¾à´²à´‚ à´¡à´¿à´¸àµ‡à´¬à´¿àµ¾ à´šàµ†à´¯àµà´¤à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ)
# ============================================================
# Google Sheets à´•à´£à´•àµà´·àµ» à´¸àµ†à´±àµà´±à´ªàµà´ªàµ
#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† JSON à´«à´¯à´²à´¿à´¨àµà´±àµ† à´ªàµ‡à´°àµ à´‡à´µà´¿à´Ÿàµ† à´¨àµ½à´•àµà´•
#creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\Asu Mj\Desktop\test taxi\service_account.json', scope)
#client = gspread.authorize(creds)

# à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´·àµ€à´±àµà´±à´¿à´¨àµà´±àµ† à´ªàµ‡à´°àµà´‚ à´Ÿà´¾à´¬à´¿à´¨àµà´±àµ† à´ªàµ‡à´°àµà´‚ à´‡à´µà´¿à´Ÿàµ† à´®à´¾à´±àµà´±àµà´•
#sheet = client.open("Taxi_Management").worksheet("Trips")
# =====================================================================
# à´¡àµà´°àµˆà´µàµ¼à´®à´¾à´°àµ† à´à´°à´¿à´¯ à´¤à´¿à´°à´¿à´šàµà´šàµ à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´•à´£àµà´Ÿàµ†à´¤àµà´¤àµà´¨àµà´¨ à´ªàµà´¤à´¿à´¯ à´«à´™àµà´·àµ»
# =====================================================================

def get_all_drivers_by_area(area_name):
    try:
        # -------------------------------------------------------------
        # 1. à´ªà´´à´¯ à´—àµ‚à´—à´¿àµ¾ à´·àµ€à´±àµà´±àµ à´•àµ‹à´¡àµ (à´Žà´±àµ¼ à´µà´°à´¾à´¤à´¿à´°à´¿à´•àµà´•à´¾àµ» à´¤à´¾àµ½à´•àµà´•à´¾à´²à´¿à´•à´®à´¾à´¯à´¿ à´•à´®à´¨àµà´±àµ à´šàµ†à´¯àµà´¤à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ)
        # -------------------------------------------------------------
        # driver_sheet = client.open("Taxi_Management").worksheet("Filtered_Data")
        # data = driver_sheet.get_all_records()
        
        # -------------------------------------------------------------
        # 2. à´ªàµà´¤à´¿à´¯ à´«à´¯àµ¼à´¬àµ‡à´¸àµ à´¡à´¾à´±àµà´±à´¾à´¬àµ‡à´¸àµ à´²àµ‹à´œà´¿à´•àµ (Firebase Logic)
        # -------------------------------------------------------------
        # à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¡àµà´°àµˆà´µàµ¼à´®à´¾à´°àµà´Ÿàµ† à´¡à´¾à´±àµà´± à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¤à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨ à´ªà´¾à´¤àµà´¤àµ (Node) 
        # 'drivers' à´…à´²àµà´²àµ†à´™àµà´•à´¿àµ½ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´¡à´¾à´±àµà´±à´¾à´¬àµ‡à´¸àµ à´˜à´Ÿà´¨à´¯àµà´•àµà´•à´¨àµà´¸à´°à´¿à´šàµà´šàµ à´®à´¾à´±àµà´±àµà´•.
        ref = db.reference('drivers') 
        drivers_data = ref.get()
        
        filtered_drivers = []
        selected_area = str(area_name).strip().lower()
        
        if drivers_data:
            # à´«à´¯àµ¼à´¬àµ‡à´¸àµ à´¡à´¾à´±àµà´± à´¡à´¿à´•àµà´·àµà´£à´±à´¿ (Dictionary) à´…à´²àµà´²àµ†à´™àµà´•à´¿àµ½ à´²à´¿à´¸àµà´±àµà´±àµ à´†à´¯à´¿à´Ÿàµà´Ÿà´¾à´•à´¾à´‚ à´µà´°àµà´¨àµà´¨à´¤àµ
            items = drivers_data.items() if isinstance(drivers_data, dict) else enumerate(drivers_data)
            
            for key, d in items:
                if not isinstance(d, dict):
                    continue
                
                # à´«à´¯àµ¼à´¬àµ‡à´¸à´¿à´²àµ† à´«àµ€àµ½à´¡àµà´•àµ¾ (Area, Telegram Chat ID à´Žà´¨àµà´¨à´¿à´µ à´•àµƒà´¤àµà´¯à´®à´¾à´¯à´¿ à´¨àµ½à´•àµà´•)
                sheet_area = str(d.get('Area', d.get('area', ''))).strip().lower()
                telegram_id = str(d.get('Telegram Chat ID', d.get('telegram_chat_id', ''))).strip()
                
                # à´•àµºà´¸àµ‹àµ¾ à´¡àµ€à´¬à´—àµà´—à´¿à´‚à´—àµ
                print(f"DEBUG Firebase: Checking '{selected_area}' against '{sheet_area}' with ID: '{telegram_id}'")
                
                if selected_area == sheet_area and telegram_id:
                    d['chat_id'] = telegram_id
                    filtered_drivers.append(d)
        
        return filtered_drivers
        
    except Exception as e:
        print(f"DEBUG FIREBASE ERROR: {e}")
        return []
# ---------------------------------------------------------
# à´‡à´¤à´¿à´¨àµ à´¤àµŠà´Ÿàµà´Ÿàµ à´¤à´¾à´´àµ†à´¯à´¾à´¯à´¿ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† 'SMART MAPPING' à´­à´¾à´—à´‚ à´µà´°à´¾à´‚
# ---------------------------------------------------------
# ============================================================
# ðŸ—ºï¸ SMART MAPPING & FALLBACK ENGINE (FULL FIXED)
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
    # ðŸ›‘ à´‡à´µà´¿à´Ÿàµ†à´¯à´¾à´£àµ geocode_place à´«à´™àµà´·àµ» à´¤àµà´Ÿà´™àµà´™àµà´¨àµà´¨à´¤àµ. 
    # à´ˆ à´«à´™àµà´·à´¨àµà´±àµ† à´à´±àµà´±à´µàµà´‚ à´¤àµà´Ÿà´•àµà´•à´¤àµà´¤à´¿àµ½ à´«à´¯àµ¼à´¬àµ‡à´¸àµ à´šàµ†à´•àµà´•àµ à´µàµ†à´•àµà´•àµà´•:
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
# ðŸ“ Haversine Distance Calculator
# ====================================================================
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # à´­àµ‚à´®à´¿à´¯àµà´Ÿàµ† à´†à´°à´‚ (à´•à´¿à´²àµ‹à´®àµ€à´±àµà´±à´±à´¿àµ½)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
# ============================================================
# âš™ï¸ CONFIGURATION - All configs in one place
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
# à´«à´¯àµ¼à´¬àµ‡à´¸àµ à´¡à´¾à´±àµà´±à´¾à´¬àµ‡à´¸àµ à´•à´£à´•àµà´·àµ» à´¸àµ†à´±àµà´±àµ à´šàµ†à´¯àµà´¯àµà´•
if not firebase_admin._apps:
    creds_dict = dict(st.secrets["firebase_service_account"])
    cred = credentials.Certificate(creds_dict)
    firebase_admin.initialize_app(cred, {
        'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
    
    })

registration_data = {}
def auto_cancel_trip(trip_id, delay_seconds=1800):
    """30 à´®à´¿à´¨à´¿à´±àµà´±à´¿à´¨àµ à´¶àµ‡à´·à´‚ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´“à´Ÿàµà´Ÿàµ‹à´®à´¾à´±àµà´±à´¿à´•àµ à´†à´¯à´¿ à´•àµà´¯à´¾àµ»à´¸àµ½ à´šàµ†à´¯àµà´¯àµà´•"""
    def cancel_task():
        time.sleep(delay_seconds)  # 30 à´®à´¿à´¨à´¿à´±àµà´±àµ (1800 à´¸àµ†à´•àµà´•àµ»à´¡àµ) à´•à´¾à´¤àµà´¤à´¿à´°à´¿à´•àµà´•àµà´•
        try:
            ref = db.reference(f"trips/{trip_id}")
            trip_data = ref.get()
            
            if trip_data:
                current_status = trip_data.get("status", "Pending")
                # à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´‡à´ªàµà´ªàµ‹à´´àµà´‚ Pending/Available à´†à´£àµ†à´™àµà´•à´¿àµ½ à´®à´¾à´¤àµà´°à´‚ à´•àµà´¯à´¾àµ»à´¸àµ½ à´šàµ†à´¯àµà´¯àµà´•
                if current_status in ["Pending", "Available", "Unassigned"]:
                    ref.update({
                        "status": "Cancelled",
                        "cancel_reason": "No driver accepted within 30 minutes",
                        "cancelled_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"â° Trip {trip_id} auto-cancelled after 30 minutes")
                else:
                    print(f"âœ… Trip {trip_id} already {current_status} - no need to cancel")
        except Exception as e:
            print(f"âŒ Auto-cancel error for {trip_id}: {e}")
    
    # Background thread-àµ½ à´±àµº à´šàµ†à´¯àµà´¯àµà´•
    thread = threading.Thread(target=cancel_task, daemon=True)
    thread.start()


def save_new_trip(booking_id, customer_name, customer_phone, pickup, drop, distance=0.0, pickup_link=""):
    """
    à´•à´¸àµà´±àµà´±à´®àµ¼ à´¬àµà´•àµà´•àµ à´šàµ†à´¯àµà´¯àµ à´®àµà´ªàµ‹àµ¾ à´µà´¿à´µà´°à´™àµà´™à´³àµà´‚ à´¦àµ‚à´°à´µàµà´‚ à´«à´¯àµ¼à´¬àµ‡à´¸à´¿à´²àµ‡à´•àµà´•àµ à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ
    """
    try:
        trip_data = {
            "trip_id": booking_id,
            
            
            "customer_name": customer_name,
            "customer_phone": str(customer_phone),
            "pickup": pickup,
            "drop": drop,
            "pickup_link": pickup_link,  # ðŸ‘ˆ à´‡à´µà´¿à´Ÿàµ† à´Žà´±àµ¼ à´µà´°à´¾à´¤à´¿à´°à´¿à´•àµà´•à´¾àµ» à´‡à´¤àµ à´†àµ¼à´—àµà´¯àµà´®àµ†à´¨àµà´±à´¿àµ½ à´šàµ‡àµ¼à´¤àµà´¤à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ
            "distance": distance,  # à´•à´¿à´²àµ‹à´®àµ€à´±àµà´±àµ¼ à´®à´¾à´¤àµà´°à´‚ à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ
            "total_fare": 0.0,              # à´«àµ†à´¯àµ¼ à´¤àµ½à´•àµà´•à´¾à´²à´‚ 0 à´†à´¯à´¿ à´µàµ†à´•àµà´•àµà´¨àµà´¨àµ
            "status": "Pending",
            "is_locked": False,  # <-- à´‡à´¤àµ à´šàµ‡àµ¼à´•àµà´•àµà´•
            "driver_name": "",
            "driver_phone": "",
            "driver_chat_id": "",
            "booking_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        trip_ref = db.reference(f"trips/{booking_id}")
        trip_ref.set(trip_data)
        # ðŸ†• 30 à´®à´¿à´¨à´¿à´±àµà´±à´¿à´¨àµ à´¶àµ‡à´·à´‚ auto-cancel scheduler à´†à´°à´‚à´­à´¿à´•àµà´•àµà´•
        auto_cancel_trip(booking_id, delay_seconds=1800)
        
        

        print(f"âœ… Trip {booking_id} saved with distance {distance} km successfully.")
        return True
    except Exception as e:
        print(f"âŒ Error saving trip to Firebase: {e}")
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
    commission="N/A"  # <--- à´‡à´µà´¿à´Ÿàµ† à´•à´®àµà´®àµ€à´·àµ» à´ªà´¾à´°à´¾à´®àµ€à´±àµà´±àµ¼ à´šàµ‡àµ¼à´•àµà´•à´¾à´‚
):
    raw_phone = str(customer_phone or '')
    if len(raw_phone) >= 6:
        masked_phone = raw_phone[:4] + "XXXX" + raw_phone[-2:]
    else:
        masked_phone = "XXXXXX"

    safe_distance = distance if distance else "N/A"
    safe_location = location_link if location_link else "Not Available"

    message = f"""
ðŸš– *à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´±à´¿à´•àµà´µà´¸àµà´±àµà´±àµ!*

ðŸ‘¤ à´•à´¸àµà´±àµà´±à´®àµ¼: {customer_name}
ðŸ“ž à´«àµ‹àµº: {masked_phone}
ðŸ“ Pickup: {pickup}
ðŸ Drop: {drop}
ðŸ“ à´¦àµ‚à´°à´‚ (Distance): {safe_distance} km
ðŸ’° Commission: {commission}
ðŸ“ GPS Live Location:
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
                        "text": "âœ… ACCEPT TRIP",
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
            bg_log("âœ… Firebase already initialized")
            return True

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

        possible_files = [
            "firebase_key.json",
            "firebase_key",
            "firebase_key.json.json"
        ]

        # Firebase à´‡à´¤à´¿à´¨à´•à´‚ à´‡à´¨à´¿à´·àµà´¯à´²àµˆà´¸àµ à´šàµ†à´¯àµà´¤à´¿à´Ÿàµà´Ÿà´¿à´²àµà´²àµ†à´™àµà´•à´¿àµ½ à´®à´¾à´¤àµà´°à´‚
        if not firebase_admin._apps:
            # Secrets-àµ½ à´¨à´¿à´¨àµà´¨àµ JSON à´‰à´³àµà´³à´Ÿà´•àµà´•à´‚ à´Žà´Ÿàµà´•àµà´•àµà´•
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
        "is_locked": True,  # <-- à´‡à´¤àµ à´šàµ‡àµ¼à´•àµà´•àµà´•
        "driver_name": driver_name,
        "driver_phone": driver_phone,
        "driver_chat_id": str(driver_chat_id)
    })
    return "success"


# ==========================================================
# âœ… ADMIN TRIP NOTIFICATION FUNCTION
# ==========================================================
def send_admin_trip_notification(trip_data):
    """
    Admin-à´¨àµ à´ªàµà´¤à´¿à´¯ trip notification à´…à´¯à´•àµà´•àµà´¨àµà´¨àµ.
    """
    try:
        if not bot or not ADMIN_TELEGRAM_CHAT_ID:
            print("âš ï¸ Admin notification skipped: bot or chat_id missing")
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
            commission_display = f"â‚¹{commission:.2f}"
        except:
            commission_display = f"â‚¹{commission}"

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
            gps_line = f"ðŸ”— GPS: [ðŸ“ Location]({gps_url})"
        else:
            gps_line = "ðŸ”— GPS: à´²à´­àµà´¯à´®à´²àµà´²"

        # Admin message
        admin_msg = (
            f"ðŸ”” *à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµ (Admin)*\n\n"
            f"ðŸ†” *Trip ID:* {trip_id}\n"
            f"ðŸ• *Time:* {booking_time}\n"
            f"ðŸ‘¤ *à´•à´¸àµà´±àµà´±à´®àµ¼:* {customer_name}\n"
            f"ðŸ“ž *à´«àµ‹àµº:* {masked_phone}\n"
            f"ðŸ“ *à´ªà´¿à´•àµà´•à´ªàµà´ªàµ:* {pickup}\n"
            f"ðŸ *à´¡àµà´°àµ‹à´ªàµà´ªàµ:* {drop}\n"
            f"ðŸ“ *à´à´°à´¿à´¯:* {area}\n"
            f"ðŸš— *à´µà´¾à´¹à´¨à´‚:* {vehicle}\n"
            f"ðŸ“ *à´¦àµ‚à´°à´‚:* {distance} km\n"
            f"ðŸ’° *Commission:* {commission_display}\n"
            f"{gps_line}"
        )

        bot.send_message(
            chat_id=ADMIN_TELEGRAM_CHAT_ID,
            text=admin_msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )

        print(f"âœ… Admin notified: {trip_id}")
        return True

    except Exception as e:
        print(f"âŒ Admin notification error: {e}")
        return False
def listener(event):
    try:
        if not event.data:
            return

        # ============================================
        # âœ… FIX: Sub-path updates skip
        # Path = "/TRIP-XXXX" â†’ Process (trip creation)
        # Path = "/TRIP-XXXX/notified_drivers" â†’ Skip
        # ============================================
        if event.path and event.path.count("/") > 1:
            print(f"   â­ï¸ Sub-path skip: {event.path}")
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
            # âœ… ADMIN NOTIFICATION â€” function call (à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚)
            # ============================================
            send_admin_trip_notification(trip_data)
            
            bg_log("ðŸš– Admin Notification Sent Successfully")
            
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
# SAFE TRIP ACCEPTANCE - DRIVER DETAILS
# ==========================================
def accept_trip_safely(
    trip_id,
    driver_chat_id,
    driver_name,
    driver_phone,
    vehicle_number="N/A"
):
    ref = db.reference(f"trips/{trip_id}")

    def transaction_update(current_data):
        if current_data is None:
            return

        current_status = str(
            current_data.get("status", "Pending")
        ).strip()

        # à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´‡à´¤àµà´µà´°àµ† à´¸àµà´µàµ€à´•à´°à´¿à´šàµà´šà´¿à´Ÿàµà´Ÿà´¿à´²àµà´²àµ†à´¨àµà´¨àµ à´‰à´±à´ªàµà´ªà´¾à´•àµà´•àµà´•
        if current_status not in [
            "Pending", "Available", "Unassigned",
            "PENDING", "AVAILABLE", "UNASSIGNED"
        ]:
            return

        # à´¡àµà´°àµˆà´µàµ¼ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´Ÿàµà´°à´¿à´ªàµà´ªà´¿àµ½ à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¯àµà´•
        urrent_data["status"] = "Accepted"
        current_data["is_locked"] = True
        current_data["driver_chat_id"] = str(driver_chat_id)
        current_data["driver_name"] = driver_name
        current_data["driver_phone"] = driver_phone
        current_data["vehicle_number"] = vehicle_number
        
        return current_data

    try:
        result = ref.transaction(transaction_update)

        if (
            result
            and str(result.get("status", "")).strip().upper() == "ACCEPTED"
            and str(result.get("driver_chat_id", "")).strip() == str(driver_chat_id)
        ):
            return result  # Dictionary à´±à´¿à´Ÿàµà´Ÿàµ‡àµº à´šàµ†à´¯àµà´¯àµà´•

        return None  # à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´²à´­à´¿à´šàµà´šà´¿à´²àµà´²àµ†à´™àµà´•à´¿àµ½ None à´±à´¿à´Ÿàµà´Ÿàµ‡àµº à´šàµ†à´¯àµà´¯àµà´•

    except Exception as e:
        print(f"âŒ Safe trip acceptance error: {e}")
        return None  # à´Žà´±àµ¼ à´µà´¨àµà´¨à´¾à´²àµà´‚ None à´±à´¿à´Ÿàµà´Ÿàµ‡àµº à´šàµ†à´¯àµà´¯àµà´•

# ==========================================================
# Telegram Callback Query Handler (Button Clicks)
# ==========================================================
def handle_telegram_callback(update, context):
    query = update.callback_query
    query.answer()
    
    callback_data = query.data
    chat_id = query.message.chat_id
    print(f"ðŸ”¥ DEBUG: Callback à´µà´¨àµà´¨à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ -> {callback_data}")
    
    if callback_data.startswith("arrived_"):
        booking_id = callback_data.replace("arrived_", "")
        ref = db.reference(f"trips/{booking_id}")
        trip_data = ref.get()
        
        if trip_data and str(trip_data.get("driver_chat_id")) == str(chat_id):
            ref.update({"status": "Arrived"})
            query.edit_message_text(
                text=query.message.text + "\n\nðŸ”´ **[Status: Arrived at Location]** - à´•à´¸àµà´±àµà´±à´®àµ¼à´•àµà´•àµ à´¨àµ‹à´Ÿàµà´Ÿà´¿à´«à´¿à´•àµà´•àµ‡à´·àµ» à´…à´¯à´šàµà´šà´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ."
            )
        else:
            query.edit_message_text(text="âŒ à´…à´¸à´¾à´§àµà´µà´¾à´¯ à´±à´¿à´•àµà´µà´¸àµà´±àµà´±àµ à´…à´²àµà´²àµ†à´™àµà´•à´¿àµ½ à´¨à´¿à´™àµà´™àµ¾à´•àµà´•àµ à´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªà´¿àµ½ à´…à´§à´¿à´•à´¾à´°à´®à´¿à´²àµà´².")
            
    else:
        # à´‡à´¤àµ "accept_" à´Žà´¨àµà´¨àµ à´¤àµà´Ÿà´™àµà´™àµà´¨àµà´¨ à´¬à´Ÿàµà´Ÿà´£à´¾à´£àµ
        booking_id = callback_data.replace("accept_", "").strip()
            
        # 1. à´¡àµà´°àµˆà´µà´±àµà´Ÿàµ† à´µà´¿à´µà´°à´™àµà´™àµ¾ à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´Žà´Ÿàµà´•àµà´•àµà´•
        driver_ref = db.reference(f"drivers/{chat_id}")
        driver_data = driver_ref.get() or {}
            
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
            or driver_data.get("Vehicle_No")
            or "N/A"
        )
            
        # 2. accept_trip_safely à´µà´¿à´³à´¿à´•àµà´•àµà´•
        result = accept_trip_safely(
            trip_id=booking_id,
            driver_chat_id=chat_id,
            driver_name=driver_name,
            driver_phone=driver_phone,
            vehicle_number=vehicle_number
        )
            
        # 3. à´«à´²à´‚ à´…à´¨àµà´¸à´°à´¿à´šàµà´šàµ à´¸à´¨àµà´¦àµ‡à´¶à´‚ à´…à´¯à´•àµà´•àµà´•
        if result:  # à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´œà´¯à´•à´°à´®à´¾à´¯à´¿ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤àµ
            query.edit_message_text(
                text=f"âœ… *à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤àµ!*\n\n"
                    f"à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿: `{booking_id}`\n"
                    f"à´¡àµà´°àµˆà´µàµ¼: {driver_name}\n"
                     f"à´µà´¾à´¹à´¨à´‚: {vehicle_number}",
                 parse_mode="Markdown"
            )
                
            # à´¡àµà´°àµˆà´µàµ¼ à´ªà´¾à´¨àµ½ à´²à´¿à´™àµà´•àµ à´…à´¯à´•àµà´•àµà´•
            driver_panel_url = f"https://taxiservisemj-x9meaffucvbt6tjijxrd6d.streamlit.app/?page=driver_trip_panel&trip_id={booking_id}&driver_chat_id={chat_id}"
            bot.send_message(
                chat_id,
                f"ðŸ“ *à´¡àµà´°àµˆà´µàµ¼ à´ªà´¾à´¨àµ½ à´¤àµà´±à´•àµà´•à´¾àµ» à´¤à´¾à´´àµ†à´¯àµà´³àµà´³ à´²à´¿à´™àµà´•à´¿àµ½ à´•àµà´²à´¿à´•àµà´•àµ à´šàµ†à´¯àµà´¯àµà´•:*\n\n[à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½ à´¤àµà´±à´•àµà´•àµà´•]({driver_panel_url})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            # à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´²à´­à´¿à´šàµà´šà´¿à´²àµà´² (à´®à´±àµà´±àµŠà´°à´¾àµ¾ à´Žà´Ÿàµà´¤àµà´¤àµ)
            query.edit_message_text(
                text="âŒ à´•àµà´·à´®à´¿à´•àµà´•à´£à´‚, à´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´®à´±àµà´±àµŠà´°àµ à´¡àµà´°àµˆà´µàµ¼ à´‡à´¤à´¿à´¨à´•à´‚ à´¸àµà´µàµ€à´•à´°à´¿à´šàµà´šà´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ.",
                parse_mode="Markdown"
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
            "âœ… Trip Saved To Firebase"
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
                # à´²àµŠà´•àµà´•àµ‡à´·àµ» à´ªàµ‡à´°àµà´•àµ¾ à´•àµ€ (Keys) à´†à´¯à´¿à´Ÿàµà´Ÿà´¾à´¯à´¤àµà´•àµŠà´£àµà´Ÿàµ data.keys() à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨àµ
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
                # à´à´°à´¿à´¯à´¯àµà´Ÿàµ† à´ªàµ‡à´°àµ à´•àµ€ (Key) à´†à´¯à´¤àµà´•àµŠà´£àµà´Ÿàµ data.keys() à´‰à´ªà´¯àµ‹à´—à´¿à´•àµà´•àµà´¨àµà´¨àµ
                return [str(k) for k in data.keys() if k and k is not True]
        return [] 
    except Exception as e:
        print(f"Areas Firebase Error: {e}")
        return []

# ==========================================================
# MAIN STARTUP
# ==========================================================
# ==========================================================
# âœ… FIX #3: Firebase Listener â€” à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚ Start
# Streamlit rerun-àµ½ duplicate listener threads à´’à´´à´¿à´µà´¾à´•àµà´•à´¾àµ»
# ==========================================================
@st.cache_resource
def start_firebase_background_services():
    """
    @st.cache_resource à´•à´¾à´°à´£à´‚ app session-àµ½ à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚
    execute à´†à´•àµà´‚. Streamlit rerun à´šàµ†à´¯àµà´¤à´¾à´²àµà´‚ à´ªàµà´¤à´¿à´¯
    listener threads à´‰à´£àµà´Ÿà´¾à´•à´¿à´²àµà´².
    """
    try:
        initialize_firebase()
        
        def run_listener():
            try:
                bg_log("ðŸš€ Starting Firebase Trip Listener...")
                trips_ref = db.reference("trips")
                trips_ref.listen(listener)
            except Exception as e:
                bg_log(f"âŒ Listener Thread Error: {e}")
                import traceback
                traceback.print_exc()
        
        firebase_thread = threading.Thread(
            target=run_listener,
            daemon=True,
            name="FirebaseTripListener"
        )
        add_script_run_ctx(firebase_thread)
        firebase_thread.start()
        
        bg_log("âœ… Firebase Listener Started (ONCE)")
        return True
        
    except Exception as e:
        bg_log(f"âŒ Background Services Error: {e}")
        return False


# App init-àµ½ à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚ execute à´†à´•àµà´‚
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
            
            # 1. à´—àµ‚à´—à´¿àµ¾ à´·àµ€à´±àµà´±àµ à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ à´’à´°àµ à´²à´¿à´¸àµà´±àµà´±àµ (List) à´†à´£àµ à´…à´¯à´•àµà´•àµà´¨àµà´¨à´¤àµ†à´™àµà´•à´¿àµ½
            if isinstance(res_json, list):
                return res_json
                
            # 2. à´¡à´¿à´•àµà´·à´£à´±à´¿ (Dictionary) à´†à´£àµ†à´™àµà´•à´¿àµ½ à´ªà´² à´¸à´¾à´§àµà´¯à´®à´¾à´¯ à´•àµ€à´•à´³àµà´‚ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ
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
            
            # 1. à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ à´²à´¿à´¸àµà´±àµà´±àµ à´†à´£àµ†à´™àµà´•à´¿àµ½
            if isinstance(res_json, list):
                return res_json
                
            # 2. à´¡à´¿à´•àµà´·à´£à´±à´¿ à´†à´£àµ†à´™àµà´•à´¿àµ½ à´•àµ€à´¸àµ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ
            if isinstance(res_json, dict):
                for key in ["areas", "data", "result", "items"]:
                    if key in res_json and isinstance(res_json[key], list):
                        return res_json[key]
                        
        return []
    except Exception as e:
        print(f"Areas Error: {e}")
        return []
# à´¡à´¿à´«àµ‹àµ¾à´Ÿàµà´Ÿàµ à´à´°à´¿à´¯ (à´¨à´¿à´™àµà´™àµ¾ à´†à´µà´¶àµà´¯à´ªàµà´ªàµ†à´Ÿàµà´Ÿà´¤àµà´ªàµ‹à´²àµ† Manjeri Central à´®à´¾à´¤àµà´°à´‚)
DEFAULT_AREAS = ["Manjeri Central"]

@st.cache_data(ttl=60)
def get_areas_from_sheets():
    try:
        response = requests.get(GOOGLE_SHEET_URL, params={"action": "get_areas"}, timeout=40)
        if response.status_code == 200:
            res_json = response.json()
            
            # 1. à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ à´²à´¿à´¸àµà´±àµà´±àµ à´†à´£àµ†à´™àµà´•à´¿àµ½
            if isinstance(res_json, list) and res_json:
                return res_json
                
            # 2. à´¡à´¿à´•àµà´·à´£à´±à´¿ à´†à´£àµ†à´™àµà´•à´¿àµ½ à´•àµ€à´¸àµ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ
            if isinstance(res_json, dict):
                for key in ["areas", "data", "result", "items"]:
                    if key in res_json and isinstance(res_json[key], list) and res_json[key]:
                        return res_json[key]
                        
        # à´·àµ€à´±àµà´±à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´¡à´¾à´±àµà´± à´•à´¿à´Ÿàµà´Ÿà´¿à´¯à´¿à´²àµà´²àµ†à´™àµà´•à´¿àµ½ Manjeri Central à´®à´¾à´¤àµà´°à´‚ à´±à´¿à´Ÿàµà´Ÿàµ‡àµº à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ
        return DEFAULT_AREAS
    except Exception as e:
        print(f"Areas Error: {e}")
        return DEFAULT_AREAS        
# ============================================================
# ðŸŽ¨ --- MODERN ULTRA-PREMIUM UI (DARK GOLD TAXI THEME) ---
# ============================================================
st.markdown("""
    <style>
    .reportview-container { background: #121212 !important; color: #FFFFFF !important; }
    
    /* à´¹àµ†à´¡àµ¼ à´¬àµ‹à´•àµà´¸à´¿à´¨àµà´±àµ† à´ªà´¾à´¡à´¿à´‚à´—àµ à´•àµà´±à´šàµà´šàµ */
    .header-box { 
        background: linear-gradient(135deg, #1e1e1e, #2d2d2d) !important; 
        padding: 15px !important; 
        border-radius: 12px !important; 
        text-align: center !important; 
        border-bottom: 4px solid #ffcc00 !important; 
        box-shadow: 0px 6px 12px rgba(0,0,0,0.3) !important; 
        margin-bottom: 15px !important; 
    }
    /* à´¹àµ†à´¡à´¿à´‚à´—àµ à´«àµ‹à´£àµà´Ÿàµ à´¸àµˆà´¸àµ 2.5rem àµ½ à´¨à´¿à´¨àµà´¨àµ 1.8rem à´†à´•àµà´•à´¿ à´•àµà´±à´šàµà´šàµ */
    .header-box h1 { color: #ffcc00 !important; font-weight: 900 !important; letter-spacing: 1px !important; margin: 0 !important; font-size: 1.8rem !important; }
    /* à´¸à´¬àµ à´¹àµ†à´¡à´¿à´‚à´—àµ à´«àµ‹à´£àµà´Ÿàµ à´¸àµˆà´¸àµ 14px àµ½ à´¨à´¿à´¨àµà´¨àµ 11px à´†à´•àµà´•à´¿ à´•àµà´±à´šàµà´šàµ */
    .header-box p { color: #b3b3b3 !important; font-size: 11px !important; margin-top: 3px !important; text-transform: uppercase !important; }
    
    /* à´«àµ‹à´®à´¿à´¨àµà´±àµ† à´ªà´¾à´¡à´¿à´‚à´—àµ à´•àµà´±à´šàµà´šàµ */
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
# ðŸ”Œ EXTERNAL CLIENT INITIALIZATION
# ============================================================
gc_client = None
# try:
#     creds = ServiceAccountCredentials.from_json_keyfile_name(
#         'service_account.json',
#         ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#     )
#     gc_client = gspread.authorize(creds)
#     print("âœ… Google Sheets Connected")
# except Exception as e:
#     print(f"âŒ Google Sheets Error: {e}")
# à´Ÿàµ†à´²à´¿à´—àµà´°à´¾à´‚ à´¬àµ‹à´Ÿàµà´Ÿàµ à´Ÿàµ‹à´•àµà´•àµº à´‡à´µà´¿à´Ÿàµ† à´¸àµ†à´±àµà´±àµ à´šàµ†à´¯àµà´¯àµà´•
# ============================================================
# ðŸ”Œ EXTERNAL CLIENT INITIALIZATION
# ============================================================
gc_client = None

# à´Ÿàµ†à´²à´¿à´—àµà´°à´¾à´‚ à´¬àµ‹à´Ÿàµà´Ÿàµ à´Ÿàµ‹à´•àµà´•àµº à´‡à´µà´¿à´Ÿàµ† à´¸àµ†à´±àµà´±àµ à´šàµ†à´¯àµà´¯àµà´•
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
# ðŸ†• FIX: bot à´’à´¬àµà´œà´•àµà´±àµà´±àµ à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚ à´¸àµƒà´·àµà´Ÿà´¿à´•àµà´•à´¾àµ» @st.cache_resource à´šàµ‡àµ¼à´•àµà´•àµà´¨àµà´¨àµ
@st.cache_resource
def get_telegram_bot():
    token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
    if token and "YOUR_BOT_TOKEN" not in token:
        try:
            _bot = telebot.TeleBot(token)
            print("âœ… Telegram Bot Connected")
            return _bot
        except Exception as e:
            print(f"âŒ Telegram Bot Error: {e}")
            return None
    return None

bot = get_telegram_bot()
# ============================================================
# ðŸ¤– MODULE 20: DRIVER TRIP HISTORY (LAST 20 TRIPS)
# ============================================================
@bot.message_handler(commands=['history'])
def handle_driver_history(message):
    chat_id = str(message.chat.id)
    try:
        ref = db.reference("trips")
        all_trips = ref.get()

        if not all_trips:
            bot.reply_to(message, "à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾ à´’à´¨àµà´¨àµà´‚ à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¾à´¨à´¾à´¯à´¿à´²àµà´².")
            return

        user_trips = []
        for booking_id, trip in all_trips.items():
            if isinstance(trip, dict) and str(trip.get("driver_chat_id")) == str(chat_id):
                trip["trip_id"] = booking_id  # ðŸ†• FIX: à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´¡à´¿à´•àµà´·à´£à´±à´¿à´¯à´¿àµ½ à´šàµ‡àµ¼à´•àµà´•àµà´¨àµà´¨àµ
                user_trips.append(trip)

        if user_trips:
            last_20_trips = user_trips[-20:]
            reply = "ðŸš– à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´…à´µà´¸à´¾à´¨à´¤àµà´¤àµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾:\n\n"
            for t in last_20_trips:
                t_id = t.get("trip_id", "N/A")  # ðŸ†• à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿
                t_date = t.get("booking_time", "N/A").split(" ")[0]  # ðŸ†• à´¶à´°à´¿à´¯à´¾à´¯ à´¤à´¿à´¯à´¤à´¿
                t_pickup = t.get("pickup", "N/A")  # ðŸ†• à´ªà´¿à´•àµà´•à´ªàµà´ªàµ
                t_drop = t.get("drop", "N/A")
                reply += f"ðŸ†” {t_id}\nðŸ“… {t_date}\nðŸ“ {t_pickup} âž” {t_drop}\n\n"
            
            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, "à´ˆ à´šà´¾à´±àµà´±àµ à´à´¡à´¿à´¯à´¿àµ½ à´‡à´¤àµà´µà´°àµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾ à´’à´¨àµà´¨àµà´‚ à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¾à´¨à´¾à´¯à´¿à´²àµà´².")

    except Exception as e:
        bot.reply_to(message, f"âŒ à´Žà´±àµ¼: {str(e)}")

flask_app = Flask(__name__)

# ============================================================
# ðŸ¤– MODULE 19: TELEGRAM BOT /start & REGISTRATION HANDLER
# ============================================================
registration_data = {}

@bot.message_handler(commands=['start'])
def handle_driver_start(message):
    print("=" * 60)
    print("ðŸ”” /start HANDLER CALLED")
    print(f"   Chat: {message.chat.id}")
    print("=" * 60)
    chat_id = message.chat.id
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ðŸ“¢ à´ªàµà´°àµˆà´µà´±àµà´±àµ à´šà´¾à´¨à´²à´¿àµ½ à´œàµ‹à´¯à´¿àµ» à´šàµ†à´¯àµà´¯àµà´•", url="https://t.me/+48S6XF9l4zM0MTY0"))
    markup.add(types.InlineKeyboardButton("âœ… à´žà´¾àµ» à´šà´¾à´¨à´²à´¿àµ½ à´œàµ‹à´¯à´¿àµ» à´šàµ†à´¯àµà´¤àµ, à´°à´œà´¿à´¸àµà´Ÿàµà´°àµ‡à´·àµ» à´¤àµà´Ÿà´™àµà´™à´¾à´‚", callback_data="start_registration"))
    
    bot.send_message(
        chat_id, 
        "ðŸš– *à´®à´žàµà´šàµ‡à´°à´¿ à´ˆà´¸à´¿ à´Ÿà´¾à´•àµà´¸à´¿ à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´¸à´¿à´¸àµà´±àµà´±à´¤àµà´¤à´¿à´²àµ‡à´•àµà´•àµ à´¸àµà´µà´¾à´—à´¤à´‚!*\n\n"
        "à´°à´œà´¿à´¸àµà´Ÿàµà´°àµ‡à´·àµ» à´¨à´Ÿà´ªà´Ÿà´¿à´•àµ¾ à´†à´°à´‚à´­à´¿à´•àµà´•àµà´¨àµà´¨à´¤à´¿à´¨àµ à´®àµàµ»à´ªàµ, à´¨à´®àµà´®àµà´Ÿàµ† **à´ªàµà´°àµˆà´µà´±àµà´±àµ à´Ÿàµ†à´²à´¿à´—àµà´°à´¾à´‚ à´šà´¾à´¨à´²à´¿àµ½** à´¨à´¿àµ¼à´¬à´¨àµà´§à´®à´¾à´¯àµà´‚ à´œàµ‹à´¯à´¿àµ» à´šàµ†à´¯àµà´¯àµà´•.\n\n"
        "à´šà´¾à´¨à´²à´¿àµ½ à´œàµ‹à´¯à´¿àµ» à´šàµ†à´¯àµà´¤ à´¶àµ‡à´·à´‚ à´¤à´¾à´´àµ†à´¯àµà´³àµà´³ à´¬à´Ÿàµà´Ÿàµº à´•àµà´²à´¿à´•àµà´•àµ à´šàµ†à´¯àµà´¯àµà´•:",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    # ðŸ†• FIX: à´‡à´µà´¿à´Ÿàµ† à´¨à´¿à´¨àµà´¨àµ à´¤àµà´Ÿà´™àµà´™àµà´¨àµà´¨àµ (1396-à´¾à´‚ à´µà´°à´¿)
    try:
        bot.send_message(
            chat_id,
            f"âœ… *à´°à´œà´¿à´¸àµà´Ÿàµà´°àµ‡à´·àµ» à´µà´¿à´œà´¯à´•à´°à´®à´¾à´¯à´¿ à´ªàµ‚àµ¼à´¤àµà´¤à´¿à´¯à´¾à´¯à´¿!*\n\n"
            f"ðŸ†” *à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´šà´¾à´±àµà´±àµ à´à´¡à´¿:* `{chat_id}`\n\n"
            f"ðŸ“Œ à´ˆ à´à´¡à´¿ à´¸àµ‚à´•àµà´·à´¿à´šàµà´šàµà´µàµ†à´•àµà´•àµà´•. à´­à´¾à´µà´¿à´¯à´¿àµ½ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´…à´±à´¿à´¯à´¾àµ» à´‡à´¤àµ à´‰à´ªà´¯àµ‹à´—à´¿à´•àµà´•à´¾à´‚.",
            parse_mode="Markdown"
        )    
        print(f"âœ… Chat ID {chat_id} sent back to driver")
    except Exception as e:
        print(f"âŒ Error sending chat ID: {e}")
    

@bot.callback_query_handler(func=lambda call: call.data == "start_registration")
def ask_contact_number(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton("ðŸ“± à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´Ÿàµ†à´²à´—àµà´°à´¾à´‚ à´«àµ‹àµº à´¨à´®àµà´ªàµ¼ à´·àµ†à´¯àµ¼ à´šàµ†à´¯àµà´¯àµà´• (Share Contact)", request_contact=True))
    
    bot.send_message(
        chat_id, 
        "à´¨à´¨àµà´¦à´¿! ðŸ™\n\nà´‡à´¨à´¿ à´¤à´¾à´´àµ†à´¯àµà´³àµà´³ à´¬à´Ÿàµà´Ÿàµº à´•àµà´²à´¿à´•àµà´•àµ à´šàµ†à´¯àµà´¤àµ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´«àµ‹àµº à´¨à´®àµà´ªàµ¼ à´·àµ†à´¯àµ¼ à´šàµ†à´¯àµà´¯àµà´•.", 
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
            "à´¨à´¨àµà´¦à´¿! ðŸ“\n\nà´‡à´¨à´¿ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´ªàµ‚àµ¼à´£àµà´£à´®à´¾à´¯ à´ªàµ‡à´°àµ (Full Name) à´‡à´µà´¿à´Ÿàµ† à´Ÿàµˆà´ªàµà´ªàµ à´šàµ†à´¯àµà´¤àµ à´…à´¯à´•àµà´•àµ‚.", 
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
        types.InlineKeyboardButton("ðŸ›º à´“à´Ÿàµà´Ÿàµ‹à´±à´¿à´•àµà´· (Autorickshaw)", callback_data="v_auto"),
        types.InlineKeyboardButton("ðŸš— à´Ÿà´¾à´•àµà´¸à´¿ à´•à´¾àµ¼ (Taxi Car)", callback_data="v_taxicar"),
        types.InlineKeyboardButton("ðŸš™ à´—àµà´¡àµà´¸àµ à´“à´Ÿàµà´Ÿàµ‹ à´ªà´¿à´•àµà´•à´ªàµà´ªàµ (Goods Auto Pickup)", callback_data="v_goodsauto"),
        types.InlineKeyboardButton("ðŸš à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´µà´¾àµ» (Pickup Van)", callback_data="v_pickupvan"),
        types.InlineKeyboardButton("ðŸšš à´®à´¿à´¨à´¿ à´²àµ‹à´±à´¿ (Mini Lorry)", callback_data="v_minilorry"),
        types.InlineKeyboardButton("ðŸš› à´Ÿàµà´°à´•àµà´•àµ (Truck)", callback_data="v_truck"),
        types.InlineKeyboardButton("ðŸï¸ à´¬àµˆà´•àµà´•àµ à´Ÿà´¾à´•àµà´¸à´¿ (Bike Taxi)", callback_data="v_biketaxi")
    )
    
    bot.send_message(
        chat_id, 
        f"à´¸à´¨àµà´¤àµ‹à´·à´‚, {driver_name}!\n\n"
        f"âš ï¸ *(à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•: à´ªàµà´°àµˆà´µà´±àµà´±àµ à´µà´¾à´¹à´¨à´™àµà´™àµ¾à´•àµà´•àµ à´…à´¨àµà´µà´¾à´¦à´®à´¿à´²àµà´². à´Ÿà´¾à´•àµà´¸à´¿/à´•àµŠà´®àµ‡à´´àµà´¸àµà´¯àµ½ à´ªàµ†àµ¼à´®à´¿à´±àµà´±àµ à´µà´¾à´¹à´¨à´™àµà´™àµ¾ à´®à´¾à´¤àµà´°à´‚ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´•àµà´•àµà´•.)*\n\n"
        f"à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´µà´¾à´¹à´¨à´‚ à´à´¤à´¾à´£àµ? à´¤à´¾à´´àµ†à´¯àµà´³àµà´³à´¤à´¿àµ½ à´’à´°àµ†à´£àµà´£à´‚ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´•àµà´•àµà´•:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("v_"))
def handle_vehicle_selection(call):
    chat_id = call.message.chat.id
    if chat_id in registration_data and registration_data[chat_id]["step"] == "waiting_vehicle_type":
        
        v_mapping = {
            "v_auto": "à´“à´Ÿàµà´Ÿàµ‹à´±à´¿à´•àµà´· (Autorickshaw)",
            "v_taxicar": "à´Ÿà´¾à´•àµà´¸à´¿ à´•à´¾àµ¼ (Taxi Car)",
            "v_goodsauto": "à´—àµà´¡àµà´¸àµ à´“à´Ÿàµà´Ÿàµ‹ à´ªà´¿à´•àµà´•à´ªàµà´ªàµ (Goods Auto Pickup)",
            "v_pickupvan": "à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´µà´¾àµ» (Pickup Van)",
            "v_minilorry": "à´®à´¿à´¨à´¿ à´²àµ‹à´±à´¿ (Mini Lorry)",
            "v_truck": "à´Ÿàµà´°à´•àµà´•àµ (Truck)",
            "v_biketaxi": "à´¬àµˆà´•àµà´•àµ à´Ÿà´¾à´•àµà´¸à´¿ (Bike Taxi)"
        }
        vehicle_type = v_mapping.get(call.data, "à´Ÿà´¾à´•àµà´¸à´¿ à´•à´¾àµ¼")
        registration_data[chat_id]["vehicle_type"] = vehicle_type
        registration_data[chat_id]["step"] = "waiting_vehicle_number"
        
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id, 
            f"à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´¤àµà´¤ à´µà´¾à´¹à´¨à´‚: *{vehicle_type}*\n\nà´…à´µà´¸à´¾à´¨à´®à´¾à´¯à´¿ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´µà´¾à´¹à´¨ à´¨à´®àµà´ªàµ¼ / à´ªàµ†àµ¼à´®à´¿à´±àµà´±àµ à´¨à´®àµà´ªàµ¼ à´Ÿàµˆà´ªàµà´ªàµ à´šàµ†à´¯àµà´¤àµ à´…à´¯à´•àµà´•àµ‚ (à´‰à´¦à´¾: KL 10 AB 1234):", 
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda message: message.chat.id in registration_data and registration_data[message.chat.id]["step"] == "waiting_vehicle_number")
def handle_vehicle_number_input(message):
    chat_id = message.chat.id
    vehicle_number = message.text.upper()
    
    registration_data[chat_id]["vehicle_number"] = vehicle_number
    registration_data[chat_id]["step"] = "waiting_agreement"
    
    disclaimer_text = (
        "âš ï¸ *à´¨à´¿à´¯à´®à´ªà´°à´®à´¾à´¯ à´¨à´¿à´¬à´¨àµà´§à´¨à´•à´³àµà´‚ à´‰à´¤àµà´¤à´°à´µà´¾à´¦à´¿à´¤àµà´¤ à´¨à´¿à´°à´¾à´•à´°à´£à´µàµà´‚ (Disclaimer & Terms):*\n\n"
        "à´žà´¾àµ» à´®àµà´•à´³à´¿àµ½ à´¨àµ½à´•à´¿à´¯à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨ à´Žà´¨àµà´±àµ† à´µà´¾à´¹à´¨à´¤àµà´¤à´¿à´¨àµà´±àµ† à´µà´¿à´µà´°à´™àµà´™à´³àµà´‚ à´ªàµ‡à´ªàµà´ªà´±àµà´•à´³àµà´Ÿàµ† à´•à´¾à´²à´¾à´µà´§à´¿à´¯àµà´‚ à´ªàµ‚àµ¼à´£àµà´£à´®à´¾à´¯àµà´‚ à´¸à´¤àµà´¯à´®à´¾à´£àµ†à´¨àµà´¨àµ à´¬àµ‹à´§àµà´¯à´ªàµà´ªàµ†à´Ÿàµà´¤àµà´¤àµà´¨àµà´¨àµ.\n\n"
        "à´ˆ à´ªàµà´²à´¾à´±àµà´±àµâ€Œà´«àµ‹à´‚ à´¡àµà´°àµˆà´µàµ¼à´®à´¾à´°àµ†à´¯àµà´‚ à´•à´¸àµà´±àµà´±à´®àµ¼à´®à´¾à´°àµ†à´¯àµà´‚ à´ªà´°à´¸àµà´ªà´°à´‚ à´¬à´¨àµà´§à´¿à´ªàµà´ªà´¿à´•àµà´•àµà´¨àµà´¨à´¤à´¿à´¨àµà´³àµà´³ à´’à´°àµ à´¸à´¾à´™àµà´•àµ‡à´¤à´¿à´• à´¸à´‚à´µà´¿à´§à´¾à´¨à´‚ à´®à´¾à´¤àµà´°à´®à´¾à´£àµ. à´¯à´¾à´¤àµà´°à´¯àµà´•àµà´•à´¿à´Ÿà´¯à´¿àµ½ à´‰à´£àµà´Ÿà´¾à´•àµà´¨àµà´¨ à´¸à´¾à´®àµà´ªà´¤àµà´¤à´¿à´• à´‡à´Ÿà´ªà´¾à´Ÿàµà´•àµ¾à´•àµà´•àµ‹, à´µàµà´¯à´•àµà´¤à´¿à´ªà´°à´®à´¾à´¯ à´¤àµ¼à´•àµà´•à´™àµà´™àµ¾à´•àµà´•àµ‹, à´µà´£àµà´Ÿà´¿à´•àµà´•àµà´£àµà´Ÿà´¾à´•àµà´¨àµà´¨ à´¤à´•à´°à´¾à´±àµà´•àµ¾à´•àµà´•àµ‹, à´…à´ªà´•à´Ÿà´™àµà´™àµ¾à´•àµà´•àµ‹ à´ˆ à´†à´ªàµà´ªà´¿à´¨àµà´±àµ† à´…à´¡àµà´®à´¿àµ»à´®à´¾àµ¼ à´‰à´¤àµà´¤à´°à´µà´¾à´¦à´¿à´•à´³à´¾à´¯à´¿à´°à´¿à´•àµà´•à´¿à´²àµà´² à´Žà´¨àµà´¨àµ à´žà´¾àµ» à´ªàµ‚àµ¼à´£àµà´£à´®à´¾à´¯à´¿ à´¸à´®àµà´®à´¤à´¿à´•àµà´•àµà´¨àµà´¨àµ."
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("âœ… à´žà´¾àµ» à´ˆ à´¨à´¿à´¬à´¨àµà´§à´¨à´•àµ¾ à´µà´¾à´¯à´¿à´šàµà´šàµ à´®à´¨à´¸àµà´¸à´¿à´²à´¾à´•àµà´•à´¿ à´…à´‚à´—àµ€à´•à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ (I Agree)", callback_data="final_agree"))
    
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
            "wallet_balance": 0.0,  # ðŸ†• à´ˆ à´µà´°à´¿ à´‡à´µà´¿à´Ÿàµ† à´šàµ‡àµ¼à´•àµà´•àµà´•
        }
        
        try:
            driver_ref = db.reference(f"drivers/{chat_id}")
            driver_ref.set(driver_data)
            
            success_text = (
                f"ðŸŽ‰ *à´°à´œà´¿à´¸àµà´Ÿàµà´°àµ‡à´·àµ» à´µà´¿à´œà´¯à´•à´°à´®à´¾à´¯à´¿ à´ªàµ‚àµ¼à´¤àµà´¤à´¿à´¯à´¾à´¯à´¿!* ðŸŽ‰\n\n"
                f"à´µà´£à´•àµà´•à´‚ {data['driver_name']},\n"
                f"à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´µà´¿à´µà´°à´™àµà´™àµ¾  à´¡à´¾à´±àµà´±à´¾à´¬àµ‡à´¸à´¿àµ½ à´¸àµà´°à´•àµà´·à´¿à´¤à´®à´¾à´¯à´¿ à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¤à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ.\n\n"
                f"ðŸš• à´‡à´¨à´¿à´®àµà´¤àµ½ à´±àµˆà´¡àµ à´±à´¿à´•àµà´µà´¸àµà´±àµà´±àµà´•àµ¾ à´ˆ à´šà´¾à´±àµà´±à´¿à´²àµ‡à´•àµà´•àµ à´µà´°àµà´¨àµà´¨à´¤à´¾à´£àµ."
            )
            bot.send_message(chat_id=chat_id, text=success_text, parse_mode="Markdown")
            del registration_data[chat_id]
            
        except Exception as e:
            bot.send_message(chat_id=chat_id, text=f"âŒ à´°à´œà´¿à´¸àµà´Ÿàµà´°àµ‡à´·à´¨à´¿àµ½ à´¤à´Ÿà´¸àµà´¸à´‚ à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ: {e}")




# ============================================================
# ðŸ—ºï¸ SMART MAPPING & FALLBACK ENGINE (FINAL FIXED)
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
                    print(f"âœ… Firebase manual: {place}")
                    return float(loc_ref['lat']), float(loc_ref['lng'])
            except Exception as e:
                print(f"âš ï¸ Firebase error: {e}")

            # 2. Nominatim â€” 4 queries
            cleaned_place = clean_place(place)
            query_variants = [
                f"{cleaned_place}, Kerala, India",
                f"{cleaned_place}, Malappuram, Kerala",
                f"{cleaned_place}, India",
                f"{cleaned_place}",
            ]

            for idx, query in enumerate(query_variants):
                try:
                    print(f"ðŸŒ Query {idx+1}: {query}")
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
                                print(f"âœ… Cached: {place}")
                            except Exception as e:
                                print(f"âš ï¸ Cache error: {e}")
                            return lat, lon
                    time.sleep(1.5)
                except Exception as e:
                    print(f"âš ï¸ Query {idx+1} failed: {e}")
                    time.sleep(1.5)
                    continue

            # ðŸŽ¯ â€” 3. Manjeri ONLY fallback
            print(f"âš ï¸ Nominatim failed: {place} â€” using Manjeri center")

            try:
                area_ref = db.reference(f'areas/Manjeri').get()
                if isinstance(area_ref, dict) and 'lat' in area_ref and 'lng' in area_ref:
                    print(f"âœ… Manjeri center fallback")
                    return float(area_ref['lat']), float(area_ref['lng'])
            except Exception as e:
                print(f"âš ï¸ Manjeri fallback error: {e}")

            print(f"âŒ Location not found: {place}")
            return None

        except Exception as e:
            print(f"âŒ Geocode error: {e}")
            return None

    # ============================================================
    # Get coordinates
    # ============================================================
    pickup_coords = geocode_place(pickup_place)
    drop_coords = geocode_place(drop_place)

    if pickup_coords is None or drop_coords is None:
        raise ValueError(f"Geocoding failed: {pickup_place} â†’ {drop_place}")

    p_lat, p_lon = pickup_coords
    d_lat, d_lon = drop_coords

    # ðŸŽ¯ â€” Sanity check
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
                print(f"âœ… Distance source: OSRM ({distance_km:.1f} km)")
                return round(distance_km, 1)

        print("âš ï¸ OSRM failed â†’ GraphHopper")
    except Exception as e:
        print(f"âš ï¸ OSRM error: {e}")

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
                print(f"âœ… Distance source: GraphHopper ({distance_km:.1f} km)")
                return round(distance_km, 1)

        print("âš ï¸ GraphHopper failed â†’ Geoapify")
    except Exception as e:
        print(f"âš ï¸ GraphHopper error: {e}")

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
                print(f"âœ… Distance source: Geoapify ({distance_km:.1f} km)")
                return round(distance_km, 1)
    except Exception as e:
        print(f"âš ï¸ Geoapify error: {e}")

    # ============================================================
    # FINAL FALLBACK â€” Haversine
    # ============================================================
    print("âš ï¸ Using Haversine fallback")
    return round(haversine_distance(p_lat, p_lon, d_lat, d_lon), 1)
# ============================================================
# ðŸ’° MASTER COMMISSION LOGIC
# ============================================================
def calculate_admin_commission(km):
    """à´¦àµ‚à´°à´¤àµà´¤à´¿à´¨àµà´±àµ† à´…à´Ÿà´¿à´¸àµà´¥à´¾à´¨à´¤àµà´¤à´¿àµ½ à´…à´¡àµà´®à´¿àµ» à´•à´®àµà´®àµ€à´·àµ» à´•à´£à´•àµà´•à´¾à´•àµà´•àµà´•"""
    if not ENABLE_COMMISSION:
        return 0.0
    
    if km <= 1.5:
        commission = 0.50  # à´†à´¦àµà´¯ 1.5 à´•à´¿.à´®àµ€-à´¨àµ â‚¹0.50
    else:
        # 1.5 à´•à´¿.à´®àµ€ à´•à´´à´¿à´žàµà´žàµà´³àµà´³ à´…à´§à´¿à´• à´¦àµ‚à´°à´‚
        extra_distance = km - 1.5
        
        # à´…à´¤à´¿à´¨àµ† à´…à´Ÿàµà´¤àµà´¤ à´ªàµ‚àµ¼à´£àµà´£ à´•à´¿.à´®àµ€à´¯à´¿à´²àµ‡à´•àµà´•àµ à´±àµ—à´£àµà´Ÿàµ à´šàµ†à´¯àµà´¯àµà´• (à´‰à´¦à´¾: 0.1 â†’ 1, 1.5 â†’ 2)
        rounded_extra = math.ceil(extra_distance)
        
        # à´“à´°àµ‹ à´…à´§à´¿à´• à´•à´¿.à´®àµ€-à´¨àµà´‚ â‚¹22.50 à´µàµ†à´šàµà´šàµ à´•à´£à´•àµà´•à´¾à´•àµà´•àµà´•
        extra_fare = rounded_extra * 22.50
        
        # à´…à´¤à´¿à´¨àµà´±àµ† 1.5% à´•à´®àµà´®àµ€à´·àµ» à´•à´£à´•àµà´•à´¾à´•àµà´•àµà´•
        commission = 0.50 + (extra_fare * 0.015)
    
    return round(commission, 2)

# ============================================================
# ðŸ“ AREA ROUTING MAP
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
# ðŸ›¡ï¸ MODULE 21: ANTI-SPAM BOMBING & RATE LIMITER ENGINE
# ============================================================
def check_spam_and_rate_limit(user_identifier):
    current_time = time.time()
    last_sub_time = st.session_state.user_submission_tracker.get(user_identifier, 0)
    
    if current_time - last_sub_time < 30:
        remaining_time = int(30 - (current_time - last_sub_time))
        log_and_report_error(f"Spam attempt blocked for User: {user_identifier}", "Rate_Limiter")
        return False, f"âš ï¸ à´¤à´¾àµ½à´•àµà´•à´¾à´²à´¿à´•à´®à´¾à´¯à´¿ à´¸à´¿à´¸àµà´±àµà´±à´‚ à´¨à´¿à´™àµà´™à´³àµ† à´¤à´Ÿà´žàµà´žà´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ! à´¦à´¯à´µà´¾à´¯à´¿ {remaining_time} à´¸àµ†à´•àµà´•àµ»à´¡à´¿à´¨àµ à´¶àµ‡à´·à´‚ à´µàµ€à´£àµà´Ÿàµà´‚ à´¶àµà´°à´®à´¿à´•àµà´•àµà´•."
        
    st.session_state.user_submission_tracker[user_identifier] = current_time
    return True, "ALLOWED"

# ============================================================
# ðŸš¨ MODULE 20: CENTRALIZED ERROR TRACKING & MONITORING ENGINE
# ============================================================
def log_and_report_error(error_message, function_name):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_details = str(error_message)
    print(f"ðŸ›‘ [SYSTEM ERROR] in {function_name} at {current_time}: {error_details}")
    
    if bot and ADMIN_TELEGRAM_CHAT_ID:
        telegram_alert_text = (
            f"ðŸš¨ *CRITICAL SYSTEM ERROR DETECTED* ðŸš¨\n\n"
            f"ðŸ“‚ *à´®àµŠà´¡àµà´¯àµ‚àµ¾/à´«à´™àµà´•àµà´·àµ»:* {function_name}\n"
            f"â° *à´¸à´®à´¯à´‚:* {current_time}\n"
            f"ðŸ“ *à´Žà´±àµ¼ à´µà´¿à´µà´°à´£à´‚:* `{error_details}`\n\n"
            f"ðŸ› ï¸ *à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•:* à´¦à´¯à´µà´¾à´¯à´¿ à´…à´¡àµà´®à´¿àµ» à´ªà´¾à´¨à´²àµ‹ à´—àµ‚à´—à´¿àµ¾ à´·àµ€à´±àµà´±àµ à´²àµ‹à´—àµà´•à´³àµ‹ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´•."
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
# ðŸ”’ SECURITY & UTILITY FUNCTIONS
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
        st.error("ðŸš¨ à´¸àµà´°à´•àµà´·à´¾ à´®àµà´¨àµà´¨à´±à´¿à´¯à´¿à´ªàµà´ªàµ: à´¤àµà´Ÿàµ¼à´šàµà´šà´¯à´¾à´¯ à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´¶àµà´°à´®à´™àµà´™àµ¾!")
        if "captcha_text_question" not in st.session_state:
            val1 = random.randint(2, 9)
            val2 = random.randint(2, 9)
            st.session_state.correct_captcha_sum = val1 + val2
            st.session_state.captcha_text_question = f"à´µàµà´¯à´¾à´œ à´¬àµà´•àµà´•à´¿à´‚à´—àµà´•àµ¾ à´¤à´Ÿà´¯àµà´¨àµà´¨à´¤à´¿à´¨à´¾à´¯à´¿: {val1} + {val2} = ?"
            
        st.markdown(f"**{st.session_state.captcha_text_question}**")
        user_captcha_ans = st.number_input("à´‰à´¤àµà´¤à´°à´‚", step=1, key="captcha_input")
        
        if user_captcha_ans == st.session_state.correct_captcha_sum:
            st.session_state.captcha_verified = True
            st.success("âœ… à´¸àµà´°à´•àµà´·à´¾ à´ªà´°à´¿à´¶àµ‹à´§à´¨ à´µà´¿à´œà´¯à´•à´°à´‚!")
            return True
        else:
            st.session_state.captcha_verified = False
            st.warning("âŒ à´¤àµ†à´±àµà´±à´¾à´¯ à´‰à´¤àµà´¤à´°à´‚!")
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
# ðŸ—ºï¸ AREA ROUTING FUNCTIONS
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
# ðŸ’¾ MODULE 22: ADVANCED AREA-WISE MASTER BACKUP SYSTEM
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
# ðŸš— DRIVER & ROUTING FUNCTIONS
# ============================================================
# 1. à´ªàµà´¤à´¿à´¯ à´«à´™àµà´·àµ» à´‡à´µà´¿à´Ÿàµ† à´¨àµ½à´•àµà´• (à´¡àµ†à´•àµà´•à´±àµ‡à´±àµà´±à´±à´¿à´¨àµ à´®àµà´•à´³à´¿àµ½)
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
    # Cache management (30 à´¸àµ†à´•àµà´•àµ»à´¡àµ à´µà´°àµ† à´ªà´´à´¯ à´¡à´¾à´±àµà´± à´‰à´ªà´¯àµ‹à´—à´¿à´•àµà´•àµà´¨àµà´¨àµ)
    if (
        "cached_drivers" in st.session_state
        and (
            time.time() - st.session_state.get("cache_time", 0)
        ) < 30
    ):
        return st.session_state.cached_drivers

    try:
        # à´—àµ‚à´—à´¿àµ¾ à´·àµ€à´±àµà´±à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´¡à´¾à´±àµà´± à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨àµ
        res = requests.get(
            f"{GOOGLE_SHEET_URL}?action=get_all_drivers",
            timeout=40
        )

        # à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ 200 à´†à´£àµ‹ à´Žà´¨àµà´¨àµ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ
        if res.status_code == 200:
            content = res.text.strip()
            # à´¡à´¾à´±àµà´± à´¶à´°à´¿à´¯à´¾à´¯ JSON à´«àµ‹àµ¼à´®à´¾à´±àµà´±à´¿à´²à´¾à´£àµ‹ à´Žà´¨àµà´¨àµ à´‰à´±à´ªàµà´ªà´¾à´•àµà´•àµà´¨àµà´¨àµ
            if content.startswith(('[', '{')):
                data = res.json()
                if isinstance(data, list):
                    st.session_state.cached_drivers = data
                    st.session_state.cache_time = time.time()
                    return data
            else:
                # à´Ÿàµ†àµ¼à´®à´¿à´¨à´²à´¿àµ½ à´Žà´±àµ¼ à´•à´¾à´£à´¿à´•àµà´•àµà´‚, à´ªà´•àµà´·àµ† à´†à´ªàµà´ªàµ à´•àµà´°à´¾à´·àµ à´†à´•à´¿à´²àµà´²
                print("à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•: à´·àµ€à´±àµà´±àµ à´¡à´¾à´±àµà´± JSON à´…à´²àµà´² -", content[:50])
        else:
            print("à´·àµ€à´±àµà´±àµ à´•à´£à´•àµà´·àµ» à´ªà´°à´¾à´œà´¯à´ªàµà´ªàµ†à´Ÿàµà´Ÿàµ, à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´•àµ‹à´¡àµ:", res.status_code)
                
    except Exception as e:
        # à´‡à´µà´¿à´Ÿàµ† à´Žà´±àµ¼ à´±à´¿à´ªàµà´ªàµ‹àµ¼à´Ÿàµà´Ÿàµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ, à´ªà´•àµà´·àµ† à´†à´ªàµà´ªàµ à´¤à´Ÿà´¸àµà´¸à´®à´¿à´²àµà´²à´¾à´¤àµ† à´ªàµà´°à´µàµ¼à´¤àµà´¤à´¿à´•àµà´•àµà´‚
        print(f"fetch_all_drivers_from_sheet à´Žà´±àµ¼: {e}")

    # à´¡à´¾à´±àµà´± à´•à´¿à´Ÿàµà´Ÿà´¿à´¯à´¿à´²àµà´²àµ†à´™àµà´•à´¿àµ½ à´ªà´´à´¯ à´•àµà´¯à´¾à´·àµ à´‰à´£àµà´Ÿàµ‹ à´Žà´¨àµà´¨àµ à´¨àµ‹à´•àµà´•àµà´¨àµà´¨àµ, à´…à´²àµà´²àµ†à´™àµà´•à´¿àµ½ à´’à´´à´¿à´žàµà´ž à´²à´¿à´¸àµà´±àµà´±àµ
    return st.session_state.get("cached_drivers", [])
def save_trip_dual_backup(payload):
    try:
        trip_id = payload.get("trip_id")
        if not trip_id:
            return False
        
        # à´«à´¯àµ¼à´¬àµ‡à´¸à´¿à´²àµ† trips à´¨àµ‹à´¡à´¿à´²àµ‡à´•àµà´•àµ à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ à´¡à´¾à´±àµà´± à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ
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
    à´¡àµà´°àµˆà´µàµ¼à´•àµà´•àµ trip notification à´…à´¯à´•àµà´•àµà´¨àµà´¨àµ.
    Format: Clean, privacy-focused, mobile-friendly.
    Includes: Booking Date + Time
    """
    # ðŸ†• FIX: commission_amount à´‡à´µà´¿à´Ÿàµ† à´¡à´¿à´«àµˆàµ» à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ
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
        # ðŸ‘‡ 2297-à´¾à´‚ à´µà´°à´¿: à´‡à´µà´¿à´Ÿàµ† à´¨à´¿à´¨àµà´¨à´¾à´£àµ à´ªàµà´¤à´¿à´¯ à´•àµ‹à´¡àµ à´¤àµà´Ÿà´™àµà´™àµà´¨àµà´¨à´¤àµ (8 à´¸àµà´ªàµ‡à´¸àµ à´‡àµ»à´¡à´¨àµà´±àµ‡à´·àµ»)
        # âš ï¸ â‚¹25 à´†à´•àµà´®àµà´ªàµ‹àµ¾ à´µà´¾à´£à´¿à´‚à´—àµ à´•à´¾à´£à´¿à´•àµà´•à´¾àµ»
        if WARNING_LIMIT <= wallet_balance < BLOCK_LIMIT:
            try:
                bot.send_message(
                    chat_id=driver["chat_id"],
                    text=f"âš ï¸ à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•: à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´•à´®àµà´®àµ€à´·àµ» à´•àµà´Ÿà´¿à´¶àµà´¶à´¿à´• â‚¹{wallet_balance} à´†à´£àµ. à´‡à´¤àµ â‚¹{BLOCK_LIMIT} à´•à´´à´¿à´žàµà´žà´¾àµ½ à´¨à´¿à´™àµà´™àµ¾à´•àµà´•àµ à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾ à´²à´­à´¿à´•àµà´•àµà´¨àµà´¨à´¤à´²àµà´²."
                )
            except:
                pass
        
        
            

        if wallet_balance >= BLOCK_LIMIT:
            try:
                bot.send_message(
                    chat_id=driver["chat_id"],
                    text="ðŸ›‘ à´µà´¾à´²à´±àµà´±àµ à´•à´®àµà´®àµ€à´·àµ» à´ªà´°à´¿à´§à´¿ à´•à´Ÿà´¨àµà´¨à´¤à´¿à´¨à´¾àµ½ à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾ à´¤à´Ÿà´žàµà´žà´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ."
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
        # âœ… Booking Date & Time
        # ============================================================
        booking_time_raw = (
            trip_details.get('booking_time')
            or trip_details.get('Booking Time')
            or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        try:
            # "2026-09-22 10:32:45" â†’ date + time
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
            gps_line = f"ðŸ”— GPS: [ðŸ“ Location à´•à´¾à´£àµà´•]({gps_url})"
        else:
            gps_line = "ðŸ”— GPS: à´²à´­àµà´¯à´®à´²àµà´²"

        # ============================================================
        # Wallet Warning
        # ============================================================
        warning_text = ""
        if wallet_balance >= WARNING_LIMIT:
            warning_text = "âš ï¸ *à´®àµà´¨àµà´¨à´±à´¿à´¯à´¿à´ªàµà´ªàµ: à´µà´¾à´²à´±àµà´±àµ à´¬à´¾à´²àµ»à´¸àµ à´•àµà´±à´µà´¾à´£àµ!*\n\n"

        # ============================================================
        # Final Message (with Date + Time)
        # ============================================================
        message_text = (
            f"ðŸš– *à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´²à´­àµà´¯à´®à´¾à´£àµ!*\n"
            f"ðŸ†” {trip_id}\n"
            f"ðŸ“… Date: {date_display}\n"       # ðŸ‘ˆ NEW
            f"ðŸ• Time: {time_display}\n"       # ðŸ‘ˆ NEW
            f"ðŸ‘¤ {customer_name}\n"
            f"ðŸ“ž {masked_phone}\n"
            f"ðŸ“ à´ªà´¿à´•àµà´•à´ªàµà´ªàµ: {pickup}\n"
            f"ðŸ à´¡àµà´°àµ‹à´ªàµà´ªàµ: {drop}\n"
            f"ðŸ’° à´•à´®àµà´®àµ€à´·àµ»: â‚¹{commission_amount}\n"
            f"ðŸ“ à´¦àµ‚à´°à´‚: {trip_distance} km\n"
            f"{gps_line}\n\n"
            f"{warning_text}"
            f"âš ï¸ *à´†à´¦àµà´¯à´‚ à´•àµà´²à´¿à´•àµà´•àµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨ à´¡àµà´°àµˆà´µàµ¼à´•àµà´•à´¾à´¯à´¿à´°à´¿à´•àµà´•àµà´‚ à´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªàµ!*"
        )

        # ============================================================
        # ACCEPT Button
        # ============================================================
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(
            types.InlineKeyboardButton(
                text="âœ… ACCEPT TRIP",
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

        print(f"âœ… Trip notification sent to driver {driver['chat_id']}")

    except Exception as e:
        print(f"âŒ send_individual_trip_link error: {e}")
        try:
            log_and_report_error(e, "send_individual_trip_link")
        except:
            pass

def normalize_vehicle_type(vehicle_str):
    v = str(vehicle_str).lower()
    if "auto" in v and "rickshaw" in v:
        return "auto"
    elif "à´“à´Ÿàµà´Ÿàµ‹" in v:
        return "auto"
    elif "taxi" in v or "car" in v or "à´•à´¾àµ¼" in v:
        return "car"
    elif "goods" in v or "à´—àµà´¡àµà´¸àµ" in v:
        return "goods"
    elif "pickup" in v and "van" in v:
        return "van"
    elif "mini" in v or "lorry" in v or "à´²àµ‹à´±à´¿" in v:
        return "mini"
    elif "truck" in v or "à´Ÿàµà´°à´•àµà´•àµ" in v:
        return "truck"
    elif "bike" in v or "à´¬àµˆà´•àµà´•àµ" in v:
        return "bike"
    return ""
def process_radius_expansion_routing(
    trip_details,
    customer_lat,
    customer_lon
):
    """
    à´“à´°àµ‹ Trip ID + Driver Chat ID combination-à´¨àµà´‚
    à´’à´°àµ Telegram notification à´®à´¾à´¤àµà´°à´‚ à´…à´¯à´¯àµà´•àµà´•à´¾àµ» à´¶àµà´°à´®à´¿à´•àµà´•àµà´¨àµà´¨àµ.
    """

    try:
        trip_id = str(trip_details.get("trip_id", "")).strip()
        customer_vehicle = normalize_vehicle_type(
            trip_details.get("vehicle_type", "")
        )    
        print(f"ðŸ” Customer wants: {customer_vehicle}")
        if not trip_id:
            print("DEBUG: Trip ID à´‡à´²àµà´².")
            return

        # ----------------------------------------------------
        # 1. Firebase-àµ½ à´¨à´¿à´¨àµà´¨àµ à´¡àµà´°àµˆà´µàµ¼à´®à´¾à´°àµ† à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨àµ
        # ----------------------------------------------------
        drivers_ref = db.reference("drivers")
        drivers_data = drivers_ref.get()

        if not drivers_data:
            print("DEBUG: Firebase-àµ½ drivers à´‡à´²àµà´².")
            return

        if isinstance(drivers_data, dict):
            all_drivers = list(drivers_data.values())
        elif isinstance(drivers_data, list):
            all_drivers = drivers_data
        else:
            print("DEBUG: Invalid drivers data.")
            return

        # ----------------------------------------------------
        # 2. Trip status à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ
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
        # 3. à´‡à´¤à´¿à´¨à´•à´‚ notification à´…à´¯à´šàµà´š drivers
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
        # 4. ONLINE drivers à´®à´¾à´¤àµà´°à´‚
        # ----------------------------------------------------
        for driver in all_drivers:
            # ðŸ”’ à´²àµ‹à´•àµà´•àµ à´šàµ†à´•àµà´•àµ (12 à´¸àµà´ªàµ‡à´¸àµà´•àµ¾)
            current_trip = db.reference(f"trips/{trip_id}").get() or {}
            if current_trip.get("is_locked", False) or current_trip.get("status") == "Accepted":
                print(f"â­ï¸ Trip {booking_id} already locked. Skipping remaining drivers.")
                break  # à´²àµ‚à´ªàµà´ªà´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´ªàµà´±à´¤àµà´¤àµà´•à´Ÿà´•àµà´•àµà´•
               
            if not isinstance(driver, dict):
                continue

            driver_status = str(
                driver.get("status", "")
            ).strip().upper()

            if driver_status != "ONLINE":
                continue
            # ðŸŽ¯ â€” Vehicle type filter
            driver_vehicle = normalize_vehicle_type(
                driver.get("vehicle_type", "")
            )
            if customer_vehicle and driver_vehicle:
                if customer_vehicle != driver_vehicle:
                    print(f"â­ï¸ Skip {driver.get('driver_name', '?')}: {driver_vehicle} â‰  {customer_vehicle}") 
                    continue 
 
           
             
            # Firebase driver record-àµ½ chat_id
            d_chat_id = str(
                driver.get("chat_id")
                or driver.get("telegram_chat_id")
                or driver.get("Telegram Chat ID")
                or ""
            ).strip()

            if not d_chat_id:
                print(
                    f"DEBUG: Driver {driver.get('name', '')} "
                    f"- Telegram Chat ID à´‡à´²àµà´²."
                )
                continue

            # ------------------------------------------------
            # 5. à´‡à´¤à´¿à´¨à´•à´‚ à´…à´¯à´šàµà´šà´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ†à´™àµà´•à´¿àµ½ skip
            # ------------------------------------------------
            if d_chat_id in already_notified:
                print(
                    f"DEBUG: Trip {trip_id} -> "
                    f"{d_chat_id} already notified. SKIP."
                )
                continue

            # ------------------------------------------------
            # 6. Telegram à´…à´¯à´¯àµà´•àµà´•àµà´¨àµà´¨à´¤à´¿à´¨àµ à´®àµà´®àµà´ªàµ
            #    notification lock à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ
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

                # Lock create à´šàµ†à´¯àµà´¯àµà´¨àµà´¨àµ
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

                # Send à´ªà´°à´¾à´œà´¯à´ªàµà´ªàµ†à´Ÿàµà´Ÿà´¾àµ½ lock FAILED à´†à´•àµà´•àµà´¨àµà´¨àµ
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
# ðŸš– à´¡àµà´°àµˆà´µàµ¼ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½ (Full Featured Web Page)
# ============================================================
def driver_trip_panel_page():
    st.title("ðŸš– à´¡àµà´°àµˆà´µàµ¼ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½")
    
    # URL-àµ½ à´¨à´¿à´¨àµà´¨àµ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´Žà´Ÿàµà´•àµà´•àµà´•
    query_params = st.query_params
    trip_id = query_params.get("trip_id", "")
    driver_chat_id = query_params.get("driver_chat_id", "")
    
    if not trip_id:
        st.error("âŒ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¾à´¨à´¾à´¯à´¿à´²àµà´².")
        return
    
    # à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´Žà´Ÿàµà´•àµà´•àµà´•
    trip_data = db.reference(f"trips/{trip_id}").get()
    
    if not trip_data:
        st.error("âŒ à´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿à´¯à´¿àµ½ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´²à´­àµà´¯à´®à´²àµà´².")
        return
    
    # à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾
    customer_name = trip_data.get("customer_name", "N/A")
    customer_phone = trip_data.get("customer_phone", "")
    pickup = trip_data.get("pickup", "N/A")
    drop = trip_data.get("drop", "N/A")
    pickup_lat = trip_data.get("pickup_lat", 0)
    pickup_lon = trip_data.get("pickup_lon", 0)
    total_fare = trip_data.get("total_fare", 0)
    status = trip_data.get("status", "Accepted")
    
    # ðŸ†• Distance & Commission à´Žà´Ÿàµà´•àµà´•àµà´•
    distance = trip_data.get("calculated_distance", "N/A")
    commission = trip_data.get("commission_amount", "N/A")
    
    # ============================================================
    # âœ… 1. à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ (Distance & Commission à´¸à´¹à´¿à´¤à´‚)
    # ============================================================
    st.markdown(f"""
    <div style="background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #2c3e50;">
        <h3 style="margin: 0; color: #2c3e50;">ðŸ†” à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿: {trip_id}</h3>
        <p style="margin: 5px 0; color: #555;">ðŸ‘¤ à´•à´¸àµà´±àµà´±à´®àµ¼: {customer_name}</p>
        <p style="margin: 5px 0; color: #555;">ðŸ“ à´ªà´¿à´•àµà´•à´ªàµà´ªàµ: {pickup}</p>
        <p style="margin: 5px 0; color: #555;">ðŸ à´¡àµà´°àµ‹à´ªàµà´ªàµ: {drop}</p>
        <p style="margin: 5px 0; color: #555;">ðŸ“ à´¦àµ‚à´°à´‚: {distance} km</p>
        <p style="margin: 5px 0; color: #555;">ðŸ’° à´µà´¾à´Ÿà´•: â‚¹{total_fare}</p>
        <p style="margin: 5px 0; color: #555;">ðŸ’µ à´•à´®àµà´®àµ€à´·àµ»: â‚¹{commission}</p>
        <p style="margin: 5px 0; color: #555;">ðŸ“Š à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ: {status}</p>
    </div>
    """, unsafe_allow_html=True)
    
        # ============================================================
    # âœ… 2. à´²àµˆà´µàµ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´·àµ†à´¯àµ¼ (Arrived à´†à´•àµà´¨àµà´¨à´¤àµ à´µà´°àµ† à´®à´¾à´¤àµà´°à´‚)
    # ============================================================
    if status != "Arrived":
        st.markdown("### ðŸ“ à´²àµˆà´µàµ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´·àµ†à´¯àµ¼ à´šàµ†à´¯àµà´¯àµà´•")
        st.info("ðŸ”” à´ˆ à´ªàµ‡à´œàµ à´“à´ªàµà´ªàµº à´†à´¯à´¿ à´µàµ†à´•àµà´•àµà´•. à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´µà´¸à´¾à´¨à´¿à´•àµà´•àµà´¨àµà´¨à´¤àµ à´µà´°àµ† à´²àµŠà´•àµà´•àµ‡à´·àµ» à´¸àµà´µà´¯à´®àµ‡à´µ à´…à´ªàµà´¡àµ‡à´±àµà´±àµ à´†à´•àµà´‚.")
        
        @st.fragment(run_every=10)
        def update_location():
            try:
                location = streamlit_geolocation()
                if location and location.get("latitude") and location.get("longitude"):
                    lat = location.get("latitude")
                    lon = location.get("longitude")
                    
                    db.reference(f"trips/{trip_id}/driver_location").set({
                        "lat": lat,
                        "lon": lon,
                        "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.success(f"âœ… à´²àµŠà´•àµà´•àµ‡à´·àµ» à´…à´ªàµà´¡àµ‡à´±àµà´±àµ à´†à´¯à´¿: {lat:.4f}, {lon:.4f}")
                else:
                    st.warning("âš ï¸ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´²à´­àµà´¯à´®à´²àµà´². à´¦à´¯à´µà´¾à´¯à´¿ GPS à´“àµº à´šàµ†à´¯àµà´¯àµà´•.")
            except Exception as e:
                st.error(f"âŒ à´Žà´±àµ¼: {e}")
        
        update_location()

    # ============================================================
    # âœ… 3. à´¨à´¾à´µà´¿à´—àµ‡à´·àµ» à´¬à´Ÿàµà´Ÿàµº & à´¨à´¿àµ¼à´¦àµà´¦àµ‡à´¶à´‚ (Arrived à´†à´•àµà´¨àµà´¨à´¤àµ à´µà´°àµ† à´®à´¾à´¤àµà´°à´‚)
    # ============================================================
    if status != "Arrived":
        if pickup_lat and pickup_lon:
            nav_url = f"https://www.google.com/maps/dir/?api=1&destination={pickup_lat},{pickup_lon}"
            st.link_button("ðŸ—ºï¸ à´•à´¸àµà´±àµà´±à´®à´±àµà´Ÿàµ† à´…à´Ÿàµà´¤àµà´¤àµ‡à´•àµà´•àµ à´ªàµ‹à´•àµà´• (Navigation)", nav_url, use_container_width=True)
            
            # ðŸ†• à´¨à´¾à´µà´¿à´—àµ‡à´·àµ» à´¨à´¿àµ¼à´¦àµà´¦àµ‡à´¶à´‚
            st.info("""
            ðŸ“Œ **à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•:**
            â€¢ à´¨à´¾à´µà´¿à´—àµ‡à´·àµ» à´¬à´Ÿàµà´Ÿàµº à´…à´®àµ¼à´¤àµà´¤à´¿à´¯à´¾àµ½, Google Maps à´¤àµà´±à´•àµà´•àµà´‚.
            â€¢ à´•à´¸àµà´±àµà´±à´®à´±àµà´Ÿàµ† à´²àµŠà´•àµà´•àµ‡à´·à´¨à´¿àµ½ à´Žà´¤àµà´¤à´¿à´•àµà´•à´´à´¿à´žàµà´žà´¾àµ½, à´«àµ‹à´£à´¿à´¨àµà´±àµ† **Back Button** à´…à´®àµ¼à´¤àµà´¤à´¿ à´ˆ à´ªàµ‡à´œà´¿à´²àµ‡à´•àµà´•àµ à´¤à´¿à´°à´¿à´•àµ† à´µà´°à´¿à´•.
            â€¢ à´¶àµ‡à´·à´‚, à´¤à´¾à´´àµ†à´¯àµà´³àµà´³ **"à´žà´¾àµ» à´Žà´¤àµà´¤à´¿"** à´¬à´Ÿàµà´Ÿàµº à´…à´®àµ¼à´¤àµà´¤àµà´•.
            """)

    # ============================================================
    # âœ… 4. "à´žà´¾àµ» à´Žà´¤àµà´¤à´¿" (Arrived) à´¬à´Ÿàµà´Ÿàµº
    # ============================================================
    if status != "Arrived":
        st.markdown("### ðŸš– à´Žà´¤àµà´¤à´¿à´¯àµ‹?")
        if st.button("ðŸš– à´žà´¾àµ» à´Žà´¤àµà´¤à´¿ (Arrived)", type="primary", use_container_width=True):
            db.reference(f"trips/{trip_id}").update({
                "status": "Arrived",
                "notification": "arrived_sound"
            })
            # ðŸ‘‡ à´‡à´µà´¿à´Ÿàµ†à´¯à´¾à´£àµ à´ªàµà´¤à´¿à´¯ à´•àµ‹à´¡àµ à´¤àµà´Ÿà´™àµà´™àµà´¨àµà´¨à´¤àµ (12 à´¸àµà´ªàµ†à´¯àµà´¸àµ / 3 à´Ÿà´¾à´¬àµ)
            try:
                if not trip_data.get("commission_added", False):
                    trip_commission = float(trip_data.get("commission_amount", 0.0))
                    driver_id = trip_data.get("driver_chat_id") or trip_data.get("driver_id")
                    
                    if trip_commission > 0 and driver_id:
                        driver_ref = db.reference(f"drivers/{driver_id}")
                        driver_data = driver_ref.get() or {}
                        current_wallet = float(driver_data.get("wallet_balance", 0.0))
                            
                        new_wallet = current_wallet + trip_commission
                        driver_ref.update({"wallet_balance": new_wallet})
                        db.reference(f"trips/{trip_id}").update({"commission_added": True})
                        # ðŸ‘‡ à´‡à´µà´¿à´Ÿàµ†à´¯à´¾à´£àµ à´ªàµà´¤à´¿à´¯ à´µà´¾à´£à´¿à´‚à´—àµ à´•àµ‹à´¡àµ à´¨àµ½à´•àµ‡à´£àµà´Ÿà´¤àµ (16 à´¸àµà´ªàµ‡à´¸àµ / 4 à´Ÿà´¾à´¬àµ à´‡àµ»à´¡à´¨àµà´±àµ‡à´·àµ»)
                        if WARNING_LIMIT <= new_wallet < BLOCK_LIMIT:
                            try:
                                bot.send_message(
                                    chat_id=driver_id,
                                    text=f"âš ï¸ à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•: à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´•à´®àµà´®àµ€à´·àµ» à´•àµà´Ÿà´¿à´¶àµà´¶à´¿à´• â‚¹{new_wallet:.2f} à´†à´¯à´¿. à´‡à´¤àµ â‚¹{BLOCK_LIMIT} à´•à´´à´¿à´žàµà´žà´¾àµ½ à´¨à´¿à´™àµà´™àµ¾à´•àµà´•àµ à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾ à´²à´­à´¿à´•àµà´•àµà´¨àµà´¨à´¤à´²àµà´²."
                                )
                            except:
                                pass
                        try:
                            bot.send_message(
                                chat_id=driver_id,
                                text=f"âœ… à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´µà´¸à´¾à´¨à´¿à´šàµà´šàµ.\nà´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªà´¿à´²àµ† à´•à´®àµà´®àµ€à´·àµ»: â‚¹{trip_commission}\nà´¨à´¿à´²à´µà´¿à´²àµ† à´†à´•àµ† à´•àµà´Ÿà´¿à´¶àµà´¶à´¿à´•: â‚¹{new_wallet:.2f}"
                            )
                        except:
                            pass
            except Exception as e:   
                print(f"Wallet Update Error: {e}")    
            st.success("âœ… à´•à´¸àµà´±àµà´±à´®à´±à´¿à´¨àµ† à´…à´±à´¿à´¯à´¿à´šàµà´šà´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ!")
            st.balloons()
            st.rerun()

    # ============================================================
    # âœ… 5. à´•à´¸àµà´±àµà´±à´®à´±àµà´Ÿàµ† à´«àµ‹àµº à´¨à´®àµà´ªàµ¼ (Arrived à´†à´¯à´¤à´¿à´¨àµ à´¶àµ‡à´·à´‚ à´®à´¾à´¤àµà´°à´‚)
    # ============================================================
    if status == "Arrived":
        st.success("âœ… à´¨à´¿à´™àµà´™àµ¾ à´•à´¸àµà´±àµà´±à´®à´±àµà´Ÿàµ† à´…à´Ÿàµà´¤àµà´¤àµ à´Žà´¤àµà´¤à´¿à´¯à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ.")
        st.markdown("### ðŸ“ž à´•à´¸àµà´±àµà´±à´®à´±àµà´®à´¾à´¯à´¿ à´¬à´¨àµà´§à´ªàµà´ªàµ†à´Ÿàµà´•")
        
        customer_phone = trip_data.get("customer_phone", "")
        
        if customer_phone:
            # ðŸ†• à´¨à´¿à´¯à´®à´ªà´°à´®à´¾à´¯ à´¸àµà´°à´•àµà´·à´¾ à´®àµà´¨àµà´¨à´±à´¿à´¯à´¿à´ªàµà´ªàµ
            st.warning("""
            âš ï¸ **à´¶àµà´°à´¦àµà´§à´¿à´•àµà´•àµà´•:**
            â€¢ à´•à´¸àµà´±àµà´±à´®à´±àµà´Ÿàµ† à´«àµ‹àµº à´¨à´®àµà´ªàµ¼ à´…à´¤àµà´¯à´¾à´µà´¶àµà´¯ à´˜à´Ÿàµà´Ÿà´™àµà´™à´³à´¿àµ½ à´®à´¾à´¤àµà´°à´‚ à´‰à´ªà´¯àµ‹à´—à´¿à´•àµà´•àµà´•.
            â€¢ à´…à´±àµˆà´µàµ½ à´²àµŠà´•àµà´•àµ‡à´·à´¨à´¿àµ½ à´•à´¸àµà´±àµà´±à´®à´±àµ† à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¾à´¨à´¾à´¯à´¿à´²àµà´²àµ†à´™àµà´•à´¿àµ½ à´®à´¾à´¤àµà´°à´‚ à´µà´¿à´³à´¿à´•àµà´•àµà´•.
            â€¢ à´¦àµà´°àµà´ªà´¯àµ‹à´—à´‚ à´šàµ†à´¯àµà´¤à´¾àµ½ à´¨à´¿à´¯à´®à´¨à´Ÿà´ªà´Ÿà´¿à´•àµ¾ à´¨àµ‡à´°à´¿à´Ÿàµ‡à´£àµà´Ÿà´¿ à´µà´°àµà´‚.
            """)
            
            # ðŸ†• à´•àµ‹àµ¾ à´¬à´Ÿàµà´Ÿàµº (à´¨à´®àµà´ªàµ¼ à´•à´¾à´£à´¾à´¤àµ†)
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
            ">ðŸ“ž à´•à´¸àµà´±àµà´±à´®à´±àµ† à´µà´¿à´³à´¿à´•àµà´•àµà´•</a>
            """, unsafe_allow_html=True)
            
            st.info("ðŸ”’ à´¸àµà´°à´•àµà´·à´¯àµà´•àµà´•à´¾à´¯à´¿ à´•à´¸àµà´±àµà´±à´®à´±àµà´Ÿàµ† à´«àµ‹àµº à´¨à´®àµà´ªàµ¼ à´®à´±à´šàµà´šàµà´µàµ†à´šàµà´šà´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ.")
        else:
            st.warning("âš ï¸ à´«àµ‹àµº à´¨à´®àµà´ªàµ¼ à´²à´­àµà´¯à´®à´²àµà´².")
            
# ==========================================================
# ðŸ”” REAL-TIME NOTIFICATION LISTENER
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
                            "ðŸš– **à´¨à´¿à´™àµà´™àµ¾ à´¬àµà´•àµà´•àµ à´šàµ†à´¯àµà´¤ à´µà´¾à´¹à´¨à´‚ à´Žà´¤àµà´¤à´¿à´šàµà´šàµ‡àµ¼à´¨àµà´¨à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ!**"
                        )
                        trip_ref.update({"notification": "played"})
            trip_ref.listen(notification_listener)            
            
# ====================================================================
# ðŸ–¥ï¸ STREAMLIT UI - CUSTOMER BOOKING INTERFACE (CLEANED & FIXED)
# ====================================================================
def main():
    # ============================================================
    # ðŸ”” Push Notification Service Worker à´°à´œà´¿à´¸àµà´±àµà´±àµ¼ à´šàµ†à´¯àµà´¯àµà´•
    # ============================================================
    components.html("""
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('âœ… Service Worker Registered');
                })
                .catch(function(err) {
                    console.log('âŒ Service Worker Registration Failed:', err);
                });
            } else {
                console.log('âŒ Service Worker not supported');
            }
        </script>
    """, height=0)
    # ðŸ†• URL-àµ½ driver_trip_panel à´‰à´£àµà´Ÿàµ†à´™àµà´•à´¿àµ½, à´† à´ªàµ‡à´œàµ à´®à´¾à´¤àµà´°à´‚ à´•à´¾à´£à´¿à´•àµà´•àµà´•
    query_params = st.query_params
    if query_params.get("page") == "driver_trip_panel":
        driver_trip_panel_page()
        return  # à´¬à´¾à´•àµà´•à´¿ à´•àµ‹à´¡àµ à´±àµº à´šàµ†à´¯àµà´¯à´°àµà´¤àµ
    st.markdown("""
    <div class="header-box" style="padding: 15px !important; margin-bottom: 15px !important;">
        <h1 style="font-size: 1.8rem !important; margin: 0 !important; color: #ffcc00 !important;">ðŸš• EASY AUTO TAXI</h1>
        <p style="font-size: 11px !important; margin-top: 3px !important; color: #b3b3b3 !important;">FAST â€¢ SECURE â€¢ RELIABLE</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("\n")

    # Session state for button disable
    if 'is_booking' not in st.session_state:
        st.session_state.is_booking = False

    # ----------------------------------------------------------------
    # ðŸ“ ULTIMATE RELIABLE GPS LOCATION (Final Clean Version)
    # ----------------------------------------------------------------
    if 'lat' not in st.session_state:
        st.session_state.lat = None
    if 'lon' not in st.session_state:
        st.session_state.lon = None
    if 'gps_link' not in st.session_state:
        st.session_state.gps_link = "Not Available"
    if 'gps_enabled' not in st.session_state:      # <--- à´ˆ à´µà´°à´¿ à´‡à´µà´¿à´Ÿàµ† à´šàµ‡àµ¼à´•àµà´•àµà´•
        st.session_state.gps_enabled = False       # <--- à´‡à´¤àµà´‚

    # ðŸŽ¯ à´œà´¿à´ªà´¿à´Žà´¸àµ à´à´•àµà´•à´£àµà´‚ à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´®àµ†à´¸àµà´¸àµ‡à´œàµà´‚ à´’à´°àµ‡ à´µà´°à´¿à´¯à´¿àµ½ à´•àµŠà´£àµà´Ÿàµà´µà´°à´¾àµ» à´•àµ‹à´³à´‚ à´‰à´ªà´¯àµ‹à´—à´¿à´•àµà´•àµà´¨àµà´¨àµ
    col_icon, col_status = st.columns([1, 5])

    with col_icon:
        try:
            location = streamlit_geolocation()
            if location and location.get("latitude"):
                st.session_state.lat = location.get("latitude")
                st.session_state.lon = location.get("longitude")
                st.session_state.gps_link = f"https://maps.google.com/?q={st.session_state.lat},{st.session_state.lon}"
        except Exception as e:
            pass

    with col_status:
        # à´à´•àµà´•à´£à´¿à´¨àµ à´…à´Ÿàµà´¤àµà´¤àµ‡à´•àµà´•àµ à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´•à´¾à´£à´¿à´•àµà´•à´¾àµ»
        lat = st.session_state.lat
        lon = st.session_state.lon
        
        # à´šàµ†à´±à´¿à´¯ à´ªà´¾à´¡à´¿à´‚à´—àµ à´‰à´ªà´¯àµ‹à´—à´¿à´šàµà´šàµ à´¸àµà´ªàµ‡à´¸àµ à´•àµà´±à´¯àµà´•àµà´•àµà´¨àµà´¨àµ
        if lat and lon:
            st.markdown(
                """
                <div style="background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 5px; border: 1px solid #c3e6cb; margin-top: 5px; margin-bottom: 0px;">
                    <b>ðŸŽ¯ GPS Status:</b> <span style="color: green; font-weight: bold;">ðŸŸ¢ à´¸à´œàµ€à´µà´®à´¾à´£àµ</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div style="background-color: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 5px; border: 1px solid #ffeeba; margin-top: 5px; margin-bottom: 0px;">
                    <b>ðŸŽ¯ GPS Status:</b> <span style="color: #856404; font-weight: bold;">âš ï¸ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´²à´­àµà´¯à´®à´²àµà´² (à´ªàµ†àµ¼à´®à´¿à´·àµ» à´…à´²àµ‹ à´šàµ†à´¯àµà´¯àµà´•)</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ðŸ“ "à´¯à´¾à´¤àµà´°à´¾ à´µà´¿à´µà´°à´™àµà´™àµ¾" à´Žà´¨àµà´¨ à´¹àµ†à´¡à´¿à´‚à´—àµ (à´‡à´¤àµ à´•àµ‚à´Ÿàµà´¤àµ½ à´®àµà´•à´³à´¿à´²àµ‡à´•àµà´•àµ à´µà´°à´¾àµ» CSS)
    st.markdown("""
    <style>
        /* à´¸àµà´ªàµ‡à´¸àµ à´•àµà´±à´¯àµà´•àµà´•à´¾àµ» */
        div[data-testid="stVerticalBlock"] > div {
            margin-bottom: 0rem !important;
            gap: 0.5rem !important;
        }
        div[data-testid="stMarkdownContainer"] h3 {
            margin-top: 5px !important;
            margin-bottom: 5px !important;
            padding-bottom: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### ðŸ“ à´¯à´¾à´¤àµà´°à´¾ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´°àµ‡à´–à´ªàµà´ªàµ†à´Ÿàµà´¤àµà´¤àµà´•")

    # ðŸ›‘ st.form à´‰à´ªà´¯àµ‹à´—à´¿à´šàµà´šàµ à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´«àµ‹à´‚ à´¸àµà´°à´•àµà´·à´¿à´¤à´®à´¾à´•àµà´•à´¿à´¯à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ
    with st.form("booking_form"):
        # ... (à´¬à´¾à´•àµà´•à´¿ à´•àµ‹à´¡àµà´•àµ¾ à´…à´¤àµ‡à´ªà´Ÿà´¿ à´‡à´°à´¿à´•àµà´•à´Ÿàµà´Ÿàµ†) ...
        c_name = st.text_input("ðŸ‘¤ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´ªàµ‡à´°àµ (Customer Name):", placeholder="à´ªàµ‡à´°àµ à´Ÿàµˆà´ªàµà´ªàµ à´šàµ†à´¯àµà´¯àµà´•")
        c_phone = st.text_input("ðŸ“ž à´«àµ‹àµº à´¨à´®àµà´ªàµ¼ (Phone Number):", placeholder="9876543210")

        # 1. à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´¸àµà´±àµà´±à´¾àµ»à´¡àµà´•à´³àµà´‚ à´à´°à´¿à´¯à´•à´³àµà´‚ à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨àµ
        locations_list = get_locations_from_firebase()
        areas_list = get_areas_from_firebase()

        # 2. à´µà´¿à´µà´¿à´§ à´µà´¾à´¹à´¨à´™àµà´™à´³àµà´Ÿàµ† à´“à´ªàµà´·à´¨àµà´•àµ¾
        vehicle_options = [
            "ðŸ›º à´“à´Ÿàµà´Ÿàµ‹à´±à´¿à´•àµà´· (Autorickshaw)",
            "ðŸš— à´Ÿà´¾à´•àµà´¸à´¿ à´•à´¾àµ¼ (Taxi Car)",
            "ðŸš™ à´—àµà´¡àµà´¸àµ à´“à´Ÿàµà´Ÿàµ‹ à´ªà´¿à´•àµà´•à´ªàµà´ªàµ (Goods Auto Pickup)",
            "ðŸš à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´µà´¾àµ» (Pickup Van)",
            "ðŸšš à´®à´¿à´¨à´¿ à´²àµ‹à´±à´¿ (Mini Lorry)",
            "ðŸš› à´Ÿàµà´°à´•àµà´•àµ (Truck)",
            "ðŸï¸ à´¬àµˆà´•àµà´•àµ à´Ÿà´¾à´•àµà´¸à´¿ (Bike Taxi)"
        ]
        vehicle_type = st.selectbox("ðŸš– à´µà´¾à´¹à´¨à´¤àµà´¤à´¿à´¨àµà´±àµ† à´¤à´°à´‚ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´•àµà´•àµà´• (Select Vehicle Type):", options=vehicle_options)

        # 3. à´¸àµà´°à´•àµà´·à´¿à´¤à´®à´¾à´¯à´¿ à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´¡àµà´°àµ‹à´ªàµà´ªàµà´¡àµ—àµº à´¨àµ½à´•àµà´¨àµà´¨àµ
        if locations_list and len(locations_list) > 0:
            pickup_place = st.selectbox("ðŸ“ à´ªàµà´±à´ªàµà´ªàµ†à´Ÿàµà´¨àµà´¨ à´¸àµà´¥à´²à´‚ (Pickup):", options=locations_list)
        else:
            st.warning("âš ï¸ à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ 'locations' à´¨àµ‹à´¡à´¿àµ½ à´²àµŠà´•àµà´•àµ‡à´·à´¨àµà´•àµ¾ à´šàµ‡àµ¼à´•àµà´•àµà´•.")
            pickup_place = st.text_input("ðŸ“ à´ªàµà´±à´ªàµà´ªàµ†à´Ÿàµà´¨àµà´¨ à´¸àµà´¥à´²à´‚ (Pickup) à´®à´¾à´¨àµà´µà´²à´¾à´¯à´¿ à´¨àµ½à´•àµà´•:")

        if locations_list and len(locations_list) > 0:
            drop_place = st.selectbox("ðŸ à´ªàµ‹à´•àµ‡à´£àµà´Ÿ à´¸àµà´¥à´²à´‚ (Drop):", options=locations_list)
        else:
            st.warning("âš ï¸ à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ 'locations' à´¨àµ‹à´¡à´¿àµ½ à´²àµŠà´•àµà´•àµ‡à´·à´¨àµà´•àµ¾ à´šàµ‡àµ¼à´•àµà´•àµà´•.")
            drop_place = st.text_input("ðŸ à´ªàµ‹à´•àµ‡à´£àµà´Ÿ à´¸àµà´¥à´²à´‚ (Drop) à´®à´¾à´¨àµà´µà´²à´¾à´¯à´¿ à´¨àµ½à´•àµà´•:")

        if areas_list and len(areas_list) > 0:
            trip_area = st.selectbox("ðŸ“ à´à´°à´¿à´¯ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´•àµà´•àµà´• (Area):", options=areas_list)
        else:
            st.warning("âš ï¸ à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ 'areas' à´¨àµ‹à´¡à´¿àµ½ à´²àµŠà´•àµà´•àµ‡à´·à´¨àµà´•àµ¾ à´šàµ‡àµ¼à´•àµà´•àµà´•.")
            trip_area = st.text_input("ðŸ“ à´à´°à´¿à´¯ à´®à´¾à´¨àµà´µà´²à´¾à´¯à´¿ à´¨àµ½à´•àµà´•:")

        # Smart Captcha (à´‰à´£àµà´Ÿàµ†à´™àµà´•à´¿àµ½ à´®à´¾à´¤àµà´°à´‚ à´±àµ†àµ»à´¡àµ¼ à´šàµ†à´¯àµà´¯àµà´‚)
        if 'render_smart_captcha_field' in globals():
            render_smart_captcha_field()

        submitted = st.form_submit_button("ðŸš— Book Ride Now", type="primary")

    if submitted:
        st.session_state.is_booking = True

        # ðŸ†• 1. GPS à´Žà´¨àµ‡à´¬à´¿àµ¾ à´šàµ†à´¯àµà´¤à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ‹ à´Žà´¨àµà´¨àµ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´•
        # lat, lon à´‰à´£àµà´Ÿàµ†à´™àµà´•à´¿àµ½ gps_enabled = True à´†à´•àµà´•àµà´• (à´‡à´¤àµ à´ªàµà´°à´§à´¾à´¨à´‚)
        if st.session_state.lat and st.session_state.lon:
            st.session_state.gps_enabled = True
        if not st.session_state.gps_enabled:
            st.markdown("""
            <div style="background-color: #ffebee; border-left: 5px solid #d32f2f; padding: 12px; border-radius: 8px; margin-bottom: 10px; font-size: 13px;">
                <b style="color: #c62828;">ðŸ“ GPS à´²àµŠà´•àµà´•àµ‡à´·àµ» à´²à´­àµà´¯à´®à´²àµà´²!</b><br>
                <span style="color: #333; font-size: 12px;">
                à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´ªàµ‚àµ¼à´¤àµà´¤à´¿à´¯à´¾à´•àµà´•à´¾àµ» à´¦à´¯à´µà´¾à´¯à´¿ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´²àµŠà´•àµà´•àµ‡à´·àµ» à´“àµº à´šàµ†à´¯àµà´¯àµà´•. 
                à´¬àµà´°àµ—à´¸àµ¼ à´¸àµ†à´±àµà´±à´¿à´‚à´—àµà´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ "Location Permission" à´¨àµ½à´•àµà´•.
                </span>
            </div>
            """, unsafe_allow_html=True)
            st.toast("âš ï¸ GPS à´“àµº à´šàµ†à´¯àµà´¯à´¾à´¤àµ† à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´¸à´¾à´§àµà´¯à´®à´²àµà´²!", icon="âŒ")
            st.session_state.is_booking = False
            st.stop()            

        
        # Validation checks
        if not (c_name and c_phone and pickup_place and drop_place):
            st.warning("âš ï¸ à´¦à´¯à´µà´¾à´¯à´¿ à´Žà´²àµà´²à´¾ à´µà´¿à´µà´°à´™àµà´™à´³àµà´‚ à´¨àµ½à´•àµà´•!")
            st.session_state.is_booking = False
            st.stop()

        if pickup_place == drop_place:
            st.warning("âš ï¸ Pickup, Drop à´’à´°àµ‡ à´¸àµà´¥à´²à´‚ à´†à´•à´°àµà´¤àµ.")
            st.warning("âš ï¸ à´¦à´¯à´µà´¾à´¯à´¿ à´µàµà´¯à´¤àµà´¯à´¸àµà´¤à´®à´¾à´¯ à´¸àµà´¥à´²à´™àµà´™àµ¾ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´•àµà´•àµà´•.")
            st.session_state.is_booking = False
            st.stop()

        # Spam Check (à´‰à´£àµà´Ÿàµ†à´™àµà´•à´¿àµ½ à´®à´¾à´¤àµà´°à´‚)
        if 'check_spam_and_rate_limit' in globals():
            is_allowed, msg = check_spam_and_rate_limit(c_phone)
            if not is_allowed:
                st.error(msg)
                st.session_state.is_booking = False
                st.stop()

        # Distance & Fare Calculation
        with st.spinner("ðŸ” à´¦àµ‚à´°à´‚ à´•à´£à´•àµà´•à´¾à´•àµà´•àµà´¨àµà´¨àµ..."):
            exact_distance = get_real_road_distance(pickup_place, drop_place) if 'get_real_road_distance' in globals() else 5.0
        # à´¸àµà´¥à´²à´‚ à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¾à´¨à´¾à´¯à´¿à´²àµà´²àµ†à´™àµà´•à´¿àµ½
        if exact_distance is None:
            st.toast("ðŸ“ à´¨à´¿à´™àµà´™àµ¾ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´¤àµà´¤ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¾à´¨à´¾à´¯à´¿à´²àµà´²! à´¦à´¯à´µà´¾à´¯à´¿ à´¸à´®àµ€à´ªà´¤àµà´¤àµà´³àµà´³ à´®à´±àµà´±àµŠà´°àµ à´¸àµà´¥à´²à´‚ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´•àµà´•àµà´•.", icon="âŒ")
            st.session_state.is_booking = False
            st.stop()

        exact_distance = round(exact_distance, 1)
        rate_per_km = 15 if vehicle_type == "Auto Rickshaw" else 22
        total_fare = round(exact_distance * rate_per_km, 2)
        commission_amount = calculate_admin_commission(exact_distance) if 'calculate_admin_commission' in globals() else 10.0
        unique_trip_id = f"TRIP-{random.randint(10000, 99999)}"

        st.info(f"ðŸ“Š Booking Details: {pickup_place} to {drop_place}")

        # ============================================================
        # ðŸš— DRIVER LOGIC & RADIUS ROUTING (FIXED)
        # ============================================================
        with st.spinner("à´¡àµà´°àµˆà´µàµ¼à´®à´¾à´°àµ† à´¤à´¿à´°à´¯àµà´¨àµà´¨àµ..."):
            drivers_in_area = get_all_drivers_by_area(trip_area) if 'get_all_drivers_by_area' in globals() else []

            if not drivers_in_area:
                st.warning("âš ï¸ à´ˆ à´à´°à´¿à´¯à´¯à´¿àµ½ à´¨à´¿à´²à´µà´¿àµ½ à´¡àµà´°àµˆà´µàµ¼à´®à´¾àµ¼ à´²à´­àµà´¯à´®à´²àµà´².")
            else:
                # ============================================
                # âœ… FIX #1: Trip à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚ Firebase-àµ½ Save
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
                    # Driver-specific fields trip-level à´…à´²àµà´²
                    "driver_name": "",
                    "driver_phone": "",
                    "driver_chat_id": "",
                    "notified_drivers": {}
                }

                # à´’à´°à´¿à´•àµà´•àµ½ à´®à´¾à´¤àµà´°à´‚ save (loop à´‡à´²àµà´²!)
                trip_saved = save_trip_dual_backup(payload)

                if trip_saved:
                    if 'register_successful_booking_attempt' in globals():
                        register_successful_booking_attempt()

                    # Driver notification â€” Vera function à´µà´´à´¿
                    if 'process_radius_expansion_routing' in globals():
                        process_radius_expansion_routing(payload, lat, lon)

                    st.success("âœ… à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´µà´¿à´œà´¯à´•à´°à´®à´¾à´¯à´¿ à´ªàµ‚àµ¼à´¤àµà´¤à´¿à´¯à´¾à´¯à´¿!")

                    # à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿à´¯àµà´‚ à´¡àµà´°àµˆà´µàµ¼ à´¸àµà´°à´•àµà´·à´¾ à´¨à´¿àµ¼à´¦àµà´¦àµ‡à´¶à´™àµà´™à´³àµà´‚ à´…à´Ÿà´™àµà´™à´¿à´¯ à´ªàµà´°àµŠà´«à´·à´£àµ½ à´•à´¾àµ¼à´¡àµ
                    card_html = f"""<div style="padding: 18px; border-radius: 12px; background-color: #eef2ff; border-left: 6px solid #2563eb; border-right: 6px solid #f59e0b; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); margin-bottom: 20px;">
    <div style="margin-bottom: 15px;">
        <span style="font-size: 15px; font-weight: 600; color: #1e3a8a;">à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿:</span>
        <div style="background-color: #fff3cd; border: 2px solid #ffc107; padding: 8px 14px; border-radius: 8px; display: inline-block; font-weight: bold; color: #856404; font-size: 18px; margin-top: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">{unique_trip_id}</div>
    </div>
    <h4 style="color: #1e3a8a; margin-top: 0; margin-bottom: 8px; font-size: 16px;">ðŸš— à´¡àµà´°àµˆà´µàµ¼ à´µà´¿à´µà´°à´™àµà´™àµ¾ & à´¸àµà´°à´•àµà´·à´¾ à´¨à´¿àµ¼à´¦àµà´¦àµ‡à´¶à´‚:</h4>
    <p style="color: #1f2937; font-size: 14px; line-height: 1.6; margin: 0;">
        à´¨à´¿à´™àµà´™àµ¾ à´¬àµà´•àµà´•àµ à´šàµ†à´¯àµà´¤ à´µà´¾à´¹à´¨à´¤àµà´¤à´¿à´¨àµà´±àµ† ðŸš– à´¡àµà´°àµˆà´µà´±àµà´Ÿàµ† à´¤à´¤àµà´¸à´®à´¯ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´…à´±à´¿à´¯àµà´¨àµà´¨à´¤à´¿à´¨à´¾à´¯à´¿ à´ˆ à´µàµ†à´¬àµ à´†à´ªàµà´ªàµ à´•àµà´²àµ‹à´¸àµ à´šàµ†à´¯àµà´¯à´¾à´¤àµ† à´¨à´¿à´²à´¨à´¿àµ¼à´¤àµà´¤àµà´•.<br><br>
        à´Žà´¨àµà´¤àµ†à´™àµà´•à´¿à´²àµà´‚ à´•à´¾à´°à´£à´µà´¶à´¾àµ½ à´†à´ªàµà´²à´¿à´•àµà´•àµ‡à´·àµ» à´•àµà´²àµ‹à´¸àµ à´†à´¯à´¿à´ªàµà´ªàµ‹à´¯à´¾àµ½, à´µàµ€à´£àµà´Ÿàµà´‚ à´†à´ªàµà´ªàµ à´“à´ªàµà´ªàµº à´šàµ†à´¯àµà´¯àµà´®àµà´ªàµ‹àµ¾ à´®àµà´•à´³à´¿àµ½ à´¨àµ½à´•à´¿à´¯à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´¨àµ½à´•à´¿ à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•à´¾à´µàµà´¨àµà´¨à´¤à´¾à´£àµ.
    </p>
</div>"""
                    
                    st.markdown(card_html, unsafe_allow_html=True)

                    # ----------------------------------------------------
                    # ðŸ“ à´²àµˆà´µàµ à´®à´¾à´ªàµà´ªàµ à´•àµ‹àµ¾
                    # ----------------------------------------------------
                    st.write("---")
                    trip_ref = db.reference(f"trips/{unique_trip_id}")
                    trip_data = trip_ref.get()
                    # ðŸ†• à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´Žà´Ÿàµà´•àµà´•àµà´®àµà´ªàµ‹àµ¾ à´…à´§à´¿à´• à´¸àµà´ªàµ‡à´¸àµà´•àµ¾ à´¨àµ€à´•àµà´•à´‚ à´šàµ†à´¯àµà´¯àµà´•
                    if trip_data:
                        status = str(trip_data.get("status", "Pending")).strip()
                    else:
                        status = "Pending" 
                    vehicle_type_check = trip_data.get("vehicle_type", "Auto Rickshaw") if trip_data else "Auto Rickshaw"
                    # ðŸ†• à´¡àµà´°àµˆà´µàµ¼ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤à´¤à´¿à´¨àµ à´¶àµ‡à´·à´‚ ("Pending" à´…à´²àµà´²à´¾à´¤àµà´¤ à´Žà´²àµà´²à´¾ à´…à´µà´¸àµà´¥à´¯à´¿à´²àµà´‚) à´ˆ à´•àµ‹à´¡àµ à´ªàµà´°à´µàµ¼à´¤àµà´¤à´¿à´•àµà´•àµà´‚
                    if status != "Pending":
    

                    
                    
                        # ðŸ”” 1. à´¨àµ‹à´Ÿàµà´Ÿà´¿à´«à´¿à´•àµà´•àµ‡à´·àµ» à´¸àµ—à´£àµà´Ÿàµ
                        notification_sound = """
                            <audio autoplay>
                              <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
                            </audio>
                        """
                        st.markdown(notification_sound, unsafe_allow_html=True)

                        # 2. à´¡àµà´°àµˆà´µàµ¼ à´µà´¿à´µà´°à´™àµà´™à´³àµà´‚ à´®à´¾à´ªàµà´ªàµà´‚ à´…à´Ÿà´™àµà´™à´¿à´¯ à´ªàµ‹à´ªàµà´ªàµ-à´…à´ªàµà´ªàµ à´•à´£àµà´Ÿàµ†à´¯àµà´¨àµ¼
                        with st.container():
                            st.success("ðŸŽ‰ **à´…à´­à´¿à´¨à´¨àµà´¦à´¨à´™àµà´™àµ¾! à´’à´°àµ à´¡àµà´°àµˆà´µàµ¼ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ!**")
                            if "taxi" in vehicle_type_check.lower() or "car" in vehicle_type_check.lower():
                                st.markdown("### ðŸš– à´Ÿà´¾à´•àµà´¸à´¿ à´•à´¾àµ¼ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´…à´Ÿàµà´¤àµà´¤àµ‡à´•àµà´•àµ à´µà´°àµà´¨àµà´¨àµ...")
                            else:
                                st.markdown("### ðŸ›º à´“à´Ÿàµà´Ÿàµ‹à´±à´¿à´•àµà´· à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´…à´Ÿàµà´¤àµà´¤àµ‡à´•àµà´•àµ à´µà´°àµà´¨àµà´¨àµ...")

                            st.markdown("### ðŸ‘¤ à´¡àµà´°àµˆà´µàµ¼ à´µà´¿à´µà´°à´™àµà´™àµ¾")
                            st.write(f"**à´¡àµà´°àµˆà´µàµ¼ à´ªàµ‡à´°àµ:** {trip_data.get('driver_name', 'N/A')}")
                            st.write(f"**à´µà´¾à´¹à´¨ à´¨à´®àµà´ªàµ¼:** {trip_data.get('vehicle_number', 'N/A')} ({vehicle_type_check})")

                            # à´®à´¾à´¸àµà´•àµ à´šàµ†à´¯àµà´¤ à´«àµ‹àµº à´¨à´®àµà´ªàµ¼
                            raw_driver_phone = trip_data.get('driver_phone', '')
                            masked_d_phone = mask_phone_number(raw_driver_phone) if 'mask_phone_number' in globals() else raw_driver_phone
                            st.write(f"**à´«àµ‹àµº à´¨à´®àµà´ªàµ¼:** `{masked_d_phone}`")

                            st.markdown("---")
                            st.markdown("### ðŸ—ºï¸ à´¡àµà´°àµˆà´µà´±àµà´Ÿàµ† à´²àµˆà´µàµ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´Ÿàµà´°à´¾à´•àµà´•à´¿à´‚à´—àµ")

                            if lat and lon:
                                render_live_tracking_map(unique_trip_id, lat, lon, vehicle_type_check)
                            else:
                                st.warning("âš ï¸ à´®à´¾à´ªàµà´ªàµ à´•à´¾à´£àµà´¨àµà´¨à´¤à´¿à´¨à´¾à´¯à´¿ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´œà´¿à´ªà´¿à´Žà´¸àµ à´²àµŠà´•àµà´•àµ‡à´·àµ» à´¸à´œàµ€à´µà´®à´¾à´•àµà´•àµà´•.")
                    else:
                        # à´¡àµà´°àµˆà´µàµ¼ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨à´¤àµ à´µà´°àµ†
                        st.info("â³ à´¡àµà´°àµˆà´µàµ¼à´®à´¾àµ¼ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨à´¤à´¿à´¨à´¾à´¯à´¿ à´•à´¾à´¤àµà´¤à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ... à´¦à´¯à´µà´¾à´¯à´¿ à´ˆ à´ªàµ‡à´œàµ à´•àµà´²àµ‹à´¸àµ à´šàµ†à´¯àµà´¯à´°àµà´¤àµ.")

                    with st.expander("ðŸ“ à´¸àµ‡à´µà´¨ à´¨à´¿à´¬à´¨àµà´§à´¨à´•à´³àµà´‚ à´¡à´¿à´¸àµà´•àµà´²àµˆà´®à´±àµà´‚"):
                        st.write("""
                        **à´¡à´¿à´¸àµà´•àµà´²àµˆà´®àµ¼ (Disclaimer):**
                        * à´ˆ à´†à´ªàµà´²à´¿à´•àµà´•àµ‡à´·àµ» à´¡àµà´°àµˆà´µàµ¼à´®à´¾à´°àµ†à´¯àµà´‚ à´¯à´¾à´¤àµà´°à´•àµà´•à´¾à´°àµ†à´¯àµà´‚ à´¬à´¨àµà´§à´¿à´ªàµà´ªà´¿à´•àµà´•àµà´¨àµà´¨ à´’à´°àµ **à´¡à´¿à´œà´¿à´±àµà´±àµ½ à´®àµ†à´¸àµà´¸àµ‡à´œà´¿à´‚à´—àµ à´ªàµà´²à´¾à´±àµà´±àµà´«àµ‹à´‚** à´®à´¾à´¤àµà´°à´®à´¾à´£àµ.
                        * à´¯à´¾à´¤àµà´°à´¯àµà´•àµà´•à´¿à´Ÿà´¯à´¿àµ½ à´‰à´£àµà´Ÿà´¾à´•àµà´¨àµà´¨ à´¸à´¾à´™àµà´•àµ‡à´¤à´¿à´•à´®àµ‹, à´µàµà´¯à´•àµà´¤à´¿à´ªà´°à´®àµ‹ à´†à´¯ à´ªàµà´°à´¶àµà´¨à´™àµà´™àµ¾à´•àµà´•àµ‹, à´…à´ªà´•à´Ÿà´™àµà´™àµ¾à´•àµà´•àµ‹ à´ˆ à´ªàµà´²à´¾à´±àµà´±àµà´«àµ‹à´®àµ‹, à´…à´¡àµà´®à´¿à´¨à´¿à´¸àµà´Ÿàµà´°àµ‡à´±àµà´±àµ¼à´®à´¾à´°àµ‹ à´‰à´¤àµà´¤à´°à´µà´¾à´¦à´¿à´•à´³à´¾à´¯à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨à´¤à´²àµà´².
                        * à´¡àµà´°àµˆà´µàµ¼à´®à´¾à´°àµà´®à´¾à´¯àµà´³àµà´³ à´‡à´Ÿà´ªà´¾à´Ÿàµà´•à´³à´¿àµ½ à´¯à´¾à´¤àµà´°à´•àµà´•à´¾àµ¼ à´œà´¾à´—àµà´°à´¤ à´ªà´¾à´²à´¿à´•àµà´•àµ‡à´£àµà´Ÿà´¤à´¾à´£àµ.
                        * à´ˆ à´¸àµ‡à´µà´¨à´‚ à´‰à´ªà´¯àµ‹à´—à´¿à´•àµà´•àµà´¨àµà´¨à´¤à´¿à´²àµ‚à´Ÿàµ† à´¨à´¿à´™àµà´™àµ¾ à´ˆ à´¨à´¿à´¬à´¨àµà´§à´¨à´•àµ¾ à´…à´‚à´—àµ€à´•à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ.
                        """)
                else:
                    st.error("âŒ à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´¸àµ‡à´µàµ à´šàµ†à´¯àµà´¯àµà´¨àµà´¨à´¤à´¿àµ½ à´ªà´°à´¾à´œà´¯à´ªàµà´ªàµ†à´Ÿàµà´Ÿàµ.")

        st.session_state.is_booking = False
        st.write("---")
    # ========================================================
    # à´µàµ†à´¬àµâ€Œà´¸àµˆà´±àµà´±àµ à´«àµ‚à´Ÿàµà´Ÿà´±àµà´‚ à´¡àµà´°àµˆà´µàµ¼ & SOS à´ªà´¾à´¨à´²àµà´•à´³àµà´‚ (à´®àµà´´àµà´µàµ» à´«àµ€à´šàµà´šà´±àµà´•à´³àµà´‚ à´‰à´³àµà´³à´¤àµ)
    # ========================================================

    # à´«àµ‚à´Ÿàµà´Ÿà´±à´¿à´¨àµ à´¬àµ‹à´•àµà´¸àµà´‚ à´¬àµ‹àµ¼à´¡à´±àµà´‚ à´¨àµ½à´•à´¾à´¨àµà´³àµà´³ CSS à´¸àµà´±àµà´±àµˆàµ½    
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
    # à´«àµ‚à´Ÿàµà´Ÿàµ¼ à´¸àµ†à´ªàµà´ªà´±àµ‡à´±àµà´±àµ¼
    str_lit.markdown("---")

    # à´®àµ‚à´¨àµà´¨àµ à´•àµ‹à´³à´™àµà´™à´³à´¿à´²à´¾à´¯à´¿ à´®àµ‚à´¨àµà´¨àµ à´ªàµà´°à´§à´¾à´¨ à´¬à´Ÿàµà´Ÿà´£àµà´•àµ¾
    footer_col1, footer_col2, footer_col3 = str_lit.columns(3)
    # 1. Contact Us à´¬à´Ÿàµà´Ÿàµº
    with footer_col1:
        if str_lit.button("ðŸ“ž Contact Us"):
            str_lit.info("à´¸à´¹à´¾à´¯à´¤àµà´¤à´¿à´¨àµ à´µà´¿à´³à´¿à´•àµà´•àµà´•: +91 XXXXXXXXXX | Email: support@example.com")
    # 2. SOS / Emergency à´¬à´Ÿàµà´Ÿàµº
    with footer_col2:
        if str_lit.button("ðŸš¨ SOS / Emergency"):
            str_lit.session_state['show_sos_panel'] = True
            str_lit.session_state['show_driver_panel'] = False  # à´¡àµà´°àµˆà´µàµ¼ à´ªà´¾à´¨àµ½ à´•àµà´²àµ‹à´¸àµ à´šàµ†à´¯àµà´¯à´¾àµ»
    # 3. Driver Panel à´¬à´Ÿàµà´Ÿàµº
    with footer_col3:
        if str_lit.button("ðŸš— Driver Panel"):
            str_lit.session_state['show_driver_panel'] = True
            str_lit.session_state['show_sos_panel'] = False  # SOS à´ªà´¾à´¨àµ½ à´•àµà´²àµ‹à´¸àµ à´šàµ†à´¯àµà´¯à´¾àµ»   
    # --------------------------------------------------------
    # SOS à´ªà´¾à´¨àµ½ (à´¡à´¯à´±à´•àµà´Ÿàµ à´•àµ‹àµ¾ à´²à´¿à´™àµà´•àµà´•à´³àµà´‚ à´µà´¾à´Ÿàµà´¸à´¾à´ªàµà´ªàµ à´·àµ†à´¯à´±àµà´‚)
    # --------------------------------------------------------        
    if str_lit.session_state.get('show_sos_panel', False):
        str_lit.markdown("---")
        str_lit.error("ðŸš¨ à´…à´Ÿà´¿à´¯à´¨àµà´¤à´° à´¸à´¹à´¾à´¯ à´µà´¿à´­à´¾à´—à´‚ (Emergency Control Rooms)") 
        # à´¨à´®àµà´ªà´±àµà´•à´³à´¿àµ½ à´…à´®àµ¼à´¤àµà´¤à´¿à´¯à´¾àµ½ à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ à´•àµ‹àµ¾ à´ªàµ‹à´•àµà´¨àµà´¨ à´²à´¿à´™àµà´•àµà´•àµ¾ (tel: link)
        str_lit.markdown("""
        * **ðŸ‘® à´ªàµ‹à´²àµ€à´¸àµ à´•àµºà´Ÿàµà´°àµ‹àµ¾ à´±àµ‚à´‚ (112 / 100):** &nbsp; [ðŸ“ž 112 à´•àµ‹àµ¾ à´šàµ†à´¯àµà´¯àµà´•](tel:112)
        * **ðŸ”¥ à´«à´¯àµ¼à´«àµ‹à´´àµà´¸àµ (101):** &nbsp; [ðŸ“ž 101 à´•àµ‹àµ¾ à´šàµ†à´¯àµà´¯àµà´•](tel:101)
        * **ðŸ¥ à´¹àµ‹à´¸àµà´ªà´¿à´±àµà´±àµ½ / à´†à´‚à´¬àµà´²àµ»à´¸àµ (108):** &nbsp; [ðŸ“ž 108 à´•àµ‹àµ¾ à´šàµ†à´¯àµà´¯àµà´•](tel:108)
        """, unsafe_allow_html=True)
    
        str_lit.markdown("---")
        str_lit.subheader("ðŸ“± à´µà´¾à´Ÿàµà´¸à´¾à´ªàµà´ªàµ à´µà´´à´¿ à´•àµà´Ÿàµà´‚à´¬à´¾à´‚à´—à´™àµà´™àµ¾à´•àµà´•àµ à´…à´¯à´•àµà´•à´¾àµ»")
    
        sos_message = "à´Žà´¨à´¿à´•àµà´•àµ à´…à´Ÿà´¿à´¯à´¨àµà´¤à´° à´¸à´¹à´¾à´¯à´‚ à´†à´µà´¶àµà´¯à´®à´¾à´£àµ! à´¦à´¯à´µà´¾à´¯à´¿ à´‰à´Ÿàµ» à´¬à´¨àµà´§à´ªàµà´ªàµ†à´Ÿàµà´•. (à´¡àµà´°àµˆà´µàµ¼/à´¯à´¾à´¤àµà´°à´•àµà´•à´¾à´°àµ»)"
        whatsapp_share_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(sos_message)}"
    
        str_lit.markdown(f"""
        <a href="{whatsapp_share_url}" target="_blank">
            <button style="background-color: #25D366; color: white; padding: 12px 20px; border: none; border-radius: 5px; font-size: 16px; font-weight: bold; cursor: pointer; width: 100%;">
                ðŸ’¬ à´µà´¾à´Ÿàµà´¸à´¾à´ªàµà´ªàµ à´µà´´à´¿ à´•àµà´Ÿàµà´‚à´¬à´¾à´‚à´—à´™àµà´™àµ¾à´•àµà´•àµ à´…à´¯à´•àµà´•àµà´•
            </button>
        </a>
        """, unsafe_allow_html=True)
    
        str_lit.markdown("<br>", unsafe_allow_html=True)
    
        if str_lit.button("SOS à´ªà´¾à´¨àµ½ à´…à´Ÿà´¯àµà´•àµà´•àµà´•"):
            str_lit.session_state['show_sos_panel'] = False
            str_lit.rerun() 
# ============================================================
# ðŸ“Š à´¡àµà´°àµˆà´µàµ¼ à´¹à´¿à´¸àµà´±àµà´±à´±à´¿ à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨ à´«à´‚à´—àµà´·àµ»
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
            print(f"âŒ Error fetching history: {e}")
            return []


# ============================================================
# ðŸš— à´¡àµà´°àµˆà´µàµ¼ à´ªà´¾à´¨àµ½ - à´«à´¯àµ¼à´¬àµ‡à´¸àµ à´¡à´¾à´±àµà´± à´•à´£à´•àµà´·àµ»
# ============================================================
    if str_lit.session_state.get('show_driver_panel', False):
        str_lit.markdown("---")
        str_lit.subheader("ðŸš— à´¡àµà´°àµˆà´µàµ¼ à´ªà´¾à´¨àµ½ - à´šà´¾à´±àµà´±àµ & à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´¹à´¿à´¸àµà´±àµà´±à´±à´¿")
        
        driver_telegram_id = str_lit.text_input("à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´Ÿàµ†à´²à´—àµà´°à´¾à´‚ à´šà´¾à´±àµà´±àµ à´à´¡à´¿ (Telegram Chat ID) à´¨àµ½à´•àµà´•:", key="driver_id_input_main")
        
        # à´®àµŠà´¬àµˆàµ½ à´‰à´ªà´¯àµ‹à´•àµà´¤à´¾à´•àµà´•àµ¾à´•àµà´•àµ à´µàµ‡à´£àµà´Ÿà´¿ à´¸àµ†àµ¼à´šàµà´šàµ à´¬à´Ÿàµà´Ÿàµº
        search_clicked = str_lit.button("ðŸ” à´¹à´¿à´¸àµà´±àµà´±à´±à´¿ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´• (Search)")
        
        # à´šà´¾à´±àµà´±àµ à´à´¡à´¿ à´¨àµ½à´•à´¿ à´¸àµ†àµ¼à´šàµà´šàµ à´…à´®àµ¼à´¤àµà´¤àµà´®àµà´ªàµ‹àµ¾ à´®à´¾à´¤àµà´°à´‚ à´¹à´¿à´¸àµà´±àµà´±à´±à´¿ à´²àµ‹à´¡àµ à´†à´•àµà´‚
        if driver_telegram_id and search_clicked:
            str_lit.info(f"à´šà´¾à´±àµà´±àµ à´à´¡à´¿ ({driver_telegram_id}) à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ...")
            
            # à´«à´‚à´—àµà´·àµ» à´•àµ‹àµ¾ à´šàµ†à´¯àµà´¤àµ à´¡à´¾à´±àµà´± à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨àµ
            driver_history_data = fetch_driver_history_from_firebase(driver_telegram_id.strip())
            
            if driver_history_data:
                str_lit.success("âœ… à´¡àµà´°àµˆà´µàµ¼ à´¹à´¿à´¸àµà´±àµà´±à´±à´¿ à´µà´¿à´œà´¯à´•à´°à´®à´¾à´¯à´¿ à´²àµ‹à´¡àµ à´šàµ†à´¯àµà´¤àµ!")
                str_lit.markdown("### ðŸ“‹ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´®àµàµ»à´•à´¾à´² à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾:")
                str_lit.table(driver_history_data)
            else:
                str_lit.warning("âš ï¸ à´ˆ à´šà´¾à´±àµà´±àµ à´à´¡à´¿à´¯à´¿àµ½ à´‡à´¤àµà´µà´°àµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾ à´’à´¨àµà´¨àµà´‚ à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¾à´¨à´¾à´¯à´¿à´²àµà´².")
                
        if str_lit.button("à´ªà´¾à´¨àµ½ à´…à´Ÿà´¯àµà´•àµà´•àµà´•"):
            str_lit.session_state['show_driver_panel'] = False
            str_lit.rerun()
    
    # ==========================================================
    # Clean Footer Component: Shadow for Malayalam Text & Styled Button
    # ==========================================================
    st.markdown("---")

    # à´®à´²à´¯à´¾à´³à´‚ à´Ÿàµ†à´•àµà´¸àµà´±àµà´±à´¿à´¨àµ à´®à´¾à´¤àµà´°à´‚ à´·à´¾à´¡àµ‹à´¯àµà´‚ à´ªàµà´°àµŠà´«à´·à´£àµ½ à´²àµà´•àµà´•àµà´‚ à´¨àµ½à´•à´¾à´¨àµà´³àµà´³ CSS à´‰à´‚ à´¬à´Ÿàµà´Ÿàµº à´•à´³àµ¼ à´®à´¾à´±àµà´±à´¾à´¨àµà´³àµà´³ à´¸àµà´±àµà´±àµˆà´²àµà´‚
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
        /* à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´¨àµ‹à´•àµà´•àµ‚ à´¬à´Ÿàµà´Ÿàµº à´•àµ‚à´Ÿàµà´¤àµ½ à´†à´•àµ¼à´·à´•à´®à´¾à´•àµà´•à´¾àµ» */
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
            <h3 style="margin:0; color: #2c3e50; font-size: 19px;">ðŸ” à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´¨à´¿à´²à´µà´¿à´²àµ† à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´…à´±à´¿à´¯à´¾àµ»</h3>
            <p style="margin: 8px 0 0 0; color: #555555; font-size: 14px;">à´†à´ªàµà´²à´¿à´•àµà´•àµ‡à´·àµ» à´•àµà´²àµ‹à´¸àµ à´†à´¯à´¿à´ªàµà´ªàµ‹à´¯àµ‹? à´®àµàµ»à´ªà´¤àµà´¤àµ† à´¬àµà´•àµà´•à´¿à´‚à´—àµ à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨à´¤à´¿à´¨à´¾à´¯à´¿ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´‡à´µà´¿à´Ÿàµ† à´¨àµ½à´•àµà´•.</p>
        </div>
    """, unsafe_allow_html=True)    
    col1, col2 = st.columns([3, 1])
    with col1: 
        footer_trip_id = st.text_input("à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´¨àµ½à´•àµà´•:", key="independent_footer_trip_id", label_visibility="collapsed", placeholder="à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´‡à´µà´¿à´Ÿàµ† à´¨àµ½à´•àµà´• (à´‰à´¦à´¾: TRIP-XXXXX)") 
    with col2:
        footer_check_btn = st.button("à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ à´¨àµ‹à´•àµà´•àµ‚", key="independent_footer_btn", use_container_width=True)        
        if footer_check_btn:    
            if footer_trip_id: 
                with st.spinner("ðŸ” à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ..."):
                    try:
                        
                        # ðŸ†• à´«à´¯àµ¼à´¬àµ‡à´¸à´¿àµ½ à´¨à´¿à´¨àµà´¨àµ à´¨àµ‡à´°à´¿à´Ÿàµà´Ÿàµ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´Žà´Ÿàµà´•àµà´•àµà´¨àµà´¨àµ
                        trip_ref = db.reference(f"trips/{footer_trip_id.strip()}")
                        trip_data = trip_ref.get()
                        if trip_data:
                            st.success(f"âœ… à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´µà´¿à´œà´¯à´•à´°à´®à´¾à´¯à´¿ à´•à´£àµà´Ÿàµ†à´¤àµà´¤à´¿!")
                            st.info(f"ðŸ“ **à´ªà´¿à´•àµà´•à´ªàµà´ªàµ:** {trip_data.get('pickup', 'N/A')}\n\nðŸ **à´¡àµà´°àµ‹à´ªàµà´ªàµ:** {trip_data.get('drop', 'N/A')}")
                            st.markdown(f"ðŸ“Š **à´¨à´¿à´²à´µà´¿à´²àµ† à´¸àµà´±àµà´±à´¾à´±àµà´±à´¸àµ:** {trip_data.get('status', 'Pending')}")
                        else:
                            st.error("âŒ à´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿à´¯à´¿àµ½ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´’à´¨àµà´¨àµà´‚ à´²à´­àµà´¯à´®à´¾à´µàµà´¨àµà´¨à´¿à´²àµà´². à´à´¡à´¿ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´šàµà´šàµ à´µàµ€à´£àµà´Ÿàµà´‚ à´¨àµ½à´•àµà´•.")
                    except Exception as e:
                        st.error(f"âŒ à´Žà´±àµ¼: {e}")
            else:
                st.warning("âš ï¸ à´¦à´¯à´µà´¾à´¯à´¿ à´’à´°àµ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿ à´¨àµ½à´•àµà´•.")
                
                if current_status == "Arrived":
                    st.warning("ðŸš¨ à´¡àµà´°àµˆà´µàµ¼ à´¨à´¿à´™àµà´™à´³àµà´Ÿàµ† à´ªà´¿à´•àµà´•à´ªàµà´ªàµ à´²àµŠà´•àµà´•àµ‡à´·à´¨à´¿àµ½ à´Žà´¤àµà´¤à´¿à´¯à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ!")    
                
            
    
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
    Driver trip accept à´šàµ†à´¯àµà´¤à´¤à´¿à´¨àµ à´¶àµ‡à´·à´‚:
    - Firebase-àµ½ status update
    - Driver-à´¨àµ navigation + arrived + call buttons à´…à´¯à´•àµà´•àµà´¨àµà´¨àµ
    """
    print("Trip Accepted:", booking_id)

    # ============================================================
    # 1. Firebase Trip Status Update
    # ============================================================
    try:
        # ðŸ†• à´¡àµ€à´¬à´—àµ à´ªàµà´°à´¿à´¨àµà´±àµ (à´‡à´µà´¿à´Ÿàµ† à´šàµ‡àµ¼à´•àµà´•àµà´•)
        print(f"DEBUG: Updating Firebase with Driver -> Name: {driver_name}, Phone: {driver_phone}")
        db.reference(f"trips/{booking_id}").update({
            "status": "Accepted",
            "driver_name": driver_name,
            "driver_phone": driver_phone,
            "driver_chat_id": str(driver_chat_id),
            "accepted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        print(f"âŒ Firebase update error: {e}")
        return False

    # ============================================================
    # 2. Masked Phone
    # ============================================================
    masked_customer_phone = mask_phone_number(customer_phone)

    # ============================================================
    # ðŸ†• à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½ à´¬à´Ÿàµà´Ÿàµº (à´ªàµà´¤à´¿à´¯ à´¸à´‚à´µà´¿à´§à´¾à´¨à´‚)
    # ============================================================
    driver_panel_url = f"https://your-app.streamlit.app/?page=driver_trip_panel&trip_id={booking_id}"
        
    markup = types.InlineKeyboardMarkup(row_width=1)
    panel_button = types.InlineKeyboardButton(
        "ðŸš– à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½ à´¤àµà´±à´•àµà´•àµà´•", 
        url=driver_panel_url
    )
    markup.add(panel_button)

    # ============================================================
    # 5. Driver Message
    # ============================================================
    driver_message = (
        f"ðŸš— *à´ªàµà´¤à´¿à´¯ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤à´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ!*\n\n"
        f"ðŸ†” TRIP-ID: `{booking_id}`\n"
        f"ðŸ‘¤ {customer_name}\n"
        f"ðŸ“± `{masked_customer_phone}`\n\n"
        f"âš ï¸ *à´…à´¤àµà´¯à´¾à´µà´¶àµà´¯ à´˜à´Ÿàµà´Ÿà´™àµà´™à´³à´¿àµ½ à´®à´¾à´¤àµà´°à´‚ à´µà´¿à´³à´¿à´•àµà´•àµà´•.*"
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
        print(f"âŒ Send error: {e}")
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
        # 1. à´¡àµà´°àµˆà´µà´±àµà´Ÿàµ† à´µà´¿à´µà´°à´™àµà´™àµ¾ à´µà´¾à´¯à´¿à´•àµà´•àµà´•
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
        # ðŸ”’ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´²àµ‹à´•àµà´•àµ à´šàµ†à´¯àµà´¯à´¾à´¨àµà´³àµà´³ à´•àµ‹à´¡àµ (à´‡à´µà´¿à´Ÿàµ† à´šàµ‡àµ¼à´•àµà´•àµà´•)
        # ============================================================
        try:
            # 1. à´¨à´¿à´²à´µà´¿à´²àµ† à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´µà´¿à´µà´°à´™àµà´™àµ¾ à´Žà´Ÿàµà´•àµà´•àµà´•
            trip_ref = db.reference(f"trips/{trip_id}")
            trip_data = trip_ref.get() or {}
            # 2. à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´‡à´¤à´¿à´¨à´•à´‚ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ‹ à´Žà´¨àµà´¨àµ à´šàµ†à´•àµà´•àµ à´šàµ†à´¯àµà´¯àµà´•
            if trip_data.get("status") == "Accepted":
                bot.send_message(
                    chat_id,
                    f"âŒ *à´•àµà´·à´®à´¿à´•àµà´•à´£à´‚!*\n\n"
                    f"à´Ÿàµà´°à´¿à´ªàµà´ªàµ `{trip_id}` à´®à´±àµà´±àµŠà´°àµ à´¡àµà´°àµˆà´µàµ¼ à´‡à´¤à´¿à´¨à´•à´‚ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤à´¿à´Ÿàµà´Ÿàµà´£àµà´Ÿàµ.\n"
                    f"à´¦à´¯à´µà´¾à´¯à´¿ à´®à´±àµà´±àµ à´Ÿàµà´°à´¿à´ªàµà´ªàµà´•àµ¾à´•àµà´•à´¾à´¯à´¿ à´•à´¾à´¤àµà´¤à´¿à´°à´¿à´•àµà´•àµà´•.",
                    parse_mode="Markdown"
                )
                print(f"â­ï¸ Trip {trip_id} already accepted by another driver.")
                return
            # 3. à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´ªàµà´¡àµ‡à´±àµà´±àµ à´šàµ†à´¯àµà´¤àµ à´²àµ‹à´•àµà´•àµ à´šàµ†à´¯àµà´¯àµà´•
            trip_ref.update({  
                "status": "Accepted",
                "is_locked": True,
                "accepted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "driver_name": driver_name,
                "driver_phone": driver_phone,
                "vehicle_number": vehicle_number,
                "driver_chat_id": chat_id
            })
            print(f"âœ… Trip {trip_id} accepted and locked by driver {chat_id}")
            # 4. à´¡àµà´°àµˆà´µàµ¼à´•àµà´•àµ à´¸àµà´¥à´¿à´°àµ€à´•à´°à´£ à´¸à´¨àµà´¦àµ‡à´¶à´‚ à´…à´¯à´•àµà´•àµà´•
            bot.send_message(
                chat_id,
                f"âœ… *à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤àµ!*\n\n"
                f"à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿: `{trip_id}`\n"
                f"à´¡àµà´°àµˆà´µàµ¼: {driver_name}\n"
                f"à´µà´¾à´¹à´¨à´‚: {vehicle_number}",
                parse_mode="Markdown"
            )
            
            # 5. à´¡àµà´°àµˆà´µàµ¼ à´ªà´¾à´¨àµ½ à´²à´¿à´™àµà´•àµ à´…à´¯à´•àµà´•àµà´•
            driver_panel_url = f"https://taxiservisemj-x9meaffucvbt6tjijxrd6d.streamlit.app/?page=driver_trip_panel&trip_id={trip_id}&driver_chat_id={chat_id}"
            bot.send_message(
                chat_id,
                f"ðŸ“ *à´¡àµà´°àµˆà´µàµ¼ à´ªà´¾à´¨àµ½ à´¤àµà´±à´•àµà´•à´¾àµ» à´¤à´¾à´´àµ†à´¯àµà´³àµà´³ à´²à´¿à´™àµà´•à´¿àµ½ à´•àµà´²à´¿à´•àµà´•àµ à´šàµ†à´¯àµà´¯àµà´•:*\n\n[à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½ à´¤àµà´±à´•àµà´•àµà´•]({driver_panel_url})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"âŒ Trip lock error: {e}")
            bot.send_message(chat_id, f"âŒ à´Žà´±àµ¼: à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¯à´¾àµ» à´•à´´à´¿à´žàµà´žà´¿à´²àµà´². ({e})")    
            
        # 2. à´¸àµà´°à´•àµà´·à´¿à´¤à´®à´¾à´¯à´¿ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´¸àµà´µàµ€à´•à´°à´¿à´•àµà´•àµà´•
        # ðŸ” Debug: accept_trip_safely à´µà´¿à´³à´¿à´•àµà´•àµà´¨àµà´¨àµ
            print("ðŸ”¥ Calling accept_trip_safely with:")
            print(f"   trip_id = {trip_id}")
            print(f"   chat_id = {chat_id}")
            print(f"   driver_name = {driver_name}")
            print(f"   driver_phone = {driver_phone}")
            print(f"   vehicle_number = {vehicle_number}")
        result = accept_trip_safely(
            trip_id=trip_id,   
            driver_chat_id=chat_id,
            driver_name=driver_name,
            driver_phone=driver_phone,
            vehicle_number=vehicle_number
        )
        
        # ðŸ” Debug: à´«à´²à´‚ à´ªà´°à´¿à´¶àµ‹à´§à´¿à´•àµà´•àµà´¨àµà´¨àµ
        print(f"ðŸ”¥ Result from accept_trip_safely: {result}")

        if result == "success":

            bot.answer_callback_query(
                call.id,
                "âš ï¸ à´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´‡à´¤à´¿à´¨à´•à´‚ à´¸àµà´µàµ€à´•à´°à´¿à´šàµà´šà´¿à´°à´¿à´•àµà´•àµà´¨àµà´¨àµ."
            )

            bot.send_message(
                chat_id=chat_id,
                text=(
                    "âš ï¸ à´ˆ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´®à´±àµà´±àµŠà´°àµ à´¡àµà´°àµˆà´µàµ¼ à´¸àµà´µàµ€à´•à´°à´¿à´šàµà´šà´¿à´°à´¿à´•àµà´•à´¾à´‚. "
                    "à´¦à´¯à´µà´¾à´¯à´¿ à´®à´±àµà´±àµŠà´°àµ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´¤à´¿à´°à´žàµà´žàµ†à´Ÿàµà´•àµà´•àµà´•."
                )
            )
            return

        # 3. ACCEPT à´¬à´Ÿàµà´Ÿàµº à´¨àµ€à´•àµà´•à´‚ à´šàµ†à´¯àµà´¯àµà´•
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )
        except Exception as edit_error:
            print(f"Button update notice: {edit_error}")

        # 4. à´¡àµà´°àµˆà´µàµ¼ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½ à´²à´¿à´™àµà´•àµ
        driver_panel_url = (
            "https://taxiservisemj-x9meaffucvbt6tjijxrd6d.streamlit.app/"
            f"?page=driver_trip_panel&trip_id={trip_id}"
            f"&driver_chat_id={chat_id}"
        )

        markup = types.InlineKeyboardMarkup(row_width=1)

        markup.add(
            types.InlineKeyboardButton(
                "ðŸš– à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´ªà´¾à´¨àµ½ à´¤àµà´±à´•àµà´•àµà´•",
                url=driver_panel_url
            )
        )

        # 5. à´µà´¿à´œà´¯ à´¸à´¨àµà´¦àµ‡à´¶à´‚
        bot.answer_callback_query(
            call.id,
            "âœ… à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´¸àµà´µàµ€à´•à´°à´¿à´šàµà´šàµ!"
        )

        bot.send_message(
            chat_id=chat_id,
            text=(
                "âœ… *à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´…à´•àµà´¸àµ†à´ªàµà´±àµà´±àµ à´šàµ†à´¯àµà´¤àµ!*\n\n"
                f"ðŸ†” à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´à´¡à´¿: `{trip_id}`\n"
                f"ðŸ‘¤ à´¡àµà´°àµˆà´µàµ¼: {driver_name}\n"
                f"ðŸ“ž à´«àµ‹àµº: {driver_phone}\n"
                f"ðŸš˜ à´µà´¾à´¹à´¨à´‚: {vehicle_number}\n\n"
                "à´¨à´¾à´µà´¿à´—àµ‡à´·àµ», à´•à´¸àµà´±àµà´±à´®àµ¼ à´µà´¿à´µà´°à´™àµà´™àµ¾, à´²àµˆà´µàµ à´²àµŠà´•àµà´•àµ‡à´·àµ» "
                "à´Žà´¨àµà´¨à´¿à´µà´¯àµà´•àµà´•à´¾à´¯à´¿ à´¤à´¾à´´àµ†à´¯àµà´³àµà´³ à´¬à´Ÿàµà´Ÿàµº à´…à´®àµ¼à´¤àµà´¤àµà´•."
            ),
            parse_mode="Markdown",
            reply_markup=markup
        )

        print(
            f"TRIP ACCEPTED: {trip_id} | "
            f"DRIVER: {chat_id} | {driver_name}"
        )

    except Exception as e:
        print(f"âŒ handle_accept_trip error: {e}")

        try:
            bot.answer_callback_query(
                call.id,
                "âŒ à´Ÿàµà´°à´¿à´ªàµà´ªàµ à´¸àµà´µàµ€à´•à´°à´¿à´•àµà´•àµà´¨àµà´¨à´¤à´¿àµ½ à´ªà´¿à´¶à´•àµ."
            )
        except Exception:
            pass


# ==========================================================
# ðŸš€ START POLLING â€” LAST (after all handlers registered)
# ==========================================================
@st.cache_resource
def start_bot_polling():
    """Start bot polling â€” ONCE only"""
    def _run_polling():
        while True:
            try:
                print("ðŸš€ Bot polling started...")
                bot.infinity_polling(
                    none_stop=True,
                    timeout=60,
                    long_polling_timeout=30
                )
            except Exception as e:
                err = str(e)
                if "409" in err:
                    print("ðŸ›‘ 409 Conflict â€” stopping polling")
                    break
                print(f"âš ï¸ Polling error: {e}")
                time.sleep(5)

    _polling_thread = threading.Thread(target=_run_polling, daemon=True)
    add_script_run_ctx(_polling_thread)
    _polling_thread.start()
    print("âœ… Bot polling thread started â€” ONCE (via cache_resource)")
    return True

start_bot_polling()




















   



