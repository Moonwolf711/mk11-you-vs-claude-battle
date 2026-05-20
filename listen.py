"""Yeti -> ElevenLabs Scribe STT -> heard.log (tail -f friendly).
Energy-gated: starts recording on speech, sends on ~0.8s silence."""
import os, sys, time, struct, io, urllib.request, json, threading, numpy as np
import sounddevice as sd

KEY = os.environ.get('ELEVENLABS_API_KEY', '')
if not KEY: print('ELEVENLABS_API_KEY not set', file=sys.stderr); sys.exit(1)

DEV_MATCH = os.environ.get('MIC_DEVICE', 'Yeti')
CAPTURE_SR = 48000           # Yeti native
SR = 16000                   # send to Scribe at 16k
DECIMATE = CAPTURE_SR // SR  # 3
CHUNK = 4800                 # 100 ms at 48k
RMS_ON = 0.004               # start threshold
RMS_OFF = 0.002              # stop threshold
SILENCE_MS = 1200            # ms of silence to close segment (longer = catches pauses)
MIN_MS = 300                 # discard sub-300ms blips
MAX_MS = 12000               # force-send at 12s

wasapi = next((i for i,h in enumerate(sd.query_hostapis()) if 'WASAPI' in h['name']), None)
cands = [(i,d) for i,d in enumerate(sd.query_devices())
         if d['max_input_channels']>0 and DEV_MATCH.lower() in d['name'].lower()]
if not cands: print(f'no mic matching "{DEV_MATCH}"', file=sys.stderr); sys.exit(1)
pref = [c for c in cands if c[1]['hostapi']==wasapi] or cands
dev_idx, dev = pref[0]
print(f'[listen] mic dev {dev_idx}: {dev["name"]}  ({SR} Hz, gate RMS_ON={RMS_ON})')

LOG = os.path.expanduser(r'C:\Users\Owner\scripts\mk_midi\heard.log')
def log(line):
    with open(LOG, 'a', encoding='utf-8') as f: f.write(line + '\n')
    print(line, flush=True)

def pcm_to_wav(pcm16):
    n = len(pcm16) * 2
    hdr = (b'RIFF' + struct.pack('<I', 36+n) + b'WAVEfmt ' + struct.pack('<I',16) +
           struct.pack('<HHIIHH', 1, 1, SR, SR*2, 2, 16) + b'data' + struct.pack('<I', n))
    return hdr + pcm16.tobytes()

def scribe(wav_bytes):
    boundary = '----mkmidi' + str(time.time())
    body = io.BytesIO()
    def part(name, value, filename=None, ctype=None):
        body.write(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'.encode())
        if filename: body.write(f'; filename="{filename}"'.encode())
        body.write(b'\r\n')
        if ctype: body.write(f'Content-Type: {ctype}\r\n'.encode())
        body.write(b'\r\n')
        body.write(value if isinstance(value, bytes) else value.encode())
        body.write(b'\r\n')
    part('model_id', 'scribe_v1')
    part('language_code', 'en')
    part('tag_audio_events', 'false')
    part('file', wav_bytes, filename='clip.wav', ctype='audio/wav')
    body.write(f'--{boundary}--\r\n'.encode())
    req = urllib.request.Request('https://api.elevenlabs.io/v1/speech-to-text',
        data=body.getvalue(),
        headers={'xi-api-key': KEY, 'Content-Type': f'multipart/form-data; boundary={boundary}'},
        method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {'error': f'{e.code}: {e.read().decode()[:200]}'}

buf = []
voiced = False
silence_chunks = 0
silence_needed = SILENCE_MS // (CHUNK*1000//CAPTURE_SR)
min_chunks = MIN_MS // (CHUNK*1000//CAPTURE_SR)
max_chunks = MAX_MS // (CHUNK*1000//CAPTURE_SR)
log(f'[listen] started at {time.strftime("%H:%M:%S")}')

def stream_cb(indata, frames, t, status):
    global voiced, silence_chunks, buf
    mono = indata[:,0] if indata.ndim>1 else indata
    rms = float(np.sqrt(np.mean(mono**2)))
    if voiced:
        buf.append(mono.copy())
        if rms < RMS_OFF: silence_chunks += 1
        else: silence_chunks = 0
        if silence_chunks >= silence_needed or len(buf) >= max_chunks:
            _flush()
    else:
        if rms > RMS_ON:
            voiced = True; silence_chunks = 0; buf = [mono.copy()]

def _flush():
    global buf, voiced, silence_chunks
    if len(buf) < min_chunks:
        buf = []; voiced = False; silence_chunks = 0; return
    audio = np.concatenate(buf)
    audio = audio[::DECIMATE]  # 48k -> 16k
    pcm16 = (audio * 32767).astype(np.int16)
    buf = []; voiced = False; silence_chunks = 0
    threading.Thread(target=_send, args=(pcm16,), daemon=True).start()

_last_text = ''
_last_text_t = 0
MUTE_FLAG = r'C:\Users\Owner\scripts\mk_midi\.speaking'
def _send(pcm16):
    global _last_text, _last_text_t
    if os.path.exists(MUTE_FLAG):
        return  # I'm speaking, ignore my own voice bleeding through
    wav = pcm_to_wav(pcm16)
    res = scribe(wav)
    if 'error' in res: log(f'[err] {res["error"]}')
    else:
        text = res.get('text','').strip()
        if not text: return
        now = time.time()
        # dedupe identical text within 5s
        if text == _last_text and (now - _last_text_t) < 5: return
        _last_text, _last_text_t = text, now
        log(f'[heard {time.strftime("%H:%M:%S")}] {text}')

try:
    with sd.InputStream(device=dev_idx, samplerate=CAPTURE_SR, channels=1, dtype='float32',
                        blocksize=CHUNK, callback=stream_cb):
        while True: sd.sleep(1000)
except KeyboardInterrupt:
    log('[listen] stopped'); sys.exit(0)
