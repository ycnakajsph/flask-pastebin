import unittest
import requests
import shlex

class TestUserSrv(unittest.TestCase):

	TestPort = "99"
	SrvAddr = "127.0.0.1"
	SrvUrl = "http://" + SrvAddr + ":" + TestPort


	def test_launchSrv(self):
		response = requests.get(self.SrvUrl+"/isalive")
		self.assertEqual(response.status_code,200)

if __name__ == '__main__':
	unittest.main()
