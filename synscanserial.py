import serial
import inspect
from time import sleep


class SynScanAZ ( object ):
	"""Class to control Synscan AZ Goto mount over serial port."""
	
	def __init__ ( self ):
		# Open serial port according to the mount specs
		try:
			self.ser = serial.Serial(	
									port 		= '/dev/ttyUSB0',
									baudrate 	= 9600			,
									parity		= 'N'			,
									stopbits	= 1				,
									timeout		= 5				,
								)
			self.isConnected = True
		except:
			self.ser = 0
			self.isConnected = False

		self.stepIsPrecise = False
		self.trackingMode = None
		self.isTelescope = True
		#self.alignmentCompleted = False



	def __del__ ( self ):
		# Destructor closes serial port
		if self.isConnected:
			self.ser.close()



	def reconnect( self ):
		# Try to connect if not connected at init
		try:
			self.ser = serial.Serial(	
									port 		= '/dev/ttyUSB0',
									baudrate 	= 9600			,
									parity		= 'N'			,
									stopbits	= 1				,
									timeout		= 5				,
								)
			self.isConnected = True
		except:
			self.isConnected = False



	def togglePrecision ( self ):
		# Sets the step size to precise
		if self.isConnected:
			self.stepIsPrecise = ( not self.stepIsPrecise )




	def getRaDec ( self ):
		# Get current pointing in 16bit, J2000. Returns [ra, dec]
		ra = 0
		dec = 0

		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('E'))

			if success:
				response = self.ser.read(10)[:-1]
			else:
				print("Communication failure in:", inspect.stack()[0][3])

			coord = response.split(str.encode(','))
			ra  = int( coord[0], 16 ) / 65536. * 360
			dec = int( coord[1], 16 ) / 65536. * 360

		return [ra, dec]



	def getRaDecPrecise ( self ):
		# Get current pointing in 24bit, J2000. Returns [ra, dec]
		ra = 0
		dec = 0

		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('e'))

			if success:
				response = self.ser.read(18)[:-1]
			else:
				print("Communication failure in:", inspect.stack()[0][3])

			coord = response.split(str.encode(','))
			ra  = int( coord[0][:-2], 16 ) / 16777216. * 360 # Last two digits discarded
			dec = int( coord[1][:-2], 16 ) / 16777216. * 360 # Last two digits discarded

		return [ra, dec]



	def getAzmAltCoarse ( self ):
		# Get current pointing in azimuth and altitude, 16bit. Returns [azm, alt]
		azm = 0
		alt = 0

		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('Z'))

			if success:
				response = self.ser.read(10)[:-1]
			else:
				print("Communication failure in:", inspect.stack()[0][3])

			coord = response.split(str.encode(','))
			azm = int( coord[0], 16 ) / 65536. * 360
			alt = int( coord[1], 16 ) / 65536. * 360

		return [azm, alt]



	def getAzmAltPrecise ( self ):
		# Get current pointing in azimuth and altitude, 24bit. Returns [azm, alt]
		azm = 0
		alt = 0

		if self.isConnected:
			response = 0
			success = self.ser.write( str.encode('z'))

			if success:
				response = self.ser.read(18)[:-1]
			else:
				print("Communication failure in ", inspect.stack()[0][3])

			coord = response.split(str.encode(','))
			azm = int( coord[0][:-2], 16 ) / 16777216. * 360 # Last two digits discarded
			alt = int( coord[1][:-2], 16 ) / 16777216. * 360 # Last two digits discarded

		return [azm, alt]



	def gotoRaDec ( self, coords ):
		# Slew to the given coordinates
		if self.stepIsPrecise:
			self.gotoRaDecPrecise( coords )
		else:
			self.gotoRaDecCoarse( coords )
		
		#If pointing with mirror, calculate new altitude based on half of zenith angle
		if not self.isTelescope:
			azmAlt = self.getAzmAltPrecise()
			azm = azmAlt[0]
			alt = azmAlt[1]

			newAlt = 90 - (90-alt)/2.
			self.gotoAzmAlt( [azm,newAlt] ) 




	def gotoRaDecCoarse ( self, coords ):
		# Goto given coordinate, input values will be converted to 16bit hex. Units, degrees.

		if self.isConnected:
			ra = coords[0]
			dec = coords[1]

			hexRa = hex( int( round( float( ra )) / 360. * 65536 ))
			hexDec = hex( int( round( float( dec )) / 360. * 65536 ))

			response = 0
			cmd = 'R' + (str(hexRa)[2:].zfill(4)+ ',' + str(hexDec)[2:].zfill(4)).upper()

			success = self.ser.write( str.encode( cmd ))

			if success:
				self.ser.read(1)
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1

		print("No device connected")
		return 1



	def gotoRaDecPrecise ( self, coords ):
		# Goto given coordinate, input values will be converted to 24bit hex. Units, degrees.

		if self.isConnected:
			ra = coords[0]
			dec = coords[1]

			hexRa  = hex( int( round( float( ra ))  / 360. * 16777216 ) )
			hexDec = hex( int( round( float( dec )) / 360. * 16777216 ) )

			cmd = 'r' + ((str(hexRa)[2:]+'00').zfill(8) + ',' + (str(hexDec)[2:]+'00').zfill(8)).upper() 

			success = self.ser.write( str.encode( cmd ))

			if success:
				self.ser.read(1)
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1

		print("No device connected")
		return 1



	def gotoAzmAlt ( self, coords ):
		if self.stepIsPrecise:
			self.gotoAzmAltPrecise( coords )
		else:
			self.gotoAzmAltCoarse( coords )



	def gotoAzmAltCoarse ( self, coords ):
		# Goto given coordinate, input values will be converted to 16bit hex. Units, degrees.

		if self.isConnected:
			azm = coords[0]
			alt = coords[1]

			hexAzm = hex( int( round( float( azm )) / 360. * 65536 ))
			hexAlt = hex( int( round( float( alt )) / 360. * 65536 ))

			response = 0
			cmd = 'B' + (str(hexAzm)[2:].zfill(4)+ ',' + str(hexAlt)[2:].zfill(4)).upper()

			success = self.ser.write( str.encode( cmd ))

			if success:
				self.ser.read(1)
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1

		print("No device connected")
		return 1


	def gotoAzmAltPrecise ( self, coords ):
		# Goto given coordinate, input values will be converted to 24bit hex. Units, degrees.

		if self.isConnected:
			azm = coords[0]
			alt = coords[1]

			hexAzm = hex( int( round( float( azm )) / 360. * 16777216. ) )
			hexAlt = hex( int( round( float( alt )) / 360. * 16777216. ))

			response = 0
			cmd = 'b' + ((str(hexAzm)[2:]+'00').zfill(8) + ',' + (str(hexAlt)[2:]+'00').zfill(8)).upper()

			success = self.ser.write( str.encode( cmd ))

			if success:
				self.ser.read(1)
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1

		print("No device connected")
		return 1



	def syncRaDec ( self, coords ):
		if self.stepIsPrecise:
			self.syncRaDecPrecise( coords )
		else:
			self.syncRaDecCoarse( coords )




	def syncRaDecCoarse ( self, coords ):
		# Sync current pointing to the given coordinates, 16bit. Units, degrees.

		if self.isConnected:
			ra = coords[0]
			dec = coords[1]

			hexRa = hex( int( round( float( ra )) / 360. * 65536 ))
			hexDec = hex( int( round( float( dec )) / 360. * 65536 ))

			response = 0
			cmd = 'S' + (str(hexRa)[2:].zfill(4)+ ',' + str(hexDec)[2:].zfill(4)).upper()

			success = self.ser.write( str.encode ( cmd ))
			self.ser.read(1)

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1

		print("No device connected")
		return 1



	def syncRaDecPrecise ( self, coords ):
		# Sync current pointing to the given coordinates, 24bit. Units, degrees.

		if self.isConnected:
			ra = coords[0]
			dec = coords[1]

			hexRa  = hex( int( round( float( ra ))  / 360. * 16777216 ) )
			hexDec = hex( int( round( float( dec )) / 360. * 16777216 ) )

			cmd = 's' + ((str(hexRa)[2:]+'00').zfill(8) + ',' + (str(hexDec)[2:]+'00').zfill(8)).upper()

			success = self.ser.write( str.encode( cmd ))

			if success:
				self.ser.read(1)
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])

		print("No device connected")
		return 1


 
	# def getTrackingMode ( self ): # BUG Doesn't work, mount does not reply according to the specs
	# 	# Get current tracking mode
	# 	# 0 = tracking off
	# 	# 1 = Alt/Az tracking
	# 	# 2 = Equatorial tracking
	# 	# 3 = PEC mode ( sidereal + PEC )
	# 	response = 0
	# 	success = self.ser.write( str.encode ('t'))

	# 	if success:
	# 		response = self.ser.read(2)[:-1]
	# 		print(response)
	# 		return int(response)
	# 	else:
	# 		print("Communication failure in: ", inspect.stack()[0][3])
	# 		return 1



	# Quick and dirty solution to the problem above, handled within class.
	def getTrackingMode ( self ):
		# Set tracking mode to specific
		return self.trackingMode




	def setTrackingMode ( self, mode ):
		# Get current tracking mode
		# 0 = tracking off
		# 1 = Alt/Az tracking
		# 2 = Equatorial tracking
		# 3 = PEC mode ( sidereal + PEC )

		if self.ser.isOpen():
			if int(mode) > 3:
				print("Argument error, possible values are\n0 = tracking off\n1 = Alt/Az tracking\n2 = Equatorial tracking\n3 = PEC mode ( sidereal + PEC )")

			self.trackingMode = int( mode )
			
			response = 0
			cmd = 'T'+str( chr(mode))
			success = self.ser.write( str.encode( cmd ))

			if success:
				response = self.ser.read(1)
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1

		print("No device connected")



	def isStopped ( self ):
		# Check if the mount is stopped
		return self.trackingMode == 0



	def isTracking ( self ):
		# Check if the mount is currently tracking
		return self.trackingMode != 0



	def isSlewing ( self ):
		# Checks if the mount is still slewing to target

		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('L'))

			if success:
				response = self.ser.read(2)[:-1]
				slews = int( response )
				return bool(slews)
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1

		print("No device connected")
		return 1



	def cancelGoto ( self ):
		# Cancel on-going GOTO action and set mount to idle

		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('M'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])

		print("No device connected")
		return 1




	def setVariableAzmRatePos ( self, rate ):
		# Set variable azimuthal rate to positive direction, units arcsec/sec 
		# Disable tracking first
		return 0

	def setVariableAzmRateNeg ( self, rate ):
		# Set variable azimuthal rate to negative direction, units arcsec/sec
		# Disable tracking first
		return 0

	def setVariableAltRatePos ( self, rate ):
		# Set variable altitudinal rate to positive direction, units arcsec/sec
		# Disable tracking first
		return 0

	def setVariableAltRateNeg ( self, rate ):
		# Set variable altitudinal tracking rate to negative direction, units arcsec/sec
		# Disable tracking first
		return 0

	def setFixedAzmRatePos ( self, rate ):
		# Set variable azimuthal rate to positive direction, units arcsec/sec
		# Disable tracking first
		return 0

	def setFixedAzmRateNeg ( self, rate ):
		# Set variable azimuthal rate to negative direction, units arcsec/sec
		# Disable tracking first
		return 0

	def setFixedAltRatePos ( self, rate ):
		# Set variable altitudinal rate to positive direction, units arcsec/sec
		# Disable tracking first
		return 0

	def setFixedAltRateNeg ( self, rate ):
		# Set variable altitudinal tracking rate to negative direction, units arcsec/sec
		# Disable tracking first
		return 0

	def getGeoLocation ( self ):
		# Get geographical location stored on the mount
		if self.isConnected:
			response = 0
			success = ser.write(str.encode('w'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
				return 1
		return 1


	def setGeoLocation ( self, geoCoords):
		# Set geographical location on the mount, units degrees
		if self.isConnected:
			self.longitude = geoCoords[0]
			self.latitude = geoCoords[1]

			response = 0
			success = self.ser.write(str.encode('W'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		print("No device connected")
		return 1



	def getTime ( self ):
		# Get current time stored on the mount
		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('h'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		return 1


	def setTime ( self):
		# Set the mount time, units...
		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('H'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		return 1


	def getVersion ( self ):
		# Get hand controller firmware version
		if self.isConnected:
			response = 0 
			success = self.ser.write(str.encode('V'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		return 1


	def getDeviceVersion ( self ):
		# Get motor controller firmware version
		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('P'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		return 1


	def getModel ( self ):
		# Get mount model
		if self.isConnected:
			response = 0 
			success = self.ser.write(str.encode('m'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		return 1


	def echo ( self, echo ):
		# Mount replies what you shout
		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('K'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		return 1


	def isAlignmentComplete ( self ):
		# Check is the alignment value has been set to completed (if somebedy answered "Yes" on the remote >:))
		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('J'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])

			isComplete = self.ser.read(1)

			self.alignmentCompleted = isComplete
			return 0
		return 1




	def getMountPointingState ( self ):
		# Returns either E(ast) or W(est)
		if self.isConnected:
			response = 0
			success = self.ser.write(str.encode('p'))

			if success:
				return 0
			else:
				print("Communication failure in ", inspect.stack()[0][3])
		return

