# Base58 encode - decode
#
# Author: Chiheb Nexus - 2017
#
# License: GPLv3
#
# More info: https://en.wikipedia.org/wiki/Base58
# 

from binascii import hexlify, unhexlify

class NotValidB58Digits(Exception):
	def __init__(self, char, string):
		Exception.__init__(self, '{0} has an invalid base58 character: {1}'.format(
																			string, char))

class NotValidEncodedDigits(Exception):
	def __init__(self, string):
		Exception.__init__(self, '{0} is not a valid string to be encoded to base58'.format(
																					string))

class Base58:
	def __init__(self):
		self.b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

	def encode(self, var):
		'''Encode Bytes/int/string to padded base58 encoded string'''
		res, czero, pad = [], 0, 0

		if isinstance(var, bytes):
			# Convert bytes into hex then into an integer
			n = int('0x0' + hexlify(var).decode('utf8'), 16)
		elif isinstance(var, int):
			# Convert integer into a bytes
			n, var = var, bytes(str(var), 'utf8')
		elif isinstance(var, str):
			# convert string into an integer
			n = int(''.join(map(str, (ord(k) for k in var))))
		else:
			raise NotValidEncodedDigits(var)

		while n > 0:
			n, r = divmod(n, 58)
			res.append(self.b58_digits[r])

		res_final = ''.join(res[::-1])

		for c in var:
			if c == czero:
				pad += 1
			else:
				break

		return self.b58_digits[0] * pad + res_final


	def decode(self, s=''):
		'''Decode padded base58 encoded string into bytes'''
		if not s:
			return b''

		n = 0
		for c in s:
			n *= 58
			if c not in self.b58_digits:
				raise NotValidB58Digits(c, s)

			digit = self.b58_digits.index(c)
			n += digit

		# Convert n into hex
		h = '{:x}'.format(n)
		if len(h) % 2:
			h = '0' + h

		res = unhexlify(h.encode('utf8'))

		pad = 0
		for c in s[:-1]:
			if c == self.b58_digits[0]:
				pad += 1
			else:
				break

		return b'\x00' * pad + res