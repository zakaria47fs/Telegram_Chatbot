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
GCS, Ventilation, SPO2, PR, BP, INOTROPE, ANALGESIA, SEDATION, ANTIBIOTIC, Other_drugs, INSULIN_infusion, ULCER_PROPHYLAXIS, REMDESIVIR, CLEXANE, METHYLPREDNISOLONE_EQUI_DOSE_DEXA, TOCILIZUMAB, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, Date, IL_6, Ferritin, CRP, D_Dimer, LDH, CxR, APACHE_IV, HAS_BLED, MDRD_GFR, SOFA_score, Other_Scores, INSTRUCTIONS = range(7,48)


reply_keyboard = [['Get','Update']]

editable_columns_list = ['GCS', 'Ventilation', 'SPO2', 'PR', 'BP', 'INOTROPE', 'ANALGESIA', 'SEDATION', 'ANTIBIOTIC(S)', 'Other drugs', 'INSULIN infusion', 'ULCER PROPHYLAXIS', 'REMDESIVIR', 'CLEXANE', 'METHYLPREDNISOLONE EQUI DOSE DEXA (1.5:8)', 'TOCILIZUMAB', 'STOOL' , 'FEVER', 'FEED', 'I/O', 'RTA/DRAIN', 'Hemogram', 'Coagulogram', 'SE', 'RFT', 'ABG/VBG', 'RBS', 'Special Ix', 'Date', 'IL 6', 'Ferritin', 'CRP', 'D Dimer', 'LDH', 'CxR', 'APACHE IV', 'HAS BLED', 'MDRD GFR', 'SOFA score', 'Other Scores', 'INSTRUCTIONS',]


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
    context.user_data['sheet'] = sheet

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

def update_patient_info_GCS(update, context):
    column_index = 0
    column = editable_columns_list[column_index]
    markup = ForceReply(True, False)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_Ventilation(update, context):
    column_index = 1
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)

    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_SPO2(update, context):
    column_index = 2
    column = editable_columns_list[column_index]
    if update.message.text.lower()=='same':
        context.user_data[editable_columns_list[column_index - 1]] = context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index-1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_PR(update, context):
    column_index = 3
    column = editable_columns_list[column_index]
    if update.message.text.lower()=='same':
        context.user_data[editable_columns_list[column_index - 1]] = context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index-1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_BP(update, context):
    column_index = 4
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_INOTROPE(update, context):
    column_index = 5
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_ANALGESIA(update, context):
    column_index = 6
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_SEDATION(update, context):
    column_index = 7
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_ANTIBIOTIC(update, context):
    column_index = 8
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_Other_drugs(update, context):
    column_index = 9
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_INSULIN_infusion(update, context):
    column_index = 10
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_ULCER_PROPHYLAXIS(update, context):
    column_index = 11
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_REMDESIVIR(update, context):
    column_index = 12
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_CLEXANE(update, context):
    column_index = 13
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_METHYLPREDNISOLONE_EQUI_DOSE_DEXA(update, context):
    column_index = 14
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_TOCILIZUMAB(update, context):
    column_index = 15
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    # reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_STOOL(update, context):
    column_index = 16
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_FEVER(update, context):
    column_index = 17
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_FEED(update, context):
    column_index = 18
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_I_O(update, context):
    column_index = 19
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_RTA_DRAIN(update, context):
    column_index = 20
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_Hemogram(update, context):
    column_index = 21
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['WNL']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_Coagulogram(update, context):
    column_index = 22
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['WNL']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_SE(update, context):
    column_index = 23
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['WNL']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_RFT(update, context):
    column_index = 24
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['WNL']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_ABG_VBG(update, context):
    column_index = 25
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['WNL']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_RBS(update, context):
    column_index = 26
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['WNL']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_Special_Ix(update, context):
    column_index = 27
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['WNL']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_Date(update, context):
    column_index = 28
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_IL_6(update, context):
    column_index = 29
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_Ferritin(update, context):
    column_index = 30
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_CRP(update, context):
    column_index = 31
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_D_Dimer(update, context):
    column_index = 32
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_LDH(update, context):
    column_index = 33
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_CxR(update, context):
    column_index = 34
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    button_labels = [['same']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    old_value = context.user_data['patient_id_row'][column].values[0]
    update.message.reply_text(f'Old {column} value: {old_value}')
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_APACHE_IV(update, context):
    column_index = 35
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def update_patient_info_HAS_BLED(update, context):
    column_index = 36
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_MDRD_GFR(update, context):
    column_index = 37
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_SOFA_score(update, context):
    column_index = 38
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_Other_Scores(update, context):
    column_index = 39
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))

def update_patient_info_Instructions(update, context):
    column_index = 40
    column = editable_columns_list[column_index]
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter the new {column}',reply_markup=markup)
    return eval(column.replace('/','_').replace(' ','_').replace('(S)','').replace(' (1.5:8)',''))


def received_information(update, context):
    column_index = 41
    if update.message.text.lower() == 'same':
        context.user_data[editable_columns_list[column_index - 1]] = \
        context.user_data['patient_id_row'][editable_columns_list[column_index - 1]].values[0]
    else:
        context.user_data[editable_columns_list[column_index - 1]] = update.message.text
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
    button_labels = [['GCS'], ['Ventilation'], ['SPO2'], ['PR'], ['BP'], ['INOTROPE'], ['ANALGESIA'], ['SEDATION'], ['ANTIBIOTIC(S)'], ['Other drugs'], ['INSULIN infusion'], ['ULCER PROPHYLAXIS'], ['REMDESIVIR'], ['CLEXANE'], ['METHYLPREDNISOLONE EQUI DOSE DEXA (1.5:8)'], ['TOCILIZUMAB'], ['STOOL'], ['FEVER'], ['FEED'], ['I/O'], ['RTA/DRAIN'], ['Hemogram'], ['Coagulogram'], ['SE'], ['RFT'], ['ABG/VBG'], ['RBS'], ['Special Ix'], ['Date'], ['IL 6'], ['Ferritin'], ['CRP'], ['D Dimer'], ['LDH'], ['CxR'], ['APACHE IV'], ['HAS BLED'], ['MDRD GFR'], ['SOFA score'],['Other Scores'], ['INSTRUCTIONS']]
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
    for column in editable_columns_list:
        context.user_data['patient_id_row'][column] =  context.user_data[column]
    context.user_data['datatable'] = context.user_data['datatable'].append(context.user_data['patient_id_row'])
    last_row_list = context.user_data['patient_id_row'].values[0].tolist()
    context.user_data['sheet'].insert_row(last_row_list, len(context.user_data['datatable']))

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
    updater = Updater("1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E", use_context=True)

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
                MessageHandler(Filters.regex('^Update$'), update_patient_info_GCS)
            ],

            #update_state:[
            #    MessageHandler(Filters.text, update_patient_info_SPO2)
            #],

            GCS:[
                MessageHandler(Filters.text, update_patient_info_Ventilation)
            ],

            Ventilation:[
                MessageHandler(Filters.text, update_patient_info_SPO2)
            ],

            SPO2:[
                MessageHandler(Filters.text, update_patient_info_PR)
            ],

            PR:[
                MessageHandler(Filters.text, update_patient_info_BP)
            ],
            
            BP:[
                MessageHandler(Filters.text, update_patient_info_INOTROPE)
            ],

            INOTROPE: [
                MessageHandler(Filters.text, update_patient_info_ANALGESIA)
            ],

            ANALGESIA: [
                MessageHandler(Filters.text, update_patient_info_SEDATION)
            ],

            SEDATION: [
                MessageHandler(Filters.text, update_patient_info_ANTIBIOTIC)
            ],

            ANTIBIOTIC: [
                MessageHandler(Filters.text, update_patient_info_Other_drugs)
            ],

            Other_drugs: [
                MessageHandler(Filters.text, update_patient_info_INSULIN_infusion)
            ],

            INSULIN_infusion: [
                MessageHandler(Filters.text, update_patient_info_ULCER_PROPHYLAXIS)
            ],

            ULCER_PROPHYLAXIS: [
                MessageHandler(Filters.text, update_patient_info_REMDESIVIR)
            ],

            REMDESIVIR: [
                MessageHandler(Filters.text, update_patient_info_CLEXANE)
            ],

            CLEXANE: [
                MessageHandler(Filters.text, update_patient_info_METHYLPREDNISOLONE_EQUI_DOSE_DEXA)
            ],

            METHYLPREDNISOLONE_EQUI_DOSE_DEXA : [
                MessageHandler(Filters.text, update_patient_info_TOCILIZUMAB)
            ],

            TOCILIZUMAB: [
                MessageHandler(Filters.text, update_patient_info_STOOL)
            ],

            STOOL: [
                MessageHandler(Filters.text, update_patient_info_FEVER)
            ],

            FEVER: [
                MessageHandler(Filters.text, update_patient_info_FEED)
            ],

            FEED: [
                MessageHandler(Filters.text, update_patient_info_I_O)
            ],

            I_O: [
                MessageHandler(Filters.text, update_patient_info_RTA_DRAIN)
            ],

            RTA_DRAIN: [
                MessageHandler(Filters.text, update_patient_info_Hemogram)
            ],

            Hemogram: [
                MessageHandler(Filters.text, update_patient_info_Coagulogram)
            ],

            Coagulogram: [
                MessageHandler(Filters.text, update_patient_info_SE)
            ],

            SE: [
                MessageHandler(Filters.text, update_patient_info_RFT)
            ],

            RFT: [
                MessageHandler(Filters.text, update_patient_info_ABG_VBG)
            ],

            ABG_VBG: [
                MessageHandler(Filters.text, update_patient_info_RBS)
            ],

            RBS: [
                MessageHandler(Filters.text, update_patient_info_Special_Ix)
            ],

            Special_Ix: [
                MessageHandler(Filters.text, update_patient_info_Date)
            ],

            Date: [
                MessageHandler(Filters.text, update_patient_info_IL_6)
            ],

            IL_6: [
                MessageHandler(Filters.text, update_patient_info_Ferritin)
            ],

            Ferritin: [
                MessageHandler(Filters.text, update_patient_info_CRP)
            ],

            CRP: [
                MessageHandler(Filters.text, update_patient_info_D_Dimer)
            ],

            D_Dimer: [
                MessageHandler(Filters.text, update_patient_info_LDH)
            ],

            LDH: [
                MessageHandler(Filters.text, update_patient_info_CxR)
            ],

            CxR: [
                MessageHandler(Filters.text, update_patient_info_APACHE_IV)
            ],

            APACHE_IV: [
                MessageHandler(Filters.text, update_patient_info_HAS_BLED)
            ],

            HAS_BLED: [
                MessageHandler(Filters.text, update_patient_info_MDRD_GFR)
            ],

            MDRD_GFR: [
                MessageHandler(Filters.text, update_patient_info_SOFA_score)
            ],

            SOFA_score: [
                MessageHandler(Filters.text, update_patient_info_Other_Scores)
            ],

            Other_Scores: [
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
