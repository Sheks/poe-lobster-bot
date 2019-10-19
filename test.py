import requests
# Here we define our query as a multi-line string
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
    'name': 'On'
}

url = 'https://graphql.anilist.co'

# Make the HTTP Api request
response = requests.post(url, json={'query': query, 'variables': variables})
print(response.json())