"""
Discord Bot Integration
Connects the Garden Advisor Agent to Discord
"""
import os
import logging
import discord
from discord.ext import commands

from core.agent import GardenAdvisorAgent

logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
agent = None

@bot.event
async def on_ready():
    """Called when bot is ready"""
    global agent
    agent = GardenAdvisorAgent()
    
    logger.info(f'Bot logged in as {bot.user.name} (ID: {bot.user.id})')
    print(f'Garden Advisor Bot is ready!')
    print(f'Logged in as: {bot.user.name}')
    print(f'Ready to help with garden advice!')

@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Handle direct mentions or DMs
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            # Remove bot mention from message
            content = message.content.replace(f'<@{bot.user.id}>', '').strip()
            
            if not content:
                await message.channel.send("Hi! I'm your Garden Advisor. Ask me anything about plant care! 🌱")
                return
            
            # Get user ID and process message
            user_id = str(message.author.id)
            
            try:
                response = agent.process_message(user_id, content)
                
                # Split long messages
                if len(response) > 2000:
                    chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for chunk in chunks:
                        await message.channel.send(chunk)
                else:
                    await message.channel.send(response)
                
                logger.info(f"Responded to {message.author.name}: {content[:50]}")
                
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                await message.channel.send("Sorry, I encountered an error. Please try again.")

@bot.command(name='helpme')
async def help_command(ctx):
    """Show help message"""
    help_text = """
**Garden Advisor Bot - Commands**

**How to use:**
- Mention me (@Garden Advisor) or DM me with your questions
- I can help with plant care, watering schedules, weather checks, and more!

**Commands:**
- `!helpme` - Show this help message
- `!myplants` - List your plants
- `!reminders` - Show your watering reminders
- `!clear` - Clear your conversation history
- `!weather <location>` - Check weather

**Example questions:**
- "How do I care for tomatoes?"
- "Should I water my plants today in New York?"
- "Remind me to water roses every 3 days"
- "Calculate how much water for 5 plants at 2 liters each"

**Features:**
- Personalized plant care advice
- Weather-based watering recommendations
- Memory of your plants and conversations
- Watering reminders
- Plant knowledge base
"""
    await ctx.send(help_text)

@bot.command(name='myplants')
async def my_plants_command(ctx):
    """Show user's plants"""
    user_id = str(ctx.author.id)
    plants = agent.get_user_plants(user_id)
    
    if plants:
        plants_list = '\n'.join([f"{plant}" for plant in plants])
        await ctx.send(f"**Your plants:**\n{plants_list}")
    else:
        await ctx.send("You haven't mentioned any plants yet. Tell me about your garden!")

@bot.command(name='reminders')
async def reminders_command(ctx):
    """Show user's reminders"""
    user_id = str(ctx.author.id)
    reminders = agent.tool_manager.get_user_reminders(user_id)
    
    if reminders:
        reminder_list = []
        for i, reminder in enumerate(reminders, 1):
            if reminder.get('active', True):
                reminder_list.append(f"{i}. {reminder['schedule']}")
        
        if reminder_list:
            await ctx.send(f"**Your reminders:**\n" + '\n'.join(reminder_list))
        else:
            await ctx.send("You have no active reminders.")
    else:
        await ctx.send("You haven't set any reminders yet. Try: 'Remind me to water plants every 2 days'")

@bot.command(name='clear')
async def clear_command(ctx):
    """Clear user's conversation history"""
    user_id = str(ctx.author.id)
    agent.memory_manager.clear_user_memory(user_id)
    await ctx.send("Your conversation history has been cleared.")

@bot.command(name='weather')
async def weather_command(ctx, *, location: str):
    """Check weather for a location"""
    async with ctx.typing():
        result = agent.tool_manager.get_weather(location)
        await ctx.send(result)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command. Use !helpme to see available commands.")
    else:
        logger.error(f"Command error: {error}", exc_info=True)
        await ctx.send("An error occurred while processing your command.")

def run_bot():
    """Start the Discord bot"""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        raise ValueError("DISCORD_TOKEN is required")
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token")
        raise
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
        raise