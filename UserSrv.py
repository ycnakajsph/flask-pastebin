"""UserSrv

Usage:
	UserSrv.py --port=<int>

Options:
	-h --help     Show this screen.
	--port=<int>  port used

"""
from docopt import docopt
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
import logging


app = Flask(__name__)

@app.route('/isAlive', methods=['GET'])
def isAlive():
	return Response(status=403)

if __name__=='__main__':
	args = docopt(__doc__)
	if args['--port'] :
		app.run(host='0.0.0.0', port=args['--port'])
	else :
		logging.error("Wrong command line arguments")

