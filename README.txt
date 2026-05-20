MK11 MIDI Controller
====================

1. Open ONE terminal, run:
     python C:\Users\Owner\scripts\mk_midi\controller.py
   (leave it running — it listens on "LoopBe Internal MIDI 0")

2. Launch MK11. Focus the game window.

3. From another terminal (or me via Bash), send inputs:
     python C:\Users\Owner\scripts\mk_midi\attack.py jab
     python C:\Users\Owner\scripts\mk_midi\attack.py uppercut
     python C:\Users\Owner\scripts\mk_midi\attack.py amp_special
     python C:\Users\Owner\scripts\mk_midi\attack.py list      # see all combos
     python C:\Users\Owner\scripts\mk_midi\attack.py seq 60 80 62 80   # raw notes

Keymap (verify in MK11 Options -> Controls — adjust SC{} and KEYMAP{} in controller.py if different):
  W A S D            movement
  U I J K            FP BP FK BK   (1 2 3 4)
  Space              block
  L                  throw
  H                  flip stance
  R                  interact

MIDI -> Key:
  C3(60) Up     D3(62) Down    E3(64) Left   F3(65) Right
  G3(67) FP     A3(69) BP      B3(71) FK     C4(72) BK
  D4(74) Block  E4(76) Throw   F4(77) Stance G4(79) Interact

Notes:
- LoopBe Internal MIDI 0 (input) and 1 (output) are the SAME virtual port.
- SendInput uses scancodes so DirectInput-based games (MK11) receive them.
- Combos timing-tuned for casual play, not frame-perfect.
- If MK11 doesn't see keys: try running controller.py in an elevated terminal.
