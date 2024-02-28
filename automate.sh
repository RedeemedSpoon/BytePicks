#!/bin/bash

fileList="daily.json weekly.json monthly.json yearly.json token.json channels.csv"
remoteDir="/opt/render/project/src"

scp -s $SERVER_NAME@ssh.oregon.render.com:$remoteDir/newsletter.db .
python youtube.py && python newsletter.py

if [[ $? -ne 0 ]]; then
  echo "Error: Script(s) exited with non-zero code." >> youtube.log
else 
  scp -s $fileList $SERVER_NAME@ssh.oregon.render.com:$remoteDir
fi

