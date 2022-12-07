#! /bin/zsh

# https://unix.stackexchange.com/a/115431
root=${0:A:h:h}

mkdir "$root/bundle"

cd "$root/addon"

zip                                       \
    "$root/bundle/AnkiMarker.ankiaddon" * \
    --recurse-paths                       \
    --exclude "**/.*"                     \
    --include                             \
        "./src/**.py"                     \
        "./src/assets/**"                 \
        "./__init__.py"                   \
        "./user_files/**"                 \
        "./manifest.json"
