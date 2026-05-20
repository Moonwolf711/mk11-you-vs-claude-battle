"""Endless Kano Assault. Real MK11 Kano advanced moves and combo strings.
Keymap (P1 left side): W=up A=back S=down D=fwd  U=FP I=BP J=FK K=BK  Space=block/AMP  L=throw H=stance
Stop: Ctrl-C or taskkill on this process."""
import mido, time, random, sys

PORT = 'LoopBe Internal MIDI 1'
out = mido.open_output(PORT)

# Notes match controller.py KEYMAP
UP,DOWN,BACK,FWD = 60,62,64,65
FP,BP,FK,BK = 67,69,71,72
BLOCK,THROW,FLIP = 74,76,77  # BLOCK doubles as AMP modifier in MK11

def k(note, hold=55, gap=18):
    """Tap a note (key down + up + small gap)."""
    out.send(mido.Message('note_on', note=note, velocity=100))
    time.sleep(hold/1000)
    out.send(mido.Message('note_off', note=note))
    time.sleep(gap/1000)

def motion(*notes, finisher_hold=70):
    """Quarter/half-circle motion: tap notes back-to-back, last one slightly longer."""
    for i, n in enumerate(notes):
        is_last = i == len(notes)-1
        k(n, hold=(finisher_hold if is_last else 35), gap=10)

def amp(special_fn, amp_window_ms=140):
    """Run a special, then press BLOCK (Space) within window to AMP it."""
    special_fn()
    time.sleep(amp_window_ms/1000)
    k(BLOCK, hold=60)

# --- Kano specials (P1 facing right) ---
def kano_ball():       motion(BACK, FWD, FK)         # ←→3
def up_ball():         motion(DOWN, BACK, FK)        # ↓←3
def kano_knives():     motion(DOWN, FWD, FP)         # ↓→1
def molotov():         motion(DOWN, BACK, FP)        # ↓←1 (low projectile)
def chemical_burn():   motion(DOWN, BACK, BP)        # ↓←2
def air_kano_ball():   k(UP, hold=120); time.sleep(0.18); motion(BACK, FWD, FK)
def laser_eye():       motion(DOWN, FWD, BP)         # ↓→2 (cybernetic)
def boomerang():       motion(BACK, DOWN, BACK, FP)  # ←↓←1 advanced

# --- Krushing / amp variants ---
def amp_ball():        amp(kano_ball)
def amp_knives():      amp(kano_knives)
def amp_up_ball():     amp(up_ball)
def amp_chemical():    amp(chemical_burn)

# --- Real Kano kombat strings (MK11 movelist) ---
def str_b14():    k(BACK, hold=80); k(FP); k(BK)                 # Black Dragon Strike (Back+FP, FP, BK is wrong — this is B1,4: Back+FP then BK)
def str_213():    k(BP); k(FP); k(FK)                            # Bayonet Slice
def str_121():    k(FP); k(BP); k(FP)                            # Choke Hold setup
def str_f44():    k(FWD, hold=60); k(BK); k(BK)                  # Stab Cycle
def str_b2():     k(BACK, hold=80); k(BP)                        # Overhead slice
def str_d4():     k(DOWN, hold=40); k(BK)                        # Low poke
def str_d1():     k(DOWN, hold=40); k(FP)                        # Faster low poke
def str_d2():     k(DOWN, hold=40); k(BP)                        # Uppercut
def str_jik():    k(UP, hold=80); k(BK)                          # Jump kick
def str_overhead_into_special(): str_b2(); time.sleep(0.05); kano_ball()

# --- Combo extensions ---
def combo_launch_special():
    str_d2()                  # uppercut launcher
    time.sleep(0.08)
    air_kano_ball()           # cancel into air ball
def combo_pressure_string():
    str_b14(); time.sleep(0.05); kano_knives()
def combo_corner_carry():
    str_f44(); time.sleep(0.05); amp_ball()
def throw_forward():  k(FWD, hold=40); k(THROW)
def throw_back():     k(BACK, hold=40); k(THROW)

# --- ULTIMATE TIER ---
def fatal_blow():
    # MK11 Fatal Blow PC default: Block + Throw simultaneously (Space + L)
    out.send(mido.Message('note_on', note=BLOCK, velocity=100))
    out.send(mido.Message('note_on', note=THROW, velocity=100))
    time.sleep(0.18)
    out.send(mido.Message('note_off', note=BLOCK))
    out.send(mido.Message('note_off', note=THROW))
def krushing_uppercut():
    # F+BP after blocked attack = krushing uppercut setup
    k(FWD, hold=60); time.sleep(0.04); k(BP, hold=110)
def krushing_ball():
    # Kano Ball after FB hit (perfect timing) = krushing
    kano_ball(); time.sleep(0.05); amp_ball()
def string_cancel_into_ball():
    str_213(); time.sleep(0.04); kano_ball()
def string_cancel_into_amp_ball():
    str_b14(); time.sleep(0.04); amp_ball()
def cross_up_jk():
    # jump forward + late jump kick = cross-up mixup
    k(UP, hold=60); time.sleep(0.05); k(FWD, hold=70); time.sleep(0.18); k(FK, hold=90)
def empty_jump_throw():
    # jump in but throw on landing (mixup)
    k(UP, hold=60); time.sleep(0.05); k(FWD, hold=60); time.sleep(0.25); k(THROW, hold=60)
def frame_trap():
    # tight jab, pause, uppercut to catch mash
    k(FP); time.sleep(0.18); k(DOWN, hold=40); k(BP, hold=100)
def wakeup_reversal():
    # simulate wake-up with up ball (input during getup)
    time.sleep(0.3); up_ball()
def safe_pressure():
    # b1 (safe overhead) into knives
    str_b2(); time.sleep(0.05); kano_knives()
def kombo_extender():
    # launcher → jump kick → air ball → on-ground knives
    str_d2(); time.sleep(0.08); k(UP, hold=60); time.sleep(0.12); k(FK, hold=70); time.sleep(0.20); air_kano_ball()
def chip_pressure_block():
    # repeated specials to chip block
    kano_knives(); time.sleep(0.20); kano_knives(); time.sleep(0.25); amp_knives()
def whiff_punish():
    # bait with back-dash, then dash-in punish
    dash_back(); time.sleep(0.18); dash_in(); time.sleep(0.04); str_213()
def corner_loop():
    # corner-only: 121 string → ball → repeat
    str_121(); time.sleep(0.05); kano_ball(); time.sleep(0.30); str_121()

# --- Movement ---
def dash_in():    k(FWD, hold=40); k(FWD, hold=180)
def dash_back():  k(BACK, hold=40); k(BACK, hold=180)
def walk_in():    k(FWD, hold=280)
def jump_in():    k(UP, hold=70)
def neutral_jump():k(UP, hold=90)

PLAYBOOK = [
    # (name, fn, weight)
    ('dash→str_b14',        lambda: (dash_in(), str_b14()),                4),
    ('amp_ball',            amp_ball,                                       5),
    ('kano_knives',         kano_knives,                                    3),
    ('amp_knives',          amp_knives,                                     4),
    ('chemical_burn',       chemical_burn,                                  3),
    ('amp_chemical',        amp_chemical,                                   3),
    ('up_ball_anti_air',    up_ball,                                        2),
    ('amp_up_ball',         amp_up_ball,                                    2),
    ('air_kano_ball',       air_kano_ball,                                  3),
    ('laser_eye',           laser_eye,                                      2),
    ('boomerang_advanced',  boomerang,                                      1),
    ('str_213',             str_213,                                        3),
    ('str_121',             str_121,                                        2),
    ('str_f44',             str_f44,                                        3),
    ('str_b2_overhead',     str_b2,                                         2),
    ('d4_low_poke',         str_d4,                                         4),
    ('d1_poke',             str_d1,                                         3),
    ('combo_pressure',      combo_pressure_string,                          5),
    ('combo_launch→air',    combo_launch_special,                           4),
    ('combo_corner_carry',  combo_corner_carry,                             3),
    ('throw_fwd',           throw_forward,                                  2),
    ('throw_back',          throw_back,                                     1),
    ('jump_kick',           str_jik,                                        2),
    ('overhead→special',    str_overhead_into_special,                      3),
    # ULTIMATE TIER
    ('FATAL_BLOW',          fatal_blow,                                     2),
    ('krushing_uppercut',   krushing_uppercut,                              3),
    ('krushing_ball_combo', krushing_ball,                                  3),
    ('cancel→ball',         string_cancel_into_ball,                        5),
    ('cancel→amp_ball',     string_cancel_into_amp_ball,                    6),
    ('cross_up_JK',         cross_up_jk,                                    4),
    ('empty_jump_throw',    empty_jump_throw,                               3),
    ('frame_trap',          frame_trap,                                     4),
    ('wakeup_reversal',     wakeup_reversal,                                2),
    ('safe_pressure',       safe_pressure,                                  5),
    ('KOMBO_EXTENDER',      kombo_extender,                                 4),
    ('chip_pressure',       chip_pressure_block,                            3),
    ('whiff_punish',        whiff_punish,                                   3),
    ('corner_loop',         corner_loop,                                    3),
]

POSITIONALS = [
    ('walk_in',   walk_in,        4),
    ('dash_in',   dash_in,        5),
    ('jump_in',   jump_in,        2),
    ('neutral_jump', neutral_jump, 1),
    ('dash_back', dash_back,      1),
]

names = [p[0] for p in PLAYBOOK]; fns = [p[1] for p in PLAYBOOK]; wts = [p[2] for p in PLAYBOOK]
pos_names = [p[0] for p in POSITIONALS]; pos_fns = [p[1] for p in POSITIONALS]; pos_wts = [p[2] for p in POSITIONALS]

n=0
print(f'[brawl] Kano ADVANCED — {len(PLAYBOOK)} moves in rotation', flush=True)
try:
    while True:
        if random.random() < 0.22:
            i = random.choices(range(len(POSITIONALS)), weights=pos_wts, k=1)[0]
            pos_fns[i]()
            print(f'  {n:4d}  pos  {pos_names[i]}', flush=True)
        i = random.choices(range(len(PLAYBOOK)), weights=wts, k=1)[0]
        fns[i]()
        n += 1
        print(f'  {n:4d}  ATK  {names[i]}', flush=True)
        time.sleep(random.uniform(0.18, 0.55))
except KeyboardInterrupt:
    print(f'[brawl] stopped after {n}')
