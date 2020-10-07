'''
pip install gspread
pip install telegram
pip install --upgrade google-api-python-client oauth2client
pip install python-telegram-bot
pip install tabulate
'''


import telegram
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,CallbackQueryHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup
import logging
from tabulate import tabulate
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('testsheet.json', scope)

# authorize the clientsheet
client = gspread.authorize(creds)

# get the instance sheet of the Spreadsheet
sheet = client.open("Bot Spreadsheet").sheet1

# get all the records of the data
data = sheet.get_all_records()

# convert the json to dataframe
df_data = pd.DataFrame.from_dict(data)

bot=telegram.Bot(token='1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E')
updater = Updater(token='1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

#State_dict = {}
from collections import defaultdict

State_dict = defaultdict(int)

Patient_Id = -1

SPO2 = PR = BP = ANTIBIOTIC = STOOL = FEVER = FEED = I_O = RTA_DRAIN = Hemogram = Coagulogram = SE = RFT = ABG_VBG = RBS = Special_Ix = APACHE_IV = HAS_BLED = MDRD_GFR = SOFA_score = Other_Scores = INSTRUCTIONS = ''


df_data_patient_id = pd.DataFrame()

df_data_last_row = pd.DataFrame()

Conversation_type = ''


#Function to start the bot,initiated on /start command
def start(bot,update):
    chat_id_str = str(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text='Hi, Enter the Patient_Id ')
    State_dict[chat_id_str] = 1

def getrow(bot, update):

    global Patient_Id
    global df_data_patient_id
    global df_data_last_row

    chat_id_str = str(update.message.chat_id)
    if  State_dict[chat_id_str] == 1:

        Patient_Id = update.message.text
        df_data_patient_id = df_data[df_data['id'] == int(Patient_Id)]
        df_data_last_row = df_data_patient_id.iloc[[-1]]

        get_update(bot, update)
        State_dict[chat_id_str] = 2


def get_updatechoice(bot,update):

    global Conversation_type

    reply_markup = telegram.ReplyKeyboardRemove()

    print("message sent by user",update.message.text)
    if update.message.text == 'Get':
        Get(bot,update)
        Conversation_type = 'Get'
        bot.send_message(chat_id=update.message.chat_id, text='\nThanks')
    elif update.message.text == 'Update':
        Conversation_type = 'Update'






def get_update(bot,update):
    button_labels = [['Get'], ['Update']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id,text='Get or Update ?',reply_markup=reply_keyboard)

def button(bot,update):
    query=update.callback_query
    bot.send_chat_action(chat_id=update.effective_user.id,action=telegram.ChatAction.TYPING)
    bot.edit_message_text(text="Your choice is received",chat_id=query.message.chat_id,message_id=query.message.message_id)

def Get(bot,update):

    global Patient_Id
    global df_data_last_row

    text = ''
    for column in df_data_last_row.columns.values:
        text = text + '\n' + column + ': ' + str(df_data_last_row[column].values[0])

    bot.send_message(chat_id=update.message.chat_id, text=text)


def update(bot, update):
    reply_markup = telegram.ReplyKeyboardRemove()
    global SPO2, PR, BP, ANTIBIOTIC, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS
    global Patient_Id
    global df_data_last_row
    chat_id_str = str(update.message.chat_id)

    if State_dict[chat_id_str] == 2 and Conversation_type == 'Update' :
        cell = sheet.find("SPO2")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'SPO2: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new SPO2 ')
        State_dict[chat_id_str] = 3
    elif State_dict[chat_id_str] == 3 and Conversation_type == 'Update':
        SPO2 = update.message.text

        cell = sheet.find("PR")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'PR: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new PR ')
        State_dict[chat_id_str] = 4
    elif State_dict[chat_id_str] == 4 and Conversation_type == 'Update':
        PR = update.message.text

        cell = sheet.find("BP")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'BP: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new BP ')
        State_dict[chat_id_str] = 5
    elif State_dict[chat_id_str] == 5 and Conversation_type == 'Update':
        BP = update.message.text

        cell = sheet.find("ANTIBIOTIC(S)")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'ANTIBIOTIC(S): {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new ANTIBIOTIC(S) ')
        State_dict[chat_id_str] = 6
    elif State_dict[chat_id_str] == 6 and Conversation_type == 'Update':
        ANTIBIOTIC = update.message.text

        cell = sheet.find("STOOL")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'STOOL: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new STOOL ')
        State_dict[chat_id_str] = 7
    elif State_dict[chat_id_str] == 7 and Conversation_type == 'Update':
        STOOL = update.message.text

        cell = sheet.find("FEVER")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'FEVER: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new FEVER ')
        State_dict[chat_id_str] = 8
    elif State_dict[chat_id_str] == 8 and Conversation_type == 'Update':
        FEVER = update.message.text

        cell = sheet.find("FEED")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'FEED: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new FEED ')
        State_dict[chat_id_str] = 9
    elif State_dict[chat_id_str] == 9 and Conversation_type == 'Update':
        FEED = update.message.text

        cell = sheet.find("I/O")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'I/O: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new I/O ')
        State_dict[chat_id_str] = 10
    elif State_dict[chat_id_str] == 10 and Conversation_type == 'Update':
        I_O = update.message.text

        cell = sheet.find("RTA/DRAIN")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'RTA/DRAIN: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new RTA/DRAIN ')
        State_dict[chat_id_str] = 11
    elif State_dict[chat_id_str] == 10 and Conversation_type == 'Update':
        RTA_DRAIN= update.message.text

        cell = sheet.find("Hemogram")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'Hemogram: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Hemogram ')
        State_dict[chat_id_str] = 11
    elif State_dict[chat_id_str] == 11 and Conversation_type == 'Update':
        Hemogram = update.message.text
        cell = sheet.find("Coagulogram")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'Coagulogram: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Coagulogram ')
        State_dict[chat_id_str] = 12
    elif State_dict[chat_id_str] == 12 and Conversation_type == 'Update':
        Coagulogram = update.message.text
        cell = sheet.find("SE")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'SE: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new SE ')
        State_dict[chat_id_str] = 13
    elif State_dict[chat_id_str] == 13 and Conversation_type == 'Update':
        SE = update.message.text
        cell = sheet.find("RFT")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'RFT: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new RFT ')
        State_dict[chat_id_str] = 14
    elif State_dict[chat_id_str] == 14 and Conversation_type == 'Update':
        RFT = update.message.text
        cell = sheet.find("ABG/VBG")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'ABG/VBG: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new ABG/VBG ')
        State_dict[chat_id_str] = 15
    elif State_dict[chat_id_str] == 15 and Conversation_type == 'Update':
        ABG_VBG = update.message.text
        cell = sheet.find("RBS")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'RBS: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new RBS ')
        State_dict[chat_id_str] = 16
    elif State_dict[chat_id_str] == 16 and Conversation_type == 'Update':
        RBS = update.message.text
        cell = sheet.find("Special Ix")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'Special Ix: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Special Ix')
        State_dict[chat_id_str] = 17
    elif State_dict[chat_id_str] == 17 and Conversation_type == 'Update':
        Special_Ix = update.message.text
        cell = sheet.find("APACHE IV")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'APACHE IV: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new APACHE IV ')
        State_dict[chat_id_str] = 18
    elif State_dict[chat_id_str] == 18 and Conversation_type == 'Update':
        APACHE_IV = update.message.text
        cell = sheet.find("HAS BLED")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'HAS BLED: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new HAS BLED ')
        State_dict[chat_id_str] = 19
    elif State_dict[chat_id_str] == 19 and Conversation_type == 'Update':
        HAS_BLED = update.message.text
        cell = sheet.find("MDRD GFR")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'MDRD GFR: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new MDRD GFR ')
        State_dict[chat_id_str] = 20
    elif State_dict[chat_id_str] == 20 and Conversation_type == 'Update':
        MDRD_GFR = update.message.text
        cell = sheet.find("SOFA score")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'SOFA score: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new SOFA score ')
        State_dict[chat_id_str] = 21
    elif State_dict[chat_id_str] == 21 and Conversation_type == 'Update':
        SOFA_score = update.message.text
        cell = sheet.find("Other Scores")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'Other Scores: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Other Scores ')
        State_dict[chat_id_str] = 22
    elif State_dict[chat_id_str] == 22 and Conversation_type == 'Update':
        Other_Scores = update.message.text
        cell = sheet.find("INSTRUCTIONS")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'INSTRUCTIONS: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new INSTRUCTIONS ')
        State_dict[chat_id_str] = 23
    elif State_dict[chat_id_str] == 23 and Conversation_type == 'Update':
        INSTRUCTIONS = update.message.text
        '''
        row =[Patient_Id, SPO2, PR, BP, ANTIBIOTIC, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS]
        cell1 = sheet.find(str(Patient_Id))
        sheet.insert_row(row,cell1.row )
        row1 = sheet.row_values(cell1.row)
        '''
        for i in df_data_last_row.columns.values:
            if i == 'SPO2' :
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = SPO2
            elif i == 'PR':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = PR
            elif i == 'BP':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = BP
            elif i == 'ANTIBIOTIC(S)':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = ANTIBIOTIC
            elif i == 'STOOL':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = STOOL
            elif i == 'FEVER':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = FEVER
            elif i == 'FEED':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = FEED
            elif i == 'I/O':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = I_O
            elif i == 'RTA/DRAIN':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = RTA_DRAIN
            elif i == 'Hemogram':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = Hemogram
            elif i == 'Coagulogram':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = Coagulogram
            elif i == 'SE':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = SE
            elif i == 'RFT':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = RFT
            elif i == 'ABG/VBG':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = ABG_VBG
            elif i == 'RBS':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = RBS
            elif i == 'Special Ix':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = Special_Ix
            elif i == 'APACHE IV':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = APACHE_IV
            elif i == 'HAS BLED':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = HAS_BLED
            elif i == 'MDRD GFR':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = MDRD_GFR
            elif i == 'SOFA score':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = SOFA_score
            elif i == 'Other Scores':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = Other_Scores
            elif i == 'INSTRUCTIONS':
                df_data_last_row.iloc[0, df_data_last_row.columns.get_loc(i)] = INSTRUCTIONS

        cell1 = sheet.find(str(Patient_Id))
        sheet.insert_row(df_data_last_row, cell1.row)
        Get(bot,update)
        confirm(bot, update)
        State_dict[chat_id_str] = 24




def confirm(bot, update):
    button_labels = [['YES'], ['NO']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Confirm please', reply_markup=reply_keyboard)

def confirmchoice(bot,update):
    reply_markup = telegram.ReplyKeyboardRemove()

    print("message sent by user",update.message.text)
    if update.message.text == 'YES':
        bot.send_message(chat_id=update.message.chat_id, text='\nGood')
    elif update.message.text == 'NO':
         edit(bot, update)

def edit(bot, update):
    button_labels = [['SPO2'], ['PR'], ['BP'], ['ANTIBIOTIC(S)'], ['STOOL'], ['FEVER'], ['FEED'], ['I/O'], ['RTA/DRAIN'], ['Hemogram'], ['Coagulogram'], ['SE'], ['RFT'], ['ABG/VBG'], ['RBS'], ['Special Ix'], ['APACHE IV'], ['HAS BLED'], ['MDRD GFR'], ['SOFA score'],['Other Scores'], ['INSTRUCTIONS']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Which field you need to edit ?', reply_markup=reply_keyboard)

def editchoice(bot, update):
    reply_markup = telegram.ReplyKeyboardRemove()
    global Conversation_type
    chat_id_str = str(update.message.chat_id)
    print("message sent by user", update.message.text)
    if update.message.text == 'SPO2':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 26
    elif update.message.text == 'PR' and Conversation_type == 'Update':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 27
    elif update.message.text == 'BP':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 28
    elif update.message.text == 'ANTIBIOTIC(S)':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 29
    elif update.message.text == 'STOOL':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 30
    elif update.message.text == 'FEVER':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 31
    elif update.message.text == 'FEED':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 32
    elif update.message.text == 'I/O':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 33
    elif update.message.text == 'RTA/DRAIN':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 34
    elif update.message.text == 'Hemogram':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 35
    elif update.message.text == 'Coagulogram':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 36
    elif update.message.text == 'SE':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 37
    elif update.message.text == 'RFT':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 38
    elif update.message.text == 'ABG/VBG':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 39
    elif update.message.text == 'RBS':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 40
    elif update.message.text == 'Special Ix':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 41
    elif update.message.text == 'APACHE IV':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 42
    elif update.message.text == 'HAS BLED':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 41
    elif update.message.text == 'MDRD GFR':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 42
    elif update.message.text == 'SOFA score':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 43
    elif update.message.text == 'Other Scores':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 44
    elif update.message.text == 'INSTRUCTIONS':
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        State_dict[chat_id_str] = 45





def main():



    updater.dispatcher.add_handler(CommandHandler('start',start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, getrow), group=0)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, get_updatechoice), group=1)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, update), group=2)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, confirmchoice), group=3)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, editchoice), group=4)

    updater.start_polling()

    # Stop the bot if Ctrl + C was pressed
    updater.idle()


main()