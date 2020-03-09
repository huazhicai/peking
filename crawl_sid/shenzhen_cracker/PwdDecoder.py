import json
import os

header = 'fort.agent:'
pwd_index = 300
pwd_length = 32
pwd_byte_width = 3

code_book = None
def decode_pwd(stream, connect_type='ssh'):
	assert connect_type in ('ssh', 'sftp')
	global code_book

	if code_book is None:
		dir_path = os.path.dirname(os.path.realpath(__file__))
		with open(dir_path + '/code_book.json') as f:
			code_book = json.load(f)

	if stream.startswith(header):
		stream = stream[len(header):]

	pwd = []
	for i in range(pwd_length):
		byte = stream[i * pwd_byte_width + pwd_index: i * pwd_byte_width + pwd_index + 3]
		pwd.append(code_book[str(i%4)][byte])

	return ''.join(pwd)



if __name__ == '__main__':
	pwd = decode_pwd('fort.agent:070015022007014054010006021087069001003025028075077085086001003025028075070026010026037031028007009000022027068090087067084088087070072090087068070070010006021054015016008026016026020087069019021027013042019025071068074071072071084088072064084091077069070070031026008029038028010087069018015000029075066093027076078095074066025011024069073093076066077090065019074088031017030080031019072012027071070070030000019013071073009026022042009000030027068085086006009006038006019014023075070015022007013008011017037025022007014087076067074089069090028006011002027027029042010006011001068085014028020013022002020008020016068036045052015036045060015036045036013037019048000085086002019007029026013007024024031087069090028006011001037026010026068')
	print(pwd)