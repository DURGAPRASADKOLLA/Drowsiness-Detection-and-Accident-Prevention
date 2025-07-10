# Drowsiness-Detection-and-Accident-Prevention
# Drowsiness Detection and Accident Prevention

This project is a real-time drowsiness detection system built using Python, OpenCV, and Deep Learning techniques. It uses a webcam feed to monitor the user's eyes and alerts the user if signs of drowsiness are detected, aiming to help prevent accidents due to fatigue.

## 🚀 Features

- Real-time face and eye detection
- Eye aspect ratio (EAR) calculation using facial landmarks
- Drowsiness alert system (sound alarm)
- Simple and intuitive webcam-based interface
- Uses **dlib**, **OpenCV**, and **scipy** for accurate detection

## 🧠 How It Works

1. Facial landmarks are detected using a pre-trained shape predictor from dlib.
2. The **Eye Aspect Ratio (EAR)** is calculated to monitor if the eyes are closing.
3. If the EAR falls below a threshold for a certain number of frames, an alarm is triggered to alert the user.

## 🛠️ Technologies Used

- Python 3.x
- OpenCV
- dlib
- imutils
- scipy
- playsound

## 📁 File Structure

```
├── Drowsiness-detection-and-accident-prevention.ipynb  # Jupyter Notebook with full implementation
├── shape_predictor_68_face_landmarks.dat              # Pre-trained model for facial landmarks (needs to be downloaded)
```

## ⚙️ Installation

1. Clone the repository or download the notebook.

2. Install the required dependencies:

```bash
pip install opencv-python dlib imutils scipy playsound
```

3. Download the shape predictor model from [dlib's official website](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2), extract it, and place the `.dat` file in your project directory.

## ▶️ Usage

Run the notebook or convert it to a Python script. Ensure your webcam is enabled.

```bash
python drowsiness_detection.py
```

> **Note:** You can extract code from the notebook and save it as a `.py` script if needed.

## 📊 EAR Thresholds

- **EAR Threshold:** ~0.25
- **Frames Threshold:** ~20 consecutive frames

These values can be fine-tuned based on testing for better sensitivity and accuracy.

## 🔔 Alert System

A beep or alarm sound is played using the `playsound` module when drowsiness is detected.

## 🧑‍💻 Author

Developed as a practical application of computer vision and facial landmark detection for real-world safety use cases.
