#!/bin/bash
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
  echo 'Python 3 ontbreekt. Installeer via https://www.python.org/downloads/macos/'
  read -r -p 'Druk op Enter om af te sluiten.'
  exit 1
fi
python3 app.py
read -r -p 'Druk op Enter om af te sluiten.'
