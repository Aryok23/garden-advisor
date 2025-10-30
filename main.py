"""
Garden Advisor Discord Bot - Main Entry Point
Smart Garden Assistant with LLM Agent capabilities
"""
import os
import sys
import signal
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
log_file = os.getenv('LOG_FILE', './logs/agent.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables"""
    required_vars = ['DISCORD_TOKEN', 'GROQ_API_KEY', 'WEATHER_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file")
        sys.exit(1)
    
    logger.info("Environment validation passed")

def handle_exit(sig, frame):
    """Graceful shutdown handler"""
    signal_name = signal.Signals(sig).name
    logger.info(f"Received {signal_name}. Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main entry point"""
    logger.info("Starting Garden Advisor Discord Bot...")
    
    # Validate environment
    validate_environment()
    
    # Create necessary directories
    os.makedirs('./data/chroma', exist_ok=True)
    os.makedirs('./logs', exist_ok=True)
    
    # Import and run Discord bot
    from integration.discord_bot import run_bot
    
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()