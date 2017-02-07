#!/usr/bin/python3.5

from __future__ import print_function
import httplib2
import os
import datetime
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import telepot
import sys, time
import logging
import json

logging.basicConfig(filename='logs', level=logging.INFO)

fd = open("config", "r")
conf = fd.read()
chat_ids = json.loads(conf)
fd.close()

bot = telepot.Bot("353764032:AAElxkfWK0Rx1tnzgpHUxLmRkHGlSr4ycVs")

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Breakfast'

sheet = None
date = None

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
    return credentials


def getSheet():
    global sheet, date
    today = datetime.datetime.now()+datetime.timedelta(days=1)
    date = today.strftime("%d.%m.%Y")
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    spreadsheetId = '1IA2D5x7xUqo7ee0GFfbfJ_W9b49jJZdeEZ5EP1sEzfE'
    rangeName = 'Sheet1!A3:Z25'
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    sheet = result.get('values', [])

def writeToCell(cell, data):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    spreadsheetId = '1IA2D5x7xUqo7ee0GFfbfJ_W9b49jJZdeEZ5EP1sEzfE'
    rangeName = "Sheet1!"+cell+":"+cell
    values = {'values': [[data,],]}
    service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=rangeName, valueInputOption='RAW', body=values).execute()

def getMenu(date):
    idx = sheet[0].index(date)
    return [item[idx] for item in sheet[1:4]]

def getCellName(date, name):
    columnStart = 'B'
    idx = sheet[0].index(date)
    columnIndex = chr(ord(columnStart)+idx-1)
    rowIndex = 8
    for item in sheet[5:]:
        if item[0] == name:
            break
        rowIndex = rowIndex + 1
    if rowIndex == 26:
        raise Exception
    return str(columnIndex)+str(rowIndex)

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    text = msg['text']
    logging.info(msg)
    try:
        username = chat_ids[str(chat_id)]
    except:
        bot.sendMessage(chat_id, "You are not a registered user!")
        bot.sendMessage(222739419, "Some unregistered user tried to send a message "+str(chat_id)+","+msg['from']['first_name'])
        return

    try:
        getSheet()
    except:
        bot.sendMessage(chat_id, "There was some problem in processing your request!")
        bot.sendMessage(222739419, "getSheet() error "+str(chat_id)+","+text)
        return

    try:
        menu = getMenu(date)
    except:
        bot.sendMessage(chat_id, "There is no menu available for "+date+"!")
        bot.sendMessage(222739419, "getMenu() error "+date+","+str(chat_id))
        return

    try:
        index = int(text)
        if index > 3:
            raise Exception
    except:
        bot.sendMessage(chat_id, "This bot only accepts integer messages! That too constraint in range 1 to 3! Availabe menu options for " +date+": \n1: "+menu[0]+"\n2: "+menu[1]+"\n3: "+menu[2]+"\nPlease reply with option number.")
        return
    selection = menu[index - 1]

    try:
        cell = getCellName(date, username)
    except:
        bot.sendMessage(chat_id, "There was some problem in updating your selection!")
        bot.sendMessage(222739419, "getCellName() error "+date+","+username)
        return

    try:
        writeToCell(cell, selection)
    except:
        bot.sendMessage(chat_id, "There was some problem in updating your selection!")
        bot.sendMessage(222739419, "writeToCell() error "+cell+","+selection+","+str(chat_id)+","+date)
        return
    bot.sendMessage(chat_id, "Selection updated for date "+date+"!")

def main():
    #getSheet()
    #for item in sheet:
    #    print(item)
    #print(getMenu(date))
    #print(getCellName(date, "ARWINDER SINGH"))
    #writeToCell("H16", "Hello world")
    bot.message_loop(handle)

if __name__ == '__main__':
    main()
    while(1):
        time.sleep(10)
