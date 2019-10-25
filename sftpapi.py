import os
import paramiko
#import logging

from appPublic.Singleton import SingletonDecorator

"""
#logon without password

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname='bsppo.com',username='ymq')
stdin, stdout, stderr = client.exec_command('ls')
for line in stdout:
    print('... ' + line.strip('\n'))
client.close()
"""

class SFTPapi:
	def __init__(self,host,user,local_root,remote_root,port=22):
		self.host = host
		self.user = user
		self.port = port
		self.local_root = local_root
		self.remote_root = remote_root
		self.client = None
		self.connect()
		FORMAT = '%(asctime)-15s %(host)s %(user)s %(port)d %(rroot):%(message)s'
		#logging.basicConfig(format=FORMAT)
		#self.logger = logging.getLogger('sftpapi')

	def info(self,msg):
		#self.logger.info(msg,extra=self.apiinfo)
		print(msg)

	def apiinfo(self):
		return {
			'host':self.host,
			'user':self.user,
			'port':self.port,
			'rroot':self.remote_root,
			'lroot':self.local_root
		}

	def connect(self):
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.client.connect(hostname=self.host,
				port=self.port,
				username=self.user)
		self.sftp = paramiko.SFTPClient.from_transport(self.client._transport)

	def close(self):
		try:
			self.client.close()
		except:
			pass
		self.client = None

	def filel2r(self,lfile):
		if not lfile.startswith(self.local_root):
			lfile = self.local_root+lfile
		f = os.path.abspath(lfile)
		if not f.startswith(self.local_root):
			raise Exception(f'({f} out of root folder')
		return self.remote_root + f[len(self.local_root):]

	def filer2l(self,rfile):
		if not rfile.startswith(self.remote_root):
			rfile = self.remote_root + rfile
		f = os.path.abspath(rfile)
		if not f.startswith(self.remote_root):
			raise Exception(f'{f} out of root folder')
		return self.local_root + f[len(self.remote_root):]

	def newfolder(self,lpath):
		rpath = self.filel2r(lpath)
		self.info(f'newfolder():{lpath}:{rpath}')
		self.sftp.mkdir(rpath)

	def delfolder(self,lpath):
		rpath = self.filel2r(lpath)
		self.info(f'delfolder(),{lpath}:{rpath}')
		self.client.exec_command('rm -rf ' + rpath)

	def delfile(self,lfile):
		rfile = self.filel2r(lfile)
		self.info(f'delfile(),{lfile},{rfile}')
		self.sftp.remove(rfile)

	def copy2(self,lfile):
		rfile = self.filel2r(lfile)
		self.info(f'copy2(),{lfile} -> {rfile}')
		self.sftp.put(lfile,rfile)

	def copyfrom(self,rfile):
		lfile = self.filel2r(rfile)
		self.info(f'copy2(),{rfile} -> {lfile}')
		self.sftp.get(rfile,lfile)

	def move(self,ofile,nfile):
		oldf = self.filel2r(ofile)
		newf = self.filel2r(nfile)
		if ofile.startswith(self.remote_root):
			if newf.startswith(self.remote_root):
				self.info(f'move(),{oldf} -> {newf}')
				self.sftp.rename(oldf,newf)
			else:
				self.info(f'move(),delete {oldf}')
				self.sftp.remove(oldf)
		else:
			if newf.startswith(self.remote_root):
				self.info(f'move(),copy {nfile} -> {newf}')
				self.sftp.put(nfile,newf)

	def heart_beat(self):
		return self.sftp.listdir(self.remote_root)
@SingletonDecorator
class SFTPs:
	def __init__(self):
		self.container = {}

	def getapi(self,host,user,lroot,rroot,port=22):
		s = f'{host}:{user}:{lroot}:{rroot}:{port}'
		api = self.container.get(s,None)
		if api is not None:
			return api
		api = SFTPapi(host,user,lroot,rroot,port=port)
		return api
if __name__ == '__main__':
	a = SFTPapi('bsppo.com','ymq','/home/ymq/tmp','/home/ymq/tmp')
	print(a.heart_beat())
	
