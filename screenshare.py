# Copyright (C) 2026
# WebRTC-based Screenshare

import argparse
import asyncio
import json
import threading
#import concurrent.futures
import time
from fractions import Fraction

import traceback

from av.frame import Frame

from flask import Flask, request, render_template_string
from flask_bootstrap import Bootstrap
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    MediaStreamTrack
)
from av import VideoFrame

import mss
import numpy as np


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>ScreenShare WebRTC</title>
    <style>
        body {
            background: #111;
            margin: 0;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        video {
            width: 100%;
            height: 100%;
            object-fit: contain;
            background: black;
        }
    </style>
</head>
<body>
    <video
        id="video"
        autoplay
        playsinline
        muted>
    </video>
<script>
const video = document.getElementById("video")
const pc = new RTCPeerConnection()
pc.ontrack = (event) => {
    video.srcObject = event.streams[0]
}
pc.addTransceiver("video", {
    direction: "recvonly"
})
async function start() {
    const offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    const response = await fetch("/offer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            sdp: pc.localDescription.sdp,
            type: pc.localDescription.type
        })
    })
    const answer = await response.json()
    await pc.setRemoteDescription(answer)
}
start()
</script>
</body>
</html>
"""

app = Flask(__name__)
Bootstrap(app)

pcs = set()

class MediaStreamError(Exception):
    pass

class ScreenTrack(MediaStreamTrack):
    kind = "video"
    VIDEO_PTIME = 0.02
    VIDEO_CLOCK_RATE = 90000
    VIDEO_TIME_BASE = Fraction(1, VIDEO_CLOCK_RATE)
    def __init__(self, fps=30, with_cursor=True):
        super().__init__()

        self.fps = fps

        # Initialize mss for screen capture
        self.sct = mss.mss(with_cursor=with_cursor)
        self.monitor = self.sct.monitors[0]


    async def next_timestamp(self):
       if self.readyState != "live":
           print("live stream error")
           raise MediaStreamError
       if hasattr(self, "_timestamp"):
           self._timestamp += int(self.VIDEO_PTIME * self.VIDEO_CLOCK_RATE)
           wait = self._start + (self._timestamp / self.VIDEO_CLOCK_RATE) - time.time()
           await asyncio.sleep(wait)
       else:
           self._start = time.time()
           self._timestamp = 0
       return self._timestamp, self.VIDEO_TIME_BASE

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        # Grab the screen (this is a fast synchronous call)
        sct_img = self.sct.grab(self.monitor)
        
        # Convert the mss screenshot to a numpy array (it defaults to BGRA)
        img_np = np.array(sct_img)
        
        # Strip the alpha channel to convert BGRA to BGR
        img_bgr = img_np[:, :, :3]

        frame = VideoFrame.from_ndarray(
            img_bgr,
            format="bgr24"
        )

        frame.pts = pts
        frame.time_base = time_base
        return frame

loop = asyncio.new_event_loop()

def start_loop():
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(
    target=start_loop,
    daemon=True
).start()



@app.route('/')
def index():
    return render_template_string(HTML_PAGE)


@app.route('/offer', methods=['POST'])
def offer():
    params = request.json
    future = asyncio.run_coroutine_threadsafe(
        handle_offer(params),
        loop
    )
    result = future.result()
    traceback.print_exc
    return result

  

async def handle_offer(params):
    offer = RTCSessionDescription(
        sdp=params['sdp'],
        type=params['type']
    )

    pc = RTCPeerConnection()

    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state:", pc.connectionState)

        if pc.connectionState in ["failed", "closed"]:
            await pc.close()
            pcs.discard(pc)

    track = ScreenTrack(fps=30)
    pc.addTrack(track)

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()

    await pc.setLocalDescription(answer)

    return json.dumps({
        'sdp': pc.localDescription.sdp,
        'type': pc.localDescription.type
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-p',
        '--port',
        help='port, default 8888',
        type=int,
        default=8888
    )

    parser.add_argument(
        '-s',
        '--https',
        help='enable https',
        action='store_true'
    )

    parser.add_argument(
        '-c',
        '--cert',
        help='certificate file'
    )

    parser.add_argument(
        '-k',
        '--key',
        help='private key file'
    )

    args = parser.parse_args()

    print(f"Starting WebRTC screenshare on port {args.port}")

    if args.https:
        if args.cert and args.key:
            app.run(
                host='0.0.0.0',
                port=args.port,
                threaded=True,
                ssl_context=(args.cert, args.key)
            )
        else:
            app.run(
                host='0.0.0.0',
                port=args.port,
                threaded=True,
                ssl_context='adhoc'
            )
    else:
        app.run(
            host='0.0.0.0',
            port=args.port,
            threaded=True
        )
