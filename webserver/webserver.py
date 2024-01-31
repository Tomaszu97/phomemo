import os
import dotenv
import flask as fl
from print import TextPrinter

dotenv.load_dotenv()
PRINTER_BT_MAC = os.getenv('PRINTER_BT_MAC')
PRINTER_BT_CHAN = os.getenv('PRINTER_BT_CHAN')
app = fl.Flask(__name__)

@app.route('/')
def print_input():
    return fl.render_template('form.html')

@app.route('/', methods=['POST'])
def print_input_post():
    text = fl.request.form['text']

    tp = TextPrinter()
    tp.open(PRINTER_BT_MAC,
            PRITER_BT_CHAN)
    tp.print(text)
    tp.close()

    return fl.render_template('form.html')

app.run(host='0.0.0.0', port=8081)
