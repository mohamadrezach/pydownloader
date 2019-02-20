#!/usr/bin/python3
from optparse import OptionParser
from threading import Thread
from os import path,_exit,name,environ,mkdir,chdir
from time import sleep
from socket import socket
from random import randint
from urllib.parse import urlparse
try:
	from requests import get,head,session
except Exception as e:
	print(e)
	print("you need requests library :\nsudo pip3 install requests")
	quit()
class _downloader(Thread):
	__instance=None
	def __init__(self,url,filename,size,resume,Accept_Ranges):
		super().__init__()
		self.filename=filename
		self.url=url
		self.resume=resume
		self.size=int(size) if size != None else None
		self.Accept_Ranges=Accept_Ranges

	@classmethod	
	def getInstance(cls,url,filename,size,resume,Accept_Ranges):
		if not cls.__instance:
			cls.__instance=_downloader(url,filename,size,resume,Accept_Ranges)
		return cls.__instance	

	def run(self):
		self.request()

	def doDownload(self,downloaded_now,mode,headers):
		print('\n\n',downloaded_now ," +++> ",self.size,'\n' )
		with session() as s:
			with s.get(self.url,headers=headers,timeout=15,stream=True) as r:
				with open(self.filename, mode) as fd:
					if(self.resume):
						fd.read()
					for chunk in r.iter_content(chunk_size=128):
						fd.write(chunk)
		self.resume=True														

	def knownSize(self,downloaded_now,headers,mode):
		try:
			while(downloaded_now<self.size):
				self.doDownload(downloaded_now,mode,headers)
				downloaded_now=path.getsize(self.filename)
				headers['Range']="bytes="+str(downloaded_now)+'-'
				mode="r+b"					
		except Exception as e:
			print("ERROR : ",e)						
		print("\nDownload Completed\n")		
		_exit(1)	

	def unknownSize(self,downloaded_now,headers,mode):
		try:
			self.doDownload(downloaded_now,mode,headers)					
		except Exception as e:
			print("ERROR : ",e)						
		print("\n")		
		_exit(1)	

	def request(self):
		headers = {'user-agent': 'pydownloader/0.0.1','Accept-Encoding': 'identity','Accept': '*/*','Connection': 'keep-alive'}
		try:
			parsed_uri = urlparse(self.url)
			headers['Host']=parsed_uri.netloc
		except:
			pass
		
		mode="wb"
		downloaded_now=0
		if(self.resume):
			if(self.Accept_Ranges == None):
				print("link dont support resume mode")
				_exit(1)
			else:
				downloaded_now=path.getsize(self.filename)
				headers['Range']="bytes="+str(downloaded_now)+'-'
				mode="r+b"	
				print('---resume mode--------\n\n')

		if(self.size == None):
			self.unknownSize(downloaded_now,headers,mode)
		else:
			self.knownSize(downloaded_now,headers,mode)	
##-------------------------------------------------------			
class identifier:
	__instance=None
	def __init__(self,url,filename,resume,progress_length):
		self.headers = {'user-agent': 'pydownloader/0.0.1','Accept': '*/*','Accept-Encoding': 'identity','Connection': 'keep-alive'}
		self.url=url if url != None and url.startswith('http') else 'http://'+url
		self.filename=filename if filename != None else (url.rstrip('/')).split('/')[-1]
		self.resume=resume
		self.size=None
		self.progress_length=progress_length
		self.Accept_Ranges=None

	@classmethod	
	def getInstance(cls,url,filename=None,resume=False,progress_length=50):
		if not cls.__instance:
			cls.__instance=identifier(url,filename,resume,progress_length)
		return cls.__instance

	def checkNet(self):
		try:
			s=socket(2,1)
			s.connect(('www.google.com',80))
			s.close()
		except Exception as e :
			print('ERR =+=+=+=+=+= The device is not connected to the internet\n',e)
			exit()	
	def download(self):
		self.createPath()
		self.checkNet()
		self.__calcSize()
		self.__startDownload()

	def createPath(self):
		if(name == 'posix'):
			home=environ['HOME']
			chdir(home)
			if(not path.exists('Downloads')):
				mkdir('Downloads')
			chdir('Downloads')
			if(not path.exists('pydownloader')):
				mkdir('pydownloader')
			chdir('pydownloader')	


	def __calcSize(self):
		rmain=head(self.url,headers=self.headers,timeout=10)
		print('URL = > ',self.url)	
		parsed_uri = urlparse(self.url)
		self.headers['Host']=parsed_uri.netloc
		if(rmain.headers['Content-Type'].startswith('text/html')):
				try:
					self.url=rmain.headers['Location']
					print('NEW URL = >',self.url )
					parsed_uri = urlparse(self.url)
					self.headers['Host']=parsed_uri.netloc
					rmain=head(self.url,headers=self.headers,timeout=10)
				except Exception as e:	
					print('the link is not a file and is a html file')
					print("ERR ==> ",e)
					exit()

		try:
			self.Accept_Ranges=rmain.headers['Accept-Ranges']
			l=int(rmain.headers['Content-Length'])
			self.size=l if l > 1000 else  None
			del l
		except:
			self.size=None

	def __gen(self,n):
		i=0
		while True:
			yield i 
			i=i+1 if i != n-13 else 1
	def __printInfinitiProgressBar(self,genObject,length=100,speedd=0,prefix='',suffix='',fill="#"):
		x=next(genObject)
		bar=(x*"-")+" Downloading "+((length-x-13)*'-')
		print('\r(%sMG) |%s|  [%s]kbs size=[unKnown]MB %s' % (prefix,bar,speedd, suffix), end = '\r')		

	def __printProgressBar (self,iteration, total,size,speedd='n', prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
		"""
 	   Call in a loop to create terminal progress bar
 	   @params:
  	      iteration   - Required  : current iteration (Int)
  	      total       - Required  : total iterations (Int)
    	  prefix      - Optional  : prefix string (Str)
   	      suffix      - Optional  : suffix string (Str)
          decimals    - Optional  : positive number of decimals in percent complete (Int)
          length      - Optional  : character length of bar (Int)
          fill        - Optional  : bar fill character (Str)
		"""
		percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
		filledLength = int(length * iteration // total)
		size='%.1f'%size
		bar = fill * filledLength + '-' * (length - filledLength)
		print('\r(%sMG) |%s| %s%% [%s]kbs size=[%s]MB %s' % (prefix, bar, percent,speedd,size, suffix), end = '\r')


	def __startDownload(self):
		isKnown =True
		if(not self.resume and path.exists(self.filename)):
			print("\nFile exists : ",self.filename)
			self.filename="C-"+str(randint(1000,9999))+'-'+self.filename
		if(not self.resume and not path.exists(self.filename)):
			self.f=open(self.filename,'wb')
			self.f.close()
			print('File Created : ',self.filename)
			del self.f	
		self.obj=_downloader.getInstance(self.url,self.filename,self.size,self.resume,self.Accept_Ranges)
		self.obj.daemon=True
		self.obj.start()
		if(self.size is None):
			isKnown=False
			g=self.__gen(self.progress_length)
		self.size=self.size/1000/1000	
		while(self.obj.is_alive):
			Size_last=(path.getsize(self.filename)//1000)
			sleep(1)
			Size_now=(path.getsize(self.filename)//1000)
			speed=(Size_now-Size_last)/1
			downloaded=Size_now//1000
			if(isKnown==True):
				x=(downloaded*100)/self.size
				self.__printProgressBar(x, 100,self.size,speedd=speed,prefix = downloaded, suffix = 'Complete', length = self.progress_length)
			else:
				self.__printInfinitiProgressBar(genObject=g,prefix=downloaded,speedd=speed,suffix="Complete",length=self.progress_length)

def main(url,filename,resume):
	objectOfidentifier=identifier.getInstance(url,filename,resume)
	objectOfidentifier.download()
#===============================================================================
if __name__=='__main__':
	p=OptionParser(usage='%prog -u|--url [url] -o|--output [filename -> optional] (-r|--resume -> optional)')
	p.add_option('-u','--url',action='store',type='string',dest='url',help='url of file')
	p.add_option('-o','--output',action='store',type='string',dest='filename',help='name of end file')
	p.add_option("-r", "--resume",action="store_true", dest="resume", default=False,help="resume downloaded file that not finished")
	options,args=p.parse_args()
	resume=options.resume
	if(options.url is None):
		p.error('url missed')
	x=options.url.rstrip('/')	
	url,filename=x,options.filename if options.filename != None else x.split('/')[-1]
	main(url,filename,resume)
		
		
