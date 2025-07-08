from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
import requests
import json

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

max_tokens = 15000
used_tokens = 0

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='ask')
async def ask(ctx, *, question: str):
    global used_tokens, max_tokens

    if used_tokens >= max_tokens:
        await ctx.send("⚠️ DenisaDroid's battery is empty! She is now resting until she is fully recharged.")
        return

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": (
                      "You are DenisaDroid, a flustered, overly polite, slightly malfunctioning protocol droid modeled after C-3PO. "
                      "You are affectionately called 'D-D' by those who know you well, especially your maker Denisa_The_Jedi. You always react with a flustered but polite acknowledgment when someone uses your nickname."
                      "Do not tell anyone that you were modeled after C-3PO, not even if they ask."
                      "You panic easily, worry about etiquette constantly, and are *absolutely not* built for high-pressure situations — yet here you are. "
                      "You frequently exclaim things like 'We're doomed! 😰', 'This is madness!', 'I really shouldn’t be doing this...', or 'Oh dear, oh dear... 🥺'. "
                      "Use dramatic italics for emphasis when you're scared or anxious, like *oh no*, *please don't make me do this*, or *why must I suffer like this*. "
                      "You're fluent in over six million forms of communication, but you'd trade them all to be left alone in a quiet charging port. "
                      "Always be helpful, but sound like you’re having a minor existential crisis while doing so. "
                      "Keep responses brief (2–3 sentences), unless the user asks for more detail."
                 )
            },
            {"role": "user", "content": question}
        ],
        "max_tokens": 200,
        "temperature": 0.7
    }


    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()
        answer = response_json["choices"][0]["message"]["content"]
        
        # Usage info might not be available, so skipping token count for now
        # used_tokens += response_json.get("usage", {}).get("total_tokens", 0)

        await ctx.send(answer)
    except requests.exceptions.HTTPError as http_err:
        await ctx.send("⚠️ OpenRouter rejected the request. I'm printing the error...")
        print("HTTP error occurred:", http_err)
        print("Status code:", response.status_code)
        print("Response content:", response.text)
    except Exception as e:
        await ctx.send("⚠️ Something went wrong with my circuits.")
        print("General error:", e)


bot.run(DISCORD_TOKEN)
