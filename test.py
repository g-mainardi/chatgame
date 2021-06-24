import time
import subprocess
from subprocess import Popen
from threading import Thread

def Execute(target):
	#subprocess.call(["python", target + ".py"])
	Popen(["python3", target + ".py"])
    
def Test():
	print("server")
	Execute("server")

	time.sleep(2)

	print("client1")
	Execute("client1")

	time.sleep(2)

	print("client2")
	Execute("client2")

	time.sleep(2)

	print("fine avvio")

if __name__ == "__main__":
    Test()
