#!/bin/bash

SESSION_ID=$1
OUTPUT_FILE="./dataset.csv"

# Coordinates (from getevent)
FEED_X=128
FEED_Y=2223
REELS_X=753
REELS_Y=2233

# Write header if not exists
if [ ! -f "$OUTPUT_FILE" ]; then
  echo "session_id,action,start_epoch,end_epoch" > $OUTPUT_FILE
fi

log_action() {
  ACTION=$1
  START=$2
  END=$3
  echo "$SESSION_ID,$ACTION,$START,$END" >> $OUTPUT_FILE
}

# Function to classify Feed content
classify_feed() {
  if grep -qi "Sponsored" ui.xml; then
    echo "feed_ad"
  elif grep -qi "Video" ui.xml || grep -qi "Play" ui.xml || grep -qi "Watch" ui.xml; then
    echo "feed_video"
  else
    echo "feed_image"
  fi
}

# Launch Instagram
adb shell am start -n com.instagram.android/.activity.MainTabActivity
sleep 5

### --- FEED SCROLLING ---
echo "📌 Switching to Feed/Home"
adb shell input tap $FEED_X $FEED_Y
sleep 3

for i in {1..5}; do
  START=$(date +%s)
  adb shell input swipe 500 1500 500 500 500
  sleep 2

  adb shell uiautomator dump /sdcard/ui.xml
  adb pull /sdcard/ui.xml ./ui.xml >/dev/null

  ACTION=$(classify_feed)
  END=$(date +%s)
  log_action $ACTION $START $END
done

### --- REELS SCROLLING ---
echo "📌 Switching to Reels"
adb shell input tap $REELS_X $REELS_Y
sleep 3

for i in {1..5}; do
  START=$(date +%s)
  adb shell input swipe 500 1500 500 500 500
  sleep 4

  # In Reels tab → always reel_video
  ACTION="reel_video"
  END=$(date +%s)
  log_action $ACTION $START $END
done

echo "✅ Dataset saved to $OUTPUT_FILE"
