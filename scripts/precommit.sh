#! /bin/zsh

root=${0:A:h:h}

black "$root/addon" \
&& isort "$root/addon" \
&& pytest \
&& rm -f "$root/addon/meta.json" \
&& rm -f "$root/bundle/anki-marker.ankiaddon" \
&& zsh "$root/scripts/bundle.sh"