import aiohttp
import logging
import io

from random import randrange
from datetime import timedelta, datetime

logger = logging.getLogger()


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (start + timedelta(seconds=random_second)).strftime('%Y-%m-%d')


class TMDBMovie:

    async def get_random_movie(self):

        d1 = datetime.strptime('2010-1-1', '%Y-%m-%d')
        d2 = datetime.strptime('2019-01-01', '%Y-%m-%d')

        date_dte = random_date(d1, d2)

        random_item = randrange(0, 20)

        url = 'https://api.themoviedb.org/3/discover/movie?api_key=8d2e58163fc7454876e382341e13c6c1&language=en-US' \
              '&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&vote_average.gte=7.5' \
              '&vote_count.gte=50'
        date_query = f'primary_release_date.gte={date_dte}'

        url = f'{url}&{date_query}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f'Could not download file {url}')
                else:
                    response_json = await resp.json()

        random_page = randrange(1, response_json['total_pages'])

        url = f'{url}&{date_query}&page={random_page}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error(f'Could not download file {url}')
                else:
                    response_json = await resp.json()

        random_movie = response_json['results'][random_item]

        name = random_movie['original_title']

        poster_path = random_movie['poster_path']
        poster_path = f'http://image.tmdb.org/t/p/w185/{poster_path}'
        poster_image_data = None

        async with aiohttp.ClientSession() as session:
            async with session.get(poster_path) as resp:
                if resp.status != 200:
                    logger.error(f'Could not download file {url}')
                else:
                    poster_image_data = io.BytesIO(await resp.read())

        return name, poster_image_data
