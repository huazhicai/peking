"""
生成codebook步骤
1、复制SecureCRT.EXE、WinSCP.exe到fort_sso对应目录替换对应exe，注意备份原文件
2、ie浏览器手动ssh、sftp连接服务器，在弹出的对话框中得到对应的十进制编码串
3、将编码串替换掉cracker.py的ssh_stream和sftp_stream。
4、运行cracker.py，生成code_book;
"""