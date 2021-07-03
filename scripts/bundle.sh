#! /bin/zsh


# https://unix.stackexchange.com/a/115431
root=${0:A:h:h}

cd "$root/addon"

zip  \
    --recurse-paths ../bundle/anki-marker.ankiaddon . \
    --exclude "**/.*" \
    --include \
        "./src/**.py" \
        "./assets/**" \
        "./__init__.py" \
        "./user_files/**" \
        "./config.json" \
        "./config.md" \
        "./meta.json"