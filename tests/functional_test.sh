#!/bin/bash
# Comprehensive functional tests for telegram-upload
# Requirements: .env file with TELEGRAM_UPLOAD_SESSION or local config

FORUM_ID="-1003818653829"
CHANNEL_ID="-1003971834184"

# Setup test artifacts
mkdir -p tests/Test_Topic_Folder
echo "topic file content" > tests/Test_Topic_Folder/topic_file.txt
echo "dist file 1" > tests/dist1.txt
echo "dist file 2" > tests/dist2.txt
echo "normal file" > tests/normal.txt

# Load environment if exists
[ -f .env ] && set -a && . .env && set +a

echo "--- TEST 1: Auto-Topic Creation & Folder Upload ---"
telegram-upload --to $FORUM_ID -t "tests/Test_Topic_Folder"

echo "--- TEST 2: Targeted Mapping to Specific Topics ---"
telegram-upload --to $FORUM_ID -t "Topic A" tests/dist1.txt -t "Topic B" tests/dist2.txt

echo "--- TEST 3: Speed Boost (Parallel Connections) ---"
export TELEGRAM_UPLOAD_MAX_CONNECTIONS=2
telegram-upload --to $CHANNEL_ID tests/normal.txt

echo "--- TEST 4: Recursive Upload to Chat ---"
telegram-upload --to $CHANNEL_ID tests/Test_Topic_Folder

echo "--- TEST 5: Download by Topic Name ---"
telegram-download --from $FORUM_ID --topic "Topic A"

# Cleanup
rm -rf tests/Test_Topic_Folder tests/dist1.txt tests/dist2.txt tests/normal.txt
