# -*- coding: utf-8 -*-

import os
import threading
import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import telebot
from telebot import types

# ==============================================================================
# 1. CONFIGURATION & INITIALIZATION
# ==============================================================================

load_dotenv()
BOT_TOKEN = os.getenv("TOKEN") 
MONGODB_URL = os.getenv("MONGODB_URL") 

ADMIN_USER_ID = 843171085
LOG_CHANNEL_ID = -1002454482195

# --- Web Scraper Configuration ---
SCRAPE_URL = "https://studybullet.com/"
LAST_LINK_FILE = 'store.json'

# --- Initialize Bot and Database ---
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
try:
    client = MongoClient(MONGODB_URL)
    db = client.get_database('udemy')
    user_collection = db.user_data
    bot.send_message(ADMIN_USER_ID, "✅ Bot started and successfully connected to the database. v1")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    bot.send_message(ADMIN_USER_ID, f"❌ Bot failed to start. DB connection error: {e}")
    exit()

# ==============================================================================
# 2. COURSE CATEGORIES & KEYWORDS
# ==============================================================================

# A structured way to manage course categories and their keywords.
# This makes adding new categories or keywords much easier.
COURSE_CATEGORIES = {
    "Programming": ["Python", "Java", "C++", "JavaScript", "Ruby", "Swift", "PHP", "Rust", "MySQL", "Kotlin", "TypeScript", "Dart", "Haskell", "Lua", "Matlab", "SQL"],
    "Adobe": ["Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Adobe Premiere Pro", "Adobe After Effects", "Adobe Lightroom", "Adobe XD", "Adobe Dreamweaver", "Adobe Audition", "Adobe Animate"],
    "Digital Marketing": ["Digital Marketing", "Social Media Marketing", "Content Creation", "Search Engine Optimization", "Email Marketing"],
    "Cloud Computing": ["Cloud Computing", "AWS", "Azure", "Google Cloud"],
    "Front-end Frameworks": ["Frontend", "React", "Angular", "Vue.js", "Ember.js", "Svelte"],
    "Back-end Frameworks": ["Backend", "Express.js", "Django", "Flask", "Laravel", "ASP.NET"],
    "Game Development": ["Game Development", "Game", "Unity", "Unreal Engine"],
    "Data Science": ["Data Science", "Data analysis", "Machine learning", "Data visualization"],
    "Video Editing": ["Video Intro", "Videography", "Video Editor", "Adobe Premiere", "Adobe After Effect"],
    "Cyber security": ["Cybersecurity", "Hacking", "Network security"],
    # Simple categories without sub-menus
    "Graphic Design": [], "AI": [], "Web Development": [], "Wordpress": [], "Scripting": [], "Full stack": [], "Linux": [], "Docker": []
}

# ==============================================================================
# 3. DATABASE HELPER FUNCTIONS
# ==============================================================================

def get_or_create_user(user_id, first_name, username):
    """Finds a user in the DB or creates a new one if they don't exist."""
    user_data = {
        "_id": user_id,
        'first_name': first_name,
        'username': username,
        'words': [],
        'course_count': 0,
        'rated_the_bot': False,
        'joined_the_channel': False
    }
    # upsert=True creates the document if it doesn't exist
    user_collection.update_one({"_id": user_id}, {"$setOnInsert": user_data}, upsert=True)
    return user_collection.find_one({"_id": user_id})

def get_user_words(user_id):
    """Fetches the list of preferred words for a user."""
    user = user_collection.find_one({"_id": user_id})
    return user.get("words", []) if user else []

def update_user_words(user_id, word, add=True):
    """Adds or removes a word from a user's preferences."""
    operator = "$push" if add else "$pull"
    user_collection.update_one({"_id": user_id}, {operator: {"words": word}})

def clear_user_words(user_id):
    """Clears all words for a user."""
    user_collection.update_one({"_id": user_id}, {"$set": {"words": []}})

def bulk_increment_course_count(user_ids: list):
    """Increments the course_count for a list of users efficiently."""
    if not user_ids:
        return
    operations = [UpdateOne({"_id": user_id}, {"$inc": {"course_count": 1}}) for user_id in user_ids]
    user_collection.bulk_write(operations)
    print(f"Incremented course_count for {len(user_ids)} users.")

# ==============================================================================
# 4. KEYBOARD MARKUP & UI HELPERS
# ==============================================================================

def create_main_menu_markup(user_id):
    """Creates the main inline keyboard for selecting course categories."""
    user_words = get_user_words(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for category in COURSE_CATEGORIES:
        # If the category name itself is a selected word
        text = f"✅ {category}" if category in user_words else category
        # Use a prefix to distinguish callback types
        callback_data = f"category:{category}"
        buttons.append(types.InlineKeyboardButton(text, callback_data=callback_data))

    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("Done ✅", callback_data="action:done"))
    return markup

def create_sub_menu_markup(category, user_id):
    """Creates a sub-menu for a specific category."""
    user_words = get_user_words(user_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    keywords = COURSE_CATEGORIES.get(category, [])
    if not keywords: # Should not happen if called correctly
        return create_main_menu_markup(user_id)
        
    buttons = []
    for keyword in keywords:
        text = f"✅ {keyword}" if keyword in user_words else keyword
        callback_data = f"select:{keyword}|{category}" # Include parent for context
        buttons.append(types.InlineKeyboardButton(text, callback_data=callback_data))

    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("Back ↩️", callback_data="action:back_main"))
    return markup
    
def create_settings_markup():
    """Creates the settings menu keyboard."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Add/Remove Words", callback_data='action:add'),
        types.InlineKeyboardButton("Clear All Words", callback_data='action:clear'),
        types.InlineKeyboardButton("Developer Contact", url="https://t.me/huam3")
    )
    return markup

def create_rating_markup():
    """Creates the keyboard for the rating prompt."""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Join Channel", url="https://t.me/huam3_info"),
        types.InlineKeyboardButton("Rate 5 ⭐", url="https://t.me/BotsArchive/2874")
    )
    markup.add(types.InlineKeyboardButton("Check My Status ✅", callback_data="action:check_rating"))
    return markup

# ==============================================================================
# 5. BOT HANDLERS
# ==============================================================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handler for the /start command."""
    user = get_or_create_user(message.chat.id, message.chat.first_name, message.chat.username)
    
    # Check if the user needs to rate the bot to continue
    if user.get('course_count', 0) > 20 and not user.get('rated_the_bot', False):
        prompt_for_rating(message.chat.id)
        return
        
    welcome_message = (
        "👋 Hello! Welcome to the Udemy Course Bot! 🎉\n\n"
        "I find free Udemy courses based on your interests. "
        "Please select your preferences using the buttons below.\n\n"
        "Use /setting to change your preferences later."
    )
    bot.send_message(message.chat.id, welcome_message, reply_markup=create_main_menu_markup(message.chat.id))


@bot.message_handler(commands=['setting'])
def handle_setting(message):
    """Handler for the /setting command."""
    bot.send_message(message.chat.id, "You can add, remove, or clear your course preferences.", reply_markup=create_settings_markup())


@bot.message_handler(commands=['mywords'])
def handle_my_words(message):
    """Shows the user their currently selected words."""
    words = get_user_words(message.chat.id)
    if words:
        words_text = ", ".join(words)
        bot.send_message(message.chat.id, f"<b>Your selected keywords:</b>\n{words_text}")
    else:
        bot.send_message(message.chat.id, "You haven't selected any keywords yet. Use /start or /setting to add some.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    """Handler for user support questions."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Cancel"))
    bot.send_message(message.chat.id, 'Please type your question or comment. The admin will get back to you.', reply_markup=markup)
    bot.register_next_step_handler(message, handle_help_response)

def handle_help_response(message):
    """Forwards user's help message to the admin."""
    if message.text == 'Cancel':
        bot.send_message(message.chat.id, "Action canceled.", reply_markup=types.ReplyKeyboardRemove())
        return
        
    user_info = f"From: {message.from_user.first_name} (@{message.from_user.username}, ID: {message.chat.id})"
    admin_message = f"<b>New Help Request</b>\n\n{user_info}\n\n<b>Message:</b>\n{message.text}\n\nUse <code>/reply {message.chat.id} your_message</code> to respond."
    
    bot.send_message(ADMIN_USER_ID, admin_message)
    bot.send_message(message.chat.id, "Your message has been sent to the admin. Thank you!", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['reply'])
def handle_admin_reply(message):
    """Allows the admin to reply to a user directly via the bot."""
    if message.chat.id != ADMIN_USER_ID:
        return
    try:
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            bot.reply_to(message, "Invalid format. Use <code>/reply USER_ID message</code>")
            return
        
        target_id = int(parts[1])
        reply_text = parts[2]
        
        bot.send_message(target_id, "<b>Message from the Admin:</b>")
        bot.send_message(target_id, reply_text)
        bot.reply_to(message, f"Reply sent to {target_id}.")
    except Exception as e:
        bot.reply_to(message, f"Failed to send reply. Error: {e}")

# --- Callback Query Handlers ---

@bot.callback_query_handler(func=lambda call: call.data.startswith('action:'))
def handle_action_callbacks(call):
    """Handles general action callbacks like done, back, clear, etc."""
    action = call.data.split(':')[1]
    user_id = call.message.chat.id

    if action == 'done':
        user_words = get_user_words(user_id)
        if not user_words:
            bot.answer_callback_query(call.id, "You haven't selected any keywords!", show_alert=True)
            return
        
        bot.delete_message(user_id, call.message.message_id)
        msg = bot.send_message(user_id, "✅ Your preferences are saved!\nI will notify you when a matching course is available.\n\nUse /setting to modify your choices anytime.")
        try:
            bot.pin_chat_message(user_id, msg.message_id)
        except Exception as e:
            print(f"Could not pin message for {user_id}: {e}")

    elif action == 'add':
        bot.edit_message_text("Select your preferences:", user_id, call.message.message_id, reply_markup=create_main_menu_markup(user_id))
    
    elif action == 'back_main':
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=create_main_menu_markup(user_id))

    elif action == 'clear':
        yes_btn = types.InlineKeyboardButton("Yes, Clear Them", callback_data='action:clear_confirm')
        no_btn = types.InlineKeyboardButton("No, Cancel", callback_data='action:clear_cancel')
        markup = types.InlineKeyboardMarkup().add(yes_btn, no_btn)
        bot.edit_message_text("Are you sure you want to clear all your preferences?", user_id, call.message.message_id, reply_markup=markup)

    elif action == 'clear_confirm':
        clear_user_words(user_id)
        bot.answer_callback_query(call.id, "Your preferences have been cleared.")
        bot.delete_message(user_id, call.message.message_id)
        handle_start(call.message)

    elif action == 'clear_cancel':
        bot.answer_callback_query(call.id, "Canceled.")
        bot.delete_message(user_id, call.message.message_id)
        handle_start(call.message)

    elif action == 'check_rating':
        check_user_rating_status(user_id, call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('category:'))
def handle_category_callbacks(call):
    """Handles clicks on main category buttons."""
    category = call.data.split(':')[1]
    user_id = call.message.chat.id
    
    if not COURSE_CATEGORIES.get(category): # It's a simple category with no sub-menu
        user_words = get_user_words(user_id)
        is_selected = category in user_words
        update_user_words(user_id, category, add=not is_selected)
        bot.answer_callback_query(call.id, f"'{category}' removed." if is_selected else f"'{category}' added.")
        bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=create_main_menu_markup(user_id))
    else: # It's a category with a sub-menu
        bot.edit_message_text(f"Select keywords for <b>{category}</b>:", user_id, call.message.message_id, reply_markup=create_sub_menu_markup(category, user_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith('select:'))
def handle_keyword_selection_callbacks(call):
    """Handles clicks on keyword buttons in a sub-menu."""
    parts = call.data.split(':')[1].split('|')
    keyword, category = parts[0], parts[1]
    user_id = call.message.chat.id

    user_words = get_user_words(user_id)
    is_selected = keyword in user_words
    
    update_user_words(user_id, keyword, add=not is_selected)
    bot.answer_callback_query(call.id, f"'{keyword}' removed." if is_selected else f"'{keyword}' added.")
    bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=create_sub_menu_markup(category, user_id))


# ==============================================================================
# 6. RATING & VERIFICATION SYSTEM
# ==============================================================================

def prompt_for_rating(user_id):
    """Sends a message asking the user to rate the bot and join the channel."""
    message = (
        "To continue receiving unlimited free courses, please complete two simple steps:\n\n"
        "1️⃣ <a href='https://t.me/huam3_info'>Subscribe to our channel</a>\n"
        "2️⃣ <a href='https://t.me/BotsArchive/2874'>Rate the bot 5 stars</a>\n\n"
        "After completing them, click the 'Check My Status' button below."
    )
    try:
        bot.send_message(user_id, message, disable_web_page_preview=True, reply_markup=create_rating_markup())
    except Exception as e:
        print(f"Failed to send rating prompt to {user_id}: {e}")

def check_user_rating_status(user_id, callback_id=None):
    """Verifies if the user has rated the bot and joined the channel."""
    try:
        # Step 1: Check rating via API
        api_url = f"https://api.botsarchive.com/getUserVote.php?bot_id=4183&user_id={user_id}"
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("vote") or data.get("result") not in ['5']:
            bot.answer_callback_query(callback_id, "You need to rate the bot 5 stars to proceed.", show_alert=True)
            return

        # Step 2: Check channel membership
        member_status = bot.get_chat_member(LOG_CHANNEL_ID, user_id).status
        if member_status not in ['member', 'administrator', 'creator']:
            bot.answer_callback_query(callback_id, "You need to join our channel to proceed.", show_alert=True)
            return
            
        # Step 3: Update user status in DB if both checks pass
        user_collection.update_one({"_id": user_id}, {"$set": {"rated_the_bot": True, "joined_the_channel": True}})
        bot.send_message(user_id, "✅ Thank you! You have been verified and will continue to receive courses.")
        if callback_id:
            bot.answer_callback_query(callback_id, "Verification successful!")
        
        # Log the successful verification
        user = user_collection.find_one({"_id": user_id})
        log_message = (
            f"✅ <b>User Verified</b>\n"
            f"User: <a href='tg://user?id={user_id}'>{user.get('first_name')}</a>\n"
            f"ID: <code>{user_id}</code>\n"
            f"Username: @{user.get('username')}\n"
            f"Courses Received: {user.get('course_count', 0)}"
        )
        bot.send_message(LOG_CHANNEL_ID, log_message)

    except requests.RequestException as e:
        bot.send_message(ADMIN_USER_ID, f"Rating API request failed: {e}")
        bot.answer_callback_query(callback_id, "Could not verify at this moment. Please try again later.", show_alert=True)
    except Exception as e:
        print(f"Error in check_user_rating_status for {user_id}: {e}")
        bot.answer_callback_query(callback_id, "An error occurred. Please try again.", show_alert=True)


# ==============================================================================
# 7. WEB SCRAPING LOGIC
# ==============================================================================

def get_last_scraped_link():
    """Reads the last successfully scraped link from a file."""
    try:
        with open(LAST_LINK_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_last_scraped_link(link):
    """Saves the last scraped link to a file."""
    with open(LAST_LINK_FILE, 'w') as f:
        json.dump(link, f, indent=2)

def fetch_course_list():
    """Fetches the main page and returns a list of new course links."""
    print("Fetching main course page...")
    try:
        response = requests.get(SCRAPE_URL, timeout=15)
        response.raise_for_status()
        soup = bs(response.content, 'lxml')
        
        course_divs = soup.find_all('div', class_='blog-entry-inner clr')
        current_last_link = get_last_scraped_link()
        new_links = []
        
        for div in course_divs:
            link_tag = div.find('a', href=True)
            if link_tag:
                href = link_tag['href']
                if href == current_last_link:
                    break  # Stop when we reach the last processed link
                new_links.append(href)
        
        # Newest courses are at the top, so we reverse to process oldest-new first
        return new_links[::-1]
    except requests.RequestException as e:
        print(f"Error fetching course list: {e}")
        return []

def parse_course_details(url):
    """Scrapes details (title, image, description, enroll link) from a course page."""
    print(f"Parsing details for: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = bs(response.content, 'lxml')

        title = soup.find('h1', class_='page-header-title clr').text.strip()
        content_div = soup.find('div', class_='entry-content clr')
        description = content_div.find('p').text.strip()
        image_link = content_div.find('img')['src']
        enroll_link = soup.find('a', class_='enroll_btn')['href']
        
        return {
            'study_link': url,
            'title': title,
            'imglink': image_link,
            'disc': description,
            'link': enroll_link
        }
    except (requests.RequestException, AttributeError, TypeError) as e:
        print(f"Error parsing course details for {url}: {e}")
        return None
def notify_interested_users(course_details):
    """
    Finds users interested in the course and sends them the details.
    If a user has received many courses but hasn't rated/joined, it sends a 'locked' version of the course.
    """
    import re
    title = course_details['title']
    print(f"Finding users for course: {title}")

    # Find users whose 'words' array has at least one element that matches a word in the title
    # Split title into words
    title_words = set(word.lower() for word in title.split())

    # Build regex queries for each word
    regex_conditions = [
        {"words": {"$regex": f"^{re.escape(word)}$", "$options": "i"}}
        for word in title_words
    ]

    # Query: users whose words match any of the title words (case-insensitive)
    interested_users_cursor = user_collection.find({
        "$or": regex_conditions
    })

    
    interested_users = list(interested_users_cursor)
    
    if not interested_users:
        print("No interested users found.")
        return

    print(f"Found {len(interested_users)} potentially interested users.")
    bot.send_message(LOG_CHANNEL_ID, f"📢 Course: {title}\nFound {len(interested_users)} interested users.")

    users_receiving_notification = []

    for user in interested_users:
        user_id = user["_id"]
        # Double-check for false positives from the database query
        user_words = set(w.lower() for w in user.get("words", []))
        if not title_words.intersection(user_words):
            continue
        
        users_receiving_notification.append(user_id)
        
        # Determine if the course link should be locked for this user
        is_locked_for_user = user.get('course_count', 0) > 20 and not user.get('rated_the_bot', False)
        
        # Send the course notification, passing the locked status
        send_course_to_user(user_id, course_details, is_locked=is_locked_for_user)
        time.sleep(0.05) # Rate limit: 20 messages per second
    
    # Update the course count for everyone who was notified
    bulk_increment_course_count(users_receiving_notification)


def send_course_to_user(user_id, details, is_locked=False):
    """
    Formats and sends a single course message to a user.
    Displays a locked or unlocked version based on the 'is_locked' flag.
    """
    caption = (
        f"<b>{details['title']}</b>\n"
        f"▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔\n"
        f"{details['disc']}\n\n"
        f"⏳ <i>Free for the first 500-1000 enrollments only!</i>"
    )
    
    markup = types.InlineKeyboardMarkup()

    if is_locked:
        # Append lock message and create the verification keyboard
        caption += (
            "\n\n"
            "🔒 <b>Link Locked:</b> To get the enrollment link for this course, please complete two quick steps below and then click 'Check My Status'."
        )
        markup.add(
            types.InlineKeyboardButton("1️⃣ Join Channel", url="https://t.me/huam3_info"),
            types.InlineKeyboardButton("2️⃣ Rate 5 ⭐", url="https://t.me/BotsArchive/2874")
        )
        markup.add(types.InlineKeyboardButton("✅ Check My Status", callback_data="action:check_rating"))
    else:
        # Create the standard enroll button
        markup.add(types.InlineKeyboardButton("🎁 Enroll for FREE 🧭", url=details['link']))
    
    try:
        bot.send_photo(user_id, details['imglink'], caption=caption, reply_markup=markup)
    except telebot.apihelper.ApiTelegramException as e:
        if "bot was blocked by the user" in e.description:
            print(f"User {user_id} blocked the bot. Consider removing them from DB.")
            # user_collection.delete_one({"_id": user_id})
        else:
            print(f"Failed to send course to {user_id}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred sending to {user_id}: {e}")

def run_web_scraper():
    """The main loop for the web scraping process."""
    while True:
        try:
            bot.send_message(ADMIN_USER_ID, "-" * 30)
            bot.send_message(ADMIN_USER_ID, "scrapping started...")
            new_course_links = fetch_course_list()
            
            if not new_course_links:
                bot.send_message(ADMIN_USER_ID, "No new courses found. Waiting 60 seconds.")
                time.sleep(60)
                continue

            print(f"Found {len(new_course_links)} new courses. Processing...")
            bot.send_message(LOG_CHANNEL_ID, f" scraper found {len(new_course_links)} new courses.")

            for link in new_course_links:
                course_details = parse_course_details(link)
                if course_details:
                    notify_interested_users(course_details)
                    save_last_scraped_link(link) # Save after successful processing
                time.sleep(5) # Be respectful to the server

            bot.send_message(ADMIN_USER_ID, "Finished processing new courses batch. sleeping 30s")
            time.sleep(30) # Wait before next check

        except Exception as e:
            error_message = f"An error occurred in the main scraper loop: {e}"
            print(error_message)
            bot.send_message(ADMIN_USER_ID, f" scraper Error: {error_message}")
            time.sleep(60) # Wait longer after an error

# ==============================================================================
# 8. MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    bot.send_message(ADMIN_USER_ID, "Starting scraper thread...")
    scraper_thread = threading.Thread(target=run_web_scraper, daemon=True)
    scraper_thread.start()

    print("Bot is now polling for messages...")
    try:
        bot.infinity_polling(timeout=20, long_polling_timeout=30)
    except Exception as e:
        print(f"Bot polling failed: {e}")
        bot.send_message(ADMIN_USER_ID, f" CRITICAL: Bot polling has stopped! Error: {e}")
