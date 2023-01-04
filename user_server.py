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
from flask import request


APP = Flask(__name__)

# can be tested with :
# $ curl -X GET 127.0.0.1:<port>/isalive
@APP.route('/isalive', methods=['GET'])
def is_alive():
	return Response(status=200)

# can be tested with:
# $ curl -v -X POST 127.0.0.1:9009/login -H "Content-Type: application/json"  -d '{"key1":"value1", "key2":"value2"}'
@APP.route('/login', methods=['POST'])
def login():
	json_payload = request.json
	if json_payload is not None:
		print(json_payload)
		return Response(status=200)

	return Response(status=400)

if __name__ == '__main__':
	ARGS = docopt(__doc__)
	if ARGS['--port']:
		APP.run(host='0.0.0.0', port=ARGS['--port'])
	else:
		logging.error("Wrong command line arguments")
