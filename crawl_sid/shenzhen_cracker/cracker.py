#-*- coding=utf-8 -*-

import subprocess
import time
import os
import random
import json

header = 'fort.agent:'
pwd_index = 300
pwd_length = 32
pwd_byte_width = 3

valid_sets = '1234567890abcdef'

def random_byte():
	return str(random.randint(0, 50)).rjust(3, '0')

def zero_byte():
	return '000'

SSH = 1
SFTP = 2

def ssh_extract_pwd(lines):
	if len(lines) < 13:
		return None
	return lines[9].strip('\n\r')

def sftp_extract_pwd(lines):
	if len(lines) < 1:
		return None
	return lines[0].strip('\n\r').split('sso:')[1].split('@')[0]

def crack_pos_code_book(stream, pos, crack_type = SSH):
	from os.path import expanduser
	home = expanduser("~")
	target_file = home + '/my_temp_!@#$135_file.txt'
	if os.path.exists(target_file):
		os.remove(target_file)

	code_book = {}

	extract_pwd = ssh_extract_pwd if crack_type == SSH else sftp_extract_pwd
	ori_pwd_stream = stream[pwd_index: pwd_index + pwd_length * pwd_byte_width]

	for i in range(0, 128):
		test_byte = str(i).rjust(3, '0')
		new_pwd_stream = random_byte() * pos + test_byte + random_byte() * (pwd_length - 1 - pos)

		#print('new_pwd_stream', new_pwd_stream)
		new_stream = stream.replace(ori_pwd_stream, new_pwd_stream)

		cmd = 'fort_agent.exe ' + header + new_stream

		subprocess.Popen(cmd)

		begin = time.time()
		pwd = None
		while time.time() - begin < 1:
			if os.path.exists(target_file):
				with open(target_file, encoding='utf-8') as f:
					try:
						lines = f.readlines()
					except UnicodeDecodeError:
						break
					pwd = extract_pwd(lines)
					if pwd is not None:
						time.sleep(0.1)
						break
			time.sleep(0.0001)
		else:
			continue

		os.remove(target_file)
		if pwd and len(pwd) == 32:
			print(i, pwd)
			if pwd[pos] in valid_sets:
				code_book[test_byte] = pwd[pos]
			if len(set(code_book.values())) >= len(valid_sets):
				break

	else:
		raise Exception('can get all code')
	return code_book

def crack_code_book(stream, crack_type):
	code_book = {}
	for i in range(0, 4):
		code_book[i] = crack_pos_code_book(stream, i, crack_type)

	with open('./code_book.json', 'w') as f:
		json.dump(code_book, f)


if __name__  ==  '__main__':
	ssh_stream = '070015022007014054010006021087069001003025028075074085086001003025028075070026010026037031028007009000022027068090087067084088087070072090087068070070010006021054015016008026016026020087069019021027013042019025071068074071072071084088072064084091077069070070031026008029038028010087069018015000029075076092073066030010028022072015064070078080031064024081026067066012064077025013078019072080024068070070030000019013071073009026022042009000030027068085086006009006038006019014023075070015022007013008011017037025022007014087076067074089069090028006011002027027029042010006011001068085014028020013022002020008020016068036045052015036045060015036045036013037019048000085086002019007029026013007024024031087069090028006011001037026010026068'
	sftp_stream = '070015022007014054010006021087069001003025028075077085086001003025028075070026010026037031028007009000022027068090087067084088087070072090087068070070010006021054015016008026016026020087069019021027013042019025071068074071072071084088072064084091077069070070031026008029038028010087069018015000029075066093027076078095074066025011024069073093076066077090065019074088031017030080031019072012027071070070030000019013071073009026022042009000030027068085086006009006038006019014023075070015022007013008011017037025022007014087076067074089069090028006011002027027029042010006011001068085014028020013022002020008020016068036045052015036045060015036045036013037019048000085086002019007029026013007024024031087069090028006011001037026010026068'
	crack_code_book(ssh_stream, SSH)