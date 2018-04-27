""" SLNS Graphical User Interface 2018
	Written by Gladys Hernandez-Amaya	gh0151@unt.edu
	Course: CSCE 4915
	Faculty Advisor: Robin P.
	File Description: This python application displays the menu functions for the SLNS. 
	It issues commands for the server and writes them to workfile.txt, and processes 
	commands from the server by reading workfile.txt. Kivy is an open source,
	cross-platform python framework that is used in this application. This file and
	the .kv should be be stored under the same directory.

	Jorge Cardona colaborated on this GUI by adding the 'Settings' portion.
	This portion allows for users to add new devices, most importatly, the port count.
	It also allows the user to see how many ports are not being used aka available.
	And finally, it allows for the users to test specific color values, selected from a
	color wheel, to be sent to that particular light.

"""
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
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
from kivy.clock import Clock


""" Establish database connection """
conn = sqlite3.connect('/home/pi/UNT-NASA/2b.db',check_same_thread=False) 
#conn = sqlite3.connect('/home/pi/2b.db',check_same_thread=False) 
curs = conn.cursor()
curs2 = conn.cursor()

workfile_path = "/home/pi/UNT-NASA/workfile.txt"
#workfile_path = "/home/pi/kivy/examples/workfile.txt"

btns_down = []
lights_down = []
instances = []

"""Circadian Rhythm values dictionary - VALUES NEED TO BE CHANGED"""
CR = {
'00':'FF5454FF',
'01':'FF545454',
'02':'FF545454',
'03':'FF545454',
'04':'FF545454',
'05':'FF545454',
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
'17':'FF545454',
'18':'FF545454',
'19':'FF545454',
'20':'FF545454',
'21':'FF545454',
'22':'FF545454',
'23':'FF545454'}

class ScreenManagement(ScreenManager):
	pass
	
""" Class contains methods that update lights to the current circadian rhythm values and checks for unprocessed commands every N seconds """
class Methods(Screen):
	keyN = '' 
	ip = ''
	d = ''
	cmd_processed = False
	process_cmd = False
	
	def __init__(self, **kwargs):
		super(Methods, self).__init__(**kwargs)
		
	#stores the user defined name for each light connected`
	def store_name(self, ip, data):
		key = self.textinput.text
		curr_screen = sm.current
		
		try:
			if key != '':
				print("updating keyN")
				global keyN
				keyN = key
				#add to database
				curs.execute("INSERT INTO Lights(IP_address,Data,Light_name) VALUES ('"+ ip + "','" + data + "','" + keyN + "')")
				conn.commit()
				#global cmd_processed
				self.cmd_processed = False
				self.process_cmd = False
				if sm.current == 'view_lights':
					sm.current = 'blank_screen'
					sm.current = 'view_lights'
				else:
					pass
		except:
			pass
			
	#################################################################################################################################

	#Updates all lights in database to current CR values based on time 
	def update_lights(self, arg1):
		try:
			
			print "Updating ALL lights"
			time = datetime.now()
			hour = time.hour
			
			if len(str(hour)) == 1: 
				hour = '0' + str(hour)
				print "changing"
			else:
				pass
			
			curs2.execute("SELECT IP_address FROM Lights")
			addresses = curs2.fetchall()
			addr =[r[0] for r in addresses]
			
			for a in addr:
				for key in CR.keys():
					if str(hour) == key:
						data = CR[key]
						(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
						dt = "%s.%03d" % (dt, int(micro) / 1000)
						data = CR[key] #should grab value from CR dictionary
						cmd = "S" + " " + a + " " + "SET" + " " + data + " " + dt
						
						#write commands into workfile
						with open("workfile.txt", "a") as workfile:
							workfile.write(cmd)
							workfile.write('\n')
						workfile.close()
					else:
						pass
						
						
			t2 = threading.Timer(50.0, self.update_lights)
			t2.daemon=True
			t2.start()
		
		except TypeError:
			print "type error in update_lights"

		
	""" This method updates the new connected light to the current CR values which is based on time """
	def update_new_light(self,ip_addr):
		print "Updating new light"
		time = datetime.now()
		
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

			
	#This method changes 'G' to 'P' when command has been processed 
	def replace_line(self, file_name, line_no, text):
		print "replacing lines"
		lines = open(file_name, 'r+').readlines()
		lines[line_no] = text + '\n'
		out = open(file_name, 'w')
		out.writelines(lines)
		out.close()
				
				
	"""This method parses the commands on the workfile"""		
	def cmdparser(self, arg1):
		print('cmdparser running')
		
		try:
			if(self.cmd_processed == False):
				print "reading wf"
				dfile = open(workfile_path, 'r')
				myfile = dfile.readlines()
				line_num = -1 #to get line number, starts at 0
				for line in myfile:
					print(line)
					if line == '\n':
						pass
					else:
						line_num +=1 	#keep line count
						curr_line = line.strip() #strip line to remove whitespaces
						parts = curr_line.split() #split line
						try:
							if parts[0] == 'G':
								#Store IP_addr, function and data, if available
								IP_addr = parts[1]
								func = parts[2]
								data = parts[3]

								if(self.process_cmd == False):
									
									self.cmd_processed = True
									self.process_cmd = True
									global ip
									global d
									ip = IP_addr
									d = data
									print "processing"
									
									if func == 'ADD':
										#check if ip_addr exists in database
										curs.execute("SELECT IP_address FROM Lights WHERE IP_address = '" + ip + "'")
										if(len(curs.fetchall()) != 0):
											print("Exists in database")
											pass
										else:
											print "IP address does not exist in database"
											box = BoxLayout(orientation = 'vertical', padding = (8))
											box.add_widget(Label(text='Enter a name for {}:'.format(ip), font_size=30, size_hint=(1,.7)))
											self.textinput = TextInput(text='', font_size=30)
											box.add_widget(self.textinput)
											self.popup = Popup(title='New Light Detected', content=box, title_size=30, size_hint=(None, None), size=(450, 300), title_align='center', auto_dismiss=False)
											#box.add_widget(Button(text='Set',font_size=25, size_hint=(.5,.7), pos_hint={'center_x': .5, 'center_y': 0},on_release=popup.dismiss))
											box.add_widget(Button(text='Set',font_size=25, size_hint=(.5,.7), pos_hint={'center_x': .5, 'center_y': 0}, on_press= lambda *args: self.store_name(ip,d), on_release = self.popup.dismiss))
											self.popup.open()

											print "updating light"
											#self.update_new_light(ip)
											print "replacing line"
											(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
											dt = "%s.%03d" % (dt, int(micro) / 1000)
											new_curr = 'P '+ ' '.join(curr_line.split()[1:]) + " " + dt
											try:
												self.replace_line(workfile_path, line_num, new_curr)
												#self.process_cmd = False
											except:
												print "error in replacing"
									
									elif func == 'SHD':
										s = LightsView()
										s.removeLight(ip)
										self.cmd_processed = False
										self.process_cmd = False
										print "replacing line"
										(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
										dt = "%s.%03d" % (dt, int(micro) / 1000)
										new_curr = 'P '+ ' '.join(curr_line.split()[1:]) + " " + dt
										try:
											self.replace_line(workfile_path, line_num, new_curr)
											#self.process_cmd = False
										except:
											print "error in replacing"
									
									elif func == 'GET':
										#h = Health()
										#h.retrieveSensor(ip)
										#store data into database
										print "updating data on database"
										curs2.execute("UPDATE Lights SET Data='" + d + "' WHERE IP_address='" + ip + "'")
										conn.commit()
										self.cmd_processed = False
										self.process_cmd = False
										try:
											self.replace_line(workfile_path, line_num, new_curr)
										except:
											print "error in replacing"

									else:
										print "fourth if"
										pass	
								else:
									print "third if"
									pass
								
							else:
								print "second if"
								pass
								
						except IndexError:
							pass
								
										
			else:
				print "first if"
				pass
				
		except IOError:
			print "IO Error"
			pass



""" Health status, of the light, class"""
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

        """ This method checks the status of all lights in the DB"""
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

	
	def retrieve_data(self):
		self.time = datetime.now().strftime('%H:%M')
		self.date = datetime.now().strftime('%Y-%m-%d')
		
		#hours go by [00-23]
		hour = str(datetime.now().hour)
		if len(hour) == 1:
			hour = '0' + str(datetime.now().hour)
		else:
			pass
			
		global A
		global R
		global G
		global B
		
		self.light_name = lights_down[0]
		print "grabbing data"
		for row in curs.execute("SELECT Data FROM Lights WHERE Light_name='" + lights_down[0] + "'"):
			print(row[0])
			d = row[0]
			if d == '0':
				A = int(0)
				R = int(0) 
				G = int(0)
				B = int(0)
				
				self.sa = str(A)
				self.sr = str(R)
				self.sg = str(G)
				self.sb = str(B)

			else:
				A = int(d[0] + d[1], 16)
				R = int(d[2] + d[3], 16) 
				G = int(d[4] + d[5], 16)
				B = int(d[6] + d[7], 16)
				
				self.sa = str(A)
				self.sr = str(R)
				self.sg = str(G)
				self.sb = str(B)
		
		for row in curs2.execute("SELECT IP_address FROM Lights WHERE Light_name='" + lights_down[0] + "'"):
			self.ip = row[0]
		
		self.retrieveCR_and_status(hour)
		print "entering retrieveCR_and_status"


        """This method shows the status of the light to the user"""
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
		
	def send_get_cmd(self, arg1):
		for row in curs.execute("SELECT IP_address FROM Lights"):
			(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
			dt = "%s.%03d" % (dt, int(micro) / 1000)
			cmd = "S" + " " + row[0] +  " " + "GET" + " " + "00000000" + " " + dt
			
			with open("workfile.txt","a") as document:
					document.write(cmd)
					document.write('\n')
			document.close()
			
	""" method retrieves sensor values """
	#def retrieveSensor(self, ip_addr):
		##self.grab_name(ip_addr)
		#print(' The values received from server: %s , %s' % (ip_addr))
		
		#global A
		#global R
		#global G
		#global B

		#for row in curs.execute("SELECT Data FROM Lights WHERE IP_address = '" + ip_addr + "'"):
			##hex to decimal conversion
			#d = row[0]
			#A = int(d[0] + d[1], 16)
			#R = int(d[2] + d[3], 16) 
			#G = int(d[4] + d[5], 16)
			#B = int(d[6] + d[7], 16)
			
			#print('%d %d %d %d' % (A,R,G,B)) 
			
	""" method retrieves current circadian rhythm values and calculates health status """
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
		
		##display sensor values
		##error, sensor values not present yet. 
		#self.sa = str(A)
		#self.sr = str(R)
		#self.sg = str(G)
		#self.sb = str(B)
		
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
		try:
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
		except:
			print "Error in set_selection"


""" This screen displays the lights available in form of buttons """
class LightsView(Screen):
	def __init__(self, **kwargs):
		self.layout = None
		super(LightsView, self).__init__(**kwargs)
		
	def clear_lights_selection(self):
		try:
			lights_down = []
		except ValueError:
			print("value error")

		
	def removeLight(self, ip_addr):
		try:
			curs.execute("SELECT Light_name FROM Lights WHERE IP_address='" + ip_addr + "'")
			n = curs.fetchone()
			name = n[0]
				
			#get current screen
			curr_screen = sm.current
			
			curs.execute("DELETE FROM Lights WHERE IP_address = '" + ip_addr + "'")
			conn.commit()
			
			if curr_screen == 'view_lights':
				box = BoxLayout(orientation = 'vertical', padding = (8))
				message = Label(text='Removing IP: {}, Name: {}'.format(ip_addr, name), font_size=25, valign = 'middle', size_hint=(1,.3))
				box.add_widget(message)
				popup = Popup(title= 'Light Removal', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box.add_widget(Button(text='Confirm and Refresh', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_press= self.screen_update, on_release = popup.dismiss))
				popup.open()
			else:
				box2 = BoxLayout(orientation = 'vertical', padding = (8))
				message = Label(text='Removing IP: {}, Name: {}'.format(ip_addr, name), font_size=25, valign = 'middle', size_hint=(1,.3))
				box2.add_widget(message)
				popup2 = Popup(title= 'Light Removal', content = box2, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box2.add_widget(Button(text='Confirm', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup2.dismiss))
				popup2.open()
		except:
			pass

	def screen_update(self, arg1):
		sm.current = 'blank_screen'
		sm.current = 'view_lights'

	""" builds a list of light buttons with scrolling feature """
	def buildlist(self):
		
		self.ids.gridlayout.clear_widgets()
				
		print('building list')
		curs.execute("SELECT Light_name FROM Lights WHERE Room='X'")
		data = curs.fetchall()
			
		instances =[r[0] for r in data]
		print(instances)
		
		for inst in instances:
			self.btn = ToggleButton(text='%s' % inst, size = (340, 45),size_hint=(None,None)) #create button
			self.btn.bind(state=self.lightscallback)
			self.ids.gridlayout.add_widget(self.btn) #add to gridlayout 
		self.ids.gridlayout.bind(minimum_height=self.ids.gridlayout.setter('height'))


	def add_room(self):
		box2 = BoxLayout(orientation = 'vertical', padding = (12))
		message = Label(text='Enter name for new room: ', font_size=25, halign = 'center', valign='middle', size_hint=(.8,.7))
		box2.add_widget(message)
		self.textinput = TextInput(text='',multiline = False, size_hint=(1,.7), font_size=25)
		box2.add_widget(self.textinput)
		popup = Popup(title= 'Add New Room', content = box2, title_size =(25),title_align='center', size_hint=(.6,.6), auto_dismiss=False)
		box3 = BoxLayout(orientation ='horizontal')
		box2.add_widget(box3)
		box3.add_widget(Button(text='Set', size_hint=(.3,.8), on_press = self.store, on_release = popup.dismiss))
		box3.add_widget(Button(text='Cancel',size_hint=(.3,.8),on_press = popup.dismiss))
		popup.open()
		
	def store_state(self, btn_name, btn):
		#add instance to ID section on database table
		curs.execute("UPDATE Lights SET ID='" + str(btn) + "' WHERE Light_name='" + btn_name +"'")
		conn.commit()

	""" method checks the state of the toggle buttons for lights section """
	def lightscallback(self, instance, value):
		try:
			print('My button instance is %s,  <%s> state is %s' % (instance,instance.text, value))
			if value == 'down':
				lights_down.append(instance.text) # add to list of buttons with down state
			elif value == 'normal':
				lights_down.remove(instance.text) # remove from list if back to normal
				print('not down')
			else:
				pass
		except ValueError:
			print("Value error")
	
	""" method checks the state of the toggle buttons for rooms section """
	def callback(self,instance, value):
		try:
			print('My button <%s> state is %s' % (instance.text, value))
			if value == 'down':
				btns_down.append(instance.text) # add to list of buttons with down state
			elif value == 'normal':
				btns_down.remove(instance.text) # remove from list if back to normal
				print('not down')
			else:
				pass
		except ValueError:
			print("Value error")
	
	""" method adds lights selected by user to a specific room """
	def add_to_room(self):
		try:
			if(len(btns_down) == 0):
				box = BoxLayout(orientation = 'vertical', padding = (8))
				#message on popup
				message = Label(text='Please select or create a room', font_size=25, valign = 'middle', size_hint=(1,.3))
				box.add_widget(message)
				popup = Popup(title= 'Error 105', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
				popup.open()
					
			elif((len(btns_down) == 1) and (len(lights_down) >= 1)):
				for i in lights_down:
					curs.execute("UPDATE Lights SET Room='" + btns_down[0] + "' WHERE Light_name = '" + i + "'")
					conn.commit()
			elif((len(btns_down) == 1) and (len(lights_down) <= 0)):
				box = BoxLayout(orientation = 'vertical', padding = (8))
				#message on popup
				message = Label(text='0 lights selected', font_size=25, valign = 'middle', size_hint=(1,.3))
				box.add_widget(message)
				popup = Popup(title= 'Error 104', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
				popup.open()
			else:
				box = BoxLayout(orientation = 'vertical', padding = (8))
				#message on popup
				message = Label(text='More than 1 room selected', font_size=25, valign = 'middle', size_hint=(1,.3))
				box.add_widget(message)
				popup = Popup(title= 'Error 104', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
				popup.open()
				
			self.update_rooms()
			self.buildlist()
		except IndexError:
			print("Index error")
	
	def room_popup(self):
		box = BoxLayout(orientation = 'vertical', padding = (8))
		#message on popup
		message = Label(text='Room name already exists', font_size=25, valign = 'middle', size_hint=(1,.3))
		box.add_widget(message)
		popup = Popup(title= 'Error 101', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
		box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
		popup.open()
	
		
	""" method should store user defined room name to table in 2b database """
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
				cmd = "S" + " " + row[0] + " " + "SHD" + " " + data + " " + dt
				with open("workfile.txt","a") as document:
					document.write(cmd)
					document.write('\n')
				document.close()
				
			#remove client from database
			curs.execute("DELETE FROM Lights WHERE Light_name='" + k + "'")
			conn.commit()
		self.buildlist()
		
	def check_lights_selected(self):
		try:
			if(len(lights_down) == 0):
				#popup
				box_2 = BoxLayout(orientation = 'vertical', padding = (8))
				#message on popup
				message = Label(text=' 0 lights selected', font_size=25, valign = 'middle', size_hint=(1,.3))
				box_2.add_widget(message)
				popup_2 = Popup(title= 'Error 106', content = box_2, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box_2.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_release = popup_2.dismiss))
				popup_2.open()
			elif(len(lights_down) > 1):
				#poup
				box_1 = BoxLayout(orientation = 'vertical', padding = (8))
				#message on popup
				message = Label(text='More than 1 light selected', font_size=25, valign = 'middle', size_hint=(1,.3))
				box_1.add_widget(message)
				popup_1 = Popup(title= 'Error 107', content = box_1, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box_1.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_release = popup_1.dismiss))
				popup_1.open()
			else:
				sm.current = 'set_values'
		except:
			print "Error in check_lights_selected"
				
	def health_check_selected(self):
		try:
			if len(lights_down) == 1:
				sm.current = 'health'
				
			elif(len(lights_down) == 0):
				#popup
				box_2 = BoxLayout(orientation = 'vertical', padding = (8))
				#message on popup
				message = Label(text=' 0 lights selected', font_size=25, valign = 'middle', size_hint=(1,.3))
				box_2.add_widget(message)
				popup_2 = Popup(title= 'Error 106', content = box_2, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box_2.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_release = popup_2.dismiss))
				popup_2.open()
			elif(len(lights_down) > 1):
				#poup
				box_1 = BoxLayout(orientation = 'vertical', padding = (8))
				#message on popup
				message = Label(text='More than 1 light selected', font_size=25, valign = 'middle', size_hint=(1,.3))
				box_1.add_widget(message)
				popup_1 = Popup(title= 'Error 107', content = box_1, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box_1.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_release = popup_1.dismiss))
				popup_1.open()
			else:
				sm.current = 'health'
		except:
			print "Error in health_check_selected"
			
		
''' This screen displays the lights assigned to a room (->View Room)'''			
class RoomView(Screen):
	room_name = StringProperty()
	def __init__(self, **kwargs):
		super(RoomView, self).__init__(**kwargs)
	
	def remove_from_database(self):
		#check lights_down
		global lights_down
		for r in lights_down:
			curs.execute("DELETE FROM Lights WHERE Light_name='" + r + "'")
			conn.commit()
		#rebuild
		self.build()
		
	def checkif_room_selected(self):
		try:
			global btns_down
			if len(btns_down) >= 1:
				pass
			else:
				#popup asking user to select a room to view
				box = BoxLayout(orientation = 'vertical', padding = (8))
				message = Label(text="Please select a room to view", font_size=25, valign = 'middle', size_hint=(1,.3))
				box.add_widget(message)
				popup = Popup(title= 'Error 103: Room not selected', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_press= self.return_to_LV, on_release = popup.dismiss))
				popup.open()
		except:
			print("Error when switching to room view")
			
	def return_to_LV(self, arg1):
		sm.current = 'view_lights'
		
	def clear_room_name(self):
		self.room_name = " "

	"""builds a list of lights assigned to the room"""
	def build(self):
		function_callback = LightsView()
		self.ids.gridlayout2.clear_widgets()
		try:
			if len(btns_down) == 1:
				self.room_name = btns_down[0]
				for row in curs.execute("SELECT Light_name FROM Lights WHERE Room='" + btns_down[0] + "'"):
					btn = ToggleButton(text='%s' % row[0],size = (580, 40),size_hint=(None,None)) #create button
					btn.bind(state=function_callback.lightscallback)
					self.ids.gridlayout2.add_widget(btn) #add to gridlayout 
				self.ids.gridlayout2.bind(minimum_height=self.ids.gridlayout2.setter('height'))
			else:
				print("must select a light")
				
		except:
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
			
class Blank(Screen):
	pass
			
'''login screen will be the first screen to execute, calls function that checks for gui commands'''
class LoginScreen(Screen):
	
	def clear_user(self, u, p):
		print "clearing username and password"
		u.text = "" 
		p.text = ""
	
	def login(self, username, password):
		try:
			user = username
			passw = password
			obj = Methods()
			h = Health()

			curs.execute("SELECT * FROM users WHERE username = '" + username + "' AND password= '" + password + "'")
			if curs.fetchone() is not None:
				print "Successful Login"
				self.parent.current = 'homepage'
				#after login, these methods should execute...
				#event checks workfile every 5 seconds for unprocessed commands 
				event = Clock.schedule_interval(obj.cmdparser, 4.0)
				event()
				#updates lights stored in database with current circadian rhythm values every minute
				light_update_event = Clock.schedule_interval(obj.update_lights, 60.0)
				light_update_event()
				
				get_event = Clock.schedule_interval(h.send_get_cmd, 15.0)
				get_event()
				
				#checks the health status of every light in the database
				
				
			else:
				box = BoxLayout(orientation = 'vertical', padding = (8))
				message = Label(text='Invalid username or password', font_size=25, valign = 'middle', size_hint=(1,.3))
				box.add_widget(message)
				popup = Popup(title= 'Login Error', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
				popup.open()
				
		except:
			print "error in login screen"
			
class HomePage(Screen):
	Timeh = StringProperty()
	Dateh = StringProperty()

        #You're Welcome!
        day_of_week = datetime.today().strftime('%A')
	month = datetime.today().strftime('%B')
	day_of_month = datetime.today().strftime('%d')
	year = datetime.today().strftime('%Y')
	Dateh = day_of_week + ' - ' + month + ' ' + day_of_month + ', ' + year

                        
	def __init__(self, **kwargs):
		super(HomePage, self).__init__(**kwargs)
	
	def verify(self):
		#verify password popup
		box2 = BoxLayout(orientation = 'vertical', padding = (8))
		#message on popup
		message1 = Label(text='Username: ',font_size=25, valign = 'middle', size_hint=(1,.3))
		box2.add_widget(message1)
		self.textuser = TextInput(text='',multiline = False, size_hint=(1,.7), font_size=25)
		box2.add_widget(self.textuser)
		message2 = Label(text='Password: ', font_size=25, valign = 'middle', size_hint=(1,.3))
		box2.add_widget(message2)
		self.textpass = TextInput(text='',multiline = False, size_hint=(1,.7), font_size=25)
		box2.add_widget(self.textpass)
		popup = Popup(title= 'Verify', content = box2, title_size =(30),size_hint=(None, None), size=(500,350),title_align='center', auto_dismiss=False)
		box2.add_widget(Button(text='OK', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_press = self.check_credentials, on_release = popup.dismiss))
		box2.add_widget(Button(text='Cancel', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0}, on_release = popup.dismiss))
		popup.open()
		
		
	def check_credentials(self, arg1):
		username = self.textuser.text
		password = self.textpass.text
		
		curs.execute("SELECT password FROM users WHERE username='" + username + "' and password='" + password + "'")
		s = curs.fetchall()
		
		try:
			if(len(s) == 1):
				print "success"
				sm.current='troubleshoot'
			else:
				box = BoxLayout(orientation = 'vertical', padding = (8))
				message = Label(text='Invalid username or password', font_size=25, valign = 'middle', size_hint=(1,.3))
				box.add_widget(message)
				popup = Popup(title= 'Login Error', content = box, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
				box.add_widget(Button(text='Return', font_size = 20, size_hint=(.5,.3), pos_hint={'center_x': .5, 'center_y': 0},on_release = popup.dismiss))
				popup.open()
		except:
			print "error in check_credentials"
			
	def getInfo(self):
		try:
			self.Timeh = datetime.now().strftime('%H:%M')
			day_of_week = datetime.today().strftime('%A')
			month = datetime.today().strftime('%B')
			day_of_month = datetime.today().strftime('%d')
			year = datetime.today().strftime('%Y')
			image_file = "/home/pi/kivy/screenshot.png"
			subprocess.call(["scrot", image_file])
			self.Dateh = day_of_week + ' - ' + month + ' ' + day_of_month + ', ' + year
			t5 = threading.Timer(10.0, self.getInfo)
			t5.daemon=True
			t5.start()
			
		except:
			print "error in getInfo"
		
		
		
	def shutdown(self):
		#grab IP address of all lights
		data = '00000000'
		for row in curs.execute("SELECT IP_address FROM Lights"):
			(dt, micro) = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f').split('.')
			dt = "%s.%03d" % (dt, int(micro) / 1000)
			cmd = 'S' + ' ' + row[0] + ' ' + 'SUS' + ' ' + data + ' ' + dt
			with open("workfile.txt","a") as document:
					document.write(cmd)
					document.write('\n')
			document.close()
		
		#popup to notify user of shutdown
		box_2 = BoxLayout(orientation = 'vertical', padding = (8))
		#message on popup
		message = Label(text='Goodbye', font_size=25, valign = 'middle', size_hint=(1,.3))
		box_2.add_widget(message)
		popup_2 = Popup(title= 'Shutting down...', content = box_2, title_size =(30),size_hint=(None, None), size=(450,250),title_align='center', auto_dismiss=False)
		popup_2.open()
		
		app = TestApp()
		Clock.schedule_once(app.stop,3)

			
		
	def run_demo(self):
		print "running demo"
		os.system("cat /home/pi/UNT-NASA/RGBdemo.txt > /home/pi/UNT-NASA/workfile.txt")
		pass


class Troubleshoot(Screen):
	pass

############################################ JORGE's GUI Section ##################################################
"""This class has the buttons to 'Add New Device', 'view Ports' """
class Setting(Screen, GridLayout, BoxLayout):
    newDevControl = 1
    portsCount = 0 #Should be Plug-And-Play Value
    
    def __init__(self, **kwargs):
        super(Setting, self).__init__(**kwargs)
    
    """Popup method that displays input field for adding a new device"""    
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

        
    """Method that handles user's input from popup"""
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

    
    """This method gets the port count from the DB and displays it to the user"""    
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
"""This class handles the color wheel popup"""
class ColorSelector(Popup):
        
        """This is the method that gets called when the user presses OK on the color wheel. It stores those values on the DB"""	
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
        
"""This class is To test OLA from any of the lights on the DB. Only one a time can be tested."""
class TestOLA(Screen):

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

        """This method loads the color wheel popup to the screen. It also writes to the workfile"""        
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

#####################################END of JORGE's GUI Section ##################################################


Builder.load_file("gui18.kv")
sm = ScreenManagement()

class TestApp(App):
	title = "Spacecraft Lighting Network System"
	def build(self):
		# return ScreenManagement()

		# Need for TestOla class
		self.color_selector = ColorSelector()

		return sm
		
if __name__ == "__main__":
        #Run voice commands at boot up
        #os.system('python /home/pi/Desktop/UNT-NASA/voiceOLA/voiceOLA.py > /dev/null 2>&1 &')

        # NEEDED For Testing Individual Lights
       # os.system("touch testOLA")

        # Run the GUI
        TestApp().run()

conn.close() #close database connection 
