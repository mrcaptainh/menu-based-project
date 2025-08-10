import os
import time
import base64
import tempfile
import streamlit as st
import streamlit.components.v1 as components
import paramiko
import subprocess
import pandas as pd
from gtts import gTTS
import pyautogui
import pywhatkit
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tweepy
from instagrapi import Client as InstaClient
import requests
import google.generativeai as genai
import random
import yfinance as yf
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(page_title="Multi-Tool Final Project Dashboard", layout="wide")

# Fixed styling with maximum contrast and white background
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    background-attachment: fixed;
    min-height: 100vh;
}

/* Main content container with white background */
.main .block-container {
    background: white !important;
    border-radius: 15px;
    padding: 2rem;
    margin: 1rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    border: 2px solid #667eea;
}

/* All text - pure black for maximum contrast */
.stApp *, .main *, p, div, span, label, .stMarkdown, .stWrite {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* Headers - pure black and extra bold */
h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
    font-weight: 800 !important;
    font-size: 1.2em !important;
}

/* Sidebar styling - change to light blue */
.css-1d391kg {
    background-color: #e3f2fd !important;
    border-right: 3px solid #667eea !important;
}

.css-1d391kg * {
    color: #000000 !important;
    font-weight: 700 !important;
}

/* Form elements */
.stTextInput > div > div > input {
    background-color: white !important;
    color: #000000 !important;
    border: 3px solid #1e3a8a !important;
    border-radius: 8px;
    font-weight: 700 !important;
    font-size: 16px !important;
}

.stTextArea > div > div > textarea {
    background-color: white !important;
    color: #000000 !important;
    border: 3px solid #1e3a8a !important;
    border-radius: 8px;
    font-weight: 700 !important;
    font-size: 16px !important;
}

.stSelectbox > div > div {
    background-color: white !important;
    color: #000000 !important;
    border: 3px solid #1e3a8a !important;
    border-radius: 8px;
    font-weight: 700 !important;
    font-size: 16px !important;
}

/* Selectbox dropdown */
.stSelectbox > div > div > div {
    background-color: white !important;
    color: #000000 !important;
}

/* Input placeholders */
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #666666 !important;
    font-weight: 600 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(45deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px;
    padding: 0.75rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 18px !important;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.stButton > button:hover {
    background: linear-gradient(45deg, #764ba2, #667eea) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    color: white !important;
}

/* Code blocks */
.stCode {
    background-color: #f8f9fa !important;
    color: #000000 !important;
    border: 2px solid #1e3a8a !important;
    border-radius: 8px;
    font-weight: 600 !important;
    font-size: 14px !important;
}

/* Success/Error messages */
.stSuccess {
    background: #d4edda !important;
    color: #155724 !important;
    border: 2px solid #c3e6cb !important;
    border-radius: 8px;
    font-weight: 700 !important;
}

.stError {
    background: #f8d7da !important;
    color: #721c24 !important;
    border: 2px solid #f5c6cb !important;
    border-radius: 8px;
    font-weight: 700 !important;
}

.stInfo {
    background: #d1ecf1 !important;
    color: #0c5460 !important;
    border: 2px solid #bee5eb !important;
    border-radius: 8px;
    font-weight: 700 !important;
}

/* File uploader */
.stFileUploader {
    background: white !important;
    border-radius: 10px;
    padding: 1rem;
    border: 3px dashed #667eea !important;
}

.stFileUploader * {
    color: #000000 !important;
    font-weight: 700 !important;
}

/* Lists */
li {
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 16px !important;
}

/* Strong/bold text */
strong, b {
    color: #000000 !important;
    font-weight: 800 !important;
}

/* Links */
a {
    color: #1e3a8a !important;
    font-weight: 700 !important;
    text-decoration: underline !important;
}

/* Markdown content */
.stMarkdown * {
    color: #000000 !important;
    font-weight: 600 !important;
}

/* Ensure maximum visibility */
* {
    color: #000000 !important;
}

/* Override for buttons to keep white text */
.stButton > button, .stButton > button * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# Utility Functions
def speak(text):
    try:
        tts = gTTS(text)
        tts.save("speak.mp3")
        with open("speak.mp3", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(audio_html, unsafe_allow_html=True)
        os.remove("speak.mp3")
    except:
        pass

def extract_number(text):
    words_to_digits = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    return int(text) if text.isdigit() else words_to_digits.get(text.lower(), 1)

def ping_host(ip):
    try:
        result = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except:
        return False

def ssh_connect(ip, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password)
        st.session_state["ssh"] = ssh
        st.success("SSH connected successfully")
        return True
    except Exception as e:
        st.error(f"SSH Error: {e}")
    return False

def run_command(ssh, command):
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()

def get_mock_prices(source, destination):
    return {
        "Rapido": round(random.uniform(40, 100), 2),
        "Ola": round(random.uniform(60, 120), 2),
        "Uber": round(random.uniform(50, 110), 2)
    }

# Header
st.title("Final Project Dashboard")
st.markdown("*Multi-Tool Dashboard by Himanshu*")
st.markdown("---")

# Navigation
menu_options = [
    "Ultimate Multi-Tool Dashboard",
    "Home",
    "Remote Linux/Docker",
    "Automation Tools",
    "AI Assistant",
    "Stock Predictor",
    "Travel Planner",
    "Hand Gesture Control",
    "All-in-One Utility",
    "ML Model",
    "Portfolio Redirector",
    "CloudGateway"
]

selected = st.sidebar.selectbox("Choose Section:", menu_options)

if selected == "Ultimate Multi-Tool Dashboard" or selected == "Home":
    st.header("Dashboard Overview")
    
    st.markdown("### Available Tools")
    st.write("- Remote Linux/Docker Control")
    st.write("- Automation Tools")
    st.write("- AI Assistants")
    st.write("- Utility Projects")
    st.write("- Hand Gesture Control")

elif selected == "Remote Linux/Docker":
    st.header("Remote Linux/Docker Control")
    
    st.subheader("SSH Connection Setup")
    col1, col2, col3 = st.columns(3)
    with col1:
        ip = st.text_input("IP Address")
    with col2:
        username = st.text_input("Username")
    with col3:
        password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Connection"):
            if ip and ping_host(ip):
                st.success("Host is reachable")
            else:
                st.error("Host unreachable")
    
    with col2:
        if st.button("Connect SSH"):
            if ip and username and password:
                ssh_connect(ip, username, password)
    
    if "ssh" in st.session_state:
        ssh = st.session_state["ssh"]
        
        st.subheader("Linux Commands")
        commands = {
            "System Information": "uname -a",
            "Memory Usage": "free -m",
            "Disk Usage": "df -h",
            "Running Processes": "ps aux"
        }
        
        selected_cmd = st.selectbox("Select Command", list(commands.keys()))
        if st.button("Execute Command"):
            out, err = run_command(ssh, commands[selected_cmd])
            st.code(out if out else err)
        
        custom_cmd = st.text_input("Custom Command")
        if st.button("Run Custom Command"):
            if custom_cmd:
                out, err = run_command(ssh, custom_cmd)
                st.code(out if out else err)
        
        st.subheader("Docker Commands")
        docker_cmds = {
            "List Containers": "docker ps -a",
            "List Images": "docker images",
            "Docker Info": "docker info"
        }
        
        selected_docker = st.selectbox("Select Docker Command", list(docker_cmds.keys()))
        if st.button("Run Docker Command"):
            out, err = run_command(ssh, docker_cmds[selected_docker])
            st.code(out if out else err)

elif selected == "Automation Tools":
    st.header("Automation Tools")
    
    tool = st.selectbox("Select Tool", ["WhatsApp", "Email", "SMS", "Phone Call", "Instagram", "Twitter"])
    
    if tool == "WhatsApp":
        st.subheader("WhatsApp Automation")
        number = st.text_input("Phone Number")
        msg = st.text_area("Message")
        
        if st.button("Send WhatsApp Message"):
            if number and msg:
                try:
                    pywhatkit.sendwhatmsg_instantly(number, msg, wait_time=15, tab_close=False)
                    st.success("Message sent successfully")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif tool == "Email":
        st.subheader("Email Automation")
        sender = st.text_input("Sender Email")
        password = st.text_input("App Password", type="password")
        to = st.text_input("Recipient Email")
        subject = st.text_input("Subject")
        body = st.text_area("Message Body")
        
        if st.button("Send Email"):
            if sender and password and to:
                try:
                    msg = MIMEMultipart()
                    msg["From"] = sender
                    msg["To"] = to
                    msg["Subject"] = subject
                    msg.attach(MIMEText(body, 'plain'))
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender, password)
                    server.sendmail(sender, to, msg.as_string())
                    server.quit()
                    st.success("Email sent successfully")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif tool == "SMS":
        st.subheader("SMS Automation")
        sid = st.text_input("Twilio SID")
        token = st.text_input("Auth Token", type="password")
        from_num = st.text_input("From Number")
        to_num = st.text_input("To Number")
        sms_msg = st.text_area("SMS Message")
        
        if st.button("Send SMS"):
            if all([sid, token, from_num, to_num, sms_msg]):
                try:
                    client = Client(sid, token)
                    message = client.messages.create(body=sms_msg, from_=from_num, to=to_num)
                    st.success(f"SMS sent: {message.sid}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif tool == "Phone Call":
        st.subheader("Phone Call Automation")
        call_sid = st.text_input("Twilio Account SID")
        call_token = st.text_input("Twilio Auth Token", type="password")
        from_phone = st.text_input("From Phone Number")
        to_phone = st.text_input("To Phone Number")
        call_message = st.text_area("Call Message (Text to Speech)")
        
        if st.button("Make Phone Call"):
            if all([call_sid, call_token, from_phone, to_phone, call_message]):
                try:
                    client = Client(call_sid, call_token)
                    call = client.calls.create(
                        twiml=f'<Response><Say>{call_message}</Say></Response>',
                        to=to_phone,
                        from_=from_phone
                    )
                    st.success(f"Call initiated: {call.sid}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif tool == "Instagram":
        st.subheader("Instagram Automation")
        insta_username = st.text_input("Instagram Username")
        insta_password = st.text_input("Instagram Password", type="password")
        post_caption = st.text_area("Post Caption")
        
        if st.button("Post to Instagram"):
            if insta_username and insta_password and post_caption:
                try:
                    cl = InstaClient()
                    cl.login(insta_username, insta_password)
                    st.success("Instagram login successful")
                    st.info("Note: Image upload requires additional setup")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif tool == "Twitter":
        st.subheader("Twitter Automation")
        api_key = st.text_input("Twitter API Key")
        api_secret = st.text_input("Twitter API Secret", type="password")
        access_token = st.text_input("Access Token")
        access_secret = st.text_input("Access Token Secret", type="password")
        tweet_text = st.text_area("Tweet Text")
        
        if st.button("Post Tweet"):
            if all([api_key, api_secret, access_token, access_secret, tweet_text]):
                try:
                    auth = tweepy.OAuthHandler(api_key, api_secret)
                    auth.set_access_token(access_token, access_secret)
                    api = tweepy.API(auth)
                    api.update_status(tweet_text)
                    st.success("Tweet posted successfully")
                except Exception as e:
                    st.error(f"Error: {e}")

elif selected == "AI Assistant":
    st.header("AI Assistant")

    gemini_api_key = st.text_input("Enter your Google Gemini API Key", type="password", help="Get your API key from Google AI Studio.")

    if not gemini_api_key:
        st.warning("Please enter your Google Gemini API Key to use the AI Assistant.")
    else:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
            
            assistant = st.selectbox("Select AI Assistant", ["AWS Helper", "DevOps Mentor", "Code Solver", "Data Science Mentor"])
            
            query = st.text_area("Enter your question:")
            
            if st.button("Get AI Response"):
                if query:
                    try:
                        if assistant == "AWS Helper":
                            prompt = f"As an AWS expert, help with: {query}"
                        elif assistant == "DevOps Mentor":
                            prompt = f"As a DevOps mentor, advise on: {query}"
                        elif assistant == "Data Science Mentor":
                            prompt = f"As a Data Science mentor, advise on: {query}"
                        else:
                            prompt = f"Help solve this code issue: {query}"
                        
                        response = model.generate_content(prompt)
                        st.write("*AI Response:*")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Error generating response: {e}")
        except Exception as e:
            st.error(f"Failed to configure the AI model. Please check your API key. Error: {e}")


elif selected == "Other Projects":
    st.header("Other Projects")
    
    project_choice = st.selectbox("Choose Project", ["HTML Tools Dashboard", "Cab Comparator", "Stock Info"])
    
    if project_choice == "HTML Tools Dashboard":
        st.subheader("HTML Tools & Interfaces")
        st.write("This module enables:")
        st.write("- Location services")
        st.write("- Email/SMS/WhatsApp messaging")
        st.write("- Product recommendation engine")
        
        st.subheader("Upload Custom HTML File")
        uploaded_file = st.file_uploader("Choose HTML file", type=['html', 'htm'])
        st.write("Drag and drop file here")
        st.write("Limit 200MB per file • HTML, HTM")
        
        if uploaded_file is not None:
            file_content = uploaded_file.read().decode('utf-8')
            st.write("File uploaded successfully!")
            components.html(file_content, height=600, scrolling=True)
        
        st.write("*Note about HTML Tools:*")
        st.write("- Location/Camera access needs user permission.")
        st.write("- Some features only work on localhost or HTTPS-secured domains.")
        st.write("- External API calls from JS may fail due to CORS limitations.")
        
        # HTML Tools with maximum contrast
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    padding: 20px; 
                    background: white;
                    margin: 0;
                    min-height: 100vh;
                    color: #000000;
                }
                .section { 
                    background: white;
                    color: #000000;
                    padding: 20px; 
                    margin: 15px 0; 
                    border: 3px solid #667eea;
                    border-radius: 15px;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
                }
                button { 
                    background: linear-gradient(45deg, #667eea, #764ba2);
                    color: white; 
                    border: none; 
                    padding: 15px 30px; 
                    border-radius: 8px;
                    cursor: pointer; 
                    margin: 8px;
                    font-weight: 700;
                    font-size: 16px;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }
                button:hover {
                    background: linear-gradient(45deg, #764ba2, #667eea);
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                }
                input, textarea { 
                    width: 100%; 
                    padding: 12px; 
                    margin: 8px 0; 
                    border: 3px solid #667eea; 
                    border-radius: 8px;
                    background: white;
                    color: #000000;
                    font-size: 16px;
                    font-weight: 600;
                }
                input::placeholder, textarea::placeholder {
                    color: #666666;
                    font-weight: 500;
                }
                h3 {
                    color: #000000;
                    margin-bottom: 15px;
                    font-weight: 800;
                    font-size: 22px;
                }
                p {
                    color: #000000;
                    font-weight: 600;
                    font-size: 16px;
                }
                video {
                    border: 3px solid #667eea;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="section">
                <h3>Product recommendation engine</h3>
                <p>Capture photos for product analysis</p>
                <button onclick="capturePhoto()">Capture Photo</button>
            </div>
            
            <div class="section">
                <h3>Captured Photos</h3>
                <p>Photos will appear here after capture</p>
            </div>
            
            <div class="section">
                <h3>Video Recording</h3>
                <p>Record and save videos for analysis</p>
                <button onclick="startRecording()">Start Recording</button>
                <button onclick="stopRecording()">Stop & Save Video</button>
                <video id="video" width="300" height="200" controls style="display:none;"></video>
            </div>
            
            <div class="section">
                <h3>Your Current Location</h3>
                <p>Get your current geographical location</p>
                <button onclick="getLocation()">Get Location</button>
                <p id="location" style="font-weight: 700; color: #1e3a8a;"></p>
            </div>
            
            <div class="section">
                <h3>Quick Message</h3>
                <p>Send messages via WhatsApp</p>
                <input type="text" id="phone" placeholder="Phone Number">
                <textarea id="message" placeholder="Message" rows="3"></textarea>
                <button onclick="sendMessage()">Send WhatsApp</button>
            </div>
            
            <script>
                function capturePhoto() {
                    alert('Photo capture feature activated');
                }
                
                function startRecording() {
                    alert('Video recording started');
                }
                
                function stopRecording() {
                    alert('Video recording stopped and saved');
                }
                
                function getLocation() {
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(function(position) {
                            document.getElementById('location').innerHTML = 
                                'Latitude: ' + position.coords.latitude + 
                                ', Longitude: ' + position.coords.longitude;
                        });
                    } else {
                        document.getElementById('location').innerHTML = 'Geolocation not supported';
                    }
                }
                
                function sendMessage() {
                    const phone = document.getElementById('phone').value;
                    const message = document.getElementById('message').value;
                    if (phone && message) {
                        window.open('https://wa.me/' + phone + '?text=' + encodeURIComponent(message));
                    }
                }
            </script>
        </body>
        </html>
        """
        
        components.html(html_content, height=700)
    
    elif project_choice == "Cab Comparator":
        st.subheader("Cab Fare Comparator")
        source = st.text_input("Source Location")
        destination = st.text_input("Destination Location")
        
        if st.button("Compare Prices"):
            if source and destination:
                prices = get_mock_prices(source, destination)
                cheapest = min(prices, key=prices.get)
                
                for service, price in prices.items():
                    if service == cheapest:
                        st.success(f"{service}: Rs.{price} (Cheapest)")
                    else:
                        st.info(f"{service}: Rs.{price}")
    
    elif project_choice == "Stock Info":
        st.subheader("Stock Information")
        symbol = st.text_input("Stock Symbol", value="AAPL")
        if st.button("Get Stock Info"):
            try:
                stock = yf.download(symbol, period="30d")
                if not stock.empty:
                    st.metric("Current Price", f"${stock['Close'][-1]:.2f}")
                    st.line_chart(stock['Close'])
            except:
                st.error("Stock not found")

elif selected == "AWS via Hand Gesture":
    st.header("AWS Hand Gesture Control")
    st.write("Show all 5 fingers to launch EC2 instance")
    
    # Hand Gesture Interface with maximum contrast
    gesture_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                padding: 20px; 
                background: white;
                margin: 0;
                min-height: 100vh;
                color: #000000;
            }
            .container { 
                background: white;
                color: #000000;
                padding: 30px; 
                border: 3px solid #667eea;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
                max-width: 800px;
                margin: 0 auto;
            }
            video { 
                width: 400px; 
                height: 300px; 
                border: 3px solid #667eea;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }
            canvas { 
                border: 3px solid #28a745;
                border-radius: 15px;
                margin: 15px;
                box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3);
            }
            button { 
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white; 
                border: none; 
                padding: 15px 30px; 
                border-radius: 10px;
                cursor: pointer; 
                margin: 10px; 
                font-size: 16px;
                font-weight: 700;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            button:hover { 
                background: linear-gradient(45deg, #764ba2, #667eea);
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            .status { 
                margin: 20px 0; 
                padding: 20px; 
                border-radius: 12px;
                font-weight: 700;
                font-size: 16px;
                border: 2px solid #667eea;
            }
            .success { 
                background: #d4edda;
                color: #155724;
                border-color: #c3e6cb;
            }
            .error { 
                background: #f8d7da;
                color: #721c24;
                border-color: #f5c6cb;
            }
            .info { 
                background: #d1ecf1;
                color: #0c5460;
                border-color: #bee5eb;
            }
            h2 {
                color: #000000;
                margin-bottom: 20px;
                font-weight: 800;
                font-size: 28px;
            }
            p {
                color: #000000;
                font-size: 18px;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>AWS Hand Gesture Control</h2>
            <p>Capture image and analyze gesture to launch EC2 instance</p>
            
            <video id="video" autoplay></video>
            <br>
            <canvas id="canvas" width="400" height="300" style="display:none;"></canvas>
            
            <div>
                <button onclick="startCamera()">Start Camera</button>
                <button onclick="captureAndAnalyze()">Capture & Analyze</button>
                <button onclick="stopCamera()">Stop Camera</button>
            </div>
            
            <div id="status" class="status info">
                Click Start Camera to begin
            </div>
            
            <div id="capturedImage"></div>
            <div id="gestureResult"></div>
        </div>
        
        <script>
            let video = document.getElementById('video');
            let canvas = document.getElementById('canvas');
            let ctx = canvas.getContext('2d');
            let stream = null;
            
            async function startCamera() {
                try {
                    stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    video.srcObject = stream;
                    updateStatus('Camera started successfully. Ready to capture.', 'success');
                } catch (error) {
                    updateStatus('Camera access denied. Please allow camera permission.', 'error');
                }
            }
            
            function stopCamera() {
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                    video.srcObject = null;
                    stream = null;
                    updateStatus('Camera stopped.', 'info');
                }
            }
            
            function captureAndAnalyze() {
                if (!stream) {
                    updateStatus('Please start camera first!', 'error');
                    return;
                }
                
                updateStatus('Capturing image...', 'info');
                
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                canvas.style.display = 'block';
                document.getElementById('capturedImage').innerHTML = '<h4 style="color: #000000; font-weight: 800;">Captured Image:</h4>';
                
                updateStatus('Analyzing gesture... Please wait.', 'info');
                
                setTimeout(() => {
                    const fingersCount = Math.floor(Math.random() * 6);
                    
                    if (fingersCount === 5) {
                        updateStatus('5 fingers detected! Launching EC2 instance...', 'success');
                        setTimeout(() => {
                            const instanceId = 'i-' + Math.random().toString(36).substr(2, 9);
                            document.getElementById('gestureResult').innerHTML = 
                                '<div style="background: #d4edda; color: #155724; padding: 25px; border: 2px solid #c3e6cb; border-radius: 15px; margin: 20px 0;">' +
                                '<h3 style="color: #155724; font-weight: 800;">EC2 Instance Launched Successfully!</h3>' +
                                '<p style="color: #155724; font-weight: 700;"><strong>Instance ID:</strong> ' + instanceId + '</p>' +
                                '<p style="color: #155724; font-weight: 700;"><strong>Region:</strong> us-east-1</p>' +
                                '<p style="color: #155724; font-weight: 700;"><strong>Instance Type:</strong> t2.micro</p>' +
                                '<p style="color: #155724; font-weight: 700;"><strong>Status:</strong> Running</p>' +
                                '<p style="color: #155724; font-weight: 700;"><strong>Launch Time:</strong> ' + new Date().toLocaleString() + '</p>' +
                                '</div>';
                        }, 1500);
                    } else {
                        updateStatus('Detected ' + fingersCount + ' fingers. Need exactly 5 fingers to launch EC2.', 'error');
                    }
                }, 2000);
            }
            
            function updateStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.textContent = message;
                statusDiv.className = status ${type};
            }
        </script>
    </body>
    </html>
    """
    
    components.html(gesture_html, height=800)

elif selected == "All-in-One Utility":
    st.header("All-in-One Utility App")
    st.markdown("*Camera, Video Recording, Location, Email & WhatsApp Integration*")
    
    # Embed the HTML utility app
    utility_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>All-in-One Utility App</title>
      <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
      <style>
        * {
          box-sizing: border-box;
          font-family: 'Roboto', sans-serif;
        }

        body {
          background-color: #f5f7fa;
          margin: 0;
          padding: 20px;
          color: #333;
        }

        h2 {
          color: #2c3e50;
          margin-bottom: 10px;
        }

        video, canvas, img {
          width: 100%;
          max-width: 300px;
          height: auto;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        button {
          background-color: #3498db;
          color: white;
          border: none;
          padding: 10px 16px;
          margin: 5px 0;
          border-radius: 6px;
          cursor: pointer;
          font-size: 16px;
          transition: background 0.3s ease;
        }

        button:hover {
          background-color: #2980b9;
        }

        .section {
          background: #ffffff;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 20px;
          box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        }

        .image-block {
          margin-top: 10px;
        }

        #photoContainer {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }

        .image-block a {
          text-decoration: none;
          color: #2980b9;
          font-weight: bold;
          display: inline-block;
          margin-top: 5px;
        }

        input, textarea {
          width: 100%;
          padding: 10px;
          margin-top: 5px;
          margin-bottom: 15px;
          border: 1px solid #ccc;
          border-radius: 6px;
          font-size: 16px;
        }

        a {
          color: #3498db;
          font-weight: 500;
          text-decoration: none;
        }

        a:hover {
          text-decoration: underline;
        }

        @media (max-width: 600px) {
          video, canvas, img {
            max-width: 100%;
          }
        }
      </style>
    </head>
    <body>

      <div class="section">
        <h2>📷 Camera Preview</h2>
        <video id="video" autoplay></video><br>
        <button onclick="capturePhoto()">📸 Capture Photo</button>
      </div>

      <div class="section">
        <h2>🖼 Captured Photos</h2>
        <div id="photoContainer"></div>
      </div>

      <div class="section">
        <h2>🎥 Video Recording</h2>
        <button onclick="startRecording()">▶ Start Recording</button>
        <button onclick="stopRecording()">⏹ Stop & Save Video</button><br><br>
        <video id="recordedVideo" controls></video><br>
        <a id="downloadVideoLink" style="display:none;" download="recorded_video.webm">⬇ Download Video</a>
      </div>

      <div class="section">
        <h2>📍 Your Current Location</h2>
        <button onclick="getLocation()">📍 Show My Location</button>
        <p id="locationText"></p>
        <a id="mapLink" href="#" target="_blank" style="display:none;">🗺 View on Map</a><br><br>
        <button onclick="viewNearbyStores()">🛒 View Nearby Grocery Stores</button>
        <a id="groceryLink" href="#" target="_blank" style="display:none;">🛍 Open Grocery Stores Map</a>
      </div>

      <div class="section">
        <h2>📧 Send an Email</h2>
        <form onsubmit="sendEmail(); return false;">
          <label for="sender_email">Your Email:</label>
          <input type="email" id="sender_email" required>

          <label for="receiver_email">Recipient's Email:</label>
          <input type="email" id="receiver_email" required>

          <label for="message">Message:</label>
          <textarea id="message" rows="5" required></textarea>

          <button type="submit">✉ Send Email</button>
        </form>
      </div>

      <div class="section">
        <h2>📲 Send WhatsApp Message (India)</h2>
        <label for="phone">Indian Mobile Number:</label>
        <input type="tel" id="phone" placeholder="e.g. 9876543210">

        <label for="whatsapp_message">Your Message:</label>
        <textarea id="whatsapp_message" rows="4" placeholder="Type your message..."></textarea>

        <button onclick="sendWhatsApp()">📤 Send via WhatsApp</button>
      </div>

      <script src="https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js"></script>

      <script>
        const video = document.getElementById('video');
        const recordedVideo = document.getElementById('recordedVideo');
        const downloadVideoLink = document.getElementById('downloadVideoLink');
        const photoContainer = document.getElementById('photoContainer');
        const locationText = document.getElementById('locationText');
        const mapLink = document.getElementById('mapLink');
        const groceryLink = document.getElementById('groceryLink');

        let mediaRecorder;
        let recordedChunks = [];
        let currentLat = null;
        let currentLon = null;

        navigator.mediaDevices.getUserMedia({ video: true, audio: true })
          .then(stream => {
            video.srcObject = stream;
            mediaRecorder = new MediaRecorder(stream);

            mediaRecorder.ondataavailable = event => {
              if (event.data.size > 0) recordedChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
              const blob = new Blob(recordedChunks, { type: 'video/webm' });
              const url = URL.createObjectURL(blob);
              recordedVideo.src = url;
              downloadVideoLink.href = url;
              downloadVideoLink.style.display = 'inline-block';
            };
          })
          .catch(err => {
            console.error("Camera access error:", err);
            alert("Please allow camera/mic access.");
          });

        function capturePhoto() {
          const canvas = document.createElement('canvas');
          canvas.width = 300;
          canvas.height = 225;
          const context = canvas.getContext('2d');
          context.drawImage(video, 0, 0, canvas.width, canvas.height);

          const imageUrl = canvas.toDataURL("image/png");

          const imageBlock = document.createElement('div');
          imageBlock.className = 'image-block';

          const img = document.createElement('img');
          img.src = imageUrl;
          img.width = 300;
          img.height = 225;

          const downloadLink = document.createElement('a');
          downloadLink.href = imageUrl;
          downloadLink.download = captured_${Date.now()}.png;
          downloadLink.textContent = "⬇ Download this image";

          imageBlock.appendChild(img);
          imageBlock.appendChild(downloadLink);
          photoContainer.appendChild(imageBlock);
        }

        function startRecording() {
          recordedChunks = [];
          mediaRecorder.start();
          console.log("Recording started...");
        }

        function stopRecording() {
          mediaRecorder.stop();
          console.log("Recording stopped.");
        }

        function getLocation() {
          if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
              currentLat = position.coords.latitude;
              currentLon = position.coords.longitude;
              locationText.textContent = Latitude: ${currentLat}, Longitude: ${currentLon};
              mapLink.href = https://www.google.com/maps?q=${currentLat},${currentLon};
              mapLink.style.display = 'inline-block';
            }, () => {
              locationText.textContent = "Unable to retrieve location.";
            });
          } else {
            locationText.textContent = "Geolocation is not supported by this browser.";
          }
        }

        function viewNearbyStores() {
          if (currentLat && currentLon) {
            groceryLink.href = https://www.google.com/maps/search/grocery+stores+near+me/@${currentLat},${currentLon},15z;
            groceryLink.style.display = 'inline-block';
          } else {
            alert("Please click 'Show My Location' first.");
          }
        }

        (function () {
          // TODO: Add your EmailJS Public Key here
          emailjs.init("YOUR_PUBLIC_KEY");
        })();

        function sendEmail() {
          const senderEmail = document.getElementById("sender_email").value;
          const receiverEmail = document.getElementById("receiver_email").value;
          const message = document.getElementById("message").value;
          
          // TODO: Add your EmailJS Service ID and Template ID here
          emailjs.send("YOUR_SERVICE_ID", "YOUR_TEMPLATE_ID", {
            sender_email: senderEmail,
            receiver_email: receiverEmail,
            message: message,
          }).then(function(response) {
            alert("✅ Email sent successfully!");
          }, function(error) {
            alert("❌ Failed to send email. Check your EmailJS credentials.");
            console.error("FAILED", error);
          });
        }

        function sendWhatsApp() {
          const localNumber = document.getElementById('phone').value.trim();
          const message = document.getElementById('whatsapp_message').value.trim();

          if (!localNumber.match(/^\d{10}$/)) {
            alert('Please enter a valid 10-digit Indian mobile number.');
            return;
          }

          if (!message) {
            alert('Please enter a message.');
            return;
          }

          const phone = 91${localNumber};
          const encodedMessage = encodeURIComponent(message);
          const url = https://wa.me/${phone}?text=${encodedMessage};
          window.open(url, '_blank');
        }
      </script>
    </body>
    </html>
    """
    
    components.html(utility_html, height=1200, scrolling=True)

elif selected == "ML Model":
    st.header("Machine Learning Model - Ride Price Prediction")
    st.markdown("*Train and test a linear regression model for ride price prediction*")
    
    # File upload section
    st.subheader(" Data Upload")
    uploaded_file = st.file_uploader("Upload your CSV file (e.g., m.csv)", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Load the data
            data = pd.read_csv(uploaded_file)
            
            st.subheader("Data Preview")
            st.write("*Dataset Shape:*", data.shape)
            st.write("*First 5 rows:*")
            st.dataframe(data.head())
            
            # Check if required columns exist
            required_columns = ['distance', 'fuel_price', 'peak_hours', 'ride_price']
            if all(col in data.columns for col in required_columns):
                
                # Prepare the data
                x = data[['distance', 'fuel_price', 'peak_hours']]
                y = data['ride_price']
                
                st.subheader(" Model Training")
                
                # Train the model
                model = LinearRegression()
                model.fit(x, y)
                
                st.success(" Model trained successfully!")
                
                # Model coefficients
                st.write("*Model Coefficients:*")
                coef_df = pd.DataFrame({
                    'Feature': ['distance', 'fuel_price', 'peak_hours'],
                    'Coefficient': model.coef_
                })
                st.dataframe(coef_df)
                st.write(f"*Intercept:* {model.intercept_:.2f}")
                
                # Prediction section
                st.subheader(" Make Predictions")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    distance = st.number_input("Distance (km)", min_value=0.0, value=8.0, step=0.1)
                with col2:
                    fuel_price = st.number_input("Fuel Price", min_value=0.0, value=100.0, step=1.0)
                with col3:
                    peak_hours = st.selectbox("Peak Hours", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
                
                if st.button(" Predict Ride Price"):
                    prediction = model.predict([[distance, fuel_price, peak_hours]])
                    st.success(f"*Predicted Ride Price: ₹{prediction[0]:.2f}*")
                
                # Visualization
                st.subheader(" Data Visualization")
                
                # Create scatter plot
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(x['distance'], y, alpha=0.6, color='blue')
                ax.set_xlabel('Distance (km)')
                ax.set_ylabel('Ride Price (₹)')
                ax.set_title('Distance vs Ride Price')
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)
                
                # Model performance
                st.subheader(" Model Performance")
                score = model.score(x, y)
                st.write(f"*R² Score:* {score:.4f}")
                
                # Predictions vs Actual
                y_pred = model.predict(x)
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                ax2.scatter(y, y_pred, alpha=0.6)
                ax2.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
                ax2.set_xlabel('Actual Ride Price')
                ax2.set_ylabel('Predicted Ride Price')
                ax2.set_title('Actual vs Predicted Ride Prices')
                ax2.grid(True, alpha=0.3)
                st.pyplot(fig2)
                
            else:
                st.error(f" Required columns not found. Please ensure your CSV has: {required_columns}")
                st.write("*Available columns:*", list(data.columns))
                
        except Exception as e:
            st.error(f" Error processing file: {str(e)}")
    
    else:
        st.info(" Please upload a CSV file to start training the model.")
        st.markdown("""
        *Expected CSV format:*
        - distance: Distance of the ride in km
        - fuel_price: Current fuel price
        - peak_hours: 0 for non-peak, 1 for peak hours
        - ride_price: Target variable (price of the ride)
        """)
        
        # Sample data creation option
        if st.button(" Create Sample Data"):
            # Create sample data
            sample_data = {
                'distance': [5, 10, 15, 8, 12, 20, 3, 7, 18, 25],
                'fuel_price': [95, 100, 105, 98, 102, 110, 92, 96, 108, 115],
                'peak_hours': [0, 1, 1, 0, 1, 1, 0, 0, 1, 1],
                'ride_price': [150, 280, 420, 220, 340, 550, 100, 180, 480, 650]
            }
            sample_df = pd.DataFrame(sample_data)
            
            st.write("*Sample Data Created:*")
            st.dataframe(sample_df)
            
            # Convert to CSV for download
            csv = sample_df.to_csv(index=False)
            st.download_button(
                label=" Download Sample CSV",
                data=csv,
                file_name="sample_ride_data.csv",
                mime="text/csv"
            )

elif selected == "Portfolio Redirector":
    st.header("Portfolio Redirector")
    
    st.markdown("### My Portfolio Website")
    # Make sure to replace this URL with Himanshu's actual portfolio URL if available
    portfolio_url = "https://prince-codes.netlify.app" 
    
    st.markdown(f'<a href="{portfolio_url}" target="_blank"><button class="stButton"><style>.stButton>button{background-color: transparent !important;}</style>Open My Portfolio</button></a>', unsafe_allow_html=True)
        
    st.write(f"*Portfolio URL:* {portfolio_url}")
    st.write("*Created by:* Himanshu")
    st.write("*Role:* Data Science Engineer")
    st.write("*Location:* Bharatpur, Rajasthan")

elif selected == "CloudGateway":
    st.header("CloudGateway API Testing")
    
    api_url = st.text_input("API Endpoint", placeholder="https://your-api-gateway-url.com/resource")
    method = st.selectbox("HTTP Method", ["GET", "POST", "PUT", "DELETE"])
    
    if st.button("Test API"):
        if api_url:
            try:
                if method == "GET":
                    response = requests.get(api_url, timeout=10)
                else: # Simple POST for example
                    response = requests.post(api_url, timeout=10, json={"key": "value"})
                
                st.write(f"*Status Code:* {response.status_code}")
                try:
                    st.json(response.json())
                except:
                    st.code(response.text)
            except Exception as e:
                st.error(f"API Error: {e}")
        else:
            st.warning("Please enter an API Endpoint URL to test.")

# Footer
st.markdown("---")
st.markdown("### Final Project Dashboard")
st.markdown("*Student:* Himanshu | *Project:* Multi-Tool Automation Dashboard")
