from flask import Flask, jsonify, request
import RPi.GPIO as GPIO

app = Flask(__name__)

GPIO.setmode(GPIO.BCM) 

pins = {
    2: {'name': 'Pin 2', 'state': GPIO.LOW},
    3: {'name': 'Pin 3', 'state': GPIO.LOW}
}

flashing_threads = {}

def flash_pin(pin, interval, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(interval)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(interval)
    GPIO.output(pin, GPIO.LOW)


for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, pins[pin]['state'])

@app.route('/gpio/<int:pin>/on', methods=['POST'])
def turn_on(pin):
    if pin in pins:
        GPIO.output(pin, GPIO.HIGH)
        pins[pin]['state'] = GPIO.HIGH
        return jsonify({pin: 'on'})
    return jsonify({'error': 'Invalid pin'}), 400

@app.route('/gpio/<int:pin>/off', methods=['POST'])
def turn_off(pin):
    if pin in pins:
        GPIO.output(pin, GPIO.LOW)
        pins[pin]['state'] = GPIO.LOW
        return jsonify({pin: 'off'})
    return jsonify({'error': 'Invalid pin'}), 400

@app.route('/gpio/status', methods=['GET'])
def status():
    return jsonify(pins)

@app.route('/gpio/<int:pin>/status', methods=['GET'])
def pin_status(pin):
    if pin in pins:
        return jsonify({pin: 'on' if pins[pin]['state'] == GPIO.HIGH else 'off'})
    return jsonify({'error': 'Invalid pin'}), 400

@app.route('/gpio/<int:pin>/setup', methods=['POST'])
def setup_pin(pin):
    if pin not in pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        pins[pin] = {'name': f'Pin {pin}', 'state': GPIO.LOW}
        return jsonify({pin: 'setup'})
    return jsonify({'error': 'Pin already setup'}), 400

@app.route('/gpio/<int:pin>/cleanup', methods=['POST'])
def cleanup_pin(pin):
    if pin in pins:
        GPIO.cleanup(pin)
        del pins[pin]
        return jsonify({pin: 'cleanup'})
    return jsonify({'error': 'Invalid pin'}), 400

@app.route('/gpio/<int:pin>/flash', methods=['POST'])
def flash(pin):
    if pin not in pins:
        return jsonify({'error': 'Invalid pin'}), 400

    data = request.json
    interval = data.get('interval', 1.0) 
    duration = data.get('duration', 10.0) 

    if pin in flashing_threads:
        flashing_threads[pin].do_run = False
        flashing_threads[pin].join()

    thread = threading.Thread(target=flash_pin, args=(pin, interval, duration))
    thread.do_run = True
    thread.start()
    flashing_threads[pin] = thread

    return jsonify({pin: 'flashing', 'interval': interval, 'duration': duration})

@app.route('/gpio/<int:pin>/stop_flash', methods=['POST'])
def stop_flash(pin):
    if pin in flashing_threads:
        flashing_threads[pin].do_run = False
        flashing_threads[pin].join()
        del flashing_threads[pin]
        GPIO.output(pin, GPIO.LOW)
        pins[pin]['state'] = GPIO.LOW
        return jsonify({pin: 'flash stopped'})
    return jsonify({'error': 'No flashing thread for pin'}), 400

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Server stopped and GPIO cleaned up.")
