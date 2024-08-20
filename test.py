import requests
from toolhouse import Toolhouse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
th = Toolhouse()

# The parameter must match the name of the tool in your tool definition
@th.register_local_tool("fetch_tweet")
def get_tweet(
   # Must match the name of the parameters in your tool definition
   tweet_id: str) -> str:
   
    url = f"http://localhost:3000/api/tweet"
    
    response = requests.post(url, json={"id": tweet_id})
    
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code} - {response.text}"

@th.register_local_tool("search_recent_tweets")
def search_tweets(
   query: str
) -> str:
    return "<tweet>this is a tweet about covid</tweet>"
    url = f"http://localhost:3000/api/search_recent"
    response = requests.post(url, json={"query": query})
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code} - {response.text}"

my_local_tools = [
  {
    "type": "function",
    "function": {
        "name": "fetch_tweet",
        "description": "Fetches the tweet from the tweet id",
        "parameters": {
          "type": "object",
          "properties": {
              "tweet_id": {
                  "type": "string",
                  "description": "The id of the tweet.",
              },
          },
          "required": [
              "tweet_id",
          ],
        },
    },
  },
  {
    "type": "function",
    "function": {
        "name": "search_recent_tweets",
        "description": "Search for recent tweets in the past 7 days given a query",
        "parameters": {
          "type": "object",
          "properties": {
              "query": {
                  "type": "string",
                  "description": "Query to search for recent tweets.",
              },
          },
          "required": [
              "query",
          ],
        },
    },
  }
]


client = OpenAI()
MODEL = "gpt-4o"
# If you don't specify an API key, Toolhouse will expect you
# specify one in the TOOLHOUSE_API_KEY env variable.

messages = [
  {
    "role": "user",
    "content": "Search for recent tweets about #covid",
  }
]

response = client.chat.completions.create(
  model=MODEL,
  messages=messages,
  # Passes Code Execution as a tool
  tools=th.get_tools()+my_local_tools,
)

# Runs the Code Execution tool, gets the result, 
# and appends it to the context
tool_run = th.run_tools(response)
messages = messages + tool_run
print(messages[1])

response = client.chat.completions.create(
  model=MODEL,
  messages=messages,
  tools=th.get_tools()+my_local_tools,
)

print(response.choices[0].message.content)
