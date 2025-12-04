@echo off
echo Starting ngrok for AI Server...
cd /d C:\Users\hi\ngrok
start "ngrok" ngrok.exe http 8001
echo ngrok started! Check http://localhost:4040 for status.
timeout /t 3
