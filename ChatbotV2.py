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

advice_plan, choosing_patient_name, Done, choosing_patient_id, update_or_get, update_state, patient_information_gathered, CONFIRM, wait_edit_choice, edit_selected_choice, patient_id, enter_new_values = range(
    12)
    
GCS, ventilation_value, SPO2, PR, BP, SPO2_vitals, next_value, bipap, feed_value, calories, stool_passed, ULCER_PROPHYLAXIS, CONFIRM_vitals, Anticoagulation, METHYLPREDNISOLONE_EQUI_DOSE_DEXA, TOCILIZUMAB, STOOL, FEVER, FEED, I_O, RTA_DRAIN, Hemogram, Coagulogram, SE, RFT, ABG_VBG, RBS, Special_Ix, Date, IL_6, Ferritin, CRP, D_Dimer, LDH, CxR, APACHE_IV, HAS_BLED, GFR, SOFA_score, Other_Scores, INSTRUCTIONS = range(
    12, 53)
vitalsvalue, id, Patient_Name, Age_Sex, Day_of_Admission, Day_of_first_positive_symptoms, Diagnosis, Co_Morbidities, CTSS_scoring, Weight, Height = range(53, 64)
antibiotic_value_to_remove = 64
discharge_choosing_patient_id = 65
discharge_confirm = 66
antibiotic_state, remove_antibiotic_yes_no = range(67, 69)

reply_keyboard = [['Get', 'Update']]

editable_columns_list = ['GCS', 'Ventilation', 'SPO2', 'PR', 'BP', 'INOTROPE', 'ANALGESIA', 'SEDATION', 'ANTIBIOTIC(S)',
                         'Other drugs', 'INSULIN infusion', 'ULCER PROPHYLAXIS', 'REMDESIVIR', 'Anticoagulation',
                         'METHYLPREDNISOLONE EQUI DOSE DEXA (1.5:8)', 'TOCILIZUMAB', 'STOOL', 'FEVER', 'FEED', 'I/O',
                         'RTA/DRAIN', 'Hemogram', 'Coagulogram', 'SE', 'RFT', 'ABG/VBG', 'RBS', 'Special Ix', 'Date',
                         'IL 6', 'Ferritin', 'CRP', 'D Dimer', 'LDH', 'CxR', 'APACHE IV', 'HAS BLED', 'GFR',
                         'SOFA score', 'Other Scores', 'INSTRUCTIONS', ]
editable_columns_list_register = ['UHID', 'Patient Name', 'Age/Sex', 'Day of Admission', 'Day of first positive symptoms', 'Diagnosis',
                                  'Co-Morbidities', 'CTSS-scoring', 'Weight', 'Height']
editable_columns_list_vitalsmode = ['GCS (E/V/M)', 'PR /min', 'BP mm hg', 'SPO2 %']
editable_columns_list_ventilation = ['Flow (l/min)', 'FiO2/Support/PEEP', 'Calories/kg', 'Protein/kg', 'Stool passed']

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
    print(df_data)
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

def roundmode(update, context):
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
    context.user_data['conversation_type'] = 'roundmode'
    
    liste = []
    for uhid in df_data['UHID'].values.tolist():
        context.user_data['patient_id'] = uhid
        df_data_patient_id = df_data[df_data['UHID'] == uhid]
        df_data_last_row = df_data_patient_id.iloc[[-1]]
        
        
        if uhid not in liste:
        
            context.user_data['patient_id_row'] = df_data_last_row
            text = ''
            for column in df_data_last_row.columns.values[:-1]:
                text = text + '\n' + column + ': ' + str(df_data_last_row[column].values[0])
            update.message.reply_text(text)
            liste.append(uhid)
      
    update.message.reply_text(text='this is all information of all patients')
    patient_name(update, context)

    return choosing_patient_name

def vitalsmode(update, context):
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
    context.user_data['conversation_type'] = 'Vitalsmode'
    patient_name(update, context)

    return choosing_patient_name

def vitals(update, context):
    context.user_data['vitals_ventillation']='vitals'
    column_index_vitals = context.user_data['column_index_vitals']
    column = editable_columns_list_vitalsmode[column_index_vitals]
    if 0< column_index_vitals <4:
        context.user_data[editable_columns_list_vitalsmode[column_index_vitals - 1 ]] = update.message.text
    
    
    markup = ForceReply(True, False)
    update.message.reply_text(f'Enter {column} value', reply_markup=markup)
    context.user_data['column_index_vitals'] = column_index_vitals + 1

    if column_index_vitals == 3:
        return SPO2_vitals

    return GCS

def ventilation(update, context):
    
    button_labels = [['NRBM'], ['Room Air'], ['SFM'], ['Nasal Cannula'], ['Bipap'], ['HFNO'], ['Invasive Ventilation'], ['NIV']]
    markup = ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
    update.message.reply_text('Enter ventilation ', reply_markup=markup)
    return ventilation_value

def Ventilation_values(update, context):
    field = update.message.text
    context.user_data['field_ventilation'] = field
    L= ['NRBM', 'Room Air', 'SFM', 'Nasal Cannula']
    K= ['HFNO', 'Invasive Ventilation', 'NIV']
    if field in L :
        markup = ForceReply(True, False)
        update.message.reply_text(text='Enter Flow (l/min)',reply_markup=markup )

    elif field in K:
        markup = ForceReply(True, False)
        update.message.reply_text(text='Enter FiO2/Support/PEEP', reply_markup=markup)

    elif field == 'Bipap':
        markup = ForceReply(True, False)
        update.message.reply_text(text='Enter Flow (l/min)', reply_markup=markup)
        return bipap 

    return feed_value  

def flow_bipap(update, context):
    context.user_data['Flow (l/min)'] = update.message.text
    markup = ForceReply(True, False)
    update.message.reply_text(text='Enter FiO2/Support/PEEP', reply_markup=markup)

    return feed_value

def Feed_ventilation(update, context):
    field = context.user_data['field_ventilation']
    L= ['NRBM', 'Room Air', 'SFM', 'Nasal Cannula']
    K= ['HFNO', 'Invasive Ventilation', 'NIV']
    if field in L :
        context.user_data['FiO2/Support/PEEP']=''
        context.user_data['Flow (l/min)'] = update.message.text

    elif field in K:
        context.user_data['Flow (l/min)']=''
        context.user_data['FiO2/Support/PEEP'] = update.message.text

    elif field == 'Bipap':
        context.user_data['FiO2/Support/PEEP'] = update.message.text
    column_index_ventitaltion = 0             
    markup = ForceReply(True, False)
    update.message.reply_text(text='Enter Calories/kg value', reply_markup=markup)
    context.user_data['column_index_ventitaltion'] = column_index_ventitaltion

    return calories 

def Feed(update, context):
    context.user_data['vitals_ventillation']='ventillation'

    column_index_ventitaltion = context.user_data['column_index_ventitaltion']
    if column_index_ventitaltion == 0:
        context.user_data['Calories/kg'] = update.message.text
        markup = ForceReply(True, False)
        update.message.reply_text(text='Enter Protein/kg value', reply_markup=markup)
    if column_index_ventitaltion == 1:
        context.user_data['Protein/kg'] = update.message.text
        markup = ForceReply(True, False)
        update.message.reply_text(text='Enter Stool passed value', reply_markup=markup)

    context.user_data['column_index_ventitaltion'] =  column_index_ventitaltion + 1

    if context.user_data['column_index_ventitaltion'] == 2:
        return stool_passed  

    

    return next_value 


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
    if (context.user_data['conversation_type'] == 'roundmode' or context.user_data['conversation_type'] == 'Vitalsmode'):
        name = update.message.text
        context.user_data['patient_name'] = name
        dic = context.user_data['dict_uhid_name']
        uhid = list(dic.keys())[list(dic.values()).index(name)]
            
        df_data = context.user_data['datatable']
        df_data_patient_id = df_data[df_data['UHID'] == int(uhid)]
        df_data_last_row = df_data_patient_id.iloc[[-1]]
        context.user_data['patient_id_row'] = df_data_last_row
        
        if context.user_data['conversation_type'] == 'roundmode':
            old_value = df_data_last_row['advice_plan'].values[0]
            update.message.reply_text(f'Old advice_plan value: {old_value}')
            update.message.reply_text(text='Enter the new advice_plan ')
            return advice_plan
        else:
            column_index_vitals = 0
            context.user_data['column_index_vitals'] = column_index_vitals 
            markup = ForceReply(True, False)
            update.message.reply_text(text='Enter GCS (E/V/M) value', reply_markup= markup)
            context.user_data['column_index_vitals'] = column_index_vitals + 1

            return vitalsvalue

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
    
    if context.user_data['conversation_type'] == 'Vitalsmode':
        if context.user_data['vitals_ventillation']== 'vitals':
            column_index_vitals = context.user_data['column_index_vitals']
            context.user_data[editable_columns_list_vitalsmode[column_index_vitals - 1]] = update.message.text
            log_received_information(update, context)
            return CONFIRM_vitals
        else:
            print('Stool')
            context.user_data['Stool passed']=update.message.text 



    if context.user_data['conversation_type'] == 'roundmode':
        context.user_data['advice_plan'] = update.message.text

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

    elif context.user_data['conversation_type'] == 'Vitalsmode':
        if context.user_data['vitals_ventillation']== 'vitals':
            for column in editable_columns_list_vitalsmode:
                text = text + '\n' + column + ': ' + str(context.user_data[column])
            update.message.reply_text(text)
            button_labels = [['YES'], ['NO']]
            reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
            update.message.reply_text("Confirm please!", reply_markup=reply_keyboard)
            return CONFIRM_vitals 
        else:
            for column in editable_columns_list_ventilation:
                text = text + '\n' + column + ': ' + str(context.user_data[column])
            
    elif context.user_data['conversation_type'] == 'roundmode':
    
        name = context.user_data['patient_name']
        advice_plan = context.user_data['advice_plan']
        text = 'Patient Name' + ':' + name + '\n' + 'advice_plan' + ':' + advice_plan
        
            
           
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
    
    if context.user_data['conversation_type'] == 'Vitalsmode':
        if context.user_data['vitals_ventillation']== 'vitals':
            button_labels = [['GCS (E/V/M)'], ['PR /min'], ['BP mm hg'], ['SPO2 %']]
        else: 
            button_labels = [['Flow (l/min)'], ['FiO2/Support/PEEP'], ['Calories/kg'], ['Protein/kg'], ['Stool passed']]
    
    reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels)

    update.message.reply_text('Which field you need to edit ?', reply_markup=reply_keyboard)

    return wait_edit_choice


def get_column_to_edit(update, context):
    if context.user_data['conversation_type'] == 'roundmode':

        context.user_data['field_to_edit'] = 'advice_plan'
        advice_plan = context.user_data['advice_plan']
        markup = ForceReply(True, False)
        update.message.reply_text(f'Old advice_plan value: {advice_plan}'
                              f'\nEnter advice_plan new value', reply_markup=markup)
    else:
        
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
    if context.user_data['vitals_ventillation']== 'vitals':
        return CONFIRM_vitals

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
        'conversation_type'] == 'discharge' or context.user_data[
        'conversation_type'] == 'roundmode' or  context.user_data['conversation_type'] == 'Vitalsmode':
        
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

        elif context.user_data['conversation_type'] == 'roundmode':
            
            context.user_data['patient_id_row']['advice_plan'] = context.user_data['advice_plan']

            context.user_data['patient_id_row']['Save time'] = IST_now
            df_data = df_data.append(context.user_data['patient_id_row'])
            last_row_list = context.user_data['patient_id_row'].values[0].tolist()
            sheet.insert_row(last_row_list, len(df_data) + 1)

            update.message.reply_text("Record saved!")

        elif context.user_data['conversation_type'] == 'Vitalsmode':

            for column in editable_columns_list_vitalsmode:
                context.user_data['patient_id_row'][column] = context.user_data[column]

            for column in editable_columns_list_ventilation:
                context.user_data['patient_id_row'][column] = context.user_data[column]    

            context.user_data['patient_id_row']['Save time'] = IST_now
            df_data = df_data.append(context.user_data['patient_id_row'])
            last_row_list = context.user_data['patient_id_row'].values[0].tolist()
            sheet.insert_row(last_row_list, len(df_data) + 1)

            update.message.reply_text("Record saved!")

    update.message.reply_text("Until next time!""\nBye!")
    context.user_data.clear()

    return ConversationHandler.END

def patient_name(update, context):
    
        df_data = context.user_data['datatable']
        dic= {}
        for i in range(len(df_data)):

            uhid = df_data.at[i, 'UHID']
            name = df_data.at[i, 'Patient Name']
            dic[uhid]= name

        context.user_data['dict_uhid_name'] = dic
        list_name = []
        for name in dic.values():
            list_name.append(name)
            
        button_labels = []
        for el in list_name:
            sub = el.split(', ')
            button_labels.append(sub)

        reply_keyboard = telegram.ReplyKeyboardMarkup(button_labels, one_time_keyboard=True)
        update.message.reply_text("Select the patient considered", reply_markup=reply_keyboard)

        return choosing_patient_name   

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

    conv_handler4 = ConversationHandler(
        entry_points=[CommandHandler('roundmode', roundmode)],

        states={
            choosing_patient_name: [
                MessageHandler(Filters.text & ~Filters.command, update_patient_info)
            ],
            
            advice_plan: [
                MessageHandler(Filters.text & ~Filters.command, received_information)
            ],

            CONFIRM: [
                MessageHandler(Filters.regex('^YES$'), done),
                MessageHandler(Filters.regex('^NO$'), get_column_to_edit)
            ],

            edit_selected_choice: [
                MessageHandler(Filters.text & ~Filters.command, edit_choice)
            ]

        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_handler5 = ConversationHandler(
        entry_points=[CommandHandler('Vitalsmode', vitalsmode)],

        states={
            choosing_patient_name: [
                MessageHandler(Filters.text & ~Filters.command, update_patient_info)
            ],

            vitalsvalue: [
                MessageHandler(Filters.text & ~Filters.command, vitals)
            ],

            GCS: [
                MessageHandler(Filters.text & ~Filters.command, vitals)
            ],

            SPO2_vitals: [
                MessageHandler(Filters.text & ~Filters.command, received_information)
            ],

            CONFIRM_vitals: [
                MessageHandler(Filters.regex('^YES$'), ventilation),
                MessageHandler(Filters.regex('^NO$'), edit)
            ],

            ventilation_value: [
                MessageHandler(Filters.text & ~Filters.command, Ventilation_values)
            ],
 
            bipap: [
                MessageHandler(Filters.text & ~Filters.command, flow_bipap)
            ],
            
            feed_value: [
                MessageHandler(Filters.text & ~Filters.command, Feed_ventilation)
            ],

            calories: [
                MessageHandler(Filters.text & ~Filters.command, Feed)
            ],

            next_value: [
                MessageHandler(Filters.text & ~Filters.command, Feed)
            ],

            stool_passed: [
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

    dp.add_handler(conv_handler)
    dp.add_handler(conv_handler2)
    dp.add_handler(conv_handler3)
    dp.add_handler(conv_handler4)
    dp.add_handler(conv_handler5)
    dp.add_handler(MessageHandler(Filters.text, log_user_message), group=1)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
