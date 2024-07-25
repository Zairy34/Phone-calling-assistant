import json
from flask import Flask,request
from flask_sock import Sock
from twilio.rest import Client
import os
from dotenv import load_dotenv
import ngrok
import assemblyai as aai
import requests
import time
import json
from threading import Thread
load_dotenv()

#setting our auth tokens
TWILIO_ACCOUNT_SID=os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN=os.getenv('TWILIO_AUTH_TOKEN')
ASSEMBLYAI_API_KEY=os.getenv('ASSEMBLYAI_API_KEY')
NGROK_AUTH_TOKEN=os.getenv('NGROK_AUTH_TOKEN')
TWILIO_NUMBER=os.getenv('TWILIO_NUMBER')

#settings our additional parameters
PORT = 5000
DEBUG = False
aai.settings.api_key = ASSEMBLYAI_API_KEY
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
WEBSOCKET_ROUTE = '/realtime'
OUTBOUND_CALL_ROUTE = '/'

#creating intances 
app = Flask(__name__)
sock = Sock(app)



@app.route('/',methods=["GET","POST"])
def outbound_call():
    
        print(f"Attempting to call :   ")
    
        xml = f"""
        <Response>
            <Say>Hello, this is ALI asif from AB world wide we specializein stock marketing tell me how may i help you.</Say>
            <Connect>
                <Stream url='wss://{request.host}{WEBSOCKET_ROUTE}'/>
            </Connect>
        </Response>
        """.strip()
        try:
            call = client.calls.create(
                twiml=xml,
                to='+1 631 464 0209',
                from_=TWILIO_NUMBER  # Use the Twilio number from environment variables
            )
            print(f"Call created successfully. SID: {call.sid}")
            return str(call.sid)
        except Exception as e:
            print(f"Error creating call: {str(e)}")
            return f"Error: {str(e)}", 500
    # else:
    #     return  f"Real-time phone call transcription app"


@sock.route(WEBSOCKET_ROUTE)
def transcription_websocket(ws):
    while True:
        data = json.loads(ws.receive())
        match data['event']:
            case "connected":
                print('twilio connected')
            case "start":
                print('twilio started')
            case "media":
                payload = data['media']['payload']
                print(payload)
            case "stop":
                print('twilio stopped')





if __name__ == "__main__":
    
    try:
        listener = ngrok.forward(f"http://localhost:{PORT}")
        print(f"Ngrok tunnel opened at {listener.url()} for port {PORT}")
        NGROK_URL = listener.url()
        
        #app.run(port=PORT,debug=DEBUG)

        # Start Flask app
        flask_thread = Thread(target=lambda: app.run(port=PORT, debug=DEBUG, use_reloader=False))
        flask_thread.start()

        # Give Flask a moment to start up
        #time.sleep(2)

        # Make a test call
        test_number = "+1 631 464 0209"  # Replace with the number you want to call
        response = requests.post(f"{NGROK_URL}{OUTBOUND_CALL_ROUTE}", json={'to': test_number})
        print(f"Call attempt response: {response.text}")

        # Keep the main thread alive
        while True:
             time.sleep(1)
    except KeyboardInterrupt:
              print("Shutting down...")
    finally:
        # Always disconnect the ngrok tunnel
             ngrok.disconnect()
     