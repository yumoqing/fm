import os
import sys
import asyncio
from watchdog.observers import Observer
from hachiko.hachiko import AIOWatchdog,AIOEventHandler

import asyncpool

import time


from appPublic.Singleton import SingletonDecorator
from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig
from appPublic.macAddress import getAllAddress

@SingletonDecorator
class Workers(asyncpool.AsyncPool):
	pass
	
class FileEventHandler(AIOEventHandler):
	def __init__(self,config,peers):
		self.config = config
		self.peers = peers
		super(FileEventHandler,self).__init__()
		self.modified_handlers = {}
		self.myAddress = [ i[1] for i in getAllAddress() ]
		self.workers = Workers(self._loop,confg.workers_count)

	async def sshcdmd(self,func,dic):
		return func(dic)

	def getTargetPath(self,path,peer):
		p = path[len(self.config.path):]
		return self.config.peers[peer]['path'] + p

	def peerExec(self,func,path1,path2=None):
		for peer in self.config.peers.keys():
			pconf = {}
			pconf.update(self.peers[peer])
			pconf.update(self.config.peers[peer])
			tpath1 = self.getTargetPath(path1,peer)
			pconf.update({'path1':path1,'tpath1':tpath1})
			if path2 is not None:
				tpath2 = self.getTargetPath(path2,peer)
				pconf.update({'path2':path2,'tpath2':tpath2})
			func(pconf)

	def _createdir(self,pconf):
		s = 'ssh  {0}@{1} "mkdir {2}"'.format(pconf['user'],
						pconf['host'],
						pconf['tpath1'])
		if pconf.get('port'):
			s = s + ' -p ' + str(pconf.get('port'))
		os.system(s)

	def createdir(self,path):
		self.peerExec(self._createdir,path)
		
	def _movefile(self,pconf):
		s = 'ssh  {0}@{1} "mv {2} {3}"'.format(pconf['user'],
					pconf['host'],
					pconf['tpath1'],
					pconf['tpath2'])
		if pconf.get('port'):
			s = s + ' -p ' + str(pconf.get('port'))
		os.system(s)
		
	def movefile(self,sfile,dfile):
		self.peerExec(self._movefile,sfile,path2=dfile)

	def _deletefile(self,pconf):
		s = 'ssh {0}@{1} "rm -rf {2}"'.format(pconf['user'],
				pconf['host'],
				pconf['tpath1'])
		if pconf.get('port'):
			s = s + ' -p ' + str(pconf.get('port'))
		os.system(s)

	def deletefile(self,path):
		self.peerExec(self._deletefile,path)

	def _copyfile(self,pconf):
		s = "scp {0} {1}@{2}:{3}&".format(pconf['path1']
				,pconf['user']
				,pconf['host']
				,pconf['tpath1'])
		if pconf.get('port'):
			s = s + ' -p ' + str(pconf.get('port'))
		os.system(s)

	def copyfile(self,path):
		self.peerExec(self._copyfile,path)
	
	@asyncio.coroutine
	def on_moved(self, event):
		if event.is_directory:
			print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
		else:
			print("file moved from {0} to {1}".format(event.src_path,event.dest_path))
		self.movefile(event.src_path,event.dest_path)

	@asyncio.coroutine
	def on_created(self, event):
		print(self.__class__,'on_create called')
		if event.is_directory:
			print("directory created:{0}".format(event.src_path))
			self.createdir(event.src_path)
		else:
			print("file created:{0}".format(event.src_path))
			#self.copyfile(event.src_path)

	@asyncio.coroutine
	def on_deleted(self, event):
		if event.is_directory:
			print("directory deleted:{0}".format(event.src_path))
		else:
			print("file deleted:{0}".format(event.src_path))
		self.deletefile(event.src_path)

	@asyncio.coroutine
	def on_modified(self, event):
		if event.is_directory:
			print("directory modified:{0}".format(event.src_path))
		else:
			print("file modified:{0}".format(event.src_path))
			oh = self.modified_handlers.get(event.src_path,None)
			if oh is not None:
				oh.cancel()
			self.modified_handlers[event.src_path] = self._loop.call_later(2,self.copyfile,event.src_path)
			#self.copyfile(event.src_path)

class OKFileHandler(FileEventHandler):

	@asyncio.coroutine
	def on_modified(self,envet):
		pass

	def _copyfile(self,pconf):
		sf1 = pconf['path1'][:-3]
		df1 = pconf['tpath1'][:-3]
		s = """sh << EOF
scp {0} {1}@{2}:{3} {4}
scp {5} {6}@{7}:{8} {4}
EOF &""".format(sf1
				,pconf['user']
				,pconf['host']
				,df1
				,' -p '+str(pconf.get('port')) if pconf.get('port') else ''
				,pconf['path1']
				,pconf['user']
				,pconf['host']
				,pconf['tpath1']
				)
		os.system(s)

		
	@asyncio.coroutine
	def on_created(self,event):
		print(self.__class__,'on_create called')
		if event.is_directory:
			print("directory created:{0}".format(event.src_path))
			self.createdir(event.src_path)
		else:
			print('{0} created'.format(event.src_path))
			if event.src_path.lower().endswith('.ok'):
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
			print('using OKFileHandler......')
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
	asyncio.get_event_loop().run_until_complete(watch())
