
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
from kivy.clock import Clock
import time
from datetime import datetime
import threading
from threading import Thread
from kivy.uix.colorpicker import ColorPicker
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
import sqlite3
import os
import subprocess

''' Establish database connection '''
#conn = sqlite3.connect('/home/pi/2b.db')
conn = sqlite3.connect('2b.db')
curs = conn.cursor()



workfile_path = '/home/pi/kivy/examples/workfile.txt'
database_path = '/home/pi/kivy/examples/database.py'

btns_down = []
lights_down = []

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

class ScreenManagement(ScreenManager):
	pass

''' Class contains methods that update lights to the current circadian rhythm values and checks for unprocessed commands every N seconds '''
class Methods(Screen):
	keyN = '' 
	ip = ''
	data = ''
	def __init__(self, **kwargs):
		super(Methods, self).__init__(**kwargs)
		
	def build(self, ip_addr, t_data):
		global bflag
		global ip
		global data
		
		#check if ip_addr exists in database
		curs.execute("SELECT IP_address FROM Lights WHERE IP_address = '" + ip_addr + "'")
		if(len(curs.fetchall()) != 0):
			print("Exists in database")
			pass
		else:
			print "IP address does not exist in database"
			#ip = ip_addr
			#data = t_data
			print "popup"
			#popup
		
			#box = BoxLayout(orientation = 'vertical', padding = (8))
			##message on popup
			#message = Label(text='Enter name for:', font_size=25, valign = 'middle', size_hint=(1,.3))
			#box.add_widget(message)
			#userinput = TextInput(text='', multiline =False, font_size=25, size_hint=(1, .2))
			#box.add_widget(self.userinput)
			#popup = Popup(title= 'New Light Detected', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
			#box.add_widget(Button(text='Set', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
			#popup.open()
			
			box = BoxLayout(orientation = 'vertical', padding = (8))
			box.add_widget(Label(text='Enter name for:', font_size=25, size_hint=(1,.3)))
			box.add_widget(TextInput(text=''))
			popup = Popup(title='New Light Detected', content=box, size_hint=(None, None), size=(400, 400))
			box.add_widget(Button(text='Set', font_size=20, size_hint=(.5,.3), on_release=popup.dismiss))
			popup.open()
			
		
	'''stores the user defined name for each light connected'''
	def store_name(self,arg1):
		key = self.textinput.text
		
		if key != '':
			global keyN
			keyN = key
			
			#add to database
			curs.execute("INSERT INTO Lights(IP_address,Data,Light_name) VALUES ('"+ ip + "','" + data + "','" + keyN + "')")
			conn.commit()
			
	#################################################################################################################################
		
	'''Updates all lights in database to current CR values based on time '''
	def update_lights(self):
		print "Updating ALL lights"
		time = datetime.now()
		hour = time.hour

		for row in curs.execute("SELECT IP_address FROM Lights"):
			for key in CR.keys():
				if str(hour) == key:
					data = CR[key]
					(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
					dt = "%s.%03d" % (dt, int(micro) / 1000)
					data = CR[key] #should grab value from CR dictionary
					cmd = "S" + " " + row[0] + " " + "SET" + " " + data + " " + dt
					
					#write commands into workfile
					with open("workfile.txt", "a") as workfile:
						workfile.write(cmd)
						workfile.write('\n')
					workfile.close()
					
		#t2 = threading.Timer(20.0, self.CR_update_ALL)
		#t2.daemon=True
		#t2.start()
		
	''' This method updates the new connected light to the current CR values which is based on time'''
	def update_new_light(self,ip_addr):
		print "Updating new light"
		time = datetime.now()
		print(time.hour)

		for key in CR.keys():
			(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
			dt = "%s.%03d" % (dt, int(micro) / 1000)
			if str(time.hour) == key:
				data = CR[key] #should grab value from CR dictionary
				cmd = "S" + " " + ip_addr + " " + "SET" + " " + data + " " + dt
				
				#write command to workfile
				with open("workfile.txt", "a") as workfile:
					workfile.write(cmd)
					workfile.write('\n')
				workfile.close()
	
	def removeLight(self,ip_address):
		curs.execute("DELETE FROM Lights WHERE IP_address = '" + ip_address + "'")
		conn.commit()
		
		#should populate again

	''' method used to process commands '''
	def process_cmd(self,IP, function, any_data):
		print('Processing...%s, %s, %s ' % (IP, function, any_data))
		if function == 'GET':
			s = Health()
			s.retrieveSensor(IP, any_data)
			s.getTime()
		elif function == 'ADD':
			#obj = addingLight() #works
			#obj.build(IP, any_data) #works
			self.build(IP,any_data)
			self.CR_update(IP)
		#elif function == 'TST':
			#ob = Methods()
			#ob.testingT(IP, any_data)
		elif function == 'RMV':
			self.removeLight(IP) #not working correctly
		else:
			print('Unknown function')
			
			
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
						#timestamp = datetime.now().strftime('%H:%M:%S')
						timestamp = datetime.now().strftime("%y-%m-%d-%H:%M:%S:%MS")
						new_curr = 'P '+ ' '.join(curr_line.split()[1:]) + " " + timestamp 
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
		data = '00000000'
		count = 0
		
		for row in curs.execute("SELECT IP_address FROM Lights"):
			count = count + 1
			(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
			dt = "%s.%03d" % (dt, int(micro) / 1000)
			cmd = "S" + " " + row[0] +  " " + "GET" + " " + data + " " + dt
		
			with open("workfile.txt","a") as document:
				document.write(cmd)
				document.write('\n')
			document.close()
			
		time.sleep(1)
		
		for c in range(count):
			print "checking health status"
			ob = Methods()
			ob.cmdparser()

		t3 = threading.Timer(32.0, self.check_status_ALL)
		t3.daemon=True
		t3.start()


	def health_status(self):
		
		if len(lights_down) == 1:
			#lights_down contains user's light selection on the view room screen
			self.light_name = lights_down[0]
			
			for row in curs.execute("SELECT IP_address FROM Lights WHERE IP_address='" + lights_down[0] + "'"):
				self.ip = row[0]
				(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
				dt = "%s.%03d" % (dt, int(micro) / 1000)
				cmd = "S" + " " + row[0] + " " + "GET" + " " + data + " " + dt
				
				with open("workfile.txt","a") as document:
					document.write(cmd)
					document.write('\n')
				document.close()
				
			time.sleep(1)
			
			#reads GET command
			m = Methods()
			m.cmdparser()
			self.getTime()
		elif len(lights_down) > 1 or len(lights_down) == 0:
			self.health_popup()
			
	def health_popup(self):
		box = BoxLayout(orientation = 'vertical', padding = (8))
		#message on popup
		message = Label(text='Error: Please select a light.', font_size=25, valign = 'middle', size_hint=(1,.3))
		box.add_widget(message)
		#user input
		health_popup = Popup(title= 'Error 100', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
		box.add_widget(Button(text='Return', size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_press = self.back_to_rv, on_release = health_popup.dismiss))
		health_popup.open()
		
	def back_to_rv(self, arg1):
		self.parent.current = 'view_room'
		
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

class SetValues(Screen):
	ARGB = ''
	def __init__(self, **kwargs):
		super(SetValues, self).__init__(**kwargs)
	
	def build(self):
		self.ids.setbox.clear_widgets()
		
		#create layout to display the data
		color_picker = ColorPicker()
		self.ids.setbox.add_widget(color_picker)
		
		#capture color selection
		def on_color(instance, value):
			RGBA = list(color_picker.hex_color[1:])
			
			A = (RGBA[6] + RGBA[7])
			B = (RGBA[4] + RGBA[5])
			G = (RGBA[2] + RGBA[3])
			R = (RGBA[0] + RGBA[1])
			
			global ARGB
			ARGB = A+R+G+B
			
		color_picker.bind(color=on_color) #binds to function above
	
	def set_selection(self):
		if len(lights_down) == 0:
			self.build()
			pass
		elif len(lights_down) > 1:
			self.build()
			pass
		else:
			for row in curs.execute("SELECT IP_address FROM Lights WHERE Light_name='" + lights_down[0] + "'"):
				(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
				dt = "%s.%03d" % (dt, int(micro) / 1000)
				cmd = "S" + " " + row[0] +  " " + "SET" + " " + str(ARGB) + " " + dt
		
			with open("workfile.txt","a") as document:
				document.write(cmd)
				document.write('\n')
			document.close()
		

'''This screen displays the lights available in form of buttons'''	
class LightsView(Screen):
	def __init__(self, **kwargs):
		super(LightsView, self).__init__(**kwargs)
		
	'''builds a list of light buttons with scrolling feature'''	
	def buildlist(self):
		print('building list')
		self.ids.gridlayout.clear_widgets()
		
		for row in curs.execute("SELECT Light_name FROM Lights WHERE Room='X'"):
			btn = ToggleButton(text='%s' % row[0], size = (360, 45),size_hint=(None,None)) #create button
			btn.bind(state=self.lightscallback)
			self.ids.gridlayout.add_widget(btn) #add to gridlayout 
		self.ids.gridlayout.bind(minimum_height=self.ids.gridlayout.setter('height'))

	def add_room(self):
		#popup
		box2 = BoxLayout(orientation = 'vertical', padding = (12))
		message = Label(text='Enter name for new room: ', font_size=25, halign = 'center', valign='middle', size_hint=(.8,.7))
		box2.add_widget(message)
		#user input
		self.textinput = TextInput(text='',multiline = False, size_hint=(1,.7), font_size=25)
		box2.add_widget(self.textinput)
		popup = Popup(title= 'Add New Room', content = box2, title_size =(25),title_align='center', size_hint=(.6,.6), auto_dismiss=True)
		box3 = BoxLayout(orientation ='horizontal')
		box2.add_widget(box3)
		box3.add_widget(Button(text='Set', size_hint=(.3,.8), on_press = self.store, on_release = popup.dismiss))
		box3.add_widget(Button(text='Cancel',size_hint=(.3,.8),on_press = popup.dismiss))
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
		## update room name in lights selected (by Light_name)
		for i in lights_down:
			curs.execute("UPDATE Lights SET Room='" + btns_down[0] + "' WHERE Light_name = '" + i + "'")
			conn.commit()
			
		if ((len(btns_down) == 1) and (len(lights_down) >= 1)):
			for i in lights_down:
				curs.execute("UPDATE Lights SET Room='" + btns_down[0] + "' WHERE Light_name = '" + i + "'")
				conn.commit()
		else:
			print('more than one room selected')
			pass
			
		self.update_rooms()
		self.buildlist()
	
	def room_popup(self):
		box = BoxLayout(orientation = 'vertical', padding = (8))
		#message on popup
		message = Label(text='Room name already exists', font_size=25, valign = 'middle', size_hint=(1,.3))
		box.add_widget(message)
		popup = Popup(title= 'Error 101', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
		box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
		popup.open()
	
		
	'''method should store user defined room name to table in 2b database '''
	def store(self, arg1):
		key = self.textinput.text

		curs.execute("SELECT * FROM rooms WHERE Room_name='" + key + "'")
		rows = curs.fetchall()
		if key == '':
			self.add_room
		elif len(rows) == 0:
			## add room name to rooms table on 2b database (2b.db)
			curs.execute("INSERT INTO rooms(Room_name) VALUES ('" + key + "')")
			conn.commit()
			self.update_rooms()
		else:
			self.room_popup()
		
	def update_rooms(self):
		#self.update_rooms() code below
		self.ids.roomlayout.clear_widgets()
		
		for row in curs.execute("SELECT Room_name FROM rooms"):
			btn = ToggleButton(text='%s' % row[0],size = (405, 45),spacing=10,size_hint=(None,None)) #create button
			btn.bind(state=self.callback)
			self.ids.roomlayout.add_widget(btn) #add to roomlayout

		global btns_down
		btns_down = []
		global lights_down
		lights_down = []
		
	
	def remove_room(self):
		#delete room from rooms table in 2b database
		for b in btns_down:
			curs.execute("DELETE FROM rooms WHERE Room_name='" + b + "'")
			conn.commit()

			#any light with that specific room name must be updated back to Room "X"
			curs.execute("UPDATE Lights SET Room='X' WHERE Room ='"+ b + "'")
			conn.commit()
		
		self.update_rooms()
		self.buildlist() # updates display lights section
		
	def remove_light(self):
		for k in lights_down:
			curs.execute("DELETE FROM Lights WHERE Light_name='" + k + "'")
			conn.commit()
		self.buildlist()
		
''' This screen displays the lights assigned to a room (->View Room)'''			
class RoomView(Screen):
	room_name = StringProperty()
	def __init__(self, **kwargs):
		super(RoomView, self).__init__(**kwargs)

	'''builds a list of lights assigned to the room'''
	def build(self):
		#global function_callback
		function_callback = LightsView()
		self.ids.gridlayout2.clear_widgets()

		if len(btns_down) == 1:
			try:
				self.room_name = btns_down[0]
				for row in curs.execute("SELECT Light_name FROM Lights WHERE Room='" + btns_down[0] + "'"):
					btn = ToggleButton(text='%s' % row[0],size = (580, 45),size_hint=(None,None)) #create button
					btn.bind(state=function_callback.lightscallback)
					self.ids.gridlayout2.add_widget(btn) #add to gridlayout 
				self.ids.gridlayout2.bind(minimum_height=self.ids.gridlayout2.setter('height'))
			except:
				print "cannot execute light names for room"
				pass
		else:
			print "must select a light"
			pass
		
	def clear_select(self):
		global lights_down
		lights_down = []
		
	def remove_light_rv(self):
		if len(lights_down) is None:
			pass
		elif len(lights_down) > 1:
			pass
		else:
			for k in lights_down:
				curs.execute("DELETE FROM Lights WHERE Light_name='" + k + "'")
				conn.commit()
			
			self.build()
			
'''login screen will be the first screen to execute, calls function that checks for gui commands'''
class LoginScreen(Screen):
	def login(self, username, password):
		curs.execute("SELECT * FROM users WHERE username = '" + username + "' AND password= '" + password + "'")
		if curs.fetchone() is not None:
			print "Successful Login"
			self.parent.current = 'homepage'
			#after login, these methods should execute...
			o = Methods()
			o.cmdparser() #checks workfile for unprocessed commands
			o.update_lights() #updates all lights stored in database with current circadian rhythm values
		else:
			box = BoxLayout(orientation = 'vertical', padding = (8))
			#message on popup
			message = Label(text='Invalid username or password', font_size=25, valign = 'middle', size_hint=(1,.3))
			box.add_widget(message)
			popup = Popup(title= 'Login Error', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
			box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
			popup.open()
			
class HomePage(Screen):
	pass
	
#class Set(Screen):
#	pass 


#######################################################
####################################################
############### ADD FOR JORGE ######################
####################################################
class Setting(Screen, GridLayout, BoxLayout):
    newDevControl = 1
    portsCount = 0 #Should be Plug-And-Play Value
    
    def __init__(self, **kwargs):
        super(Setting, self).__init__(**kwargs)
    
    
    def addPorts(self):
        
        self.box = BoxLayout(orientation = 'vertical', padding = (5))

        global newDevControl       
        if(self.newDevControl):
            self.myLabel = Label(text = 'Enter Number Of Ports On New Device', font_size='25sp')
            self.box.add_widget(self.myLabel)
        else:
            self.myLabel = Label(text = 'Number Must Be An Integer Value', font_size='25sp')
            self.box.add_widget(self.myLabel)

        self.popup = Popup(title = 'Add New Device',
                           title_size = (35), title_align = 'center',
                           content = self.box, size = (25,25), auto_dismiss=True)
        
        self.uInput = TextInput(text='', multiline=False, font_size='25sp')
        self.box.add_widget(self.uInput)

        self.okBtn = Button(text='Update', on_press = self.getUser, font_size='20sp', on_release=self.popup.dismiss)
        self.box.add_widget(self.okBtn)

        self.cancelBtn = Button(text='Cancel', font_size='20sp', on_press=self.popup.dismiss)
        self.box.add_widget(self.cancelBtn)
   
        self.popup.open()

   
   
    def getUser(self, arg1):
        if(self.uInput.text.isdigit()):
            global newDevControl, portsCount
            self.portsCount = self.uInput.text
            self.newDevControl = 1
            print("User Entered: {}".format(self.uInput.text))
            
        else:
            global newDeviceControl
            self.newDevControl = 0
            print("Wrong value!")
            return self.addPorts()

        
    def getPorts(self):

        self.box = BoxLayout(orientation = 'vertical', padding = (5))

        global portsCount
        self.myLabel = Label(text = ("There are " + str(self.portsCount) + " Ports Available!"), font_size='25sp')
        self.box.add_widget(self.myLabel)
        #self.box.add_widget(Label(text = ("There are " + str(self.portsCount) + " Ports Available!"), font_size='25sp'))

        self.popup = Popup(title = 'Open Ports',
                        title_size = (35), title_align = 'center',
                        content = self.box, size = (25,25), auto_dismiss=True)
        
        self.popButton = Button(text='OK', font_size='20sp', on_press=self.popup.dismiss)
        self.box.add_widget(self.popButton)
        
        self.popup.open()

        print("{} Ports".format(self.portsCount))
        
        
        
class TestOLA(Screen):

        killWeb = None
        
	def build(self):
		self.ids.testolalayout.clear_widgets()
		
		for row in curs.execute("SELECT Light_name FROM Lights WHERE Room='X'"):
			btn = ToggleButton(text='%s' % row[0], size = (780, 45),size_hint=(None,None)) #create button
			btn.bind(state=self.lightscallback, on_press=self.showOLA)
			self.ids.testolalayout.add_widget(btn) #add to gridlayout 
		self.ids.testolalayout.bind(minimum_height=self.ids.testolalayout.setter('height'))
		
		'''method checks the state of the toggle buttons for lights section'''
	def lightscallback(self, instance, value):
		print('My button <%s> state is %s' % (instance.text, value))
		if value == 'down':
                        lights_down.append(instance.text) # add to list of buttons with down state
		elif value == 'normal':
                        lights_down.remove(instance.text) # remove from list if back to normal
			print('not down')
                        

                        # Lets see if we hacec a child
                        proc = subprocess.Popen(["pidof python olaUI.py"],
                                                stdout=subprocess.PIPE, shell=True)
                        
                        (out, err) = proc.communicate()

                        # out = 6, one PID aka parent
                        if( len(out) > 8):
                                # If they pressed it again, lets kill the current window
                                # Maybe thats what they ment by pressing it again.
                                # Otherwise, it will show another windows and there will
                                # no be two windows for the same thing.
                                
                                os.system(" kill  $(pidof python olaUI.py | awk '{print $1}')")
                                #os.system("pkill -P $(pidof python olaUI.py)")
                        else:
                                pass

                         
		else:
			pass
		
	def showOLA(self, arg1):
		if len(lights_down) == 1:
			for row in curs.execute("SELECT IP_address FROM Lights WHERE Light_name= '" + lights_down[0] + "'"):
				ip = row[0]
				#print(ip)

                                os.system("python olaUI.py "+ ip + " &")
                                print(TestOLA.killWeb)
                                        
                else:
                        pass

###########################################################
############### END OF ADD FOR JORGE ######################
###########################################################
###########################################################


Builder.load_file("gui8J.kv")
sm = ScreenManagement()

class TestApp(App):
	title = "Spacecraft Lighting Network System"
	def build(self):
		# return ScreenManagement()
		return sm
		
if __name__ == "__main__":
	TestApp().run()

conn.close() #close database connection 
