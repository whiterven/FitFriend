import telebot
from telebot import types
from openai import OpenAI
import sqlite3
import random

API_TOKEN = 'YOUR_TELEGRAM_API_TOKEN'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'

bot = telebot.TeleBot(API_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

conn = sqlite3.connect('fitfriend.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY,
    goal TEXT,
    fitness_level TEXT,
    age INTEGER,
    gender TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS user_progress (
    user_id INTEGER,
    progress TEXT,
    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
)
''')

conn.commit()
conn.close()


# Inline keyboards
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Set Profile", callback_data="set_profile"),
        types.InlineKeyboardButton("Start Workout", callback_data="start_workout"),
        types.InlineKeyboardButton("Track Progress", callback_data="track_progress"),
        types.InlineKeyboardButton("Get Motivation", callback_data="get_motivation")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Welcome to FitFriend! Choose an option:", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "set_profile":
        bot.send_message(call.message.chat.id, "Let's set up your profile.")
        ask_fitness_goal(call.message)
    elif call.data == "start_workout":
        ask_workout_frequency(call.message)
    elif call.data == "track_progress":
        track_progress(call.message)
    elif call.data == "get_motivation":
        get_motivation(call.message)

# Step-by-step user profiling
def ask_fitness_goal(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Weight Loss', 'Muscle Gain', 'Endurance')
    msg = bot.send_message(message.chat.id, "What's your fitness goal?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_goal_step)

def process_goal_step(message):
    chat_id = message.chat.id
    goal = message.text
    conn = sqlite3.connect('fitfriend.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_profiles (user_id, goal) VALUES (?, ?)", (chat_id, goal))
    conn.commit()
    conn.close()
    ask_fitness_level(message)

def ask_fitness_level(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Beginner', 'Intermediate', 'Advanced')
    msg = bot.send_message(message.chat.id, "What's your current fitness level?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_fitness_level_step)

def process_fitness_level_step(message):
    chat_id = message.chat.id
    fitness_level = message.text
    conn = sqlite3.connect('fitfriend.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE user_profiles SET fitness_level = ? WHERE user_id = ?", (fitness_level, chat_id))
    conn.commit()
    conn.close()
    ask_age(message)

def ask_age(message):
    msg = bot.send_message(message.chat.id, "What's your age?")
    bot.register_next_step_handler(msg, process_age_step)

def process_age_step(message):
    chat_id = message.chat.id
    age = message.text
    conn = sqlite3.connect('fitfriend.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE user_profiles SET age = ? WHERE user_id = ?", (age, chat_id))
    conn.commit()
    conn.close()
    ask_gender(message)

def ask_gender(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Male', 'Female', 'Other')
    msg = bot.send_message(message.chat.id, "What's your gender?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_gender_step)

def process_gender_step(message):
    chat_id = message.chat.id
    gender = message.text
    conn = sqlite3.connect('fitfriend.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE user_profiles SET gender = ? WHERE user_id = ?", (gender, chat_id))
    conn.commit()
    conn.close()
    bot.send_message(chat_id, "Profile setup complete! You can now start your workout.", reply_markup=main_menu())

# Workout plan generation
def ask_workout_frequency(message):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        types.InlineKeyboardButton("Daily", callback_data="workout_daily"),
        types.InlineKeyboardButton("Weekly", callback_data="workout_weekly"),
        types.InlineKeyboardButton("Monthly", callback_data="workout_monthly")
    )
    bot.send_message(message.chat.id, "How often would you like to work out?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('workout_'))
def process_workout_frequency(call):
    frequency = call.data.split('_')[1]
    chat_id = call.message.chat.id
    conn = sqlite3.connect('fitfriend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (chat_id,))
    user_profile = cursor.fetchone()
    conn.close()

    if user_profile:
        workout = generate_workout(user_profile, frequency)
        workout_msg = "\n".join(workout)
        bot.send_message(chat_id, f"Here is your {frequency} workout plan:\n{workout_msg}")
        generate_workout_images(workout, call.message)
    else:
        bot.send_message(chat_id, "Please set up your profile first by using /start and then selecting 'Set Profile'.")

def generate_workout(user_profile, frequency):
    fitness_level = user_profile[2].lower()
    exercises = {
        'beginner': ['Push-ups', 'Squats', 'Lunges', 'Plank'],
        'intermediate': ['Pull-ups', 'Deadlifts', 'Bench Press', 'Rows'],
        'advanced': ['Clean and Jerk', 'Snatch', 'Handstand Push-ups', 'Muscle-ups']
    }
    return exercises.get(fitness_level, exercises['beginner'])

def generate_workout_images(workout, message):
    for exercise in workout:
        prompt = f"Illustration of a person doing {exercise}"
        response = openai_client.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        bot.send_photo(message.chat.id, image_url, caption=exercise)

# Progress tracking
def track_progress(message):
    chat_id = message.chat.id
    conn = sqlite3.connect('fitfriend.db')
    cursor = conn.cursor()
    cursor.execute("SELECT progress FROM user_progress WHERE user_id = ?", (chat_id,))
    user_progress = cursor.fetchone()
    conn.close()

    if user_progress:
        bot.send_message(chat_id, f"Your progress: {user_progress[0]}")
    else:
        bot.send_message(chat_id, "No progress recorded yet. Start your workout first.")

# Motivation
def get_motivation(message):
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a motivational fitness coach."},
            {"role": "user", "content": "Give me a motivational quote for fitness."}
        ]
    )
    motivation = completion.choices[0].message['content']
    bot.send_message(message.chat.id, motivation)

# Running the bot
bot.polling()
