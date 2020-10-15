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
from collections import defaultdict

def def_value(): 
    return -1



def get_update(bot,update):
    button_labels = [['Get'], ['Update']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id,text='Get or Update ?',reply_markup=reply_keyboard)

def button(bot,update):
    query=update.callback_query
    bot.send_chat_action(chat_id=update.effective_user.id,action=telegram.ChatAction.TYPING)
    bot.edit_message_text(text="Your choice is received",chat_id=query.message.chat_id,message_id=query.message.message_id)

def confirm(bot, update):
    button_labels = [['YES'], ['NO']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Confirm please', reply_markup=reply_keyboard)


def edit(bot, update):
    button_labels = [['SPO2'], ['PR'], ['BP'], ['ANTIBIOTIC(S)'], ['STOOL'], ['FEVER'], ['FEED'], ['I/O'], ['RTA/DRAIN'], ['Hemogram'], ['Coagulogram'], ['SE'], ['RFT'], ['ABG/VBG'], ['RBS'], ['Special Ix'], ['APACHE IV'], ['HAS BLED'], ['MDRD GFR'], ['SOFA score'],['Other Scores'], ['INSTRUCTIONS']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    bot.send_chat_action(chat_id=update.effective_user.id, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=update.message.chat_id, text='Which field you need to edit ?', reply_markup=reply_keyboard)



df_data_dict = defaultdict(def_value)

# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('testsheet.json', scope)

bot=telegram.Bot(token='1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E')
updater = Updater(token='1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)


State_dict = defaultdict(def_value)

Patient_Id_dict = defaultdict(def_value)

SPO2, PR, BP, ANTIBIOTIC, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS = defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value), defaultdict(def_value)

editable_columns_list = ['SPO2', 'PR', 'BP', 'ANTIBIOTIC(S)', 'STOOL', 'FEVER', 'FEED', 'I/O', 'RTA/DRAIN', 'Hemogram', 'Coagulogram', 'SE', 'RFT', 'ABG/VBG', 'RBS', 'Special Ix', 'APACHE IV', 'HAS BLED', 'MDRD GFR', 'SOFA score','Other Scores', 'INSTRUCTIONS']

df_data_patient_id_dict = defaultdict(def_value)

df_data_last_row_dict = defaultdict(def_value)

Conversation_type_dict = defaultdict(def_value)

sheet = ''


#Function to start the bot,initiated on /start command
def start(bot,update):

    global df_data_dict
    global State_dict
    global sheet
    global Conversation_type_dict

    chat_id_str = str(update.message.chat_id)

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance sheet of the Spreadsheet
    sheet = client.open("Bot Spreadsheet").sheet1

    # get all the records of the data
    data = sheet.get_all_records()

    # convert the json to dataframe
    df_data_dict[chat_id_str] = pd.DataFrame.from_dict(data)

    bot.send_message(chat_id=update.message.chat_id, text='Hi, Enter the Patient_Id ')
    Conversation_type_dict[chat_id_str] = ''
    
    State_dict[chat_id_str] = 0


def getrow(bot, update):

    global Patient_Id_dict
    global df_data_patient_id_dict
    global df_data_last_row_dict
    global State_dict

    chat_id_str = str(update.message.chat_id)
    if  State_dict[chat_id_str] == 0:

        Patient_Id_dict[chat_id_str] = update.message.text
        df_data_patient_id_dict[chat_id_str] = df_data_dict[chat_id_str][df_data_dict[chat_id_str]['id'] == int(Patient_Id_dict[chat_id_str])]
        df_data_last_row_dict[chat_id_str] = df_data_patient_id_dict[chat_id_str].iloc[[-1]]

        get_update(bot, update)
        State_dict[chat_id_str] = 1


def get_updatechoice(bot,update):

    global Conversation_type_dict
    global State_dict

    chat_id_str = str(update.message.chat_id)

    if update.message.text == 'Get' and State_dict[chat_id_str] == 1:
        Get(bot,update)
        Conversation_type_dict[chat_id_str] = 'Get'
        bot.send_message(chat_id=update.message.chat_id, text='\nThanks')
    elif update.message.text == 'Update' and State_dict[chat_id_str] == 1:
        Conversation_type_dict[chat_id_str] = 'Update'
        State_dict[chat_id_str] = 2

def Get(bot,update):

    chat_id_str = str(update.message.chat_id)
    text = ''
    for column in df_data_last_row_dict[chat_id_str].columns.values:
        text = text + '\n' + column + ': ' + str(df_data_last_row_dict[chat_id_str][column].values[0])

    bot.send_message(chat_id=update.message.chat_id, text=text)


def update(bot, update):

    global SPO2, PR, BP, ANTIBIOTIC, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS
    global df_data_last_row_dict
    global State_dict

    chat_id_str = str(update.message.chat_id)

    if 2<=State_dict[chat_id_str]<=23 and Conversation_type_dict[chat_id_str] == 'Update' :
        
        if State_dict[chat_id_str]>2:
            print(f'State = {State_dict[chat_id_str]}')
            globals()[editable_columns_list[State_dict[chat_id_str]-3].replace('/','_').replace(' ','_').replace('(S)','')][chat_id_str]= update.message.text

        
        column_str = editable_columns_list[State_dict[chat_id_str]-2]
        cell = sheet.find(column_str)
        cell1 = sheet.find(str(Patient_Id_dict[chat_id_str]))
        cell2 = sheet.cell(cell1.row, cell.col).value
        bot.send_message(chat_id=update.message.chat_id, text=f'{column_str}: {cell2}')
        bot.send_message(chat_id=update.message.chat_id, text=f'Enter the new {column_str} ')
        State_dict[chat_id_str] += 1

    elif State_dict[chat_id_str] == 24 and Conversation_type_dict[chat_id_str] == 'Update':
        INSTRUCTIONS[chat_id_str] = update.message.text

        for column in editable_columns_list:
            print(df_data_last_row_dict[chat_id_str][column])
            df_data_last_row_dict[chat_id_str][column] = globals()[column.replace('/','_').replace(' ','_').replace('(S)','')][chat_id_str]
        
        Get(bot,update)
        confirm(bot, update)
        State_dict[chat_id_str] = 25



def confirmchoice(bot,update):
    
    global df_data_dict

    chat_id_str = str(update.message.chat_id)
    
    if update.message.text == 'YES' and State_dict[chat_id_str] == 25:
        df_data_dict[chat_id_str] = df_data_dict[chat_id_str].append(df_data_last_row)
        last_row_list = df_data_last_row_dict[chat_id_str].values[0].tolist()
        sheet.insert_row(last_row_list, len(df_data))
        bot.send_message(chat_id=update.message.chat_id, text='\nGood')
        State_dict[chat_id_str] = -1
    
    elif update.message.text == 'NO' and State_dict[chat_id_str] == 25:
        State_dict[chat_id_str] = 26
        edit(bot, update)


def editchoice(bot, update):

    global Conversation_type_dict
    global SPO2, PR, BP, ANTIBIOTIC, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS
    global df_data_last_row_dict
    global State_dict
    
    chat_id_str = str(update.message.chat_id)
    print("message sent by user", update.message.text)

    if (update.message.text in editable_columns_list) and 26<=State_dict[chat_id_str]<=46 and Conversation_type_dict[chat_id_str] == 'Update':

        bot.send_message(chat_id=update.message.chat_id, text='Enter the new value')
        column_index = editable_columns_list.index(update.message.text)
        State_dict[chat_id_str] = column_index + 27

    if 27<=State_dict[chat_id_str]<=47 and Conversation_type_dict[chat_id_str] == 'Update':
        new_value = update.message.text
        print(new_value)
        globals()[editable_columns_list[State_dict[chat_id_str]-27].replace('/','_').replace(' ','_').replace('(S)','')][chat_id_str] = new_value
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