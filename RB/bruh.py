# A MESS OF CHATGPT CODE AND MY OWN, HALF THE COMMANDS DO NOT WORK
# REST IN POWER RAT BASTARD - 21 JUNE 2024 to 28 JUNE 2025

import discord
import json
import random
import requests
import os
import math
import aiohttp
import asyncio
import time
from googletrans import Translator, LANGUAGES
from datetime import datetime, timezone
#import yfinance as yf

intents = discord.Intents.all()
intents.messages = True
intents.message_content = True  # Ensure you can read message content

from discord.ext import commands, tasks
client = commands.Bot(command_prefix = ".", intents = discord.Intents.all())

JSON_FILE_PATH = 'C:\\Users\\adam\\Downloads\\brogramming\\economy.json'  # Change this to your JSON file path
STOCK_FILE_PATH = 'C:\\Users\\adam\\Downloads\\brogramming\\python\\ssdata.json' # STOCK DATA!!!
UPTIME_FILE = "uptime.txt" # txt FILE FOR UPTIME.

CHANNEL_ID = 1247542948346724465 # Channel ID for UPTIME.

# Reference time
reference_time = datetime(2024, 6, 21, 21, 45, tzinfo=timezone.utc)
translator = Translator()


@client.event
async def on_ready():
### THIS HERE IS THE OLD VERSION OF THE STATUS SYSTEM.
#    last_message_time = None  # To store the time of the last message
#    last_message_channel = None  # To store the channel of the last message
#
#    # Loop through all channels the bot can access
#    for channel in client.get_all_channels():
#        if isinstance(channel, discord.TextChannel):  # Make sure it's a text channel
#            try:
#                async for message in channel.history(limit=1000):  # Adjust the limit if necessary
#                    if message.author == client.user:
#                        if last_message_time is None or message.created_at > last_message_time:
#                            last_message_time = message.created_at
#                            last_message_channel = channel
#            except discord.Forbidden:
#                print(f"Missing permissions to read messages in {channel.name}")
#                continue

#    # If the bot found any previous message
#    if last_message_time and last_message_channel:
#        last_online = datetime.now(timezone.utc) - last_message_time
#        days = last_online.days
#        hours, remainder = divmod(last_online.seconds, 3600)
#        minutes, seconds = divmod(remainder, 60)
#        await last_message_channel.send(
#            f"I was last online {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds ago."
#        )
#    else:
#        # If no previous message was found in any channel
#       first_text_channel = discord.utils.get(client.get_all_channels(), type=discord.ChannelType.text)
#        if first_text_channel:
#           await first_text_channel.send("This is my first time online or I couldn't find my last message in any channel!")

    # Function to save the current time to a text file
    def save_current_time():
        with open(UPTIME_FILE, "w") as file:
            file.write(datetime.now(timezone.utc).isoformat())  # Use timezone-aware UTC time

    # Function to read the last saved time from the text file
    def read_last_update():
        try:
            with open(UPTIME_FILE, "r") as file:
                last_update = datetime.fromisoformat(file.read().strip())
                
                # Ensure `last_update` is timezone-aware in UTC
                if last_update.tzinfo is None:
                    last_update = last_update.replace(tzinfo=timezone.utc)
                return last_update
        except (FileNotFoundError, ValueError):
            return None

    # Background task to update the text file every minute
    async def update_uptime_file():
        while True:
            save_current_time()
            await asyncio.sleep(60)  # Wait 1 minute

    # Start the uptime update task
    client.loop.create_task(update_uptime_file())

    # Calculate and send uptime message in the specified channel
    last_update = read_last_update()
    if last_update:
        uptime_duration = datetime.now(timezone.utc) - last_update
        days, remainder = divmod(uptime_duration.total_seconds(), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_message = f"Last online: {int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s."
    else:
        uptime_message = "This is the bot's first recorded uptime."

    # Send the uptime message to the specified channel
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(uptime_message)
    else:
        print(f"Could not find channel with ID {CHANNEL_ID}")

    now = datetime.now(timezone.utc)
    delta = now - reference_time

    # Breakdown delta into days, hours, minutes, seconds
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    await channel.send(f"Established: {days}d {hours}h {minutes}m {seconds}s")

    api_key = 'E92DF58BTR7PGEAK'
    symbol = 'QQQM'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        await channel.send("Could not retrieve data for QQQM. Please try again later.")
    else:
        time_series = data["Time Series (Daily)"]
        sorted_dates = sorted(time_series.keys(), reverse=True)

        last_above = None
        for date in sorted_dates:
            closing_price = float(time_series[date]['4. close'])
            if closing_price > 222:
                last_above = datetime.strptime(date, '%Y-%m-%d')
                break  # Stop after finding the most recent one

        if last_above:
            now = datetime.now()
            delta = now - last_above
            message = (
                f"NASDAQ ETF QQQM was last above $222 on {last_above.strftime('%B %d, %Y')} "
                f"({delta.days} days ago)."
            )
            await channel.send(message)
        else:
            await channel.send("QQQM has not been above $222 in the available data.")
            
    print(f'{client.user} has connected to Discord!')
    channel = client.get_channel(1247542948346724465)
    # await channel.send(f'We up, we good, we up :smiling_imp: {client.user}. <@!993544303827767437>')

@client.event
async def on_member_remove(member):
    user_id = member.id
    channel = client.get_channel(1247542948346724465)  # Replace with your specific channel ID
    if channel:
        await channel.send(f"Member {member.name} has left the server. Their ID was {user_id}.")

@client.event
async def on_member_join(member):
    if member.bot:
        return

    # Load existing data from JSON file or create an empty dictionary if the file doesn't exist or is empty
    try:
        with open(JSON_FILE_PATH, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = {}
    except FileNotFoundError:
        data = {}

    user_id = str(member.id)
    if user_id not in data:
        data[user_id] = {"value": "your_value"}

    # Save the updated data back to the JSON file
    with open(JSON_FILE_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        print("Done!")

@client.command()
async def gamble25(ctx, amount, bet):
    with open(JSON_FILE_PATH, 'r') as f:
        data = json.load(f)
    
    # Get user's balance and maxvalue from JSON (assuming ctx.author.id is used as key)
    user_id = str(ctx.author.id)
    
    # Check if user_id exists in data
    if user_id in data:
        user_data = data[user_id]
        balance = int(user_data[0]["balance"])  # Assuming balance is in the first dictionary
        maxvalue = int(user_data[1]["maxvalue"])  # Assuming maxvalue is in the second dictionary
    else:
        # If user_id does not exist, initialize with default values
        balance = 0
        maxvalue = 0

    amount = int(amount)
    bet = int(bet)
    
    # Check if bet amount is greater than balance
    if amount > balance:
        await ctx.send(f'Your balance ({balance}) is not sufficient for this bet.')
        return

    # First part in relation to the numbers.
    await ctx.send(f'You have bet the amount "{amount}" on "{bet}" being chosen.')

    random_number = random.randint(1, 100)
    if random_number > 50:
        if 50 < bet < 75:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} are both between 50 and 75, you win!')
            amount *= 4
            balance += amount
            maxvalue += amount  # Update maxvalue when user wins
            await ctx.send(f'You have won: {amount} your total balance is now: {balance}')
        elif 75 < bet < 100:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} are both between 75 and 100, you win!')
            amount *= 4
            balance += amount
            maxvalue += amount  # Update maxvalue when user wins
            await ctx.send(f'You have won: {amount} your total balance is now: {balance}')
        else:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} do not match, you lose!')
            amount *= 4
            balance -= amount
            await ctx.send(f'You lost {amount} your new balance is {balance}')
    else:
        if bet < 25:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} are between 1 and 25, you win!')
            amount *= 4
            balance += amount
            maxvalue += amount  # Update maxvalue when user wins
            await ctx.send(f'You have won: {amount} your total balance is now: {balance}')
        elif 25 < bet < 50:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} are between 25 and 50, you win!')
            amount *= 4
            balance += amount
            maxvalue += amount  # Update maxvalue when user wins
            await ctx.send(f'You have won: {amount} your total balance is now: {balance}')
        else:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} do not match, you lose!')
            amount *= 4
            balance -= amount
            await ctx.send(f'You lost {amount} your new balance is {balance}')

    # Update balances in JSON file
    data[user_id][0]["balance"] = str(balance)
    data[user_id][1]["maxvalue"] = str(maxvalue)
    
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)


@client.command()
async def gamble(ctx, amount, bet):
    with open(JSON_FILE_PATH, 'r') as f:
        data = json.load(f)
    
    # Get user's balance and maxvalue from JSON (assuming ctx.author.id is used as key)
    user_id = str(ctx.author.id)
    
    # Check if user_id exists in data
    if user_id in data:
        user_data = data[user_id]
        balance = int(user_data[0]["balance"])  # Assuming balance is in the first dictionary
        maxvalue = int(user_data[1]["maxvalue"])  # Assuming maxvalue is in the second dictionary
    else:
        # If user_id does not exist, initialize with default values
        balance = 0
        maxvalue = 0

    amount = int(amount)
    bet = int(bet)
    
    # Check if bet amount is greater than balance
    if amount > balance:
        await ctx.send(f'Your balance ({balance}) is not sufficient for this bet.')
        return

    # This stops the GLITCH!!!
    if amount < 0:
        await ctx.send(f'Your amount ({amount}) is not valid.')
        return

    # First part in relation to the numbers.
    await ctx.send(f'You have bet the amount "{amount}" on "{bet}" being chosen.')

    random_number = random.randint(1, 100)
    if random_number > 50:
        if bet > 50:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} are both above 50, you win!')
            amount *= 2
            balance += amount
            maxvalue += amount  # Update maxvalue when user wins
            await ctx.send(f'You have won: {amount} your total balance is now: {balance}')
        else:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} do not match, you lose!')
            balance -= amount 
            await ctx.send(f'You lost {amount} your new balance is {balance}')
    else:
        if bet < 50:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} are both below 50, you win!')
            amount *= 2
            balance += amount
            maxvalue += amount  # Update maxvalue when user wins
            await ctx.send(f'You have won: {amount} your total balance is now: {balance}')
        else:
            await ctx.send(f'The random number: {random_number} and your guess: {bet} do not match, you lose!')
            balance -= amount 
            await ctx.send(f'You lost {amount} your new balance is {balance}')

    # Update balances in JSON file
    data[user_id][0]["balance"] = str(balance)
    data[user_id][1]["maxvalue"] = str(maxvalue)
    
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(data, f, indent=4)

@client.command()
async def datadump(ctx):
    with open(JSON_FILE_PATH) as json_file:
        data = json.load(json_file)
    with open(STOCK_FILE_PATH) as json_file:
        stock_data = json.load(json_file)
    await ctx.send(f'```{data}```')
    await ctx.send(f'```{stock_data}```')

@client.command()
async def resetprofiles(ctx):
    if ctx.author.id == 558366862510129192:
        # Clear existing data from JSON file
        try:
            with open(JSON_FILE_PATH, 'w') as json_file:
                json_file.write(json.dumps({}))
        except FileNotFoundError:
            pass  # If file doesn't exist, do nothing
        
        # Initialize data dictionary
        data = {}
        
        # Iterate through all members in the server
        for member in ctx.guild.members:
            if not member.bot:
                user_id = str(member.id)
                if user_id not in data:
                    data[user_id] = {"balance": "1"}, {"maxvalue": "1"}

        # Save the updated data back to the JSON file
        with open(JSON_FILE_PATH, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        await ctx.send("Profiles reset and created for all non-bot members.")
    else:
        await ctx.send("You are not allowed to reset the profiles.")

@client.command()
async def echo(ctx, *, echo: str):
    await ctx.send(echo)  
    await ctx.message.delete()

@client.command()
async def bal(ctx):
    user_id = str(ctx.author.id)

    # Load user economy data
    with open(JSON_FILE_PATH, 'r') as f:
        econ_data = json.load(f)

    if user_id in econ_data:
        balance = 0
        maxvalue = 0

        for entry in econ_data[user_id]:
            if "balance" in entry:
                balance = int(entry["balance"])
            elif "maxvalue" in entry:
                maxvalue = int(entry["maxvalue"])
        
        # Load user stock data
        try:
            with open(STOCK_FILE_PATH, 'r') as f:
                stock_data = json.load(f)
        except FileNotFoundError:
            stock_data = {}

        # Check if user owns any stocks
        if user_id in stock_data:
            stocks_owned = stock_data[user_id]
            stocks_info = ", ".join([f"{stock}: {quantity}" for stock, quantity in stocks_owned.items()])
            await ctx.send(f'Your current balance is: {balance} and your maximum value is/was {maxvalue}. \nYou currently own: {stocks_info}')
        else:
            await ctx.send(f'Your current balance is: {balance} and your maximum value is/was {maxvalue}. \nYou do not own any stocks.')
        
        # Ensure balance is not zero
        if balance <= 0:
            await ctx.send("Your balance is 0, you will be given 1 unit to avoid the '0 of doom'.")
            balance = 1
            econ_data[user_id][0]["balance"] = str(balance)
            with open(JSON_FILE_PATH, 'w') as f:
                json.dump(econ_data, f, indent=4)
    else:
        await ctx.send("User data not found.")

@client.command()
async def m(ctx, ID: int, *, message: str):
    if ctx.author.id == 558366862510129192:
        channelID = client.get_channel(ID)
        await channelID.send(message)
    else:
        await ctx.send("You're not authorized to use this command.")

@client.command()
async def promptB(ctx):
    words = []
    LINT = random.randint(1, 100)
    for channel in ctx.guild.text_channels:
        try:
            async for message in channel.history(limit = LINT):
                words.extend(message.content.split())
        except (discord.Forbidden, discord.HTTPException):
            continue

    if len(words) < 20:
        await ctx.send("Prompt failed.")
    else:
        selected_words = random.sample(words, 20)
        await ctx.send(' '.join(selected_words))

@client.command()
async def prompt(ctx):
    words = []
    LINT = random.randint(1, 100)
    for channel in ctx.guild.text_channels:
        try:
            async for message in channel.history(limit=LINT):
                if not message.author.bot:  # Only include messages from non-bot users
                    words.extend(message.content.split())
        except (discord.Forbidden, discord.HTTPException):
            continue

    if len(words) < 20:
        await ctx.send("Prompt failed.")
    else:
        selected_words = random.sample(words, 20)
        await ctx.send(' '.join(selected_words))

@client.command()
async def promptRB(ctx):
    words = []
    LINT = random.randint(1, 100)
    target_user_id = 1253812459068985415  # The specific user ID

    for channel in ctx.guild.text_channels:
        try:
            async for message in channel.history(limit=LINT):
                if message.author.id == target_user_id:
                    words.extend(message.content.split())
        except (discord.Forbidden, discord.HTTPException):
            continue

    if len(words) < 20:
        await ctx.send("Prompt failed.")
    else:
        selected_words = random.sample(words, 20)
        await ctx.send(' '.join(selected_words))

@client.command()
async def cp(ctx, stock):
    api_key = 'E92DF58BTR7PGEAK'
    symbol = f'{stock}'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'

    response = requests.get(url)
    data = response.json()

    if "Time Series (1min)" not in data:
        await ctx.send("Could not retrieve data. Please check the stock symbol and try again.")
        return

    time_series = data["Time Series (1min)"]
    latest_time = list(time_series.keys())[0]
    latest_data = time_series[latest_time]

    current_price = latest_data['4. close']

    message = f"The current price of {symbol} is ${current_price} (as of {latest_time})."

    await ctx.send(message)

@client.command()
async def buy(ctx, stock: str, quantity: int):
    user_id = str(ctx.author.id)
    api_key = 'E92DF58BTR7PGEAK'    
    # Fetch latest stock price from Alpha Vantage
    symbol = stock.upper()  # Ensure stock symbol is in uppercase
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'
    
    response = requests.get(url)
    data = response.json()
    
    if "Time Series (1min)" not in data:
        await ctx.send("Invalid stock symbol. Please check and try again.")
        return
    
    latest_close_price = float(next(iter(data["Time Series (1min)"].values()))['4. close'])
    latest_close_price = math.ceil(latest_close_price)  # Round up to nearest whole number
    
    # Load user balance from DATA_RENAME
    try:
        with open(JSON_FILE_PATH, "r") as f:
            user_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("Error loading user data. Please try again later.")
        return
    
    if user_id not in user_data:
        await ctx.send("User data not found. Please try again later.")
        return
    
    user_balance = float(user_data[user_id][0]['balance'])
    required_amount = latest_close_price * quantity
    
    if user_balance < required_amount:
        await ctx.send(f"Insufficient balance. You need {required_amount} to buy {quantity} of {stock}.")
        return
    
    # Proceed with the purchase
    try:
        with open(STOCK_FILE_PATH, "r") as f:
            stock_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stock_data = {}
    
    if user_id not in stock_data:
        stock_data[user_id] = {}
    
    if stock in stock_data[user_id]:
        stock_data[user_id][stock] += quantity
    else:
        stock_data[user_id][stock] = quantity
    
    # Deduct the amount from user balance and round to nearest whole number
    new_balance = math.floor(user_balance - required_amount)  # Round down to ensure no decimal places    
    user_data[user_id][0]['balance'] = str(new_balance)  # Convert to string before updating
    
    # Save updated user data
    with open(JSON_FILE_PATH, "w") as f:
        json.dump(user_data, f, indent=4)
    
    # Save updated stock data
    with open(STOCK_FILE_PATH, "w") as f:
        json.dump(stock_data, f, indent=4)
    
    await ctx.send(f"{ctx.author.mention} bought {quantity} of {stock} for {required_amount}.")

@client.command()
async def sell(ctx, stock: str, quantity: int):
    user_id = str(ctx.author.id)
    api_key = 'E92DF58BTR7PGEAK'     
    # Fetch latest stock price from Alpha Vantage
    symbol = stock.upper()  # Ensure stock symbol is in uppercase
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'
    
    response = requests.get(url)
    data = response.json()
    
    if "Time Series (1min)" not in data:
        await ctx.send("Invalid stock symbol. Please check and try again.")
        return
    
    try:
        latest_close_price = float(next(iter(data["Time Series (1min)"].values()))['4. close'])
        latest_close_price_rounded = math.ceil(latest_close_price)  # Round up to nearest whole number
    except (KeyError, ValueError):
        await ctx.send("Error fetching stock price. Please try again later.")
        return
    
    # Load user stock data from STOCK_FILE_PATH
    try:
        with open(STOCK_FILE_PATH, "r") as f:
            stock_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stock_data = {}
    
    if user_id not in stock_data or stock not in stock_data[user_id] or stock_data[user_id][stock] < quantity:
        await ctx.send(f"You don't have enough {stock} to sell.")
        return
    
    # Calculate total amount to receive and round it
    total_amount = latest_close_price_rounded * quantity
    
    # Update user balance in DATA_RENAME_PATH
    try:
        with open(JSON_FILE_PATH, "r") as f:
            user_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("Error loading user data. Please try again later.")
        return
    
    if user_id not in user_data:
        await ctx.send("User data not found. Please try again later.")
        return
    
    try:
        current_balance = float(user_data[user_id][0]['balance'])
        new_balance = math.floor(current_balance + total_amount)  # Round down to nearest whole number
    except (KeyError, ValueError):
        await ctx.send("Error with user balance data. Please try again later.")
        return
    
    # Update user balance in user_data and save
    user_data[user_id][0]['balance'] = str(new_balance)
    
    # Update user's stock holdings in stock_data
    stock_data[user_id][stock] -= quantity
    
    if stock_data[user_id][stock] == 0:
        del stock_data[user_id][stock]  # Remove the stock entry if quantity becomes zero
    
    # Save updated data to files
    try:
        with open(JSON_FILE_PATH, "w") as f:
            json.dump(user_data, f, indent=4)
    except IOError:
        await ctx.send("Error saving user data. Please try again later.")
        return
    
    try:
        with open(STOCK_FILE_PATH, "w") as f:
            json.dump(stock_data, f, indent=4)
    except IOError:
        await ctx.send("Error saving stock data. Please try again later.")
        return
    
    await ctx.send(f"{ctx.author.mention} sold {quantity} of {stock} for {total_amount}.")

@client.command()
async def portal(ctx, *, message: str):
    IDA = client.get_channel(1247546147493380157)
    IDB = client.get_channel(1259420693703950346)
    user = ctx.author.name
    
    # Check if the message is from a bot and ignore it
    if ctx.author.bot:
        return
    
    if ctx.channel.id == 1247546147493380157:
        await IDB.send(f'{user} says: {message}')

    elif ctx.channel.id == 1259420693703950346:
        await IDA.send(f'{user} says: {message}')

@client.command()
@commands.has_permissions(manage_emojis=True)
async def addemoji(ctx, name: str, image_url: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status != 200:
                    await ctx.send('Could not download file...')
                    return
                
                img_data = await response.read()
                
                guild = ctx.guild
                emoji = await guild.create_custom_emoji(name=name, image=img_data)
                await ctx.send(f'Emoji created: <:{emoji.name}:{emoji.id}>')
    except discord.Forbidden:
        await ctx.send('I do not have permission to manage emojis.')
    except discord.HTTPException as e:
        await ctx.send(f'An error occurred: {e}')
    except Exception as e:
        await ctx.send(f'An unexpected error occurred: {e}')

@client.command()
async def lb(ctx):
    # Load the JSON data
    with open(JSON_FILE_PATH, 'r') as file:
        data = json.load(file)
    
    # Extract and sort balances
    leaderboard = []
    for user_id, values in data.items():
        balance = int(values[0]['balance'])
        leaderboard.append((user_id, balance))
    
    # Sort by balance in descending order
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    
    # Create the leaderboard message
    embed = discord.Embed(title="Leaderboard", color=discord.Color.blue())
    for rank, (user_id, balance) in enumerate(leaderboard, start=1):
        user = await client.fetch_user(user_id)
        embed.add_field(name=f"#{rank} {user}", value=f"Balance: {balance}", inline=False)
    
    # Send the leaderboard
    await ctx.send(embed=embed)

@client.command()
async def newnick(ctx, *, new_nickname: str):
    try:
        await ctx.guild.me.edit(nick=new_nickname)
        await ctx.send(f"Nickname successfully changed to: {new_nickname}")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to change nickname: {e}")

@client.command()
async def status(ctx, status_type: str, *, status_message: str):
    """Change the bot's status and activity."""
    # Determine the status type
    status_type = status_type.lower()
    if status_type == "online":
        new_status = discord.Status.online
    elif status_type == "idle":
        new_status = discord.Status.idle
    elif status_type == "dnd":
        new_status = discord.Status.dnd
    elif status_type == "invisible":
        new_status = discord.Status.invisible
    else:
        await ctx.send("Invalid status type! Choose from `online`, `idle`, `dnd`, or `invisible`.")
        return

    # Update the bot's status
    try:
        await client.change_presence(status=new_status, activity=discord.Game(name=status_message))
        await ctx.send(f"Status updated to `{status_type}` with message: {status_message}")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to change status: {e}")

@client.command()
async def choose(ctx, *choices):
    
    if not choices:
        await ctx.send("You need to provide some options for me to choose from!")
        return
    
    chosen = random.choice(choices)
    await ctx.send(f"I choose: {chosen}")

@client.command()
async def lifespan(ctx):
    now = datetime.now(timezone.utc)
    delta = now - reference_time

    # Breakdown delta into days, hours, minutes, seconds
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    await ctx.send(f"Established: {days}d {hours}h {minutes}m {seconds}s")

#@client.command()
#async def nasdaq_check(ctx):
#    symbol = '^IXIC'  # NASDAQ Composite Index
#    index = yf.Ticker(symbol)
#    hist = index.history(period="1y")  # You can adjust this for longer lookback

#    above_20k = hist[hist['Close'] > 20000]

#    if not above_20k.empty:
#        last_date = above_20k.index[-1]
#        now = datetime.now()
#        delta = now - last_date.to_pydatetime()

#        message = (
#            f"The NASDAQ Composite was last above 20,000 on {last_date.strftime('%B %d, %Y')}, "
#            f"{delta.days} days ago."
#        )
#        await ctx.send(message)
#    else:
#        await ctx.send("NASDAQ Composite has not been above 20,000 in the past year.")

@client.command()
async def q(ctx):
    api_key = 'E92DF58BTR7PGEAK'
    symbol = 'QQQM'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        await ctx.send("Could not retrieve data for QQQM. Please try again later.")
        return

    time_series = data["Time Series (Daily)"]
    sorted_dates = sorted(time_series.keys(), reverse=True)

    for date in sorted_dates:
        closing_price = float(time_series[date]['4. close'])
        if closing_price > 222:
            last_above = datetime.strptime(date, '%Y-%m-%d')
            now = datetime.now()
            delta = now - last_above
            message = (
                f"NASDAQ ETF QQQM was last above $222 on {last_above.strftime('%B %d, %Y')} "
                f"({delta.days} days ago)."
            )
            await ctx.send(message)
            return

    await ctx.send("QQQM has not been above $200 in the available data.")

### ADD FUTURE SENATE SYSTEM???

@client.command()
async def babel(ctx, *, message: str):
    languages = list(LANGUAGES.keys())  # Get language codes like 'fr', 'de', etc.
    target_lang = random.choice(languages)

    try:
        translated = translator.translate(message, dest=target_lang)
        # await ctx.send(f"🌐 ({target_lang}) {translated.text}")
        await ctx.send(translated.text)
    except Exception as e:
        await ctx.send(f"Translation failed: {str(e)}")

    await ctx.message.delete()

### Code for RPG here!!!

# JSON utility
def load_json(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Helper
def get_faction_id(user_id):
    factions = load_json("factions.json")
    for fid, data in factions.items():
        if user_id in data['members']:
            return fid
    return None

# --- FACTIONS ---

@client.command()
async def create_faction(ctx, *, faction_name):
    user_id = str(ctx.author.id)
    factions = load_json("factions.json")

    if get_faction_id(user_id):
        await ctx.send("You're already in a faction!")
        return

    fid = f"FA{random.randint(1000,9999)}"
    while fid in factions:
        fid = f"FA{random.randint(1000,9999)}"

    factions[fid] = {"name": faction_name, "members": [user_id]}
    save_json("factions.json", factions)
    await ctx.send(f"Faction `{faction_name}` created with ID: `{fid}`.")

@client.command()
async def join_faction(ctx, faction_id):
    user_id = str(ctx.author.id)
    factions = load_json("factions.json")

    if faction_id not in factions:
        await ctx.send("Faction not found.")
        return

    if get_faction_id(user_id):
        await ctx.send("You are already in a faction!")
        return

    factions[faction_id]["members"].append(user_id)
    save_json("factions.json", factions)
    await ctx.send(f"You joined faction `{faction_id}`.")

@client.command()
async def leave_faction(ctx):
    user_id = str(ctx.author.id)
    factions = load_json("factions.json")

    for fid, data in factions.items():
        if user_id in data["members"]:
            data["members"].remove(user_id)
            if not data["members"]:
                del factions[fid]
                await ctx.send(f"Faction `{fid}` disbanded as all members left.")
            else:
                await ctx.send(f"You left faction `{fid}`.")
            save_json("factions.json", factions)
            return
    await ctx.send("You're not in a faction.")

# --- VILLAGES ---

@client.command()
async def list_villages(ctx):
    villages = load_json("villages.json")
    factions = load_json("factions.json")
    msg = "**🏘️ Villages:**\n"

    for vname, data in villages.items():
        controller = data['controller']
        if controller:
            if controller.startswith("FA"):
                ctrl_name = factions.get(controller, {}).get("name", "Unknown Faction")
            else:
                ctrl_name = f"<@{controller}>"
        else:
            ctrl_name = "Unclaimed"

        gdp = 10 + 100 * data['buildings']
        msg += f"🏘️ `{vname.title()}` | GDP: **${gdp}** | Controlled by: {ctrl_name}\n"

    await ctx.send(msg or "No villages yet!")

@client.command()
async def check_village(ctx, name):
    villages = load_json("villages.json")
    name = name.lower()
    if name not in villages:
        await ctx.send("Village not found.")
        return
    data = villages[name]
    b = data['buildings']
    await ctx.send(f"🏘️ `{name}`\nBuildings: {'🛖' * b} ({b})\nLast Collected: <t:{int(data['last_collected'])}:R>")

@client.command()
async def build(ctx, village_name):
    user_id = str(ctx.author.id)
    factions = load_json("factions.json")
    eco = load_json("economy.json")
    villages = load_json("villages.json")

    village_name = village_name.lower()
    if village_name not in villages:
        await ctx.send("Village not found.")
        return

    controller = villages[village_name]['controller']
    user_faction = get_faction_id(user_id)
    if controller != user_id and controller != user_faction:
        await ctx.send("You don't control this village.")
        return

    if eco.get(user_id, 0) < 100:
        await ctx.send("Not enough money. ($100 needed)")
        return

    eco[user_id] -= 100
    villages[village_name]['buildings'] += 1
    save_json("economy.json", eco)
    save_json("villages.json", villages)
    await ctx.send("Built a 🛖 in the village!")

@client.command()
async def rename_village(ctx, old_name, new_name):
    villages = load_json("villages.json")
    user_id = str(ctx.author.id)
    old_name = old_name.lower()
    new_name = new_name.lower()

    if old_name not in villages:
        await ctx.send("Old village not found.")
        return

    controller = villages[old_name]["controller"]
    if villages[old_name]['buildings'] < 10:
        await ctx.send("You need 10 buildings to rename the village.")
        return

    if controller != user_id and controller != get_faction_id(user_id):
        await ctx.send("You don't control this village.")
        return

    villages[new_name] = villages.pop(old_name)
    save_json("villages.json", villages)
    await ctx.send(f"Village renamed to `{new_name}`.")

@client.command()
async def collect_gdp(ctx, village_name):
    user_id = str(ctx.author.id)
    village_name = village_name.lower()
    villages = load_json("villages.json")
    eco = load_json("economy.json")
    factions = load_json("factions.json")

    if village_name not in villages:
        await ctx.send("Village not found.")
        return

    v = villages[village_name]
    controller = v['controller']
    owner_check = (controller == user_id or controller == get_faction_id(user_id))

    if not owner_check:
        await ctx.send("You do not control this village.")
        return

    now = time.time()
    if now - v["last_collected"] < 3600:
        await ctx.send("Too soon. You can collect GDP once per hour.")
        return

    gdp = 10 + 100 * v["buildings"]
    if controller.startswith("FA"):
        members = factions[controller]['members']
        share = gdp // len(members)
        for m in members:
            eco[m] = eco.get(m, 0) + share
    else:
        eco[controller] = eco.get(controller, 0) + gdp

    v["last_collected"] = now
    save_json("villages.json", villages)
    save_json("economy.json", eco)
    await ctx.send(f"Collected ${gdp} GDP!")

# --- CHALLENGES ---

@client.command()
async def challenge(ctx, user: discord.User, village_name):
    challenger_id = str(ctx.author.id)
    opponent_id = str(user.id)
    village_name = village_name.lower()

    villages = load_json("villages.json")
    if village_name not in villages:
        await ctx.send("Village not found.")
        return

    village = villages[village_name]
    controller = village['controller']
    if controller != opponent_id and controller != get_faction_id(opponent_id):
        await ctx.send("That user doesn't control this village.")
        return

    await ctx.send(f"{user.mention}, {ctx.author.name} challenges you for `{village_name}`! Accept with `!accept`.")

    def check(m):
        return m.author.id == user.id and m.content.lower() == "!accept"

    try:
        await client.wait_for("message", check=check, timeout=30)
    except:
        await ctx.send("Challenge timed out.")
        return

    moves = ['rock', 'paper', 'scissors']
    scores = {challenger_id: 0, opponent_id: 0}

    for round in range(3):
        await ctx.send(f"**Round {round+1}** - DM me your move (`rock/paper/scissors`).")

        def move_check(m):
            return m.author.id in [ctx.author.id, user.id] and m.content.lower() in moves

        p1_move = await client.wait_for("message", check=move_check, timeout=60)
        p2_move = await client.wait_for("message", check=move_check, timeout=60)

        p1 = p1_move.content.lower()
        p2 = p2_move.content.lower()

        winner = None
        if p1 == p2:
            await ctx.send(f"Tie! Both chose {p1}.")
        elif (p1 == 'rock' and p2 == 'scissors') or (p1 == 'scissors' and p2 == 'paper') or (p1 == 'paper' and p2 == 'rock'):
            winner = challenger_id
        else:
            winner = opponent_id

        if winner:
            scores[winner] += 1
            await ctx.send(f"{ctx.guild.get_member(int(winner)).mention} wins this round!")

    if scores[challenger_id] >= 2:
        new_controller = get_faction_id(challenger_id) or challenger_id
        village['controller'] = new_controller
        save_json("villages.json", villages)
        await ctx.send(f"{ctx.author.name} won the challenge and now controls `{village_name}`!")
    else:
        await ctx.send(f"{user.name} defended `{village_name}` successfully!")

# --- ECONOMY ---

@client.command()
async def balance(ctx):
    eco = load_json("economy.json")
    user_id = str(ctx.author.id)
    bal = eco.get(user_id, 0)
    await ctx.send(f"You have ${bal}.")

# --- INIT EXAMPLE VILLAGE ---
#@client.command()
#async def create_village(ctx, name):
#    villages = load_json("villages.json")
#    name = name.lower()
#    if name in villages:
#        await ctx.send("Village already exists.")
#        return
#    controller = get_faction_id(str(ctx.author.id)) or str(ctx.author.id)
#    villages[name] = {"controller": controller, "buildings": 0, "last_collected": time.time()}
#    save_json("villages.json", villages)
#    await ctx.send(f"Village `{name}` created and under your control.")

@client.command()
@commands.has_permissions(administrator=True)
async def reset_economy(ctx):
    economy = {}
    for member in ctx.guild.members:
        if not member.bot:
            economy[str(member.id)] = 100
    save_json("economy.json", economy)
    await ctx.send("✅ Economy reset. Profiles created for all non-bot users.")

@client.command()
@commands.has_permissions(administrator=True)
async def init_villages(ctx):
    def generate_random_village_names(count):
        base_names = [
            "Abbeyfeale", "Askeaton", "Bruff", "Caherconlish", "Castleconnell",
            "Dromcollogher", "Kilmallock", "Murroe", "Pallaskenry", "Rathkeale",
            "Adare", "Croom", "Foynes", "Hospital", "Kilfinane",
            "Newcastle West", "Patrickswell", "Glin", "Galbally", "Fedamore",
            "Herbertstown", "Ballylanders", "Cappamore", "Kilcornan", "Doon"
        ]
        return random.sample(base_names, count)

    if not os.path.exists("villages.json"):
        villages = {}
    else:
        villages = load_json("villages.json")

    if len(villages) > 0:
        await ctx.send("⚠️ Villages already initialized.")
        return

    new_names = generate_random_village_names(25)
    for name in new_names:
        villages[name.lower()] = {
            "controller": None,
            "buildings": 0,
            "last_collected": time.time()
        }

    save_json("villages.json", villages)
    await ctx.send("✅ 25 villages have been initialized.")

client.run("PUT YO TOKEN HERE")
