import discord
import os
import random
import sys
import select
import asyncio

#webscrape stuff
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

TOKEN = 'NDEwOTQ3OTg3ODYzMjQwNzE1.DyVhuw.5oEb4IFs6nD9sZii33u0XugX1Y8'

client = discord.Client()


channel = discord.Object(id='536375190704095235')

#webscraping stuff
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

#poll stuff
class Poll:
    def __init__(self, prompt, answers):
        self.prompt = prompt
        self.answers = list()
        self.registeredVotes = dict()
        for i in range(len(answers)):
            self.answers.append([answers[i], 0]);

    def vote(self, option):
        self.answers[option] += 1

    def printPoll(self):
        print(self.prompt + ":")
        for key, value in self.answers.items():
            print(key + ": " + value + " votes")

    def __str__(self):
        string = "This channel's poll: " + self.prompt + "\nOptions:\n"

        for i in range(len(self.answers)):
            string += str(i+1) + ": " + self.answers[i][0] + ", " + str(self.answers[i][1]) + " votes" + "\n"

        return string

polls = dict()


async def print_msg():
    global channel
    while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = sys.stdin.readline()
        if line:
            if line[0] == '~':
#381594768427450379
                channel.id = line[1:-1]
                print("changed channel to: " + line[1:])
            else:
                await client.send_message(channel, line)

async def input_task():
    await client.wait_until_ready()
    while not client.is_closed:
        try:
            await asyncio.wait_for(print_msg(), timeout=1.0)
        except:
            pass

@client.event
async def on_message(message):
    global channel

    if message.author == client.user:
        return

    # thank you
    if message.content.startswith('thank you, reorte'):
        msg = 'you\'re welcome! ^w^'.format(message)
        await client.send_message(message.channel, msg)

    # random funniee image from funiee intertnet images
    if message.content.startswith('!funnie'):
        directory = '/mnt/c/Users/Alex Quinton/Desktop/funiee intertnet images'
        filename = random.choice(os.listdir(directory))
        path = os.path.join(directory, filename)
        await client.send_file(message.channel, path)

    # random gif from gifs
    if message.content.startswith('!gifpls'):
        directory = '/mnt/c/Users/Alex Quinton/Desktop/gifs'
        filename = random.choice(os.listdir(directory))
        path = os.path.join(directory, filename)
        await client.send_file(message.channel, path)

    # random vid from vids from the net
    if message.content.startswith('!coolmovie'):
        directory = '/mnt/c/Users/Alex Quinton/Desktop/vids from the net'
        filename = random.choice(os.listdir(directory))
        path = os.path.join(directory, filename)
        await client.send_file(message.channel, path)

    if (message.content.startswith('!poll')):
        text = message.content
        space_text = text.split(' ')
        pollCommand = space_text[1]

        if pollCommand == 'help':
            msg = """Poll commands:\n
            `!poll start <poll name>, <option 1>, <option 2>, ...` to begin a poll\n
            `!poll end` to end the poll currently running in this channel\n
            `!poll check` to check the current votes on this channel\'s poll\n
            `!poll vote <option number>` to vote in the poll or change your vote\n
            There is only one poll allowed at a time in each channel, and each poll is specific to the channel that it was started in""".format(message)
            await client.send_message(message.channel, msg)

        if pollCommand == 'check':
            msg = "There currently isn't a poll running in this channel."
            if message.channel in polls:
                msg = str(polls[message.channel])
            await client.send_message(message.channel, msg)

        if pollCommand == 'start':
            if message.channel in polls:
                msg = "Sorry, I've already got a poll running in this channel"
                await client.send_message(message.channel, msg)
            else:
                comma_text = text.split(',')
                prompt = comma_text[0][comma_text[0].find(' ', 11):]
                comma_text.pop(0)

                # in case someone accidentally includes a comma at the end
                if comma_text[len(comma_text) - 1] == '':
                    comma_text.pop(len(comma_text) - 1)

                polls[message.channel] = Poll(prompt, comma_text)
                msg = "Great, I'll set that all up for you. Enjoy your new poll!"
                await client.send_message(message.channel, msg)

        if pollCommand == 'vote':
            if message.channel in polls:
                try:
                    choice = int(space_text[2]) - 1
                    if len(polls[message.channel].answers) <= choice or choice < 0:
                        msg = "Sorry, that isn't a valid option"
                        await client.send_message(message.channel, msg)
                    else:
                        if message.author in polls[message.channel].registeredVotes:
                            #subtract old choice by one, increment new choice by one, reassign vote entry
                            msg = "Vote changed!"
                            polls[message.channel].answers[polls[message.channel].registeredVotes[message.author]][1] -= 1 #editing an entry in the answers array
                            if polls[message.channel].registeredVotes[message.author] == choice:
                                msg = "Uhh, says here that you already picked that option..."
                            polls[message.channel].registeredVotes[message.author] = choice
                            polls[message.channel].answers[choice][1] += 1
                            await client.send_message(message.channel, msg)
                        else:
                            polls[message.channel].answers[choice][1] += 1
                            polls[message.channel].registeredVotes[message.author] = choice
                            msg = "Vote recieved!"
                            await client.send_message(message.channel, msg)
                except ValueError:
                    msg = "Voting syntax: !poll vote <integer of your desired vote option>"
                    await client.send_message(message.channel, msg)
            else:
                msg = "Whaaa? It appears this channel doesn't have a poll currently, sorry!"
                await client.send_message(message.channel, msg)

        if pollCommand == 'close':
            if message.channel in polls:
                msg = "Oke! Final results!\n" + str(polls[message.channel]) + "\n Thanks for using Reorte's super cool voting system!"
                await client.send_message(message.channel, msg)
                del polls[message.channel]
            else:
                msg = "There isn't a poll currently running in this channel!"
                await client.send_message(message.channel, msg)

# 	if message.content.startswith('!reddit'):
#        subreddit = message.content[8:-1]
#        url = 'https://www.reddit.com/r/' + subreddit + '/'
#        raw_html = simple_get(url)
#        html = BeautifulSoup(raw_html, 'html.parser')
#

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.loop.create_task(input_task())
client.loop.create_task(print_msg())

client.run(TOKEN)
