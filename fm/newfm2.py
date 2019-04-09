import os
import sys
import asyncio
from watchdog.observers import Observer
from hachiko.hachiko import AIOWatchdog,AIOEventHandler
from datetime import datetime
import time


from appPublic.Singleton import SingletonDecorator
from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig
from appPublic.macAddress import getAllAddress
from sftpapi import SFTPs

def curdt():
	dt = datetime.now()
	return '%04d-%02d-%02d %02d:%02d:%02d' % (dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.day)

class FileEventHandler(AIOEventHandler):
	def __init__(self,config,peers):
		self.config = config
		self.peers = peers
		super(FileEventHandler,self).__init__()
		self.infos = self._getsftpinfo()
		self.modified_handlers = {}
		#self.myAddress = [ i[1] for i in getAllAddress() ]
		#self.workers = Workers(self._loop)
		#print(self.myAddress)

	def _getsftpinfo(self):	
		infos = {}
		sftps = SFTPs()
		for peer in self.config.peers.keys():
			pconf = {}
			pconf.update(self.peers[peer])
			pconf['rroot'] = self.config.peers[peer]['path']
			pconf['lroot'] = self.config.path
			infos[peer] = pconf
			pconf['sftpapi'] = sftps.getapi(pconf['host'],
					pconf['user'],
					pconf['lroot'],
					pconf['rroot'],
					pconf.get('port',22))

		return infos
		
	def createdir(self,path):
		for i in self.infos.values():
			sftpapi = i['sftpapi']
			sftpapi.newfolder(path)
		
	def movefile(self,sfile,dfile):
		for i in self.infos.values():
			sftpapi = i['sftpapi']
			sftpapi.move(sfile,dfile)

	def deletedir(self,path):
		for i in self.infos.values():
			sftpapi = i['sftpapi']
			sftpapi.delfolder(path)

	def deletefile(self,path):
		for i in self.infos.values():
			sftpapi = i['sftpapi']
			sftpapi.delfile(path)

	def copyfile(self,path):
		for i in self.infos.values():
			sftpapi = i['sftpapi']
			sftpapi.copy2(path)
	
	@asyncio.coroutine
	def on_moved(self, event):
		if event.is_directory:
			print(curdt(),':',"directory moved from {0} to {1}".format(event.src_path,event.dest_path))
		else:
			print(curdt(),':',"file moved from {0} to {1}".format(event.src_path,event.dest_path))
		self.movefile(event.src_path,event.dest_path)

	@asyncio.coroutine
	def on_created(self, event):
		if event.is_directory:
			print(curdt(),':',"directory created:{0}".format(event.src_path))
			self.createdir(event.src_path)
		else:
			print(curdt(),':',"file created:{0}".format(event.src_path))
			#self.copyfile(event.src_path)

	@asyncio.coroutine
	def on_deleted(self, event):
		if event.is_directory:
			print(curdt(),':',"directory deleted:{0}".format(event.src_path))
			self.deletedir(event.src_path)
		else:
			print(curdt(),':',"file deleted:{0}".format(event.src_path))
			self.deletefile(event.src_path)

	@asyncio.coroutine
	def on_modified(self, event):
		if event.is_directory:
			print(curdt(),':',"directory modified:{0}".format(event.src_path))
		else:
			print(curdt(),':',"file modified:{0}".format(event.src_path))
			oh = self.modified_handlers.get(event.src_path,None)
			if oh is not None:
				oh.cancel()
			self.modified_handlers[event.src_path] = self._loop.call_later(self.config.modified_delay,self.copyfile,event.src_path)

class OKFileHandler(FileEventHandler):

	@asyncio.coroutine
	def on_modified(self,envet):
		pass

	@asyncio.coroutine
	def on_created(self,event):
		print(curdt(),':',self.__class__,'on_create called')
		if event.is_directory:
			print(curdt(),':',"directory created:{0}".format(event.src_path))
			self.createdir(event.src_path)
		else:
			print(curdt(),':','{0} created'.format(event.src_path))
			if event.src_path.lower().endswith('.ok'):
				self.copyfile(event.src_path[:-3])
				self.copyfile(event.src_path)

@asyncio.coroutine
def watch():
	workdir = ProgramPath()
	if len(sys.argv)>1:
		workdir = sys.argv[1]
	config = getConfig(workdir)
	observer = Observer()
	for m in config.monitors:
		handler = None
		if m.get('identify_by_ok'):
			print(curdt(),':','using OKFileHandler......')
			handler =OKFileHandler(m,config.peers)
		else:
			handler = FileEventHandler(m,config.peers)
		observer.schedule(handler,m.get('path'),True)
	observer.start()
	try:
		while True:
			yield from asyncio.sleep(1)

	except KeyboardInterrupt:
		observer.stop()
	observer.join()


if __name__ == "__main__":
	print('fm version 0.2\n')
	asyncio.get_event_loop().run_until_complete(watch())
