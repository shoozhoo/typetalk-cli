#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from termcolor import colored, cprint
import argparse
import json
import sys
import codecs
import datetime
import calendar
import time
import re
import os
import math
import getpass

sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

baseUrl = 'https://typetalk.in/api/v1/'
confFile = os.environ['HOME']+'/.ttcrc'

conf = None
enableColor = True

def loadConf():
	if not os.path.exists(confFile):
		return {'accounts':{}}
	f = open(confFile,'r')
	val = json.loads(f.read())
	f.close()
	return val	

def saveConf(accountJson):
	f = open(confFile,'w')
	f.write(json.dumps(accountJson))
	f.close()
	os.chmod(confFile,0600)

def addAccountConf(conf, uniqueId, clientId, clientSecret):
	if uniqueId not in conf['accounts']:
		conf['accounts'][uniqueId] = {}
	conf['accounts'][uniqueId]['clientId'] = clientId
	conf['accounts'][uniqueId]['clientSecret'] = clientSecret
	conf['selected'] = uniqueId
	saveConf(conf)

def switchAccountConf(conf, uniqueId):
	if uniqueId not in conf['accounts']:
		sys.exit(" %s not found. Please add new account." % uniqueId)
	conf['selected'] = uniqueId
	saveConf(conf)

def addNewAccount():
	print "See https://typetalk.in/my/develop/applications"
	clientId = raw_input('Please enter [Client ID]: ')
	clientSecret = getpass.getpass('Please enter [Client Secret]: ')
	try:
		token = getToken(clientId, clientSecret)
	except KeyError:
		sys.exit(" Invalid client credentials!")
	data = ttReq(token, 'GET', 'profile')
	addAccountConf(conf, data['account']['name'], clientId, clientSecret)

def enableDebug():
	import httplib
	import logging
	httplib.HTTPConnection.debuglevel = 2
	logging.basicConfig() 
	logging.getLogger().setLevel(logging.DEBUG)
	requests_log = logging.getLogger("requests.packages.urllib3")
	requests_log.setLevel(logging.DEBUG)
	requests_log.propagate = True

def ttReq(token, method, path, params={}, data=None, headers={}, files=None):
	headers['Authorization']='Bearer '+token
	if method=='POST' and files==None and data!=None:
		headers['Content-type']='application/json'
		data = json.dumps(data)
	res = requests.request(method, baseUrl+path, params=params, data=data, headers=headers, files=files)
	if res.status_code!=200:
		print "# ERR "+path+"  "+str(res.status_code)
		print res.text
	return res.json()

def printStatus(s=None):
	if sys.stdout.isatty():
		if s==None:
			sys.stdout.write("                         \r")
			sys.stdout.flush()
		else:
			sys.stdout.write(s+"\r")
			sys.stdout.flush()

def getToken(clientId=None, clientSecret=None):
	if clientId==None or clientSecret==None:
		clientId = conf['accounts'][conf['selected']]['clientId']
		clientSecret = conf['accounts'][conf['selected']]['clientSecret']
	printStatus("Get access token")
	res = requests.post("https://typetalk.in/oauth2/access_token", {
        'client_id': clientId,
        'client_secret': clientSecret,
        'grant_type': 'client_credentials',
        'scope': 'my,topic.read,topic.post'
        })
	printStatus()
	return res.json()['access_token']



def maxLen(list, func):
	vals = map(lambda d: len(str(func(d))), list)
	return max(vals)

nextColorIndex = 0
def updateNameColorDict(names, dict={}):
	global nextColorIndex
	colors = ['green', 'red', 'yellow', 'blue', 'magenta','cyan']
	for name in names:
		if name not in dict:
			if len(colors) <= nextColorIndex:
				nextColorIndex=0
			dict[name] = colors[nextColorIndex]
			nextColorIndex+=1
	return dict

def fileSize(byte):
	if byte<1000:
		return '%dbytes' % (byte)
	elif byte<1000*1000:
		return '%dKbyte' % (math.ceil(byte/(1000.0*1000.0)))
	else:
		return '%dMbyte' % (math.ceil(byte/(1000.0*1000.0*1000.0)))

def headerColored(s):
	return colored(s,'white','on_grey')

'''
From UTC string to Local time string
'''
def utc2local(utcStr):
	fmt = "%Y-%m-%dT%H:%M:%SZ"
	utcTime = datetime.datetime.strptime(utcStr, fmt)
	localTime = datetime.datetime.fromtimestamp(calendar.timegm(utcTime.timetuple()))
	return "{0:%m/%d %H:%M:%S}".format(localTime)

def createMsgHeaderString(p, topicName, nameColorDict):
	headerFormat = '%s [%s]%s - %s'
	if enableColor:
		headerFormat = headerColored('%s [')+'%s'+headerColored(']')+'%s'+headerColored(' - %s')
	date = utc2local(p['updatedAt'])
	name = '%s(%s)' % (p['account']['fullName'], p['account']['name'])
	if enableColor:
		name = colored(name, nameColorDict[p['account']['name']], 'on_grey')
	star = '' if len(p['likes'])==0 else ' Like*'+str(len(p['likes']))
	if star!='' and enableColor:
		star = colored(star, 'yellow', 'on_grey')
	return headerFormat % (date, name, star, topicName)

def createMsgContentString(msg):
	if enableColor:
		# comment
		msg = re.sub(r'[^\n]```',"\n```", msg)
		msg = re.sub(r'\s?```\s?(.*?)\s*```\s*', lambda m: "\n"+colored(m.group(1), 'grey','on_white')+"\n", msg, flags=re.MULTILINE|re.DOTALL)
		# mention
		msg = re.sub(r'(@[A-Za-z0-9]+)', lambda m: colored(m.group(1), 'white','on_blue'), msg, flags=re.MULTILINE|re.DOTALL)
	return msg

def createAttachmentString(att):
	attchFormat = '# File: %s (%s)\n  %s'
	fileInfo = att['attachment']
	attLine = attchFormat % (fileInfo['fileName'], fileSize(fileInfo['fileSize']), att['webUrl'])
	if enableColor:
		attLine = colored(attLine,'yellow',attrs=['underline'])
	return attLine

def attachFile(token, topicId, fname):
	# {"fileKey":"2f166f90b301c2fbd70e9c75eeb057559154fdd6","fileName":"200911_25_63_c0108763_1354839.jpg","fileSize":71949}
	printStatus("File upload "+os.path.basename(fname))
	files = {'file': open(fname, 'rb')}
	r = ttReq(token, 'POST', 'topics/'+topicId+'/attachments', files=files)
	printStatus()
	return r

'''
Show topic list
'''
def cmdList(args):
	data = ttReq(getToken(), 'GET', 'topics')
	topics = data['topics']
	if args.favoriteOnly==True:
		topics = filter(lambda t: t['favorite'], topics)
	if args.unreadOnly==True:
		topics = filter(lambda t: t['unread']['count']>0, topics)
	
	topics = sorted(topics, key=lambda t: t['topic']['lastPostedAt'], reverse=False)

	countSize = maxLen(topics, lambda t: t['unread']['count'])
	idSize = maxLen(topics, lambda t: t['topic']['id'])
	outFormat = '%'+str(countSize)+'d [%'+str(idSize)+'d] %s'
	for t in topics:
		line = outFormat % (t['unread']['count'], t['topic']['id'], t['topic']['name'])
		if t['unread']['count'] > 0 and enableColor:
			line = colored(line,'white','on_green')
		print line


'''
Show topic messages
'''
def cmdTopic(args):
	nameColorDict={}
	param_count = args.count
	param_from = None
	param_direction = 'backword'
	token = getToken()
	while True:
		data = ttReq(token, 'GET', 'topics/' + args.TOPIC_ID, params={'count':param_count, 'from':param_from, 'direction':param_direction})
		posts = data['posts']
		if len(posts)==0:
			time.sleep(3)
			continue

		nameColorDict = updateNameColorDict(reversed(map(lambda p: p['account']['name'], posts)), nameColorDict)

		nameSize = maxLen(posts, lambda p: p['account']['name'])

		for p in posts:
			print '\n'+createMsgHeaderString(p, data['topic']['name'], nameColorDict)
			print createMsgContentString(p['message'])

			# attachments
			for att in p['attachments']:
				print createAttachmentString(att)
		if args.bookmark:
			ttReq(token,'PUT', 'bookmarks', params={'topicId':args.TOPIC_ID, 'postId':posts[len(posts)-1]['id']})
		if not args.follow:
			break
		time.sleep(3)
		param_count = 5
		param_direction = 'forward'
		param_from =  posts[len(posts)-1]['id']
'''
Post message
'''
def cmdPost(args):
	msg = args.MESSAGE
	if msg==None:
		if sys.stdout.isatty():
			print "[Please input message and Ctrl-D]:"
		msg = sys.stdin.read()
	data = {'message':msg}
	token = getToken()
	if args.talk!=None:
		for i, t in enumerate(args.talk):
			data['talkIds['+str(i)+']']=t
	if args.file!=None:
		for i, f in enumerate(args.file):
			data['fileKeys['+str(i)+']'] = attachFile(token, args.TOPIC_ID, f)['fileKey']

	ttReq(token, 'POST', 'topics/'+args.TOPIC_ID, data=data)
	print "OK"

def cmdAccount(args):
	if args.add:
		# add new account
		addNewAccount()
	elif args.UNIQUE_ID==None:
		# show accunts and selected
		print " Current account: %s" % (conf['selected'])
		print " Stored accounts:"
		for uniqueId in conf['accounts']:
			print "                  %s" % uniqueId
	else:
		# switch selected account
		switchAccountConf(conf, args.UNIQUE_ID)
		print " swtch account to [%s]" % (args.UNIQUE_ID)

def main():
	parser = argparse.ArgumentParser(description='TypeTalk cli')
	parser.add_argument('-nc', action='store_true', default=False, help='no color')
	parser.add_argument('--debug', action='store_true', default=False, help='enable http debug')
	subparsers = parser.add_subparsers(help='sub command help')

	parser_list = subparsers.add_parser('list', help='show topic list')
	parser_list.add_argument('-f', action='store_true', dest='favoriteOnly', default=False, help='show favorite only')
	parser_list.add_argument('-u', action='store_true', dest='unreadOnly', default=False, help='show unread only')
	parser_list.set_defaults(func=cmdList)

	parser_topic = subparsers.add_parser('topic', help='show topic messages')
	parser_topic.add_argument("-n", type=int, dest="count", default=20, help='message counts')
	parser_topic.add_argument("-f", action='store_true', dest="follow", default=False, help='follow like "tail -f"')
	parser_topic.add_argument("-b", action='store_true', dest="bookmark", default=False, help='set read flag')
	parser_topic.add_argument("TOPIC_ID", help='your topic_id')
	parser_topic.set_defaults(func=cmdTopic)

	parser_post = subparsers.add_parser('post', help='post message')
	parser_post.add_argument('-t', dest='talk', action='append', help='talk_ids')
	parser_post.add_argument('-a', dest='file', action='append', help='attachment files')
	parser_post.add_argument("TOPIC_ID", help='your topic_id')
	parser_post.add_argument("MESSAGE", nargs='?', help='if you do not specify, use stdin')
	parser_post.set_defaults(func=cmdPost)

	parser_account = subparsers.add_parser('account', help='manage account')
	parser_account.add_argument('-a', dest='add', action='store_true', default=False, help='add new account')
	parser_account.add_argument("UNIQUE_ID", nargs='?', help='switch account')
	parser_account.set_defaults(func=cmdAccount)

	args =  parser.parse_args()
	if sys.stdout.isatty()==False or args.nc==True:
		global enableColor
		enableColor = False
	if args.debug:
		enableDebug()

	global conf
	conf = loadConf()
	if 'selected' not in conf:
		addNewAccount()
		return

	args.func(args)

if __name__ == "__main__":
	main()



