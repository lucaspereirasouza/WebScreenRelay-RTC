## Description
For from "dsavchenko/screenshare"

I made it more appropriated with RTC and able to use mouse Icon with MSS. Prob i'll make specific for some windows, because i wanted to see my phone and my computer through spaceframe, and i suspect i need some security beside being purely on local

## Requirements

This tool can run on Linux, Windows and MAC.

+ Python 2.x or 3.x

+ Know issue: Idk, i'm using rtc am MSS, prob some linux interfaces doesn't work well.

## Install

1. pip install -r requirements.txt

2. run "**git clone https://github.com/lucaspereirasouza/WebScreenRelay-RTC.git**".

## Run as http

1. To start the screen sharing service, run "**python screenshare.py [-p port] [-w password]**".

	The default service port is 18331. Example commands are below.

	\# host screenshots on port 18331 and no password

	python screenshare.py

	\# host screenshots on port 80 and password "abcdef"

	python screenshare.py -p 80 -w abcdef

	python screenshare.py --port 80 --password abcdef

2. On other computers, open a web browser and browse "**http://serverip:port**".

	For example, if the server ip is 192.168.0.101 and the service port is 18331, then the URL to browse is "http://192.168.0.101:18331".

## Run as https

1. (Optional) Create a self-signed certificate and a private key. Or, obtain a signed certificate and private key.

    \# openssl req -x509 -newkey rsa:2048 -nodes -out **cert.pem** -keyout **key.pem** -days 9999

2. To start the screen sharing service with https, run "**python screenshare.py -s [-p port] [-w password] [-c cert.pem -k key.pem]**".

	The default service port is 18331. Example commands are below.

	\# host screenshots on port 18331 and no password, https with default built-in certificate and private key

	python screenshare.py **-s**

	\# host screenshots on port 443 and password "abcdef", https with default built-in certificate and private key

	python screenshare.py **-s** -p 443 -w abcdef

	python screenshare.py **-s** --port 443 --password abcdef

    \# host screenshots on port 18331 and no password, https with a certificate file and a private key file

    python screenshare.py **-s** -c cert.pem -k key.pem

3. On other computers, open a web browser and browse "**https://serverip:port**".

	For example, if the server ip is 192.168.0.101 and the service port is 18331, then the URL to browse is "https://192.168.0.101:18331".

    You will see a warning about the self-signed certificate in the web browser. Accept the warning and continue.

## To terminate:

    In Linux, press CTRL \  (Control Backslash, not CTRL C)

    In Windows, press CTRL Break


