import socket, select,sys
import json
import struct



#Function to broadcast chat messages to all connected clients
def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data	
def broadcast_data (sock, message):
	#Do not send the message to master socket and the client who has send us the message
	print(CONNECTION_LIST)
	print(message)
	for socket in CONNECTION_LIST:
		if socket != server_socket:
			print('broadcast//////*/*/*/*')
			print(socket)
			print('broadcast//////*/*/*/*')
			try :
				msg = message.encode('utf-8')
				msg = struct.pack('>I', len(msg)) + msg
				socket.sendall(msg)
			except :
				# broken socket connection may be, chat client pressed ctrl+c for example
				socket.close()
				CONNECTION_LIST.remove(socket)
				conn_stat.remove(socket)
				index = next(index for (index, d) in enumerate(conn_stat) if d['socket']== socket)
				#print('+++++1')
				#print(conn_stat[index]['name'])
				onlineuser.remove(conn_stat[index]['name'])
 
if __name__ == "__main__":
	 
	# List to keep track of socket descriptors
	CONNECTION_LIST = []
	conn_stat = []
	RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
	PORT = 5000
	userlist = [{'name':'merry','pwd':'1234','offline':[]},{'name':'jack','pwd':'1234','offline':[]},{'name':'emily','pwd':'1234','offline':[]}]
	onlineuser = []
	 
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# this has no effect, why ?
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(("0.0.0.0", PORT))
	server_socket.listen(10)
 
	# Add server socket to the list of readable connections
	CONNECTION_LIST.append(server_socket)

	print ("Chat server started on port " + str(PORT))
 
	while 1:
		# Get the list sockets which are ready to be read through select
		read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
 
		for sock in read_sockets:
			#New connection
			if sock == server_socket:
				# Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				CONNECTION_LIST.append(sockfd)
				conn_stat.append({'socket':sockfd , 'state':0, 'talk':''})
				account = [item for item in conn_stat if item['socket'] == sockfd]
				#if account:
				#	print("yes")
				#	print(str(account[0]['socket']))
				#else:
				#	print("no")
				#print "Client (%s, %s) connected" % addr
				
				#broadcast_data(sockfd, "[%s:%s] entered room\n" % addr)
			 
			#Some incoming message from a client
		
			else:
				# Data recieved from client, process it
				try:
					print('???')
					account = [item for item in conn_stat if item['socket'] == sock]
					accountindex =  next(index for (index, d) in enumerate(conn_stat) if d['socket']== sock)
					#if account:
					#	print(str(account[0]['state']))
					data = recv_msg(sock)
					#data = sock.recv(RECV_BUFFER)
					data = data.decode('utf-8')
					data = json.loads(data)
					print(data)
					print(data['action'])
					
					if data['action'] == 'Login':
						print('=================================')
						print(conn_stat)
						print('=================================')
						name = data['username'].strip()
						pwd  = data['password'].strip()
						user = [item for item in userlist if item['name'] == name]
						if user:
							if user[0]['pwd'] == pwd:
								msglist = {'action':'Login','status':0,'offline':[]}
								conn_stat[accountindex]['state'] = 1
								conn_stat[accountindex]['name'] = name
								onlineuser.append(user[0]['name'])
								userindex = next(index for (index, d) in enumerate(userlist) if d['name'] == name)
								if userlist[userindex]['offline']:
									for item in userlist[userindex]['offline']:
										msglist['offline'].append({'who':item['name'],'msg':item['msg']})
								
								
								msg = json.dumps(msglist).encode('utf-8')
								msg = struct.pack('>I', len(msg)) + msg
								sock.sendall(msg)
								
								#msglist = json.dumps(msglist)
								#sock.sendall(msglist.encode('utf-8'))
								
								userlist[userindex]['offline'] = []
								#broadcast_data(sockfd,  'Client ' + name +  " login\n" )
								
								print('print user someone login')
								userjson = {'action':'ListUser','user':[]}
								print(onlineuser)
								for user in onlineuser:
									userjson['user'].append({'name':user})
									
								msg = json.dumps(userjson)
								print(msg)
								
								broadcast_data(sock, msg)
								
							else:
								#login failed , wrong password
								msglist = {'action':'Login','status':1}
								msg = json.dumps(msglist).encode('utf-8')
								msg = struct.pack('>I', len(msg)) + msg
								sock.sendall(msg)
								
								#sock.sendall(json.dumps(msglist).encode('utf-8'))
						else:
							msglist = {'action':'Login','status':2}
							msg = json.dumps(msglist).encode('utf-8')
							msg = struct.pack('>I', len(msg)) + msg
							sock.sendall(msg)
							#sock.sendall(json.dumps(msglist).encode('utf-8'))
					elif data['action'] == 'ListUser':
						print('print user')
						userjson = {'action':'ListUser','user':[]}
						print(onlineuser)
						for user in onlineuser:
							userjson['user'].append({'name':user})
							
						msg = json.dumps(userjson).encode('utf-8')
						msg = struct.pack('>I', len(msg)) + msg
						sock.sendall(msg)
					elif data['action'] == 'Talk':
						#cmd = {'name':data['name'],'msg':data['msg']}
						talkto  = [item for item in conn_stat if item['name'] == data['recv']]
						print('conn_state')
						print(conn_stat)
						print(talkto)
						#if offline
						if not talkto :
							userindex = next(index for (index, d) in enumerate(userlist) if d['name']== data['recv'])
							userlist[userindex]['offline'].append({'name':account[0]['name'],'msg':data})
							print('not talkto')
							#print(userlist)
						else:
							talktosock = talkto[0]['socket']
							
							msg = json.dumps(data).encode('utf-8')
							msg = struct.pack('>I', len(msg)) + msg
							talktosock.sendall(msg)
							
							#talktosock.sendall(json.dumps(data).encode('utf-8'))
							print('talk to sock')
					elif data['action'] == 'Game' or data['action']=='Answer':
						talkto  = [item for item in conn_stat if item['name'] == data['recv']]
						print('Game')
						print(data)
						#if offline
						if not talkto :
							userindex = next(index for (index, d) in enumerate(userlist) if d['name']== data['recv'])
							#userlist[userindex]['offline'].append({'name':account[0]['name'],'msg':data})
							print('not talkto')
							#print(userlist)
						else:
							print('====================Game===========================')
							print(talkto)
							print(data['send'] + 'talk to '+ data['recv'])
							print('====================Game===========================')
							talktosock = talkto[0]['socket']
							
							msg = json.dumps(data).encode('utf-8')
							msg = struct.pack('>I', len(msg)) + msg
							talktosock.sendall(msg)
							
							#talktosock.sendall(json.dumps(data).encode('utf-8'))
							print('talk to sock')
					elif data['action'] == 'Logout':
					
						index = next(index for (index, d) in enumerate(conn_stat) if d['socket']== sock)
						
						CONNECTION_LIST.remove(sock)
						onlineuser.remove(conn_stat[index]['name'])
						del conn_stat[index]
						
						
						print('print user')
						userjson = {'action':'ListUser','user':[]}
						print(onlineuser)
						for user in onlineuser:
							userjson['user'].append({'name':user})
							
						msg = json.dumps(userjson)
						broadcast_data(sock, msg)
						
						
						
						#print ('Client ' + conn_stat[index]['name'] + ' is offline \n')
						sock.close()
						
					
				except:
					index = next(index for (index, d) in enumerate(conn_stat) if d['socket']== sock)
					broadcast_data(sock, 'Client' + conn_stat[index]['name'] + 'is offline')
					print ('Client' + conn_stat[index]['name'] + 'is offline')
					sock.close()
					CONNECTION_LIST.remove(sock)
					#conn_stat.remove(sock)
					
					del conn_stat[index]
					#print('+++++2')
					#print(conn_stat[index]['name'])
					onlineuser.remove(conn_stat[index]['name'])
					#print(conn_stat)
					continue
	server_socket.close()