"""MK11 MIDI controller. MIDI note ON/OFF -> keyboard press/release via SendInput scancodes.
Run, focus MK11 window, then send MIDI to LoopBe Internal MIDI 0 (port 1 from the sender side)."""
import ctypes, mido, sys
from ctypes import wintypes

# --- SendInput plumbing (scancode = DirectInput-friendly, MK11 reads these) ---
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_EXTENDED = 0x0001

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk",wintypes.WORD),("wScan",wintypes.WORD),("dwFlags",wintypes.DWORD),
                ("time",wintypes.DWORD),("dwExtraInfo",ctypes.POINTER(wintypes.ULONG))]
class _U(ctypes.Union):
    _fields_ = [("ki",KEYBDINPUT),("pad",ctypes.c_ubyte*32)]
class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type",wintypes.DWORD),("u",_U)]

EXTENDED = {0xE048,0xE050,0xE04B,0xE04D,0xE01C,0xE053,0xE052,0xE04F,0xE047,0xE049,0xE051}
def _send(scan, up):
    flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if up else 0)
    if scan in EXTENDED: flags |= KEYEVENTF_EXTENDED; scan &= 0xFF
    inp = INPUT(type=INPUT_KEYBOARD, u=_U(ki=KEYBDINPUT(0, scan, flags, 0, None)))
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

# --- MK11 default PC scancodes (verify in MK11 Options -> Controls) ---
SC = {
    'w':0x11,'a':0x1E,'s':0x1F,'d':0x20,
    'u':0x16,'i':0x17,'j':0x24,'k':0x25,'l':0x26,'h':0x23,'r':0x13,
    'space':0x39,'enter':0x1C,'esc':0x01,'tab':0x0F,
    'up':0xE048,'down':0xE050,'left':0xE04B,'right':0xE04D,
    'numenter':0xE01C, 'backspace':0x0E,
}
KEYMAP = {
    60:'w', 62:'s', 64:'a', 65:'d',            # C3 D3 E3 F3  movement (P1)
    67:'u', 69:'i', 71:'j', 72:'k',            # G3 A3 B3 C4  FP BP FK BK
    74:'space', 76:'l', 77:'h', 79:'r',        # D4 E4 F4 G4  Block Throw Stance Interact
    81:'enter', 83:'esc', 84:'tab',            # A4 B4 C5
    86:'up', 88:'down', 89:'left', 91:'right', # D5 E5 F5 G5  arrow keys (menus / P2 nav)
    93:'numenter',                              # A5
}

PORT = 'LoopBe Internal MIDI 0'
print(f'[mk-ctrl] listening on "{PORT}"')
print(f'[mk-ctrl] {len(KEYMAP)} notes mapped. Focus MK11 window.')
held = set()
try:
    with mido.open_input(PORT) as inp:
        for msg in inp:
            note = getattr(msg,'note',None)
            if note is None or note not in KEYMAP: continue
            key = KEYMAP[note]; scan = SC[key]
            on = msg.type=='note_on' and msg.velocity>0
            if on and note not in held:
                _send(scan, False); held.add(note); print(f'  DN {note:3d} -> {key}')
            elif (msg.type=='note_off' or (msg.type=='note_on' and msg.velocity==0)) and note in held:
                _send(scan, True); held.discard(note); print(f'  UP {note:3d} -> {key}')
except KeyboardInterrupt:
    for n in list(held): _send(SC[KEYMAP[n]], True)
    print('\n[mk-ctrl] released all, bye')
