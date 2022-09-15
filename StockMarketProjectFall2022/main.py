import json
import finnhub
import datetime
import discord
import asyncio

import pandas as pd
from requests import JSONDecodeError

TOKEN = 'MTAxMjEzMDMzMDc3NTM5NjM4NA.GQhv5i.RRYrbpK_Dkx4hMBKZ3se2cmDvT6s0OqFRY8OvE'  # Discord Bot token
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to message
intents.typing = True  # Allows the bot to type
discord_client = discord.Client(intents=intents)

key = "cc360riad3i96jb01de0"
finnhub_client = finnhub.Client(api_key=key)

data = {
    "TurtlestWizard#5714": ['TSLA', 'AAPL']
}
data["TurtlestWizard#5714"].append('PEEN')

# Print the favorites list of the messenger
def show_list(user_id):
    user = str(user_id)
    with open("discordData.json", "r") as read_file:  # Get the favorites list from json file
        x = json.load(read_file)

    reply = ''
    if not user in x:
        reply += f'User {user} is not in the current data set.'
        return reply
    else:
        reply += f'{user}\'s current favorites list:\n\n'
        for symbol in x[user_id]:
            reply += symbol + ', '
        return reply[0:len(reply)-2]


# Add symbols to a list of favorites
async def add(user_id, symbol_str):

    my_csv = pd.read_csv('StockSymbols.csv')  # Read the csv
    nasdq_symbols = my_csv['Symbol']  # Get symbol series

    symbols = symbol_str.replace(',', '').split(' ')  # Creates an array of the symbols
    user = str(user_id)
    with open("discordData.json", "r") as read_file:  # Get the favorites list from json file
        x = json.load(read_file)

    fakes = ''
    if user in x:  # Check if the user is already in the json file
        for symbol in symbols:
            if symbol in nasdq_symbols.values:
                if not symbol in x[user_id]:
                    x[user_id].append(symbol)
            else:
                fakes += symbol+', '
    else:
        new_dict = {user: symbols}
        x.update(new_dict)

    if fakes != '':
        channel = discord_client.get_channel(946167541334704158)
        await channel.send(f'At least one fake stock has been spotted: {fakes[0:len(fakes)-2]}')

    with open("discordData.json", "w") as write_file:
        json.dump(x, write_file)


# Remove symbols from a list of favorites
async def remove(user_id, symbol_str):
    my_csv = pd.read_csv('StockSymbols.csv')  # Read the csv
    nasdq_symbols = my_csv['Symbol']  # Get symbol series
    symbols = symbol_str.replace(',', '').split(' ')  # Creates an array of the symbols
    user = str(user_id)
    with open("discordData.json", "r") as read_file:  # Get the favorites list from json file
        x = json.load(read_file)

    fakes = ''
    if user in x:  # Check if the user is already in the json file
        for symbol in symbols:
            if symbol in nasdq_symbols.values:
                if symbol in x[user_id]:
                    x[user_id].remove(symbol)
            else:
                fakes += symbol + ', '
    else:
        channel = discord_client.get_channel(946167541334704158)
        await channel.send(f'User {user} does not exist in the current set of data.')

    if fakes != '':
        channel = discord_client.get_channel(946167541334704158)
        await channel.send(f'At least one fake stock has been spotted: {fakes[0:len(fakes)-2]}')

    with open("discordData.json", "w") as write_file:
        json.dump(x, write_file)

# Get real-time quote data for US stocks
def get_quote(symbol):
    quote = finnhub_client.quote(symbol)  # Type dict
    try:
        c = round(quote['c'], 2)  # Current price
        d = round(quote['d'], 2)  # Change from current price and opening
        dp = quote['dp']  # Percent change
        h = round(quote['h'], 2)  # Today's high
        l = round(quote['l'], 2)  # Today's low
        o = round(quote['o'], 2)  # Opening price
        pc = round(quote['pc'], 2)  # Previous close

        str = symbol + '\n\n'
        # Making the quote readable for normal people
        if (d < 0):
            d = abs(d)
            str += f'Current Price: ${c} \nChange: -${d} \nPercent Change: {dp}% \nHigh Price of Today: ${h} ' \
                   f'\nLow Price of Today: ${l} \nOpening Price of Today: ${o} \nPrevious Close Price: ${pc}'
        else:
            str += f'Current Price: ${c} \nChange: ${d} \nPercent Change: {dp}% \nHigh Price of Today: ${h} ' \
                   f'\nLow Price of Today: ${l} \nOpening Price of Today: ${o} \nPrevious Close Price: ${pc}'
        return str
    except TypeError:
        return f'{symbol} is not a valid symbol. Try again.'


# Search for best-matching symbols based on your query, returns top 5 results
def look_up(query):
    search = finnhub_client.symbol_lookup(query)  # Type dict
    count = search['count']  # Number of results
    results = search['result']  # Array of search results
    str = f'Top 5 results from {query}:\n\n'

    for result in range(5):
        desc = results[result]['description']
        display_symbol = results[result]['displaySymbol']
        symbol = results[result]['symbol']
        type = results[result]['type']
        str += f'Description: {desc} \nDisplay Symbol: {display_symbol} \nSymbol: {symbol} \nType: {type}\n\n'
    return str


# Search for best-matching symbols based on your query, returns all results
def look_up_all(query):
    search = finnhub_client.symbol_lookup(query)  # Type dict
    count = search['count']  # Number of results
    results = search['result']  # Array of search results
    str = f'Number of results from {query}: {count}\n\n'
    for result in results:
        desc = result['description']
        display_symbol = result['displaySymbol']
        symbol = result['symbol']
        type = result['type']
        str += f'Description: {desc} \nDisplay Symbol: {display_symbol} \nSymbol: {symbol} \nType: {type}\n\n'
    return str


# Add favorites to a user in a database

@discord_client.event
async def on_ready():
    print("We have hacked into the mainframe".format(discord_client))
    # await schedule_daily_message()


@discord_client.event
async def on_message(message):
    user_message = str(message.content)
    channel = message.channel
    user_id = str(message.author)
    msg = user_message[3:len(user_message)]

    # Make sure it only works in its designated channel
    if channel == discord_client.get_channel(946167541334704158):

        # Gets the favorites list of the messenger
        if '!l' == user_message[0:2] and len(user_message) == 2:
            await message.channel.send(show_list(user_id))
            return

        # Look up all command:
        if '!k ' == user_message[0:3]:
            await message.channel.send(look_up_all(msg))
            return

        # Look up top 5 command:
        if '!s ' == user_message[0:3]:
            await message.channel.send(look_up(msg))
            return

        # Gets quote of specific stock
        if '!q ' == user_message[0:3]:
            await message.channel.send(get_quote(msg))
            return

        # Adds stock(s) to their favorite stocks list:
        if '!a ' == user_message[0:3]:
            await add(user_id, msg)
            with open("discordData.json", "r") as read_file:
                x = json.load(read_file)
            reply = 'Your current list of favorite stocks:\n\n'
            for symbol in x[user_id]:
                reply += symbol + ', '
            await message.channel.send(reply[0:len(reply) - 2])
            return

        # Removes stock(s) from their favorite stocks list:
        if '!r ' == user_message[0:3]:
            await remove(user_id, msg)
            with open("discordData.json", "r") as read_file:
                x = json.load(read_file)
            reply = 'Your current list of favorite stocks:\n\n'
            for symbol in x[user_id]:
                reply += symbol + ', '
            await message.channel.send(reply[0:len(reply) - 2])
            return


'''async def schedule_daily_message():
    # Set up time for query
    time_today = datetime.datetime.now()
    time_tmrw = time_today.replace(day=time_today.day, hour=16, minute=30) + datetime.timedelta(days=1)
    delta_time = time_tmrw - time_today
    secs = delta_time.total_seconds()

    # Make it wait for a certain amount of seconds
    await asyncio.sleep(5)

    channel = discord_client.get_channel(784440016800579606)
    await channel.send(get_quote('TSLA'))    '''

discord_client.run(TOKEN)