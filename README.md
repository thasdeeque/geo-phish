# geo-phish
**GeoSpy** is a phishing tool disguised as a survey or prayer compass. Attackers generate a public link and trick victims into visiting. It secretly collects GPS location, device details, IP address, battery status, and survey answers. Data is sent to the attacker’s ser[README.md](https://github.com/user-attachments/files/26217180/README.md)
ver# 📍 LocationPhish — GPS Location Tracker Awareness Demo

> Demonstrates how attackers trick users into sharing their GPS location through fake survey pages.

⚠️ **Educational and awareness purposes only. Only use on yourself or with explicit permission.**

---

## How it works

1. Flask serves a fake survey page with 3 random questions from a pool of 30
2. After question 1, a location permission modal appears
3. If granted, GPS coordinates are sent to the Flask backend
4. Device info, IP, timezone, and survey answers are also collected
5. Terminal displays all data with a Google Maps link
6. Everything saved as JSON in the `logs/` folder

---

## Install

```bash
pip install -r requirements.txt
```

Cloudflared installs automatically on first run.

---

## Usage

```bash
python3 app.py
```

---

## File Structure

```
locationphish/
├── app.py
├── templates/
│   └── index.html
├── logs/
├── requirements.txt
└── README.md
```

---

## Disclaimer

For **educational awareness only**. Unauthorized use is illegal.
 and logged. Victims unknowingly expose sensitive personal information.
