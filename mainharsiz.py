import discord
from discord.ext import commands, tasks
import sqlite3
import random
import asyncio
import time
import datetime
import math # For help pagination
from discord.ui import Button, View

btoken = "MTM4MTMzMjQ1NjIyMDY1NTgyNw.GBIKle.ezlDWQzf68w6jr3ZAOw2TBiK1c9RWt_3kfMEf0"
# --- CONFIGURATION ---
CONFIG = {
    "PREFIX": ">",
    "DEFAULT_COLOR": 0x2B2D31, # Discord dark gray color
    "ERROR_COLOR": 0xED4245,   # Discord red color
    "SUCCESS_COLOR": 0x57F287, # Discord green color
    "INFO_COLOR": 0x5865F2,    # Discord blurple color

    # Economy Settings
    "WORK_COOLDOWN_SECONDS": 240, # 4 minutes
    "WORK_MIN_PAY": 100,
    "WORK_MAX_PAY": 500,
    "ROB_COOLDOWN_SECONDS": 900, # 15 minutes
    "ROB_SUCCESS_CHANCE": 0.35, # 35% chance to succeed
    "ROB_MIN_STOLEN_PERCENT": 0.10, # Steal 10-30% of target's cash
    "ROB_MAX_STOLEN_PERCENT": 0.30,
    "MAX_LEADERBOARD_ENTRIES": 10,
    "BLACKJACK_WIN_MULTIPLIER": 2,

    # New Economy Command Settings
    "DAILY_COOLDOWN_SECONDS": 86400, # 24 hours
    "DAILY_PAY_MIN": 1000,
    "DAILY_PAY_MAX": 4000,

    "BEG_COOLDOWN_SECONDS": 300, # 5 minutes
    "BEG_SUCCESS_CHANCE": 0.40, # 40% chance to get money
    "BEG_MIN_PAY": 50,
    "BEG_MAX_PAY": 200,
    "BEG_FAIL_CHANCE": 0.20, # 20% chance to lose money
    "BEG_MIN_LOSS": 10,
    "BEG_MAX_LOSS": 50,

    "COINFLIP_WIN_MULTIPLIER": 1.125, # Win double your bet

    # --- Earning/Work Alternatives ---
    "SCAVENGE_COOLDOWN_SECONDS": 180, # 3 minutes
    "SCAVENGE_CASH_CHANCE": 0.60, # 60% chance to find cash
    "SCAVENGE_MIN_CASH": 20,
    "SCAVENGE_MAX_CASH": 150,
    "SCAVENGE_ITEM_CHANCE": 0.25, # 25% chance to find item (if no cash)
    "SCAVENGE_POSSIBLE_ITEMS": ["trash", "potion"], # Items that can be found
    "SCAVENGE_FAIL_CHANCE": 0.15, # 15% chance to find nothing

    "ADVENTURE_COOLDOWN_SECONDS": 600, # 10 minutes
    "ADVENTURE_SUCCESS_CHANCE": 0.50, # 50% chance for good outcome
    "ADVENTURE_MEDIUM_CHANCE": 0.30, # 30% chance for neutral outcome
    "ADVENTURE_RISK_CHANCE": 0.20, # 20% chance for negative outcome
    "ADVENTURE_MIN_SUCCESS_PAY": 500,
    "ADVENTURE_MAX_SUCCESS_PAY": 2000,
    "ADVENTURE_SUCCESS_ITEMS": ["gem", "mystery box"],
    "ADVENTURE_MIN_RISK_LOSS": 100,
    "ADVENTURE_MAX_RISK_LOSS": 500,

    # --- NEW: Two Stock Commands (10 min cooldown each) ---
    "MINE_COOLDOWN_SECONDS": 600, # 10 minutes
    "MINE_CASH_CHANCE": 0.40,      # 40% chance to find cash
    "MINE_MIN_CASH": 150,
    "MINE_MAX_CASH": 600,
    "MINE_ITEM_CHANCE": 0.50,      # 50% chance to find item (if no cash)
    "MINE_POSSIBLE_ITEMS": ["metal", "gem"], # Items that can be found while mining
    "MINE_FAIL_CHANCE": 0.10,      # 10% chance to find nothing

    "FORAGE_COOLDOWN_SECONDS": 600, # 10 minutes
    "FORAGE_CASH_CHANCE": 0.30,     # 30% chance to find cash
    "FORAGE_MIN_CASH": 50,
    "FORAGE_MAX_CASH": 250,
    "FORAGE_ITEM_CHANCE": 0.60,     # 60% chance to find item (if no cash)
    "FORAGE_POSSIBLE_ITEMS": ["berry", "mushroom", "herb"], # New items
    "FORAGE_FAIL_CHANCE": 0.10,     # 10% chance to find nothing

    # --- NEW: Investment Settings ---
    "INVEST_CUT_PERCENTAGE": 0.0125,
    "INVEST_COOLDOWN_SECONDS": 3,

    # --- Gambling Command Settings ---
    "ROULETTE_COOLDOWN_SECONDS": 90, # 90 seconds
    "ROULETTE_SINGLE_NUMBER_MULTIPLIER": 35,
    "ROULETTE_COLOR_ODD_EVEN_HIGH_LOW_MULTIPLIER": 2,

    "DICEROLL_COOLDOWN_SECONDS": 45, # 45 seconds
    "DICEROLL_HIGHLOW_MULTIPLIER": 2,
    "DICEROLL_SEVEN_MULTIPLIER": 5,

    "SLOTS_COOLDOWN_SECONDS": 75, # 75 seconds
    "SLOTS_SYMBOLS": ["🍒", "🍋", "🍊", "🍇", "🔔", "💰", "💎", "7️⃣"],
    "SLOTS_WEIGHTS": [0.30, 0.25, 0.20, 0.10, 0.08, 0.04, 0.02, 0.01], # Sum must be 1.0
    "SLOTS_PAYOUTS": {
        ("🍒", "🍒", "🍒"): 1.5,
        ("🍋", "🍋", "🍋"): 1.5,
        ("🍊", "🍊", "🍊"): 1.5,
        ("🍇", "🍇", "🍇"): 2.0,
        ("🔔", "🔔", "🔔"): 2.0,
        ("💰", "💰", "💰"): 5.0,
        ("💎", "💎", "💎"): 7.5,
        ("7️⃣", "7️⃣", "7️⃣"): 15.0, # Jackpot
        ("7️⃣", "7️⃣", "*"): 2.5, # Two 7s + any other
        ("*", "7️⃣", "7️⃣"): 2.5,
        ("7️⃣", "*", "7️⃣"): 2.5,
    },
    "SLOTS_LOSE_MULTIPLIER": 0.5, # If a specific payout isn't hit, what happens?

    "RPS_COOLDOWN_SECONDS": 30, # 30 seconds
    "RPS_WIN_MULTIPLIER": 2,

    "GUESS_COOLDOWN_SECONDS": 60, # 60 seconds
    "GUESS_RANGE": (1, 10),
    "GUESS_WIN_MULTIPLIER": 8,

    # --- NEW: Additional Gambling Commands ---
    "HIGHLOWER_COOLDOWN_SECONDS": 45, # 45 seconds
    "HIGHLOWER_WIN_MULTIPLIER": 1.9, # Close to double

    "SCRATCH_COOLDOWN_SECONDS": 60, # 60 seconds
    "SCRATCH_WIN_CHANCE": 0.30, # 30% chance to win
    "SCRATCH_WIN_MULTIPLIER": 3.0, # Win 3x your bet
    "SCRATCH_LOSE_MULTIPLIER": 0.1, # Get 10% back on loss

    "TRIVIA_COOLDOWN_SECONDS": 90, # 90 seconds
    "TRIVIA_WIN_MULTIPLIER": 2.5, # Win 2.5x your bet
    "TRIVIA_QUESTIONS": [ # (question, [correct_answers], wrong_answers, difficulty_rating)
        ("What is the capital of France?", ["paris"], ["berlin", "london", "rome"], "Easy"),
        ("Which planet is known as the 'Red Planet'?", ["mars"], ["venus", "jupiter", "saturn"], "Easy"),
        ("What is the largest ocean on Earth?", ["pacific"], ["atlantic", "indian", "arctic"], "Medium"),
        ("Who wrote 'Romeo and Juliet'?", ["william shakespeare", "shakespeare"], ["charles dickens", "jane austen", "mark Twain"], "Easy"),
        ("What is the chemical symbol for water?", ["h2o"], ["co2", "o2", "nacl"], "Easy"),
        ("What is the square root of 144?", ["12"], ["10", "14", "16"], "Easy"),
        ("Which animal lays the largest eggs?", ["ostrich"], ["chicken", "emu", "snake"], "Medium"),
        ("What is the fastest land animal?", ["cheetah"], ["lion", "tiger", "gazelle"], "Medium"),
        ("In what country would you find the Great Barrier Reef?", ["australia"], ["new zealand", "indonesia", "philippines"], "Easy"),
        ("What is the name of the first man on the moon?", ["neil armstrong", "armstrong"], ["buzz aldrin", "michael collins", "yuri gagarin"], "Easy"),
        ("How many continents are there?", ["7", "seven"], ["5", "6", "8"], "Easy"),
        ("Which fictional city is the home of Batman?", ["gotham city", "gotham"], ["metropolis", "starling city", "central city"], "Easy"),
        ("What is the longest river in the world?", ["nile"], ["amazon", "yangtze", "mississippi"], "Hard"), # Technically Amazon is debated
        ("Who painted the Mona Lisa?", ["leonardo da vinci", "da vinci"], ["vincent van gogh", "pablo picasso", "michelangelo"], "Easy"),
        ("What is the smallest prime number?", ["2"], ["1", "3", "0"], "Medium"),
        ("What year did the Titanic sink?", ["1912"], ["1905", "1915", "1920"], "Medium"),
        ("Which gas is most abundant in Earth's atmosphere?", ["nitrogen"], ["oxygen", "argon", "carbon dioxide"], "Medium"),
        ("What is the hardest natural substance on Earth?", ["diamond"], ["steel", "titanium", "quartz"], "Easy"),
        ("What is the capital of Japan?", ["tokyo"], ["beijing", "seoul", "bangkok"], "Easy"),
        ("How many bones are in the adult human body?", ["206"], ["200", "210", "220"], "Medium"),
        ("What is the currency of the United Kingdom?", ["pound sterling", "pound"], ["euro", "dollar", "yen"], "Easy"),
        ("What is the name of the galaxy our solar system is in?", ["milky way"], ["andromeda", "triangulum", "sombrero"], "Easy"),
        ("Who is the Greek god of the sea?", ["poseidon"], ["zeus", "hades", "ares"], "Easy"),
        ("What is the process by which plants make their food?", ["photosynthesis"], ["respiration", "transpiration", "germination"], "Medium"),
        ("Which country is famous for its fjords?", ["norway"], ["sweden", "finland", "denmark"], "Medium"),
    ],

    # --- NEW: Additional Gambling Command Settings ---
    "WAR_COOLDOWN_SECONDS": 45, # 45 seconds
    "WAR_WIN_MULTIPLIER": 2,

    "SHELLGAME_COOLDOWN_SECONDS": 60, # 60 seconds
    "SHELLGAME_WIN_MULTIPLIER": 3,

    "FISHING_COOLDOWN_SECONDS": 120, # 2 minutes
    "FISHING_MIN_CATCH_PAY": 50,
    "FISHING_MAX_CATCH_PAY": 300,
    "FISHING_TRASH_CHANCE": 0.20, # 20% chance to catch trash
    "FISHING_NOTHING_CHANCE": 0.30, # 30% chance to catch nothing (remaining is fish)

    # Item Related Settings
    "USABLE_ITEMS": {
        "potion": {"effect": "cash_boost", "amount": 250, "description": "Restores a bit of cash."},
        "mystery box": {"effect": "random_item_or_cash", "description": "Contains a random surprise!"},
        "trash": {"effect": "none", "description": "It's just trash. No real use."},
        "gem": {"effect": "high_value", "description": "A shiny, valuable gem. Useful for crafting!"},
        "metal": {"effect": "cash_boost", "amount": 510, "description": "Metal... cash."},
        "berry": {"effect": "cash_boost", "amount": 75, "description": "A wild berry, slightly sweet."}, # NEW
        "mushroom": {"effect": "cash_boost", "amount": 120, "description": "A forest mushroom. Looks safe enough to eat."}, # NEW
        "herb": {"effect": "cash_boost", "amount": 100, "description": "A fragrant herb. Might be useful for concoctions."}, # NEW
    },
    "CRAFTING_RECIPES": {
        "super potion": {
            "ingredients": {"potion": 3, "gem": 1},
            "result": {"super potion": 1},
            "description": "Combines potions and a gem into a powerful super potion, for a large cash boost."
        },
        "mega gem": {
            "ingredients": {"gem": 5, "trash": 1},
            "result": {"mega gem": 1},
            "description": "Crafts a mighty mega gem from smaller ones."
        },
        "metal tool": {
            "ingredients": {"metal": 4, "mystery box": 3},
            "result": {"pro metal": 1},
            "description": "Crafts a mighty mega gem from smaller ones."
        }
    },
    "DEFAULT_ITEM_SELL_PRICE": 100, # Default sell price for generic items if not specified

    # Initial liquidity for new bet markets (to avoid division by zero and allow initial 50/50 price)
    "BETON_INITIAL_LIQUIDITY": 1250, # Each side starts with this much 'virtual' cash/tokens

    # Sniper Cache
    "SNIPE_CACHE_LIMIT": 100, # How many deleted messages to store per channel

    # --- NEW: Stupid/Text Command Data ---
    "INSPIRATIONAL_QUOTES": [
        "The only way to do great work is to love what you do.",
        "Believe you can and you're halfway there.",
        "The future belongs to those who believe in the beauty of their dreams.",
        "It always seems impossible until it's done.",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "The best way to predict the future is to create it.",
        "Don't watch the clock; do what it does. Keep going."
    ],
    "ROAST_LINES": [
        "I've seen more personality in a brick.",
        "Your brain is 90% song lyrics you misheard.",
        "Is your brain made of play-doh? Because it looks like it's been molded by a toddler.",
        "I’d agree with you but then we’d both be wrong.",
        "You’re not the dumbest person in the world, but you better hope they don’t die.",
        "I could eat a bowl of alphabet soup and poop out a smarter statement than that.",
        "Were you born on a highway? Because that's where most accidents happen.",
        "I’ve had a better conversation with a cardboard box.",
        "You're like a dull pencil - pointless.",
        "If your brain was gasoline, it wouldn't even power a scooter."
    ],
    "JOKES": [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call a fake noodle? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "How do you organize a space party? You planet!",
        "What do you call a fish with no eyes? Fsh!",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "Why did the bicycle fall over? Because it was two-tired!",
        "What’s orange and sounds like a parrot? A carrot!",
        "Did you hear about the restaurant on the moon? Great food, no atmosphere.",
        "What do you call a pile of cats? A meow-tain!"
    ],
    "SHOWER_THOUGHTS": [
        "The 's' in 'fast' is silent.",
        "If you wait for a waiter, aren't you the waiter?",
        "If you get out of the shower clean, how does your towel get dirty?",
        "When you sneeze, your brain briefly stops functioning. It's like a mini-reboot.",
        "The word 'bed' looks like a bed.",
        "We are all just skeletons covered in meat and wearing wet clothes.",
        "A bookmark is a tiny seatbelt for your book.",
        "Your hands never really touch anything, because of the electrons repelling.",
        "Every single person has at least one unique talent that literally no one else has.",
        "The world's fastest way to make coffee is to eat coffee beans and then drink hot water."
    ]
}

# --- BOT SETUP ---
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix=CONFIG["PREFIX"], intents=intents, help_command=None)

# --- DATABASE SETUP ---
DATABASE_NAME = "harsizbot.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            cash INTEGER DEFAULT 0,
            bank INTEGER DEFAULT 0,
            last_work INTEGER DEFAULT 0,
            last_rob INTEGER DEFAULT 0
        )
    ''')

    # Add new cooldown columns using ALTER TABLE, handling existing tables
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_daily INTEGER DEFAULT 0')
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_beg INTEGER DEFAULT 0')
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_scavenge INTEGER DEFAULT 0')
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_adventure INTEGER DEFAULT 0')
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_mine INTEGER DEFAULT 0') # NEW
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_forage INTEGER DEFAULT 0') # NEW
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_highlow INTEGER DEFAULT 0') # NEW
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_scratch INTEGER DEFAULT 0') # NEW
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_trivia INTEGER DEFAULT 0') # NEW
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_invest INTEGER DEFAULT 0') # NEW for individual cooldown on investing
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_war INTEGER DEFAULT 0') # NEW for war
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_shellgame INTEGER DEFAULT 0') # NEW for shellgame
    except sqlite3.OperationalError: pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN last_fishing INTEGER DEFAULT 0') # NEW for fishing
    except sqlite3.OperationalError: pass


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            user_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            PRIMARY KEY (user_id, item_name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            listing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            item_name TEXT,
            quantity INTEGER,
            price_per_item INTEGER,
            is_custom BOOLEAN DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snipe (
            channel_id INTEGER PRIMARY KEY,
            author_id INTEGER,
            content TEXT,
            timestamp INTEGER
        )
    ''')

    # NEW TABLE FOR INVESTMENTS
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            investor_id INTEGER,
            investee_id INTEGER,
            amount INTEGER, -- the amount invested
            start_time INTEGER, -- timestamp when investment started
            PRIMARY KEY (investor_id, investee_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bet_markets (
            market_id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER NOT NULL,
            event_text TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN' CHECK(status IN ('OPEN', 'RESOLVED')),
            resolved_outcome TEXT NULL CHECK(resolved_outcome IN ('YES', 'NO')),
            yes_cash_pool INTEGER DEFAULT 0,
            no_cash_pool INTEGER DEFAULT 0,
            yes_token_supply REAL DEFAULT 0.0,
            no_token_supply REAL DEFAULT 0.0,
            message_id INTEGER NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_bet_holdings (
            user_id INTEGER,
            market_id INTEGER,
            yes_tokens REAL DEFAULT 0.0,
            no_tokens REAL DEFAULT 0.0,
            PRIMARY KEY (user_id, market_id)
        )
    ''')

    conn.commit()
    conn.close()

# --- DATABASE HELPERS ---
def get_user_data(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id) VALUES (?)
    ''', (user_id,))
    conn.commit()
    # Ensure all new columns are fetched in the correct order
    cursor.execute('''
        SELECT cash, bank, last_work, last_rob, COALESCE(last_daily, 0), COALESCE(last_beg, 0),
               COALESCE(last_scavenge, 0), COALESCE(last_adventure, 0),
               COALESCE(last_mine, 0), COALESCE(last_forage, 0),
               COALESCE(last_highlow, 0), COALESCE(last_scratch, 0), COALESCE(last_trivia, 0),
               COALESCE(last_invest, 0), COALESCE(last_war, 0), COALESCE(last_shellgame, 0),
               COALESCE(last_fishing, 0)
        FROM users WHERE user_id = ?
    ''', (user_id,))
    data = cursor.fetchone()
    conn.close()
    return data

def update_user_money(user_id, cash_change=0, bank_change=0):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # This logic prevents cash from going below 0, unless specifically bypassed (e.g. for admin commands)
    if cash_change < 0:
        cursor.execute('SELECT cash FROM users WHERE user_id = ?', (user_id,))
        current_cash_row = cursor.fetchone()
        current_cash = current_cash_row[0] if current_cash_row else 0
        if current_cash + cash_change < 0:
            cash_change = -current_cash # Only remove what they have, so cash becomes 0
    
    cursor.execute('UPDATE users SET cash = cash + ?, bank = bank + ? WHERE user_id = ?', (cash_change, bank_change, user_id))
    conn.commit()
    conn.close()

def set_user_cooldown(user_id, cooldown_type, timestamp):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    if cooldown_type == "work":
        cursor.execute('UPDATE users SET last_work = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "rob":
        cursor.execute('UPDATE users SET last_rob = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "daily":
        cursor.execute('UPDATE users SET last_daily = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "beg":
        cursor.execute('UPDATE users SET last_beg = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "scavenge":
        cursor.execute('UPDATE users SET last_scavenge = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "adventure":
        cursor.execute('UPDATE users SET last_adventure = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "mine": # NEW
        cursor.execute('UPDATE users SET last_mine = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "forage": # NEW
        cursor.execute('UPDATE users SET last_forage = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "highlow": # NEW
        cursor.execute('UPDATE users SET last_highlow = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "scratch": # NEW
        cursor.execute('UPDATE users SET last_scratch = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "trivia": # NEW
        cursor.execute('UPDATE users SET last_trivia = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "invest": # NEW for individual cooldown on investing
        cursor.execute('UPDATE users SET last_invest = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "war": # NEW
        cursor.execute('UPDATE users SET last_war = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "shellgame": # NEW
        cursor.execute('UPDATE users SET last_shellgame = ? WHERE user_id = ?', (timestamp, user_id))
    elif cooldown_type == "fishing": # NEW
        cursor.execute('UPDATE users SET last_fishing = ? WHERE user_id = ?', (timestamp, user_id))
    conn.commit()
    conn.close()

def get_user_inventory(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, quantity FROM inventory WHERE user_id = ?', (user_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def add_item_to_inventory(user_id, item_name, quantity):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO inventory (user_id, item_name, quantity) VALUES (?, ?, COALESCE((SELECT quantity FROM inventory WHERE user_id = ? AND item_name = ?), 0) + ?)',
                   (user_id, item_name, user_id, item_name, quantity))
    conn.commit()
    conn.close()

def remove_item_from_inventory(user_id, item_name, quantity):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_name = ?', (user_id, item_name))
    current_quantity = cursor.fetchone()
    if current_quantity and current_quantity[0] >= quantity:
        new_quantity = current_quantity[0] - quantity
        if new_quantity <= 0:
            cursor.execute('DELETE FROM inventory WHERE user_id = ? AND item_name = ?', (user_id, item_name))
        else:
            cursor.execute('UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_name = ?', (new_quantity, user_id, item_name))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_listings():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT listing_id, seller_id, item_name, quantity, price_per_item, is_custom FROM listings')
    listings = cursor.fetchall()
    conn.close()
    return listings

def get_listing_by_id(listing_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT listing_id, seller_id, item_name, quantity, price_per_item, is_custom FROM listings WHERE listing_id = ?', (listing_id,))
    listing = cursor.fetchone()
    conn.close()
    return listing

def add_listing(seller_id, item_name, quantity, price_per_item, is_custom=False):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO listings (seller_id, item_name, quantity, price_per_item, is_custom) VALUES (?, ?, ?, ?, ?)',
                   (seller_id, item_name, quantity, price_per_item, is_custom))
    conn.commit()
    listing_id = cursor.lastrowid
    conn.close()
    return listing_id

def remove_listing(listing_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM listings WHERE listing_id = ?', (listing_id,))
    conn.commit()
    conn.close()

# --- NEW: INVESTMENT HELPERS ---
def add_investment(investor_id, investee_id, amount):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO investments (investor_id, investee_id, amount, start_time) VALUES (?, ?, ?, ?)',
                   (investor_id, investee_id, amount, int(time.time())))
    conn.commit()
    conn.close()

def get_investments_in_user(investee_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT investor_id, amount FROM investments WHERE investee_id = ?', (investee_id,))
    investments = cursor.fetchall()
    conn.close()
    return investments

def get_user_investments(investor_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT investee_id, amount FROM investments WHERE investor_id = ?', (investor_id,))
    investments = cursor.fetchall()
    conn.close()
    return investments

# --- CORE EARNING PROCESSING HELPER ---
async def process_earnings(ctx, user_id, base_earnings):
    """
    Processes earnings for a user, distributing a cut to investors if applicable.
    Returns the net earnings for the user after deductions.
    """
    if base_earnings <= 0: # No earnings, no cuts to distribute
        return base_earnings, None

    investments = get_investments_in_user(user_id)
    total_cut = 0
    investor_messages = []

    for investor_id, _ in investments:
        cut_amount = int(base_earnings * CONFIG["INVEST_CUT_PERCENTAGE"])
        if cut_amount > 0:
            update_user_money(investor_id, cash_change=cut_amount)
            total_cut += cut_amount
            try:
                investor_user = bot.get_user(investor_id) or await bot.fetch_user(investor_id)
                investor_name = investor_user.display_name if investor_user else f"Unknown Investor ({investor_id})"
                investor_messages.append(f"• **{investor_name}**: ${cut_amount:,}")
            except discord.NotFound:
                investor_messages.append(f"• **Unknown Investor ({investor_id})**: ${cut_amount:,}")


    net_earnings = base_earnings - total_cut
    
    # Apply the net earnings to the user
    update_user_money(user_id, cash_change=net_earnings)

    if investor_messages:
        investee_message_embed = discord.Embed(
            title="📉 Investment Revenue Claimed!",
            description=f"{ctx.author.mention}, some of your recent earnings have been claimed by your investors:\n\n"
                        + "\n".join(investor_messages) + f"\n\nYour net gain was **${net_earnings:,}** (after **${total_cut:,}** in cuts).",
            color=CONFIG["ERROR_COLOR"] # Red to signify money "leaving"
        )
        investee_message_embed.set_footer(text="Made With 💖 By Harsizcool")
        try:
            await ctx.author.send(embed=investee_message_embed)
        except discord.Forbidden:
            # User might have DMs disabled, send in channel if possible
            await ctx.send(embed=investee_message_embed, delete_after=15) # Delete after a short while
        return net_earnings, total_cut
    
    return net_earnings, total_cut

# --- BETON MARKET HELPERS --- (No changes to these)

def create_bet_market(creator_id, event_text):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bet_markets (creator_id, event_text, yes_cash_pool, no_cash_pool, yes_token_supply, no_token_supply)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (creator_id, event_text, CONFIG["BETON_INITIAL_LIQUIDITY"], CONFIG["BETON_INITIAL_LIQUIDITY"],
          CONFIG["BETON_INITIAL_LIQUIDITY"], CONFIG["BETON_INITIAL_LIQUIDITY"]))
    market_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return market_id

def get_bet_market(market_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT market_id, creator_id, event_text, status, resolved_outcome, yes_cash_pool, no_cash_pool, yes_token_supply, no_token_supply, message_id FROM bet_markets WHERE market_id = ?', (market_id,))
    market_data = cursor.fetchone()
    conn.close()
    return market_data

def get_all_open_bet_markets():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT market_id, creator_id, event_text, yes_cash_pool, no_cash_pool FROM bet_markets WHERE status = "OPEN"')
    markets = cursor.fetchall()
    conn.close()
    return markets

def update_bet_market_pools(market_id, yes_cash_change, no_cash_change, yes_token_change, no_token_change):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE bet_markets
        SET yes_cash_pool = yes_cash_pool + ?,
            no_cash_pool = no_cash_pool + ?,
            yes_token_supply = yes_token_supply + ?,
            no_token_supply = no_token_supply + ?
        WHERE market_id = ?
    ''', (yes_cash_change, no_cash_change, yes_token_change, no_token_change, market_id))
    conn.commit()
    conn.close()

def get_user_bet_holdings(user_id, market_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO user_bet_holdings (user_id, market_id) VALUES (?, ?)', (user_id, market_id))
    conn.commit()
    cursor.execute('SELECT yes_tokens, no_tokens FROM user_bet_holdings WHERE user_id = ? AND market_id = ?', (user_id, market_id))
    holdings = cursor.fetchone()
    conn.close()
    return holdings

def update_user_bet_holdings(user_id, market_id, yes_tokens_change=0.0, no_tokens_change=0.0):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO user_bet_holdings (user_id, market_id) VALUES (?, ?)', (user_id, market_id))
    conn.commit() # Ensure the row exists before updating
    cursor.execute('''
        UPDATE user_bet_holdings
        SET yes_tokens = yes_tokens + ?,
            no_tokens = no_tokens + ?
        WHERE user_id = ? AND market_id = ?
    ''', (yes_tokens_change, no_tokens_change, user_id, market_id))
    conn.commit()
    conn.close()

def set_bet_market_resolved(market_id, outcome):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE bet_markets SET status = "RESOLVED", resolved_outcome = ? WHERE market_id = ?', (outcome, market_id))
    conn.commit()
    conn.close()

def get_all_user_bet_holdings_for_market(market_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, yes_tokens, no_tokens FROM user_bet_holdings WHERE market_id = ?', (market_id,))
    holdings = cursor.fetchall()
    conn.close()
    return holdings

def clear_user_bet_holdings_for_market(market_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_bet_holdings WHERE market_id = ?', (market_id,))
    conn.commit()
    conn.close()

def get_market_prices_and_supply(yes_cash, no_cash, yes_tokens, no_tokens):
    total_cash = yes_cash + no_cash
    
    yes_price = (no_cash / total_cash) if total_cash > 0 else 0.5
    no_price = (yes_cash / total_cash) if total_cash > 0 else 0.5

    sum_prices = yes_price + no_price
    if not (0.99999 < sum_prices < 1.00001):
        if sum_prices > 0:
            yes_price /= sum_prices
            no_price /= sum_prices
        else:
            yes_price = 0.5
            no_price = 0.5

    yes_prob = round(yes_price * 100, 2)
    no_prob = round(no_price * 100, 2)

    return {
        "yes_price": yes_price,
        "no_price": no_price,
        "yes_prob": yes_prob,
        "no_prob": no_prob,
        "yes_tokens_supply": yes_tokens,
        "no_tokens_supply": no_tokens
    }

# --- SNIPE CACHE ---
deleted_messages = {}

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO snipe (channel_id, author_id, content, timestamp) VALUES (?, ?, ?, ?)',
                   (message.channel.id, message.author.id, message.content, int(time.time())))
    conn.commit()
    conn.close()

# --- BOT EVENTS ---
@bot.event
async def on_ready():
    init_db()
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print(f'Prefix: {CONFIG["PREFIX"]}')
    print('Ready!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        seconds = int(error.retry_after)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        cooldown_str_parts = []
        if hours > 0:
            cooldown_str_parts.append(f"{hours}h")
        if minutes > 0:
            cooldown_str_parts.append(f"{minutes}m")
        if seconds > 0 or not cooldown_str_parts: # Ensure '0s' is shown if time is very short
            cooldown_str_parts.append(f"{seconds}s")
        
        cooldown_str = " ".join(cooldown_str_parts)
        
        embed = discord.Embed(
            title="⏳ Cooldown",
            description=f"You are on cooldown for this command. Try again in `{cooldown_str.strip()}`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="🤔 Missing Argument",
            description=f"You are missing a required argument: `{error.param.name}`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="🚫 Bad Argument",
            description=f"One of your arguments was invalid. Please check your input.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="⛔️ Missing Permissions",
            description="You don't have the necessary permissions to use this command.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="🚨 An Error Occurred",
            description=f"```py\n{error}\n```",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)

# --- ECONOMY COMMANDS ---

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(aliases=["bal", "balance"])
async def money(ctx, member: discord.Member = None):
    target = member or ctx.author
    # Extended tuple unpacking for new cooldown columns
    cash, bank, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(target.id)

    embed = discord.Embed(
        title=f"{target.display_name}'s Balance",
        color=CONFIG["INFO_COLOR"]
    )
    embed.add_field(name="💰 Cash", value=f"${cash:,}")
    embed.add_field(name="🏦 Bank", value=f"${bank:,}")
    embed.add_field(name="💸 Total", value=f"${cash + bank:,}", inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["WORK_COOLDOWN_SECONDS"], commands.BucketType.user)
async def work(ctx):
    user_id = ctx.author.id
    current_time = int(time.time())
    
    pay = random.randint(CONFIG["WORK_MIN_PAY"], CONFIG["WORK_MAX_PAY"])
    
    # Process earnings through the helper to handle investment cuts
    net_earnings, total_cut = await process_earnings(ctx, user_id, pay)

    set_user_cooldown(user_id, "work", current_time)

    work_responses = [
        "You fixed the server racks and earned",
        "You coded a new bot feature and got paid",
        "You cleaned the office, receiving",
        "You delivered pizzas, earning",
        "You mined some crypto, gaining",
        "You helped a grandma cross the street, she gave you"
    ]
    
    embed = discord.Embed(
        title="💼 Work Done!",
        description=f"{random.choice(work_responses)} **${pay:,}** cash. "
                    f"{f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["DAILY_COOLDOWN_SECONDS"], commands.BucketType.user)
async def daily(ctx):
    user_id = ctx.author.id
    current_time = int(time.time())

    reward = random.randint(CONFIG["DAILY_PAY_MIN"], CONFIG["DAILY_PAY_MAX"])
    
    # Process earnings through the helper to handle investment cuts
    net_earnings, total_cut = await process_earnings(ctx, user_id, reward)

    set_user_cooldown(user_id, "daily", current_time)

    embed = discord.Embed(
        title="🗓️ Daily Reward!",
        description=f"You claimed your daily reward of **${reward:,}** cash! "
                    f"{f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["BEG_COOLDOWN_SECONDS"], commands.BucketType.user)
async def beg(ctx):
    user_id = ctx.author.id
    current_time = int(time.time())

    outcome_roll = random.random()
    pay_or_loss = 0
    
    embed = discord.Embed(title="🙏 Begging Outcome", color=CONFIG["INFO_COLOR"])

    if outcome_roll < CONFIG["BEG_SUCCESS_CHANCE"]:
        pay_or_loss = random.randint(CONFIG["BEG_MIN_PAY"], CONFIG["BEG_MAX_PAY"])
        
        # Process earnings through the helper to handle investment cuts
        net_earnings, total_cut = await process_earnings(ctx, user_id, pay_or_loss)

        response = random.choice([
            f"A kind stranger gave you **${pay_or_loss:,}**.",
            f"You found **${pay_or_loss:,}** on the ground!",
            f"Someone felt pity and handed you **${pay_or_loss:,}**.",
            f"You successfully begged and got **${pay_or_loss:,}**."
        ])
        embed.title = "🙏 Beg Successful!"
        embed.description = f"{response} {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}"
        embed.color = CONFIG["SUCCESS_COLOR"]
    elif outcome_roll < (CONFIG["BEG_SUCCESS_CHANCE"] + CONFIG["BEG_FAIL_CHANCE"]):
        loss = random.randint(CONFIG["BEG_MIN_LOSS"], CONFIG["BEG_MAX_LOSS"])
        update_user_money(user_id, cash_change=-loss) # Direct deduction, as this is a loss
        response = random.choice([
            f"A mugger stole **${loss:,}** from you while you were begging.",
            f"You tripped and lost **${loss:,}** from your pocket.",
            f"Someone laughed at you and you felt so embarrassed you dropped **${loss:,}**.",
            f"You were fined **${loss:,}** for loitering."
        ])
        embed.title = "😭 Beg Failed!"
        embed.description = response
        embed.color = CONFIG["ERROR_COLOR"]
    else:
        response = random.choice([
            "No one paid attention to you.",
            "You got nothing.",
            "The street was empty.",
            "A bird pooped on your head. No money, just indignity."
        ])
        embed.title = "😐 Beg - No Luck"
        embed.description = response
        embed.color = CONFIG["INFO_COLOR"]
    
    set_user_cooldown(user_id, "beg", current_time)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

# --- NEW EARNING/WORK ALTERNATIVES ---
@bot.command()
@commands.cooldown(1, CONFIG["SCAVENGE_COOLDOWN_SECONDS"], commands.BucketType.user)
async def scavenge(ctx):
    user_id = ctx.author.id
    current_time = int(time.time())
    
    roll = random.random()
    
    if roll < CONFIG["SCAVENGE_CASH_CHANCE"]:
        # Found cash
        pay = random.randint(CONFIG["SCAVENGE_MIN_CASH"], CONFIG["SCAVENGE_MAX_CASH"])
        net_earnings, total_cut = await process_earnings(ctx, user_id, pay)
        response = random.choice([
            f"You rummaged through some old bins and found **${pay:,}**!",
            f"You spotted a glint in the gutter and picked up **${pay:,}**.",
            f"A lost wallet! You found **${pay:,}** inside (and returned it, mostly).",
            f"While exploring an abandoned building, you stumbled upon **${pay:,}**."
        ])
        embed = discord.Embed(
            title="🔎 Scavenge Success!",
            description=f"{response} {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}",
            color=CONFIG["SUCCESS_COLOR"]
        )
    elif roll < (CONFIG["SCAVENGE_CASH_CHANCE"] + CONFIG["SCAVENGE_ITEM_CHANCE"]):
        # Found item
        item_found = random.choice(CONFIG["SCAVENGE_POSSIBLE_ITEMS"])
        add_item_to_inventory(user_id, item_found, 1)
        response = random.choice([
            f"You found a discarded **{item_found.capitalize()}**!",
            f"Beneath a pile of leaves, you discovered a **{item_found.capitalize()}**.",
            f"Your keen eyes spotted a shiny **{item_found.capitalize()}**."
        ])
        embed = discord.Embed(
            title="📦 Scavenge Success!",
            description=response,
            color=CONFIG["INFO_COLOR"]
        )
    else:
        # Found nothing
        response = random.choice([
            "You searched high and low, but found nothing.",
            "Just dust and cobwebs. Better luck next time.",
            "A suspicious squirrel glared at you, then ran off with your hopes.",
            "You found nothing, but stepped in something wet. Gross."
        ])
        embed = discord.Embed(
            title="💨 Scavenge - No Luck",
            description=response,
            color=CONFIG["DEFAULT_COLOR"]
        )
    
    set_user_cooldown(user_id, "scavenge", current_time)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["ADVENTURE_COOLDOWN_SECONDS"], commands.BucketType.user)
async def adventure(ctx):
    user_id = ctx.author.id
    current_time = int(time.time())

    roll = random.random()
    
    embed = discord.Embed(title="✨ Adventure Outcome", color=CONFIG["INFO_COLOR"])

    if roll < CONFIG["ADVENTURE_SUCCESS_CHANCE"]:
        # Good outcome
        outcome_type = random.choice(["cash", "item"])
        if outcome_type == "cash":
            payout = random.randint(CONFIG["ADVENTURE_MIN_SUCCESS_PAY"], CONFIG["ADVENTURE_MAX_SUCCESS_PAY"])
            net_earnings, total_cut = await process_earnings(ctx, user_id, payout)
            response = random.choice([
                f"You explored an ancient ruin and found a hidden treasure chest containing **${payout:,}**!",
                f"You successfully navigated a treacherous jungle and were rewarded **${payout:,}** by grateful villagers.",
                f"You helped a lost traveler find their way and received **${payout:,}** as a thank you."
            ])
            embed.title = "✨ Adventure Success!"
            embed.description = f"{response} {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}"
            embed.color = CONFIG["SUCCESS_COLOR"]
        else: # outcome_type == "item"
            item_found = random.choice(CONFIG["ADVENTURE_SUCCESS_ITEMS"])
            add_item_to_inventory(user_id, item_found, 1)
            response = random.choice([
                f"You ventured into a mystical cave and discovered a rare **{item_found.capitalize()}**!",
                f"After defeating a fearsome beast, you looted a sparkling **{item_found.capitalize()}**.",
                f"You found a magical portal that led you to a **{item_found.capitalize()}**."
            ])
            embed.title = "✨ Adventure Success!"
            embed.description = response
            embed.color = CONFIG["SUCCESS_COLOR"]
    elif roll < (CONFIG["ADVENTURE_SUCCESS_CHANCE"] + CONFIG["ADVENTURE_MEDIUM_CHANCE"]):
        # Neutral outcome
        response = random.choice([
            "You went on an adventure, but nothing particularly interesting happened.",
            "You bravely explored the unknown... and then safely returned home with no gains or losses.",
            "A long walk, a nice view, but no treasure in sight.",
            "Your adventure was uneventful. At least you didn't get lost!"
        ])
        embed.title = "🚶 Adventure - Neutral"
        embed.description = response
        embed.color = CONFIG["INFO_COLOR"]
    else:
        # Negative outcome
        loss = random.randint(CONFIG["ADVENTURE_MIN_RISK_LOSS"], CONFIG["ADVENTURE_MAX_RISK_LOSS"])
        update_user_money(user_id, cash_change=-loss) # Direct deduction
        response = random.choice([
            f"You were ambushed by goblins and lost **${loss:,}** cash!",
            f"During your expedition, you accidentally fell into a pit and dropped **${loss:,}**.",
            f"You got lost in a dark forest and had to pay **${loss:,}** to a guide to get back.",
            f"A rogue squirrel stole **${loss:,}** directly from your pocket!"
        ])
        embed.title = "💥 Adventure Gone Wrong!"
        embed.description = response
        embed.color = CONFIG["ERROR_COLOR"]
    
    set_user_cooldown(user_id, "adventure", current_time)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)


# --- NEW STOCK COMMANDS ---

@bot.command()
@commands.cooldown(1, CONFIG["MINE_COOLDOWN_SECONDS"], commands.BucketType.user)
async def mine(ctx):
    """
    Go mining for cash or valuable minerals.
    """
    user_id = ctx.author.id
    current_time = int(time.time())
    
    roll = random.random()
    
    if roll < CONFIG["MINE_CASH_CHANCE"]:
        # Found cash
        pay = random.randint(CONFIG["MINE_MIN_CASH"], CONFIG["MINE_MAX_CASH"])
        net_earnings, total_cut = await process_earnings(ctx, user_id, pay)
        response = random.choice([
            f"You struck a small vein of gold and found **${pay:,}**!",
            f"Your pickaxe hit something soft, revealing a pouch with **${pay:,}**.",
            f"After a hard swing, you uncovered a hidden stash of **${pay:,}** cash.",
            f"You found a lost miner's wallet containing **${pay:,}**."
        ])
        embed = discord.Embed(
            title="⛏️ Mining Success!",
            description=f"{response} {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}",
            color=CONFIG["SUCCESS_COLOR"]
        )
    elif roll < (CONFIG["MINE_CASH_CHANCE"] + CONFIG["MINE_ITEM_CHANCE"]):
        # Found item
        item_found = random.choice(CONFIG["MINE_POSSIBLE_ITEMS"])
        add_item_to_inventory(user_id, item_found, 1)
        response = random.choice([
            f"You chipped away at a rock face and unearthed a shiny **{item_found.capitalize()}**!",
            f"Deep within the mine, you discovered a rare **{item_found.capitalize()}**.",
            f"Your efforts paid off! You found a pristine **{item_found.capitalize()}**."
        ])
        embed = discord.Embed(
            title="💎 Mining Success!",
            description=response,
            color=CONFIG["INFO_COLOR"]
        )
    else:
        # Found nothing
        response = random.choice([
            "You swung your pickaxe tirelessly, but found nothing but dust.",
            "The mine was barren. Better luck next time.",
            "You found an old, rusty pickaxe, but nothing valuable.",
            "A cave-in almost occurred! You narrowly escaped with nothing."
        ])
        embed = discord.Embed(
            title="💨 Mining - No Luck",
            description=response,
            color=CONFIG["DEFAULT_COLOR"]
        )
    
    set_user_cooldown(user_id, "mine", current_time)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["FORAGE_COOLDOWN_SECONDS"], commands.BucketType.user)
async def forage(ctx):
    """
    Search for edible plants or hidden cash in the wilderness.
    """
    user_id = ctx.author.id
    current_time = int(time.time())

    roll = random.random()
    
    if roll < CONFIG["FORAGE_CASH_CHANCE"]:
        # Found cash
        pay = random.randint(CONFIG["FORAGE_MIN_CASH"], CONFIG["FORAGE_MAX_CASH"])
        net_earnings, total_cut = await process_earnings(ctx, user_id, pay)
        response = random.choice([
            f"While digging for roots, you unearthed a small bag of **${pay:,}**!",
            f"You stumbled upon a hidden bird's nest with **${pay:,}** neatly tucked inside.",
            f"You found a discarded map leading to **${pay:,}** buried under a tree.",
            f"A strange animal led you to a sparkling pile of **${pay:,}**."
        ])
        embed = discord.Embed(
            title="💰 Foraging Success!",
            description=f"{response} {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}",
            color=CONFIG["SUCCESS_COLOR"]
        )
    elif roll < (CONFIG["FORAGE_CASH_CHANCE"] + CONFIG["FORAGE_ITEM_CHANCE"]):
        # Found item
        item_found = random.choice(CONFIG["FORAGE_POSSIBLE_ITEMS"])
        add_item_to_inventory(user_id, item_found, 1)
        response = random.choice([
            f"You found a patch of ripe **{item_found.capitalize()}**!",
            f"Under a mossy log, you discovered a rare **{item_found.capitalize()}**.",
            f"Your sharp eyes spotted a valuable **{item_found.capitalize()}** growing nearby."
        ])
        embed = discord.Embed(
            title="🌿 Foraging Success!",
            description=response,
            color=CONFIG["INFO_COLOR"]
        )
    else:
        # Found nothing
        response = random.choice([
            "You scoured the forest floor, but found nothing edible or valuable.",
            "The forest was quiet, yielding no treasures today.",
            "You almost stepped on a snake! No money, just fright.",
            "Just a lot of leaves and dirt. Maybe try another spot."
        ])
        embed = discord.Embed(
            title="🍂 Foraging - No Luck",
            description=response,
            color=CONFIG["DEFAULT_COLOR"]
        )

    set_user_cooldown(user_id, "forage", current_time)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["INVEST_COOLDOWN_SECONDS"], commands.BucketType.user)
async def invest(ctx, member: discord.Member, amount: int):
    """
    Invest in another user to get a percentage cut of their future earnings.
    """
    user_id = ctx.author.id

    if member.bot:
        embed = discord.Embed(
            title="🤖 Cannot Invest",
            description="You cannot invest in a bot.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if member.id == user_id:
        embed = discord.Embed(
            title="🤦‍♂️ Self-Investment",
            description="You cannot invest in yourself.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="You must invest a positive amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    investor_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(user_id)
    if investor_cash < amount:
        embed = discord.Embed(
            title="💰 Insufficient Funds",
            description=f"You don't have **${amount:,}** cash to make this investment.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    # Check if user already invested in this member
    current_investments = get_user_investments(user_id)
    for investee_id, _ in current_investments:
        if investee_id == member.id:
            embed = discord.Embed(
                title="📈 Already Invested",
                description=f"You have already invested in {member.mention}. You can only have one active investment per person.",
                color=CONFIG["ERROR_COLOR"]
            )
            embed.set_footer(text="Made With 💖 By Harsizcool")
            await ctx.send(embed=embed)
            return

    update_user_money(user_id, cash_change=-amount)
    add_investment(user_id, member.id, amount)
    set_user_cooldown(user_id, "invest", int(time.time()))

    embed = discord.Embed(
        title="📈 Investment Made!",
        description=f"You successfully invested **${amount:,}** in {member.mention}.\n"
                    f"You will now receive a **{CONFIG['INVEST_CUT_PERCENTAGE'] * 100:.0f}%** cut from their future earnings!",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command(aliases=["lb"])
async def leaderboard(ctx):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, cash + bank AS total_money FROM users ORDER BY total_money DESC LIMIT ?', (CONFIG["MAX_LEADERBOARD_ENTRIES"],))
    top_users = cursor.fetchall()
    conn.close()

    if not top_users:
        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="No one is on the leaderboard yet! Start earning money!",
            color=CONFIG["INFO_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="🏆 Global Leaderboard",
        color=CONFIG["INFO_COLOR"]
    )

    description = ""
    for i, (user_id, total_money) in enumerate(top_users):
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)
        if user:
            description += f"**{i+1}.** {user.display_name} - **${total_money:,}**\n"
        else:
            description += f"**{i+1}.** Unknown User ({user_id}) - **${total_money:,}**\n"
    
    embed.description = description
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command(aliases=["with"])
async def withdraw(ctx, amount: str):
    user_id = ctx.author.id
    # Extended tuple unpacking for new cooldown columns
    cash, bank, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(user_id)

    if amount.lower() == "all":
        amount = bank
    else:
        try:
            amount = int(amount)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please provide a valid number or 'all'.",
                color=CONFIG["ERROR_COLOR"]
            )
            embed.set_footer(text="Made With 💖 By Harsizcool")
            await ctx.send(embed=embed)
            return

    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="You must withdraw a positive amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if amount > bank:
        embed = discord.Embed(
            title="🏦 Insufficient Funds",
            description="You don't have that much in your bank.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(user_id, cash_change=amount, bank_change=-amount)
    
    embed = discord.Embed(
        title="💸 Withdrawal Successful",
        description=f"You withdrew **${amount:,}** from your bank.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command(aliases=["dep"])
async def deposit(ctx, amount: str):
    user_id = ctx.author.id
    # Extended tuple unpacking for new cooldown columns
    cash, bank, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(user_id)

    if amount.lower() == "all":
        amount = cash
    else:
        try:
            amount = int(amount)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Amount",
                description="Please provide a valid number or 'all'.",
                color=CONFIG["ERROR_COLOR"]
            )
            embed.set_footer(text="Made With 💖 By Harsizcool")
            await ctx.send(embed=embed)
            return

    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="You must deposit a positive amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if amount > cash:
        embed = discord.Embed(
            title="💰 Insufficient Funds",
            description="You don't have that much cash.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(user_id, cash_change=-amount, bank_change=amount)
    
    embed = discord.Embed(
        title="🏦 Deposit Successful",
        description=f"You deposited **${amount:,}** into your bank.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command(aliases=["dn"])
async def donate(ctx, member: discord.Member, amount: int):
    if member.bot:
        embed = discord.Embed(
            title="🤖 Cannot Donate",
            description="You cannot donate to a bot.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if member.id == ctx.author.id:
        embed = discord.Embed(
            title="🤦‍♂️ Self-Donation",
            description="You cannot donate to yourself.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="You must donate a positive amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    sender_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)

    if amount > sender_cash:
        embed = discord.Embed(
            title="💰 Insufficient Funds",
            description="You don't have enough cash to donate that amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount)
    update_user_money(member.id, cash_change=amount)

    embed = discord.Embed(
        title="🎁 Donation Successful",
        description=f"You donated **${amount:,}** to {member.mention}.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["ROB_COOLDOWN_SECONDS"], commands.BucketType.user)
async def rob(ctx, member: discord.Member):
    if member.bot:
        embed = discord.Embed(
            title="🤖 Cannot Rob",
            description="You cannot rob a bot. They have no money anyway.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if member.id == ctx.author.id:
        embed = discord.Embed(
            title="🤦‍♂️ Self-Robbery",
            description="You cannot rob yourself, that's just moving money around.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    # Extended tuple unpacking for new cooldown columns
    target_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(member.id)
    if target_cash < 100:
        embed = discord.Embed(
            title="💸 Target Too Poor",
            description=f"{member.mention} is too broke to rob! They need at least $100 cash.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    current_time = int(time.time())
    set_user_cooldown(ctx.author.id, "rob", current_time)

    if random.random() < CONFIG["ROB_SUCCESS_CHANCE"]:
        stolen_percentage = random.uniform(CONFIG["ROB_MIN_STOLEN_PERCENT"], CONFIG["ROB_MAX_STOLEN_PERCENT"])
        stolen_amount = int(target_cash * stolen_percentage)
        stolen_amount = max(1, stolen_amount)

        update_user_money(ctx.author.id, cash_change=stolen_amount)
        update_user_money(member.id, cash_change=-stolen_amount)

        embed = discord.Embed(
            title="😈 Robbery Successful!",
            description=f"You successfully robbed **${stolen_amount:,}** from {member.mention}!",
            color=CONFIG["SUCCESS_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
    else:
        fine_amount = int(target_cash * random.uniform(0.05, 0.15))
        fine_amount = max(1, fine_amount)
        current_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
        
        if current_cash < fine_amount:
            fine_amount = current_cash

        update_user_money(ctx.author.id, cash_change=-fine_amount)
        
        embed = discord.Embed(
            title="🚓 Robbery Failed!",
            description=f"You tried to rob {member.mention} but failed! You lost **${fine_amount:,}** cash in the process.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)

# --- ITEM & LISTING COMMANDS ---

@bot.command()
async def inventory(ctx, member: discord.Member = None):
    target = member or ctx.author
    items = get_user_inventory(target.id)

    embed = discord.Embed(
        title=f"{target.display_name}'s Inventory",
        color=CONFIG["INFO_COLOR"]
    )

    if not items:
        embed.description = "This user has no items in their inventory."
    else:
        description = ""
        for item_name, quantity in items:
            description += f"• **{item_name.capitalize()}**: {quantity}\n"
        embed.description = description
    
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def itemcreate(ctx, name: str, quantity: int, sellingprice: int):
    if sellingprice <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Price",
            description="Selling price must be a positive number.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    if quantity <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Quantity",
            description="Quantity must be a positive number.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    name = name.lower()

    listing_id = add_listing(ctx.author.id, name, quantity, sellingprice, is_custom=True)

    embed = discord.Embed(
        title="🌟 Custom Item Created!",
        description=f"You've created a custom item listing: **{quantity}x {name.capitalize()}** for **${sellingprice:,}** each (Listing ID: `{listing_id}`).\n"
                    "It's now available on the market!",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command(aliases=["cl", "listings"])
async def currentlistings(ctx):
    listings = get_listings()

    embed = discord.Embed(
        title="🛒 Current Market Listings",
        color=CONFIG["INFO_COLOR"]
    )

    if not listings:
        embed.description = "No items are currently listed on the market."
    else:
        description = ""
        for listing_id, seller_id, item_name, quantity, price_per_item, is_custom in listings:
            seller = bot.get_user(seller_id) or await bot.fetch_user(seller_id)
            seller_name = seller.display_name if seller else f"Unknown ({seller_id})"
            custom_tag = "🌟" if is_custom else ""
            description += (f"**ID: {listing_id}** | **{item_name.capitalize()}** {custom_tag}\n"
                            f"  Quantity: {quantity} | Price/item: ${price_per_item:,}\n"
                            f"  Seller: {seller_name}\n\n")
        
        embed.description = description
    
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, listing_id: int, amount: int = 1):
    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="You must buy a positive quantity.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    listing = get_listing_by_id(listing_id)

    if not listing:
        embed = discord.Embed(
            title="❌ Listing Not Found",
            description=f"No listing found with ID `{listing_id}`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    l_id, seller_id, item_name, available_quantity, price_per_item, is_custom = listing

    if ctx.author.id == seller_id:
        embed = discord.Embed(
            title="🚫 Cannot Buy Own Item",
            description="You cannot buy your own listings.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if amount > available_quantity:
        embed = discord.Embed(
            title="📉 Insufficient Stock",
            description=f"There are only {available_quantity} of **{item_name.capitalize()}** available.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    total_cost = amount * price_per_item
    # Extended tuple unpacking for new cooldown columns
    buyer_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)

    if buyer_cash < total_cost:
        embed = discord.Embed(
            title="💰 Insufficient Funds",
            description=f"You need **${total_cost:,}** but you only have **${buyer_cash:,}** cash.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-total_cost)
    update_user_money(seller_id, cash_change=total_cost)
    add_item_to_inventory(ctx.author.id, item_name, amount)

    new_quantity = available_quantity - amount
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    if new_quantity <= 0:
        cursor.execute('DELETE FROM listings WHERE listing_id = ?', (listing_id,))
    else:
        cursor.execute('UPDATE listings SET quantity = ? WHERE listing_id = ?', (new_quantity, listing_id))
    conn.commit()
    conn.close()

    seller_member = bot.get_user(seller_id) or await bot.fetch_user(seller_id)
    seller_mention = seller_member.mention if seller_member else f"a user with ID `{seller_id}`"

    embed = discord.Embed(
        title="✅ Purchase Successful!",
        description=f"You bought **{amount} {item_name.capitalize()}** for **${total_cost:,}** from {seller_mention}.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def sell(ctx, item_name: str, amount: int, price_per_item: int):
    item_name = item_name.lower()
    if amount <= 0 or price_per_item <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount/Price",
            description="Quantity and price per item must be positive numbers.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT quantity FROM inventory WHERE user_id = ? AND item_name = ?', (ctx.author.id, item_name))
    inventory_quantity_row = cursor.fetchone()
    inventory_quantity = inventory_quantity_row[0] if inventory_quantity_row else 0
    conn.close()

    if not inventory_quantity_row or inventory_quantity < amount:
        embed = discord.Embed(
            title="📦 Insufficient Items",
            description=f"You don't have {amount} of **{item_name.capitalize()}** to sell. You have {inventory_quantity}.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    remove_item_from_inventory(ctx.author.id, item_name, amount)

    listing_id = add_listing(ctx.author.id, item_name, amount, price_per_item, is_custom=False)

    embed = discord.Embed(
        title="📈 Item Listed!",
        description=f"You listed **{amount} {item_name.capitalize()}** for **${price_per_item:,}** each (total: **${amount * price_per_item:,}**) on the market.\n"
                    f"Your listing ID is `{listing_id}`.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def use(ctx, *, item_name: str):
    item_name = item_name.lower()
    user_id = ctx.author.id

    if not remove_item_from_inventory(user_id, item_name, 1):
        embed = discord.Embed(
            title="🚫 Item Not Found",
            description=f"You don't have **{item_name.capitalize()}** in your inventory.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    item_data = CONFIG["USABLE_ITEMS"].get(item_name)
    
    response_description = f"You used **{item_name.capitalize()}**."
    response_color = CONFIG["INFO_COLOR"]
    pay_or_loss = 0

    if item_data:
        effect = item_data.get("effect")
        if effect == "cash_boost":
            pay_or_loss = item_data.get("amount", 0)
            net_earnings, total_cut = await process_earnings(ctx, user_id, pay_or_loss)
            response_description += f" It granted you **${pay_or_loss:,}** cash! {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}"
            response_color = CONFIG["SUCCESS_COLOR"]
        elif effect == "random_item_or_cash":
            outcome_roll = random.random()
            if outcome_roll < 0.5:
                pay_or_loss = random.randint(500, 1500)
                net_earnings, total_cut = await process_earnings(ctx, user_id, pay_or_loss)
                response_description += f" It contained **${pay_or_loss:,}** cash! {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}"
                response_color = CONFIG["SUCCESS_COLOR"]
            else:
                possible_items = ["trash", "gem", "potion"]
                random_new_item = random.choice(possible_items)
                add_item_to_inventory(user_id, random_new_item, 1)
                response_description += f" It contained a **{random_new_item.capitalize()}**!"
                response_color = CONFIG["INFO_COLOR"]
        elif effect == "none":
            response_description += " Nothing happened. It was useless."
            response_color = CONFIG["DEFAULT_COLOR"]
        elif effect == "high_value":
            response_description += " It glittered brightly. Perhaps it's for crafting or selling?"
            response_color = CONFIG["INFO_COLOR"]
        else:
            response_description += " But nothing specific happened. (Undefined effect)"
    else:
        response_description += " But it doesn't seem to have any special effect. Perhaps it's a decorative item or a custom item with no defined use."
        response_color = CONFIG["DEFAULT_COLOR"]

    embed = discord.Embed(
        title="✨ Item Used!",
        description=response_description,
        color=response_color
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def giveitem(ctx, member: discord.Member, item_name: str, amount: int = 1):
    item_name = item_name.lower()
    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="You must give a positive quantity.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if member.id == ctx.author.id:
        embed = discord.Embed(
            title="🤦‍♂️ Self-Give",
            description="You cannot give items to yourself. They're already in your inventory!",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    if not remove_item_from_inventory(ctx.author.id, item_name, amount):
        embed = discord.Embed(
            title="📦 Insufficient Items",
            description=f"You don't have {amount} of **{item_name.capitalize()}** to give.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    add_item_to_inventory(member.id, item_name, amount)

    embed = discord.Embed(
        title="🤝 Item Gifted!",
        description=f"You gave **{amount} {item_name.capitalize()}** to {member.mention}.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def iteminfo(ctx, *, item_name: str):
    item_name = item_name.lower()
    
    predefined_info = CONFIG["USABLE_ITEMS"].get(item_name)
    
    crafting_as_ingredient = False
    for recipe_name, recipe_data in CONFIG["CRAFTING_RECIPES"].items():
        if item_name in recipe_data["ingredients"]:
            crafting_as_ingredient = True
            break

    craftable_item_info = CONFIG["CRAFTING_RECIPES"].get(item_name)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT price_per_item FROM listings WHERE item_name = ? AND is_custom = 1 LIMIT 1', (item_name,))
    custom_item_data = cursor.fetchone()
    conn.close()

    embed = discord.Embed(
        title=f"📦 Item Info: {item_name.capitalize()}",
        color=CONFIG["INFO_COLOR"]
    )

    found_info = False
    
    if predefined_info:
        embed.add_field(name="Type", value="Predefined Item", inline=True)
        embed.add_field(name="Description", value=predefined_info.get("description", "No description available."), inline=False)
        if predefined_info.get("effect") == "cash_boost":
            embed.add_field(name="Effect", value=f"Grants ${predefined_info.get('amount'):,} cash upon use.", inline=True)
        elif predefined_info.get("effect") == "random_item_or_cash":
            embed.add_field(name="Effect", value="Gives a random item or cash upon use.", inline=True)
        elif predefined_info.get("effect") == "none":
            embed.add_field(name="Effect", value="No special effect upon use.", inline=True)
        else:
            embed.add_field(name="Effect", value=predefined_info.get("effect").replace('_', ' ').capitalize(), inline=True)
        found_info = True
    
    if craftable_item_info:
        ingredients_str = "\n".join([f"- {qty}x {ing.capitalize()}" for ing, qty in craftable_item_info["ingredients"].items()])
        embed.add_field(name="Crafting Recipe", value=f"To craft:\n{ingredients_str}\n\nResult: {list(craftable_item_info['result'].values())[0]}x {item_name.capitalize()}", inline=False)
        if not found_info:
            embed.add_field(name="Description", value=craftable_item_info.get("description", "No description for this craftable item."), inline=False)
        found_info = True
    elif crafting_as_ingredient and not found_info:
        embed.add_field(name="Crafting Role", value="Can be used as an ingredient in crafting recipes.", inline=False)
        found_info = True

    if custom_item_data:
        if not found_info:
            embed.add_field(name="Type", value="Custom Item 🌟", inline=True)
            embed.add_field(name="Description", value="A custom item created by a user.", inline=False)
        embed.add_field(name="Last Listed Price (Custom)", value=f"${custom_item_data[0]:,}", inline=True)
        found_info = True
    
    if not found_info:
        embed.description = "No specific information found for this item. It might be a generic item or simply not defined."
        embed.color = CONFIG["ERROR_COLOR"]
        
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def craft(ctx, *, recipe_name: str):
    recipe_name = recipe_name.lower()
    recipe = CONFIG["CRAFTING_RECIPES"].get(recipe_name)

    if not recipe:
        embed = discord.Embed(
            title="❌ Recipe Not Found",
            description=f"No crafting recipe found for `{recipe_name.capitalize()}`. Check available recipes with `>help craft`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_id = ctx.author.id
    user_inventory = get_user_inventory(user_id)
    user_items = {item[0]: item[1] for item in user_inventory}

    can_craft = True
    missing_ingredients = []
    for ingredient, required_qty in recipe["ingredients"].items():
        if user_items.get(ingredient, 0) < required_qty:
            can_craft = False
            missing_ingredients.append(f"{required_qty}x {ingredient.capitalize()} (You have {user_items.get(ingredient, 0)})")
    
    if not can_craft:
        embed = discord.Embed(
            title="📦 Cannot Craft",
            description=f"You are missing the following ingredients for **{recipe_name.capitalize()}**:\n" + "\n".join(missing_ingredients),
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    for ingredient, required_qty in recipe["ingredients"].items():
        remove_item_from_inventory(user_id, ingredient, required_qty)
    
    result_item, result_qty = list(recipe["result"].items())[0]
    add_item_to_inventory(user_id, result_item, result_qty)

    embed = discord.Embed(
        title="🔨 Crafting Successful!",
        description=f"You successfully crafted **{result_qty}x {result_item.capitalize()}** using the `{recipe_name.capitalize()}` recipe!",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

# --- GAMBLING COMMANDS ---

@bot.command(aliases=["bj"])
async def blackjack(ctx, amount: int):
    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Bet",
            description="You must bet a positive amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(
            title="💰 Insufficient Funds",
            description=f"You don't have **${amount:,}** cash to bet.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    def calculate_hand(hand):
        value = sum(hand)
        num_aces = hand.count(11)
        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1
        return value

    def deal_card():
        return random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])
    
    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront

    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]

    player_score = calculate_hand(player_hand)
    dealer_score = calculate_hand(dealer_hand)

    embed = discord.Embed(
        title="♠️♥️ Blackjack",
        description=f"Your Hand: {player_hand} (Score: {player_score})\n"
                    f"Dealer Hand: [{dealer_hand[0]}, ?]",
        color=CONFIG["INFO_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    msg = await ctx.send(embed=embed)

    while player_score < 21:
        embed.description = (f"Your Hand: {player_hand} (Score: {player_score})\n"
                             f"Dealer Hand: [{dealer_hand[0]}, ?]\n\n"
                             "Type `hit` to get another card or `stand` to finish.")
        embed.color = CONFIG["INFO_COLOR"]
        await msg.edit(embed=embed)

        try:
            choice_msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['hit', 'stand'], timeout=30.0)
            choice = choice_msg.content.lower()
            # It's generally good practice to delete the user's command response if it's part of a game interaction
            try:
                await choice_msg.delete()
            except discord.Forbidden:
                pass # Bot doesn't have permissions to delete messages
            except discord.HTTPException:
                pass # Message already deleted or other error
        except asyncio.TimeoutError:
            embed.description = "Time's up! You stood automatically."
            embed.color = CONFIG["ERROR_COLOR"]
            await msg.edit(embed=embed)
            choice = "stand"

        if choice == 'hit':
            new_card = deal_card()
            player_hand.append(new_card)
            player_score = calculate_hand(player_hand)
        else:
            break

    while dealer_score < 17:
        dealer_hand.append(deal_card())
        dealer_score = calculate_hand(dealer_hand)
    
    result_embed = discord.Embed(
        title="♠️♥️ Blackjack - Results",
        color=CONFIG["INFO_COLOR"]
    )
    result_embed.add_field(name="Your Hand", value=f"{player_hand} (Score: {player_score})", inline=False)
    result_embed.add_field(name="Dealer Hand", value=f"{dealer_hand} (Score: {dealer_score})", inline=False)

    win = False
    if player_score > 21:
        result_embed.description = "You busted! You lose."
        result_embed.color = CONFIG["ERROR_COLOR"]
    elif dealer_score > 21:
        result_embed.description = "Dealer busted! You win!"
        result_embed.color = CONFIG["SUCCESS_COLOR"]
        win = True
    elif player_score == dealer_score:
        result_embed.description = "It's a push! Your money is returned."
        result_embed.color = CONFIG["INFO_COLOR"]
        update_user_money(ctx.author.id, cash_change=amount)
    elif player_score > dealer_score:
        result_embed.description = "You win!"
        result_embed.color = CONFIG["SUCCESS_COLOR"]
        win = True
    else:
        result_embed.description = "You lose!"
        result_embed.color = CONFIG["ERROR_COLOR"]
    
    if win:
        payout = amount * CONFIG["BLACKJACK_WIN_MULTIPLIER"]
        update_user_money(ctx.author.id, cash_change=payout)
        result_embed.add_field(name="Payout", value=f"You won **${payout:,}**!", inline=False)
    elif player_score <= 21 and player_score == dealer_score:
        result_embed.add_field(name="Payout", value=f"You kept your **${amount:,}** bet.", inline=False)
    else:
        result_embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)

    result_embed.set_footer(text="Made With 💖 By Harsizcool")
    await msg.edit(embed=result_embed)

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)  # 1 use every 60 seconds per user
async def coinflip(ctx, choice: str, amount: int):
    choice = choice.lower()
    if choice not in ['heads', 'tails', 'h', 't']:
        embed = discord.Embed(
            title="🚫 Invalid Choice",
            description="Please choose 'heads' or 'tails'.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Bet",
            description="You must bet a positive amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(
            title="💰 Insufficient Funds",
            description=f"You don't have **${amount:,}** cash to bet.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    coin_result = random.choice(['heads', 'tails'])

    embed = discord.Embed(title="🪙 Coin Flip")
    embed.add_field(name="Your Choice", value=f"`{choice.capitalize()}` for **${amount:,}**", inline=False)
    embed.add_field(name="Coin Result", value=f"The coin landed on... **{coin_result.capitalize()}!**", inline=False)

    win = (choice[0] == coin_result[0])

    if win:
        payout = int(amount * CONFIG["COINFLIP_WIN_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=payout)
        embed.description = "🎉 You won!"
        embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
        embed.color = CONFIG["SUCCESS_COLOR"]
    else:
        update_user_money(ctx.author.id, cash_change=-amount)
        embed.description = "😞 You lost!"
        embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
        embed.color = CONFIG["ERROR_COLOR"]

    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

# Error handler for cooldowns
@coinflip.error
async def coinflip_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        retry = round(error.retry_after, 1)
        embed = discord.Embed(
            title="⏳ Chill!",
            description=f"You're flipping too fast. Try again in `{retry}` seconds.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)

# --- NEW 5 GAMBLING COMMANDS ---
@bot.command()
@commands.cooldown(1, CONFIG["ROULETTE_COOLDOWN_SECONDS"], commands.BucketType.user)
async def roulette(ctx, amount: int, *, bet_type: str):
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    bet_type = bet_type.lower()
    
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

    winning_number = random.randint(0, 36)
    result_color = "Green" if winning_number == 0 else ("Red" if winning_number in red_numbers else "Black")
    result_parity = "Even" if winning_number % 2 == 0 and winning_number != 0 else "Odd" if winning_number != 0 else "N/A (Green)"
    result_range = "Low (1-18)" if 1 <= winning_number <= 18 else "High (19-36)" if 19 <= winning_number <= 36 else "N/A (Green)"

    win = False
    payout_multiplier = 0
    bet_info = ""

    if bet_type in ["red", "black"]:
        bet_info = f"Color: {bet_type.capitalize()}"
        if winning_number != 0 and bet_type == result_color.lower():
            win = True
            payout_multiplier = CONFIG["ROULETTE_COLOR_ODD_EVEN_HIGH_LOW_MULTIPLIER"]
    elif bet_type in ["odd", "even"]:
        bet_info = f"Parity: {bet_type.capitalize()}"
        if winning_number != 0 and bet_type == result_parity.lower():
            win = True
            payout_multiplier = CONFIG["ROULETTE_COLOR_ODD_EVEN_HIGH_LOW_MULTIPLIER"]
    elif bet_type in ["low", "high", "1-18", "19-36"]:
        bet_info = f"Range: {bet_type.capitalize()}"
        if winning_number != 0:
            if (bet_type == "low" or bet_type == "1-18") and 1 <= winning_number <= 18:
                win = True
                payout_multiplier = CONFIG["ROULETTE_COLOR_ODD_EVEN_HIGH_LOW_MULTIPLIER"]
            elif (bet_type == "high" or bet_type == "19-36") and 19 <= winning_number <= 36:
                win = True
                payout_multiplier = CONFIG["ROULETTE_COLOR_ODD_EVEN_HIGH_LOW_MULTIPLIER"]
    elif bet_type.isdigit() and 0 <= int(bet_type) <= 36:
        chosen_number = int(bet_type)
        bet_info = f"Number: {chosen_number}"
        if winning_number == chosen_number:
            win = True
            payout_multiplier = CONFIG["ROULETTE_SINGLE_NUMBER_MULTIPLIER"]
    else:
        embed = discord.Embed(
            title="❌ Invalid Bet Type",
            description="Valid bets: `red`, `black`, `odd`, `even`, `low` (1-18), `high` (19-36), or a specific number (0-36).",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront

    result_embed = discord.Embed(title="🎡 Roulette Spin!", color=CONFIG["INFO_COLOR"])
    result_embed.add_field(name="Your Bet", value=f"`{bet_info}` for **${amount:,}**", inline=False)
    result_embed.add_field(name="Result", value=f"The ball landed on: **{winning_number}** ({result_color}, {result_parity}, {result_range})", inline=False)

    if win:
        payout = amount * payout_multiplier
        update_user_money(ctx.author.id, cash_change=payout)
        result_embed.description = "🎉 You won!"
        result_embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
        result_embed.color = CONFIG["SUCCESS_COLOR"]
    else:
        result_embed.description = "😞 You lost!"
        result_embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
        result_embed.color = CONFIG["ERROR_COLOR"]

    result_embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=result_embed)

@bot.command()
@commands.cooldown(1, CONFIG["DICEROLL_COOLDOWN_SECONDS"], commands.BucketType.user)
async def diceroll(ctx, amount: int, bet_type: str):
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    bet_type = bet_type.lower()
    valid_bets = ['high', 'low', '7']

    if bet_type not in valid_bets:
        embed = discord.Embed(title="❌ Invalid Bet Type", description="Please choose `high` (7-12), `low` (2-6), or `7` (exactly 7).", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront

    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    total_roll = dice1 + dice2

    win = False
    payout_multiplier = 0

    if bet_type == 'high':
        if 7 <= total_roll <= 12 and total_roll != 7: # High includes 8,9,10,11,12 but not 7 for this specific bet
            win = True
            payout_multiplier = CONFIG["DICEROLL_HIGHLOW_MULTIPLIER"]
    elif bet_type == 'low':
        if 2 <= total_roll <= 6:
            win = True
            payout_multiplier = CONFIG["DICEROLL_HIGHLOW_MULTIPLIER"]
    elif bet_type == '7':
        if total_roll == 7:
            win = True
            payout_multiplier = CONFIG["DICEROLL_SEVEN_MULTIPLIER"]

    result_embed = discord.Embed(title="🎲 Dice Roll!", color=CONFIG["INFO_COLOR"])
    result_embed.add_field(name="Your Bet", value=f"`{bet_type.capitalize()}` for **${amount:,}**", inline=False)
    result_embed.add_field(name="Result", value=f"You rolled **{dice1}** and **{dice2}** for a total of **{total_roll}**!", inline=False)

    if win:
        payout = amount * payout_multiplier
        update_user_money(ctx.author.id, cash_change=payout)
        result_embed.description = "🎉 You won!"
        result_embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
        result_embed.color = CONFIG["SUCCESS_COLOR"]
    else:
        result_embed.description = "😞 You lost!"
        result_embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
        result_embed.color = CONFIG["ERROR_COLOR"]

    result_embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=result_embed)

@bot.command()
@commands.cooldown(1, CONFIG["SLOTS_COOLDOWN_SECONDS"], commands.BucketType.user)
async def slots(ctx, amount: int):
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront

    # Spin reels based on weights
    reel = random.choices(CONFIG["SLOTS_SYMBOLS"], weights=CONFIG["SLOTS_WEIGHTS"], k=3)
    
    payout_multiplier = 0
    outcome_text = ""

    # Check for specific payouts
    if reel[0] == reel[1] == reel[2]: # All three match
        payout_multiplier = CONFIG["SLOTS_PAYOUTS"].get(tuple(reel), 0)
        if payout_multiplier > 0:
            outcome_text = f"Triple {reel[0]}! You hit a big one!"
    elif reel.count("7️⃣") == 2: # Two 7s + any other
        # Check all possible two 7s combinations for wildcard
        if ("7️⃣", "7️⃣", "*") in CONFIG["SLOTS_PAYOUTS"] and ((reel[0] == "7️⃣" and reel[1] == "7️⃣") or \
                                                            (reel[0] == "7️⃣" and reel[2] == "7️⃣") or \
                                                            (reel[1] == "7️⃣" and reel[2] == "7️⃣")):
            payout_multiplier = CONFIG["SLOTS_PAYOUTS"].get(("7️⃣", "7️⃣", "*"), 0)
            outcome_text = "Two 7️⃣s! Almost a jackpot!"
    
    if payout_multiplier > 0:
        payout = int(amount * payout_multiplier)
        update_user_money(ctx.author.id, cash_change=payout)
        description = f"🎉 You won **${payout:,}**!"
        color = CONFIG["SUCCESS_COLOR"]
    else:
        payout = int(amount * CONFIG["SLOTS_LOSE_MULTIPLIER"]) # Return a portion of the bet
        update_user_money(ctx.author.id, cash_change=payout)
        description = f"😔 You lost, but got **${payout:,}** back."
        color = CONFIG["ERROR_COLOR"] # Still a loss overall, so error color
        outcome_text = outcome_text if outcome_text else "No matching symbols." # Override if specific condition was met
        
    embed = discord.Embed(
        title="🎰 Slots!",
        description=f"Spinning the reels for **${amount:,}**...",
        color=CONFIG["INFO_COLOR"]
    )
    embed.add_field(name="Result", value=f"**{reel[0]} | {reel[1]} | {reel[2]}**", inline=False)
    embed.add_field(name="Outcome", value=outcome_text if outcome_text else "Better luck next time!", inline=False)
    embed.add_field(name="Net Change", value=description, inline=False)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["RPS_COOLDOWN_SECONDS"], commands.BucketType.user)
async def rps(ctx, amount: int, choice: str):
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    player_choice = choice.lower()
    valid_choices = ['rock', 'paper', 'scissors']

    if player_choice not in valid_choices:
        embed = discord.Embed(title="❌ Invalid Choice", description="Please choose `rock`, `paper`, or `scissors`.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    bot_choice = random.choice(valid_choices)

    result_text = ""
    win = False
    tie = False

    if player_choice == bot_choice:
        result_text = "It's a tie!"
        tie = True
    elif (player_choice == 'rock' and bot_choice == 'scissors') or \
         (player_choice == 'paper' and bot_choice == 'rock') or \
         (player_choice == 'scissors' and bot_choice == 'paper'):
        result_text = "You win!"
        win = True
    else:
        result_text = "You lose!"
    
    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront

    embed = discord.Embed(title="✊✋✌️ Rock Paper Scissors!")
    embed.add_field(name="Your Choice", value=f"`{player_choice.capitalize()}`", inline=True)
    embed.add_field(name="Bot's Choice", value=f"`{bot_choice.capitalize()}`", inline=True)
    embed.add_field(name="Result", value=result_text, inline=False)

    if win:
        payout = int(amount * CONFIG["RPS_WIN_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=payout)
        embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
        embed.color = CONFIG["SUCCESS_COLOR"]
    elif tie:
        update_user_money(ctx.author.id, cash_change=amount) # Return bet
        embed.add_field(name="Payout", value=f"You got your **${amount:,}** back.", inline=False)
        embed.color = CONFIG["INFO_COLOR"]
    else:
        embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
        embed.color = CONFIG["ERROR_COLOR"]

    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["GUESS_COOLDOWN_SECONDS"], commands.BucketType.user)
async def guess(ctx, amount: int, guess_number: int):
    min_num, max_num = CONFIG["GUESS_RANGE"]
    
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if not (min_num <= guess_number <= max_num):
        embed = discord.Embed(title="❌ Invalid Guess", description=f"Your guess must be between {min_num} and {max_num}.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront

    target_number = random.randint(min_num, max_num)
    
    win = False
    if guess_number == target_number:
        win = True

    embed = discord.Embed(title="🤔 Guess The Number!")
    embed.add_field(name="Your Guess", value=f"`{guess_number}` for **${amount:,}**", inline=False)
    embed.add_field(name="The Number Was...", value=f"**{target_number}**!", inline=False)

    if win:
        payout = int(amount * CONFIG["GUESS_WIN_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=payout)
        embed.description = "🎉 You guessed correctly and won!"
        embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
        embed.color = CONFIG["SUCCESS_COLOR"]
    else:
        embed.description = "😞 Your guess was incorrect."
        embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
        embed.color = CONFIG["ERROR_COLOR"]

    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

# --- NEW GAMBLING COMMANDS ---
@bot.command()
@commands.cooldown(1, CONFIG["HIGHLOWER_COOLDOWN_SECONDS"], commands.BucketType.user)
async def highlow(ctx, amount: int, guess: str):
    """
    Bet whether the next card will be higher or lower than the current card.
    """
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    guess = guess.lower()
    if guess not in ["higher", "lower", "h", "l"]:
        embed = discord.Embed(title="❌ Invalid Guess", description="Your guess must be `higher` or `lower`.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront
    set_user_cooldown(ctx.author.id, "highlow", int(time.time()))

    card_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    card_values = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, '10':10, 'J':11, 'Q':12, 'K':13}

    first_card_rank = random.choice(card_ranks)
    first_card_value = card_values[first_card_rank]

    second_card_rank = random.choice(card_ranks)
    second_card_value = card_values[second_card_rank]

    win = False
    result_text = ""
    if second_card_value > first_card_value and (guess == 'higher' or guess == 'h'):
        win = True
        result_text = "The next card was higher! You win!"
    elif second_card_value < first_card_value and (guess == 'lower' or guess == 'l'):
        win = True
        result_text = "The next card was lower! You win!"
    elif second_card_value == first_card_value:
        result_text = "It's a tie! Your money is returned."
        update_user_money(ctx.author.id, cash_change=amount) # Return bet
    else:
        result_text = "You lost!"

    embed = discord.Embed(title="🃏 Higher or Lower?", color=CONFIG["INFO_COLOR"])
    embed.add_field(name="First Card", value=f"`{first_card_rank}`", inline=True)
    embed.add_field(name="Your Guess", value=f"`{guess.capitalize()}`", inline=True)
    embed.add_field(name="Next Card", value=f"`{second_card_rank}`", inline=True)
    embed.add_field(name="Result", value=result_text, inline=False)

    if win:
        payout = int(amount * CONFIG["HIGHLOWER_WIN_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=payout)
        embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
        embed.color = CONFIG["SUCCESS_COLOR"]
    elif not win and second_card_value != first_card_value: # Not a win and not a tie
        embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
        embed.color = CONFIG["ERROR_COLOR"]
    
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, CONFIG["SCRATCH_COOLDOWN_SECONDS"], commands.BucketType.user)
async def scratch(ctx, amount: int):
    """
    Buy a scratch card for a chance at a big win!
    """
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to buy a scratch card.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront
    set_user_cooldown(ctx.author.id, "scratch", int(time.time()))

    win_chance = random.random()
    result_embed = discord.Embed(title="🎟️ Scratch Card!", color=CONFIG["INFO_COLOR"])

    if win_chance < CONFIG["SCRATCH_WIN_CHANCE"]:
        payout = int(amount * CONFIG["SCRATCH_WIN_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=payout)
        
        result_embed.description = f"🎉 You scratched the card and won **${payout:,}**!"
        result_embed.color = CONFIG["SUCCESS_COLOR"]
        result_embed.add_field(name="Net Change", value=f"+${payout - amount:,}", inline=False)
    else:
        refund = int(amount * CONFIG["SCRATCH_LOSE_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=refund)
        
        result_embed.description = f"😞 You scratched the card, but it wasn't a winner. You got **${refund:,}** back."
        result_embed.color = CONFIG["ERROR_COLOR"]
        result_embed.add_field(name="Net Change", value=f"-${amount - refund:,}", inline=False)
    
    result_embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=result_embed)

@bot.command()
@commands.cooldown(1, CONFIG["TRIVIA_COOLDOWN_SECONDS"], commands.BucketType.user)
async def trivia(ctx, amount: int):
    """
    Answer a trivia question to win money!
    """
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront
    set_user_cooldown(ctx.author.id, "trivia", int(time.time()))

    question_data = random.choice(CONFIG["TRIVIA_QUESTIONS"])
    question, correct_answers, wrong_answers, difficulty = question_data

    # Ensure there are enough wrong answers to pick 2
    num_wrong_to_pick = min(2, len(wrong_answers))
    all_answers_options = [ans.capitalize() for ans in correct_answers[:1]] + \
                          [ans.capitalize() for ans in random.sample(wrong_answers, num_wrong_to_pick)]
    random.shuffle(all_answers_options)
    
    answer_options_str = "\n".join([f"• {ans}" for ans in all_answers_options])

    trivia_embed = discord.Embed(
        title="🧠 Trivia Challenge!",
        description=f"You bet **${amount:,}** to play.\n\n**Question**: {question}\n\n**Difficulty**: {difficulty}\n\n"
                    f"Type your answer within 30 seconds!\n\nOptions (not necessarily all): \n{answer_options_str}",
        color=CONFIG["INFO_COLOR"]
    )
    trivia_embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=trivia_embed)

    try:
        response_msg = await bot.wait_for('message', 
                                         check=lambda m: m.author == ctx.author and m.channel == ctx.channel, 
                                         timeout=30.0)
        player_answer = response_msg.content.lower()

        if player_answer in [ans.lower() for ans in correct_answers]:
            payout = int(amount * CONFIG["TRIVIA_WIN_MULTIPLIER"])
            update_user_money(ctx.author.id, cash_change=payout)
            result_embed = discord.Embed(
                title="✅ Correct Answer!",
                description=f"You got it right! The answer was `{correct_answers[0].capitalize()}`.\n"
                            f"You won **${payout:,}**!",
                color=CONFIG["SUCCESS_COLOR"]
            )
            result_embed.set_footer(text="Made With 💖 By Harsizcool")
            await ctx.send(embed=result_embed)
        else:
            result_embed = discord.Embed(
                title="❌ Incorrect Answer!",
                description=f"That's not it. The correct answer was `{correct_answers[0].capitalize()}`.\n"
                            f"You lost **${amount:,}**.",
                color=CONFIG["ERROR_COLOR"]
            )
            result_embed.set_footer(text="Made With 💖 By Harsizcool")
            await ctx.send(embed=result_embed)

    except asyncio.TimeoutError:
        result_embed = discord.Embed(
            title="⏰ Time's Up!",
            description=f"You ran out of time! The correct answer was `{correct_answers[0].capitalize()}`.\n"
                        f"You lost **${amount:,}**.",
            color=CONFIG["ERROR_COLOR"]
        )
        result_embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=result_embed)

@bot.command()
@commands.cooldown(1, CONFIG["WAR_COOLDOWN_SECONDS"], commands.BucketType.user)
async def war(ctx, amount: int):
    """
    Play a card game of War against the bot. Higher card wins.
    """
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront
    set_user_cooldown(ctx.author.id, "war", int(time.time()))

    card_ranks_display = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
    card_values = list(range(2, 15)) # 2-14 for Ace

    player_card_value = random.choice(card_values)
    bot_card_value = random.choice(card_values)

    player_card_display = card_ranks_display[card_values.index(player_card_value)]
    bot_card_display = card_ranks_display[card_values.index(bot_card_value)]

    embed = discord.Embed(title="⚔️ Card War!", color=CONFIG["INFO_COLOR"])
    embed.add_field(name="Your Card", value=f"🃏 {player_card_display}", inline=True)
    embed.add_field(name="Bot's Card", value=f"🤖 {bot_card_display}", inline=True)

    win = False
    result_text = ""
    if player_card_value > bot_card_value:
        win = True
        result_text = "Your card is higher! You win!"
        embed.color = CONFIG["SUCCESS_COLOR"]
    elif player_card_value < bot_card_value:
        result_text = "The bot's card is higher! You lose!"
        embed.color = CONFIG["ERROR_COLOR"]
    else:
        result_text = "It's a tie! Your money is returned."
        update_user_money(ctx.author.id, cash_change=amount) # Return bet
        embed.color = CONFIG["INFO_COLOR"]

    embed.add_field(name="Outcome", value=result_text, inline=False)

    if win:
        payout = int(amount * CONFIG["WAR_WIN_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=payout)
        embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
    elif not win and player_card_value != bot_card_value: # Not a win and not a tie
        embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
    
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, CONFIG["SHELLGAME_COOLDOWN_SECONDS"], commands.BucketType.user)
async def shellgame(ctx, amount: int, position: int):
    """
    Play the shell game. Guess which position the prize is under!
    """
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must bet a positive amount.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to bet.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if position not in [1, 2, 3]:
        embed = discord.Embed(title="❌ Invalid Position", description="Please choose a position: `1`, `2`, or `3`.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct bet upfront
    set_user_cooldown(ctx.author.id, "shellgame", int(time.time()))

    prize_position = random.randint(1, 3)
    shells = ["⚪", "⚪", "⚪"] # Represent shells

    # Reveal the prize in the correct position
    shells[prize_position - 1] = "💰" 

    win = (position == prize_position)

    embed = discord.Embed(title="🎲 Shell Game!", color=CONFIG["INFO_COLOR"])
    embed.add_field(name="Your Bet", value=f"**${amount:,}** on position `{position}`", inline=False)
    embed.add_field(name="Result", value=f"{shells[0]} {shells[1]} {shells[2]}", inline=False)

    if win:
        payout = int(amount * CONFIG["SHELLGAME_WIN_MULTIPLIER"])
        update_user_money(ctx.author.id, cash_change=payout)
        embed.description = "🎉 You found the prize! You win!"
        embed.add_field(name="Winnings", value=f"You won **${payout:,}**!", inline=False)
        embed.color = CONFIG["SUCCESS_COLOR"]
    else:
        embed.description = f"😞 No prize at position `{position}`. You lost!"
        embed.add_field(name="Loss", value=f"You lost **${amount:,}**.", inline=False)
        embed.color = CONFIG["ERROR_COLOR"]

    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, CONFIG["FISHING_COOLDOWN_SECONDS"], commands.BucketType.user)
async def fishing(ctx, amount: int):
    """
    Go fishing for cash or unexpected items.
    """
    if amount <= 0:
        embed = discord.Embed(title="🚫 Invalid Bet", description="You must pay a positive amount to go fishing.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(title="💰 Insufficient Funds", description=f"You don't have **${amount:,}** cash to go fishing.", color=CONFIG["ERROR_COLOR"])
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    update_user_money(ctx.author.id, cash_change=-amount) # Deduct cost upfront
    set_user_cooldown(ctx.author.id, "fishing", int(time.time()))

    roll = random.random()
    
    # Catching nothing (highest priority for fail cases)
    if roll < CONFIG["FISHING_NOTHING_CHANCE"]:
        response = random.choice([
            "You cast your line, but the water was still. Nothing bit.",
            "A long wait... only to reel in an empty hook.",
            "You caught nothing but a cold. And you lost your bait money."
        ])
        embed = discord.Embed(
            title="🎣 Fishing - No Luck",
            description=f"You paid **${amount:,}** for bait and gear. {response}",
            color=CONFIG["DEFAULT_COLOR"]
        )
        embed.add_field(name="Net Change", value=f"-${amount:,}", inline=False)
    # Catching trash
    elif roll < (CONFIG["FISHING_NOTHING_CHANCE"] + CONFIG["FISHING_TRASH_CHANCE"]):
        item_found = "trash"
        add_item_to_inventory(ctx.author.id, item_found, 1)
        response = random.choice([
            "You felt a tug on your line! You reeled in... a soggy piece of **trash**.",
            "Gross! Your catch was nothing but some old **trash**.",
            "Congratulations! You're now the proud owner of a single piece of **trash**."
        ])
        embed = discord.Embed(
            title="🗑️ Fishing - Trash!",
            description=f"You paid **${amount:,}** for bait and gear. {response}",
            color=CONFIG["ERROR_COLOR"] # Still a loss of money
        )
        embed.add_field(name="Net Change", value=f"-${amount:,}", inline=False)
    # Catching cash (fish)
    else:
        pay = random.randint(CONFIG["FISHING_MIN_CATCH_PAY"], CONFIG["FISHING_MAX_CATCH_PAY"])
        net_earnings, total_cut = await process_earnings(ctx, ctx.author.id, pay)
        response = random.choice([
            f"You reeled in a big one! You caught a shimmering **fish** worth **${pay:,}**!",
            f"Success! Your fishing trip yielded a nice **fish** that sold for **${pay:,}**.",
            f"The fish were biting! You caught several, earning you **${pay:,}**."
        ])
        embed = discord.Embed(
            title="🐟 Fishing Success!",
            description=f"You paid **${amount:,}** for bait and gear. {response} {f'(After a ${total_cut:,} cut for investors)' if total_cut > 0 else ''}",
            color=CONFIG["SUCCESS_COLOR"]
        )
        embed.add_field(name="Net Change", value=f"+${net_earnings - amount:,}", inline=False)

    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)


@bot.command()
async def betoncreate(ctx, *, event_text: str):
    market_id = create_bet_market(ctx.author.id, event_text)
    
    market_data = get_bet_market(market_id)
    if market_data:
        _, _, _, _, _, yes_cash, no_cash, yes_tokens, no_tokens, _ = market_data
        prices = get_market_prices_and_supply(yes_cash, no_cash, yes_tokens, no_tokens)

        embed = discord.Embed(
            title="🎲 New Prediction Market Created!",
            description=f"**Market ID**: `{market_id}`\n**Event**: {event_text}\n"
                        f"Creator: {ctx.author.mention}\n\n"
                        "Use `>buybet <id> <yes/no> <amount>` to buy tokens.",
            color=CONFIG["INFO_COLOR"]
        )
        embed.add_field(name="📊 Current Probabilities", value=f"Yes: `{prices['yes_prob']:.2f}%` | No: `{prices['no_prob']:.2f}%`", inline=False)
        embed.add_field(name="💰 Total Pool", value=f"${yes_cash + no_cash:,}", inline=False)
        embed.set_footer(text="Made With 💖 By Harsizcool")
        
        msg = await ctx.send(embed=embed)
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('UPDATE bet_markets SET message_id = ? WHERE market_id = ?', (msg.id, market_id))
        conn.commit()
        conn.close()
    else:
        embed = discord.Embed(
            title="❌ Creation Failed",
            description="Could not create the market. Please try again.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)

@bot.command()
async def buybet(ctx, market_id: int, side: str, amount: int):
    side = side.lower()
    if side not in ['yes', 'no']:
        embed = discord.Embed(
            title="🚫 Invalid Side",
            description="Please specify 'yes' or 'no' for the side.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="You must buy a positive amount.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    market = get_bet_market(market_id)
    if not market:
        embed = discord.Embed(
            title="❌ Market Not Found",
            description=f"No market found with ID `{market_id}`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    m_id, creator_id, event_text, status, resolved_outcome, yes_cash, no_cash, yes_tokens_supply, no_tokens_supply, _ = market

    if status == 'RESOLVED':
        embed = discord.Embed(
            title="🔒 Market Closed",
            description=f"This market (ID `{market_id}`) has already been resolved.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    user_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(ctx.author.id)
    if user_cash < amount:
        embed = discord.Embed(
            title="💰 Insufficient Funds",
            description=f"You don't have **${amount:,}** cash to make this bet.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    prices = get_market_prices_and_supply(yes_cash, no_cash, yes_tokens_supply, no_tokens_supply)
    
    tokens_bought = 0.0
    if side == 'yes':
        if prices['yes_price'] == 0:
            embed = discord.Embed(title="⚠️ Cannot Buy", description="Yes tokens currently have a price of $0. This market is unbalanced.", color=CONFIG["ERROR_COLOR"])
            embed.set_footer(text="Made With 💖 By Harsizcool")
            await ctx.send(embed=embed)
            return
        tokens_bought = amount / prices['yes_price']
        update_bet_market_pools(market_id, amount, 0, tokens_bought, 0)
        update_user_bet_holdings(ctx.author.id, market_id, yes_tokens_change=tokens_bought)
    else:
        if prices['no_price'] == 0:
            embed = discord.Embed(title="⚠️ Cannot Buy", description="No tokens currently have a price of $0. This market is unbalanced.", color=CONFIG["ERROR_COLOR"])
            embed.set_footer(text="Made With 💖 By Harsizcool")
            await ctx.send(embed=embed)
            return
        tokens_bought = amount / prices['no_price']
        update_bet_market_pools(market_id, 0, amount, 0, tokens_bought)
        update_user_bet_holdings(ctx.author.id, market_id, no_tokens_change=tokens_bought)

    update_user_money(ctx.author.id, cash_change=-amount)

    embed = discord.Embed(
        title="✅ Bet Placed!",
        description=f"You bought **{tokens_bought:.2f}** `{side.upper()}` tokens for market **{market_id}** for **${amount:,}**.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    updated_market = get_bet_market(market_id)
    if updated_market:
        _, _, _, _, _, new_yes_cash, new_no_cash, new_yes_tokens, new_no_tokens, _ = updated_market
        updated_prices = get_market_prices_and_supply(new_yes_cash, new_no_cash, new_yes_tokens, new_no_tokens)
        embed.add_field(name="📊 New Probabilities", value=f"Yes: `{updated_prices['yes_prob']:.2f}%` | No: `{updated_prices['no_prob']:.2f}%`", inline=False)
        embed.add_field(name="💰 Total Pool", value=f"${new_yes_cash + new_no_cash:,}", inline=False)
    
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def betmarkets(ctx):
    open_markets = get_all_open_bet_markets()

    embed = discord.Embed(
        title="📊 Open Prediction Markets",
        color=CONFIG["INFO_COLOR"]
    )

    if not open_markets:
        embed.description = "No open markets currently. Create one with `>betoncreate`!"
    else:
        description = ""
        for market_id, creator_id, event_text, yes_cash, no_cash in open_markets:
            creator = bot.get_user(creator_id) or await bot.fetch_user(creator_id)
            creator_name = creator.display_name if creator else f"Unknown ({creator_id})"
            
            prices = get_market_prices_and_supply(yes_cash, no_cash, 0, 0)
            
            description += (f"**ID: {market_id}** | **{event_text}**\n"
                            f"  Creator: {creator_name}\n"
                            f"  Probabilities: Yes `{prices['yes_prob']:.2f}%` | No `{prices['no_prob']:.2f}%`\n"
                            f"  Total Pool: ${yes_cash + no_cash:,}\n\n")
        embed.description = description
    
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def betinfo(ctx, market_id: int):
    market = get_bet_market(market_id)
    if not market:
        embed = discord.Embed(
            title="❌ Market Not Found",
            description=f"No market found with ID `{market_id}`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    m_id, creator_id, event_text, status, resolved_outcome, yes_cash, no_cash, yes_tokens_supply, no_tokens_supply, _ = market
    creator = bot.get_user(creator_id) or await bot.fetch_user(creator_id)
    creator_name = creator.display_name if creator else f"Unknown ({creator_id})"

    prices = get_market_prices_and_supply(yes_cash, no_cash, yes_tokens_supply, no_tokens_supply)

    embed = discord.Embed(
        title=f"🎲 Market Info: ID {m_id}",
        description=f"**Event**: {event_text}\n"
                    f"Creator: {creator_name}\n"
                    f"Status: `{status.upper()}`",
        color=CONFIG["INFO_COLOR"] if status == 'OPEN' else CONFIG["DEFAULT_COLOR"]
    )
    embed.add_field(name="📊 Probabilities", value=f"Yes: `{prices['yes_prob']:.2f}%` | No: `{prices['no_prob']:.2f}%`", inline=False)
    embed.add_field(name="💰 Total Pool", value=f"${yes_cash + no_cash:,}", inline=False)
    embed.add_field(name="📜 Token Supply", value=f"Yes Tokens: `{prices['yes_tokens_supply']:.2f}` | No Tokens: `{prices['no_tokens_supply']:.2f}`", inline=False)

    if status == 'RESOLVED':
        embed.add_field(name="✅ Resolved Outcome", value=f"`{resolved_outcome}`", inline=False)
        embed.color = CONFIG["SUCCESS_COLOR"] if resolved_outcome == 'YES' else CONFIG["ERROR_COLOR"]

    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def mybets(ctx):
    user_id = ctx.author.id
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT market_id, yes_tokens, no_tokens FROM user_bet_holdings WHERE user_id = ? AND (yes_tokens > 0.01 OR no_tokens > 0.01)', (user_id,))
    user_holdings = cursor.fetchall()
    conn.close()

    embed = discord.Embed(
        title=f"{ctx.author.display_name}'s Bet Holdings",
        color=CONFIG["INFO_COLOR"]
    )

    if not user_holdings:
        embed.description = "You currently hold no tokens in any markets. Use `>buybet` to get started!"
    else:
        description = ""
        for market_id, yes_tokens, no_tokens in user_holdings:
            market_data = get_bet_market(market_id)
            if market_data:
                _, _, event_text, status, _, _, _, _, _, _ = market_data
                
                holdings_str = []
                if yes_tokens > 0.01:
                    holdings_str.append(f"`{yes_tokens:.2f}` Yes tokens")
                if no_tokens > 0.01:
                    holdings_str.append(f"`{no_tokens:.2f}` No tokens")
                
                description += (f"**Market ID {market_id}**: {event_text}\n"
                                f"  Holdings: {', '.join(holdings_str)}\n"
                                f"  Status: `{status.upper()}`\n\n")
            else:
                description += f"**Market ID {market_id}**: Data unavailable (Market might have been removed)\n\n"
        embed.description = description
    
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def resolvebet(ctx, market_id: int, outcome: str):
    outcome = outcome.upper()
    if outcome not in ['YES', 'NO']:
        embed = discord.Embed(
            title="🚫 Invalid Outcome",
            description="Outcome must be 'YES' or 'NO'.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    market = get_bet_market(market_id)
    if not market:
        embed = discord.Embed(
            title="❌ Market Not Found",
            description=f"No market found with ID `{market_id}`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    m_id, creator_id, event_text, status, resolved_outcome_old, yes_cash, no_cash, yes_tokens_supply, no_tokens_supply, _ = market

    if ctx.author.id != creator_id:
        embed = discord.Embed(
            title="🚫 Not Authorized",
            description="Only the market creator can resolve this market.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    if status == 'RESOLVED':
        embed = discord.Embed(
            title="🔒 Market Already Resolved",
            description=f"This market (ID `{market_id}`) has already been resolved to `{resolved_outcome_old}`.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    set_bet_market_resolved(market_id, outcome)

    total_market_cash = yes_cash + no_cash
    winning_side_tokens = 0.0
    
    if outcome == 'YES':
        winning_side_tokens = yes_tokens_supply
    else:
        winning_side_tokens = no_tokens_supply

    payout_info = []
    
    if winning_side_tokens <= 0.01:
        embed = discord.Embed(
            title="💸 Market Resolved - No Winners!",
            description=f"Market ID `{market_id}` (`{event_text}`) resolved to `{outcome}`.\n\n"
                        "No one held tokens for the winning side, so the entire pool was unclaimed.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        clear_user_bet_holdings_for_market(market_id)
        return

    user_holdings_for_market = get_all_user_bet_holdings_for_market(market_id)

    for user_id, yes_tokens, no_tokens in user_holdings_for_market:
        user_payout = 0
        if outcome == 'YES' and yes_tokens > 0.01:
            user_share_ratio = yes_tokens / winning_side_tokens
            user_payout = int(user_share_ratio * total_market_cash)
        elif outcome == 'NO' and no_tokens > 0.01:
            user_share_ratio = no_tokens / winning_side_tokens
            user_payout = int(user_share_ratio * total_market_cash)
        
        if user_payout > 0:
            update_user_money(user_id, cash_change=user_payout)
            user_obj = bot.get_user(user_id) or await bot.fetch_user(user_id)
            user_name = user_obj.display_name if user_obj else f"User ID {user_id}"
            payout_info.append(f"{user_name}: +${user_payout:,}")
    
    embed = discord.Embed(
        title="✅ Market Resolved!",
        description=f"Market ID `{market_id}` (`{event_text}`) resolved to **`{outcome}`**!\n\n"
                    f"Total Pool: **${total_market_cash:,}**",
        color=CONFIG["SUCCESS_COLOR"]
    )
    if payout_info:
        embed.add_field(name="💸 Payouts", value="\n".join(payout_info), inline=False)
    else:
        embed.add_field(name="💸 Payouts", value="No one bet on the winning side.", inline=False)

    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)
    
    clear_user_bet_holdings_for_market(market_id)

# --- ADMIN COMMANDS ---

@bot.command()
@commands.has_permissions(administrator=True)
async def addmoney(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="Amount must be a positive number.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (member.id,))
    cursor.execute('UPDATE users SET cash = cash + ? WHERE user_id = ?', (amount, member.id))
    conn.commit()
    conn.close()

    embed = discord.Embed(
        title="✅ Money Added",
        description=f"Successfully added **${amount:,}** cash to {member.mention}.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def removemoney(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        embed = discord.Embed(
            title="🚫 Invalid Amount",
            description="Amount must be a positive number.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (member.id,))
    
    # Using update_user_money to handle clamping to 0 if amount > current cash
    update_user_money(member.id, cash_change=-amount)
    
    embed = discord.Embed(
        title="💸 Money Removed",
        description=f"Successfully removed **${amount:,}** cash from {member.mention}.",
        color=CONFIG["SUCCESS_COLOR"]
    )
    current_cash, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = get_user_data(member.id)
    embed.add_field(name="Current Cash", value=f"${current_cash:,}", inline=False)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)


# --- UNRELATED COMMANDS ---

@bot.command()
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
async def snipe(ctx):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT author_id, content, timestamp FROM snipe WHERE channel_id = ?', (ctx.channel.id,))
    data = cursor.fetchone()
    conn.close()

    if data:
        author_id, content, timestamp = data
        author = bot.get_user(author_id) or await bot.fetch_user(author_id)
        author_name = author.display_name if author else "Unknown User"
        
        embed = discord.Embed(
            title="🕵️‍♂️ Sniped Message",
            description=content,
            color=CONFIG["INFO_COLOR"],
            timestamp=datetime.datetime.fromtimestamp(timestamp)
        )
        embed.set_author(name=author_name, icon_url=author.display_avatar.url if author else discord.Embed.Empty)
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="❌ No Message to Snipe",
            description="There's nothing to snipe in this channel!",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)

@bot.command(name="8ball")
async def eightball(ctx, *, question: str):
    responses = [
        "It is certain.",
        "It is decidedly so.",
        "Without a doubt.",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it, yes.",
        "Most likely.",
        "Outlook good.",
        "Yes.",
        "Signs point to yes.",
        "Reply hazy, try again.",
        "Better not tell you now.",
        "Cannot predict now.",
        "Concentrate and ask again.",
        "Don't count on it.",
        "My reply is no.",
        "My sources say no.",
        "Outlook not so good.",
        "Very doubtful."
    ]
    
    embed = discord.Embed(
        title="🎱 Magic 8-Ball",
        color=CONFIG["INFO_COLOR"]
    )
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=random.choice(responses), inline=False)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member):
    if user1.id == user2.id:
        embed = discord.Embed(
            title="🤔 Self-Love?",
            description=f"You can't ship someone with themselves, {user1.mention} already loves themselves enough!",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    # To make ship results consistent between the same two users
    # Sort user IDs to ensure the seed is always the same regardless of order
    sorted_ids = sorted([user1.id, user2.id])
    seed = (sorted_ids[0] + sorted_ids[1]) % 100000 
    random.seed(seed)

    compatibility = random.randint(0, 100)
    
    if compatibility < 30:
        phrase = "It's a bumpy road ahead."
    elif compatibility < 60:
        phrase = "There's potential, but work is needed."
    elif compatibility < 85:
        phrase = "A solid match!"
    else:
        phrase = "Perfectly compatible!"

    embed = discord.Embed(
        title="💖 Ship Calculator 💖",
        description=f"**{user1.display_name}** and **{user2.display_name}**",
        color=CONFIG["INFO_COLOR"]
    )
    embed.add_field(name="Compatibility", value=f"{compatibility}%", inline=False)
    embed.add_field(name="Outlook", value=phrase, inline=False)
    embed.set_thumbnail(url="https://i.imgur.com/gK2Jp5j.png") # Image for shipping
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

    random.seed(time.time()) # Reset random seed after use

@bot.command(aliases=["tr"])
async def typereaction(ctx, message_id: int, *, text_to_react: str):
    try:
        target_message = await ctx.channel.fetch_message(message_id)
    except discord.NotFound:
        embed = discord.Embed(
            title="❌ Message Not Found",
            description="Could not find a message with that ID in this channel.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return
    except discord.Forbidden:
        embed = discord.Embed(
            title="🚫 Permissions Error",
            description="I don't have permission to view that message.",
            color=CONFIG["ERROR_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass # Bot doesn't have permissions to delete messages
    except discord.HTTPException:
        pass # Message already deleted or other error

    reaction_chars = []
    for char in text_to_react.upper():
        if 'A' <= char <= 'Z':
            reaction_chars.append(f" regional_indicator_{char.lower()}")
        elif char == ' ': # Represent space with a blue square
            reaction_chars.append("🟦")
    if not reaction_chars:
        embed = discord.Embed(
            title="⚠️ No Valid Characters",
            description="The text contained no valid characters for regional indicator reactions (A-Z, space).",
            color=CONFIG["INFO_COLOR"]
        )
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    for emoji_name in reaction_chars:
        try:
            await target_message.add_reaction(emoji_name)
            await asyncio.sleep(0.7) # Small delay to avoid hitting rate limits
        except discord.HTTPException as e:
            print(f"Error adding reaction: {e}")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            break

@bot.command()
async def liedetector(ctx, *, statement: str):
    outcomes = [
        ("The statement is **TRUE**.", CONFIG["SUCCESS_COLOR"]),
        ("The statement is **FALSE**.", CONFIG["ERROR_COLOR"]),
        ("Analysis inconclusive.", CONFIG["INFO_COLOR"]),
        ("ERROR: Lie detector malfunction. Try again.", CONFIG["ERROR_COLOR"])
    ]
    
    result_text, result_color = random.choice(outcomes)

    embed = discord.Embed(
        title="🤥 Lie Detector Test",
        color=result_color
    )
    embed.add_field(name="Statement Under Analysis", value=statement, inline=False)
    embed.add_field(name="Result", value=result_text, inline=False)
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)


# --- NEW STUPID/TEXT COMMANDS ---
@bot.command()
async def inspire(ctx):
    """
    Get a random inspirational quote.
    """
    quote = random.choice(CONFIG["INSPIRATIONAL_QUOTES"])
    embed = discord.Embed(
        title="✨ Get Inspired!",
        description=f"\"*{quote}*\"",
        color=CONFIG["INFO_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def roast(ctx, member: discord.Member = None):
    """
    Roast yourself or another user.
    """
    target = member or ctx.author
    roast_line = random.choice(CONFIG["ROAST_LINES"])
    
    embed = discord.Embed(
        title="🔥 Roast Session!",
        description=f"{target.mention}, {roast_line}",
        color=CONFIG["ERROR_COLOR"] # Red for a roast!
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def joke(ctx):
    """
    Tell a random joke.
    """
    selected_joke = random.choice(CONFIG["JOKES"])
    embed = discord.Embed(
        title="😂 Have a Laugh!",
        description=selected_joke,
        color=CONFIG["INFO_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)

@bot.command()
async def showerthought(ctx):
    """
    Get a random, quirky shower thought.
    """
    thought = random.choice(CONFIG["SHOWER_THOUGHTS"])
    embed = discord.Embed(
        title="🚿 Shower Thought",
        description=f"\"*{thought}*\"",
        color=CONFIG["DEFAULT_COLOR"]
    )
    embed.set_footer(text="Made With 💖 By Harsizcool")
    await ctx.send(embed=embed)


# --- CUSTOM HELP COMMAND ---

HELP_CATEGORIES = {
    "💸 Economy": [
        "`bal` / `balance` / `money [user]`: Check your (or someone else's) money.",
        "`work`: Earn some cash.",
        "`daily`: Claim your daily reward.",
        "`beg`: Beg for some cash.",
        "`scavenge`: Search for hidden cash or items.",
        "`adventure`: Embark on a journey with unpredictable outcomes.",
        "`mine`: Go mining for cash or valuable minerals.",
        "`forage`: Search for edible plants or hidden cash in the wilderness.",
        "`invest <user> <amount>`: Invest in another user to get a cut of their earnings.",
        "`lb` / `leaderboard`: See the richest users.",
        "`withdraw` / `with <amount>`: Take cash from your bank.",
        "`deposit` / `dep <amount>`: Put cash into your bank.",
        "`donate` / `dn <user> <amount>`: Give money to another user.",
        "`rob <user>`: Try to steal cash from another user (long cooldown!)."
    ],
    "📦 Items & Market": [
        "`inventory [user]`: View your (or someone else's) items.",
        "`currentlistings` / `cl` / `listings`: See items for sale on the market.",
        "`itemcreate <name> <quantity> <sellingprice>`: Create a new custom item listing.",
        "`buy <listing_id> [amount]`: Purchase an item from a listing.",
        "`sell <item_name> <amount> <price_per_item>`: List an item from your inventory for sale.",
        "`use <item_name>`: Use an item from your inventory.",
        "`giveitem <user> <item_name> [amount]`: Give an item to another user.",
        "`iteminfo <item_name>`: Get details about a specific item.",
        "`craft <recipe_name>`: Craft new items from ingredients."
    ],
    "🎰 Gambling": [
        "`blackjack` / `bj <amount>`: Play a game of blackjack against the bot.",
        "`coinflip <heads/tails> <amount>`: Bet on a coin flip.",
        "`roulette <amount> <bet_type>`: Bet on the roulette wheel.",
        "`diceroll <amount> <high/low/7>`: Bet on the sum of two dice.",
        "`slots <amount>`: Spin the slot machine reels.",
        "`rps <amount> <rock/paper/scissors>`: Play Rock Paper Scissors against the bot.",
        "`guess <amount> <number>`: Guess a number (1-10) for a big payout.",
        "`highlow <amount> <higher/lower>`: Bet if the next card will be higher or lower.",
        "`scratch <amount>`: Buy a scratch card for a chance at a big win.",
        "`trivia <amount>`: Answer a trivia question to win cash.",
        "`war <amount>`: Play a card game of War against the bot.", # NEW
        "`shellgame <amount> <position 1/2/3>`: Guess which position the prize is under.", # NEW
        "`fishing <amount>`: Go fishing for cash or unexpected items.", # NEW
        "`betoncreate <event_text>`: Create a new prediction market.",
        "`buybet <market_id> <yes/no> <amount>`: Buy tokens for a prediction market.",
        "`betmarkets`: List all open prediction markets.",
        "`betinfo <market_id>`: Get details for a specific market.",
        "`mybets`: View your token holdings across all markets.",
        "`resolvebet <market_id> <yes/no>`: (Market Creator Only) Resolve a market and trigger payouts."
    ],
    "✨ General": [
        "`ping`: Check bot latency.",
        "`say <message>`: Make the bot repeat your message and delete yours.",
        "`snipe`: See the last deleted message in the channel.",
        "`8ball <question>`: Ask the magic 8-ball anything.",
        "`ship <user1> <user2>`: Calculate compatibility between two users.",
        "`typereaction` / `tr <message_id> <text>`: React to a message with text (A-Z, space).",
        "`liedetector <statement>`: Test if a statement is true or false (for fun).",
        "`inspire`: Get a random inspirational quote.", # NEW
        "`roast [user]`: Roast yourself or another user.", # NEW
        "`joke`: Tell a random joke.", # NEW
        "`showerthought`: Get a random, quirky shower thought." # NEW
    ],
    "👑 Admin Commands": [
        "`addmoney <user> <amount>`: (Admin Only) Add cash to a user.",
        "`removemoney <user> <amount>`: (Admin Only) Remove cash from a user."
    ]
}

def get_help_pages():
    pages = []
    # Create the first page (general overview)
    page1_embed = discord.Embed(
        title="📚 HarsizBot Help (Page 1/2)",
        description=f"Hello! I'm HarsizBot. My prefix is `{CONFIG['PREFIX']}`.\n\n"
                    f"Use `{CONFIG['PREFIX']}help [command]` for more info on a specific command.\n\n"
                    "Here are my commands:",
        color=CONFIG["DEFAULT_COLOR"]
    )
    # Add fields for page 1
    page1_embed.add_field(name="💸 Economy", value="\n".join(HELP_CATEGORIES["💸 Economy"]), inline=False)
    page1_embed.add_field(name="📦 Items & Market", value="\n".join(HELP_CATEGORIES["📦 Items & Market"]), inline=False)
    page1_embed.set_footer(text="Made With 💖 By Harsizcool")
    pages.append(page1_embed)

    # Create the second page (gambling, general, admin)
    page2_embed = discord.Embed(
        title="📚 HarsizBot Help (Page 2/2)",
        description=f"Commands continued from Page 1.",
        color=CONFIG["DEFAULT_COLOR"]
    )
    # Add fields for page 2
    page2_embed.add_field(name="🎰 Gambling", value="\n".join(HELP_CATEGORIES["🎰 Gambling"]), inline=False)
    page2_embed.add_field(name="✨ General", value="\n".join(HELP_CATEGORIES["✨ General"]), inline=False)
    page2_embed.add_field(name="👑 Admin Commands", value="\n".join(HELP_CATEGORIES["👑 Admin Commands"]), inline=False)
    page2_embed.set_footer(text="Made With 💖 By Harsizcool")
    pages.append(page2_embed)

    return pages

class HelpView(View):
    def __init__(self, pages, author_id):
        super().__init__(timeout=180) # Timeout after 3 minutes of inactivity
        self.pages = pages
        self.current_page = 0
        self.author_id = author_id # Store author ID to check interactions
        self.message = None # Will store the message object once sent
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        
        # Previous button
        prev_button = Button(label="Previous", style=discord.ButtonStyle.blurple, disabled=(self.current_page == 0))
        prev_button.callback = self.previous_page
        self.add_item(prev_button)

        # Page number indicator (optional, but good for UX)
        page_indicator = Button(label=f"Page {self.current_page + 1}/{len(self.pages)}", style=discord.ButtonStyle.gray, disabled=True)
        self.add_item(page_indicator)

        # Next button
        next_button = Button(label="Next", style=discord.ButtonStyle.blurple, disabled=(self.current_page == len(self.pages) - 1))
        next_button.callback = self.next_page
        self.add_item(next_button)

    async def on_timeout(self):
        # Disable buttons on timeout
        for item in self.children:
            item.disabled = True
        if self.message: # Ensure message exists
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass # Message might have been deleted

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the command invoker can interact with the buttons
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This help menu is not for you!", ephemeral=True)
            return False
        return True

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

@bot.command()
async def help(ctx, command_name: str = None):
    if command_name:
        cmd = bot.get_command(command_name)
        if not cmd:
            embed = discord.Embed(
                title="❌ Command Not Found",
                description=f"Could not find a command named `{command_name}`.",
                color=CONFIG["ERROR_COLOR"]
            )
            embed.set_footer(text="Made With 💖 By Harsizcool")
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title=f"❓ Help: {CONFIG['PREFIX']}{cmd.name}",
            color=CONFIG["INFO_COLOR"]
        )
        embed.description = cmd.help or "No help message available for this command."

        aliases = ", ".join([f"`{a}`" for a in cmd.aliases]) if cmd.aliases else "None"
        embed.add_field(name="Aliases", value=aliases, inline=False)
        
        usage = f"{CONFIG['PREFIX']}{cmd.name}"
        params = []
        # Accessing `signature.parameters` is more robust for command arguments
        for param in cmd.signature.parameters.values():
            if param.name == 'ctx':
                continue
            if param.kind == param.POSITIONAL_OR_KEYWORD or param.kind == param.KEYWORD_ONLY:
                if param.default is param.empty: # Required argument
                    params.append(f"<{param.name}>")
                else: # Optional argument
                    params.append(f"[{param.name}]")
            elif param.kind == param.VAR_POSITIONAL: # *args
                params.append(f"<...{param.name}>")

        if params:
            usage += " " + " ".join(params)
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
        embed.set_footer(text="Made With 💖 By Harsizcool")
        await ctx.send(embed=embed)
        return

    pages = get_help_pages()
    view = HelpView(pages, ctx.author.id)
    view.message = await ctx.send(embed=pages[0], view=view)


# --- RUN BOT ---
bot.run(btoken)
