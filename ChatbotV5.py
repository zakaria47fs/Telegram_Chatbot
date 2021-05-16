#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

packages:
pip install gspread
pip install gspread-dataframe
pip install telegram
pip install --upgrade google-api-python-client oauth2client
pip install python-telegram-bot
pip install numpy
pip install pandas
pip install pytz
pip install tabulate
"""

import logging

from telegram import ReplyKeyboardMarkup, ForceReply
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
import logging
from tabulate import tabulate
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from collections import defaultdict
import pytz
from datetime import datetime
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

choosing_patient_id, update_or_get, update_state, patient_information_gathered, CONFIRM, wait_edit_choice, edit_selected_choice, patient_id, enter_new_values = range(
    9)
GCS, Ventilation, SPO2, PR, BP, INOTROPE, ANALGESIA, SEDATION, ANTIBIOTIC, Other_drugs, INSULIN_infusion, ULCER_PROPHYLAXIS, REMDESIVIR, Anticoagulation, METHYLPREDNISOLONE_EQUI_DOSE_DEXA, TOCILIZUMAB, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, Date, IL_6, Ferritin, CRP, D_Dimer, LDH, CxR, APACHE_IV, HAS_BLED, GFR, SOFA_score, Other_Scores, INSTRUCTIONS = range(
    9, 50)
id, Patient_Name, Age_Sex, Day_of_Admission, Day_of_first_positive_symptoms, Diagnosis, Co_Morbidities, CTSS_scoring, Weight, Height = range(50, 60)
antibiotic_value_to_remove = 60
discharge_choosing_patient_id = 61
discharge_confirm = 62
antibiotic_state, remove_antibiotic_yes_no = range(63, 65)

reply_keyboard = [['Get', 'Update']]

editable_columns_list = ['GCS', 'Ventilation', 'SPO2', 'PR', 'BP', 'INOTROPE', 'ANALGESIA', 'SEDATION', 'ANTIBIOTIC(S)',
                         'Other drugs', 'INSULIN infusion', 'ULCER PROPHYLAXIS', 'REMDESIVIR', 'Anticoagulation',
                         'METHYLPREDNISOLONE EQUI DOSE DEXA (1.5:8)', 'TOCILIZUMAB', 'STOOL', 'FEVER', 'FEED', 'I/O',
                         'RTA/DRAIN', 'Hemogram', 'Coagulogram', 'SE', 'RFT', 'ABG/VBG', 'RBS', 'Special Ix', 'Date',
                         'IL 6', 'Ferritin', 'CRP', 'D Dimer', 'LDH', 'CxR', 'APACHE IV', 'HAS BLED', 'GFR',
                         'SOFA score', 'Other Scores', 'INSTRUCTIONS', ]
editable_columns_list_register = ['UHID', 'Patient Name', 'Age/Sex', 'Day of Admission', 'Day of first positive symptoms', 'Diagnosis',
                                  'Co-Morbidities', 'CTSS-scoring', 'Weight', 'Height']

# Read Google sheet data
# define the scope
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('testsheet.json', scope)


# Function to start the bot,initiated on /start command
def start(update, context):
    fname = update.message.from_user.first_name

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance sheet of the Spreadsheet
    sheet = client.open("Bot Spreadsheet").worksheet('Sheet1')
    context.user_data['sheet'] = sheet

    # get all the records of the data
    data = sheet.get_all_records()

    # convert the json to dataframe
    df_data = pd.DataFrame.from_dict(data)
    context.user_data['datatable'] = df_data
    context.user_data['conversation_type'] = 'start'

    update.message.reply_text(f'Hi {fname}, Enter the Patient_Id')

    return choosing_patient_id


def register(update, context):
    fname = update.message.from_user.first_name
    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance sheet of the Spreadsheet
    sheet = client.open("Bot Spreadsheet").sheet1
    context.user_data['sheet'] = sheet

    # get all the records of the data
    data = sheet.get_all_records()

    # convert the json to dataframe
    df_data = pd.DataFrame.from_dict(data)
    context.user_data['datatable'] = df_data
    context.user_data['column_index_register'] = 1
    context.user_data['conversation_type'] = 'register'
    update.message.reply_text(f'Hi {fname}, Enter the new patient UHID')

    return enter_new_values


def discharge(update, context):
    fname = update.message.from_user.first_name
    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance sheet of the Spreadsheet
    sheet = client.open("Bot Spreadsheet").sheet1
    context.user_data['sheet'] = sheet

    # get all the records of the data
    data = sheet.get_all_records()

    # convert the json to dataframe
    df_data = pd.DataFrame.from_dict(data)
    context.user_data['datatable'] = df_data
    context.user_data['conversation_type'] = 'discharge'
    update.message.reply_text(f"Hi {fname}, Enter the patient to discharge's id")

    return discharge_choosing_patient_id


def new_values(update, context):
    column_index_register = context.user_data['column_index_register']
    if column_index_register == 1:
        context.user_data['conversation_type'] = 'register'
        context.user_data['UHID'] = update.message.text

    column = editable_columns_list_register[column_index_register]

    if column_index_register > 1:
        context.user_data[editable_columns_list_register[column_index_register - 1]] = update.message.text

    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}', reply_markup=markup)
    context.user_data['column_index_register'] = column_index_register + 1
    
    if column_index_register == 9:
        print('weight')
        return Height

    return patient_id


def get_patient_id(update, context):
    patient_id = update.message.text
    context.user_data['patient_id'] = patient_id
    df_data = context.user_data['datatable']
    df_data_patient_id = 'Not found'

    if patient_id.isdigit() and (int(patient_id) in df_data['UHID'].values.tolist()):
        df_data_patient_id = df_data[df_data['UHID'] == int(patient_id)]
    elif '_' in patient_id:
        name_age = patient_id.split("_")
        name = name_age[0]
        age = name_age[1]
        df_data_patient_id = df_data[
            (df_data['Patient Name'] == str(name)) & (df_data['Age/Sex'].str.contains(f'^{age}/.*') == True)]

    if ((type(df_data_patient_id) == str) and (df_data_patient_id == 'Not found')) or len(df_data_patient_id) == 0:
        update.message.reply_text(
            text="The patient id you entered doesn't exit in our database, please enter a valid one!")
        return choosing_patient_id

    df_data_last_row = df_data_patient_id.iloc[[-1]]
    context.user_data['patient_id_row'] = df_data_last_row
    context.user_data['column_index'] = 0
    # Get/Update
    button_labels = [['Get'], ['Update']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(text='Get or Update ?', reply_markup=markup)

    return update_or_get


def get_patient_id_discharge(update, context):
    patient_id = update.message.text
    context.user_data['patient_id'] = patient_id
    df_data = context.user_data['datatable']
    df_data_patient_id = 'Not found'

    if patient_id.isdigit() and (int(patient_id) in df_data['UHID'].values.tolist()):
        df_data_patient_id = df_data[df_data['UHID'] == int(patient_id)]
    elif '_' in patient_id:
        name_age = patient_id.split("_")
        name = name_age[0]
        age = name_age[1]
        df_data_patient_id = df_data[
            (df_data['Patient Name'] == str(name)) & (df_data['Age/Sex'].str.contains(f'^{age}/.*') == True)]

    if ((type(df_data_patient_id) == str) and (df_data_patient_id == 'Not found')) or len(df_data_patient_id) == 0:
        update.message.reply_text(
            text="The patient id you entered doesn't exit in our database, please enter a valid one!")
        return discharge_choosing_patient_id

    df_data_last_row = df_data_patient_id.iloc[[-1]]
    context.user_data['patient_id_row'] = df_data_last_row
    text = ''
    for column in df_data_last_row.columns.values[:-1]:
        text = text + '\n' + column + ': ' + str(df_data_last_row[column].values[0])
    update.message.reply_text(text)

    # Confirm patient discharge
    button_labels = [['YES'], ['NO']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(text='Confirm discharging the selected patient?', reply_markup=markup)

    return discharge_confirm


def get_patient_info(update, context):
    context.user_data['conversation_type'] = 'Get'
    df_data_last_row = context.user_data['patient_id_row']
    text = ''
    for column in df_data_last_row.columns.values[:-1]:
        text = text + '\n' + column + ': ' + str(df_data_last_row[column].values[0])

    update.message.reply_text(text)
    button_labels = [['Update'], ['/Done']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text("Enter 'Update' to edit patient information or click on '/Done' to finish the chat",
                              reply_markup=markup)

    return None


def update_patient_info(update, context):
    if context.user_data['patient_id_row'].iloc[0]['Discharged'] == 'YES':
        update.message.reply_text("You can't update the selected patient information because he has been discharged!")
        done(update, context)
        return ConversationHandler.END

    column_index = context.user_data['column_index']
    if column_index == 0:
        context.user_data['conversation_type'] = 'Update'

    column = editable_columns_list[column_index]

    if column_index > 0 and column_index != 9:
        if update.message.text.lower() == 'same':
            context.user_data[editable_columns_list[column_index - 1]] = \
            context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
        # Antibiotics column
        # elif column_index==9:
        #    context.user_data[editable_columns_list[8]] =  context.user_data['patient_id_row'][editable_columns_list[8]].values[0] + '\n' + update.message.text
        else:
            context.user_data[editable_columns_list[column_index - 1]] = update.message.text

    markup = ForceReply(True, False)
    if 20 < column_index < 28:
        button_labels = [['WNL']]
        markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)

    if column_index == 1 or 4 < column_index < 16 or 27 < column_index < 35 or column_index == 18:
        button_labels = [['same']]
        markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)

        old_value = context.user_data['patient_id_row'][column].values[0]
        update.message.reply_text(f'Old {column} value: {old_value}')

    update.message.reply_text(f'Enter the new {column}', reply_markup=markup)
    context.user_data['column_index'] = column_index + 1

    if column_index == 8:  # Antibiotics column
        return antibiotic_state

    if column_index == 40:
        return INSTRUCTIONS

    return SPO2


def antibiotic_line(update, context):
    column_index = context.user_data['column_index']
    if column_index == 0:
        context.user_data['conversation_type'] = 'Update'

    column = editable_columns_list[column_index]

    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[8]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[8]] = \
        context.user_data['patient_id_row'][editable_columns_list[8]].values[0] + '\n' + update.message.text

    button_labels = [['YES'], ['NO']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text("Do you need to remove any ANTIBIOTIC?", reply_markup=reply_keyboard)

    return remove_antibiotic_yes_no


def get_antibiotic_line(update, context):
    column = editable_columns_list[8]
    antibiotic_text = context.user_data[column]
    button_labels = []
    for antibotic_line in antibiotic_text.strip().split('\n'):
        button_labels.append([f'({len(button_labels) + 1})- {antibotic_line}'])

    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    update.message.reply_text(f'Old {column} value: {context.user_data[column]}'
                              f'\nSelect Antibiotic line to remove', reply_markup=reply_keyboard)

    return antibiotic_value_to_remove


def received_information(update, context):
    if context.user_data['conversation_type'] == 'Update':
        column_index = context.user_data['column_index']
        if update.message.text.lower() == 'same':
            context.user_data[editable_columns_list[column_index - 1]] = \
            context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
        else:
            context.user_data[editable_columns_list[column_index - 1]] = update.message.text

    if context.user_data['conversation_type'] == 'register':
        column_index_register = context.user_data['column_index_register']
        context.user_data[editable_columns_list_register[column_index_register - 1]] = update.message.text
    log_received_information(update, context)
    
    return CONFIRM


def log_received_information(update, context):
    text = ''

    if context.user_data['conversation_type'] == 'Update':
        for column in editable_columns_list:
            text = text + '\n' + column + ': ' + str(context.user_data[column])
            

    elif context.user_data['conversation_type'] == 'register':
        for column in editable_columns_list_register:
            text = text + '\n' + column + ': ' + str(context.user_data[column])

           
    update.message.reply_text(text)
    button_labels = [['YES'], ['NO']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text("Confirm please!", reply_markup=reply_keyboard)

    return CONFIRM

def edit(update, context):
    if context.user_data['conversation_type'] == 'Update':
        button_labels = [['GCS'], ['Ventilation'], ['SPO2'], ['PR'], ['BP'], ['INOTROPE'], ['ANALGESIA'], ['SEDATION'],
                         ['ANTIBIOTIC(S)'], ['Other drugs'], ['INSULIN infusion'], ['ULCER PROPHYLAXIS'],
                         ['REMDESIVIR'], ['Anticoagulation'], ['METHYLPREDNISOLONE EQUI DOSE DEXA (1.5:8)'],
                         ['TOCILIZUMAB'], ['STOOL'], ['FEVER'], ['FEED'], ['I/O'], ['RTA/DRAIN'], ['Hemogram'],
                         ['Coagulogram'], ['SE'], ['RFT'], ['ABG/VBG'], ['RBS'], ['Special Ix'], ['Date'], ['IL 6'],
                         ['Ferritin'], ['CRP'], ['D Dimer'], ['LDH'], ['CxR'], ['APACHE IV'], ['HAS BLED'], ['GFR'],
                         ['SOFA score'], ['Other Scores'], ['INSTRUCTIONS']]

    if context.user_data['conversation_type'] == 'register':
        button_labels = [['UHID'], ['Patient Name'], ['Age/Sex'], ['Day of Admission'], ['Day of first positive symptoms'],
                         ['Diagnosis'], ['Co-Morbidities'], ['CTSS-scoring'], ['Weight'], ['Height'] ]

    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)

    update.message.reply_text('Which field you need to edit ?', reply_markup=reply_keyboard)

    return wait_edit_choice


def get_column_to_edit(update, context):
    column = update.message.text
    context.user_data['field_to_edit'] = column
    markup = ForceReply(True, False)
    update.message.reply_text(f'Old {column} value: {context.user_data[column]}'
                              f'\nEnter {column} new value', reply_markup=markup)

    return edit_selected_choice


def edit_choice(update, context):
    column = context.user_data['field_to_edit']
    if column == editable_columns_list[8]:
        context.user_data[column] = context.user_data['patient_id_row'][editable_columns_list[8]].values[
                                        0] + '\n' + update.message.text
    else:
        context.user_data[column] = update.message.text
    if 'field_to_edit' in context.user_data:
        del context.user_data['field_to_edit']

    log_received_information(update, context)

    return CONFIRM


def remove_selected_antibiotic(update, context):
    column = editable_columns_list[8]
    line_index = int(re.search('^\((.*)\)-', update.message.text).group(1))
    antibiotic_text = context.user_data[editable_columns_list[8]]
    new_antibiotic_value = ''
    antibiotic_lines = antibiotic_text.strip().split('\n')
    for i in range(len(antibiotic_lines)):
        if i != line_index - 1:
            new_antibiotic_value = new_antibiotic_value + '\n' + antibiotic_lines[i]

    new_antibiotic_value = new_antibiotic_value.strip()
    context.user_data[editable_columns_list[8]] = new_antibiotic_value

    update.message.reply_text(f'New {column} value: {new_antibiotic_value}')

    button_labels = [['YES'], ['NO']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text("Do you need to remove any other ANTIBIOTIC?", reply_markup=reply_keyboard)

    return remove_antibiotic_yes_no


def done(update, context):
    if 'conversation_type' in context.user_data and context.user_data['conversation_type'] == 'Update' or \
            context.user_data['conversation_type'] == 'register' or context.user_data[
        'conversation_type'] == 'discharge':
        # authorize the clientsheet
        client = gspread.authorize(creds)

        # get the instance sheet of the Spreadsheet
        sheet = client.open("Bot Spreadsheet").sheet1

        # get all the records of the data
        data = sheet.get_all_records()

        # convert the json to dataframe
        df_data = pd.DataFrame.from_dict(data)

        IST = pytz.timezone('Asia/Kolkata')
        now = datetime.now(IST)
        IST_now = now.strftime("%d/%m/%Y %H:%M:%S")

        if context.user_data['conversation_type'] == 'Update':

            for column in editable_columns_list:
                context.user_data['patient_id_row'][column] = context.user_data[column]

            context.user_data['patient_id_row']['Save time'] = IST_now
            df_data = df_data.append(context.user_data['patient_id_row'])
            last_row_list = context.user_data['patient_id_row'].values[0].tolist()
            sheet.insert_row(last_row_list, len(df_data) + 1)

            update.message.reply_text("Record saved!")

        elif context.user_data['conversation_type'] == 'register':

            df_data_len = len(df_data)
            for column in editable_columns_list_register:
                df_data.at[df_data_len, column] = context.user_data[column]

            df_data.at[df_data_len, 'Save time'] = IST_now
            df_data.at[df_data_len, 'Discharged'] = 'NO'

            df_data.iloc[- 1].fillna('')
            new_row_list = df_data.iloc[- 1].fillna('').values.tolist()
            sheet.insert_row(new_row_list, len(df_data) + 1)

            update.message.reply_text("Record saved!")

        elif context.user_data['conversation_type'] == 'discharge':

            context.user_data['patient_id_row']['Discharged'] = 'YES'
            context.user_data['patient_id_row']['Save time'] = IST_now
            df_data = df_data.append(context.user_data['patient_id_row'])
            last_row_list = context.user_data['patient_id_row'].values[0].tolist()
            sheet.insert_row(last_row_list, len(df_data) + 1)

            update.message.reply_text(text='The patient has been discharged successfully!')

    update.message.reply_text("Until next time!""\nBye!")
    context.user_data.clear()

    return ConversationHandler.END


def cancel(update, context):
    if ('conversation_type' in context.user_data) and (context.user_data['conversation_type'] == 'discharge'):
        update.message.reply_text(text='Discharging has been cancelled!\nEnter /discharge to select another patient')

    else:
        update.message.reply_text('Record has been cancelled!'
                                  '\nBye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
                                  )

    context.user_data.clear()

    return ConversationHandler.END


def log_user_message(update, context):
    print(f'Message sent by {update.message.from_user.first_name}: {update.message.text}')


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # Misktok: 1366155886:AAH98WssxAmqqnv6xXdWPVsco9-qKtgHWP0
    # Covidtok: 1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E
    # meryemhamdanebot: 1825224146:AAEBZVTH0fCwkwHVnPrRIM7nGOnPvzF0trM
    updater = Updater("1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E", use_context=True)

    print('Bot has started ...')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            choosing_patient_id: [
                MessageHandler(Filters.text & ~Filters.command, get_patient_id)
            ],

            update_or_get: [
                MessageHandler(Filters.regex('^Get$'), get_patient_info),
                MessageHandler(Filters.regex('^Update$'), update_patient_info)
            ],

            SPO2: [
                MessageHandler(Filters.text & ~Filters.command, update_patient_info)
            ],

            antibiotic_state: [
                MessageHandler(Filters.text & ~Filters.command, antibiotic_line)
            ],

            remove_antibiotic_yes_no: [
                MessageHandler(Filters.regex('^YES$'), get_antibiotic_line),
                MessageHandler(Filters.regex('^NO$'), update_patient_info)
            ],

            antibiotic_value_to_remove: [
                MessageHandler(Filters.text & ~Filters.command, remove_selected_antibiotic)
            ],

            INSTRUCTIONS: [
                MessageHandler(Filters.text & ~Filters.command, received_information)
            ],

            CONFIRM: [
                MessageHandler(Filters.regex('^YES$'), done),
                MessageHandler(Filters.regex('^NO$'), edit)
            ],

            wait_edit_choice: [
                MessageHandler(Filters.text & ~Filters.command, get_column_to_edit)
            ],

            edit_selected_choice: [
                MessageHandler(Filters.text & ~Filters.command, edit_choice)
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('register', register)],

        states={

            enter_new_values: [
                MessageHandler(Filters.text & ~Filters.command, new_values)
            ],

            patient_id: [
                MessageHandler(Filters.text & ~Filters.command, new_values)
            ],

            Height: [
                MessageHandler(Filters.text & ~Filters.command, received_information)
            ],

            CONFIRM: [
                MessageHandler(Filters.regex('^YES$'), done),
                MessageHandler(Filters.regex('^NO$'), edit)
               
               
                
              
            ],

            wait_edit_choice: [
                MessageHandler(Filters.text & ~Filters.command, get_column_to_edit)
            ],

            edit_selected_choice: [
                MessageHandler(Filters.text & ~Filters.command, edit_choice)
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler3 = ConversationHandler(
        entry_points=[CommandHandler('discharge', discharge)],

        states={

            discharge_choosing_patient_id: [
                MessageHandler(Filters.text & ~Filters.command, get_patient_id_discharge)
            ],

            discharge_confirm: [
                MessageHandler(Filters.regex('^YES$'), done),
                MessageHandler(Filters.regex('^NO$'), cancel)
            ],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler2)
    dp.add_handler(conv_handler3)
    dp.add_handler(MessageHandler(Filters.text, log_user_message), group=1)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
