from flask import Flask, jsonify, request
import RPi.GPIO as GPIO

app = Flask(__name__)

GPIO.setmode(GPIO.BCM) 

pins = {
    17: {'name': 'Pin 17', 'state': GPIO.LOW},
    18: {'name': 'Pin 18', 'state': GPIO.LOW}
}

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

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Server stopped and GPIO cleaned up.")
