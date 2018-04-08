from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from pathlib import Path
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from collections import defaultdict
from kivy.clock import Clock
import shutil #to move files into different directories
import os #used for moving file into archive directory
import time
from datetime import datetime
import json
import signal
import threading
from threading import Thread
from kivy.uix.colorpicker import ColorPicker
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
import logging
from multiprocessing import Process

workfile_path = '/home/pi/kivy/examples/workfile.txt'
database_path = '/home/pi/kivy/examples/database.py'

#Globals
'''dictionary to hold rooms and lights data'''
database_dict = defaultdict(list) # {'Name1':[Ip_addr, data], 'Name2': [Ip_addr, data]..etc}

btns_down = []
lights_down = []
lights_assigned = []

''' set of users for login screen '''
usersSet = {"g", "jack", "taylor", "jorge"}

'''Circadian Rhythm dictionary - VALUES NEED TO BE CHANGED'''
CR = {
'00':'005454FF',
'01':'00545454',
'02':'00545454',
'03':'00545454',
'04':'00545454',
'05':'88545454',
'06':'FF7FFFFF',
'07':'FF7FFFFF',
'08':'FF7FFFFF',
'09':'FF7FFFFF',
'10':'FF1E90FF',
'11':'FF1E90FF',
'12':'FF87CEFA',
'13':'FF87CEFA',
'14':'FF87CEFB',
'15':'FF87CEFC',
'16':'FF87CEFA',
'17':'88545454',
'18':'00545454',
'19':'00545454',
'20':'00545454',
'21':'00545454',
'22':'00545454',
'23':'00545454'}


class Health(Screen):
	time = StringProperty()
	date = StringProperty()
	red = StringProperty()
	green = StringProperty()
	blue =  StringProperty()
	intensity = StringProperty()
	status = StringProperty()
	light_name = StringProperty()
	ip = StringProperty()
	sa = StringProperty()
	sr = StringProperty()
	sg = StringProperty()
	sb = StringProperty()

	A = NumericProperty()
	B = NumericProperty()
	R = NumericProperty()
	G = NumericProperty()
	
	def __init__(self, **kwargs):
		super(Health, self).__init__(**kwargs)
		
	def check_status_ALL(self):
		with open("database.py","r") as db:
			database = db.readlines()
		db.close()
		
		count = 0
		for line in database:
			curr_line = line.strip() # remove white spaces
			sec = curr_line.split() # split line
			if sec[0] == '#[IP_address]':
				pass
			else:
				ip = sec[0]
				self.write_(ip)
				count = count + 1
				
		for c in range(count):
			ob = Methods()
			ob.cmdparser()
			#self.getTime()
		
		t3 = threading.Timer(32.0, self.check_status_ALL)
		t3.daemon=True
		t3.start()
	
	def grab_name(self, ip):
		with open("database.py","r") as db:
			d =db.readlines()
		db.close()
		
		for line in database:
			curr_line = line.strip() # remove white spaces
			sec = curr_line.split() # split line
			if sec[0] == ip:
				c_light = sec[2]
			else:
				pass


	def health_status(self):
		#lights_down contains user's light selection on the view room screen
		self.light_name = lights_down[0]
		
		with open("database.py","r") as db:
			data = db.readlines()
		db.close()
		
		for line in data:
			curr_line = line.strip()
			sec = curr_line.split()
			if sec[2] == lights_down[0]:
				#grab ip
				ip_addr = sec[0]
				self.ip = sec[0]
				#sends command to server
				self.write_(ip_addr)
			else:
				pass

		#reads GET command
		m = Methods()
		#m.cmdparser(10,10)
		m.cmdparser()
		self.getTime()
		
	''' method retrieves sensor values, this is called after m.cmdparser()'''
	def retrieveSensor(self, ip_addr, d):
		#self.grab_name(ip_addr)
		print(' The values received from server: %s , %s' % (ip_addr, d))
		
		global A
		global R
		global G
		global B

		#hex to decimal conversion
		A = int(d[0] + d[1], 16)
		R = int(d[2] + d[3], 16) 
		G = int(d[4] + d[5], 16)
		B = int(d[6] + d[7], 16)
		5
		print('%d %d %d %d' % (A,R,G,B)) 
		
	''' method retrieves the current time and date'''
	def getTime(self):
		#determine time and date
		self.time = datetime.now().strftime('%H:%M')
		self.date = datetime.now().strftime('%Y-%m-%d')
		
		#hours go by [00-23]
		hour = str(datetime.now().hour)
		if len(hour) == 1:
			hour = '0' + str(datetime.now().hour)
		else:
			pass
		
		self.retrieveCR_and_status(hour)
	
	''' method retrieves current circadian rhythm values and calculates health status'''
	def retrieveCR_and_status(self, hour):
		#Grabs current circadian rhythm values
		values = str(CR[hour])
		
		#Hex to decimal 
		intensity = int(values[0] + values[1], 16)
		red = int(values[2] + values[3], 16)
		green = int(values[4] + values[5], 16)
		blue = int(values[6] + values[7], 16)
		
		#display the current circadian rhythm values 
		self.intensity = str(intensity)
		self.red = str(red)
		self.green = str(green)
		self.blue = str(blue)
		
		#determine the minimum and maximum
		min_intensity = intensity - (intensity * 0.05)
		min_red = red - (red * 0.05)
		min_green = green - (green * 0.05)
		min_blue = blue - (blue * 0.05)

		max_intensity =  intensity + (intensity * 0.05)
		max_red = red + (red * 0.05)
		max_green = green + (green * 0.05)
		max_blue = blue + (blue * 0.05)
		
		#check for min and max range of each value
		if min_intensity < 0:
			min_intensity = 0
		elif max_intensity > 255:
			max_intensity = 255
		else:
			print('inten in range')
			
		if min_red < 0:
			min_red = 0
		elif max_red > 255:
			max_red = 255
		else:
			print('red in range')
			
		if min_green < 0:
			min_green = 0
		elif max_green > 255:
			max_green = 255
		else:
			print('green in range')

		if min_blue < 0:
			min_blue = 0
		elif max_blue > 255:
			max_blue = 255
		else:
			print('blue in range')

		global A
		global R
		global G
		global B
		
		#display sensor valuesa
		self.sa = str(A)
		self.sr = str(R)
		self.sg = str(G)
		self.sb = str(B)
		
		#compare CR values and sensor values
		if ((A >= min_intensity) and (A <= max_intensity)):
			print('pass 1')
			if((R >= min_red) and (R <= max_red)):
				print('pass 2')
				if((G >= min_green) and (G <= max_green)):
					print('pass 3')
					if ((B >= min_blue) and (B <= max_blue)):
						print('pass 4')
						self.status = 'Healthy'
						print('Healthy')
					else:
						print('no4')
						self.status = 'Unhealthy'
						print('Unhealthy')
						self.status_popup()

				else:
					print('no3')
					self.status = 'Unhealthy'
					print('Unhealthy')
					self.status_popup()

			else:
				print('no2')
				self.status = 'Unhealthy'
				print('Unhealthy')
				self.status_popup()

		else:
			print('no1')
			self.status = 'Unhealthy'
			print('Unhealthy')
			self.status_popup()

			
		self.clear_selection()
			
	def clear_selection(self):
		global lights_down
		lights_down = []
		
	def status_popup(self):
		#Read and Accept Popup
		box = BoxLayout(orientation = 'vertical', padding = (8))
		#message on popup
		message = Label(text='Warning:', font_size=20, valign = 'middle', size_hint=(1,.3))
		box.add_widget(message)
		#user input
		_popup = Popup(title= 'Warning', content = box, title_size =(25),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
		box.add_widget(Button(text='Read and Accept', size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_press = _popup.dismiss))
		_popup.open()

	''' Send 'GET' command to server by writing it in the work file'''
	def write_(self, ip_addr):
		data = '00000000'
		(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
		dt = "%s.%03d" % (dt, int(micro) / 1000)
		cmd = "S" + " " + ip_addr +  " " + "GET" + " " + data + " " + dt
		
		with open("workfile.txt","a") as document:
			document.write(cmd)
			document.write('\n')
		document.close()
		

class SetValues(Screen):
	ARGB = ''
	def __init__(self, **kwargs):
		super(SetValues, self).__init__(**kwargs)
	
	def build(self):
		#create layout to display the data
		color_picker = ColorPicker()
		self.ids.setbox.add_widget(color_picker)
		
		#capture color selection
		def on_color(instance, value):
			#print "RGBA = ", str(value)  #  or instance.color
			#print "HSV = ", str(instance.hsv)
			#print "HEX = ", str(instance.hex_color)
			RGBA = list(color_picker.hex_color[1:])
			
			A = (RGBA[6] + RGBA[7])
			B = (RGBA[4] + RGBA[5])
			G = (RGBA[2] + RGBA[3])
			R = (RGBA[0] + RGBA[1])
			
			global ARGB
			ARGB = A+R+G+B
			print(ARGB)
			

		color_picker.bind(color=on_color) #binds to function above
	
	def set_selection(self):
		#may have to change this to the part under Health where it can pass to as many lights
		#actually just one light at a time based on requirements and the screen being too small. 
		light =  lights_down[0]
		
		with open("database1.json", "r") as db:
			data = db.read()
			db.close()
		dictionary = json.loads(data)
		
		with open("database.py","r") as db:
			data = db.readlines()
		db.close()
		
		for line in data:
			curr_line = line.strip()
			sec = curr_line.split()
			if sec[2] == light:
				#grab ip
				ip_addr = sec[0]
				self.write(ip_addr)
			else:
				pass
				
			
	def write(self, ip_addr):
		(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
		dt = "%s.%03d" % (dt, int(micro) / 1000)
		cmd = "S" + " " + ip_addr +  " " + "SET" + " " + str(ARGB) + " " + dt
		
		with open("workfile.txt","a") as document:
			document.write(cmd)
			document.write('\n')
		document.close()
			

''' Popup that allows user to define light names '''
class addingLight(Popup):
	keyN = '' 
	ip = ''
	data = ''
	bflag = ''
	def __init__(self, **kwargs):
		super(addingLight, self).__init__(**kwargs)
		
	def build(self, ip_addr, t_data):
		global bflag
		global ip
		global data
		
		# check if ip address exists in database.py
		with open("database.py","r") as f:
			myfile = f.readlines()
			f.close()
		
		for line in myfile:
			curr_line = line.strip() # remove white spaces
			sec = curr_line.split() # split line
			if sec[0] == ip_addr: 
				print('IP address exists in database')
				bflag = 0
				break
			else:
				print('not in database')
				bflag = 1
				continue

		if (bflag == 1):
			# temp store ip address and data
			ip = ip_addr
			data = t_data
			
			''' customize box layout with popup & user text input '''
			box = BoxLayout(orientation = 'vertical', padding = (8))
			#message on popup
			message = Label(text=('Enter name for {}'.format(ip_addr)), font_size=20, valign = 'middle', size_hint=(.3,.3))
			box.add_widget(message)
			#user input
			self.textinput = TextInput(text='',multiline = False, size=(1,.08),font_size=35, pos_hint={'center_x': .5, 'center_y': .6})
			box.add_widget(self.textinput)
			#popup
			light_popup = Popup(title= 'New Light Detected', content = box, title_size =(25),title_align='center',size=(.5,.5), auto_dismiss=False)
			box.add_widget(Button(text='Set', size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': .2}, on_press=self.store_name,on_release = light_popup.dismiss))
			light_popup.open()
		
	def add2database(self, key, ip, data):
		f = open('database.py','a')
		f.write(ip + ' ' + data + ' ' + key)
		f.write('\n')
		f.close()
		
				
	'''stores the user defined name for each light connected'''
	def store_name(self,arg1):
		key = self.textinput.text
		
		#some error checking
		if key == '' or len(key) < 5:
			print('error: no input given or input is less than 5 chars')
			#self.build(ip)
			self.build(ip, data)
		elif key != '' and len(key) >=5:
			global keyN
			keyN = key
			self.add2database(keyN, ip, data)
			#self.initial_CR(ip)
			o = Methods()
			o.CR_update(ip)
			
			
	''' Method sends a [one-time] set of values to the new connected light to signal that it has been successfully added to the database '''		
	def initial_CR(self,ip_address):
		#timestamp = datetime.now().strftime("%y-%m-%d-%H:%M:%S:%f")
		(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
		dt = "%s.%03d" % (dt, int(micro) / 1000)
		data = 'XXXXXXXX' #value should be changed when testing 
		cmd = "S" + " " + ip_address + " " + "SET" + " " + data + " " + dt
		with open("workfile.txt", "a") as workfile:
			workfile.write(cmd)
			workfile.write('\n')
			workfile.close()
			

class Methods(Screen):
	def __init__(self, **kwargs):
		super(Methods, self).__init__(**kwargs)
		
	def CR_update_ALL(self): 

		print('updating ALL lights')
		#grab current time
		time = datetime.now()
		#grab current hour
		hour = time.hour 
		with open("database.py","r") as db:
			dbfile = db.readlines()
			db.close()
			
		for line in dbfile:
			curr_line = line.strip() # remove white spaces
			sec = curr_line.split() # split line
			for key in CR.keys():
				if str(hour) == key:
					print(CR[key])
					data = CR[key]
					(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
					dt = "%s.%03d" % (dt, int(micro) / 1000)
					data = CR[key] #should grab value from CR dictionary
					if sec[0] == '#[IP_address]':
						pass
					else:
						cmd = "S" + " " + sec[0] + " " + "SET" + " " + data + " " + dt
						with open("workfile.txt", "a") as workfile:
							workfile.write(cmd)
							workfile.write('\n')
						workfile.close()
							
		t2 = threading.Timer(12.0, self.CR_update_ALL)
		t2.daemon=True
		t2.start()
		
		''' This method updates the new connected light to the current CR values which is based on time'''
	def CR_update(self,ip_addr):
		#store current time
		time = datetime.now()
		print(time.hour)
		#loop through CR dictionary
		for key in CR.keys():
			(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
			dt = "%s.%03d" % (dt, int(micro) / 1000)
			if str(time.hour) == key:
				print(CR[key])
				data = CR[key] #should grab value from CR dictionary
				cmd = "S" + " " + ip_addr + " " + "SET" + " " + data + " " + dt
				with open("workfile.txt", "a") as workfile:
					workfile.write(cmd)
					workfile.write('\n')
				workfile.close()
				break
			else:
				print('does not exist in CR')

	
	def update_dict(self):
		with open('database.py', 'r') as document:
			for line in document:
				line = line.split()
				if not line:  # empty line?
					continue
				database_dict[line[2]] = line[0:2]
			document.close()
			
		with open("lights_assigned.json","r") as fp:
			data = fp.read()
			fp.close()
		assigned_list = json.loads(data)

		for i in assigned_list:
			for key in database_dict.keys():
				if i == key:
					del database_dict[key]
					print('found a key in database_dict that matches an element in lights_assigned.json')
				else:
					print('not in database_dict, from update_dict()')
		print(database_dict)

	
	def removeLight(self,ip_address):
		
		with open("database.py","r") as db:
			database = db.readlines()
		db.close()
		
		del database_dict[ip_address]
		
		for key in database_dict.keys():
			database = db.readlines()
			#access line by line
			for line in database:
				curr_line = line.strip() # remove white spaces
				sec = curr_line.split() # split line
				if sec[0] != ip_address: 
					print('writing')
					b.write(line)
				else:
					pass
		
		with open("database.py", "w") as doc:
			doc.write(database)
		doc.close()
		
	
		#with open("database.py","r+") as db:
			#database = db.readlines()
		#db.close()
		
		##with open("database.py","w") as b:
		#with open("database.py","w") as b:
			#database = db.readlines()
			##access line by line
			#for line in database:
				#curr_line = line.strip() # remove white spaces
				#sec = curr_line.split() # split line
				
				##if user defined light name is equal to the light selected
				#if sec[0] != ip_address: 
					#print('writing')
					#b.write(line)
				#else:
					#key = sec[2]
					#del database_dict[key]
					#break
		#b.close()
		
		#print('database after removal')
		#print(database_dict)
		
		
	''' method that helps process commands '''
	def process_cmd(self,IP, function, any_data):
		print('Processing...%s, %s, %s ' % (IP, function, any_data))
		if function == 'GET':
			s = Health()
			s.retrieveSensor(IP, any_data)
			s.getTime()
		elif function == 'ADD':
			obj = addingLight() #works
			obj.build(IP, any_data) #works
		elif function == 'TST':
			ob = Methods()
			ob.testingT(IP, any_data)
		elif function == 'RMV':
			self.removeLight(IP) #not working correctly
		else:
			print('Unknown function')
			
	#def cmdparser(self,signum,frame):
	def cmdparser(self):

		print('cmdparser running')
		
		''' This method changes 'G' to 'P' when command has been processed'''
		def replace_line(file_name, line_no, text):
			lines = open(file_name, 'r+').readlines()
			lines[line_no] = text + '\n'
			out = open(file_name, 'w')
			out.writelines(lines)
			out.close()
			
		flag = 1
		if(flag == 1):
			try:
				dfile = open(workfile_path, 'r')
				myfile = dfile.readlines()
				line_num = -1 #to get line number, starts at 0
				for line in myfile:
					line_num +=1 	#keep line count
					curr_line = line.strip() #strip line to remove whitespaces
					parts = curr_line.split() #split line
					if parts[0] == 'G': #if command exist
						#Store IP_addr, function and data, if available
						IP_addr = parts[1]
						func = parts[2]
						data = parts[3]
						print(IP_addr, func, data)
						self.process_cmd(IP_addr, func, data) #process command
						timestamp = datetime.now().strftime('%H:%M:%S')
						#timestamp = datetime.now().strftime("%y-%m-%d-%H:%M:%S:%MS")
						new_curr = 'P '+ ' '.join(curr_line.split()[1:]) + " " + timestamp # replaces 'G' with 'P'
						replace_line(workfile_path, line_num, new_curr)
						break
					else:
						pass #no command
			except:
				print('empty file')
				flag = 0

		t1 = threading.Timer(7.0, self.cmdparser)
		t1.daemon=True
		t1.start()		

	#'''this function allows the cmdparser() to run every N seconds, which checks for 'G' commands (GUI)'''
	#def check(self):
		#signal.signal(signal.SIGALRM, self.cmdparser)
		#signal.setitimer(signal.ITIMER_REAL, 15, 8) 


class ScreenManagement(ScreenManager):
	pass

'''This screen displays the lights available in form of buttons'''	
class LightsView(Screen):
	def __init__(self, **kwargs):
		super(LightsView, self).__init__(**kwargs)
		
	'''builds a list of light buttons with scrolling'''	
	def buildlist(self):
		print('building list')
		self.ids.gridlayout.clear_widgets()
		self.update()
		for key in database_dict:
			if key == '[Name]':
				pass
			else:
				btn = ToggleButton(text='%s' % key,size = (380, 40),size_hint=(None,None)) #create button
				btn.bind(state=self.lightscallback)
				self.ids.gridlayout.add_widget(btn) #add to gridlayout 
		self.ids.gridlayout.bind(minimum_height=self.ids.gridlayout.setter('height'))

	

	def update(self):
		o = Methods()
		o.update_dict()
	
	def add_room(self):
		#popup
		box2 = BoxLayout(orientation = 'vertical', padding = (8))
		message = Label(text='Enter name: ', font_size=25, valign = 'middle', size_hint=(.8,.1))
		box2.add_widget(message)
		#user input
		self.textinput = TextInput(text='',multiline = False, size_hint=(1,.08), font_size=20)
		box2.add_widget(self.textinput)
		popup = Popup(title= 'Add Room', content = box2, title_size =(25),title_align='center', size_hint=(.5,.5), auto_dismiss=True)
		box2.add_widget(Button(text='Set Name', size_hint=(.2,.1), on_press = self.store, on_release = popup.dismiss))
		popup.open()
		
		
	'''method checks the state of the toggle buttons for lights section'''
	def lightscallback(self, instance, value):
		
		print('My button <%s> state is %s' % (instance.text, value))
		if value == 'down':
			lights_down.append(instance.text) # add to list of buttons with down state
		elif value == 'normal':
			lights_down.remove(instance.text) # remove from list if back to normal
			print('not down')
		else:
			pass
		print(lights_down)
		
	'''method checks the state of the toggle buttons for rooms section'''		
	def callback(self,instance, value):

		print('My button <%s> state is %s' % (instance.text, value))
		if value == 'down':
			btns_down.append(instance.text) # add to list of buttons with down state
		elif value == 'normal':
			btns_down.remove(instance.text) # remove from list if back to normal
			print('not down')
		else:
			pass
	
	'''method adds lights selected by user to a specific room'''
	def add_to_room(self):
		with open("database1.json", "r") as f:
			data = f.read()
			f.close()
		new_dict = json.loads(data)

		if ((len(btns_down) == 1) and (len(lights_down) >= 1)):
			for i in lights_down: 
				if i in new_dict:
					pass
				else:
					print('not a duplicate')
					new_dict[btns_down[0]].append(i)
					lights_assigned.append(i)
		else:
			print('error 1')
			pass
			
		self.store_lights_assigned(lights_assigned)
		self.write2JSON(new_dict)
		self.update_rooms()
		self.move_lights_database()
	
	'''method stores lights_assigned list to a json file'''
	def store_lights_assigned(self, arg1):		
		data = json.dumps(arg1)
		
		#add to json file
		with open("lights_assigned.json","w") as f:
			f.write(data)
			f.close()
			
	def move_lights_database(self):
		self.buildlist()
		
	
	'''method updates the display for rooms, retrieves data from json file'''
	def update_rooms(self):
		
		self.ids.roomlayout.clear_widgets()
	
		#open json file
		with open("database1.json","r") as f:
			data = f.read()
			f.close()
		js_dict = json.loads(data)
		
		for key in js_dict:
			btn = ToggleButton(text='%s' % key,size = (400, 40),size_hint=(None,None)) #create button
			btn.bind(state=self.callback)
			self.ids.roomlayout.add_widget(btn) #add to roomlayout

		global btns_down
		btns_down = []
		global lights_down
		lights_down = []
		
	'''method writes to json file, updates the json file with new entry'''
	def write2JSON(self, dictionary):
		data = json.dumps(dictionary)
		with open("database1.json","w") as fp:
			fp.write(data)
			fp.close()
		
	'''method should store user defined room names to dict, dict is created by existing room database'''
	def store(self, arg1):
		# retrieve from database
		with open("database1.json","r") as fp:
			data = fp.read()
			fp.close()
			
		#load the data
		room_dict = json.loads(data)

		key = self.textinput.text # input given by user
		room_dict[key] = [] # stores key into dict, initialized with empty list, since its a new room
		
		self.write2JSON(room_dict) 
		self.update_rooms() 
	
	def remove_room(self):
		#load the data
		with open("database1.json","r") as g:
			data = g.read()
			g.close()
		js_dict = json.loads(data)

		#open lights_assigned.json
		with open("lights_assigned.json","r") as fp:
			d = fp.read()
			fp.close()

		#contains list from lights_assigned.json file
		lights_in_file = json.loads(d)

		#remove lights from lights_assigned.json
		#should be able to remove more than one room at a time
		for x in btns_down:
			var = js_dict.get(x) #returns list of values for key x 
			
			#delete key from database1.json file
			del js_dict[x]
			
			for element in var: #loop through each element in list
				if element in lights_in_file: #if it exists in lights_in_file then remove
					lights_in_file.remove(element)
				else: 
					print('element does not exist in lights_in_file')
					#break

		print('this is the dictionary with deleted keys')
		print(js_dict)
		
		newdata = json.dumps(lights_in_file)
		
		#update lights_assigned.json file
		with open("lights_assigned.json","w") as f:
			f.write(newdata)
			f.close()
	
		self.write2JSON(js_dict) #update database1.json file
		self.update_rooms() #updates display rooms section
		self.buildlist() # updates display lights section
		
	''' This method removes lights from the LightView, removes from database.py, user can select more than 1 light to remove'''
	def remove_light(self):
		for x in lights_down:
			removeLight(x)
			
		self.ids.gridlayout.clear_widgets()

''' This screen displays the lights assigned to a room (->View Room)'''			
class RoomView(Screen):
	def __init__(self, **kwargs):
		super(RoomView, self).__init__(**kwargs)

	'''builds a list of lights assigned to the room'''
	def build(self):
		global function_callback
		self.ids.gridlayout2.clear_widgets()
		with open("database1.json","r") as f:
			data = f.read()
			f.close()
		
		db = json.loads(data)
		if len(btns_down) > 1:
			print('error')
			pass
		elif len(btns_down) == 1:
			for key in db.keys():
				if btns_down[0] == key:
					name = key
				else:
					print('not in dict')
		else:
			pass
			
		#create object for func in LightsView
		function_callback = LightsView()
		
		try:
			for element in db[name]:
				btn = ToggleButton(text='%s' % element,size = (600, 40),size_hint=(None,None)) #create button
				btn.bind(state=function_callback.lightscallback)
				self.ids.gridlayout2.add_widget(btn) #add to gridlayout 
			self.ids.gridlayout2.bind(minimum_height=self.ids.gridlayout2.setter('height'))
		except:
			print('error')
			pass

	def set(self): 
		# Determine if only one button was pressed by user
		if len(lights_down) == 1:
			with open("database.py", "r") as d:
				my_file = d.readlines()
				d.close()
			
			#access line by line
			for line in my_file:
				curr_line = line.strip() # remove white spaces
				sec = curr_line.split() # split line
				
				#if user defined light name is equal to the light selected
				if sec[2] == lights_down[0]: 
					#grab IP address
					IP = sec[0]
					#grab data (can be changed later on)
					data = sec[1]
					self.write2workfile(IP, data)
					break
				else:
					print('not found in database')
		else:
			print('error: more than one light pressed')
			pass
		
	''' writes the full command line to the workfile such as: S IP SET DATA TIMESTAMP_ISSUED '''
	def write2workfile(self, ip_address, data_values):
			S = 'SET'
			
			#to get timestamp
			timestamp_issued = datetime.now().strftime('%H:%M:%S')
			
			#command line to write to the work file
			cmd_line = 'S' + ' ' + ip_address + ' ' + S + ' ' + data_values + ' ' + timestamp_issued
			
			#write to workfile.txt
			with open('workfile.txt', 'a') as f:
				f.write(cmd_line)
				f.write('\n')
				f.close()


'''login screen will be the first screen to execute, calls function that checks for gui commands'''
class LoginScreen(Screen):
	def login(self, username, password):
		if username in usersSet: # and password == "test":
			self.parent.current = 'homepage'
			
			#after login, these methods should execute...
			o = Methods()
			o.cmdparser() #checks workfile for commands to execute
			o.CR_update_ALL() #updates all lights stored in database with current circadian rhythm values
			#sh = Health()
			#h.check_status_ALL() #checks the status of each light that's stored in the database
			
		
		else:
			box = BoxLayout(orientation = 'vertical', padding = (5))
			box.add_widget(Label(text='Invalid username or password'))
			popup = Popup(title='Login Error', title_size =(30),title_align='center',content=box,size=(25,25),auto_dismiss=False)
			box.add_widget(Button(text='Dismiss', username = "", password="", on_press=popup.dismiss))
			popup.open()
			
			
class HomePage(Screen):
    pass

class Set(Screen):
	pass 

Builder.load_file("gui2.kv")

sm = ScreenManagement()

class TestApp(App):
	title = "Spacecraft Lighting Network System"
	def build(self):
		# return ScreenManagement()
		return sm
		
	
if __name__ == "__main__":
	TestApp().run()
	

	
