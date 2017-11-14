# Generate Bitcoin addresses
#
# Author: Chiheb Nexus - 2017
#
# License: GPLv3
#
# More info: 
#   https://www.coindesk.com/math-behind-bitcoin/
#	https://github.com/jgarzik/python-bitcoinlib/blob/master/bitcoin/base58.py
#	https://en.bitcoin.it/wiki/Wallet_import_format
#	http://bitcoin.stackexchange.com/questions/8057/how-do-i-get-the-public-bitcoin-address-from-a-given-private-key-in-wallet-impor
# 	https://en.bitcoin.it/wiki/List_of_address_prefixes
#   http://chimera.labs.oreilly.com/books/1234000001802/ch04.html#_implementing_keys_and_addresses_in_python
#   http://zeltsinger.com/2016/07/18/keys/

from os import urandom
from hashlib import sha256
from binascii import hexlify, unhexlify
from base58 import Base58
import ecdsa
import hashlib

class PrivKeyNotBytes(Exception):
	def __init__(self, priv):
		Exception.__init__(self, '{0} is not a valid bytes'.format(repr(priv)))

class PrivKeySuperiorToN(Exception):
	def __init__(self, priv):
		Exception.__init__(self, '{0} is superior to N'.format(repr(priv)))

class NotSupportedPrivKeyType(Exception):
	def __init__(self, priv):
		Exception.__init__(self, 'Not supported private key type: {0}'.formar(repr(priv)))

class NotSupportedPrefix(Exception):
	def __init__(self, msg):
		Exception.__init__(self, '{0} prefix is not supported for now'.format(repr(msg)))

class GenerateBTCAddresses:
	def __init__(self):
		self.private_prefixes = {
				'WIF': {'prefix': '80', 'name': 'Private Key uncompressed'},
				'cWIF': {'prefix': '80', 'name': 'Private Key compressed'},
				'BIP32Private': {'prefix': '0488ade4', 'name': 'BIP32 private key'},
				'tWIF': {'prefix': 'ef', 'name': 'Testnet Private Key uncompressed'},
				'tcWIF': {'prefix': 'ef', 'name': 'Testnet Private Key compressed'},			
				'tBIP32Private': {'prefix': '04358394', 'name': 'Testnet BIP32 private key'}
		}

		self.public_prefixes = {
				'P2PKH': {'prefix': '00', 'name': 'Pubkey Hash'},
				'P2SH': {'prefix': '05', 'name': 'Script Hash'},
				'BIP32Public': {'prefix': '0488b21e', 'name': 'BIP32 pubkey'},
				'tP2PKH': {'prefix': '6f', 'name': 'Testnet pubkey'},
				'tP2SH': {'prefix': 'c4', 'name': 'Testnet Script Hash'},
				'tBIP32Public': {'prefix': '043587cf', 'name': 'Testnet BIP32 pubkey'},
		}

		self.N = 115792089237316195423570985008687907852837564279074904382605163141518161494337

	def get_prefix(self, p_type, compressed=False):
		'''Get public and private keys prefixes'''
		if p_type == 'mainnet_1':
			return self.private_prefixes['WIF']['prefix'], self.public_prefixes['P2PKH']['prefix']
		elif p_type == 'mainnet_2':
			return self.private_prefixes['WIF']['prefix'], self.public_prefixes['P2SH']['prefix']
		elif p_type == 'testnet_1':
			return self.private_prefixes['tWIF']['prefix'], self.public_prefixes['tP2PKH']['prefix']
		elif p_type == 'testnet_2':
			return self.private_prefixes['tWIF']['prefix'], self.public_prefixes['tP2SH']['prefix']
		else:
			raise NotSupportedPrefix(p_type)


	def get_decoded_priv_key(self, privkey=b'', num=32):
		''' Return string decoded private key '''
		if not isinstance(privkey, bytes):
			raise PrivKeyNotBytes(privkey)

		if not privkey:
			while True:
				priv_hex = hexlify(urandom(num)).decode('utf8')
				priv_int = int(priv_hex, 16)
				if 0 < priv_int < self.N:
					return priv_hex
		else:
			priv_hex = hexlify(privkey).decode('utf8')
			priv_int = int(priv_hex, 16)
			if 0 < priv_int < self.N:
				return priv_hex
			else:
				raise PrivKeySuperiorToN(privkey)

	def priv_to_wif(self, privkey=b'', p_type='WIF', compressed=False, verbose=False):
		prefix, _ = self.get_prefix(p_type)
		if not prefix:
			raise NotSupportedPrivKeyType(p_type)

		privkey = self.get_decoded_priv_key(privkey=privkey)
		step1 = prefix + hex(int(privkey, 16))[2:].strip('L').zfill(64)
		if compressed:
			step1 += '01'
		# First sha256 hash
		step2 = sha256(unhexlify(step1)).hexdigest()
		# Second sha256 hash
		step3 = sha256(unhexlify(step2)).hexdigest()
		# step1 + first 4 bytes from step1 (8 digits) then convert into int (hex -> int) 
		step4 = int(step1 + step3[:8] , 16)
		step5 = Base58().encode(step4)

		if verbose:
			from pprint import pprint
			pprint({
				'Prefix': prefix,
				'Compressed': compressed,
				'Private key': privkey,
				p_type: step5 
				}, indent=2)

		return privkey, step5

	def priv_to_public(self, privkey, compress=False):
		sk = ecdsa.SigningKey.from_string(bytes.fromhex(privkey), curve=ecdsa.SECP256k1)
		vk = sk.get_verifying_key()
		prefix = b'04' if not compress else ( b'03' if vk.pubkey.point.y() % 2 == 1 else b'02' )
		return prefix + ( b'%032x' % vk.pubkey.point.x() if compress else hexlify(sk.to_string()))

	def make_public_address(self, pubkey, p_type='WIF', verbose=False):
		'''Return public address'''
		_, prefix = self.get_prefix(p_type)
		rmd = hashlib.new('ripemd160')
		rmd.update(hashlib.sha256(unhexlify(pubkey)).digest())
		hashed_pubkey = bytes(prefix, 'utf8') + hexlify(rmd.digest())
		checksum = hexlify(hashlib.sha256(hashlib.sha256(unhexlify(hashed_pubkey)).digest()).digest()[:4])
		binary_addr = unhexlify(hashed_pubkey + checksum)
		final_btc_address = Base58().encode(binary_addr)

		if verbose:
			from pprint import pprint
			pprint({
				'pubkey': pubkey,
				'hashed_pubkey': hashed_pubkey,
				'Bitcoin public address': final_btc_address
				}, indent=2)

		return final_btc_address


# Test:
if __name__ == '__main__':
	from pprint import pprint
	keys = []
	p_types = [
			('mainnet_1', False),
			('mainnet_1', True),
			('mainnet_2', False),
			('mainnet_2', True),
			('testnet_1', False),
			('testnet_1', True),
			('testnet_2', False),
			('testnet_2', True)	
	]

	app = GenerateBTCAddresses()
	for p_type, compressed in p_types:
		a, b = app.priv_to_wif(p_type=p_type, verbose=False, compressed=compressed)
		c = app.priv_to_public(a, compress=compressed)
		d = app.make_public_address(c, p_type=p_type, verbose=False)
		keys.append({
			'Private key': a,
			p_type: b,
			'Public address': d,
			'Compressed': compressed
			})

	pprint(keys, indent=2)

