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

	def test_GetLinkToken(self):
		regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z', re.I)
		uuid_token = db_handling.GetLinkToken()
		match = regex.match(uuid_token) # just checking that we are getting a string like uuid as intended
		self.assertTrue(bool(match))

if __name__ == '__main__':
	unittest.main()
