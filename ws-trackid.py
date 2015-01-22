#!/usr/bin/env python

DIR = "'/home/anri/Dropbox/Cloudscanspeak/'"
import gevent.monkey
gevent.monkey.patch_all()
import os
from time import sleep,time
from bottle import Bottle, request, abort, route, run
import logging
LOGFILE = '/home/anri/bottle/ws-trackid/ws-trackid.log'
logging.basicConfig(filename = LOGFILE, format = '%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

def get_ices_pid():
	try:
		p = os.popen("ps -ef|grep ices |grep -v grep | awk '{print $2}'")
		return p.readline()[:-1]
	except Exception:
                logging.exception("Unable to detect ices PID")

def get_track(ices_pid):
	try:
		lsof_str = "lsof -p %s | grep %s" %(ices_pid,DIR)
		p = os.popen(lsof_str)	
		track = p.readline()[:-1].split('/')[-1].replace('.mp3','').replace('.MP3','')
		return track
	except Exception:
                logging.exception("Unable to do lsof")

app = Bottle()

@app.route('/websocket')
def handle_websocket():
	wsock = request.environ.get('wsgi.websocket')
	if not wsock:
		abort(400, 'Failed to create WS')
    	logging.info("Client IP: %s connected" %request.remote_addr)
	track_id = ''
	while True:
		try:
			track = get_track(get_ices_pid()) 
			if (track_id.find(track) == -1): 
				track_id = track
			wsock.send(track_id)
		except WebSocketError:
			logging.exception("Exception raised: probably user closed connection")
			break
		sleep(3)

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from geventwebsocket import WebSocketError
if __name__ == "__main__":
	try:		
		server = WSGIServer(("0.0.0.0", 1982), app,handler_class=WebSocketHandler)
		server.serve_forever()
		logging.info("Server initialized")
	except Exception:
		logging.exception("Exception raised:")
	


