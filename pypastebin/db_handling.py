import sqlite3
import json
import os
import uuid

def GetUuidToken():
	return str(uuid.uuid4())

def CheckUsername(username):
	if len(username) <= 3:
		return False

	for ch in username:
		if not ch.isalnum():
			return False

	return True

def CheckPassword(password):
	if len(password) < 8:
		return False

	has_spec_char = False
	has_number = False
	has_upper = False
	has_lower = False
	for ch in password:
		if not ch.isalnum():
			has_spec_char = True
		if ch.isnumeric():
			has_number = True
		if ch.isupper():
			has_upper = True
		if ch.islower():
			has_lower = True

	return has_spec_char and has_number and has_upper and has_lower

def CreateDb(db_path):
	# check if file exists if it does return False
	if os.path.isfile(db_path):
		return False
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	cur.execute('''CREATE TABLE users
			(username TEXT NOT NULL UNIQUE ,
			password TEXT NOT NULL,
			link TEXT
			)''')
	con.commit()
	cur.execute('''CREATE TABLE links
			(token TEXT NOT NULL UNIQUE ,
			content TEXT NOT NULL
			)''')
	con.commit()
	con.close()
	return True

def AddUser(db_path, username, password):
	if any([not CheckUsername(username), not CheckPassword(password)]):
		return False
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	try:
		cur.execute("INSERT INTO users VALUES (?,?,?)", (username, password, json.dumps({'links':[]})))
	except sqlite3.IntegrityError: # this means that we failed to insert
		con.close()
		return False
	con.commit()
	con.close()
	return True

def RemoveUser(db_path, username):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	try:
		cur.execute("DELETE FROM users WHERE username=:username", {"username":username})
		con.commit()
		if cur.rowcount == 0: # this means no collumn where affected
			return False
		con.close()
		return True

	except sqlite3.Error: # this means that we failed to insert
		con.close()
		return False

def GetUserLinks(db_path, username):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	try:
		cur.execute("SELECT link FROM users WHERE username=:username", {"username":username})
		ret = cur.fetchall()
		con.close()
		if len(ret) == 0: #that would mean this is a bad user
			return None
		links = ret[0][0]
		links = json.loads(links)
		return links["links"]

	except sqlite3.IntegrityError: # this means that we failed to insert
		con.close()
		return None

def SetLinksUser(db_path, username, links):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	try:
		cur.execute("UPDATE users SET link = ? WHERE username = ?", (json.dumps({'links':links}), username))
	except sqlite3.IntegrityError: # this means that we failed to insert
		con.close()
		return False
	con.commit()
	con.close()
	return True

def AddLinkUser(db_path, username, link):
	links = GetUserLinks(db_path, username)
	if links is not None:
		links.append(link)
		return SetLinksUser(db_path, username, links)
	return False

def RemoveLinkUser(db_path, username, token):
	links = GetUserLinks(db_path, username)
	if links is not None and token in links:
		links.remove(token)
		return SetLinksUser(db_path, username, links)
	return False

def AddLinkTokenContent(db_path, token, content):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	try:
		cur.execute("INSERT INTO links VALUES (?,?)", (token, content))
	except sqlite3.IntegrityError: # this means that we failed to insert
		con.close()
		return False
	con.commit()
	con.close()
	return True

def GetLinkTokenContent(db_path, token):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	try:
		cur.execute("SELECT content FROM links WHERE token=?", (token,))
		ret = cur.fetchall()
		con.close()
		if len(ret) != 1:
			return None
		content = ret[0][0]
		return content

	except sqlite3.IntegrityError:
		con.close()
		return None

def RemoveLinkToken(db_path, token):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	try:
		cur.execute("DELETE FROM links WHERE token=?", (token,))
		con.commit()
		if cur.rowcount == 0: # this means no collumn where affected
			return False
		con.close()
		return True

	except sqlite3.Error: # this means that we failed to insert
		con.close()
		return False


def CheckUserLogin(db_path, username, password):
	con = sqlite3.connect(db_path)
	cur = con.cursor()

	cur.execute("SELECT password FROM users WHERE username=:username", {"username":username})
	ret = cur.fetchall()
	if len(ret) != 1 or password != ret[0][0]:
		con.close()
		return False
	con.close()
	return True

def CheckDbHealth(db_path):
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	cur.execute("SELECT * FROM users")
	ret = cur.fetchall()
	if len(ret) == 0:
		return True # empty Db is healthy..?
	for usr in ret:
		if any([not CheckUsername(usr[0]), not CheckPassword(usr[1])]):
			return False

	return True
