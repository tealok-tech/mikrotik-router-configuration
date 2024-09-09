#!/usr/bin/python3
# -*- coding: latin-1 -*-
import argparse
import binascii
import hashlib
import logging
import select
import socket
import ssl
import sys

from typing import List


LOGGER = logging.getLogger("example")


class ApiRos:
	"Routeros api"

	def __init__(self, sk: socket.socket) -> None:
		self.socket = sk
		self.currenttag = 0

	def login(self, username: str, pwd: str) -> bool:
		for repl, attrs in self.talk(
			["/login", "=name=" + username, "=password=" + pwd]
		):
			if repl == "!trap":
				return False
			elif "=ret" in attrs.keys():
				# for repl, attrs in self.talk(["/login"]):
				chal = binascii.unhexlify((attrs["=ret"]).encode(sys.stdout.encoding))
				md = hashlib.md5()
				md.update(b"\x00")
				md.update(pwd.encode(sys.stdout.encoding))
				md.update(chal)
				for repl2, attrs2 in self.talk(
					[
						"/login",
						"=name=" + username,
						"=response=00"
						+ binascii.hexlify(md.digest()).decode(sys.stdout.encoding),
					]
				):
					if repl2 == "!trap":
						return False
		return True

	def talk(self, words):
		if self.writeSentence(words) == 0:
			return
		r = []
		while 1:
			i = self.readSentence()
			if len(i) == 0:
				continue
			reply = i[0]
			attrs = {}
			for w in i[1:]:
				j = w.find("=", 1)
				if j == -1:
					attrs[w] = ""
				else:
					attrs[w[:j]] = w[j + 1 :]
			r.append((reply, attrs))
			if reply == "!done":
				return r

	def writeSentence(self, words):
		ret = 0
		for w in words:
			self.writeWord(w)
			ret += 1
		self.writeWord("")
		return ret

	def readSentence(self):
		r = []
		while 1:
			w = self.readWord()
			if w == "":
				return r
			r.append(w)

	def writeWord(self, w):
		print(("<<< " + w))
		self.writeLen(len(w))
		self.writeStr(w)

	def readWord(self):
		ret = self.readStr(self.readLen())
		print((">>> " + ret))
		return ret

	def writeLen(self, length: int) -> None:
		if length < 0x80:
			self.writeByte((length).to_bytes(1, sys.byteorder))
		elif length < 0x4000:
			length |= 0x8000
			self.writeByte(((length >> 8) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte((length & 0xFF).to_bytes(1, sys.byteorder))
		elif length < 0x200000:
			length |= 0xC00000
			self.writeByte(((length >> 16) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte(((length >> 8) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte((length & 0xFF).to_bytes(1, sys.byteorder))
		elif length < 0x10000000:
			length |= 0xE0000000
			self.writeByte(((length >> 24) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte(((length >> 16) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte(((length >> 8) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte((length & 0xFF).to_bytes(1, sys.byteorder))
		else:
			self.writeByte((0xF0).to_bytes(1, sys.byteorder))
			self.writeByte(((length >> 24) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte(((length >> 16) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte(((length >> 8) & 0xFF).to_bytes(1, sys.byteorder))
			self.writeByte((length & 0xFF).to_bytes(1, sys.byteorder))

	def readLen(self):
		c = ord(self.readByte())
		# print (">rl> %i" % c)
		if (c & 0x80) == 0x00:
			pass
		elif (c & 0xC0) == 0x80:
			c &= ~0xC0
			c <<= 8
			c += ord(self.readByte())
		elif (c & 0xE0) == 0xC0:
			c &= ~0xE0
			c <<= 8
			c += ord(self.readByte())
			c <<= 8
			c += ord(self.readByte())
		elif (c & 0xF0) == 0xE0:
			c &= ~0xF0
			c <<= 8
			c += ord(self.readByte())
			c <<= 8
			c += ord(self.readByte())
			c <<= 8
			c += ord(self.readByte())
		elif (c & 0xF8) == 0xF0:
			c = ord(self.readByte())
			c <<= 8
			c += ord(self.readByte())
			c <<= 8
			c += ord(self.readByte())
			c <<= 8
			c += ord(self.readByte())
		return c

	def writeStr(self, buffer: str) -> None:
		n = 0
		while n < len(buffer):
			r = self.socket.send(bytes(buffer[n:], "UTF-8"))
			if r == 0:
				raise RuntimeError("connection closed by remote end")
			n += r

	def writeByte(self, buffer: bytes) -> None:
		n = 0
		while n < len(buffer):
			r = self.socket.send(buffer[n:])
			if r == 0:
				raise RuntimeError("connection closed by remote end")
			n += r

	def readByte(self) -> bytes:
		s = self.socket.recv(1)
		if s == b"":
			raise RuntimeError("connection closed by remote end")
		LOGGER.debug(b">>>" + s)
		return s

	def readStr(self, length: int) -> str:
		ret = ""
		LOGGER.debug("length: %i", length)
		while len(ret) < length:
			s = self.socket.recv(length - len(ret))
			if s == b"":
				raise RuntimeError("connection closed by remote end")
			LOGGER.debug(">>> %s", s.decode("UTF-8"))
			ret += s.decode(sys.stdout.encoding, "replace")
		return ret


def open_socket(dst, port: int, secure=False) -> socket.socket | ssl.SSLSocket:
	res = socket.getaddrinfo(dst, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
	af, socktype, proto, canonname, sockaddr = res[0]
	skt = socket.socket(af, socktype, proto)
	if secure:
		secure = ssl.wrap_socket(
			skt, ssl_version=ssl.PROTOCOL_TLSv1_2, ciphers="ECDHE-RSA-AES256-GCM-SHA384"
		)  # ADH-AES128-SHA256
		secure.connect(sockaddr)
		return secure
	skt.connect(sockaddr)
	return skt


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"destination", help="The address of the Mikrotik router to communicate with"
	)
	parser.add_argument(
		"user", default="admin", help="The username to use for authentication"
	)
	parser.add_argument(
		"password", default="", help="The password to authenticate with"
	)
	parser.add_argument(
		"--secure",
		"-s",
		action="store_true",
		help="If present, use a secure connection on port 8729. Otherwise use the default insecure on 8728",
	)
	parser.add_argument(
		"--verbose", "-v", action="store_true", help="If present show verbose logging"
	)
	args = parser.parse_args()

	logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

	s = None
	port = 8729 if args.secure else 8728

	s = open_socket(args.destination, port, args.secure)
	if s is None:
		print("could not open socket")
		sys.exit(1)

	apiros = ApiRos(s)
	if not apiros.login(args.user, args.password):
		return

	inputsentence: List[str] = []

	while 1:
		r = select.select([s, sys.stdin], [], [], None)
		if s in r[0]:
			# something to read in socket, read sentence
			apiros.readSentence()

		if sys.stdin in r[0]:
			# read line from input and strip off newline
			length = sys.stdin.readline()
			length = length[:-1]

			# if empty line, send sentence and start with new
			# otherwise append to input sentence
			if length == "":
				apiros.writeSentence(inputsentence)
				inputsentence = []
			else:
				inputsentence.append(length)


if __name__ == "__main__":
	main()
