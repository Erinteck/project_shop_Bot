# Project Name: Telegram Bot for Product Management 🤖📦

This project is a Telegram bot that allows users to retrieve product information from a database. The bot uses Python and `asyncio` for asynchronous operations. This README provides an overview of the project, its setup, and usage.

## Features ✨

- Retrieve product list from the database.
- Easy configuration and management of Telegram bot settings.
- Database interaction for storing and fetching product information.
- Simple configuration through environment variables.

## Prerequisites ⚙️

Before setting up the project, make sure you have the following:

1. **Python 3.7+** 🐍
2. **Required Libraries**:
   - `aiomysql` (for asynchronous MySQL database interaction)
   - `python-telegram-bot` (for interacting with the Telegram Bot API)
   - `asyncpg` (for asynchronous PostgreSQL database interaction)

   To install the dependencies, run:
   ```bash
   pip install -r requirements.txt
   ```

## Setting Up the Project 🛠️

Follow these steps to set up and run the project:

1. **Set Environment Variables** 🌱:
   First, you need to configure your environment variables. These include your Telegram bot's token and database connection details.

   In your `.env` file, set the following variables:
   ```bash
   APP_ID=your_app_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   ```

2. **Database Setup** 🗃️:
   This project uses a database to store product information. Ensure you have a database with a `products` table. The table structure is as follows:
   ```sql
   CREATE TABLE products (
       id INT PRIMARY KEY AUTO_INCREMENT,
       name VARCHAR(255),
       description TEXT,
       price DECIMAL(10, 2),
       image_url VARCHAR(255),
       is_available BOOLEAN
   );
   ```

3. **Running the Project 🚀**:
   Once your environment variables and database are set up, run the bot using:
   ```bash
   python bot.py
   ```

## Code Explanation 📜

### 1. **Configuration Code (`config.py`)** 🔧:
This file stores the settings for the bot and the database. It retrieves the `APP_ID`, `API_HASH`, and `BOT_TOKEN` from the environment variables.

```python
import os

class Config(object):
    APP_ID = int(os.environ.get("APP_ID", 'your APP_ID'))
    API_HASH = os.environ.get("API_HASH", "API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "BOT_TOKEN")
```

### 2. **Database Connection Code (`database.py`)** 💾:
This file contains the functions to connect to the database and perform asynchronous operations. The `get_db_connection()` function handles the database connection.

```python
import aiomysql

async def get_db_connection():
    conn = await aiomysql.connect(
        host='localhost',
        user='root',
        password='your_password',
        db='your_db',
        loop=loop
    )
    return conn
```

### 3. **Product List Code (`product_list.py`)** 🛍️:
This file contains the `get_product_list()` function, which fetches the product list from the database asynchronously. The function returns the product details as a dictionary.

```python
from database import get_db_connection

async def get_product_list():
    products = []
    conn = await get_db_connection()
    if conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute("SELECT * FROM products")
            rows = await cursor.fetchall()
            for row in rows:
                products.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": row[3],
                    "image_url": row[4],
                    "is_available": row[5]
                })
        except Exception as e:
            print(f"Error getting product list: {e}")
        finally:
            await conn.close()
    return products
```

### 4. **Telegram Bot Code (`bot.py`)** 🤖:
This file contains the code to interact with the Telegram Bot API. The bot uses the `BOT_TOKEN` defined in `config.py` to connect to Telegram and respond to user commands.

```python
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import Config

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your product management bot.')

def main():
    updater = Updater(Config.BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()
```

## Project Structure 📂

```
project_name/
│
├── bot.py               # Telegram bot code
├── config.py            # Configuration and environment variables
├── database.py          # Database connection code
├── product_list.py      # Function to fetch product list
├── requirements.txt     # List of required libraries
└── .env                 # Environment variables file
```
## 🙋 Developed by

[Matin Ebadi (GitHub)](https://github.com/matinebadi)

