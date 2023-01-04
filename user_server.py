"""UserSrv

Usage:
	UserSrv.py --port=<int>

Options:
	-h --help     Show this screen.
	--port=<int>  port used

"""
import logging
from docopt import docopt
from flask import Flask, Response, request, jsonify
from flask_json_schema import JsonSchema, JsonValidationError

APP = Flask(__name__)
SCHEMA = JsonSchema(APP)

@APP.errorhandler(JsonValidationError)
def validation_error(json_error):
	error = { \
		'error': json_error.message, \
		'errors': [validation_error.message for validation_error in json_error.errors] \
	}
	return jsonify(error), 400

@APP.route('/isalive', methods=['GET'])
def is_alive():
	return Response(status=200)

# of course schemas shall go in a separated folder
LOGIN_SCHEMA = { \
	"type" : "object", \
	"required" : ["username", "password"], \
	"properties" : { \
		"username" : {"type" : "string"}, \
		"password" : {"type" : "string"}, \
	}, \
}

@APP.route('/login', methods=['POST'])
@SCHEMA.validate(LOGIN_SCHEMA)
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
