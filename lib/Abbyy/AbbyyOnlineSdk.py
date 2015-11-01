#!/usr/bin/python

# Usage: recognize.py <input file> <output file> [-language <Language>] [-pdf|-txt|-rtf|-docx|-xml]

import argparse
import base64
import getopt
import MultipartPostHandler
import os
import re
import sys
import time
import urllib2
import urllib
import xml.dom.minidom
from lxml import etree,objectify
from celery.contrib import rdb

class ProcessingSettings:
	Language = "English"
	OutputFormat = "xml"
	ImageSource = "auto"
	CorrectOrientation = "true"
	CorrectSkew = "true"
	ExtendedCharacters = "true"
	FieldComponents = "true"

class RunOCR:


	def RunProc( self,filePath,  language, outputFormat ):
		print "Uploading.."
		processor = AbbyyOnlineSdk()
		settings = ProcessingSettings()

		#task = processor.ProcessImage( filePath, settings )
		task = processor.ProcessBusinessCard( filePath, settings )
		if task == None:
			print "Error"
			return ("Error", None)
		print "Id = %s" % task.Id
		print "Status = %s" % task.Status

		# Wait for the task to be completed
		sys.stdout.write( "Waiting.." )
		# Note: it's recommended that your application waits at least 2 seconds
		# before making the first getTaskStatus request and also between such requests
		# for the same task. Making requests more often will not improve your
		# application performance.
		# Note: if your application queues several files and waits for them
		# it's recommended that you use listFinishedTasks instead (which is described
		# at http://ocrsdk.com/documentation/apireference/listFinishedTasks/).
	        count = 0
		#while task.IsActive == True :
		#while task.Status == "Queued" or task.Status == "InProgress":
                while task.IsActive():
	                count = count + 1
			time.sleep( 2 )
			sys.stdout.write( "." )
			task = processor.GetTaskStatus( task )

		print "Task Status = %s" % task.Status
		"""print "isActive = %s" % task.IsActive"""

		if task.Status == "Completed":
			if task.DownloadUrl != None:
				cardOutput = processor.DownloadResultString( task)
				cardFields = processor.ExtractFields(cardOutput)
				print cardFields.items()
                                return (task.Status, cardFields)

	#			print "Result was written to %s" % cardOutput
		else:
                    print "Error processing task %s" % task.Status
                    return (task.Status, None)





class Task:
	Status = "Unknown"
	Id = None
	DownloadUrl = None
	def IsActive( self ):
		if self.Status == "InProgress" or self.Status == "Queued":
			return True
		else:
			return False

class AbbyyOnlineSdk:
	ServerUrl = "http://cloud.ocrsdk.com/"
	# To create an application and obtain a password,
	# register at http://cloud.ocrsdk.com/Account/Register
	# More info on getting your application id and password at
	# http://ocrsdk.com/documentation/faq/#faq3
	ApplicationId = "wizcard_ocr1"
	Password = "ufQ1u0ko5OIKZ+sWKc0Z8Wpv"
	Proxy = None
	enableDebugging = 0

	def ProcessImage( self, filePath, settings ):
		urlParams = urllib.urlencode({
			"language" : settings.Language,
			"exportFormat" : settings.OutputFormat

			})
		requestUrl = self.ServerUrl + "processImage?" + urlParams

		bodyParams = { "file" : open( filePath, "rb" )  }
		request = urllib2.Request( requestUrl, None, self.buildAuthInfo() )
		response = self.getOpener().open(request, bodyParams).read()
		if response.find( '<Error>' ) != -1 :
			return None
		# Any response other than HTTP 200 means error - in this case exception will be thrown

		# parse response xml and extract task ID
		task = self.DecodeResponse( response )
		return task
	def ProcessBusinessCard( self, filePath, settings ):
		urlParams = urllib.urlencode({
			"language" : settings.Language,
			"imageSource" : settings.ImageSource,
			"exportFormat" : settings.OutputFormat,
			"xml:writeFieldComponents": settings.FieldComponents,
			"xml:writeExtendedCharacterInfo": settings.ExtendedCharacters,
			"correctSkew" : settings.CorrectSkew,
			"correctOrientation" : settings.CorrectOrientation
			})
		requestUrl = self.ServerUrl + "processBusinessCard?" + urlParams

		bodyParams = { "file" : open( filePath, "rb" )  }
		request = urllib2.Request( requestUrl, None, self.buildAuthInfo() )
		response = self.getOpener().open(request, bodyParams).read()
		if response.find( '<Error>' ) != -1 :
			return None
		# Any response other than HTTP 200 means error - in this case exception will be thrown

		# parse response xml and extract task ID
		task = self.DecodeResponse( response )
		return task

	def GetTaskStatus( self, task ):
		urlParams = urllib.urlencode( { "taskId" : task.Id } )
		statusUrl = self.ServerUrl + "getTaskStatus?" + urlParams
		request = urllib2.Request( statusUrl, None, self.buildAuthInfo() )
		response = self.getOpener().open( request ).read()
		task = self.DecodeResponse( response )
		return task

	def DownloadResult( self, task, outputPath ):
		getResultParams = urllib.urlencode( { "taskId" : task.Id } )
		getResultUrl = self.ServerUrl + "getResult?" + getResultParams
		request = urllib2.Request( getResultUrl, None, self.buildAuthInfo() )
		fileResponse = self.getOpener().open( request ).read()
		resultFile = open( outputPath, "wb" )
		resultFile.write( fileResponse )

	def DownloadResultString( self, task):
		getResultParams = urllib.urlencode( { "taskId" : task.Id } )
		getResultUrl = self.ServerUrl + "getResult?" + getResultParams
		request = urllib2.Request( getResultUrl, None, self.buildAuthInfo() )
		fileResponse = self.getOpener().open( request ).read()
		return fileResponse

	def ExtractFields(self, fileResponse):
		fileResponse = re.sub(r'<document(.*?)>',r'<document>',fileResponse)

		root = etree.fromstring(fileResponse)
		cardField = dict()

		for elem in root.iter("field"):
			for value in elem[0].iter("value"):
				cardField[elem.get('type').lower()] = value.text

		return cardField


	def DecodeResponse( self, xmlResponse ):
		""" Decode xml response of the server. Return Task object """
		dom = xml.dom.minidom.parseString( xmlResponse )
		taskNode = dom.getElementsByTagName( "task" )[0]
		task = Task()
		task.Id = taskNode.getAttribute( "id" )
		task.Status = taskNode.getAttribute( "status" )
		if task.Status == "Completed":
			task.DownloadUrl = taskNode.getAttribute( "resultUrl" )
		return task


	def buildAuthInfo( self ):
		return { "Authorization" : "Basic %s" % base64.encodestring( "%s:%s" % (self.ApplicationId, self.Password) ) }

	def getOpener( self ):
		if self.Proxy == None:
			self.opener = urllib2.build_opener( MultipartPostHandler.MultipartPostHandler,
			urllib2.HTTPHandler(debuglevel=self.enableDebugging))
		else:
			self.opener = urllib2.build_opener(
				self.Proxy,
				MultipartPostHandler.MultipartPostHandler,
				urllib2.HTTPHandler(debuglevel=self.enableDebugging))
		return self.opener
