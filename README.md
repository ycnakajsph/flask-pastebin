# Python Flask Pastebin Remake

## Intro

This project is a reimplementation of Pastebin API made using Python3.8, Flask, Sqlite3 and unittest.

The purpose is to show how to write a REST API while keeping the test level high.

It will use a very simple stupid auth mecanism to show case the use of cookies and decorator in Flask.

## Endpoints

### @APP.route('/isalive', methods=['GET'])

This endpoint only returns 200 when the server is online

### @APP.route('/login', methods=['POST'])

This endpoint takes a username and password and let a auth cookie containing a userid

Nothing is encrypted and password are stored as are in database

See schema : schemas/schemas.py LOGIN_SCHEMA

### @APP.route('/add/user', methods=['POST'])

This endpoint will add a new user to the database.

See schema : schemas/schemas.py LOGIN_SCHEMA

### @APP.route('/remove/user', methods=['DELETE'])

This endpoint will remove an existing user from the database

See schema : schemas/schemas.py REMOVE_USER_SCHEMA

### @APP.route('/add/user/content', methods=['POST'])

This endpoint will create add a new link to a logged in user and stores the content

See schema : schemas/schemas.py ADD_USER_LINK_SCHEMA

### @APP.route('/remove/user/link', methods=['DELETE'])

This endpoint will remove a link of a logged in user. It will also remove the content associated.

See schema : schemas/schemas.py REMOVE_USER_LINK_SCHEMA

### @APP.route('/get/link', methods=['GET'])

This endpoint will return the content of a link.

See schema : schemas/schemas.py GET_LINK_SCHEMA

## Testing

### Server Testing

test_user_server.py are a set of tests that will trigger the various endpoints and the associated errors.

It is based on unittest and rely on requests module to act as a client.

In order to perform the integration test, a server is launched with a fresh database in SetUp, the server is killed and the database removed in TearDown.

To run the tests :
```
$ nose2
```

To run individual test:
```
$ nose2 test_user_server.TestUserSrv.<test_name>
```
for instance :
```
$ nose2 test_user_server.TestUserSrv.test_remove_user_link_no_auth
```

### DataBase and tooling Testing

The tests are based on unittest and will mostly perform action on the db.

The purpose is to be sure that all sqlite3 command to what is intended.

To run the tests:
```
nose2 tests.tests_db_handling
```

### Linter

This project uses pylint in order to keep a certain level of quality.

```
$ pylint pypastebin/db_handling.py 
$ pylint user_server.py
```