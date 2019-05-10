import threading, queue, sys, multiprocessing

class MultiThreadHandler(object):
	def __init__(self,threads=8):
		self.queue = queue.Queue()
		self.threads=[
			Thread(self.queue, i+1)
			for i in range(threads)
		]

	def RunThreads(self):
		for t in self.threads:
			t.start()
		self.queue.join()
		print('All Files Processesed')

class Thread(threading.Thread):
	def __init__(self, queue, num=0):
		super(Thread, self).__init__()
		self._stop_event = threading.Event()
		self.queue = queue
		self.num = num

	def run(self):
		while True:
			try:
				method,kwargs = self.queue.get(timeout=1)
				p = multiprocessing.Process(target=method, kwargs = kwargs)
				p.start()
				p.join()
				#method(**kwargs)
				self.queue.task_done()

				if self.queue.empty():
					break
			except queue.Empty:
					break
			except Exception as e:
				print('Process Get Error: %s'%e)
		print('Kill Thread %s'%self.num)
		return