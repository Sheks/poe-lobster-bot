import aiohttp
import logging
import io

logger = logging.getLogger()


class AniList:

    @staticmethod
    async def search_anime(name):
        query = '''
        query ($name: String) { # Define which variables will be used in the query (id)
          Media (search: $name, type: ANIME) { # Insert our variables into the query arguments (id) (type: ANIME is hard-coded in the query)
            id
            title {
              romaji
              english
              native
              
            }
            bannerImage
          }
        
        }
        '''

        # Define our query variables and values that will be used in the query request
        variables = {
            'name': name
        }

        url = 'https://graphql.anilist.co'

        # Make the HTTP Api request
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'query': query, 'variables': variables}) as resp:
                if resp.status != 200:
                    logger.error(f'Could not download file {url}')
                else:
                    response_json = await resp.json()

        banner_path = response_json['data']['Media']['title']['bannerImage']
        name = response_json['data']['Media']['title']['english']

        async with aiohttp.ClientSession() as session:
            async with session.get(banner_path) as resp:
                if resp.status != 200:
                    logger.error(f'Could not download file {url}')
                else:
                    poster_image_data = io.BytesIO(await resp.read())

        return name, poster_image_data
