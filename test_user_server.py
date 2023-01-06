import unittest
import requests
import shlex
import subprocess
import time
import os
import re

from user_server import isUserIdLoggedIn, LogedInUserId

class TestUserSrv(unittest.TestCase):

	SrvSubprocess = None

	TestPort = "9009"
	SrvAddr = "127.0.0.1"
	SrvUrl = "http://" + SrvAddr + ":" + TestPort
	test_db = "test_db.db"

	def setUp(self):
		cmd = "python user_server.py --port="+self.TestPort+" --db="+self.test_db
		args = shlex.split(cmd)
		self.SrvSubprocess  = subprocess.Popen(args) # launch command as a subprocess
		time.sleep(1)

	def tearDown(self):
		print("killing subprocess user_server")
		self.SrvSubprocess.kill()
		self.SrvSubprocess.wait()
		if os.path.isfile(self.test_db):
			os.remove(self.test_db)

	def test_isUserIdLoggedIn(self):
		self.assertFalse(isUserIdLoggedIn("toto"))
		LogedInUserId.append("toto")
		self.assertTrue(isUserIdLoggedIn("toto"))

	# can be tested with :
	# $ curl -X GET 127.0.0.1:<port>/isalive
	def test_launchSrv(self):
		response = requests.get(self.SrvUrl+"/isalive")
		self.assertEqual(response.status_code,200)

	def test_add_user(self):
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,400) # can't add twice the same user
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"bbbb", "password":"a"})
		self.assertEqual(response.status_code,400) # can't add a bad user/password couple

	def test_remove_user(self):
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)
		response = requests.delete(self.SrvUrl+"/remove/user",json={"username":"aaaa"})
		self.assertEqual(response.status_code,200)

		response = requests.delete(self.SrvUrl+"/remove/user",json={"username":"bbbb"})
		self.assertEqual(response.status_code,400)

	# can be tested with:
	# $ curl -v -X POST 127.0.0.1:9009/login -H "Content-Type: application/json"  -d '{"username":"value1", "password":"value2"}'
	def test_login(self):
		response = requests.post(self.SrvUrl+"/login")
		self.assertEqual(response.status_code,403) #missing json payload

		response = requests.post(self.SrvUrl+"/login",json={"key": "value"})
		self.assertEqual(response.status_code,403) # bad json payload

		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)

		session = requests.Session()

		response = session.post(self.SrvUrl+"/login",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)

		cookies = session.cookies.get_dict()
		self.assertIn("userid",cookies)

		regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
		match = regex.match(cookies["userid"]) # just checking that we are getting a string like uuid as intended
		self.assertTrue(bool(match))

		response = requests.post(self.SrvUrl+"/login",json={"username":"bbbb", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,400)

	def test_add_user_content(self):
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)

		response = requests.post(self.SrvUrl+"/add/user/content",json={"username":"aaaa", "content":"lorem ipsum... blablabla"})
		self.assertEqual(response.status_code,200)

		resp_js = response.json()
		self.assertEqual(resp_js["status"],"ok")
		self.assertIn("link",resp_js)

	def test_add_user_content_bad_user(self):
		response = requests.post(self.SrvUrl+"/add/user/content",json={"username":"aaaa", "content":"lorem ipsum... blablabla"})
		self.assertEqual(response.status_code,400)

	def test_remove_user_link(self):
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)

		response = requests.post(self.SrvUrl+"/add/user/content",json={"username":"aaaa", "content":"lorem ipsum... blablabla"})
		self.assertEqual(response.status_code,200)
		resp_js = response.json()

		link = resp_js["link"]
		response = requests.delete(self.SrvUrl+"/remove/user/link",json={"username":"aaaa", "link":link})
		self.assertEqual(response.status_code,200)

		response = requests.delete(self.SrvUrl+"/remove/user/link",json={"username":"aaaa", "link":link})
		self.assertEqual(response.status_code,400) # can't remove unexisting link
		response = requests.delete(self.SrvUrl+"/remove/user/link",json={"username":"bbbb", "link":link})
		self.assertEqual(response.status_code,400) # can't remove unexisting user

	def test_get_link(self):
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)
		txt = "lorem ipsum... blablabla"

		response = requests.post(self.SrvUrl+"/add/user/content",json={"username":"aaaa", "content":txt})
		self.assertEqual(response.status_code,200)
		resp_js = response.json()

		link = resp_js["link"]

		response = requests.get(self.SrvUrl+"/get/link",json={"link":link})
		self.assertEqual(response.status_code,200)
		resp_js = response.json()
		content = resp_js["content"]

		self.assertEqual(content,txt)

		response = requests.get(self.SrvUrl+"/get/link",json={"link":"whatever"})
		self.assertEqual(response.status_code,400)


	def test_add_content(self):
		txt = "lorem ipsum... blablabla"
		response = requests.post(self.SrvUrl+"/add/content",json={"content":txt})
		self.assertEqual(response.status_code,200)

		resp_js = response.json()
		self.assertEqual(resp_js["status"],"ok")
		self.assertIn("link",resp_js)

		link = resp_js["link"]

		response = requests.get(self.SrvUrl+"/get/link",json={"link":link})
		self.assertEqual(response.status_code,200)
		resp_js = response.json()
		content = resp_js["content"]

		self.assertEqual(content,txt)

if __name__ == '__main__':
	unittest.main()
