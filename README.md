# Python Flask Pastebin Remake

## Intro

This project is a reimplementation of Pastebin API made using Python3.8, Flask, Sqlite3 and unittest.

The purpose is to show how to write a REST API while keeping the test level high.

## Endpoints

### @APP.route('/isalive', methods=['GET'])

This endpoint only returns 200 when the server is online

### @APP.route('/login', methods=['POST'])

This endpoint is not yet really implemented

### @APP.route('/add/user', methods=['POST'])

This endpoint will add a new user to the database.

See schema : schemas/schemas.py LOGIN_SCHEMA

### @APP.route('/remove/user', methods=['DELETE'])

This endpoint will remove an existing user from the database

See schema : schemas/schemas.py REMOVE_USER_SCHEMA

### @APP.route('/add/user/content', methods=['POST'])

This endpoint will create add a new link to an existing user and stores the content

See schema : schemas/schemas.py ADD_USER_LINK_SCHEMA


