# Test cases of base58
#
# Author : Chiheb Nexus - 2017
# License: GPLv3
#
# Using this website to do tests: https://www.browserling.com/tools/base58-encode
#

import unittest
from base58 import Base58

class TestBase58(unittest.TestCase):
	test_strings_safe = {
			'Cn8eVZg': 'hello',
			'44Wkp8ipFf3nRDj4y2KNa': 'mes salutations',
			'4jJc4sAwPs': 'bitcoin',
			'6XidGdGeMggztM': 'blockchain',
			'wxp9EoXTiX6LZZZb': '27beaf134de2'
	}

	test_strings_not_safe = {
			'Cn8eVZg': 'helllo',
			'44Wkp8ipFf3nRDj4y2KNl': 'mes salutations',
			'4jJc4sAwP': 'bitcoin'
	}

	test_encode_string_safe = {
			'hello': 'Cn8eVZg',
			'mes salutations': '44Wkp8ipFf3nRDj4y2KNa',
			'bitcoin': '4jJc4sAwPs',
			'blockchain': '6XidGdGeMggztM',
			'27beaf134de2': 'wxp9EoXTiX6LZZZb'
	}

	test_encode_string_not_safe = {
			'hello' : 'Cn8eVZf',
			'bitcoins': '44Wkp8ipFf3nRDj4y2KNa',
			'bLockchain': '6XidGdGeMggztM',
			'28beaf134de2': 'wxp9EoXTiX6LZZZb'
	}

	def test_decodage(self):
		for string in self.test_strings_safe:
			self.assertEqual(Base58().decode(string), 
								self.test_strings_safe.get(string).encode())

	def test_decodage2(self):
		for string in self.test_strings_not_safe:
			try:
				self.assertNotEqual(Base58().decode(string), 
									self.test_strings_not_safe.get(string).encode())
			except Exception as e:
				print('\n{0} in test_decodage2: {1}'.format(type(e).__name__, e))

	def test_encodage(self):
		for string in self.test_encode_string_safe:
			self.assertEqual(Base58().encode(string.encode()), 
									self.test_encode_string_safe.get(string))

	def test_encodage2(self):
		for string in self.test_encode_string_not_safe:
			try:
				self.assertNotEqual(Base58().encode(string.encode()),
									self.test_encode_string_not_safe.get(string))
			except Exception as e:
				print('\n{0} in test_encodage2: {1}'.format(type(e).__name__, e))




# Run the tests
if __name__ == '__main__':
	unittest.main()

