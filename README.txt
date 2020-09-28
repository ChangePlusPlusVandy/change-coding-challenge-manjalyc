The program is written in Python3 and is called twitter.py. Assuming you already have python3 installed, you will need to install the requests_oauthlib package for python (see Tips & Troubleshooting #1 below)

Note this program requires Python v3.6 or greater, Python3.5 and below will error out.

Also I couldn't really document my code as well as I might've liked as I only had the last 2-3 hours to code this because of my classes, exams, and the fact twitter just gave me access this morning. But I've tried my best in the timeframe I've been given.

Tips & Troubleshooting:

1. ModuleNotFoundError: No module named 'requests_oauthlib'
    - The requests_oauthlib package is not installed
    - For most windows distrubtions with python3 and pip installed (pip is an option in the default installation process for python) running the following command in command prompt should suffice:
        > "C:\Program Files\Python38\python.exe" -m pip install requests_oauthlib
            - note the use of Python38, it is likely you might be on Python37 (or another version) and should make the appropriate changes, also if you installed python to a nonstandard location you will need to replace this file location
            - Th

2. Pasting keys/secrets instead of typing them out:
    - In windows you can right click to paste from clipboard instead of typing out your client_key & client_secret when prompted if your in cmd, if using an IDE or IDLE, ctrl+shift+v might work
    - In linux, ctrl+shift+v or shift+ins should paste from clipboard in your terminals/ides

3. Not having to type in your client key and secret every time:
    a. Open up twitter-game.py
    b. Change the following lines (line 9 & 10) from:
        > client_key = input('Please Enter Your Client Key (available in your developer portal as API Key): ')
        > client_secret = input('Please Enter Your Client Secret (available in your developer portal as API Key Secret): ')
        to
        > client_key = 'YOUR_CLIENT_KEY_HERE'
        > client_secret = 'YOUR_CLIENT_SECRET_HERE'