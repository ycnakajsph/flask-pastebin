import unittest
import requests
import shlex
import subprocess
import time
import os

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

	# can be tested with :
	# $ curl -X GET 127.0.0.1:<port>/isalive
	def test_launchSrv(self):
		response = requests.get(self.SrvUrl+"/isalive")
		self.assertEqual(response.status_code,200)

	# can be tested with:
	# $ curl -v -X POST 127.0.0.1:9009/login -H "Content-Type: application/json"  -d '{"username":"value1", "password":"value2"}'
	def test_login(self):
		response = requests.post(self.SrvUrl+"/login")
		self.assertEqual(response.status_code,403) #missing json payload

		response = requests.post(self.SrvUrl+"/login",json={"key": "value"})
		self.assertEqual(response.status_code,403) # bad json payload

		response = requests.post(self.SrvUrl+"/login",json={"username":"value1", "password":"value2"})
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
		response = requests.post(self.SrvUrl+"/remove/user",json={"username":"aaaa"})
		self.assertEqual(response.status_code,200)


		response = requests.post(self.SrvUrl+"/remove/user",json={"username":"bbbb"})
		self.assertEqual(response.status_code,400)

	def test_add_user_content(self):
		response = requests.post(self.SrvUrl+"/add/user",json={"username":"aaaa", "password":"aAaa#a9aa"})
		self.assertEqual(response.status_code,200)

		response = requests.post(self.SrvUrl+"/add/user/content",json={"username":"aaaa", "content":"lorem ipsum... blablabla"})
		self.assertEqual(response.status_code,200)

		resp_js = response.json()
		print(resp_js)
		self.assertEqual(resp_js["status"],"ok")
		self.assertIn("link",resp_js)

	def test_add_user_content_bad_user(self):
		response = requests.post(self.SrvUrl+"/add/user/content",json={"username":"aaaa", "content":"lorem ipsum... blablabla"})
		self.assertEqual(response.status_code,400)

if __name__ == '__main__':
	unittest.main()
