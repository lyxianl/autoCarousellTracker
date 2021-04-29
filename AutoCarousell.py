from Py.Carousell.main import *
from Py.Google.main import *
from Py.Server.main import hostServer
from datetime import datetime
import pandas as pd
import pytz
import time

if __name__ == '__main__':
    if os.getenv('DYNO') and os.get('HOME') == '/app':
        app = hostServer('Automated Carousell DB')
    else:
        app = hostServer()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
