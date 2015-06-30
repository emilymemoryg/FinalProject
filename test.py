import tkinter as tk
from tkinter import ttk

import argparse,struct,sys ,time
import time
import os
import random
from pygamehelper import *
from pygame import *
from pygame.locals import *

from random import uniform

import select, string, sys
from getpass import getpass
from ChatFns import *
import struct
from socket import *
from tkinter import messagebox
from threading import Thread
import json


LoginStatus = ['Login Success','Wrong Passwod', 'User is not exist']

LARGE_FONT = ('Verdana', 12)

chatcontroller = ''
userlistobj=''
chatobjarray = []
socketobj = ''



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

def recvMsg():
	global chatcontroller
	global userlistobj
	global chatobjarray
	global socketobj
	while 1:
		print('recvMsg1')
		#data = recv_msg(self.socket)
		data = recv_msg(socketobj)
		print('recvMsg2')
		if not data:
			print('Disconnected from chat server')
			sys.exit()
		data = data.decode('utf-8')
		data = json.loads(data)
		print('recvMsg3')
		print(data)
		
		if (data['action'] == 'Talk'):
			print('Talk')
			#self.controller.Talk(data['recv'],data['msg'],data['send'])
			if data['msg']=='successful':
				#global chatcontroller
				drawarray = chatcontroller.getDraw()
				print(drawarray)
				drawframe =[item for item in drawarray if item['name']== data['send']]
				print(drawframe)
				drawframe[0]['draw'].running = False
			
			Thread(target = chatcontroller.Talk,args=(data['recv'],data['msg'],data['send'],)).start()
			playsound('notif.wav')
			FlashMyWindow('talk to ' + data['send'])
			
#		elif(data['action'] == 'ListUser'):
			#global userlistobj
			#global chatcontroller
#			for btn in userlistobj.btn_user:
#				btn.pack_forget()
#			userlistobj.btn_user.clear()
#			print('ListUser--------------------')
#			print('------------online user-------------')
#			i=0
#			for item in data['user']:
#				print(item,'---***')
#				print(userlistobj.username,'***')
#				if item['name'] != userlistobj.username:
#					print()
#					print(str(i+1) + '.' + item['name'])
#					print(item['name'])
#					talkto = item['name']
#					btn = ttk.Button(userlistobj, text=talkto, command=lambda:chatcontroller.show_chatroom(userlistobj.username,talkto))
#					btn.pack()
#					userlistobj.btn_user.append(btn)
#			print('------------online user-------------')
		
		elif(data['action'] == 'Game'):
			#Thread(chatcontroller.DrawRoom,args=(json.dumps(data),)).start()
			chatcontroller.DrawRoom(data)
		elif(data['action'] == 'Answer'):
		
			#global chatobjarray
			print(data['send'])
			print(data['recv'])
			print(chatobjarray)
			chatroomobj = [item for item in chatobjarray if item['name'] == data['send']]
			
			print('Answer' + data['answer'])
			
			chatroomobj[0]['chat'].setAnswer(data['answer'])
class ChatRoom(tk.Tk):
	def __init__(self, *args, **kwargs):
		self.host = '127.0.0.1'
		self.port = 5000
		
		global socketobj
		self.socket = socketobj = socket(AF_INET, SOCK_STREAM)
		
		
		try :
			self.socket.connect((self.host, self.port))
		except :
			print ('Unable to connect')
			sys.exit()
		
		
		tk.Tk.__init__(self, *args, **kwargs)
		
		#tk.Tk.iconbitmap(self, default='jiji.ico')
		tk.Tk.wm_title(self, "ChatRoom")
		
		self.containter = tk.Frame(self)
		self.containter.pack(side='top', fill='both', expand=True)
		
		self.containter.grid_rowconfigure(0, weight=1)
		self.containter.grid_columnconfigure(0,weight=1)
		
		self.chat = []
		self.draw = []
		self.frames = {}
		frame = LoginFrame(self.containter, self, self.socket)
		self.frames[LoginFrame] = frame
		frame.grid(row=0, column=0, sticky='nsew')
		
		#for F in (LoginFrame,UserList, Chat):
		#	frame = F(containter, self, self.socket)
		#	self.frames[F] = frame
		#	frame.grid(row=0, column=0, sticky='nsew')
		self.show_frame(LoginFrame)
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()
	def Login(self, username, password):
		
		username = FilteredMessage(username).strip()
		password = FilteredMessage(password).strip()
		
		print(username,password)
		#encodeStr = username + ',' +password
		encodeStr = {'action':'Login','username':username,'password':password}
		encodeStr = json.dumps(encodeStr)
		encodeStr = str(encodeStr).encode("utf-8")
		
		msg = encodeStr
		msg = struct.pack('>I', len(msg)) + msg
		self.socket.sendall(msg)
		
		#self.socket.send(encodeStr)
		#sys.stdout.flush()
		
		data = recv_msg(self.socket)
		data = data.decode('utf-8')
		data = json.loads(data)
		while data['action'] != 'Login':
			data = recv_msg(self.socket)
			data = data.decode('utf-8')
			data = json.loads(data)
		
		
		#data = self.socket.recv(4096)
		#data = data.decode('utf-8')
		#sys.stdout.flush()
		#print(data)
		#data = json.loads(data)
		if data['status'] == 0:
			#global name 
			#name =username.strip()
			print('login success')
			messagebox.showinfo("info", "Login Success")
			print(username)
			frame = UserList(self.containter, self, self.socket,username.strip())
			self.frames[UserList] = frame
			frame.grid(row=0, column=0, sticky='nsew')
			self.show_frame(UserList)
			
		elif data['status'] != 0:
			print(LoginStatus[data['status']])

	def show_chatroom(self, username, talkto):
		chatroom = tk.Tk()

		chatroom.title('talk to ' + talkto)
		chatroom.geometry("400x700")
		chatroom.resizable(width=FALSE, height=FALSE)
		
		chatobj = Chat(chatroom, self, self.socket, talkto, username)
		chatobj.pack()
		#self.chat.append({'name':talkto,'chat':chatobj})
		global chatobjarray
		chatobjarray.append({'name':talkto,'chat':chatobj})
		print(chatobjarray)
		
		chatroom.mainloop()
#	def test(self):
#		print(self.chat[0].getEntryContent())
#		self.chat[0].setEntryContent(self.chat[0].getEntryContent(),'test')
	def Talk(self, username, text, talkto):
		global chatobjarray
		print('talk to ' , talkto, username)
		ChatRoomExist = [item for item in chatobjarray if item['name'] == talkto]
		if ChatRoomExist:
			print('ChatRoomExist')
			print(talkto)
			print(text)
			ChatRoomExist[0]['chat'].setEntryContent(text , talkto)
		else:
			#self.show_chatroom(username, talkto)
			
			
			print('not ChatRoomExist')
			chatroom = tk.Tk()
			chatroom.title('talk to ' + talkto)
			chatroom.geometry("400x700")
			chatroom.resizable(width=FALSE, height=FALSE)
			
			chatobj = Chat(chatroom, self, self.socket, talkto, username)
			chatobj.pack()
			#self.chat.append({'name':talkto,'chat':chatobj})
			
			global chatobjarray
			chatobjarray.append({'name':talkto,'chat':chatobj})
			
			chatobj.setEntryContent(text,talkto)
			
			chatroom.mainloop()
	def Logout(self,username):
		print('Logout')
		cmd = {'action':'Logout','name':username}
		msg = json.dumps(cmd).encode('utf-8')
		msg = struct.pack('>I', len(msg)) + msg
		self.socket.sendall(msg)
		sys.exit()
		
	def DrawRoom(self, data):
		#data = data.loads(data)
		print('opendrawroom')
		print(self.draw)
		print('***************draw')
		print(data['recv'])
		print(self.draw)
		print('***************draw')
		DrawRoomExist = [item for item in self.draw if item['name'] == data['send']]
		if DrawRoomExist:
			print('drawroom exist')
			#DrawRoomExist[0]['chat'].setEntryContent(text , talkto)
			print(data)
			buttons = (int(data['buttons'][0]),int(data['buttons'][1]),int(data['buttons'][2]))
			pos = (int(data['pos'][0]),int(data['pos'][1]))
			rel = (int(data['rel'][0]),int(data['rel'][1]))
			R = int(data['R'])
			G = int(data['G'])
			B = int(data['B'])
			#print(DrawRoomExist['draw'])
			print(type(buttons[0]))
			print(type(pos[0]))
			print(type(rel[0]))
			if (buttons[0] == 1 ) :
				pygame.draw.line(DrawRoomExist[0]['draw'].screen, (R,G,B) , pos , (pos[0] - rel[0] , pos[1] - rel[1]), 5)
				
			if (buttons[2] == 1 ) :
				pygame.draw.circle(DrawRoomExist[0]['draw'].screen, (255,255,255) , pos , 30)
		else:
			print('drawroom is not exist')
			Thread(target=self.MakeDrawRoom,args=(json.dumps(data),)).start()
#			talkto = data['send']
#			username = data['recv']
#			s = Starter(username, talkto)																						#遊戲開始
#			self.draw.append({'name':talkto,'draw':s})
#			s.mainLoop(40,username)
	def MakeDrawRoom(self, data):
		data = json.loads(data)
		global chatobjarray
		
		print(data)
		print(data['send'])
		print(data['recv'])
		print(chatobjarray)
		chatroomobj = [item for item in chatobjarray if item['name'] == data['send']]
		print(chatroomobj)
		chatroomobj[0]['chat'].setRole('answer')
		print('answer')
		print('2starter')
		talkto = data['send']
		username = data['recv']
		print('1starter')
		s = Starter(username, talkto)																						#遊戲開始
		print('starter')
		self.draw.append({'name':talkto,'draw':s})
		print(self.draw)
		s.mainLoop(40,username)
		print('mainloop')
	def getDraw(self):
		return self.draw
	def setDraw(self,name,s):
		self.draw.append({'name':name,'draw':s})
			
class LoginFrame(tk.Frame):
	def __init__(self, parent, controller, socket):
		tk.Frame.__init__(self, parent)
		self.label_Username = Label( self, text='Username:', relief=FLAT )
		self.label_Password = Label( self, text='Password:', relief=FLAT )
		#Create a text
		self.entry_Username = Entry(self, width=15)
		self.entry_Password = Entry(self, show="*", width=15)
		#Create a Button
		self.button_Login = Button(self, text="Login", command=lambda:controller.Login(self.entry_Username.get(),self.entry_Password.get()))
		#this opetion takes one or more value from the set, align the label to the (E,S,W,N) border
		
		self.label_Username.grid(row=0,sticky=E)
		self.label_Password.grid(row=1,sticky=E)

		self.entry_Username.grid(row=0,column=1)
		self.entry_Password.grid(row=1,column=1)

		self.button_Login.grid(columnspan=2)
		
		#label = tk.Label(self, text = 'PAge Home!!', font=LARGE_FONT)
		#label.pack(pady=10,padx=10)
		#button1 = ttk.Button(self, text = "Back to One",command=lambda:controller.show_frame(UserList))
		#button1.pack()
		#button2 = ttk.Button(self, text = "Back to Two",command=lambda:controller.show_frame(Chat))
		#button2.pack()
class UserList(tk.Frame):
	def __init__(self, parent, controller , socket, username):
		print('UserList:' , username)
		self.username = username
		self.controller = controller
		self.socket = socket
		self.btn_user = []
		tk.Frame.__init__(self, parent)
		cmd = {'action':'ListUser'}
		cmd = str(json.dumps(cmd)).encode('utf-8')
		print(cmd)
		
		msg = cmd
		msg = struct.pack('>I', len(msg)) + msg
		self.socket.sendall(msg)
		
		
		
		button1 = ttk.Button(self, text = "Refresh",command=lambda:self.refreshUserList())
		button1.pack()
		button2 = ttk.Button(self, text = "Logout",command=lambda:self.controller.Logout(self.username))
		button2.pack()
		
		#self.socket.send(cmd)
		#sys.stdout.flush()
		data = recv_msg(self.socket)
		#data = self.socket.recv(4096)
		data = data.decode('utf-8')
		data = json.loads(data)
		print('------------online user-------------')
		i=0
		for item in data['user']:
			print(item,'---***')
			print(username,'***')
			if item['name'] != username:
				print()
				print(str(i+1) + '.' + item['name'])
				print(item['name'])
				talkto = item['name']
				btn = ttk.Button(self, text=talkto, command=lambda:self.controller.show_chatroom(self.username,talkto))
				#show_chatroom(user , talkto someone name)
				btn.pack()
				self.btn_user.append(btn)
		print('------------online user-------------')
		
		
		
		global chatcontroller
		global userlistobj
		chatcontroller =self.controller
		userlistobj=self
		
		Thread(target=recvMsg).start()
	def refreshUserList(self):
#		for btn in self.btn_user:
#			btn.pack_forget()
#		self.btn_user.clear()
		cmd = {'action':'ListUser'}
		cmd = str(json.dumps(cmd)).encode('utf-8')
		
		msg = cmd
		msg = struct.pack('>I', len(msg)) + msg
		self.socket.sendall(msg)
		#self.socket.send(cmd)
		#sys.stdout.flush()
		print('refreshUserList')
class Chat(tk.Frame):
	def __init__(self, parent, controller, socket, talkto, username):
		tk.Frame.__init__(self, parent)
		self.role=''
		self.answer =''
		self.username = username
		self.talkto = talkto
		self.socket = socket
		#Create a Chat window
		self.ChatLog = Text(parent, bd=0, bg="white", height="8", width="50", font="Arial",)
		self.ChatLog.insert(END, "Connecting to your partner..\n")
		self.ChatLog.config(state=DISABLED)

		#Bind a scrollbar to the Chat window
		self.scrollbar = Scrollbar(parent, command=self.ChatLog.yview, cursor="heart")
		self.ChatLog['yscrollcommand'] = self.scrollbar.set

		self.AnswerEntry =  Text(parent, bd=0, bg="white",width="29", height="5", font="Arial")
		#Create the Button to send message
		self.SendButton = Button(parent, font=30, text="Send", width="12", height=5,
							bd=0, bg="#FFBF00", activebackground="#FACC2E",
							command=lambda: self.Send(talkto))
		self.DrawButton = Button(parent, font=30, text="Draw", width="12", height=5,
							bd=0, bg="#FFBF00", activebackground="#FACC2E",
							command=lambda: Thread(target=self.Draw,args=(talkto,)).start())
							
		self.AnswerButton = Button(parent, font=30, text="AnswerButton", width="12", height=5,
							bd=0, bg="#FFBF00", activebackground="#FACC2E",
							command=lambda: Thread(target=self.Answer,args=(talkto,self.AnswerEntry.get("0.0",END),)).start())
							
		

		#Create the box to enter message
		self.EntryBox = Text(parent, bd=0, bg="white",width="29", height="5", font="Arial")
		self.EntryBox.bind("<Return>", self.DisableEntry)
		self.EntryBox.bind("<KeyRelease-Return>", self.PressAction)

		#Place all components on the screen
		self.scrollbar.place(x=376,y=6, height=386)
		self.ChatLog.place(x=6,y=6, height=386, width=370)
		self.EntryBox.place(x=128, y=401, height=90, width=265)
		self.SendButton.place(x=6, y=401, height=90)
		self.DrawButton.place(x=6, y=501, height=90)
		
		self.AnswerButton.place(x=6, y=601 , height=90)
		self.AnswerEntry.place(x=128, y=601, height=90)
		
	
		
		#label = tk.Label(self, text = 'PAge Two!!', font=LARGE_FONT)
		#label.pack(pady=10,padx=10)
		#button1 = ttk.Button(self, text = "Back to HOmw",command=lambda:controller.show_frame(LoginFrame))
		#button1.pack()
		#button2 = ttk.Button(self, text = "Back to One",command=lambda:controller.show_frame(UserList))
		#button2.pack()
	def setRole(self,role):
		self.role = role
	def setAnswer(self,answer):
		self.answer = answer
	def Send(self,talkto):
		msg = self.EntryBox.get('0.0',END)
		cmd = {'action':'Talk','send':self.username ,'msg':msg,'recv':talkto}
		LoadMyEntry(self.ChatLog, msg)
		self.ChatLog.yview(END)
		self.EntryBox.delete('0.0',END)
		cmd = json.dumps(cmd).encode('utf-8')
		
		msg = cmd
		msg = struct.pack('>I', len(msg)) + msg
		self.socket.sendall(msg)
		
		#self.socket.sendall(cmd)
	def Draw(self,talkto):
		self.role='maker'
		print('Draw')
		cmd = {'action':'Game','send':self.username, 'recv':talkto}
		cmd = json.dumps(cmd).encode('utf-8')
		msg = cmd
		msg = struct.pack('>I', len(msg)) + msg
		self.socket.sendall(msg)
		
		

				
		#self.socket.sendall(json.dumps(cmd).encode('utf-8'))
		print('||||||||||||talk to ')
		print(talkto)
		print('||||||||||||talk to ')
#		Thread(target=self.test, args=talkto).start()
		
#		s.mainLoop(40,self.username)
#	def test(self,talkto):
		s = Starter(self.username, talkto, self.socket)																					#遊戲開始
		global chatcontroller
		chatcontroller.setDraw(talkto,s)
		s.mainLoop(40,self.username)
	def Answer(self, talkto, answer):
		if self.role == 'answer':
			succ = ''
			if self.answer == self.AnswerEntry.get("0.0",END):
				succ ='successful'
				global chatcontroller
				drawarray = chatcontroller.getDraw()
				print(drawarray)
				drawframe =[item for item in drawarray if item['name']== talkto]
				print(drawframe)
				drawframe[0]['draw'].running = False
				
			else:
				succ = 'wrong'
			msg = {'action':'Talk','msg': succ,'recv':talkto,'send':self.username}
			
			msg = json.dumps(msg).encode('utf-8')
			msg = struct.pack('>I', len(msg)) + msg
			self.socket.sendall(msg)
			
		elif self.role =='maker':
			msg = {'action':'Answer','answer': answer,'recv':talkto,'send':self.username,'msg':'answer'}
			msg = json.dumps(msg).encode('utf-8')
			msg = struct.pack('>I', len(msg)) + msg
			self.socket.sendall(msg)
			print('maker')
		
		
		
	def setEntryContent(self,text,username):
		LoadOtherEntry(self.ChatLog, text,username)
	def getEntryContent(self):
		print('getEntryContent')
		return self.EntryBox.get("0.0",END)
	def DisableEntry(self):
		print('disableentry')
	def PressAction(self):
		print('PressActions')
	def ClickAction(self):
		print('ClickAction')

class Starter(PygameHelper):
	global gameplayer																				#
	def __init__(self,username,talkto,socket=''):																				#初始化遊戲 RGB為RANDOM
		self.w ,self.h = 800,600
		PygameHelper.__init__(self, size=(self.w , self.h) , fill = ((255,255,255)))
		self.R = random.randint(0,255)
		self.G = random.randint(0,255)
		self.B = random.randint(0,255)
		self.socket = socket
		self.username = username
		self.talkto = talkto
		print('----------socket')
		print(self.socket)
		print('----------socket')
		print('draw')
		#elf.timer = time.time()#計時開始
		#time.sleep( 3 )
		#pygame.draw.circle(self.screen, (0,0,0) , (50,100) , 20)
		
	def update(self):
		pass
		
	def keyup(self,key):
		pass
		
	def mouseUp(self , button , pos):
		#pygame.draw.circle(self.screen, (0,0,0) , pos , 20)
		pass
		
	def mouseMotion(self , buttons , pos , rel):													#偵側滑鼠事件  左右鍵
		if self.socket == '':
			pass
		else:
			if (buttons[0] == 1 ) :
				cmd = {'action':'Game','recv':self.talkto,'send':self.username,'pos':[pos[0],pos[1]], 'rel':[rel[0],rel[1]],'R':self.R,'G':self.G,'B':self.B,'buttons':[buttons[0],buttons[1],buttons[2]]}
				print('----------socket')
				print(self.socket)
				print('----------socket')
				
				msg = json.dumps(cmd).encode('utf-8')
				msg = struct.pack('>I', len(msg)) + msg
				self.socket.sendall(msg)
				
				#self.socket.sendall(json.dumps(cmd).encode('utf-8'))
				#if (gameplayer == True) :
					#sendset(buttons,pos,rel,self.R,self.G,self.B)
				pygame.draw.line(self.screen, (self.R,self.G,self.B) , pos , (pos[0] - rel [0] , pos[1] - rel[1]), 5)
			
			if (buttons[2] == 1 ) :
				cmd = {'action':'Game','recv':self.talkto,'send':self.username,'pos':[pos[0],pos[1]], 'rel':[rel[0],rel[1]],'R':self.R,'G':self.G,'B':self.B,'buttons':[buttons[0],buttons[1],buttons[2]]}
				
				msg = json.dumps(cmd).encode('utf-8')
				msg = struct.pack('>I', len(msg)) + msg
				self.socket.sendall(msg)
				
				self.socket.sendall(json.dumps(cmd).encode('utf-8'))
				#if (gameplayer == True) :
					#sendset(buttons,pos,rel,255,255,255)
				pygame.draw.circle(self.screen, (255,255,255) , pos , 30)
	
	def draw(self):
		pass
app =ChatRoom()
app.mainloop()