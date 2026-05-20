"""ElevenLabs TTS -> WAV -> winsound. Plays on Windows default device.
Usage: python say.py "trash talk"   |   --bg = play non-blocking"""
import os, sys, urllib.request, json, tempfile, struct, winsound, time

KEY = os.environ.get('ELEVENLABS_API_KEY', '')
VOICE = os.environ.get('VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Adam
MODEL = os.environ.get('VOICE_MODEL', 'eleven_turbo_v2_5')
SR = 44100

if not KEY:
    print('ELEVENLABS_API_KEY not set', file=sys.stderr); sys.exit(1)

args = [a for a in sys.argv[1:] if a != '--bg']
bg = '--bg' in sys.argv
text = ' '.join(args).strip() or 'Get over here.'

req = urllib.request.Request(
    f'https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=pcm_{SR}',
    data=json.dumps({'text': text, 'model_id': MODEL,
                     'voice_settings': {'stability': 0.4, 'similarity_boost': 0.85, 'style': 0.6}}).encode(),
    headers={'xi-api-key': KEY, 'Content-Type': 'application/json'},
    method='POST')
try:
    with urllib.request.urlopen(req, timeout=20) as r:
        pcm = r.read()
except urllib.error.HTTPError as e:
    print(f'ElevenLabs {e.code}: {e.read().decode()[:200]}', file=sys.stderr); sys.exit(1)

n = len(pcm)
hdr = (b'RIFF' + struct.pack('<I', 36+n) + b'WAVEfmt ' + struct.pack('<I',16) +
       struct.pack('<HHIIHH', 1, 1, SR, SR*2, 2, 16) + b'data' + struct.pack('<I', n))
out = os.path.join(tempfile.gettempdir(), 'mk_say.wav')
with open(out, 'wb') as f: f.write(hdr + pcm)
dur = n / (SR*2)
print(f'[say] "{text}"  ({dur:.1f}s)')

# Mute the listener for the duration of playback + small tail
MUTE = r'C:\Users\Owner\scripts\mk_midi\.speaking'
open(MUTE, 'w').close()
try:
    flags = winsound.SND_FILENAME | (winsound.SND_ASYNC if bg else 0)
    winsound.PlaySound(out, flags)
    time.sleep(dur + 0.4)  # always wait so MUTE covers full playback
finally:
    try: os.remove(MUTE)
    except: pass
