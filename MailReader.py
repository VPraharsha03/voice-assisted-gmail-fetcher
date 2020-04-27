#Credits: Vivek Praharsha
#Ported from Python2
#Enable Less secure app access in gmail security settings & IMAP to allow access to mails

#Standard library modules
import sys
import imaplib
import getpass
import email
import datetime
import os

from tkinter import *
import tkinter.messagebox

import subprocess

from bs4 import BeautifulSoup
import html5lib
import traceback

#offline TTS module
import pyttsx3

#speech recognition module
import speech_recognition as sr

#fuzzy matching module
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

engine = pyttsx3.init('sapi5') 
voices = engine.getProperty('voices') 
engine.setProperty('voice', voices[0].id) 

def speak(audio): 
		engine.say(audio) 
		engine.runAndWait()

def get_body(m):
    if m.is_multipart():
        return get_body(m.get_payload(0))
    else:
        return m.get_payload(None,True)

def process_mailbox(M):
	#Search Command tags: [https://tools.ietf.org/html/rfc3501.html#section-6.4.4]
	rv, data = M.search(None, "ALL")
	if rv != 'OK':
			print("No messages found!")
			return

	for num in data[0].split():
			rv, data = M.fetch(num, '(RFC822)')
			if rv != 'OK':
					print("ERROR getting message", num)
					return

			msg = email.message_from_bytes(data[0][1])
			print('Message %s: %s' % (num.decode(), msg['Subject']))
			print('Raw Date:', msg['Date'])
			#str_body_obj = str(msg.get_payload(0))
			str_body_obj = get_body(msg)
			soup = BeautifulSoup(str_body_obj,'html5lib').text
			print(soup)
			date_tuple = email.utils.parsedate_tz(msg['Date'])
			if date_tuple:
					local_date = datetime.datetime.fromtimestamp(
							email.utils.mktime_tz(date_tuple))
					print("Local Date:", local_date.strftime("%a, %d %b %Y %H:%M:%S"))
					print("\n")
																					
# Create IMAP4 instance of SSL security variant
# connects to Gmail server @ imap.gmail.com
M = imaplib.IMAP4_SSL('imap.gmail.com')


#WARNING! Echo free input is unavailable for getpass() on IDLE, use an actual terminal
#read more: https://docs.python.org/2/library/getpass.html

subprocess.call('', shell=True) #workaround for a bug in Python3.7 to print colored text to console
width = os.get_terminal_size().columns
print(r"   _____         .__.__    __________                   .___            ".center(width))
print(r"  /     \ _____  |__|  |   \______   \ ____ _____     __| _/___________ ".center(width))
print(r" /  \ /  \\__  \ |  |  |    |       _// __ \\__  \   / __ |/ __ \_  __\\".center(width))
print(r"/    Y    \/ __ \|  |  |__  |    |   \  ___/ / __ \_/ /_/ \  ___/|  | \/".center(width))
print(r"\____|__  (____  /__|____/  |____|_  /\___  >____  /\____ |\___  >__|   ".center(width))
print(r"        \/     \/                  \/     \/     \/      \/    \/       ".center(width))
print("Credits: Vivek Praharsha".rjust(width))
print('\033[1;32m'+"Note: Use an actual terminal to avoid password echoing!"+'\033[0;0m')
speak("Use an actual terminal to avoid password echoing!")
#Login attempt
username = input("Enter Username: ")
try:
		M.login(username, getpass.getpass())
#Throw an exception of type 'imaplib.IMAP4.error' on fail    
except imaplib.IMAP4.error:
		print('\033[1;31m'+"Login attempt failed!"+'\033[0;0m')
		print("Reasons: ")
		print("-Enable IMAP and Allow Less Secure App Access on your Gmail Account [https://www.google.com/settings/security/lesssecureapps]")
		print("-You entered wrong credentials")
		window = Tk()
		window.withdraw()
		tkinter.messagebox.showerror("Login attempt failed!", 
															 "Reasons: \n"
															 "- Enable IMAP and Allow Less Secure App Access on your Gmail Account\n"
															 "- You entered wrong credentials\n"
																 "\n"
																 "Re-run the application \n")
		sys.exit()


#'IMAP4' method returns tuples
#Get list of mailboxes/labels on the server
speak("Listing your mailboxes...")
rv, mailboxes = M.list()
if rv == 'OK':
		print("Mailboxes:")
		
		#cleaning-up data
		
		#list comprehension to apply decode() to each byte string in the 'mailboxes' list
		in_str = [bs.decode() for bs in mailboxes]
		#slice-up un-necessary data
		for x in range(len(in_str)):
			in_str[x] = in_str[x][in_str[x][:in_str[x].rindex('"')].rindex('"'):]
		#join the list 'in_str' on '\n' and print
		print('\n'.join(in_str))


#return list of labels
#select() method to open one of mailboxes/labels
speak("Select a label or mailbox to read messages from")

while True:
	with sr.Microphone() as source:
		print("Listening...")
		sr.Recognizer().pause_threshold = 1
		audio = sr.Recognizer().listen(source)

	try:
		print("Recognizing...")
		query = sr.Recognizer().recognize_google(audio, language ='en-in')
		print(f"User said: {query}\n")
		bestMatch = process.extractOne(query, in_str, score_cutoff=90)
		
		try:			
			k = bestMatch[0]
			print(k+"is selected")
			if k in in_str:
				rv, data = M.select(k)
				if rv == 'OK':
					print("Processing mailbox...\n")
					process_mailbox(M)
					M.close()
					break
		except TypeError as e:
			print(e)
			traceback.print_exc()
			print("In-correct mailbox, try again!")
			speak("In-correct mailbox, try again!")
			continue
				
	except Exception as e:
		print(e)
		print("Unable to Recognize your voice. Try Again...")
		continue
	break

sm, dat = M.logout()
if sm == 'BYE':
	log_out_status = [bs.decode("utf-8") for bs in dat]
	print(log_out_status)
	print("Successfully logged out.")
