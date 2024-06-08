from flask import Flask, jsonify, send_file, request, abort
import qrcode
import io
import time
from datetime import datetime

app = Flask(__name__)

# This function generates the current timestamp in seconds
def get_current_timestamp():
    return int(time.time())

@app.route('/qr')
def qr_code():
    # Generate a URL with a changing parameter based on the current time
    timestamp = get_current_timestamp()
    url = f"http://127.0.0.1:5000/validate?timestamp={timestamp}"
    
    # Generate a QR code for the URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image to a BytesIO object
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@app.route('/validate')
def validate():
    # Get the timestamp from the query parameter
    timestamp = request.args.get('timestamp', type=int)
    print(timestamp)
    # Get the current timestamp
    current_timestamp = get_current_timestamp()
    dt_object = datetime.fromtimestamp(current_timestamp)

    # Check if the QR code has expired (1 second validity)
    if not timestamp or current_timestamp - timestamp > 100:
        return jsonify({"message": "QR code is expired","Currenttime":dt_object,"Qr_Created":datetime.fromtimestamp(timestamp),"difference":current_timestamp-timestamp})
    
    return jsonify({"message": "QR code is valid"})

@app.route('/')
def index():
    # Serve an HTML page that refreshes the QR code every second
    return '''
    <!doctype html>
    <html>
    <head>
        <title>QR Code Refresh</title>
    </head>
    <body>
        <h1>QR Code that changes every second</h1>
        <img id="qr" src="/qr">
        <script>
            setInterval(function() {
                document.getElementById('qr').src = '/qr?' + new Date().getTime();
            }, 1000);
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
