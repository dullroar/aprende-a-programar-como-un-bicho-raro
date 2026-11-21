#!/bin/sh
# Backup pusher: push loop/es-v4 to origin whenever HEAD changes (checks every 45 s).
# Start:  setsid nohup loop/pusher.sh > loop/pusher.out 2>&1 < /dev/null &
# Stop:   touch loop/PUSHER-STOP
cd "$(dirname "$0")/.." || exit 2
exec 8>loop/.pusher.lock
flock -n 8 || { echo "pusher already running"; exit 0; }
rm -f loop/PUSHER-STOP
while [ ! -f loop/PUSHER-STOP ]; do
  loop/push-backup.sh
  sleep 45
done
