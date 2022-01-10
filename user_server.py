"""UserSrv

Usage:
	UserSrv.py --port=<int>

Options:
	-h --help     Show this screen.
	--port=<int>  port used

"""
import logging
from docopt import docopt
from flask import Flask
from flask import Response


APP = Flask(__name__)

@APP.route('/isalive', methods=['GET'])
def is_alive():
	return Response(status=200)

if __name__ == '__main__':
	ARGS = docopt(__doc__)
	if ARGS['--port']:
		APP.run(host='0.0.0.0', port=ARGS['--port'])
	else:
		logging.error("Wrong command line arguments")
