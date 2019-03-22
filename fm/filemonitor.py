import os
import sys
from watchdog.observers import Observer
from watchdog.events import *
import time


from appPublic.folderUtils import ProgramPath
from appPublic.jsonConfig import getConfig
from appPublic.macAddress import getAllAddress

def endsWith(x,y):
	return x[-len(y):] == y

class FileEventHandler(FileSystemEventHandler):
	def __init__(self,config,peers):
		self.config = config
		self.peers = peers
		FileSystemEventHandler.__init__(self)
		self.myAddress = [ i[1] for i in getAllAddress() ]

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
	
	def on_moved(self, event):
		if event.is_directory:
			print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
		else:
			print("file moved from {0} to {1}".format(event.src_path,event.dest_path))
		self.movefile(event.src_path,event.dest_path)

	def on_created(self, event):
		print(self.__class__,'on_create called')
		if event.is_directory:
			print("directory created:{0}".format(event.src_path))
			self.createdir(event.src_path)
		else:
			print("file created:{0}".format(event.src_path))
			#self.copyfile(event.src_path)

	def on_deleted(self, event):
		if event.is_directory:
			print("directory deleted:{0}".format(event.src_path))
		else:
			print("file deleted:{0}".format(event.src_path))
		self.deletefile(event.src_path)

	def on_modified(self, event):
		if event.is_directory:
			print("directory modified:{0}".format(event.src_path))
		else:
			print("file modified:{0}".format(event.src_path))
			self.copyfile(event.src_path)

class OKFileHandler(FileEventHandler):

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

		
	def on_created(self,event):
		print(self.__class__,'on_create called')
		if event.is_directory:
			print("directory created:{0}".format(event.src_path))
			self.createdir(event.src_path)
		else:
			print('{0} created'.format(event.src_path))
			if endsWith(event.src_path.lower(),'.ok'):
				self.copyfile(event.src_path)

if __name__ == "__main__":
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
			time.sleep(0.01)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()
