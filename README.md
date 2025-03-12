# Udemy Telegram Bot  

A Telegram bot that sends Udemy courses to interested users based on their selected preferences.  

## 🔗 Bot Link  
[Udemy Course Bot](https://t.me/Udemy_corse_bot)  

## 🚀 Features  
- `/start` - Welcome message with a button to select course preferences  
- Users can select topics (e.g., Python, Web Development) or type their own preferences  
- The bot checks for new Udemy courses every minute using Celery  
- New courses are automatically sent to interested users  
- Courses include an image, title, short description, and buttons for refresh & course link  
- After sending 20+ courses, the bot stops sending if the user hasn’t joined the channel or rated the bot  

## 📌 TODO List  
- [ ] Implement `/start` and `/help` commands  
- [ ] Build the course selection system (buttons & text input)  
- [ ] Save user preferences in the database  
- [ ] Integrate with Udemy API to fetch courses  
- [ ] Implement Celery for periodic course updates  
- [ ] Send course updates to users based on their interests  
- [ ] Add course message buttons (refresh & link)  
- [ ] Stop sending courses if user hasn’t joined/rated  
- [ ] Deploy the bot and set up background workers  

## 🛠 Tech Stack  
- **Python**  
- **python-telegram-bot**  
- **Celery** for scheduled tasks  
- **PostgreSQL** for storing user data  
- **Django REST Framework (Future Integration)**  

Stay tuned for updates! 🚀  
