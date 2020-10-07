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
df_data_patient_id = pd.DataFrame()

df_data_last_row = pd.DataFrame()

Conversation_type = ''


#Function to start the bot,initiated on /start command
def start(bot,update):
    chat_id_str = str(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id, text='Hi, Enter the Patient_Id ')
    State_dict[chat_id_str] = 1

def main0(bot, update):

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


def type_(bot,update):

    global Conversation_type

    reply_markup = telegram.ReplyKeyboardRemove()
    chat_id_str = str(update.message.chat_id)

    print("message sent by user",update.message.text)
    if update.message.text == 'Get' and State_dict[chat_id_str] == 2:
        Get(bot,update)
        Conversation_type = 'Get'
        bot.send_message(chat_id=update.message.chat_id, text='\nThanks')
    elif update.message.text == 'Update' and State_dict[chat_id_str] == 2:
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


def update1(bot, update):

    global SPO2, PR, BP, ANTIBIOTIC, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS
    global Patient_Id
    chat_id_str = str(update.message.chat_id)

    if State_dict[chat_id_str] == 2 and Conversation_type == 'Update' :
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new SPO2 ')
        State_dict[chat_id_str] = 3
    elif State_dict[chat_id_str] == 3 and Conversation_type == 'Update':
        cell = sheet.find("SPO2")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row,cell.col).value
        SPO2 = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {SPO2} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new PR ')
        State_dict[chat_id_str] = 4
    elif State_dict[chat_id_str] == 4 and Conversation_type == 'Update':
        cell = sheet.find("PR")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row,cell.col).value
        PR = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {PR} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new BP ')
        State_dict[chat_id_str] = 5
    elif State_dict[chat_id_str] == 5 and Conversation_type == 'Update':
        cell = sheet.find("BP")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row,cell.col).value
        BP = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {BP} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new ANTIBIOTIC(S) ')
        State_dict[chat_id_str] = 6
    elif State_dict[chat_id_str] == 6 and Conversation_type == 'Update':
        cell = sheet.find("ANTIBIOTIC(S)")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        ANTIBIOTIC = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {ANTIBIOTIC} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new STOOL ')
        State_dict[chat_id_str] = 7
    elif State_dict[chat_id_str] == 7 and Conversation_type == 'Update':
        cell = sheet.find("STOOL")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        STOOL = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {STOOL} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new FEVER ')
        State_dict[chat_id_str] = 8
    elif State_dict[chat_id_str] == 8 and Conversation_type == 'Update':
        cell = sheet.find("FEVER")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        FEVER = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {FEVER} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new FEED ')
        State_dict[chat_id_str] = 9
    elif State_dict[chat_id_str] == 9 and Conversation_type == 'Update':
        cell = sheet.find("FEED")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        FEED = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {FEED} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new I/O ')
        State_dict[chat_id_str] = 10
    elif State_dict[chat_id_str] == 10 and Conversation_type == 'Update':
        cell = sheet.find("I/O")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        I_O = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {I_O} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new RTA/DRAIN ')
        State_dict[chat_id_str] = 11
    elif State_dict[chat_id_str] == 10 and Conversation_type == 'Update':
        cell = sheet.find("RTA/DRAIN")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        RTA_DRAIN= update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {RTA_DRAIN} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Hemogram ')
        State_dict[chat_id_str] = 11
    elif State_dict[chat_id_str] == 11 and Conversation_type == 'Update':
        cell = sheet.find("Hemogram")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        Hemogram = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {Hemogram} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Coagulogram ')
        State_dict[chat_id_str] = 12
    elif State_dict[chat_id_str] == 12 and Conversation_type == 'Update':
        cell = sheet.find("Coagulogram")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        Coagulogram = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {Coagulogram} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new SE ')
        State_dict[chat_id_str] = 13
    elif State_dict[chat_id_str] == 13 and Conversation_type == 'Update':
        cell = sheet.find("SE")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        SE = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {SE} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new RFT ')
        State_dict[chat_id_str] = 14
    elif State_dict[chat_id_str] == 14 and Conversation_type == 'Update':
        cell = sheet.find("RFT")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        RFT = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {RFT} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new ABG/VBG ')
        State_dict[chat_id_str] = 15
    elif State_dict[chat_id_str] == 15 and Conversation_type == 'Update':
        cell = sheet.find("ABG/VBG")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        ABG_VBG = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {ABG_VBG} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new RBS ')
        State_dict[chat_id_str] = 16
    elif State_dict[chat_id_str] == 16 and Conversation_type == 'Update':
        cell = sheet.find("RBS")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        RBS = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {RBS} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Special Ix')
        State_dict[chat_id_str] = 17
    elif State_dict[chat_id_str] == 17 and Conversation_type == 'Update':
        cell = sheet.find("Special Ix")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        Special_Ix = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {Special_Ix} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new APACHE IV ')
        State_dict[chat_id_str] = 18
    elif State_dict[chat_id_str] == 18 and Conversation_type == 'Update':
        cell = sheet.find("APACHE IV")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        APACHE_IV = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {APACHE_IV} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new HAS BLED ')
        State_dict[chat_id_str] = 19
    elif State_dict[chat_id_str] == 19 and Conversation_type == 'Update':
        cell = sheet.find("HAS BLED")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        HAS_BLED = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {HAS_BLED} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new MDRD GFR ')
        State_dict[chat_id_str] = 20
    elif State_dict[chat_id_str] == 20 and Conversation_type == 'Update':
        cell = sheet.find("MDRD GFR")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        MDRD_GFR = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {MDRD_GFR} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new SOFA score ')
        State_dict[chat_id_str] = 21
    elif State_dict[chat_id_str] == 21 and Conversation_type == 'Update':
        cell = sheet.find("SOFA score")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        SOFA_score = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {SOFA_score} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new Other Scores ')
        State_dict[chat_id_str] = 22
    elif State_dict[chat_id_str] == 22 and Conversation_type == 'Update':
        cell = sheet.find("Other Scores")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        Other_Scores = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {Other_Scores} ')
        bot.send_message(chat_id=update.message.chat_id, text='Enter the new INSTRUCTIONS ')
        State_dict[chat_id_str] = 23
    elif State_dict[chat_id_str] == 23 and Conversation_type == 'Update':
        cell = sheet.find("INSTRUCTIONS")
        cell1 = sheet.find(str(Patient_Id))
        cell2 = sheet.cell(cell1.row, cell.col).value
        INSTRUCTIONS = update.message.text
        bot.send_message(chat_id=update.message.chat_id, text=f'old value: {cell2}\n new value: {INSTRUCTIONS} ')
        State_dict[chat_id_str] = 24
    elif State_dict[chat_id_str] == 24 and Conversation_type == 'Update':
        Get(bot, update)
        confirm(bot, update)
        State_dict[chat_id_str] = 25


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
    bot.send_message(chat_id=update.message.chat_id, text='Get or Update ?', reply_markup=reply_keyboard)

def editchoice(bot, update):
    reply_markup = telegram.ReplyKeyboardRemove()

    print("message sent by user", update.message.text)
    if update.message.text == 'SPO2':
        pass


def main():

    updater.dispatcher.add_handler(CommandHandler('start',start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, main0), group=0)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, type_), group=1)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, update1), group=2)
    updater.start_polling()

    # Stop the bot if Ctrl + C was pressed
    updater.idle()


if __name__ == "__main__":
    main()