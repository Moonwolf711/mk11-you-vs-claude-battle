"""Capture screen. MK11 (DirectX) renders to display surface — PrintWindow can't see it,
but full-screen grab catches whatever is currently displayed. Run when MK11 is foreground."""
import sys, os, tempfile
from PIL import ImageGrab

out = os.path.join(tempfile.gettempdir(), 'mk_see.png')
img = ImageGrab.grab(all_screens=False)  # primary only by default
img.save(out, optimize=True)
print(f'{out}  [{img.size[0]}x{img.size[1]} primary screen]')
