import os
from dotenv import dotenv_values
import flask as fl
from print import TextPrinter

config = dotenv_values('.env')
app = fl.Flask(__name__)

@app.route('/')
def print_input():
    return fl.render_template('form.html')

@app.route('/', methods=['POST'])
def print_input_post():
    global config
    text = fl.request.form['text']
    tp = TextPrinter()
    mac = config['PRINTER_BT_MAC']
    chan = config['PRINTER_BT_CHAN']
    tp.open(mac, int(chan))
    tp.print(text)
    tp.close()
    return fl.render_template('form.html')

app.run(host='0.0.0.0', port=8081)
