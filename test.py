import requests
from toolhouse import Toolhouse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
th = Toolhouse()

# The parameter must match the name of the tool in your tool definition
@th.register_local_tool("get_current_weather")
def get_weather_forecast(
   # Must match the name of the parameters in your tool definition
   latitude: float, 
   longitude: float) -> str:
   
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&forecast_days=1"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text
    else:
        return f"Error: {response.status_code} - {response.text}"

my_local_tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Retrieves the current weather for the location you specify.",
            "parameters": {
              "type": "object",
              "properties": {
                  "latitude": {
                      "type": "number",
                      "description": "The latitude of the location.",
                  },
                  "longitude": {
                      "type": "number",
                      "description": "The longitude of the location.",
                  },
              },
              "required": [
                  "latitude",
                  "longitude",
              ],
            },
        },
    }
]

client = OpenAI()
MODEL = "gpt-4o-mini"
# If you don't specify an API key, Toolhouse will expect you
# specify one in the TOOLHOUSE_API_KEY env variable.

messages = [
  {
    "role": "user",
    "content": "What's the weather in Palo Alto, CA?",
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
  tools=th.get_tools(),
)

print(response.choices[0].message.content)
