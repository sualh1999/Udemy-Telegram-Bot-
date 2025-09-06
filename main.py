import os,threading
import requests,json,time,random
import telebot
from datetime import datetime
from telebot import types
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient, UpdateOne
import logging, os
from dotenv import load_dotenv



load_dotenv()
TOKEN = os.getenv("TOKEN") 
MONGODB_URL = os.getenv("MONGODB_URL") 



bot= telebot.TeleBot(TOKEN)
bot.send_message(843171085, "Bot Starting...")
# db_password = os.environ['db_password']
# db_user = os.environ['db_user']
client= MongoClient(MONGODB_URL)
db= client.get_database('udemy')
db_data=db.user_data
tcours=2300
LOG_CHA_ID = -1002454482195

bot.send_message(843171085,"Connected to db")
                 
def test_foo():
  print("Starting...")
  users = db_data.find({})
  t = db_data.count_documents({})
  c = 0
  start = 4000
  for user in users:
    user_id = user["_id"]
    c+=1
    if c < start:
      continue
    print(f"Status: {c}/{t}, user_id: {user_id}")
    # try:
    bot.forward_message(user_id, "@huam3_info", 495)
    time.sleep(0.05)
      
    # except Exception as e:
    #    print(e, "\n\n\n")
  print("Finished... ")
# test_foo() 
# bot.forward_message(843171085, "@huam3_info", 495)
# raise "HI"


# @bot.message_handler(commands=['ss'])
# def in_link(message):
#   n=0
#   for i in range(300):
#     try:
#       time.sleep(2)
#       link= bot.create_chat_invite_link(chat_id='@salihmmy',member_limit=3)
#       bot.send_message(message.chat.id,link.invite_link)
#       n+=1
#       print("done",n)
#     except:
#       print("error")
@bot.message_handler(commands=['s1s21'])
def status_db(message):
  
  users = db_data.find({})
  count=0
  for user in users:
    count+=1
  bot.send_message(message.chat.id,f"Total users: {count}")
    
def auto_status(update=True):
  print("auto status in\n")
  users = db_data.find({})
  tuser=0
  auser=0
  if update:
    num = random.randint(1,13)
    if num == 1:

      for user in users:
        try:
          bot.send_chat_action(user['_id'],'typing')
          auser+=1
        except:
          pass
        tuser+=1
    else:
    #   print("didn't check",num)
      us= db_data.find_one({"_id":1111})
      tuser = int(us['tuser']) + 1
      auser = int(us['auser']) + 1
      

    
    db_data.update_one({"_id":1111},{"$set":{"tuser":tuser,"auser":auser}})
  ttt = db_data.find_one({"_id":1111})
  now = datetime.now()
  f_time = now.strftime("%d/%m/%y-%I:%M %p")

  mess= f"Udemy bot 🇪🇹 live statistics\n-----------------------------------\nTotal users: {ttt['tuser']} \nActive users: {ttt['auser']} \nTotal posted courses: {ttt['tcours']}+\nLast Update: {f_time}"
  try:
    bot.edit_message_text(chat_id="@huam3_info",message_id=487,text=mess)
  except:
    pass
  print("auto status out")

def check_words(chat_id):
  user = db_data.find_one({"_id":chat_id})
  words= user["words"]
  return words
all_buttons = ["Programming``", "Adobe``", "Digital Marketing``", "Cloud Computing``", "Front-end Frameworks``", "Back-end Frameworks``", "Game Development``", "Data Science``", "Cyber security", "Video Editing", "Graphic Design","AI", "Web Development", "Wordpress", "Scripting", "Full stack", "Linux","Docker"]
programming_languages = [
    "Python", "Java", "C++", "JavaScript", "Ruby",
    "Swift", "php", "Rust", "MySQL", "Kotlin",
    "TypeScript", "Dart", "Haskell", "Lua",
    "Matlab", "sql"
]
adobe_buttons= ["Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Adobe Premiere Pro", "Adobe After Effects", "Adobe Lightroom", "Adobe XD", "Adobe Dreamweaver", "Adobe Audition", "Adobe Animate"]
graphic_buttons= ["Graphic Design", "Adobe Illustrator", "Logo Design"]
digital_marketing_buttons= ["Digital Marketing", "Social Media Marketing", "Content Creation", "Search Engine Optimization", "Email Marketing"]
cloud_computing_buttons= ["Cloud Computing", "AWS", "Azure", "Google Cloud"]
frontend_buttons= ["Frontend", "React", "Angular", "Vue.js","Ember.js","Svelte"]
backend_buttons= ["Backend","Express.js","Django","Flask","Laravel","ASP.NET"]
game_development_buttons= ["Game Development", "Game", "Unity", "Unreal Engine"]
data_science_buttons= ["Data Science", "Data analysis", "Machine learning", "Data visualization"]
video_editing= [ "Video Intro" ,"Videography", "Video Editor", "Adobe Premiere", "Adobe After Effect"]
cybersecurity= ["Cybersecurity", "Hacking", "Network security"]

def main_buttons(chat_id):
    user_languages= check_words(chat_id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    # Define inline keyboard buttons for each programming language
    btns=[]
    for button in all_buttons:
      btn = types.InlineKeyboardButton(text=f"✅ {button}" if button in user_languages else button, callback_data=button)
      btns.append(btn)
    back_main = types.InlineKeyboardButton(text="Done", callback_data='done')
    
    
    markup.add(*btns)
    markup.add(back_main)
    #bot.send_message(chat_id,'Programming languages:',reply_markup=markup)
    return markup
  
def sub_buttons(call_data,chat_id):
    user_languages= check_words(chat_id)
    print(call_data)
    clicked_button= check_clicked_button(call_data)
    markup = types.InlineKeyboardMarkup(row_width=2)
    all_lang = types.InlineKeyboardButton(text=f"✅ UnSelect All" if 'all~'+str(call_data) in user_languages else "Select All", callback_data='all~'+str(call_data))
    markup.add(all_lang)
    # Define inline keyboard buttons for each programming language
    btns=[]
    for button in clicked_button:
      btn = types.InlineKeyboardButton(text=f"✅ {button}" if button in user_languages else button, callback_data=button+'|'+str(call_data))
      btns.append(btn)
    back_main = types.InlineKeyboardButton(text="Back↩️", callback_data='back_main')
    
    
    markup.add(*btns)
    markup.add(back_main)
    #bot.send_message(chat_id,'Programming languages:',reply_markup=markup)
    return markup
@bot.callback_query_handler(func=lambda call: call.data in all_buttons and call.data[-1] == "`")
def callback_main_menu_buttons(call):
    
    user_id = call.from_user.id
    lang = call.data
    
  
    
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=sub_buttons(call.data,call.message.chat.id))
    
    #bot.delete_message(call.message.chat.id,call.message.message_id)
    #bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text=call.data, reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def other_callbacks(call):
  user_languages= check_words(call.message.chat.id)
  global user_language
  if call.data == "rated":
     check_rate(call.message.chat.id)
     return
  if call.data == "clear":
    bot.delete_message(call.message.chat.id,call.message.message_id)
    yes = types.InlineKeyboardButton(text="Yes", callback_data='clear_yes')
    no=types.InlineKeyboardButton(text ="No" , callback_data="clear_no")
    seting=types.InlineKeyboardMarkup()
    seting.add(yes,no)
    bot.send_message(call.message.chat.id,"Do you want to Clear all your preferences(words)?",reply_markup=seting)
    return
  if call.data == "clear_no":
    bot.delete_message(call.message.chat.id,call.message.message_id)
    bot.answer_callback_query(call.id, text="Canceled!")
    handle_start(call.message)
    return
  if call.data == "clear_yes":
    
    db_data.update_one({"_id":call.message.chat.id},{"$set":{"words":[]}})
    bot.delete_message(call.message.chat.id,call.message.message_id)
    bot.answer_callback_query(call.id, text="Your words has been Cleared!")
    handle_start(call.message)
    return
  if call.data == 'add':
    handle_start(call.message)
    return
  if call.data == 'done':
    word = check_words(call.message.chat.id)
    if not word:
      bot.answer_callback_query(call.id, text="You didn't touch anything!!")
      return
    else:
      bot.delete_message(call.message.chat.id,call.message.message_id)
      ss=bot.send_message(call.message.chat.id,"Thanks for using the bot. \n------------------------------------\nI will notify you when there is new course.\n\nUse /setting to delete or add new course")
      bot.pin_chat_message(call.message.chat.id,ss.message_id)
    return
  if "~" in call.data:
    #'all~'+str(call_data)
    buttons = call.data.split("~")[1]
    clicked_button= check_clicked_button(buttons)
    if call.data in user_languages:
      db_data.update_one({"_id":call.message.chat.id},{"$pull":{"words":call.data}})
      for button in clicked_button:
        db_data.update_one({"_id":call.message.chat.id},{"$pull":{"words":button}})
    else:
      db_data.update_one({"_id":call.message.chat.id},{"$push":{"words":call.data}})
      for button in clicked_button:
        if button in user_languages:
          pass
        else:
          db_data.update_one({"_id":call.message.chat.id},{"$push":{"words":button}})
    bot.answer_callback_query(call.id, text="Selected all!")
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=main_buttons(call.message.chat.id))
    return
  if call.data == "back_main":
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=main_buttons(call.message.chat.id))
  else:
    if "|" in call.data:
      call_data = call.data.split("|")[0]
      the_button = call.data.split("|")[1]
      
      if call_data in user_languages:
        if f"all~{the_button}" in user_languages:
          print(f"the_button: {the_button} ")
          db_data.update_one({"_id":call.message.chat.id},{"$pull":{"words":f"all~{the_button}"}})
        db_data.update_one({"_id":call.message.chat.id},{"$pull":{"words":call_data}})
      else:
          db_data.update_one({"_id":call.message.chat.id},{"$push":{"words":call_data}})
      print(call.data)
      bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=sub_buttons(the_button,call.message.chat.id))
    else:
      print(call.data)
      if call.data in user_languages:
          db_data.update_one({"_id":call.message.chat.id},{"$pull":{"words":call.data}})
          
      else:
          db_data.update_one({"_id":call.message.chat.id},{"$push":{"words":call.data}})
      print(call.data)
      bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=main_buttons(call.message.chat.id))

@bot.message_handler(commands=['setting'])
def handle_setting(message):
  sql = types.InlineKeyboardButton(text=f"Add/Remove", callback_data='add')
  can=types.InlineKeyboardButton(text ="Clear" , callback_data="clear")
  dev=types.InlineKeyboardButton(text ="Dev.." , url="https://t.me/huam3")
  seting=types.InlineKeyboardMarkup()
  seting.row_width=(2)
  seting.add(sql,can,dev)
  bot.send_message(message.chat.id,"You can add, delete or clear your preferences",reply_markup=seting)


# Handle /start command
@bot.message_handler(commands=['salih'])
def handle_start(message):
    global markup
    #sql = types.InlineKeyboardButton(text=f"✅{'call.data'}", callback_data='call.data')
   # markup.add(sql)
    user_id = message.chat.id
    bot.send_message(user_id, "Select Your Preferences:", reply_markup=main_buttons(message.chat.id))

def check_clicked_button(the_button):
    if the_button == "Programming``":
      clicked_button= programming_languages
    elif the_button == "Adobe``":
      clicked_button= adobe_buttons
    elif the_button == "Digital Marketing``":
      clicked_button= digital_marketing_buttons
    elif the_button == "Cloud Computing``":
      clicked_button= cloud_computing_buttons
    elif the_button == "Front-end Frameworks``":
      clicked_button= frontend_buttons
    elif the_button == "Back-end Frameworks``":
      clicked_button= backend_buttons
    elif the_button == "Game Development``":
      clicked_button= game_development_buttons
    elif the_button == "Data Science``":
      clicked_button= data_science_buttons
    return clicked_button

def get_courses_list():
  baseurl="https://studybullet.com/"
  print("Sending request to url")
  r = requests.get(baseurl, timeout=10, allow_redirects=False)
  print("Recived data from url")
  soup = bs(r.content,'lxml')
  print("Converted to lxml")
  courses_list = soup.find_all('div', class_ = 'blog-entry-inner clr')
  print("Get the 'div")
  return courses_list

def get_course_detail_list(colinks:list) -> list:
  headers= {
    'User-Agent' : 'Mozilla/5.0 (Linux; Android 10; SM-G980F Build/QP1A.190711.02AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.96 Mobile Safari/537.36'
  }
  print("Getting data for each course")
  course_details = []
  for i in colinks:     
    print("Getting course data...")
    re= requests.get(i, headers=headers)
    print("Recived it!")
    soup= bs(re.content,'lxml')
    title= soup.find('h1', class_='page-header-title clr').text
    for k in soup.find_all('div', class_= 'entry-content clr'):
      disc=k.find('p').text
      imglink=k.find('img',src=True)['src']
    link=soup.find('a', class_='enroll_btn',href=True)['href']
    codetail={
      "study_link": i,
      'title': title,
      'imglink': imglink,
      'disc': disc,
      'link': link
    }
                 
    course_details.append(codetail)
  return course_details

def increase_users_course_count(user_ids:list):
  operations = [
    UpdateOne(
        {"_id": user_id},
        {"$inc": {"course_count": 1}},
        upsert=True
    )
    for user_id in user_ids
  ]

  db_data.bulk_write(operations)
  print(f"Increased the users course_count by 1 for {len(user_ids)} users!")

def send_the_course_to_user(user_id, imglink, title, disc, link, rate_button=None):
  butmark=telebot.types.InlineKeyboardMarkup()
  button= telebot.types.InlineKeyboardButton("🎁Enroll Link🧭", url=link)
  butmark.add(button)
  if rate_button:
    butmark.add(rate_button)
  try:
    bot.send_photo(user_id,imglink,caption=f'{title} \n▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔\n{disc}\n⏳Free for first 500-1000 Enrollments only❗️', reply_markup=butmark)
  except:
    try:
      bot.send_photo(user_id,imglink,caption=f'{title} \n▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔\n{disc}\n⏳Free for first 500-1000 Enrollments only❗️', reply_markup=butmark)
    except:
      # db_data.delete_one({"_id": user_id})
      # print('blocked user deleted')
      pass

def send_rate_the_bot_m(user_id, rel=False): 
  can=types.InlineKeyboardButton(text ="Join" , url="https://t.me/huam3_info")
  rate=types.InlineKeyboardButton(text ="Rate" , url="https://t.me/BotsArchive/2874")
  rated=types.InlineKeyboardButton(text ="Check" , callback_data="rated")
  seting=types.InlineKeyboardMarkup()
  seting.row_width=(2)
  seting.add(can, rate)
  seting.add(rated)
  message = "<a href='https://t.me/BotsArchive/2874'>Rate the bot 5 star</a> and join the channel to continue using the bot\nClick the 'Check' button after joining the channel and <a href='https://t.me/BotsArchive/2874'>rating the bot 5 start</a>"
  m = """

1️⃣ <a href='https://t.me/huam3_info'>Subscribe to our channel</a>
2️⃣ <a href='https://t.me/BotsArchive/2874'>Rate the bot 5 stars</a>

Complete these steps and click 'check'"""
  try:
      if rel:
        message = m
      bot.send_message(user_id, message, parse_mode="HTML", disable_web_page_preview=True, reply_markup=seting)
  except: 
      pass
    
def check_rate(user_id):
   api_url = f"https://api.botsarchive.com/getUserVote.php?bot_id=4183&user_id={user_id}"
   res = requests.get(api_url)
   if res.status_code != 200:
      bot.send_message(843171085, "error on rate api request") #There's some error so it will act like the user vote
   rate = res.json().get("result")
   no_vote = res.json().get("vote", None)
   print(f"user {user_id} has rate: {rate}, no_vote: {no_vote}")
   rat=types.InlineKeyboardButton(text ="Rate" , url="https://t.me/BotsArchive/2874")
   rated=types.InlineKeyboardButton(text ="Check" , callback_data="rated")
   seting=types.InlineKeyboardMarkup()
   seting.row_width=(1)
   seting.add(rat, rated)
   if no_vote:
      bot.send_message(user_id, "You need to vote first...", reply_markup=seting)
      return
   if rate in ['1', '2', '3', '4']:
      bot.send_message(user_id, f"You have rated the bot {rate} star...\nIf you have feedback or some issue you can <a href='https://t.me/huam3'>contact me</a>:) @huam3\nYou have to rate 5 to use the bot", parse_mode="HTML", disable_web_page_preview=True, reply_markup=seting)
      return
   
   chat_member=bot.get_chat_member("@huam3_info",user_id)
   if chat_member.status == "left":
      can=types.InlineKeyboardButton(text ="Join" , url="https://t.me/huam3_info")
      seting=types.InlineKeyboardMarkup()
      seting.row_width=(1)
      seting.add(can)
      bot.send_message(user_id, "You have rated the bot, Now join the channel...", reply_markup=seting)
      return
   db_data.update_one({"_id": user_id},{"$set":{"rated_the_bot": True, "joined_the_channel": True}})
   bot.send_message(user_id, "You have rated the bot and joined the channel.\nThe bot will now send you Courses as before.")
   user = db_data.find_one({"_id": user_id})
   f_name = user.get("first_name")
   u_name = user.get("username")
   c_count = user.get("course_count")
   words = len(user.get("words", []))
   bot.send_message(LOG_CHA_ID, f"<blockquote expandable>User: <a href='https://t.me/{u_name}'>{f_name}</a>\nID: {user_id}\nCourse count: {c_count}\nTotal words: {words} </blockquote>", parse_mode="HTML", disable_web_page_preview=True)
   

def webbscrapping():
    try:
      count=0
      while True:
        try:
                count+=1
                print(f'count:{count}!')
                # bot.send_message(843171085, f"count: {count}")
                courses_list = get_courses_list()
                colink=[]
                bre=False
                with open('store.json', 'r') as json_file:
                        current_link = json.load(json_file)
                for listdiv in courses_list:
                  for list in listdiv.find_all('div', class_ ='thumbnail'):
                    for i in list.find_all('a', href=True):
                      
                      if i['href'] == current_link:
                        bre=True
                        break
                      else:
                        colink.append(i['href'])
                    if bre:
                      break
                  if bre:
                    break
                      
                if not colink:
                  time.sleep(60)
                      
                print("Found new ", len(colink), " courses")
                # bot.send_message(843171085, f"Found {len(colink)}")
                courses_details= get_course_detail_list(colink)
                
                if courses_details:
                  
                  # with open('data.json', 'r') as json_file:
                  #       users = json.load(json_file)
                  for details in courses_details[::-1]:
                    try:
                      study_link = details['study_link']
                      try:
                          print(f"Looping inside each course: {details['title']}\nstudy_link: {study_link}")
                      except:
                          pass
                      
                      bot.send_message(LOG_CHA_ID, f"Looping inside each course: {details['title']}")
                      int_users=[]
                      users_course_count = {}
                      rated_the_bot = {}
                      db_users = db_data.find({})
                      blocked_users = db_data.find({"$nor": [{"course_count": {"$gt": 30}, "rated_the_bot": False}]})

                      for user in db_users:
                        try:
                          user_id = user["_id"]
                          users_course_count[user_id] = user.get("course_count", 0)
                          rated_the_bot[user_id] = user.get("rated_the_bot", False)

                          for word in user.get("words", []):
                            if word.lower() in details['title'].lower().split():
                              if user["_id"] in int_users:
                                pass
                              else:
                                int_users.append(user["_id"])
                        except Exception as e:
                          print(f"Error while looping on users to check the word: {e}")
                    
                      try:
                          print(f"Found {len(int_users)} interested users on: {details['title']}")
                      except:
                         pass
                      bot.send_message(LOG_CHA_ID, f"Found {len(int_users)} interested users on: {details['title']}")
                      
                      
                      for user_id in int_users:
                        if users_course_count.get(user_id) > 20 and not rated_the_bot.get(user_id):
                          send_rate_the_bot_m(user_id)
                          
                          # continue
                        time.sleep(0.05)
                        send_the_course_to_user(user_id, details['imglink'], details['title'], details['disc'], details['link'])
                      if len(int_users) > 1:
                        increase_users_course_count(int_users)

                      if len(int_users) > 2:                      
                        users = db_data.find(
                            {"course_count": {"$exists": True}}  # Optional: Only include documents with 'course_count'
                        ).sort("course_count", -1).limit(10)

                        mes = {
                            user["_id"]: {
                                "first_name": user["first_name"],
                                "username": user["username"],
                                "course_count": user["course_count"],
                                "words_count": len(user["words"])
                            }
                            for user in users
                        }

                        gt5 = db_data.count_documents({"course_count": {"$gt": 5, "$lt": 10}})
                        gt10 = db_data.count_documents({"course_count": {"$gt": 9, "$lt": 15}})
                        gt15 = db_data.count_documents({"course_count": {"$gt": 14, "$lt": 20}})
                        gt20 = db_data.count_documents({"course_count": {"$gt": 19, "$lt": 30}})
                        gt30 = db_data.count_documents({"course_count": {"$gt": 30}})
                        message = f"Users with course_count greater than \n5: {gt5}, 10: {gt10}, 15: {gt15}, 20: {gt20}, 30: {gt30}\n\n"

                        for user_id, user_detail in mes.items():
                            message += (
                                f"ID: {user_id}\n"
                                f"Name: {user_detail['first_name']}\n"
                                f"Username: {user_detail['username']}\n"
                                f"Courses: {user_detail['course_count']}\n"
                                f"Words Count: {user_detail['words_count']}\n\n"
                            )

                        bot.send_message(LOG_CHA_ID, f"<blockquote expandable>{message}</blockquote>", parse_mode="HTML")


                      

                      with open('store.json', 'w') as json_file:
                            json.dump(study_link, json_file, indent=3)
                      
                      # if len(int_users) != 0:
                      #   # bot.send_photo(843171085,details['imglink'],caption=f'{ttile} \n{thier_word} in {details}', reply_markup=butmark)
                      #   tcours = db_data.find_one({"_id":1111})
                      #   total=int(tcours['tcours'])+1
                      #   db_data.update_one({"_id":1111},{"$set":{"tcours":total}})
                        # th= threading.Thread(target=auto_status,args=(False,))
                        # th.start()
                    except Exception as e:
                      try:
                        msg = str(e).split(" ")[-1]
                        sec = int(msg)
                        bot.send_message(843171085, f"Flood error sleeping {sec}")
                        time.sleep(sec)
                      except:
                        bot.send_message(843171085, f"Error when looping sleep 10s: {e}")
                        time.sleep(10)
        except Exception as e:
          print(e)
          bot.send_message(843171085, f"Error: {e}")
    except:
        pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    check = db_data.find_one({"_id":message.chat.id})
    if check == None:
      # th= threading.Thread(target=auto_status)
      # th.start()
      try:
        db_data.insert_one({"_id":message.chat.id, 'first_name': message.chat.first_name,'username':message.chat.username,'words':[], 'course_count': 0, 'rated_the_bot':False, 'joined_the_channel': False})
      except:
        try:
          db_data.update_one({"_id":message.chat.id},{"$set":{'first_name': message.chat.first_name,'username':message.chat.username,'words':[], 'course_count': 0, 'rated_the_bot':False, 'joined_the_channel': False}}, upsert=True)
        except Exception as e:
          bot.send_message(843171085, f"error when adding user to db: {e}")
    if check.get("course_count") > 30 and not check.get("rated_the_bot"):
      send_rate_the_bot_m(message.chat.id)
      return
    if check.get("course_count") > 20 and not check.get("rated_the_bot"):
      send_rate_the_bot_m(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    add = types.InlineKeyboardButton(text="Add", callback_data='add')
    markup.add(add)
    welcome_message = "👋 Hello!! Welcome to the Udemy Course Bot! 🎉\n\n"
    welcome_message += "This bot is here to help you find the latest free Udemy courses based on your interests. Add your preferences with the button below.\n"
    welcome_message += "If you have any questions or need assistance, feel free to ask with /help command. I'm here to help!"

    bot.send_message(message.chat.id, welcome_message,reply_markup=markup)

    time.sleep(2)
    join_mess= "You can join the channel to get any updates."
    button= "📁Join the Channel🎓"
  
    chat_member=bot.get_chat_member("@huam3_info",message.chat.id)
    can=types.InlineKeyboardButton(text =button , url="https://t.me/huam3_info")
    seting=types.InlineKeyboardMarkup()
    seting.row_width=(1)
    seting.add(can)
    #if chat_member.status == "left":
    #  bot.reply_to(message,join_mess,reply_markup=seting)
    #  pass
    




@bot.message_handler(commands=['my'])
def my_welcome(message):
  try:
    words = check_words(message.chat.id)
    bot.send_message(message.chat.id,f"Your words:\n{words}")
  except:
    pass


@bot.message_handler(commands=['help'])
def help(message):
  markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  markup.add(types.KeyboardButton("Cancel"))
  bot.send_message(message.chat.id,'How can i help you? write your question or comments!',reply_markup=markup)
  bot.register_next_step_handler(message,respons)

def respons(message):
  if message.text == 'Cancel':
    send_welcome(message)
    return
  bot.send_message(843171085,f'{message.from_user.first_name} @{message.from_user.username} {message.chat.id}:\n{message.text}\n\nUse h__843171085@hello')
  bot.send_message(message.chat.id,'Your text has been send to the admin.')

@bot.message_handler(func=lambda message:True)
def lisning(message):
    print(message.text)
    user_id=message.chat.id
    wait= bot.send_message(user_id,"wait...",reply_markup=types.ReplyKeyboardRemove())
    bot.delete_message(user_id,wait.message_id)
    check = db_data.find_one({"_id":message.chat.id})
    if check == None:
      db_data.update_one({"_id":message.chat.id},{"$set":{'first_name': message.chat.first_name,'username':message.chat.username,'words':[], 'course_count': 0, 'rated_the_bot':False, 'joined_the_channel': False}}, upsert=True)
    join_mess= "You can join the channel to get any updates."
    button= "📁Join the Channel🎓"
    
    chat_member=bot.get_chat_member("@huam3_info",message.chat.id)
    can=types.InlineKeyboardButton(text =button , url="https://t.me/huam3_info")
    seting=types.InlineKeyboardMarkup()
    seting.row_width=(1)
    seting.add(can)
    if chat_member.status == "left":
      cu=random.randint(1,2)
      print(cu)
      if cu== 2:
        bot.reply_to(message,join_mess,reply_markup=seting)
  
  
    if message.text[0:3] == 'h__':
      ids,mess=message.text[3:].split('@',1)
      print(ids,mess)
      bot.send_message(ids,'Message from Admin:')
      bot.send_message(int(ids),mess)
    if message.text == "Cancel":
      handle_start(message)
      return
    else:
      print(message.text)
      with open('data.json', 'r') as f:
        users=json.load(f)
      ids=str(message.chat.id)
      print(ids)
      db_data.update_one({"_id":message.chat.id},{"$push":{"words":message.text}})
      bot.send_message(message.chat.id,f"The word {message.text} has been Savedd!")
    
    


th= threading.Thread(target=webbscrapping)
th.start()

# server()
bot.send_message(843171085, "Starting the poll ...")
print("Server Started...")
bot.infinity_polling()

# webbscrapping()
