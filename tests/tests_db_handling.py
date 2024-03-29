import unittest
import string
import random
import sqlite3
import os
import re

from pypastebin import db_handling

class TestFuncs(unittest.TestCase):

	test_db = "test_db.db"

	def setUp(self):
		if os.path.isfile(self.test_db):
			os.remove(self.test_db)
		db_handling.CreateDb(self.test_db)

	def tearDown(self):
		if os.path.isfile(self.test_db):
			os.remove(self.test_db)

	def test_CheckUsername(self):
		self.assertFalse(db_handling.CheckUsername("")) # empty
		self.assertFalse(db_handling.CheckUsername("aaa")) # bad size
		self.assertFalse(db_handling.CheckUsername("aaa#")) # good size but special
		self.assertTrue(db_handling.CheckUsername("aaaaa")) # good size
		self.assertTrue(db_handling.CheckUsername("aaaa9a")) # good size with number
		self.assertTrue(db_handling.CheckUsername("aaAa9")) # good size with number and MAJ

	def test_CheckPassword(self):
		self.assertFalse(db_handling.CheckPassword("")) # empty
		self.assertTrue(db_handling.CheckPassword("aAaa#a9aa")) # good size MAJ Special number

		self.assertFalse(db_handling.CheckPassword("aAaa#a9")) # bad size MAJ Special number
		self.assertFalse(db_handling.CheckPassword("aaaa#a9aa")) # good size no MAJ Special number
		self.assertFalse(db_handling.CheckPassword("aAaaaa9aa")) # good size MAJ no Special number
		self.assertFalse(db_handling.CheckPassword("aAaa#aaaa")) # good size MAJ Special no number

	def test_CreateDb(self):
		if os.path.isfile(self.test_db):
			os.remove(self.test_db)
		self.assertTrue(db_handling.CreateDb(self.test_db))
		# Let's check that the created db has all necessary tables and fields
		con = sqlite3.connect(self.test_db)
		cursor = con.execute('select * from USERS')
		names = list(map(lambda x: x[0], cursor.description))
		self.assertIn("username",names)
		self.assertIn("password",names)
		cursor = con.execute('select * from LINKS')
		names = list(map(lambda x: x[0], cursor.description))
		self.assertIn("token",names)
		self.assertIn("content",names)

		self.assertFalse(db_handling.CreateDb(self.test_db)) # verifying we cannot recreate the db

	def test_AddUser(self):
		self.assertFalse(db_handling.AddUser(self.test_db,"aaa","aAaa#a9aa")) # bad username
		self.assertFalse(db_handling.AddUser(self.test_db,"aaaa","")) # bad password
		self.assertTrue(db_handling.AddUser(self.test_db,"aaaa","aAaa#a9aa")) 
		self.assertFalse(db_handling.AddUser(self.test_db,"aaaa","aAaa#a9aa")) # Not supposed to be able to add 2* same user

	def test_UserLogin(self):
		# Let's add a correct user :
		self.assertTrue(db_handling.AddUser(self.test_db,"aaaa","aAaa#a9aa"))
		self.assertTrue(db_handling.CheckUserLogin(self.test_db,"aaaa","aAaa#a9aa"))
		self.assertFalse(db_handling.CheckUserLogin(self.test_db,"aaaa","aAaa#a9a")) # Bad Password
		self.assertFalse(db_handling.CheckUserLogin(self.test_db,"aaab","aAaa#a9aa")) # Bad Username

	def test_GetUser(self):
		self.assertTrue(db_handling.AddUser(self.test_db,"aaaa","aAaa#a9aa"))
		self.assertEquals(db_handling.GetUserLinks(self.test_db, "aaaa"),[])
		self.assertIsNone(db_handling.GetUserLinks(self.test_db, "bbbb"))

	def test_AddLinkUser(self):
		self.assertTrue(db_handling.AddUser(self.test_db,"aaaa","aAaa#a9aa"))
		self.assertTrue(db_handling.AddLinkUser(self.test_db,"aaaa","toto"))
		self.assertEquals(db_handling.GetUserLinks(self.test_db, "aaaa"),["toto"])
		self.assertTrue(db_handling.AddLinkUser(self.test_db,"aaaa",""))
		self.assertEquals(db_handling.GetUserLinks(self.test_db, "aaaa"),["toto",""])

	def test_GetUuidToken(self):
		regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
		uuid_token = db_handling.GetUuidToken()
		match = regex.match(uuid_token) # just checking that we are getting a string like uuid as intended
		self.assertTrue(bool(match))

	def test_RemoveUser(self):
		self.assertTrue(db_handling.AddUser(self.test_db,"aaaa","aAaa#a9aa"))
		self.assertTrue(db_handling.RemoveUser(self.test_db,"aaaa"))

		con = sqlite3.connect(self.test_db)
		cur = con.execute('select * from USERS')
		ret = cur.fetchall()

		self.assertEquals(len(ret),0)

		con.close()

	def test_RemoveUser_NoSuchUser(self):
		self.assertFalse(db_handling.RemoveUser(self.test_db,"aaaa"))

	def test_AddLinkTokenContent(self):
		token = db_handling.GetUuidToken()
		content = "lorem ipsum... blablabla"
		self.assertTrue(db_handling.AddLinkTokenContent(self.test_db, token, content))

		con = sqlite3.connect(self.test_db)
		cur = con.execute('select * from links')
		ret = cur.fetchall()

		self.assertEquals(len(ret),1)
		self.assertEquals(ret[0][0],token)
		self.assertEquals(ret[0][1],content)

		con.close()

		self.assertFalse(db_handling.AddLinkTokenContent(self.test_db, token, content)) # can't have twice the same token

	def test_GetLinkTokenContent(self):
		token = db_handling.GetUuidToken()
		content = "lorem ipsum... blablabla"
		self.assertTrue(db_handling.AddLinkTokenContent(self.test_db, token, content))

		self.assertEqual(db_handling.GetLinkTokenContent(self.test_db, token),content)

		self.assertIsNone(db_handling.GetLinkTokenContent(self.test_db, "bad token"))

	def test_RemoveLinkToken(self):
		token = db_handling.GetUuidToken()
		content = "lorem ipsum... blablabla"
		self.assertTrue(db_handling.AddLinkTokenContent(self.test_db, token, content))

		self.assertTrue(db_handling.RemoveLinkToken(self.test_db, token))

		con = sqlite3.connect(self.test_db)
		cur = con.execute('select * from links')
		ret = cur.fetchall()

		self.assertEquals(len(ret),0)

		con.close()

		self.assertFalse(db_handling.RemoveLinkToken(self.test_db, token)) # can't remove non existing token

	def test_RemoveLinkUser(self):
		self.assertTrue(db_handling.AddUser(self.test_db,"aaaa","aAaa#a9aa"))
		self.assertTrue(db_handling.AddLinkUser(self.test_db,"aaaa","toto"))
		self.assertEquals(db_handling.GetUserLinks(self.test_db, "aaaa"),["toto"])
		self.assertTrue(db_handling.AddLinkUser(self.test_db,"aaaa","tata"))
		self.assertEquals(db_handling.GetUserLinks(self.test_db, "aaaa"),["toto","tata"])

		self.assertTrue(db_handling.RemoveLinkUser(self.test_db,"aaaa","toto"))
		self.assertEquals(db_handling.GetUserLinks(self.test_db, "aaaa"),["tata"])


if __name__ == '__main__':
	unittest.main()
