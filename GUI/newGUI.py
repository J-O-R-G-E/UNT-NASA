"""
By Gladys Hernandez
   Jorge Cardona*
   Taylor Shinn**

This is the User's Graphical Interface for our project.
It communicates with a TCP server written in C++.
All its information entred and retrieved by the user
are stored in a database using SQLite3 which means that even
if the GUI crahsed, all information such as Logins, Passwords, and
user defined values are kept alive.

...

* = Jorge Cardona only added a small fraction to the entire functionality 
of this GUI. Under the 'Settings' button, the 'Add New Device', 'Ports Available',
and 'Test OLA' were implemented.

** = Taylor Shinn ...

"""


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
from time import sleep
from datetime import datetime
import threading
from threading import Thread
from kivy.uix.colorpicker import ColorPicker
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
import sqlite3
import os
import subprocess

""" Establish database connection """
conn = sqlite3.connect('/home/pi/2b.db',check_same_thread=False) 
curs = conn.cursor()

#workfile_path = '/home/pi/kivy/examples/workfile.txt'
workfile_path = 'workfile.txt'

btns_down = []
lights_down = []

"""Circadian Rhythm dictionary - VALUES NEED TO BE CHANGED"""
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

""" Class contains methods that update lights to the current circadian rhythm values and checks for unprocessed commands every N seconds """
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
			ip = ip_addr
			data = t_data
			
			box = BoxLayout(orientation = 'vertical', padding = (8))
			box.add_widget(Label(text='Enter name for:', font_size=25, size_hint=(1,.3)))
			self.textinput = TextInput(text='')
			box.add_widget(self.textinput)
			popup = Popup(title='New Light Detected', content=box, size_hint=(None, None), size=(400, 400), auto_dismiss=False)
			box.add_widget(Button(text='Set', font_size=20, size_hint=(.5,.3), on_press= self.store_name, on_release=popup.dismiss))
			popup.open()
			
		
	"""stores the user defined name for each light connected"""
	def store_name(self,arg1):
		key = self.textinput.text
		
		if key != '':
			global keyN
			keyN = key
			
			#add to database
			curs.execute("INSERT INTO Lights(IP_address,Data,Light_name) VALUES ('"+ ip + "','" + data + "','" + keyN + "')")
			conn.commit()
			
	#################################################################################################################################
		
		
	def return_to_previous(self, scr):
		sm.current = scr
		
	"""Updates all lights in database to current CR values based on time """
	def update_lights(self):
		print "Updating ALL lights"
		time = datetime.now()
		hour = time.hour
		
		if hour == 0:
			hour = '0' + str(hour)
		else:
			pass

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
					
		t2 = threading.Timer(10.0, self.update_lights)
		t2.daemon=True
		t2.start()

		
	""" This method updates the new connected light to the current CR values which is based on time"""
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

	""" method used to process commands """
	def process_cmd(self,IP, function, any_data):
		print('Processing...%s, %s, %s ' % (IP, function, any_data))
		if function == 'GET':
			s = Health()
			s.retrieveSensor(IP, any_data)
			s.getTime()
		elif function == 'ADD':
			#grab current screen
			current_screen  = sm.current
			sm.current = 'homepage'
			self.build(IP,any_data)
			self.update_new_light(IP)
			if sm.current != 'view_lights':
				pass
			else:
				sm.current = 'view_lights'
			
		elif function == 'RMV':
			s = LightsView()
			#s.removeLight(IP)
			s.buildlist2(IP)
		else:
			print('Unknown function')
			
			
	def cmdparser(self):
		print('cmdparser running')
		
		""" This method changes 'G' to 'P' when command has been processed"""
		def replace_line(file_name, line_no, text):
			lines = open(file_name, 'r+').readlines()
			lines[line_no] = text + '\n'
			out = open(file_name, 'w')
			out.writelines(lines)
			out.close()
			
		dfile = open(workfile_path, 'r')
		myfile = dfile.readlines()
		line_num = -1 #to get line number, starts at 0
		for line in myfile:
			if line == '\n':
				pass
			else:
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
					(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
					dt = "%s.%03d" % (dt, int(micro) / 1000)
					new_curr = 'P '+ ' '.join(curr_line.split()[1:]) + " " + dt
					replace_line(workfile_path, line_num, new_curr)
					break
				else:
					pass

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
				(dt, micro) = datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]').split('.')
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
		
	""" method retrieves sensor values, this is called after m.cmdparser()"""
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
		
	""" method retrieves the current time and date"""
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
	
	""" method retrieves current circadian rhythm values and calculates health status"""
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
		

"""This screen displays the lights available in form of buttons"""	
class LightsView(Screen):
	def __init__(self, **kwargs):
		super(LightsView, self).__init__(**kwargs)
		
	def removeLight(self,ip_address):
		for row in curs.execute("SELECT Light_name FROM Lights WHERE IP_address = '" + ip_address + "'"):
			print(row[0])
			if btn.id == row[0]:
				print(btn.id)
				self.ids.gridlayout.remove_widget(btn)
			else:
				pass
				
		#try:
			#for row in curs.execute("SELECT Light_name FROM Lights WHERE IP_address='" + ip_address + "'"):
				#name = row[0]
				##update screen
				#curs.execute("DELETE FROM Lights WHERE IP_address = '" + ip_address + "'")
				#conn.commit()
				#box = BoxLayout(orientation = 'vertical', padding = (8))
				##message on popup
				#message = Label(text='Removing {}, {}'.format(ip_address, name), font_size=25, valign = 'middle', size_hint=(1,.3))
				#box.add_widget(message)
				#popup = Popup(title= 'Light Removal', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				#box.add_widget(Button(text='Confirm', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_press= self.new_update, on_release = popup.dismiss))
				#popup.open()
		#except:
			#print('not working')
		
	def new_update(self, arg1):
		#get current screen
		screen_name = sm.current
		#check whether if it's already in view_lights screen
		if sm.current == 'view_lights':
			print('the temp page is view lights')
		else:
			print('the temp page is not view lights')
			
		#redirect to homepage temporary
		sm.current = 'homepage'
		
		#popup to view new changes (light removal)
		#if YES -> redirect to view_lights screen and if NO -> redirect to the previous screen that user was in 
		box = BoxLayout(orientation = 'vertical', padding = (8))
		#message on popup
		message = Label(text='View new changes?', font_size=25, valign = 'middle', size_hint=(1,.3))
		box.add_widget(message)
		popup = Popup(title= 'Update', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
		box.add_widget(Button(text='YES', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_press= self.go_to_view_lights,on_release = popup.dismiss))
		box.add_widget(Button(text='NO', font_size=20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_press = lambda *args: self.previous_screen(screen_name, *args), on_release=popup.dismiss))
		popup.open()

	def previous_screen(self, sn, arg2):
		if sm.current == sn:
			print "do nothing"
			pass
		else:
			newob = Methods()
			newob.return_to_previous(sn)
	
	def go_to_view_lights(self, arg1):
		sm.current = 'view_lights'
		
	"""builds a list of light buttons with scrolling feature"""	
	def buildlist(self):
		print('building list')
		self.ids.gridlayout.clear_widgets()
		
		for row in curs.execute("SELECT Light_name FROM Lights WHERE Room='X'"):
			btn = ToggleButton(id = row[0], text='%s' % row[0], size = (360, 45),size_hint=(None,None)) #create button
			#btn.bind(state=self.initialize)
			btn.bind(state=self.lightscallback)
			#store id into database
			#curs.execute("UPDATE Lights SET ID='" + row[0] + "' WHERE Light_name= '" + row[0] + "'")
			#conn.commit()
			#btn.state = 'down'
			#btn.state = 'normal'
			self.ids.gridlayout.add_widget(btn) #add to gridlayout 
		self.ids.gridlayout.bind(minimum_height=self.ids.gridlayout.setter('height'))
		
	def buildlist2(self, ip):
		for row in curs.execute("SELECT Light_name FROM Lights WHERE IP_address = '" + ip +"'"):
			ln = row[0]
		
		print('building list')
		self.ids.gridlayout.clear_widgets()
		
		for row in curs.execute("SELECT Light_name FROM Lights WHERE Room='X'"):
			btn = ToggleButton(id = row[0], text='%s' % row[0], size = (360, 45),size_hint=(None,None)) #create button
			btn.bind(state=self.lightscallback)
			self.ids.gridlayout.add_widget(btn) #add to gridlayout 
			btn.state = 'down'
			btn.state = 'up'
		self.ids.gridlayout.bind(minimum_height=self.ids.gridlayout.setter('height'))
		
		
		
		if btn.id == ln:
			self.ids.gridlayout.remove_widget(btn)
			curs.execute("DELETE FROM Lights WHERE IP_address = '" + ip + "'")
			conn.commit()
			pass
		else:
			pass

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
		
	#def initialize(self, instance, value):
		
		
		
	"""method checks the state of the toggle buttons for lights section"""
	def lightscallback(self, instance, value):
		
		print('My button instance is %s,  <%s> state is %s' % (instance,instance.text, value))
		curs.execute("UPDATE Lights SET ID='" + str(instance) + "' WHERE IP_address = '" + instance.text + "'")
		conn.commit()
		if value == 'down':
			lights_down.append(instance.text) # add to list of buttons with down state
		elif value == 'normal':
			lights_down.remove(instance.text) # remove from list if back to normal
			print('not down')
		else:
			pass
		print(lights_down)
		
	"""method checks the state of the toggle buttons for rooms section"""		
	def callback(self,instance, value):

		print('My button <%s> state is %s' % (instance.text, value))
		if value == 'down':
			btns_down.append(instance.text) # add to list of buttons with down state
		elif value == 'normal':
			btns_down.remove(instance.text) # remove from list if back to normal
			print('not down')
		else:
			pass
	
	"""method adds lights selected by user to a specific room"""
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
	
		
	"""method should store user defined room name to table in 2b database """
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
			#retrieve IP address from database
			for row in curs.execute("SELECT IP_address FROM Lights WHERE Light_name='" + k + "'"):
				data = "00000000"
				(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
				dt = "%s.%03d" % (dt, int(micro) / 1000)
				cmd = "S" + " " + row[0] + " " + "RMV" + " " + data + " " + dt
				with open("workfile.txt","a") as document:
					document.write(cmd)
					document.write('\n')
				document.close()
				
			#delete client from database
			curs.execute("DELETE FROM Lights WHERE Light_name='" + k + "'")
			conn.commit()
				
		self.buildlist()

""" This screen displays the lights assigned to a room (->View Room)"""			
class RoomView(Screen):
	room_name = StringProperty()
	def __init__(self, **kwargs):
		super(RoomView, self).__init__(**kwargs)

	"""builds a list of lights assigned to the room"""
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
		
	#unassign lights from room
	def unassign_lights(self):
		if len(lights_down) == 0:
			pass
		else:
			for k in lights_down:
				curs.execute("UPDATE Lights SET Room='X' WHERE Light_name='" + k + "'")
				conn.commit()
			self.build()
			
"""login screen will be the first screen to execute, calls function that checks for gui commands"""
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
	#pass 



####################################################
####################################################
############### ADD FOR JORGE ######################
####################################################
""" The Settings Button. 
It allows the user to test lights by sending custom colors.
Add new devices and see how many ports are abalable at that time. """
class Setting(Screen, GridLayout, BoxLayout):
    newDevControl = 1
    portsCount = 0 #Should be Plug-And-Play Value
    
    def __init__(self, **kwargs):
        super(Setting, self).__init__(**kwargs)
    
    """ This method process the user's input """
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

   
    """ This method gets called whe user wants to add a new device """   
    def getUser(self, arg1):
        if(self.uInput.text.isdigit()):
            global newDevControl, portsCount
            
            # Make sure add them as numbers and not as strings
            self.old = int(self.portsCount)
            self.new = int(self.uInput.text)
            self.new += self.old

            self.portsCount = str(self.new)
            self.newDevControl = 1
            
            curs.execute("UPDATE PORTS SET Amount='" + self.portsCount + "'")
            conn.commit()
  
            print("User Entered: {}".format(self.uInput.text))
            
        else:
            global newDeviceControl
            self.newDevControl = 0
            print("Wrong value!")
            return self.addPorts()



    """ This method gets call when the user want to see how many ports are avalable """
    def getPorts(self):

        global portsCount
        for row in curs.execute("SELECT * FROM Ports"):
		self.portsCount = row[0]                       

        ##############################################################
        # Taylor, here is where I need to get your Plug And Play value
        # so I can substract it from the total ports count.
        # This is how I will be able to show the ports available
        #
        # e.g.: self.portsCount -= plugAnPlaCount      
        #############################################################
        
        self.box = BoxLayout(orientation = 'vertical', padding = (5))
        self.myLabel = Label(text = ("There are " + str(self.portsCount) + " Ports Available!"), font_size='25sp')
        self.box.add_widget(self.myLabel)
        #self.box.add_widget(Label(text = ("There are " + str(self.portsCount) + " Ports Available!"), font_size='25sp'))

        self.popup = Popup(title = 'Open Ports',
                        title_size = (35), title_align = 'center',
                        content = self.box, size = (25,25), auto_dismiss=True)
        
        self.popButton = Button(text='OK', font_size='20sp', on_press=self.popup.dismiss)
        self.box.add_widget(self.popButton)
        
        self.popup.open()


        ############################################################
        # IF PORTS >= 2048. AKA SOMAXCONN has been reached,        #
        # Call the script that updates this ammount.               #
        # Maybe Create another instance of the servere?            #
        # If SOMAXCONN is updated, I may need to reboot the system #
        # Maybe Create a warning pop up telling the user what is   #
        # about to happen so that they dont think they crashed the #
        # GUI by adding that new devicew                           #
        ############################################################
            
        
        print("{} Ports".format(self.portsCount))
        
        


# For Color WHeel Only
testOLAColors = None
""" This class is for the color wheel popup."""
class ColorSelector(Popup):
        
        """ This method adds the selected colors to the workfile.txt"""
        def on_press_dismiss(self, colorPicker, *args):
                
                self.dismiss()
                #Gets as it was selected - x
                RGBA = list(colorPicker.hex_color[1:])
                
                As = str(RGBA[6]) + str(RGBA[7])
                Rs = str(RGBA[0])  +  str(RGBA[1])
                Gs = str(RGBA[2]) + str(RGBA[3])
                Bs = str(RGBA[4]) + str(RGBA[5])

                ARGBs = As+Rs+Gs+Bs + " "
                
                (dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
		dt = "%s.%03d" % (dt, int(micro) / 1000)
		ARGBs  += dt
		
		# Finish the Command
		with open("testOLA", "a") as f:
			f.write(ARGBs)
			f.write('\n')
		f.close()

                
                # make the file empty
                os.system("cat testOLA >> workfile.txt ; echo \" \" > testOLA")
                               
                return True

""" This class shows the screen with all the lights available to test """
class TestOLA(Screen):

        """ This method handles all the layout of the current screen """
        def build(self):
		self.ids.testolalayout.clear_widgets()
		
		for row in curs.execute("SELECT Light_name FROM Lights WHERE Room='X'"):
			btn = ToggleButton(text='%s' % row[0], size = (780, 45),size_hint=(None,None)) #create button
			btn.bind(state=self.lightscallback, on_press=self.showOLA)
			self.ids.testolalayout.add_widget(btn) #add to gridlayout 
		self.ids.testolalayout.bind(minimum_height=self.ids.testolalayout.setter('height'))

	
	"""method checks the state of the toggle buttons for lights section"""
	def lightscallback(self, instance, value):
		print('My button <%s> state is %s' % (instance.text, value))
		if value == 'down':
                      	lights_down.append(instance.text) # add to list of buttons with down state
                        
                        
		elif value == 'normal':
			lights_down.remove(instance.text) # remove from list if back to normal
			print('not down')
                        
		else:
			pass
		
        """ This methos was to show the actual OLA Dashboard, but now is just a helper for the color wheel """
        def showOLA(self, arg1):
		if len(lights_down) == 1:

                        # Show Color wheel
                        self.aColor  = ColorSelector()
                        self.aColor.open()

                        # Prepare for color selection
                        for row in curs.execute("SELECT IP_address FROM Lights WHERE Light_name='" + lights_down[0] + "'"):
			        cmd = "S "  + row[0] +  " " + "SET" + " "
		                ip = row[0]
				#print(ip)
                                

                        with open("testOLA","a") as f:
				f.write(cmd)
                        f.close()
                                
                        			        
		else:
			pass
        

###########################################################
############### END OF ADD FOR JORGE ######################
###########################################################
###########################################################

Builder.load_file("gui8.kv")
sm = ScreenManagement()

class TestApp(App):
	title = "Spacecraft Lighting Network System"
	def build(self):
		# return ScreenManagement()
                  
                ####################################################
                ############### ADD FOR JORGE ######################
                ####################################################
                self.color_selector = ColorSelector()
                
                return sm
		
if __name__ == "__main__":
        #Run voice commands at boot up
        os.system('python /home/pi/Desktop/UNT-NASA/voiceOLA/voiceOLA.py > /dev/null 2>&1 &')

        #For Testing Individual Lights
        os.system("touch testOLA")

        # Run the GUI
        TestApp().run()

conn.close() #close database connection 

# Replaces ''' with """ to allow Doxygen 
#sed "s/'''/\"\"\"/g" GUI8.py
