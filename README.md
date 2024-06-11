# FitFriend
Fitness Telegram bot 


FitFriend Telegram BotFitFriend is a Telegram bot that acts as a personal fitness coach. It provides personalized workout plans, tracks progress, and offers motivation and support to users. The bot uses the latest OpenAI models (GPT-3.5 Turbo and DALL-E 3) for generating workout instructions and images.FeaturesUser Profiling: Collects user information (fitness goals, current fitness level, age, gender) to create personalized profiles.Workout Planning: Generates customized workout plans based on user profiles and selected workout frequency (daily, weekly, monthly).Progress Tracking: Tracks user progress and provides feedback.Motivation: Offers motivational quotes and advice to keep users engaged.Image Generation: Uses DALL-E 3 to generate images illustrating workout exercises.PrerequisitesPython 3.6+A Telegram bot token from BotFatherOpenAI API keyInstallationClone the repository:git clone https://github.com/yourusername/fitfriend-bot.git
cd fitfriend-bot
Install the dependencies:pip install -r requirements.txt
Set up the database:import sqlite3

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
Update the script with your API keys:Replace YOUR_TELEGRAM_API_TOKEN with your Telegram bot token.Replace YOUR_OPENAI_API_KEY with your OpenAI API key.Run the bot:python bot.py
UsageStart the bot: Use the /start command in your Telegram bot to initialize the interaction.Set Profile: Follow the prompts to provide your fitness goal, current fitness level, age, and gender.Start Workout: Choose your workout frequency (daily, weekly, monthly) to receive a personalized workout plan.Track Progress: Check your progress anytime using the "Track Progress" option.Get Motivation: Get motivational quotes and advice to keep you going.Filesbot.py: Main script for the FitFriend bot.requirements.txt: List of dependencies.README.md: This README file.ContributingFeel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.LicenseThis project is licensed under
