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
"""

import logging

from telegram import ReplyKeyboardMarkup, ForceReply
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

import telegram
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,CallbackQueryHandler
from telegram import InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup
import logging
from tabulate import tabulate
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from collections import defaultdict


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

choosing_patient_id, update_or_get, update_state, patient_information_gathered, CONFIRM, wait_edit_choice, edit_selected_choice = range(7)
SPO2, PR, BP, INSTRUCTIONS = range(7,11)


reply_keyboard = [['Get','Update']]

editable_columns_list = ['SPO2', 'PR', 'BP', 'INSTRUCTIONS']


# Read Google sheet data
# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']

# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('testsheet.json', scope)


#Function to start the bot,initiated on /start command
def start(update, context):
    fname = update.message.from_user.first_name

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance sheet of the Spreadsheet
    sheet = client.open("Bot Spreadsheet").sheet1

    # get all the records of the data
    data = sheet.get_all_records()

    # convert the json to dataframe
    df_data = pd.DataFrame.from_dict(data)
    context.user_data['datatable']  = df_data

    update.message.reply_text(f'Hi {fname}, Enter the Patient_Id')

    return choosing_patient_id


def get_patient_id(update, context):
    patient_id = update.message.text
    context.user_data['patient_id'] = patient_id
    df_data = context.user_data['datatable']
    df_data_patient_id = df_data[df_data['id'] == int(patient_id)]
    df_data_last_row = df_data_patient_id.iloc[[-1]]
    context.user_data['patient_id_row'] = df_data_last_row

    # Get/Update
    button_labels = [['Get'], ['Update']]
    #reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(text='Get or Update ?',reply_markup=markup)

    return update_or_get


def get_patient_info(update, context):
    print('Get')
    print(update.message.text)
    df_data_last_row = context.user_data['patient_id_row']
    text = ''
    for column in df_data_last_row.columns.values:
        text = text + '\n' + column + ': ' + str(df_data_last_row[column].values[0])

    update.message.reply_text(text)
    update.message.reply_text("Enter 'Update' to edit patient information or click on '/Done' to finish the chat")
    
    return None

'''
def update_case(update, context):
    column = 'SPO2'
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    
    return update_state 
'''

def update_patient_info_SPO2(update, context):
    column_index = 0
    column = editable_columns_list[column_index]
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column)


def update_patient_info_PR(update, context):
    column_index = 1
    column = editable_columns_list[column_index]
    context.user_data[editable_columns_list[column_index-1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column)

def update_patient_info_BP(update, context):
    column_index = 2
    column = editable_columns_list[column_index]
    context.user_data[editable_columns_list[column_index-1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column)

def update_patient_info_Instructions(update, context):
    column_index = 3
    column = editable_columns_list[column_index]
    context.user_data[editable_columns_list[column_index-1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column)

def received_information(update, context):
    column_index = 4
    context.user_data[editable_columns_list[column_index-1]] = update.message.text
    log_received_information(update, context)

    return CONFIRM

def log_received_information(update, context):
    text = ''
    for column in editable_columns_list:
        text = text + '\n' + column + ': ' + context.user_data[column]
    update.message.reply_text(text)

    button_labels = [['YES'], ['NO']]
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text('Confirm please', reply_markup=reply_keyboard)
    
    return CONFIRM

def edit(update, context):
    update.message.reply_text('Under restruction...')
    button_labels = [['SPO2'], ['PR'], ['BP'], ['ANTIBIOTIC(S)'], ['STOOL'], ['FEVER'], ['FEED'], ['I/O'], ['RTA/DRAIN'], ['Hemogram'], ['Coagulogram'], ['SE'], ['RFT'], ['ABG/VBG'], ['RBS'], ['Special Ix'], ['APACHE IV'], ['HAS BLED'], ['MDRD GFR'], ['SOFA score'],['Other Scores'], ['INSTRUCTIONS']]
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
    context.user_data[column] = update.message.text
    if 'field_to_edit' in context.user_data:
        del context.user_data['field_to_edit']

    log_received_information(update, context)
    
    return CONFIRM

def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "Until next time!"
                              "\nBye!")

    user_data.clear()
    return ConversationHandler.END

def log_user_message(update, context):
    print(f'Message sent by user: {update.message.text}')


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1366155886:AAH98WssxAmqqnv6xXdWPVsco9-qKtgHWP0", use_context=True)

    print('Bot has started ...')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            choosing_patient_id:[
                MessageHandler(Filters.text, get_patient_id)
            ],

            update_or_get: [
                MessageHandler(Filters.regex('^Get$'), get_patient_info),
                MessageHandler(Filters.regex('^Update$'), update_patient_info_SPO2)
            ],

            #update_state:[
            #    MessageHandler(Filters.text, update_patient_info_SPO2)
            #],

            SPO2:[
                MessageHandler(Filters.text, update_patient_info_PR)
            ],

            PR:[
                MessageHandler(Filters.text, update_patient_info_BP)
            ],
            
            BP:[
                MessageHandler(Filters.text, update_patient_info_Instructions)
            ],

            INSTRUCTIONS:[
                MessageHandler(Filters.text, received_information)
            ],

            CONFIRM:[
                MessageHandler(Filters.regex('^YES$'), done),
                MessageHandler(Filters.regex('^NO$'), edit)
            ],
            
            wait_edit_choice:[
                MessageHandler(Filters.text, get_column_to_edit)
            ],

            edit_selected_choice:[
                MessageHandler(Filters.text, edit_choice)
            ]
        },

        fallbacks=[CommandHandler('Done', done),
                MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text, log_user_message), group=1)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()