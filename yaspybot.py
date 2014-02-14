#!/usr/bin/python3

import socket
from os import linesep

COMMANDPREFIX = ':'
HOST = 'irc.freenode.net'
PORT = 6667
PASSWORD = ''
NICK = 'yaspybot'
CHANNELS = '#yaspybot'
IPV6 = False

class yaspybot(object):
	
	def __init__(self, host, port, password, nick, channels, ipv6 = False):
		if ipv6:
			self._socket = socket.socket(socket.AF_INET6)
		else:
			self._socket = socket.socket()
		self._socket.connect((host, port))
		self._send_command('PASS %s' % password)
		self._send_command('USER %s %s %s :This is retarded.' % (nick, nick, nick))
		self._send_command('NICK %s' % nick)
		for channel in channels:
			self._send_command('JOIN %s' % channel)
		_buffer = ''
		
		while True:
			_buffer += self._socket.recv(2048).decode()
			lines = _buffer.split('\r\n')
			if lines[0] == '':
				continue
			if lines[len(lines) - 1] != '':
				_buffer = lines[len(lines) - 1]
				to = len(lines) - 2
			else:
				_buffer = ''
				to = len(lines) - 1
			for line in lines[:to]:
				print(line)
				if line.startswith('PING'):
					self._send_command('PONG ' + line.split(':')[1])
				else:
					self._process_line(line)

	def _send_command(self, string):
		self._socket.send((string + '\r\n').encode('utf-8'))
		print(string)

	def _say(self, string, channel):
		self._send_command('PRIVMSG %s :%s' % (channel, string))

	def _process_line(self, line):
		try:
			who = line[1:line.index('!')]
			where = line[line.index(' PRIVMSG ') + 9:line.index(' :')]
			what = line[line.index(' :') + 2:]
		except:
			return
		
		if where == NICK:
			where = who
		
		self._check_for_hook(who, where, what)
		if what.startswith(COMMANDPREFIX):
			self._command(who, where, what[1:])

	def _command(self, who, where, what):
		if what.startswith('unicode '):
			try:
				arg = int(what[8:], 16)
			except:
				self._say('%s: \'%s\' is not valid hex.' % (who, what[8:]), where)
				return
			if arg in range(0x0, 0x110000):
				if arg in range(0xD800, 0xDFFF):
					self._say('%s: \'%s\' is a lone surrogate and can not be printed seperately.' % (who, hex(arg)), where)
					return
				self._say('%s: %s' % (who, chr(arg)), where)
			else:
				self._say('%s: \'%s\' is not a valid unicode codepoint.' % (who, hex(arg)), where)

	def _check_for_hook(self, who, where, what):
		pass
		
if __name__ == '__main__':
	HOST = 'irc.freenode.net'
	PORT = 6667
	NICK = 'yaspybot'
	CHANNELS = '#yaspybot','##aufschrei'
	PASSWORD = ''
	yaspybot(HOST, PORT, PASSWORD, NICK, CHANNELS, IPV6)
	
