#!/bin/bash

NAME="$1"
TASK="$2"
RUN="$3"

echo "Make sure direwolf is running: direwolf/direwolf -t 0"
read
echo "Okay, starting now..."
source env/bin/activate
./gentag.py direwolf 15 "$NAME" "$TASK" "$RUN"
