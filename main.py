'''
pip install gspread
pip install gspread-dataframe
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

def def_value(): 
    return -1

State_dict = defaultdict(def_value)

Patient_Id = -1

SPO2 = PR = BP = ANTIBIOTIC = STOOL = FEVER = FEED = I_O = RTA_DRAIN = Hemogram = Coagulogram = SE = RFT = ABG_VBG = RBS = Special_Ix = APACHE_IV = HAS_BLED = MDRD_GFR = SOFA_score = Other_Scores = INSTRUCTIONS = ''

editable_columns_list = ['SPO2', 'PR', 'BP', 'ANTIBIOTIC(S)', 'STOOL', 'FEVER', 'FEED', 'I/O', 'RTA/DRAIN', 'Hemogram', 'Coagulogram', 'SE', 'RFT', 'ABG/VBG', 'RBS', 'Special Ix', 'APACHE IV', 'HAS BLED', 'MDRD GFR', 'SOFA score','Other Scores', 'INSTRUCTIONS']

df_data_patient_id = pd.DataFrame()

df_data_last_row = pd.DataFrame()

Conversation_type = ''


#Function to start the bot,initiated on /start command
def start(bot,update):
    chat_id_str = str(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text='Hi, Enter the Patient_Id ')
    State_dict[chat_id_str] = 0

def getrow(bot, update):

    global Patient_Id
    global df_data_patient_id
    global df_data_last_row

    chat_id_str = str(update.message.chat_id)
    if  State_dict[chat_id_str] == 0:

        Patient_Id = update.message.text
        df_data_patient_id = df_data[df_data['id'] == int(Patient_Id)]
        df_data_last_row = df_data_patient_id.iloc[[-1]]

        get_update(bot, update)
        State_dict[chat_id_str] = 1


def get_updatechoice(bot,update):

    global Conversation_type

    reply_markup = telegram.ReplyKeyboardRemove()
    chat_id_str = str(update.message.chat_id)

    if update.message.text == 'Get' and State_dict[chat_id_str] == 1:
        Get(bot,update)
        Conversation_type = 'Get'
        bot.send_message(chat_id=update.message.chat_id, text='\nThanks')
    elif update.message.text == 'Update' and State_dict[chat_id_str] == 1:
        Conversation_type = 'Update'
        State_dict[chat_id_str] = 2


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
    global df_data_last_row

    chat_id_str = str(update.message.chat_id)

    if 2<=State_dict[chat_id_str]<=23 and Conversation_type == 'Update' :
        
        if State_dict[chat_id_str]>2:
            globals()[editable_columns_list[State_dict[chat_id_str]-3].replace('/','_').replace(' ','_').replace('(S)','')] = update.message.text

        column_str = editable_columns_list[State_dict[chat_id_str]-2]
        cell = sheet.find(column_str)
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'{column_str}: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text=f'Enter the new {column_str} ')
        State_dict[chat_id_str] += 1

    elif State_dict[chat_id_str] == 24 and Conversation_type == 'Update':
        INSTRUCTIONS = update.message.text
        State_dict[chat_id_str] = 25

    elif State_dict[chat_id_str] == 25 and Conversation_type == 'Update':
        for column in editable_columns_list:
            df_data_last_row[column] = globals()[column.replace('/','_').replace(' ','_').replace('(S)','')]
        
        Get(bot,update)
        confirm(bot, update)
        State_dict[chat_id_str] = 26


def confirm(bot, update):
    button_labels = [['YES'], ['NO']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Confirm please', reply_markup=reply_keyboard)

def confirmchoice(bot,update):
    reply_markup = telegram.ReplyKeyboardRemove()
    chat_id_str = str(update.message.chat_id)
    
    if update.message.text == 'YES' and State_dict[chat_id_str] == 25:
        df_data = df_data.append(df_data_last_row)
        last_row_list = df_data_last_row.values[0].tolist()
        sheet.insert_row(last_row_list, len(df_data))
        bot.send_message(chat_id=update.message.chat_id, text='\nGood')
        State_dict[chat_id_str] = -1
    
    elif update.message.text == 'NO' and State_dict[chat_id_str] == 25:
        State_dict[chat_id_str] = 26
        edit(bot, update)

def edit(bot, update):
    button_labels = [['SPO2'], ['PR'], ['BP'], ['ANTIBIOTIC(S)'], ['STOOL'], ['FEVER'], ['FEED'], ['I/O'], ['RTA/DRAIN'], ['Hemogram'], ['Coagulogram'], ['SE'], ['RFT'], ['ABG/VBG'], ['RBS'], ['Special Ix'], ['APACHE IV'], ['HAS BLED'], ['MDRD GFR'], ['SOFA score'],['Other Scores'], ['INSTRUCTIONS']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Which field you need to edit ?', reply_markup=reply_keyboard)

def editchoice(bot, update):

    reply_markup = telegram.ReplyKeyboardRemove()
    global Conversation_type
    global SPO2, PR, BP, ANTIBIOTIC, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS
    global df_data_last_row
    
    chat_id_str = str(update.message.chat_id)
    print("message sent by user", update.message.text)

    if (update.message.text in editable_columns_list) and 26<=State_dict[chat_id_str]<=46 and Conversation_type == 'Update':

        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        column_index = editable_columns_list.index(update.message.text)
        State_dict[chat_id_str] = column_index+27

    if 27<=State_dict[chat_id_str]<=47 and Conversation_type == 'Update':
        globals()[editable_columns_list[State_dict[chat_id_str]-27].replace('/','_').replace(' ','_').replace('(S)','')] = update.message.text
        Get(bot,update)
        confirm(bot, update)
        State_dict[chat_id_str] = 25



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


if __name__ == "__main__":
    main()