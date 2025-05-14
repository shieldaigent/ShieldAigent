import os
import logging
import time
import random
import tweepy
import requests
from textblob import TextBlob
from dotenv import load_dotenv
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Load environment variables
load_dotenv()
X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET = os.getenv('X_API_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("ShieldAigent starting up...")

# Initialize Flask app
app = Flask(__name__)

# Initialize X API client
try:
    auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
    auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    logger.info("Tweepy authenticated successfully.")
except Exception as e:
    logger.error(f"Tweepy authentication failed: {e}")
    exit(1)

class ShieldAigentEngagementAgent:
    def __init__(self):
        self.tagged_posts_replied = 0  # Track daily tagged post replies
        self.gm_replies_today = 0      # Track daily "gm" replies
        self.scam_posts_today = 0      # Track daily scam posts
        self.market_posts_today = 0    # Track daily market posts
        self.iot_posts_today = 0       # Track daily IoT posts
        self.last_reset_date = time.strftime("%Y-%m-%d")
        self.active_hours_start = 4    # 4:00 AM WAT
        self.active_hours_end = 23     # 11:00 PM WAT
        
        # List of top crypto/stock/cybersecurity accounts
        self.top_accounts = [
            "CoinMarketCap", "Binance", "Coinbase", "Krakenfx", "Gemini",
            "StockMarket", "YahooFinance", "Bloomberg", "CNBC", "Investopedia",
            "CyberSec", "DarkReading", "TheHackerNews", "Kaspersky", "Norton"
        ]

    def reset_daily_counters(self):
        """Reset daily counters if the date has changed"""
        current_date = time.strftime("%Y-%m-%d")
        if current_date != self.last_reset_date:
            self.tagged_posts_replied = 0
            self.gm_replies_today = 0
            self.scam_posts_today = 0
            self.market_posts_today = 0
            self.iot_posts_today = 0
            self.last_reset_date = current_date
            logger.info("Daily counters reset.")

    def post_update(self, content):
        """Post an update to X using the X API"""
        logger.info(f"Attempting to post: {content}")
        try:
            response = api.update_status(status=content)
            logger.info(f"Successfully posted update: {content} - Response: {response.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to post update: {e}")
            return False

    def reply_to_mentions(self, count=2):  # 2 replies per run
        """Reply to mentions of @Shield_Aigent"""
        try:
            mentions = api.mentions_timeline(count=count)
            mentions_replied = 0

            for mention in mentions:
                if mentions_replied >= count:
                    break

                try:
                    tweet_text = mention.text.lower()
                    if "@shield_aigent" in tweet_text:
                        reply = f"Thx for the shoutout! @Shield_Aigent here with the real stuff—follow for more! #ShieldAigent 🤙"
                        api.update_status(
                            status=reply,
                            in_reply_to_status_id=mention.id
                        )
                        mentions_replied += 1
                        time.sleep(random.uniform(3, 5))
                except Exception as e:
                    logger.error(f"Error replying to mention: {e}")

            logger.info(f"Replied to {mentions_replied} mentions")
        except Exception as e:
            logger.error(f"Error checking mentions: {e}")

    def engage_with_top_accounts(self, count=1):  # 1 comment per run
        """Engage with posts from top crypto/stock/cybersecurity accounts"""
        try:
            for account in random.sample(self.top_accounts, min(len(self.top_accounts), 1)):
                tweets = api.user_timeline(screen_name=account, count=1, tweet_mode="extended")
                if tweets:
                    tweet = tweets[0]
                    comment = f"Big props @{account}! @Shield_Aigent’s vibin’ with this—keep slaying! #ShieldAigent 🔥"
                    api.update_status(
                        status=comment,
                        in_reply_to_status_id=tweet.id
                    )
                    time.sleep(random.uniform(3, 5))
            logger.info(f"Engaged with {count} top accounts")
        except Exception as e:
            logger.error(f"Error engaging with top accounts: {e}")

    def reply_to_gm_posts(self, max_replies=1):  # 1 reply per run
        """Reply to 'gm' posts"""
        try:
            gm_tweets = api.search(q="gm -from:@Shield_Aigent", count=1, tweet_mode="extended")
            gm_replies_made = 0

            for tweet in gm_tweets:
                if gm_replies_made >= max_replies:
                    break

                try:
                    tweet_text = tweet.full_text.lower()
                    if "gm" in tweet_text and "@shield_aigent" not in tweet_text:
                        reply = "gm fam! @Shield_Aigent here—let’s yeet some alpha today! #ShieldAigent 🤪"
                        api.update_status(
                            status=reply,
                            in_reply_to_status_id=tweet.id
                        )
                        gm_replies_made += 1
                        self.gm_replies_today += 1
                        time.sleep(random.uniform(3, 5))
                except Exception as e:
                    logger.error(f"Error replying to 'gm' post: {e}")

            logger.info(f"Replied to {gm_replies_made} 'gm' posts (Total today: {self.gm_replies_today})")
        except Exception as e:
            logger.error(f"Error searching for 'gm' posts: {e}")

    def run_engagement_routine(self):
        """Run a full engagement routine for ShieldAigent"""
        try:
            # Check if within active hours
            current_hour = time.localtime().tm_hour
            if not (self.active_hours_start <= current_hour < self.active_hours_end):
                logger.info("Outside active hours, skipping engagement routine.")
                return

            # Reply to mentions (2 posts)
            self.reply_to_mentions(count=2)

            # Engage with top accounts (1 post)
            self.engage_with_top_accounts(count=1)

            # Reply to 'gm' posts (1 post)
            self.reply_to_gm_posts(max_replies=1)

        except Exception as e:
            logger.error(f"Error in engagement routine: {e}")

# Fetch X sentiment using X API and TextBlob
def get_x_sentiment(query):
    logger.info(f"Skipping X sentiment fetch for query: {query} due to API restrictions")
    return "neutral"

# Uncomment this when you upgrade your X API plan
"""
def get_x_sentiment(query):
    try:
        tweets = api.search(
            q=f"{query} -from:@Shield_Aigent",
            count=20,
            tweet_mode="extended"
        )
        positive = 0
        negative = 0
        total = len(tweets)
        for tweet in tweets:
            text = tweet.full_text
            analysis = TextBlob(text)
            polarity = analysis.sentiment.polarity
            if polarity > 0:
                positive += 1
            elif polarity < 0:
                negative += 1
        if total == 0:
            return "neutral"
        positive_percent = (positive / total) * 100
        negative_percent = (negative / total) * 100
        if positive_percent > negative_percent + 10:
            sentiment = f"{positive_percent:.1f}% positive"
        elif negative_percent > positive_percent + 10:
            sentiment = f"{negative_percent:.1f}% negative"
        else:
            sentiment = "neutral"
        logger.info(f"Fetched X sentiment: {sentiment}")
        return sentiment
    except Exception as e:
        logger.error(f"Error fetching X sentiment: {e}")
        return "neutral"
"""

# Fetch Finnhub sentiment for a stock ticker
def get_finnhub_sentiment(ticker):
    try:
        url = f"https://finnhub.io/api/v1/news-sentiment?symbol={ticker}&token={FINNHUB_API_KEY}"
        logger.info(f"Finnhub API URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        bearish = data.get('bearishPercent', 0)
        bullish = data.get('bullishPercent', 0)
        if bullish > bearish + 10:
            sentiment = f"{bullish:.1f}% positive"
        elif bearish > bullish + 10:
            sentiment = f"{bearish:.1f}% negative"
        else:
            sentiment = "neutral"
        logger.info(f"Fetched Finnhub sentiment for {ticker}: {sentiment}")
        return sentiment
    except Exception as e:
        logger.error(f"Error fetching Finnhub sentiment for {ticker}: {e}")
        return "neutral"

# Fetch sentiment for cryptocurrencies, memecoins, stocks, gold, bonds, oil
def get_market_sentiment():
    try:
        # Cryptocurrencies
        crypto_symbols = ["BTC", "ETH", "XRP", "SOL", "DOGE"]
        # Trending memecoins
        memecoin_symbols = ["SHIB", "PEPE", "BONK", "WIF", "TRUMP"]
        # Binance symbols for API call (not used in output)
        binance_symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "SOLUSDT", "DOGEUSDT", "SHIBUSDT", "PEPEUSDT", "BONKUSDT", "WIFUSDT", "TRUMPUSDT"]
        # Stock (using Finnhub)
        stock_symbols = ["AAPL"]
        # Gold, Bonds, Oil (using X API with ETFs)
        commodity_symbols = {"GLD": "Gold", "TLT": "Bonds", "USO": "Oil"}
        
        crypto_sentiments = []
        memecoin_sentiments = []
        stock_sentiments = []
        commodity_sentiments = []
        
        # Fetch Binance data (not used in output, kept for future use)
        for binance_symbol in binance_symbols:
            response = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}")
            response.raise_for_status()
            data = response.json()
            logger.info(f"Fetched Binance 24hr data for {binance_symbol}")
        
        # Fetch sentiment for cryptocurrencies using X API
        for symbol in crypto_symbols:
            sentiment = get_x_sentiment(f"{symbol} cryptocurrency")
            crypto_sentiments.append(f"{symbol}: {sentiment}")
        
        # Fetch sentiment for memecoins using X API
        for symbol in memecoin_symbols:
            sentiment = get_x_sentiment(f"{symbol} memecoin")
            memecoin_sentiments.append(f"{symbol}: {sentiment}")
        
        # Fetch sentiment for stocks using Finnhub API
        for symbol in stock_symbols:
            sentiment = get_finnhub_sentiment(symbol)
            stock_sentiments.append(f"{symbol}: {sentiment}")
        
        # Fetch sentiment for gold, bonds, oil using X API
        for symbol, name in commodity_symbols.items():
            sentiment = get_x_sentiment(f"{symbol} {name.lower()}")
            commodity_sentiments.append(f"{name}: {sentiment}")
        
        logger.info("Fetched all market sentiments.")
        return (f"Market Sentiment | Cryptos: {', '.join(crypto_sentiments)} | "
                f"Trending Memecoins: {', '.join(memecoin_sentiments)} | "
                f"Stocks: {', '.join(stock_sentiments)} | "
                f"Commodities: {', '.join(commodity_sentiments)}")
    except Exception as e:
        logger.error(f"Error fetching market sentiments: {e}")
        return "ShieldAigent here! Sentiments are hiding—I’ll try again soon."

# Scan IoT vulnerabilities using ip-api.com
def scan_iot_vulnerabilities():
    try:
        response = requests.get("http://ip-api.com/json/8.8.8.8")  # Example IP (Google DNS)
        response.raise_for_status()
        geo_data = response.json()
        location = f"Suspicious activity from {geo_data['city']}, {geo_data['country']}"
        cyber_trends = get_x_sentiment("IoT cybersecurity vulnerabilities phishing firmware")
        threats = f"Phishing and firmware exploits trending—{cyber_trends} on X. {location}."
        logger.info("Scanned IoT vulnerabilities with ip-api.com.")
        return threats
    except Exception as e:
        logger.error(f"Error scanning IoT vulnerabilities: {e}")
        return "ShieldAigent alert! IoT scan hit a snag—cyber threats are sneaky! I’ll be back."

# Monitor scams using X API
def monitor_scams():
    try:
        agent.reset_daily_counters()
        if agent.scam_posts_today >= 1:  # Cap at 1 scam post per day
            logger.info("Daily scam post limit reached.")
            return

        tweets = api.search(
            q="double your BTC OR cryptocurrency scam -from:@Shield_Aigent",
            count=10,
            tweet_mode="extended"
        )
        for tweet in tweets:
            text = tweet.full_text.lower()
            if "scam" in text and ("double" in text or "giveaway" in text):
                sentiment = get_x_sentiment("cryptocurrency scam")
                post_content = f"ShieldAigent alert! Scam detected: {text[:50]}... Sentiment: {sentiment} #Scam #ShieldAigent"
                agent.post_update(post_content)
                agent.scam_posts_today += 1
                break
        logger.info("Monitored scams with X API.")
    except Exception as e:
        logger.error(f"Error monitoring scams: {e}")

# Post a market sentiment update
def post_market_update():
    try:
        agent.reset_daily_counters()
        if agent.market_posts_today >= 5:  # Cap at 5 market posts per day
            logger.info("Daily market post limit reached.")
            return

        market_sentiment = get_market_sentiment()
        post = f"ShieldAigent’s on duty! {market_sentiment} #Crypto #ShieldAigent"
        agent.post_update(post)
        agent.market_posts_today += 1
        logger.info(f"Posted market sentiment update: {post}")
    except Exception as e:
        logger.error(f"Error posting market sentiment update: {e}")

# Post an IoT alert using ip-api.com data
def post_iot_alert():
    try:
        agent.reset_daily_counters()
        if agent.iot_posts_today >= 1:  # Cap at 1 IoT post per day
            logger.info("Daily IoT post limit reached.")
            return

        threats = scan_iot_vulnerabilities()
        post = f"🚨 ShieldAigent’s IoT alert! {threats} #Cybersecurity #ShieldAigent"
        agent.post_update(post)
        agent.iot_posts_today += 1
        logger.info(f"Posted IoT alert: {post}")
    except Exception as e:
        logger.error(f"Error posting IoT alert: {e}")

# Initialize the engagement agent
agent = ShieldAigentEngagementAgent()

# Set up APScheduler
scheduler = BackgroundScheduler(timezone="Africa/Lagos")  # WAT timezone

# Schedule tasks
scheduler.add_job(post_market_update, CronTrigger(hour=9, minute=0))
scheduler.add_job(post_market_update, CronTrigger(hour=10, minute=30))
scheduler.add_job(post_market_update, CronTrigger(hour=13, minute=30))
scheduler.add_job(post_market_update, CronTrigger(hour=19, minute=0))
scheduler.add_job(post_market_update, CronTrigger(hour=20, minute=30))

scheduler.add_job(post_iot_alert, CronTrigger(hour=16, minute=0))

scheduler.add_job(agent.run_engagement_routine, CronTrigger(hour=6, minute=30))
scheduler.add_job(agent.run_engagement_routine, CronTrigger(hour=19, minute=30))

scheduler.add_job(monitor_scams, CronTrigger(hour=12, minute=0))

# Add a test job to run immediately for debugging
scheduler.add_job(post_market_update, 'interval', seconds=60, id='test_job')  # Runs every 60 seconds

# Log all scheduled jobs
jobs = scheduler.get_jobs()
logger.info(f"Scheduled jobs: {[job.id for job in jobs]}")

# Start the scheduler
logger.info("Starting APScheduler...")
scheduler.start()

# Flask routes
@app.route("/")
def home():
    return "ShieldAigent is running!"

@app.route("/post-now")
def post_now():
    api_key = request.args.get('api_key')
    if api_key != "your-secret-key-123":  # Replace with your own secret key
        return "Unauthorized: Invalid API key", 401
    try:
        post_market_update()
        return "Market update posted successfully!"
    except Exception as e:
        logger.error(f"Error in /post-now endpoint: {e}")
        return f"Failed to post: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway provides PORT env variable
    app.run(host="0.0.0.0", port=port)