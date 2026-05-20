"""Send MK11 inputs as MIDI to LoopBe Internal MIDI 1 -> loops to controller.py.
Usage:  python attack.py <combo>
        python attack.py seq <note> <hold_ms> [<note> <hold_ms> ...]
        python attack.py list"""
import mido, time, sys

PORT = 'LoopBe Internal MIDI 1'
out = mido.open_output(PORT)

UP,DOWN,LEFT,RIGHT = 60,62,64,65
FP,BP,FK,BK = 67,69,71,72
BLOCK,THROW,FLIP,GRAB = 74,76,77,79

def press(note, hold_ms=70, gap_ms=30):
    out.send(mido.Message('note_on', note=note, velocity=100))
    time.sleep(hold_ms/1000)
    out.send(mido.Message('note_off', note=note))
    time.sleep(gap_ms/1000)

def hold(notes, hold_ms=80):
    for n in notes: out.send(mido.Message('note_on', note=n, velocity=100))
    time.sleep(hold_ms/1000)
    for n in notes: out.send(mido.Message('note_off', note=n))

COMBOS = {
    'jab':           lambda: press(FP),
    'jab2':          lambda: (press(FP), press(FP)),
    'uppercut':      lambda: (press(DOWN,40), press(BP,90)),
    'sweep':         lambda: (press(DOWN,40), press(BK,90)),
    'low_kick':      lambda: (press(DOWN,40), press(FK,80)),
    'jump':          lambda: press(UP, 60),
    'jump_kick':     lambda: (press(UP,60), press(FK,80)),
    'crouch':        lambda: press(DOWN, 300),
    'block':         lambda: press(BLOCK, 600),
    'walk_fwd':      lambda: press(RIGHT, 500),
    'walk_back':     lambda: press(LEFT, 500),
    'dash_fwd':      lambda: (press(RIGHT,60), press(RIGHT,200)),
    'dash_back':     lambda: (press(LEFT,60), press(LEFT,200)),
    'throw':         lambda: press(THROW),
    'flip_stance':   lambda: press(FLIP),
    'punch_kombo':   lambda: (press(FP,50), press(FP,50), press(BP,80)),
    'kick_kombo':    lambda: (press(FK,50), press(FK,50), press(BK,80)),
    'cross_kombo':   lambda: (press(FP,50), press(FK,50), press(BP,80)),
    'amp_special':   lambda: (press(DOWN,40), press(RIGHT,40), press(FP,80)),  # ↓→ FP fireball-ish
}

if len(sys.argv) < 2 or sys.argv[1] in ('list','-h','--help'):
    print('combos:'); [print(f'  {k}') for k in COMBOS]
    print('seq:  python attack.py seq 60 80 62 80  (note, hold_ms pairs)')
    sys.exit()

cmd = sys.argv[1]
if cmd == 'seq':
    args = sys.argv[2:]
    for i in range(0, len(args), 2): press(int(args[i]), int(args[i+1]))
elif cmd in COMBOS:
    print(f'[atk] {cmd}'); COMBOS[cmd]()
else:
    print(f'unknown: {cmd}. try "list"')
