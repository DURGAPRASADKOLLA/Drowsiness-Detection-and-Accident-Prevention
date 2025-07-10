import cv2
import numpy as np
import dlib
from imutils import face_utils
from pygame import mixer
import smtplib
from email.message import EmailMessage
import time
import os
import threading
import tempfile
import requests
from twilio.rest import Client

# === Sound Setup ===
mixer.init()
alert_sound = mixer.Sound('C:/Users/Lenovo/Downloads/mixkit-alert-alarm-1005.wav')
emergency_sound = mixer.Sound('C:/Users/Lenovo/Downloads/loud-emergency-alarm-54635.mp3')

# === Twilio Setup ===
TWILIO_SID = 'AC5fe7e6c378ba64536cbe09b9595f2ace'
TWILIO_AUTH_TOKEN = '2efb3a2bfd96d01267b60811249e6ce4'
TWILIO_PHONE = '+16622658023'
RECIPIENT_NUMBERS = ['+919177812737']
EMAIL_RECIPIENTS = ["dp4485588@gmail.com", "ro200519@rguktong.ac.in"]

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

def get_location_info():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        if res.status_code == 200:
            data = res.json()
            loc = data.get("loc")
            city = data.get("city", "Unknown")
            region = data.get("region", "Unknown")
            country = data.get("country", "Unknown")
            location_name = f"{city}, {region}, {country}"
            if loc:
                gmaps_link = f"https://maps.google.com/?q={loc}"
                return location_name, gmaps_link
    except Exception as e:
        print(f"❌ Location fetch failed: {e}")
    return "Unknown", "Location unavailable"

def send_sms_alert(location_name, location_link):
    try:
        for number in RECIPIENT_NUMBERS:
            body = f"🚨 Drowsiness detected! Location: {location_name}. Map: {location_link}"
            message = twilio_client.messages.create(
                body=body,
                from_=TWILIO_PHONE,
                to=number
            )
            print(f"📩 SMS sent to {number}: SID {message.sid}")
    except Exception as e:
        print(f"❌ SMS send error: {e}")

def make_emergency_call(location_name):
    try:
        for number in RECIPIENT_NUMBERS:
            twiml = f'<Response><Say voice="alice">Emergency! Your friend might be in danger. Their last known location is {location_name}. Check your email.</Say></Response>'
            call = twilio_client.calls.create(
                twiml=twiml,
                from_=TWILIO_PHONE,
                to=number
            )
            print(f"📞 Call placed to {number}: SID {call.sid}")
    except Exception as e:
        print(f"❌ Call error: {e}")

def send_emergency_email(video_path, location_name, location_link):
    try:
        msg = EmailMessage()
        msg.set_content(
            f"🚨 Emergency! Eyes closed too long.\n\n"
            f"📍 Location: {location_name}\n"
            f"🌐 Map: {location_link}\n\n"
            f"Check the attached video for more details."
        )
        msg['Subject'] = "Emergency Drowsiness Alert"
        msg['From'] = "durgaprasadkolla519@gmail.com"
        msg['To'] = ', '.join(EMAIL_RECIPIENTS)

        with open(video_path, 'rb') as f:
            msg.add_attachment(f.read(), maintype='video', subtype='mp4', filename='drowsiness_clip.mp4')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("durgaprasadkolla519@gmail.com", "enni vrhc gsfy ctkw")
            smtp.send_message(msg)

        print(f"✅ Email sent with video to: {', '.join(EMAIL_RECIPIENTS)}")
    except Exception as e:
        print("❌ Failed to send email:", e)

# === Main Loop Logic ===
FRAME_RATE = 20
BUFFER_SIZE = FRAME_RATE * 6
video_buffer = []

cap = cv2.VideoCapture(0)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("C:/Users/Lenovo/Downloads/archive (1)/shape_predictor_68_face_landmarks.dat")

sleep = drowsy = active = 0
status = ""
color = (0, 0, 0)
closed_start_time = None
emergency_triggered = False
alert_triggered = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    video_buffer.append(frame.copy())
    if len(video_buffer) > BUFFER_SIZE:
        video_buffer.pop(0)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        x1, y1 = face.left(), face.top()
        x2, y2 = face.right(), face.bottom()
        face_frame = frame.copy()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        def compute(ptA, ptB):
            return np.linalg.norm(ptA - ptB)

        def blinked(a, b, c, d, e, f):
            up = compute(b, d) + compute(c, e)
            down = compute(a, f)
            ratio = up / (2.0 * down)
            if ratio > 0.25:
                return 2
            elif 0.21 < ratio <= 0.25:
                return 1
            else:
                return 0

        left_blink = blinked(landmarks[36], landmarks[37], landmarks[38],
                             landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43], landmarks[44],
                              landmarks[47], landmarks[46], landmarks[45])

        eye_closed = (left_blink == 0 or right_blink == 0)
        current_time = time.time()

        if eye_closed:
            if closed_start_time is None:
                closed_start_time = current_time
                alert_triggered = False
                emergency_triggered = False

            sleep_duration = current_time - closed_start_time

            if 3 <= sleep_duration < 10 and not alert_triggered:
                status = "SLEEPING !!!!!"
                color = (255, 0, 0)
                alert_sound.play()
                alert_triggered = True

            elif 10 <= sleep_duration and not emergency_triggered:
                status = "EMERGENCY !!!"
                color = (0, 0, 255)
                emergency_sound.play()

                print("⚠️ Emergency detected. Sending alerts...")

                location_name, location_link = get_location_info()

                video_filename = os.path.join(tempfile.gettempdir(), "drowsiness_clip.mp4")
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                height, width, _ = video_buffer[0].shape
                out = cv2.VideoWriter(video_filename, fourcc, FRAME_RATE, (width, height))
                for frame_in_buffer in video_buffer:
                    out.write(frame_in_buffer)
                out.release()

                threading.Thread(target=send_emergency_email, args=(video_filename, location_name, location_link)).start()
                threading.Thread(target=send_sms_alert, args=(location_name, location_link)).start()
                threading.Thread(target=make_emergency_call, args=(location_name,)).start()

                emergency_triggered = True

            elif sleep_duration < 3:
                status = "SLEEPING"
                color = (100, 0, 0)

            sleep += 1
            drowsy = 0
            active = 0

        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            closed_start_time = None
            emergency_triggered = False
            alert_triggered = False
            if drowsy > 6:
                status = "Drowsy !"
                color = (0, 0, 255)
        else:
            drowsy = 0
            sleep = 0
            active += 1
            closed_start_time = None
            emergency_triggered = False
            alert_triggered = False
            emergency_sound.stop()
            if active > 6:
                status = "Active :)"
                color = (0, 255, 0)

        cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 0, 0), -1)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('b'):
        alert_sound.stop()
        emergency_sound.stop()
        break

cap.release()
cv2.destroyAllWindows()
