from cgitb import text
from distutils import errors
from distutils.command.upload import upload
from http import client
from turtle import update
from unicodedata import name
from telegram import (
    Chat,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, Update,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler, CallbackContext,
    ConversationHandler, MessageHandler,
    filters, Updater, CallbackQueryHandler
)
from config import (
    api_key, sener_email,
    api_secret,
    FAUNA_KEY
)
import cloudinary
from cloudinary.uploader import upload
from faunadb import query as q
from faunadb.client import FaunaClient
from faunadb.errors import NotFound

# configure cloudinary
cloudinary.config(
    cloud_name="curiospaul",
    api_key=api_key,
    api_secret=api_secret
)

# fauna client config
client = FaunaClient(secret=FAUNA_KEY)

# Define options
CHOOSING, CLASS_STATE, SME_DETAILS, CHOOSE_PREF, \
    SME_CAT, ADD_PRODUCTS, SHOW_STOCKS, POST_VIEV_PRODUCTS = range(8)

def start(update,context: CallbackContext) -> int:
    print("You called")
    bot = context.bot
    chat_id = update.message.chat.id
    bot.send_message(
        chat_id=chat_id,
        text= "Привіт мій друже.Вітаю я Pelmennobot ,"
    )
        
    
    return CHOOSING

# get data generic user data from user and store
def choose (update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    # create new data entry
    data = update.message.text.split(',')
    if len(data) < 3 or len(data) > 3:
        bot.send_message(
            chat_id=chat_id,
            text="Недійсний запис.Будь ласка,переконайтесь,що ви ввели записи"
            "Як потрібно в інструкції"
        )
        bot.send_message(
            chat_id=chat_id,
            text="Введіть /start,щоб перезапустити бота"
        )
        return ConversationHandler.END
    #TODO: Check if user already exists before creating new user
    new_user = client.query(
        q.create(q.collection('User'),{
            "data":{
                "name":data[0],
                "email":data[1],
                "telephone":data[2],
                "is_smeowner":False,
                "preference": "",
                "chat_id":chat_id
            }
        }
        )
    )
    context.user_data["user-id"] = new_user ["ref"].id()
    context.user_data["user-name"] = data [0]
    context.user_data['user-data'] = new_user['data']
    reply_keyboard = [
        [
            InlineKeyboardButton(
                text="SME",
                callback_data="SME"
            ),
            InlineKeyboardButton(
                text="Customer",
                callback_data="Customer"
            )
        ]
    ]
    markup = InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    bot.send_message(
        chat_id=chat_id,
        text="Інформація збережена успішно! \n",
        reply_markup=markup
    )
    return CLASS_STATE

def classer(upgrade, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    name = context.user_data ["user-name"]
    if update.callback_query.data.lower() == "sme":
         # update user as smeowner
         client.query(
            q.update(
                q.ref(q.collection("User"), context.user_data["user-id"]),
                {"data": {"is_smeowner":True}}
            )
         )
         bot.send_message(
            chat_id=chat_id,
            text=f"Чудово! {name}, будь-ласка розкажи про свій бізнес",
            reply_markup=ReplyKeyboardRemove()
         )
         return SME_DETAILS
    categories = [
        [
            InlineKeyboardButton(
                text="Їжа/Кава",
                callback_data="Їжа/Кава"
            ),
            InlineKeyboardButton(
                text="Комплексні обіди/Десерти",
                callback_data="Комплексні обіди/Десерти"
            ),
            InlineKeyboardButton(
                text="Морозиво",
                callback_data="Морозиво"
            )
        ]
    ]
    bot.send_message(
        chat_id=chat_id,
        text="Тут список меню"
        "Виберіть,що вас інтересує",
        reply_markup=InlineKeyboardMarkup(categories)
    )
    return CHOOSE_PREF

# Control
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply.text (
        'До побачення! Я надіюсь ми ще зможем поспілкуватися.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END