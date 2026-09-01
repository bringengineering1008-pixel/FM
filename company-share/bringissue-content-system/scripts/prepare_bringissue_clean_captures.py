from pathlib import Path
from PIL import Image


SOURCE = Path(r"C:\Users\user\.codex\worktrees\7129\마케팅\blog\assets\2026-08-21-goyounjung-youtube")
DEST = Path(r"C:\Users\user\.codex\worktrees\7129\마케팅\blog\assets\2026-08-21-goyounjung-youtube-clean")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.glob("*.png")):
        with Image.open(source) as image:
            # The source screenshot contains a 1422x800 16:9 video frame in the
            # upper-left. Everything to its right/below belongs to YouTube UI.
            clean = image.crop((0, 0, 1422, 800))
            clean.save(DEST / source.name, optimize=True)
    print(DEST)


if __name__ == "__main__":
    main()
