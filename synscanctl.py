import re
from  synscanserial import SynScanAZ
import tkinter as tk
from PIL import Image, ImageTk
from copy import deepcopy
from time import sleep
import threading

		
class StatusWindow( object ):
	"""Class for handling the graphical status and control window for SynscanAZ mount."""

	def __init__ ( self, root ):
		
		self.mount = SynScanAZ()	

		# Init GUI
		self.root = root
		self.root.title("SynScanAZ Control Window")

		# labelList will contain handles to GUI labels
		self.widget_list = []

		# Graphics
		self.art_path = "./art/151x151/"
		self.art = [

						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_left.png").convert("RGBA")),
						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_up.png").convert("RGBA")),
						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_down.png").convert("RGBA")),
						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_right.png").convert("RGBA")),
						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_left_on_click.png").convert("RGBA")),
						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_up_on_click.png").convert("RGBA")),
						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_down_on_click.png").convert("RGBA")),
						ImageTk.PhotoImage(Image.open(self.art_path + "arrow_right_on_click.png").convert("RGBA"))

					]

		# Arrow left, #0
		widget_list_item = tk.Button(self.root, image = self.art[0], command = self.button_click_left )
		widget_list_item.grid(row = 1, column = 0, columnspan = 2)
		self.widget_list.append( widget_list_item )
		
		
		# Arrow up, #1
		widget_list_item = tk.Button( self.root, image = self.art[1], command = self.button_click_up )
		widget_list_item.grid(row = 0, column = 2, columnspan = 2)
		self.widget_list.append( widget_list_item )

		
		# Arrow down, #2
		widget_list_item = tk.Button( self.root, image = self.art[2], command = self.button_click_down )
		widget_list_item.grid(row = 1, column = 2, columnspan = 2)
		self.widget_list.append( widget_list_item )

		
		# Arrow right, #3
		widget_list_item = tk.Button(self.root, image = self.art[3], command = self.button_click_right )
		widget_list_item.grid(row = 1, column = 4, columnspan = 2)
		self.widget_list.append( widget_list_item )

	
		# Add text labels and append handles to the items needing updates to the widget_list
		tk.Label(self.root, text = "Coordinates", height = 2).grid(row = 3, column = 0, columnspan = 6)


		# Azimuth and altitude info
		azm_alt = self.mount.getAzmAltPrecise()

		tk.Label( self.root, text = "Azm.", height = 2, width = 10).grid(row = 4, column = 0 )
		
		widget_list_item = tk.Label( self.root, text = "%.4f"%azm_alt[0], relief = tk.RIDGE, bg = 'white', height = 2, width = 15 )
		widget_list_item.grid( row = 4, column = 1, columnspan = 2 )
		# #4
		self.widget_list.append( widget_list_item )

		tk.Label( self.root, text = "Alt.", height = 2, width = 10).grid(row = 4, column = 3 )
		
		widget_list_item = tk.Label( self.root, text = "%.4f"%azm_alt[1], relief = tk.RIDGE, bg = 'white', height = 2, width = 15 )
		widget_list_item.grid( row = 4, column = 4, columnspan = 2 )
		#5
		self.widget_list.append( widget_list_item )

	
		# Right ascension and declination info
		ra_dec = decimalCoordToPretty( self.mount.getRaDecPrecise() )

		tk.Label( self.root, text = "RA", height = 2, width = 10).grid(row = 6, column = 0 )
		
		widget_list_item = tk.Label(self.root, text = ra_dec[0], relief = tk.RIDGE, bg = 'white', height = 2, width = 15 )
		widget_list_item.grid( row = 6, column = 1, columnspan = 2 )
		# #6
		self.widget_list.append( widget_list_item )

		tk.Label( self.root, text = "DEC", height = 2, width = 10).grid(row = 6, column = 3 )
		
		widget_list_item = tk.Label( self.root, text = ra_dec[1], relief = tk.RIDGE, bg = 'white', height = 2, width = 15 )
		widget_list_item.grid( row = 6, column = 4, columnspan = 2 )
		# #7	
		self.widget_list.append( widget_list_item )


		# Stop button and tracking status, #8
		widget_list_item = tk.Button(self.root, relief = tk.RAISED, bg = 'red1', text = "STARTING...\n[stopped]", height = 4, width = 10, command = self.buttonStop )
		widget_list_item.grid( row = 0, column = 4, columnspan = 2 )
		self.widget_list.append( widget_list_item )


		# Goto precision toggle, #9
		widget_list_item = tk.Button(self.root, relief = tk.RAISED, bg = "lightgrey", text = "PRECISE\nGOTO", height = 4, width = 10, command = self.button_toggle_precision )
		widget_list_item.grid( row = 0, column = 0, columnspan = 2 )
		self.widget_list.append( widget_list_item )

		# Vertical space
		tk.Label(self.root, height = 1).grid(row = 7, column = 0, columnspan = 6)
		
		# GOTO Button right ascension + declination
		widget_list_item = tk.Button( self.root, text = "GOTO RA/DEC", height = 2, width = 10, relief = tk.RAISED, command = self.buttonGotoRadec)
		widget_list_item.grid( row = 9, column = 0 )
		# #10
		self.widget_list.append( widget_list_item )

		# GOTO coordinates for right ascension, declination
		widget_list_item = tk.Entry( self.root, bg = "white", width = 30, relief = tk.RIDGE)		
		widget_list_item.grid( row = 9, column = 1, columnspan = 4 )
		# #11	
		self.widget_list.append( widget_list_item )
		tk.Label(self.root, height = 2, text="hh:mm:ss.s\n+/-dd:mm:ss.s").grid(row = 9, column = 5)

		# GOTO Button azimuth + altitude
		widget_list_item = tk.Button( self.root, text = "GOTO Azm/Alt", height = 2, width = 10, relief = tk.RAISED, command = self.buttonGotoAzmAlt)
		widget_list_item.grid( row = 10, column = 0 )
		# #12
		self.widget_list.append( widget_list_item )

		# GOTO coordinates for azimuth and altitude
		widget_list_item = tk.Entry( self.root, bg = "white", width = 30, relief = tk.RIDGE)		
		widget_list_item.grid( row = 10, column = 1, columnspan = 4 )
		# #13	
		self.widget_list.append( widget_list_item )
		tk.Label(self.root, height = 2, text="deg,deg").grid(row = 10, column = 5)

		# Synchronize button
		widget_list_item = tk.Button( self.root, text = "SYNC", height = 2, width = 10, relief = tk.RAISED, command = self.buttonSync)
		widget_list_item.grid( row = 11, column = 0 )
		# #14
		self.widget_list.append( widget_list_item )

		# Synchronize coordinate values
		widget_list_item = tk.Entry( self.root, bg = "white", width = 30, relief = tk.RIDGE)		
		widget_list_item.grid( row = 11, column = 1, columnspan = 4 )
		# #15	
		self.widget_list.append( widget_list_item )
		tk.Label(self.root, height = 2, text="hh:mm:ss.s\n+/-dd:mm:ss.s").grid(row = 11, column = 5)

		# Set tracking mode
		tk.Label( self.root, height = 2, text = "Pointing Mode").grid( row = 12, column = 0)
		widget_list_item = tk.Button( self.root, bg = "magenta1", text = "Telescope", width = 10, relief = tk.RAISED, command = self.buttonTelescope )		
		widget_list_item.grid( row = 12, column = 1, columnspan = 2 )
		# #16	
		self.widget_list.append( widget_list_item )

		widget_list_item = tk.Button( self.root, bg = "magenta1", text = "Mirror", width = 10, relief = tk.RAISED, command = self.buttonMirror )		
		widget_list_item.grid( row = 12, column = 2, columnspan = 4 )
		# #17	
		self.widget_list.append( widget_list_item )


	#def __del__ ( self ):
	#	# Destructor, TODO better implementation with ctrl-C and 
	#	self.root.destroy()



	def refresh ( self ):
		# Update the GUI

		if self.mount.stepIsPrecise:
			self.widget_list[9].configure(bg = "seagreen1")
		else:
			self.widget_list[9].configure(bg = "lightgrey")

		if self.mount.isSlewing():
			self.widget_list[8].configure(bg = "yellow", text = "READY\n[slewing]")
		elif self.mount.trackingMode == 0:
			self.widget_list[8].configure(bg = "red1", text = "READY\n[stopped]")
		elif self.mount.trackingMode != 0:
			self.widget_list[8].configure(bg = "seagreen1", text = "READY\n[tracking]")



		azm_alt = self.mount.getAzmAltPrecise()
		self.widget_list[4].configure(text = "%.4f"%azm_alt[0])
		self.widget_list[5].configure(text = "%.4f"%azm_alt[1])

		ra_dec = decimalCoordToPretty( self.mount.getRaDecPrecise() )
		self.widget_list[6].configure(text = ra_dec[0])
		self.widget_list[7].configure(text = ra_dec[1])



	def button_click_left ( self ):
		# Define button click
		a = 1


	def button_click_up ( self ):
		# Define button click
		a = 1

	
	def button_click_down ( self ):
		# Define button click
		a = 1


	def button_click_right ( self ):
		# Define button click
		a = 1



	def button_toggle_precision ( self ):
		# Toggle between coarse and fine precision positioning
		self.mount.togglePrecision()
		if self.mount.stepIsPrecise == True:
			self.widget_list[9].configure(bg = "seagreen1")
		else:
			self.widget_list[9].configure(bg = "lightgrey")


	def buttonStop ( self ):
		# Stop the mount
		if self.mount.isSlewing():
			self.mount.cancelGoto()

		self.mount.setTrackingMode(0) # Sets mount to idle

		if self.mount.isStopped():
			self.widget_list[8].configure(bg = "red1", text = "READY\n[stopped]")


	def buttonGotoRadec ( self ):
		coordString = self.widget_list[11].get()	
		self.mount.gotoRaDec( prettyCoordToDeg( coordString ) )
		self.widget_list[11].delete(0,tk.END)


	def buttonGotoAzmAlt ( self ):
		coords = self.widget_list[13].get()
		self.mount.gotoAzmAlt( re.split("[,]", coords) )
		self.widget_list[13].delete(0,tk.END)


	def buttonSync ( self ):
		coords = self.widget_list[15].get()
		self.mount.syncRaDec( prettyCoordToDec( coords ) )
		self.widget_list[15].delete(0,tk.END)


	def buttonTelescope ( self ):
		self.mount.isTelescope = True
		self.widget_list[16].configure(bg = "magenta1")
		self.widget_list[17].configure(bg = "lightgrey")


	def buttonMirror ( self ):
		self.mount.isTelescope = False
		self.widget_list[16].configure(bg = "lightgrey")
		self.widget_list[17].configure(bg = "magenta1")



	def updater ( self ):
		if self.mount.isConnected:
			self.refresh()
			self.root.after( 500, self.updater )
		else:
			self.mount.reconnect()
			print("Trying to reconnect in 10s")
			self.root.after( 10000, self.updater )



# Some convenience funtions below this line

def prettyCoordToDec( coordString ):
	# Input format hh mm ss.s +/- hh mm ss.s. Returns the given coordinate in decimal hours as tuple.
	celSphereSouth = False

	if '-' in coordString:
		celSphereSouth = True

	coords = re.split( "[+-]", coordString )
	ra = re.split( "[ ]", coords[0] )
	dec = re.split( "[ ]", coords[1] )

	# Convert to hours
	ra_hh = float( ra[0] ) 
	ra_mm = float( ra[1] ) / 60.
	ra_ss = float( ra[2] ) / 3600.

	dec_hh = float( dec[0] ) 
	dec_mm = float( dec[1] ) / 60.
	dec_ss = float( dec[2] ) / 3600

	if celSphereSouth == True:
		dec_hh * -1 

	ra = ra_hh + ra_mm + ra_ss 
	dec = dec_hh + dec_mm + dec_ss 	

	return [ ra, dec ]




def prettyCoordToDeg( coordString ):
	# Input format hh mm ss.s +/- hh mm ss.s. Returns the given coordinate in decimal fraction of a full rotation as tuple.
	celSphereSouth = False

	if '-' in coordString:
		celSphereSouth = True

	coords = re.split( "[+-]", coordString )
	ra = re.split( "[ ]", coords[0] )
	dec = re.split( "[ ]", coords[1] )

	# Convert to hours
	ra_hh = float( ra[0] ) 
	ra_mm = float( ra[1] ) / 60.
	ra_ss = float( ra[2] ) / 3600.

	dec_hh = float( dec[0] ) 
	dec_mm = float( dec[1] ) / 60.
	dec_ss = float( dec[2] ) / 3600

	if celSphereSouth == True:
		dec_hh * -1 

	ra = ( ra_hh + ra_mm + ra_ss ) / 24. * 360
	dec = ( dec_hh + dec_mm + dec_ss )

	return [ ra, dec ]




def decimalCoordToPretty( coords ):
	# Input as a tuple containing decimal values for right ascension and declinatin. Output as tuple of right ascension and declination in format hh mm ss.s [+/-]dd mm ss.s
	ra = coords[0]
	dec = coords[1]

	# The mount handles right ascension as a fraction of full rotation. Change units hours.
	ra = ra / 360 * 24.

	ra_hh = int(ra)							# Extract hours		
	ra_mm = ( ra - int(ra) ) * 60			# Minutes including seconds
	ra_ss = ( ra_mm - int(ra_mm) ) * 60 	# Seconds

	ra_string = str(ra_hh).zfill(2) + " : " + str(int(ra_mm)).zfill(2) + " : " + "%.2f"%ra_ss

	dec_dd = int(dec)
	dec_mm = ( dec - int(dec) ) * 60
	dec_ss = ( dec_mm - int(dec_mm) ) * 60

	dec_string = str(dec_dd).zfill(2) + " : " + str(int(dec_mm)).zfill(2) + " : " + "%.2f"%dec_ss

	return [ra_string, dec_string]





if __name__ == "__main__":
	import serial
	import synscanctl as az
	import tkinter as tk
	from time import sleep
	from sys import argv

	root_window = tk.Tk()
	root_window.resizable(width=False, height=False)
	#root_window.bind('<Control-c>', quit)
	win = az.StatusWindow(root_window)
	
	# while True:
	# 	try:
	# 		sleep(1)
	# 		win.refresh
	# 		print("About time to do something")
	# 	except KeyboardInterrupt:
	# 		break
	win.updater()
	root_window.mainloop()
