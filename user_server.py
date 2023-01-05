"""UserSrv

Usage:
	UserSrv.py --port=<int> --db=<path_to_database>

Options:
	-h --help     Show this screen.
	--port=<int>  port used
	--db=<path_to_database> path to the database

"""
import os
import logging
from docopt import docopt
from flask import Flask, Response, request, jsonify
from flask_json_schema import JsonSchema, JsonValidationError
from pypastebin import db_handling

APP = Flask(__name__)
SCHEMA = JsonSchema(APP)

def send_status(status, msg, code):
	return jsonify({"status": status, "msg":msg}), code

@APP.errorhandler(JsonValidationError)
def validation_error(json_error):
	error = { \
		'error': json_error.message, \
		'errors': [validation_error.message for validation_error in json_error.errors] \
	}
	return jsonify(error), 403

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

@APP.route('/add/user', methods=['POST'])
@SCHEMA.validate(LOGIN_SCHEMA)
def add_user():
	json_payload = request.json
	if json_payload is not None:
		ret = db_handling.AddUser(DATABASE_PATH, json_payload["username"], json_payload["password"])
		if not ret:
			return send_status("error", "failed to create user", 400)
		return send_status("ok", "created user "+json_payload["username"], 200)
	return Response(status=400)

REMOVE_USER_SCHEMA = { \
	"type" : "object", \
	"required" : ["username"], \
	"properties" : { \
		"username" : {"type" : "string"}, \
	}, \
}

@APP.route('/remove/user', methods=['POST'])
@SCHEMA.validate(REMOVE_USER_SCHEMA)
def remove_user():
	json_payload = request.json
	if json_payload is not None:
		ret = db_handling.RemoveUser(DATABASE_PATH, json_payload["username"])
		if not ret:
			return send_status("error", "failed to remove user "+json_payload["username"], 400)
		return send_status("ok", "removed user "+json_payload["username"], 200)
	return Response(status=400)

ADD_USER_LINK_SCHEMA = { \
	"type" : "object", \
	"required" : ["username", "content"], \
	"properties" : { \
		"username" : {"type" : "string"}, \
		"content" : {"type" : "string"}, \
	}, \
}

@APP.route('/add/user/content', methods=['POST'])
@SCHEMA.validate(ADD_USER_LINK_SCHEMA)
def add_user_content():
	json_payload = request.json
	if json_payload is not None:
		token = db_handling.GetLinkToken()
		ret = db_handling.AddLinkUser(DATABASE_PATH, json_payload["username"], token)
		if not ret:
			return send_status("error", "failed to add content to user "+json_payload["username"], 400)

		ret = db_handling.AddLinkTokenContent(DATABASE_PATH, token, json_payload["content"])
		if not ret:
			return send_status("error", "failed to add content to user "+json_payload["username"], 400)

		return jsonify({"status": "ok", "msg":"added content to user "+json_payload["username"], "link":token}), 200
	return Response(status=400)

REMOVE_USER_LINK_SCHEMA = { \
	"type" : "object", \
	"required" : ["username", "link"], \
	"properties" : { \
		"username" : {"type" : "string"}, \
		"link" : {"type" : "string"}, \
	}, \
}

@APP.route('/remove/user/link', methods=['POST'])
@SCHEMA.validate(REMOVE_USER_LINK_SCHEMA)
def remove_user_link():
	json_payload = request.json
	if json_payload is not None:
		ret = db_handling.RemoveLinkUser(DATABASE_PATH, json_payload["username"], json_payload["link"])
		if not ret:
			return send_status("error", "failed to remove link "+json_payload["link"]+" from user "+json_payload["username"], 400)
		ret = db_handling.RemoveLinkToken(DATABASE_PATH, json_payload["link"])
		if not ret:
			return send_status("error", "failed to remove link "+json_payload["link"]+" from user "+json_payload["username"], 400)
		return send_status("ok", "removed link "+json_payload["link"]+" from user "+json_payload["username"], 200)
	return Response(status=400)

if __name__ == '__main__':
	ARGS = docopt(__doc__)
	if ARGS['--port'] and ARGS['--db']:
		DATABASE_PATH = ARGS['--db']
		if not os.path.isfile(DATABASE_PATH):
			db_handling.CreateDb(DATABASE_PATH)
		APP.run(host='0.0.0.0', port=ARGS['--port'])
	else:
		logging.error("Wrong command line arguments")
