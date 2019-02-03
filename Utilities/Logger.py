# A module that logs information about a program run to a text file or standard output.
# This module provides classes that represent logging objects (class Logger), or objects
# that have the same interface (class NullLogger) but don't really log anything. There
# is also a function that examines command-line arguments and returns one or the other of
# these objects according to whether there's a file name (log to that file) or "-" (log
# to standard output). These features let programmers write programs that can log their
# actions by just calling the makeLogger function and then acting as if the result logs
# whatever they tell it to, without worrying about parsing command line arguments
# themselves, remembering whether they are or aren't logging a particular run, etc. See
# the July 16, 2018 notes for my crystals project for more discussion of this module.
#
# Usage of the logging feature for any program that uses this module is
#     program_name [-l [logname]]
#     program_name [--log [logname]]
# If there is no -l or --log option, the program runs without logging. If either option is
# present but there's no log file name, the log goes to standard output. Otherwise the
# log goes to the file, erasing any previous contents.

# Copyright (C) 2018 by Doug Baldwin (baldwin@geneseo.edu).
# This work is licensed under a Creative Commons Attribution 4.0 International License
# (http://creativecommons.org/licenses/by/4.0/).

# History:
#
#   July 2018 -- Created by Doug Baldwin.


from argparse import ArgumentParser
from timeit import default_timer
import sys




# The function that creates a logger based on command-line arguments.

def makeLogger() :
	
	
	# Make a parser with which to process the command line.
	
	parser = ArgumentParser()
	parser.add_argument( "-l", "--log", nargs = "?", const = Logger.STDOUT,
						help = "Record activity in log file or to stdout if no file name given" )
	
	arguments = parser.parse_args()
	
	
	# Create either a real or dummy logger, as requested on the command line.
	
	if arguments.log :
		return Logger( arguments.log )
	else :
		return NullLogger()






# The class that represents loggers.

class Logger :
	
	
	# A "file name" loggers recognize as meaning standard output.
	
	STDOUT = "-"
	
	
	
	
	# Loggers need to remember the name of the file they log to, and to maintain a list of
	# data they will eventually write to that file. They do this with the following
	# member variables:
	#   o logName - The name of the log file.
	#   o data - A list of strings, each of which represents a data record this logger is
	#       remembering. Loggers identify records within this list by their indices.
	
	
	
	
	# Initialize a logger with the name of the file it will log to.
	
	def __init__( self, logName ) :
		
		
		# Copy the client-requested log file name to the corresponding member variable,
		# and empty the list of log records.
		
		self.logName = logName
		self.data = []
	
	
	
	
	# Start a timer, i.e., a virtual stopwatch that will measure the time from the call
	# to this method until a call to "stopTimer" on the same timer. I identify timers via
	# an ID; this method creates a new timer and returns its ID. Note that timers measure
	# wall clock time in seconds.
	
	def startTimer( self ) :
		
		
		# Temporarily store the starting time in this log's data list. Allocate a new
		# space for the time now, before actually noting the time, to avoid including
		# any time associated with the allocation itself.
		
		id = len( self.data )
		self.data.append( 0 )
		
		
		# Now note the time.
		
		self.data[id] = default_timer()
		
		return id
	
	
	
	
	# Stop a timer, i.e., note the time since someone started this timer in its log
	# record. In addition to the ID of the timer to stop, callers provide a string that
	# serves as a label for the time in the log and when eventually printed.
	
	def stopTimer( self, id, label ) :
		
		
		# Immediately note the time, to avoid timing anything more than necessary.
		
		endTime = default_timer()
		
		
		# Now make a nicely formatted log entry.
		
		elapsedTime = endTime - self.data[id]
		
		self.data[id] = label + ": " + str( elapsedTime )
	
	
	
	
	# Add a record, i.e., an arbitrary string meaningful to the caller, to this log.
	# Return a value by which the caller can later identify this specific record if they
	# need to.
	
	def addRecord( self, data ) :
		
		
		# Note the initial length of the data list, since that will be the new record's
		# index, then add the new record at the end.
		
		index = len( self.data )
		self.data.append( data )
		
		return index
	
	
	
	
	# Write all the data in this log to its file.
	
	def writeAll( self ) :
		
		
		# A function that does the actual work of dumping the log, once someone has
		# figured out what file object to dump it to.
		
		def dumpLog( destination ) :
			for rec in self.data :
				destination.write( rec + "\n" )
		
		
		# Write the log to either standard output or an open but erased disk file,
		# according to whether or not the log name is the logger code for standard output.
		
		if self.logName == Logger.STDOUT :
			dumpLog( sys.stdout )
		else :
			with open( self.logName, "w" ) as logFile :
				dumpLog( logFile )






# The class that represents dummy loggers, i.e., objects that provide a logger's interface
# but ignore all calls to it as quickly as possible.

class NullLogger :
	
	
	# (Don't) start a timer in this log. Return None as the ID for the non-timer.
	
	def startTimer( self ) :
		return None
	
	
	# (Don't) stop a specified timer in this log, with a specified label.
	
	def stopTimer( self, id, label ) :
		pass
	
	
	# (Don't) add a new record to this log. Use None as the ID for the non-record.
	
	def addRecord( self, data ) :
		return None
	
	
	# (Don't) write a label or other text to this log's file.
	
	def writeText( self, message ) :
		pass
	
	
	# (Don't) dump the contents of this log to its file.
	
	def writeAll( self ) :
		pass
