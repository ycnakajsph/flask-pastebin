import unittest
import requests
import shlex
import subprocess
import time

class TestUserSrv(unittest.TestCase):

	SrvSubprocess = None

	TestPort = "9009"
	SrvAddr = "127.0.0.1"
	SrvUrl = "http://" + SrvAddr + ":" + TestPort

	def setUp(self):
		cmd = "python user_server.py --port="+self.TestPort
		args = shlex.split(cmd)
		self.SrvSubprocess  = subprocess.Popen(args) # launch command as a subprocess
		time.sleep(3)

	def tearDown(self):
		print("killing subprocess user_server")
		self.SrvSubprocess.kill()
		self.SrvSubprocess.wait()

	def test_launchSrv(self):
		response = requests.get(self.SrvUrl+"/isalive")
		self.assertEqual(response.status_code,200)

	def test_login(self):
		response = requests.post(self.SrvUrl+"/login")
		self.assertEqual(response.status_code,400) #missing json payload

		response = requests.post(self.SrvUrl+"/login",json={"key": "value"})
		self.assertEqual(response.status_code,200) # we accept anything at this stage



if __name__ == '__main__':
	unittest.main()
