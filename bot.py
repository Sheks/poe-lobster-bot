# -*- coding: utf-8 -*-
import aiohttp
import sys
import json
import random
import logging
import io
import datetime
import re

from PIL import Image, ImageOps
from discord.ext import commands
from discord import Embed, File
from utils import BotContext, get_text_from_image, image as image_utils
from movies import TMDBMovie, AniList


logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class LobsterCommands:

    def __init__(self, ctx, session):
        self.ctx = ctx
        self.session = session

    @staticmethod
    def get_russian_command_synonyms():
        return {
            'краб': 'lobster',
            'убер_лаба': 'uber_lab',
            'курс': 'exchange_rate',
            'помощь': 'help',
            'фильм': 'movie'
        }

    def get_available_commands(self):
        return {
            '$краб ($lobster)': 'показать, кто сегодня краб.',
            '$убер_лаба ($uber_lab)': 'схема текущей убер лабы.',
            '$курс ($exchange_rate)': 'показать курс валюты (екзальты к хаосам).',
            '$фильм ($movie)': 'показать случайный фильм',
        }

    async def run(self):
        messages = self.ctx.message.content.strip().replace('$', '').split(' ')
        command = messages[0]
        message_to_command = ' '.join(messages[1:]) if len(messages) > 1 else None

        synonyms = self.get_russian_command_synonyms()

        if command in synonyms.keys():
            command = synonyms.get(command)

        try:
            await getattr(self, command)(message_to_command)
        except AttributeError as e:
            logger.error(e)
            await self.ctx.channel.send('Думай, что пишешь! Нет такой команды!')

    async def help(self, message=None):
        available_commands = self.get_available_commands()
        em = Embed(title='Команды:',
                   description='\n'.join([f'{key} - {value}' for key, value in available_commands.items()]))
        await self.ctx.channel.send(embed=em)

    async def anime(self, message=None):
        if message:
            name, poster_data = await AniList().search_anime(message)
            await self.ctx.channel.send(name, file=File(poster_data, 'anime.png'))
        else:
            await self.ctx.channel.send('name required!')

    async def movie(self, message=None):
        name, poster_data = await TMDBMovie().get_random_movie()
        await self.ctx.channel.send(name, file=File(poster_data, 'movie.png'))

    async def lobster(self, message=None):
        try:
            member_num = random.randrange(0, len(self.ctx.guild.members))
            em = Embed(title='Конечно же, {} - КРАБ!'.format(self.ctx.guild.members[member_num].name),
                       description='Достоверный факт!')
            await self.ctx.channel.send(embed=em)
        except Exception as e:
            logger.error(e)

    async def uber_lab(self, message=None):
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        url = f'https://www.poelab.com/wp-content/labfiles/{now_date}_uber.jpg'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await self.ctx.channel.send('Could not download file...')

                data = io.BytesIO(await resp.read())
                await self.ctx.channel.send(file=File(data, 'uber_laba.jpg'))

    async def exchange_rate(self, message=None):
        request_data = {'exchange': {'status': {'option': 'online'}, 'have': ['chaos'], 'want': ['exa']}}
        url = 'https://ru.pathofexile.com/api/trade/exchange/Blight'
        first_ten = []

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request_data) as resp:
                if resp.status == 200:
                    response_json = await resp.json()
                    first_ten = ','.join(response_json.get('result')[:10])

        response_json = None

        if first_ten:
            url = f'https://ru.pathofexile.com/api/trade/fetch/{first_ten}'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        response_json = await resp.json()

        if response_json:
            em = Embed(title='Первые 10 предложений',
                       description='\n'.join([i.get('item').get('note') for i in response_json['result']]))
            await self.ctx.channel.send(embed=em)


class MessageReaction:

    def __init__(self, ctx):
        self.ctx = ctx
        self.valuables = ['возвыш', 'золотое', 'каланд', 'зеркало']

    async def react_to_attachment(self, attachments: list):
        """
        Trying to find exalted or gold oil on attachment image
        """
        if attachments and attachments[0].url.endswith('png'):
            attach = attachments[0]
            url = attach.url

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        logger.error(f'Could not download file {url}')
                        return None

                    data = io.BytesIO(await resp.read())

            image = Image.open(data)
            b_a_w_image = None
            b_a_w_image_text = ''

            image_converted = ImageOps.invert(image.convert('RGB'))
            image_converted_text = get_text_from_image(image_converted)
            is_valuable_in_text = re.search(
                '|'.join(self.valuables),
                image_converted_text.lower()
            )

            if not is_valuable_in_text:
                try:
                    b_a_w_image = image_utils.make_black_and_white(image)
                except Exception as e:
                    logger.info(e)

                if b_a_w_image:
                    try:
                        b_a_w_converted_image = ImageOps.invert(b_a_w_image.convert('RGB'))
                        b_a_w_image_text = get_text_from_image(b_a_w_converted_image)
                    except Exception as e:
                        logger.info(e)

                is_valuable_in_text = re.search(
                    '|'.join(self.valuables),
                    b_a_w_image_text.lower()
                )

            if is_valuable_in_text:
                author = self.ctx.message.author.id
                emoji = '\N{THUMBS UP SIGN}'
                await self.ctx.message.add_reaction(emoji)
                await self.ctx.channel.send(f'Грац, <@!{author}>')


class PoeLobster(commands.Bot):

    def __init__(self, *args, **kwargs):
        self.description = 'To be continued'
        self.dump_channel = None
        self.owner = None

        # Configs & token
        with open('config.json') as f:
            self.config = json.load(f)

        super().__init__(command_prefix=commands.when_mentioned, description=self.description,
                         pm_help=None, *args, **kwargs)

        self.session = aiohttp.ClientSession(loop=self.loop)

        # self.server_config = ServerConfig('server_config.json')
        # logger.info(self.server_config.conf)

    def run(self):
        super().run(self.config['token'])

    async def report(self, msg):
        await self.owner.send(f'Error, context: `{msg}`')

    async def on_message(self, message):

        if message.author.id == self.user.id:
            return

        await self.wait_until_ready()

        ctx = await self.get_context(message, cls=BotContext)
        logger.info(ctx.message.content)

        lobster = LobsterCommands(ctx, self.session)
        reaction = MessageReaction(ctx)

        logger.info(ctx.message.attachments)

        if '$' in ctx.message.content:
            try:
                await lobster.run()
            except Exception as e:
                logger.error(e)

        elif ctx.message.attachments:
            await reaction.react_to_attachment(ctx.message.attachments)

    async def on_ready(self):

        # Dump channel where i can upload 10 images at once, get url and serve in embeds freely as i'd like to
        self.dump_channel = self.get_channel(self.config.get('dump_channel_id'))
        c = await self.application_info()
        self.owner = c.owner
        logger.info(f'Client logged in.\n'
                    f'{self.user.name}\n'
                    f'{self.user.id}\n'
                    '--------------------------')
