
import subprocess
import urllib.request
import socket
from threading import Thread, Lock
from queue import Queue

# Configuration
N_THREADS = 100
q = Queue()
print_lock = Lock()

def check_ips_role(ip, role):
    """
    
    """

    try:
        contents = urllib.request.urlopen("http://" + ip + ":8000/whois/", timeout=2).read()
        contents = str(contents, 'utf-8')
    except:
        contents = "" 
    print(contents)
    if contents.startswith(role):
        return True
    else:
        return False
    
DEVICES = {}   
DEVICES["all"] = {} 
DEVICES["robots"] = {} 
DEVICES["hubs"] = {} 
DEVICES["repositories"] = {} 

def scan_address(host, b_stop_hub_repo=True):
    """Scan a single port."""
    global DEVICES
    global print_lock
    b_scan = True

    if b_stop_hub_repo:

        if len(DEVICES["hubs"]) > 0 and len(DEVICES["repositories"]) > 0:
            b_scan = False

    # try:

    if b_scan: 
        with print_lock:
            DEVICES["all"][host] = "Active"  
            try:
                contents = urllib.request.urlopen("http://" + host + ":8000/whois/", timeout=1).read()
                contents = str(contents, 'utf-8')
            except:
                contents = "" 

            if contents.startswith("robot:"):
                DEVICES["robots"][host]  = contents.split(":")[1] 
                
            elif contents.startswith("hub:"):
                DEVICES["hubs"][host]  = contents.split(":")[1] 

            elif contents.startswith("repository:"):
                DEVICES["repositories"][host]  = contents.split(":")[1]  
   # except:
   #     pass
   # finally:
   #     pass

def worker():
    """Thread worker function."""
    while not q.empty():
         url = q.get()
         scan_address(url)
         q.task_done()


def get_local_ip():
    """
    
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
 
def scan():
    global q
    ip_parts = get_local_ip().split('.')
    base_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
    for i in range(1, 55):
        ip = base_ip + '{0}'.format(i)
        q.put(ip)

    # Start threads
    threads = []
    for _ in range(N_THREADS):
         t = Thread(target=worker)
         t.daemon = True
         t.start()
         threads.append(t)
    
    q.join()
    return DEVICES


if __name__ == "__main__":
     print(scan())
