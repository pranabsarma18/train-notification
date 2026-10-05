# 🚆 Train Notification Monitor

A Raspberry Pi-based train monitoring system that automatically checks the live status of a train and announces when it reaches a specified station.

The system uses the **RailRadar API** to obtain live train information, **Python** to monitor the train, **Piper TTS** to generate natural-sounding voice announcements, and a **Bluetooth speaker** connected to the Raspberry Pi for audio output.

The entire system runs automatically on a Raspberry Pi using a `systemd` service.

---

## ✨ Features

- 🚆 Monitors a specific train using its train number
- 📍 Tracks a specific station
- 🔄 Checks the train's live status periodically
- ⏱️ Runs only during a configured monitoring window
- 🧠 Detects whether the train:
  - Has not reached the station
  - Has reached the station
  - Has reached and departed the station
- 🔊 Generates natural voice announcements using Piper TTS
- 📢 Repeats the arrival announcement multiple times
- 🔵 Uses a Bluetooth speaker connected to the Raspberry Pi
- 🔐 Keeps the RailRadar API key outside the source code using environment variables
- ⚙️ Runs automatically using `systemd`

---

## 🏗️ Architecture

```text
                    ┌──────────────────────┐
                    │     RailRadar API    │
                    │   Live Train Status  │
                    └──────────┬───────────┘
                               │
                               │ HTTP Request
                               ▼
                    ┌──────────────────────┐
                    │  train_monitor.py    │
                    │                      │
                    │  Check train status  │
                    │  Check target station│
                    └──────────┬───────────┘
                               │
                    Station reached?
                               │
                    ┌──────────┴──────────┐
                    │                     │
                   No                    Yes
                    │                     │
                    ▼                     ▼
              Wait 5 minutes       Generate message
                                          │
                                          ▼
                                  ┌───────────────┐
                                  │   Piper TTS   │
                                  └───────┬───────┘
                                          │
                                          ▼
                                  ┌───────────────┐
                                  │ Bluetooth     │
                                  │ Speaker       │
                                  └───────────────┘
```

---

## 🛠️ Technologies Used

- **Python**
- **Requests** – API requests
- **python-dotenv** – loading environment variables
- **RailRadar API** – live train information
- **Piper TTS** – text-to-speech
- **PipeWire** – Linux audio system
- **Bluetooth** – wireless speaker connection
- **systemd** – automatic service execution
- **Raspberry Pi 5**
- **Debian GNU/Linux 13**

---

## 🚆 Current Configuration

The current version is configured to monitor:

| Setting | Value |
|---|---|
| Train | Brahmaputra Mail |
| Train Number | `15657` |
| Target Station | New Alipurduar |
| Station Code | `NOQ` |
| Monitoring Start | 06:15 AM |
| Monitoring End | 08:15 AM |
| Check Interval | 5 minutes |
| Announcement Repetitions | 10 |
| Delay Between Announcements | 2 seconds |

These values can be changed directly in `train_monitor.py`.

---

## 📡 RailRadar API

The project uses the RailRadar live train endpoint:

```text
GET https://api.railradar.in/v1/trains/{TRAIN_NUMBER}/live
```

Authentication is performed using a Bearer token:

```text
Authorization: Bearer <API_KEY>
```

The API response contains the train's route and the current status of individual stations.

For example, a station can have statuses such as:

```text
upcoming
reached
departed
```

The application uses these statuses to determine whether the target station has been reached.

---

## 🔍 Station Detection Logic

The monitor searches the train's route for the configured station code.

For example:

```python
STATION_CODE = "NOQ"
```

The application then checks the station's status.

### Upcoming

```text
status = upcoming
```

The train has not reached the station yet.

The application waits and checks again after the configured interval.

### Reached

```text
status = reached
```

The train has reached the target station.

The application generates an announcement.

### Departed

```text
status = departed
```

The train has already reached and departed the target station.

The API provides the observed arrival and departure times, which are included in the announcement.

This is particularly useful because the application does not need to catch the exact moment when the train changes from `upcoming` to `reached`.

---

## 🔊 Voice Announcements

The project uses **Piper TTS** to generate natural-sounding speech.

When the train reaches the target station, the announcement is repeated:

```text
10 times
```

with a:

```text
2 second
```

pause between announcements.

Example:

```text
Train reached NOQ at 07:52 and departed at 07:54
```

The generated audio is played through the connected Bluetooth speaker.

---

## 🔵 Bluetooth Speaker

The Raspberry Pi connects to a Bluetooth speaker and exposes it as a PipeWire audio sink.

The connected audio device can be checked using:

```bash
pactl list short sinks
```

A Bluetooth sink will look similar to:

```text
bluez_output.00_02_3C_CA_9C_49.1
```

The Bluetooth connection can be checked with:

```bash
bluetoothctl info <MAC_ADDRESS>
```

Look for:

```text
Connected: yes
```

---

## 📁 Project Structure

```text
train-notification/
│
├── train_monitor.py
├── requirements.txt
├── .gitignore
├── .env                  # Not committed
│
├── .venv/                # Not committed
│
└── Piper voice model     # Not committed
```

The Piper voice model is intentionally excluded from Git because it does not need to be stored in the source repository.

---

## 🔐 Environment Variables

The RailRadar API key is stored in `.env` rather than directly in the Python source code.

Create:

```text
.env
```

with:

```env
RAILRADAR_API_KEY=your_api_key_here
```

The Python application loads it using:

```python
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("RAILRADAR_API_KEY")
```

### ⚠️ Security

Never commit `.env` to GitHub.

The repository's `.gitignore` contains:

```gitignore
.env
```

If an API key is accidentally exposed on GitHub, revoke it and generate a new one.

---

## 🐍 Python Environment

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running Manually

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run:

```bash
python train_monitor.py
```

The application will monitor the train during the configured time window.

---

## ⚙️ Automatic Execution with systemd

The application can run automatically using a user-level `systemd` service.

The service executes:

```text
/home/pranabsarma18/Desktop/train-notification/.venv/bin/python
```

against:

```text
train_monitor.py
```

This means the application runs using the project's virtual environment rather than the system Python installation.

Check the service:

```bash
systemctl --user status train-monitor.service
```

Restart it:

```bash
systemctl --user restart train-monitor.service
```

Stop it:

```bash
systemctl --user stop train-monitor.service
```

---

## ⏰ Monitoring Window

The application is configured to monitor only during:

```text
06:15 AM → 08:15 AM
```

Before 06:15:

```text
Waiting for monitoring window
```

During the monitoring window:

```text
RailRadar API
      ↓
Check train
      ↓
Check NOQ
      ↓
Wait 5 minutes
      ↓
Check again
```

At 08:15:

```text
Monitoring window finished.
```

The Python process exits normally.

---

## 📋 Checking the Service

Check the current status of the train monitor:

```bash
systemctl --user status train-monitor.service
```

Start the service manually:

```bash
systemctl --user start train-monitor.service
```

Restart the service:

```bash
systemctl --user restart train-monitor.service
```

Stop the service:

```bash
systemctl --user stop train-monitor.service
```

The service status also shows recent output from the Python application, which is useful for checking whether the monitor started correctly and whether it encountered an error.

For troubleshooting, the application can also be run directly:

```bash
source .venv/bin/activate
python train_monitor.py
```

Running it manually is useful when troubleshooting API requests, Bluetooth connectivity, audio output, or Python errors.

---

## 🧪 Testing

Before relying on the system automatically, test the individual components.

### Test Bluetooth

```bash
bluetoothctl info <MAC_ADDRESS>
```

Confirm:

```text
Connected: yes
```

### Test audio output

```bash
pactl list short sinks
```

### Test text-to-speech

```bash
espeak-ng "Bluetooth speaker test"
```

Piper can also be tested directly using the installed voice model.

### Test Python syntax

```bash
python -m py_compile train_monitor.py
```

No output indicates that the syntax check passed.

---

## 🔄 How the System Works

The complete workflow is:

```text
Start
  │
  ▼
Check current time
  │
  ├── Outside monitoring window ──► Wait / Exit
  │
  ▼
Request live train status
  │
  ▼
Find NOQ in train route
  │
  ├── Upcoming ──► Wait 5 minutes
  │
  ├── Reached ──► Announce
  │
  └── Departed ─► Announce
                       │
                       ▼
                 Repeat 10 times
                       │
                       ▼
                      Exit
```

---

## 💡 Why This Project?

The idea behind the project is simple:

Instead of manually checking the train status every morning, the Raspberry Pi continuously monitors the train during the relevant time window and provides an audible notification when the train reaches the station.

This combines several practical concepts:

- REST API consumption
- Python automation
- JSON data processing
- Time-based scheduling
- Text-to-speech
- Bluetooth audio
- Linux services
- Raspberry Pi
- Environment variable management

---

## 🚀 Possible Future Improvements

Some possible improvements for future versions:

- [ ] Add support for multiple trains
- [ ] Add support for multiple stations
- [ ] Automatically reconnect the Bluetooth speaker
- [ ] Add API failure retry/backoff handling
- [ ] Store historical train delays
- [ ] Calculate average delay at the target station
- [ ] Add a web dashboard
- [ ] Add Telegram/WhatsApp/mobile notifications
- [ ] Add configurable settings through a YAML/JSON file
- [ ] Add logging to a local database
- [ ] Add a system health check
- [ ] Detect missed station updates more intelligently
- [ ] Add a daily notification history

---

## 📜 License

This project is intended for personal and educational use.

---

## 👤 Author

**Pranab Sarma**

Built with Python and Raspberry Pi.
