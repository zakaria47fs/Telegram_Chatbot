from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import os

# States
FIRST, SECOND = range(2)

# Callback data
ONE, TWO, THREE, FOUR, FIVE = range(5)

# function that is called to start the conversation
def start(update, context):
    fname = update.message.from_user.first_name

    # Build InlineKeyboard
    keyboard1 = [InlineKeyboardButton("< 100K samples", callback_data=str(ONE))]
    keyboard2 = [InlineKeyboardButton("> 100K samples", callback_data=str(TWO))]

    # create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])

    # send message with text and appended inline keyboarde
    update.message.reply_text(
        "Welcome {}. Let's figure out the best possible classifer for your data\n\nHow many samples do you have?".format(fname),
        reply_markup=reply_markup
    )
    # tell ConversationHandler that we're in state 'FIRST' now
    return FIRST


# the function is similar to the previous function without the greetings message
def start_over(update, context):
    # Get callback query from update
    query = update.callback_query

    # answering callback query
    query.answer()
    # Build InlineKeyboard
    keyboard1 = [InlineKeyboardButton("< 100K samples", callback_data=str(ONE))]
    keyboard2 = [InlineKeyboardButton("> 100K samples", callback_data=str(TWO))]
    # create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])

    # send message with text and appended inline keyboarde
    query.edit_message_text(
        "How many samples do you have?",
        reply_markup=reply_markup
    )
    # tell ConversationHandler that we're in state 'FIRST' now
    return FIRST


# linear_svc
def linear_svc(update, context):
    """show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # build inline keyboard
    keyboard1 = [InlineKeyboardButton("Let me try it out", callback_data=str(TWO))]
    keyboard2 = [InlineKeyboardButton("It's not working", callback_data=str(THREE))]
    #create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])
    query.edit_message_text(
        "I think you should try Linear SVC",
        reply_markup=reply_markup
    )
    return SECOND


# yes or no
def yes_no(update, context):
    """show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # build inline keyboard
    keyboard1 = [InlineKeyboardButton("Yes", callback_data=str(THREE))]
    keyboard2 = [InlineKeyboardButton("No", callback_data=str(FOUR))]
    #create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])
    query.edit_message_text(
        "Are you working with text data?",
        reply_markup=reply_markup
    )
    return FIRST


# naive bayes
def naive_bayes(update, context):
    """show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # build inline keyboard
    keyboard1 = [InlineKeyboardButton("Let me try it out", callback_data=str(TWO))]
    keyboard2 = [InlineKeyboardButton("Let's begin again", callback_data=str(ONE))]
    #create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])
    query.edit_message_text(
        "Naive Bayes is the best for text data",
        reply_markup=reply_markup
    )
    return SECOND


# k neighbours classifier
def k_neighbours(update, context):
    """show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # build inline keyboard
    keyboard1 = [InlineKeyboardButton("Let me try it out", callback_data=str(ONE))]
    keyboard2 = [InlineKeyboardButton("It's not working", callback_data=str(FIVE))]
    #create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])
    query.edit_message_text(
        "K Neighbours classifier please",
        reply_markup=reply_markup
    )
    return SECOND


# svc
def svc(update, context):
    """show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # build inline keyboard
    keyboard1 = [InlineKeyboardButton("Let me try it out", callback_data=str(TWO))]
    keyboard2 = [InlineKeyboardButton("Let's begin again", callback_data=str(ONE))]
    #create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])
    query.edit_message_text(
        "I think you should try out SVC",
        reply_markup=reply_markup
    )
    return SECOND


# SGD classifier
def sgd(update, context):
    """show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # build inline keyboard
    keyboard1 = [InlineKeyboardButton("Let me try it out", callback_data=str(TWO))]
    keyboard2 = [InlineKeyboardButton("It's not working", callback_data=str(FOUR))]
    #create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])
    query.edit_message_text(
        "I think you should try the SGD Classifier",
        reply_markup=reply_markup
    )
    return SECOND

# kernel approximation
def kernel_approx(update, context):
    """show new choice of buttons"""
    query = update.callback_query
    query.answer()
    # build inline keyboard
    keyboard1 = [InlineKeyboardButton("Let me try it out", callback_data=str(TWO))]
    keyboard2 = [InlineKeyboardButton("Let's begin again", callback_data=str(ONE))]
    #create reply markup
    reply_markup = InlineKeyboardMarkup([keyboard1, keyboard2])
    query.edit_message_text(
        "Please try out Kernel Approximation",
        reply_markup=reply_markup
    )
    return SECOND


# function to end the conversation
def end(update, context):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Goodbye, and all the best\n\nIf you need my help again click on /start"
    )
    return ConversationHandler.END


def main():
    # setting to appropriate values
    TOKEN = "1372061263:AAEcokfTYO9LnvdM_njDzl3XNHSCqtr9h2E"

    # set up updater
    updater = Updater(token=TOKEN, use_context=True)
    # set up dispatcher
    dispatcher = updater.dispatcher
    # a print message to log successful initiation of the bot
    # this is for self
    print("Bot started")

    # Setup conversation handler with states FIRST and SECOND
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command='start', callback=start)],
        states={
            FIRST: [CallbackQueryHandler(linear_svc, pattern='^' + str(ONE) + '$'),
                    CallbackQueryHandler(sgd, pattern='^' + str(TWO) + '$'),
                    CallbackQueryHandler(naive_bayes, pattern='^' + str(THREE) + '$'),
                    CallbackQueryHandler(k_neighbours, pattern='^' + str(FOUR) + '$')],
            SECOND: [CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
                     CallbackQueryHandler(end, pattern='^' + str(TWO) + '$'),
                     CallbackQueryHandler(yes_no, pattern='^' + str(THREE) + '$'),
                     CallbackQueryHandler(kernel_approx, pattern='^' + str(FOUR) + '$'),
                     CallbackQueryHandler(svc, pattern='^' + str(FIVE) + '$'),]
        },
        fallbacks=[CommandHandler(command='start', callback=start)]
    )
    
    
    # add command handler to dispatcher
    dispatcher.add_handler(conv_handler)

    # start the bot
    updater.start_polling()

    # run the bot until pressed ctrl+c
    updater.idle()


if __name__ == "__main__":
    main()