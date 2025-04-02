import socket
import time
import pygame
import threading
import subprocess
pygame.init()
pygame.mixer.init()

'''Simple SIP Application

Get's request, send TRYING, RINGING, and OK response
via SIP.

*NOTE, this only works on MAC
'''

# Message creation
'''Trying Response
Specifies that call has been received.

Get info from INVITE:
'''

def get_loc_ip():
    ifcon = subprocess.run('ifconfig',text=True,capture_output=True).stdout
    # go through each text-part 
    for i in range(len(ifcon)-8):
        if ifcon[i:i+8] == "inet 10.":
            return str(ifcon[i+5:i+30].split(' ')[0])

print(get_loc_ip())
local_ip = get_loc_ip()



def create_trying_response(invite):
    lines = invite.splitlines()

    sip_resp = ['SIP/2.0 100 Trying',
                lines[1],lines[3],lines[4].replace("<","").replace(">",""),lines[6],lines[7],
                ""  # Empty line to terminate headers
                ]

    return "\r\n".join(sip_resp)


'''Telling info about 
VOIP machine as per protocol; ringing now'''

def create_ringing_response(invite,tag="BIa8F5f"):
    lines = invite.splitlines()

    resp = ['SIP/2.0 180 Ringing',
        lines[1],lines[3],f"{lines[4]};tag={tag}", # random-tag!
        lines[6],lines[7],
        "User-Agent: Linphone-Desktop/5.2.6 (Charlies-MacBook-Air.local) osx/15.2 Qt/5.15.2 LinphoneSDK/5.3.72",
        "Supported: replaces, outbound, gruu, path, record-aware",
        ""
        ]
    return "\r\n".join(resp) 


def create_ok_msg(invite,tag="BIa8F5f",port=5060):
    lines = invite.splitlines()

    resp = ['SIP/2.0 200 OK',
        lines[1],lines[3],f"{lines[4]};tag={tag}", # random-tag!
        lines[6],lines[7],
        "User-Agent: Linphone-Desktop/5.2.6 (Charlies-MacBook-Air.local) osx/15.2 Qt/5.15.2 LinphoneSDK/5.3.72",
        "Supported: replaces, outbound, gruu, path, record-aware",
        "Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO, PRACK, UPDATE",
        f'Contact: <sip:{local_ip}:{port};transport=udp>;+org.linphone.specs="lime"',
        "Content-Type: application/sdp",
        "Content-Length: 170",
        "",
        "v=0",
        "o=charlie 1317 2917 IN IP4 10.138.57.243",
        "s=Talk",
        f"c=IN IP4 {local_ip}",
        "t=0 0",
        "m=audio 61095 RTP/AVP 8 0 101",
        "a=rtpmap:101 telephone-event/8000",
        "a=rtcp:57629",
        ""
        ]
    return "\r\n".join(resp) 




accepted = False


# listen for response
sip_listener = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sip_listener.bind((local_ip,5060))
msg, addr = sip_listener.recvfrom(1024)
print(f"***{(msg.decode('utf-8'))}*** \nreceived from {addr}")
# creating responses
msg=msg.decode('utf-8')
trying = create_trying_response(msg)
ringing = create_ringing_response(msg)
sip_listener.sendto(trying.encode('utf-8'),addr)
sip_listener.sendto(ringing.encode('utf-8'),addr)


############
sound = pygame.mixer.Sound("simpleringtone.mp3")
sound.play()
def accept_decline():

    # display call
    appleScript = """
    tell application "System Events"
        display dialog "Incoming call" buttons {"Accept", "Decline"} default button "Accept" with icon 1 giving up after 30
    end tell
    """

    # running applescript
    r = subprocess.run(['osascript','-e',appleScript],capture_output=True,text=True)
    r.stdout

    if 'Accept' in (r.stdout):
        return True
    else: 
        return False
############

# ok response
ok = create_ok_msg(msg)
accepted = accept_decline()
sound.stop()

if accepted:
    sip_listener.sendto(ok.encode('utf-8'),addr)
    print("call accepted!")


time.sleep(5)
sip_listener.close()

print("\n\n",trying,"\n\n",ringing,"\n\n",ok)

# TODO: add rest of SIP flow