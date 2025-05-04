import socket
import secrets # for branch/tag
import time
'''
ALWAYS starts with type of command:
ALWAYS end each command with \r\n bytes

(this is a minimal example with only
required parameters)
--------------------------------------

INVITE sip:{ip_addr} SIP/2.0
Via: SIP/2.0/UDP {ip_addr}:{port=5060};branch=z9hG4bK.GOXyfZY7y;rport
From: "{DisplayName}" <sip:{username}@{server_ipaddr}>;tag=MDiQjEkoG
To: {"othername}" sip:{dest_addr}
CSeq: 20 INVITE
Call-ID: {unique_call_id=lq66o-0T6P}
Max-Forwards: 70
Contact: <sip:{ip_addr}>
Content-Type: application/sdp
Content-Length: {len(sdp)}

'''

# SDP: for negotiating media 
# more on audio formatting later
# when we discuss audio transport
'''
v=0 // version
o =- {rand1} {rand1} IN IP4 {ip_addr}// origin: empty,session_id,session version,network type,adress type (ip4),origin adress
s=SIP call // name
c =IN IP4 {ip_addr} // connection info
t=0 0 // time info 
m=audio 49177 RTP/AVP 0 // media format, port, type, codece 0

'''

# sip client which builds all request types!
# local (for now)
class SIPClient:
    ########################

    # for tag/branch
    @staticmethod
    def create_ranhex(length=10):
        return secrets.token_hex(length//2)

    # creating full identifiers for init
    def create_identifiers():
        branch = "z9hG4bK."+SIPClient.create_ranhex()
        tag = SIPClient.create_ranhex()
        call_id = SIPClient.create_ranhex()
        session_sdp = secrets.randbits(32)

        identifiers = {
            "Via":branch,
            "From":tag,
            "Call-ID":call_id
        }
        return identifiers,session_sdp


    #########################
    def __init__(self,ip_addr,username,timeout=20,max_retries=10):
        self.ip = ip_addr # loacl
        self.max_retries = max_retries
        self.username = username
        self.timeout = timeout
        

        # udp socket to listen/recv
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.port_src = 5061
        self.sock.bind((self.ip,self.port_src)) # normal port
        self.sock.settimeout(self.timeout)


    


    #########################

    def generate_sip_command(self,type,cmd,cmd_num,dest_ip,identifiers,cseq,session_sdp,via=True,extra_cmds=[],sdp_include=True,keep_branch=False):
        full_sip = []
        # difference in titles
        if type == "request":
            sip_title = f"{cmd} sip:{dest_ip} SIP/2.0"
        elif type == "response":
            sip_title = f"SIP/2.0 {cmd_num} cmd"
        full_sip.append(sip_title)
        
        # command-type/sequence...(if request)
        if cseq:
            assert(type == "response"), "cannot pass cseq for request"
            cseq = cseq
        else:
            cseq = f"CSeq: {cmd_num} {cmd.upper()}"
        

        # via parameter
        via = f"Via: SIP/2.0/UDP"
        if via:
            via += f" {self.ip}:{self.port_src}"
        if "Via" in identifiers.keys() and type == "response" or keep_branch:
            via += f";branch={identifiers['Via']};rport"
        else:
            new_branch = f"z9hG4bK.{SIPClient.create_ranhex()}"
            via += f";branch={new_branch}" # a new branch
            identifiers["Via"] = new_branch
        full_sip.append(via)
        
        # From header
        from_header = f'From: <sip:{self.username}@{self.ip}>'

        if "From" in identifiers.keys():
            from_header += f";tag={identifiers['From']}"
        full_sip.append(from_header)
        
        # To header
        to_header = f"To: sip:{dest_ip}"
        if "To" in identifiers.keys():
            to_header = f"To: <sip:{dest_ip}>;tag={identifiers['To']}"
        full_sip.append(to_header)
        full_sip.append(cseq) # &********

        # Call-id
        callID = f"Call-ID: {identifiers['Call-ID']}"
        full_sip.append(callID)

        # max-forwards (routing, really not important)
        max_forwards = f"Max-Forwards: 70"
        full_sip.append(max_forwards)

        # contact for sending back
        # directly to server for receiver
        contact = f"Contact: <sip:{self.ip};transport=udp>"
        full_sip.append(contact)

        # any extra commands!
        [full_sip.append(header)for header in extra_cmds]

        # SDP
        sdp_info = [
            'v=0',
            f'o=- {session_sdp} {session_sdp} IN IP4 {self.ip}',
            's=sip call',
            f'c=IN IP4 {self.ip}',
            f'm=audio 49922 RTP/AVP 0', # port!
            f'a=rtpmap:0 PCMU/8000', # TODO: COME BACK TO THIS
            '\r\n' # empty line (not appended to w/join)
        ]
        sdp = '\r\n'.join(sdp_info) 
        length_sdp = len(sdp) #length in bytes, chars=bytes

            
        # adding sdp (optional)
        if sdp_include:
            full_sip.append("Content-type: appliciation/sdp")
            full_sip.append(f"Content-length: {length_sdp}")
            return "\r\n".join(full_sip) +'\r\n\r\n' +sdp , identifiers
        else:
            return '\r\n'.join(full_sip) + '\r\n\r\n',identifiers
    
    #########################

    def parse_sip_response(self,msg,debug=False):
        # splitting if SIP present
        msg_parts = msg.split('\r\n\r\n')
        if len(msg_parts) == 3:
            has_sdp = True
        else:
            has_sdp = False

        sdp_headers = msg_parts[1].split('\r\n') # ignore for now...
        sip_headers = msg_parts[0].split('\r\n')
   
        # num and cmd type
        cmd_type = (' ').join(sip_headers[0].split(' ')[-2:])


        # get into a dict list
        pairs = [prt.split(': ') for prt in sip_headers[1:]]
        sip_params = {header:value for header,value in pairs}

        # making sure we extract branches
        identifiers = {header:sip_params[header].split(';')[1] for header in sip_params.keys() if any(substring in sip_params[header] for substring in ["branch=","tag="])}
        for key in identifiers.keys():
            identifiers[key] = identifiers[key].replace('branch=','').replace('tag=','')

        print("Parsor-----------------------------")
        print(sip_headers)
        print(sip_params)
        print()
        print("Parsor-----------------------------")
        identifiers["Call-ID"] = sip_params["Call-ID"]

        return cmd_type,sip_params,identifiers
    
    #########################

    # send msg, get (forc_ip to make recvd from dest)
    # when we NEED to be sure we get a response...
    def send_retry(self,msg,dest,port,force_ip=True):
            self.sock.sendto(msg.encode('utf-8'),(dest,port))
            self.sock.settimeout(2.0)

            # try to recv/send!
            retries = 0
            while retries <= self.max_retries:
                try:
                    data,addr= self.sock.recvfrom(4096)
                    if dest == addr[0]:
                        self.sock.settimeout(self.timeout)
                        return data,addr
                    else:
                        pass # wrong adress...
                except socket.timeout:
                    retries+=1
                    print(f"timeout, retrying:{retries}")
                    self.sock.sendto(msg.encode('utf-8'),(dest,port))
                    if retries == self.max_retries:
                        self.sock.settimeout(self.timeout)
                        raise TimeoutError("Could not send packet")                    
            
    
    # listen for specific message
    def listen_for(self,msg_target,call_id):
        # Wait for RINGING
        while True:
            msg,addr= self.sock.recvfrom(4096)
            if not msg:
                print("empty bytes received")
            else:
                msg_type,headers,identifiers = self.parse_sip_response(msg.decode('utf-8'))
                if any(msg_type == m for m in msg_target) and call_id == headers["Call-ID"]:
                    return msg,addr
                time.sleep(0.2)
                print(f"- Recvd {msg_type}, waiting for: {msg_target} from {call_id}")

            

    #########################

    def initiate_call(self,dest_addr,port):
        # INVITE --> (repeat if nec.)
        # TRYING <--
        # RINGING <--
        # ACK (the ok) -->
        # BYE --><---
        # OK --><-- (either or)
        print("Call initiating...")

        # generate: branch: z9hG4bK.GOXyfZY7y
        # tag: (for entire)
        # call-id for entire

        identifiers,session_sdp = SIPClient.create_identifiers()

        ### TESTING IT OUT...
        sip_generated = self.generate_sip_command(type="request",
                                                cmd="INVITE",
                                                cmd_num="20",
                                                dest_ip=dest_addr,
                                                identifiers=identifiers,
                                                session_sdp=session_sdp,
                                                cseq=None,
                                                via=True,
                                                extra_cmds=[])
        full_invite = sip_generated[0]
        identifiers = sip_generated[1]
        # add media...

        
        ###
        print("*****INVITE*****")
        print(full_invite)
        print("**********")

        print("*****RECVing*****")
        recvd_msg,addr= self.send_retry(full_invite,dest=dest_addr,port=port)
        print(addr)
        print(recvd_msg)        
        print("**********")

        # Parse message, wait
        msg_type,headers,identifiers_new = self.parse_sip_response(recvd_msg.decode('utf-8'))
        if msg_type == "100 Trying":
            pass
        else:
            raise Exception(f"^^^^^^^^Error, {msg_type} response received^^^^^^^^^")
        

        # Wait for RINGING
        msg,recvd_addr = self.listen_for(["180 Ringing",],call_id=identifiers["Call-ID"])
        identifiers_new = self.parse_sip_response(msg.decode('utf-8'))[2] # only ones really necessary...
        print("*****ringing...*****")
        print(identifiers_new)
        print("*************")

        
        # Wait for accept/decline
        # ACK whatever, now we've gotta call!
        msg,recvd_addr = self.listen_for(["200 Ok", "603 Decline"],call_id=identifiers_new["Call-ID"])
        msg_type,headers,new_identifiers = self.parse_sip_response(msg.decode('utf-8'),debug=True)


        # handling either response
        # need to include how we transport to the client
        if msg_type == "603 Decline":
            print("DECLINED")
            identifiers = new_identifiers
            msg_ack,identifiers= self.generate_sip_command(type="request", # ACK is request
                                      cmd="ACK",
                                      cmd_num="20", # 20 for ack
                                      dest_ip=dest_addr,
                                      identifiers=identifiers,
                                      cseq=None, # On same for ack
                                      session_sdp=None,
                                      via=True,
                                      extra_cmds=[],
                                      sdp_include=False,
                                      keep_branch = True # only for decline!
                                      )
            print(msg_ack)
            self.sock.sendto(msg_ack.encode('utf-8'),(dest_addr,port))
        elif msg_type == "200 Ok":
            print("ACCEPTED")
            identifiers = new_identifiers
            msg_ack,identifiers= self.generate_sip_command(type="request", # ACK is request
                                      cmd="ACK",
                                      cmd_num="20", # 20 for ack
                                      dest_ip=dest_addr,
                                      identifiers=identifiers,
                                      cseq=None, # On same for ack
                                      session_sdp=None,
                                      via=True,
                                      sdp_include=False,
                                      keep_branch = False # new for accept...
                                      )
            print(msg_ack)
            self.sock.sendto(msg_ack.encode('utf-8'),(dest_addr,port))


      
        



        
    #########################
    def close_client(self):
        self.sock.close()
        print("sucessfully closed client")

# Simple call-flow...
iphone = '100.105.32.112'
imac = '100.124.130.10'
windows = '100.70.82.70'
client1 = SIPClient(imac,"Charl")
client1.port_src = 5061
client1.initiate_call(windows,port=5060)
client1.close_client()