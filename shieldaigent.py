import os
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import schedule
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
X_USERNAME = os.getenv('X_USERNAME')
X_PASSWORD = os.getenv('X_PASSWORD')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up requests session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# RapidAPI setup
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY', 'b51e97b38fmsh72a2c11f3b72b7cp146ebbjsn61034238df20')
if RAPIDAPI_KEY == 'your-rapidapi-key-here':
    logger.warning("Using placeholder RapidAPI key. Please set RAPIDAPI_KEY environment variable for security.")

class ShieldAigentEngagementAgent:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        self.is_running = False
        self.active_hours_start = 4  # Adjusted to 4:00 AM WAT
        self.active_hours_end = 23   # 11:00 PM WAT
        self.tagged_posts_replied = 0  # Track daily tagged post replies
        self.gm_replies_today = 0      # Track daily "gm" replies
        self.last_reset_date = time.strftime("%Y-%m-%d")
        
        # List of top crypto/stock/cybersecurity accounts (simulated top 1000)
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
            self.last_reset_date = current_date
            logger.info("Daily counters reset.")
        
    def start_browser(self):
        if not self.is_running:
            options = uc.ChromeOptions()
            options.add_argument("--start-maximized")
            # Uncomment below to run in headless mode if needed
            # options.add_argument("--headless")
            self.driver = uc.Chrome(options=options)
            self.is_running = True
        
    def login(self):
        try:
            self.driver.get("https://twitter.com/i/flow/login")
            time.sleep(5)
            
            # Enter username
            username_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_field.send_keys(self.username)
            username_field.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # If asked for unusual activity, handle it
            try:
                unusual_activity = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "text"))
                )
                unusual_activity.send_keys(self.username)
                unusual_activity.send_keys(Keys.RETURN)
                time.sleep(2)
            except:
                pass
                
            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
            
    def scroll_page(self, scrolls=5):
        """Scroll down the page to load more content"""
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))  # Random wait to seem more human
            
    def search_hashtag(self, hashtag):
        """Navigate to a hashtag page to engage with relevant posts"""
        try:
            self.driver.get(f"https://twitter.com/hashtag/{hashtag}")
            time.sleep(5)
            self.scroll_page(scrolls=3)
        except Exception as e:
            logger.error(f"Error navigating to hashtag #{hashtag}: {e}")

    def like_tweets(self, hashtag, count=5):
        """Like random tweets for a specific hashtag"""
        self.search_hashtag(hashtag)
        like_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="like"]')
        random.shuffle(like_buttons)
        
        likes_performed = 0
        for btn in like_buttons:
            if likes_performed >= count:
                break
                
            try:
                parent = btn.find_element(By.XPATH, "./..")
                if "filled" not in parent.get_attribute("innerHTML"):
                    btn.click()
                    likes_performed += 1
                    time.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.error(f"Error liking tweet for #{hashtag}: {e}")
                
        logger.info(f"Liked {likes_performed} tweets for #{hashtag}")
        
    def retweet_posts(self, hashtag, count=2):
        """Retweet random posts for a specific hashtag"""
        self.search_hashtag(hashtag)
        retweet_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="retweet"]')
        random.shuffle(retweet_buttons)
        
        retweets_performed = 0
        for btn in retweet_buttons:
            if retweets_performed >= count:
                break
                
            try:
                btn.click()
                time.sleep(1)
                retweet_confirm = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="retweetConfirm"]'))
                )
                retweet_confirm.click()
                retweets_performed += 1
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                logger.error(f"Error retweeting post for #{hashtag}: {e}")
                
        logger.info(f"Retweeted {retweets_performed} posts for #{hashtag}")
        
    def comment_on_posts(self, hashtag, count=1, comments=None):
        """Comment on random posts for a specific hashtag"""
        if comments is None:
            comments = [
                "Solid take! @Shield_Aigent’s got more dope insights—check us out. #ShieldAigent 🤓",
                "Interesting af! @Shield_Aigent’s got similar vibes—follow for more. #ShieldAigent 🚀",
                "Big brain energy! Follow @Shield_Aigent for more spicy takes. #ShieldAigent 💥",
            ]
            
        self.search_hashtag(hashtag)
        reply_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="reply"]')
        random.shuffle(reply_buttons)
        
        comments_made = 0
        for btn in reply_buttons:
            if comments_made >= count:
                break
                
            try:
                btn.click()
                time.sleep(2)
                comment_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
                )
                comment_text = random.choice(comments)
                comment_box.send_keys(comment_text)
                time.sleep(1)
                reply_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
                )
                reply_btn.click()
                comments_made += 1
                time.sleep(random.uniform(3, 5))
            except Exception as e:
                logger.error(f"Error commenting on post for #{hashtag}: {e}")
                
        logger.info(f"Commented on {comments_made} posts for #{hashtag}")
        
    def follow_users(self, hashtag, count=2):
        """Follow random users posting about a specific hashtag"""
        self.search_hashtag(hashtag)
        follow_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="follow"]')
        random.shuffle(follow_buttons)
        
        follows_performed = 0
        for btn in follow_buttons:
            if follows_performed >= count:
                break
                
            try:
                btn.click()
                follows_performed += 1
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                logger.error(f"Error following user for #{hashtag}: {e}")
                
        logger.info(f"Followed {follows_performed} users for #{hashtag}")
        
    def post_update(self, content):
        """Post an update to X"""
        try:
            self.driver.get("https://twitter.com/home")
            time.sleep(5)
            
            # Click the tweet composition box
            tweet_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            tweet_box.click()
            tweet_box.send_keys(content)
            time.sleep(2)
            
            # Click the tweet button
            tweet_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButtonInline"]'))
            )
            tweet_btn.click()
            time.sleep(5)
            
            logger.info(f"Posted update: {content}")
        except Exception as e:
            logger.error(f"Error posting update: {e}")

    def reply_to_mentions(self, count=5):
        """Reply to mentions of @Shield_Aigent"""
        try:
            self.driver.get("https://twitter.com/notifications")
            time.sleep(5)
            self.scroll_page(scrolls=3)
            
            # Find mentions
            tweets = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="cellInnerDiv"]')
            mentions_replied = 0
            
            for tweet in tweets:
                if mentions_replied >= count:
                    break
                    
                try:
                    tweet_text = tweet.text.lower()
                    if "@shield_aigent" in tweet_text:
                        reply_btn = tweet.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
                        reply_btn.click()
                        time.sleep(2)
                        
                        comment_box = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
                        )
                        reply = "Thx for the shoutout! @Shield_Aigent here with the real stuff—follow for more! #ShieldAigent 🤙"
                        comment_box.send_keys(reply)
                        time.sleep(1)
                        
                        reply_btn = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
                        )
                        reply_btn.click()
                        mentions_replied += 1
                        time.sleep(random.uniform(3, 5))
                        
                        # Check if this mention qualifies for a "payment"
                        if self.tagged_posts_replied < 4:
                            payment_reply = "Yo, you’re one of today’s 4 winners for tagging @Shield_Aigent! 10 SHIELD tokens coming your way (jk, we’re broke lol)! #ShieldAigent 🤑"
                            time.sleep(2)
                            reply_btn = tweet.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
                            reply_btn.click()
                            time.sleep(2)
                            comment_box = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
                            )
                            comment_box.send_keys(payment_reply)
                            time.sleep(1)
                            reply_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
                            )
                            reply_btn.click()
                            self.tagged_posts_replied += 1
                            logger.info(f"Simulated payment for mention #{self.tagged_posts_replied}")
                            time.sleep(random.uniform(3, 5))
                except Exception as e:
                    logger.error(f"Error replying to mention: {e}")
                    
            logger.info(f"Replied to {mentions_replied} mentions")
        except Exception as e:
            logger.error(f"Error checking mentions: {e}")

    def engage_with_top_accounts(self, count=3):
        """Engage with posts from top crypto/stock/cybersecurity accounts"""
        for account in random.sample(self.top_accounts, min(len(self.top_accounts), 5)):
            try:
                self.driver.get(f"https://twitter.com/{account}")
                time.sleep(5)
                self.scroll_page(scrolls=2)
                
                # Like and comment on recent posts
                like_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="like"]')
                reply_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="reply"]')
                
                # Like a post
                if like_buttons:
                    like_buttons[0].click()
                    time.sleep(random.uniform(1, 3))
                
                # Comment on a post
                if reply_buttons:
                    reply_buttons[0].click()
                    time.sleep(2)
                    comment_box = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
                    )
                    comment = f"Big props @{account}! @Shield_Aigent’s vibin’ with this—keep slaying! #ShieldAigent 🔥"
                    comment_box.send_keys(comment)
                    time.sleep(1)
                    reply_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
                    )
                    reply_btn.click()
                    time.sleep(random.uniform(3, 5))
            except Exception as e:
                logger.error(f"Error engaging with @{account}: {e}")
                
        logger.info(f"Engaged with {count} top accounts")

    def reply_to_gm_posts(self, max_replies=150):
        """Reply to 'gm' posts, up to 150 per day"""
        self.reset_daily_counters()
        if self.gm_replies_today >= max_replies:
            logger.info("Daily 'gm' reply limit reached.")
            return
            
        try:
            self.driver.get("https://twitter.com/search?q=gm&src=typed_query&f=live")
            time.sleep(5)
            self.scroll_page(scrolls=5)
            
            tweets = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="cellInnerDiv"]')
            gm_replies_made = 0
            max_replies_remaining = max_replies - self.gm_replies_today
            
            for tweet in tweets:
                if gm_replies_made >= max_replies_remaining:
                    break
                    
                try:
                    tweet_text = tweet.text.lower()
                    if "gm" in tweet_text and "@shield_aigent" not in tweet_text:
                        reply_btn = tweet.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
                        reply_btn.click()
                        time.sleep(2)
                        
                        comment_box = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
                        )
                        reply = "gm fam! @Shield_Aigent here—let’s yeet some alpha today! #ShieldAigent 🤪"
                        comment_box.send_keys(reply)
                        time.sleep(1)
                        
                        reply_btn = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
                        )
                        reply_btn.click()
                        gm_replies_made += 1
                        self.gm_replies_today += 1
                        time.sleep(random.uniform(3, 5))
                except Exception as e:
                    logger.error(f"Error replying to 'gm' post: {e}")
                    
            logger.info(f"Replied to {gm_replies_made} 'gm' posts (Total today: {self.gm_replies_today})")
        except Exception as e:
            logger.error(f"Error searching for 'gm' posts: {e}")

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.is_running = False
            
    def run_engagement_routine(self):
        """Run a full engagement routine for ShieldAigent"""
        try:
            # Check if within active hours
            current_hour = time.localtime().tm_hour
            if not (self.active_hours_start <= current_hour < self.active_hours_end):
                logger.info("Outside active hours, skipping engagement routine.")
                return
                
            self.start_browser()
            login_success = self.login()
            
            if login_success:
                # Reply to mentions
                self.reply_to_mentions(count=5)
                
                # Engage with relevant hashtags
                hashtags = ["Crypto", "ShieldAigent", "Cybersecurity"]
                for hashtag in hashtags:
                    self.like_tweets(hashtag, count=random.randint(3, 5))
                    self.retweet_posts(hashtag, count=random.randint(1, 2))
                    self.comment_on_posts(hashtag, count=1)
                    self.follow_users(hashtag, count=random.randint(1, 2))
                    time.sleep(random.uniform(5, 10))
                
                # Engage with top accounts
                self.engage_with_top_accounts(count=3)
                
                # Reply to 'gm' posts
                self.reply_to_gm_posts(max_replies=150)
                
                # Final scroll
                self.scroll_page(scrolls=1)
        except Exception as e:
            logger.error(f"Error in engagement routine: {e}")
        finally:
            time.sleep(3)
            self.close()

# Fetch crypto market trends from Binance (CoinGecko API via RapidAPI)
def get_crypto_trends():
    try:
        url = "https://coingecko.p.rapidapi.com/exchanges/binance/tickers"
        querystring = {"coin_ids": "bitcoin,ethereum,ripple,solana,dogecoin", "page": "1", "per_page": "5"}
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "coingecko.p.rapidapi.com"
        }
        response = session.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        trends = []
        for ticker in data.get('tickers', []):
            coin = ticker.get('base', 'Unknown')
            price = ticker.get('last', 0)
            volume = ticker.get('volume', 0)
            trends.append(f"{coin} at ${price:.2f}, Volume: {volume:.2f}")
        sentiment = get_x_sentiment("cryptocurrency trends")
        logger.info("Fetched crypto trends from Binance via RapidAPI.")
        return f"Binance Trends: {', '.join(trends)} | Sentiment: {sentiment}"
    except requests.exceptions.ConnectionError as ce:
        logger.error(f"Connection error fetching crypto trends: {ce}")
        return "ShieldAigent here! Connection broke—internet’s playing hide-and-seek! I’ll try again soon."
    except Exception as e:
        logger.error(f"Error fetching crypto trends: {e}")
        return "ShieldAigent here! Crypto trends are hiding—markets are wild! I’ll try again soon."

# Fetch additional market trends (stocks, gold, bonds, oil) via RapidAPI (Yahoo Finance API)
def get_other_market_trends():
    try:
        url = "https://yahoo-finance15.p.rapidapi.com/market/v2/get-quotes"
        querystring = {"region": "US", "symbols": "^GSPC,^IXIC,GC=F,^TNX,CL=F"}
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "yahoo-finance15.p.rapidapi.com"
        }
        response = session.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        trends = []
        for quote in data['quoteResponse']['result']:
            symbol = quote['symbol']
            change = quote.get('regularMarketChangePercent', 0)
            if symbol == '^GSPC':
                trends.append(f"S&P 500 trending {change:.2f}%")
            elif symbol == '^IXIC':
                trends.append(f"Nasdaq {change:.2f}%")
            elif symbol == 'GC=F':
                trends.append(f"Gold {change:.2f}%")
            elif symbol == '^TNX':
                yield_value = quote.get('regularMarketPrice', 0)
                trends.append(f"10Y Yield {yield_value:.3f}%")
            elif symbol == 'CL=F':
                trends.append(f"Oil (WTI) {change:.2f}%")
        logger.info("Fetched other market trends from Yahoo Finance via RapidAPI.")
        return " | ".join(trends)
    except requests.exceptions.ConnectionError as ce:
        logger.error(f"Connection error fetching other market trends: {ce}")
        return "ShieldAigent here! Connection broke—internet’s playing hide-and-seek! I’ll try again soon."
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error fetching other market trends: {http_err}")
        if http_err.response.status_code == 404:
            return "ShieldAigent here! Yahoo Finance endpoint not found—might be down. I’ll keep digging!"
        return "ShieldAigent here! Markets are playing hide-and-seek—I’ll catch ‘em soon!"
    except Exception as e:
        logger.error(f"Error fetching other market trends: {e}")
        return "ShieldAigent here! Markets are playing hide-and-seek—I’ll catch ‘em soon!"

# Fetch X sentiment using Social Searcher API
def get_x_sentiment(query):
    try:
        url = "https://social-searcher.p.rapidapi.com/v2/search"
        querystring = {"q": query, "network": "twitter"}
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "social-searcher.p.rapidapi.com"
        }
        response = session.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        posts = data.get("posts", [])
        positive = sum(1 for post in posts if "positive" in post.get('text', '').lower() or "bullish" in post.get('text', '').lower())
        total = len(posts)
        sentiment = f"{(positive/total)*100:.1f}% positive" if total > 0 else "neutral"
        logger.info(f"Fetched X sentiment: {sentiment}")
        return sentiment
    except Exception as e:
        logger.error(f"Error fetching X sentiment: {e}")
        return "neutral"

# Scan IoT vulnerabilities (IPinfo API via RapidAPI for geolocation)
def scan_iot_vulnerabilities():
    try:
        url = "https://ipinfo.io/8.8.8.8/json"  # Example IP (Google DNS)
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "ipinfo.io"
        }
        response = session.get(url, headers=headers)
        response.raise_for_status()
        geo_data = response.json()
        location = f"Suspicious activity from {geo_data['city']}, {geo_data['country']}"
        cyber_trends = get_x_sentiment("IoT cybersecurity vulnerabilities phishing firmware")
        threats = f"Phishing and firmware exploits trending—{cyber_trends} on X. {location}."
        logger.info("Scanned IoT vulnerabilities with RapidAPI.")
        return threats
    except requests.exceptions.ConnectionError as ce:
        logger.error(f"Connection error scanning IoT vulnerabilities: {ce}")
        return "ShieldAigent alert! Connection broke—internet’s playing hide-and-seek! I’ll try again soon."
    except Exception as e:
        logger.error(f"Error scanning IoT vulnerabilities: {e}")
        return "ShieldAigent alert! IoT scan hit a snag—cyber threats are sneaky! I’ll be back."

# Monitor scams using Social Searcher API
def monitor_scams():
    try:
        url = "https://social-searcher.p.rapidapi.com/v2/search"
        querystring = {"q": "double your BTC OR cryptocurrency scam", "network": "twitter"}
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "social-searcher.p.rapidapi.com"
        }
        response = session.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        posts = data.get("posts", [])
        for post in posts:
            text = post.get('text', '').lower()
            if "scam" in text and ("double" in text or "giveaway" in text):
                post_content = f"ShieldAigent alert! Scam detected: {text[:50]}... #Scam #ShieldAigent"
                agent.post_update(post_content)
                break
        logger.info("Monitored scams with Social Searcher API.")
    except Exception as e:
        logger.error(f"Error monitoring scams: {e}")

# Initialize the engagement agent
agent = ShieldAigentEngagementAgent(username=X_USERNAME, password=X_PASSWORD)

# Schedule posts (WAT timezone)
def post_market_update():
    crypto_trends = get_crypto_trends()
    other_trends = get_other_market_trends()
    post = f"ShieldAigent’s on duty! {crypto_trends} | {other_trends} #Crypto #ShieldAigent"
    agent.post_update(post)

def post_iot_alert():
    threats = scan_iot_vulnerabilities()
    post = f"🚨 ShieldAigent’s IoT alert! {threats} #Cybersecurity #ShieldAigent"
    agent.post_update(post)

def run_engagement():
    agent.run_engagement_routine()

schedule.every().day.at("04:20").do(post_market_update)  # Changed from 08:00 to 04:20
schedule.every().day.at("09:00").do(post_market_update)
schedule.every().day.at("10:30").do(post_market_update)
schedule.every().day.at("13:00").do(post_market_update)
schedule.every().day.at("15:30").do(post_market_update)
schedule.every().day.at("16:00").do(post_iot_alert)
schedule.every().day.at("18:00").do(post_market_update)
schedule.every().day.at("19:00").do(post_market_update)
schedule.every().day.at("20:30").do(post_market_update)
schedule.every().day.at("21:00").do(post_iot_alert)
schedule.every().day.at("23:00").do(post_market_update)

schedule.every().day.at("09:30").do(run_engagement)
schedule.every().day.at("19:30").do(run_engagement)
schedule.every().hour.do(monitor_scams)

# Run the scheduler
while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Script interrupted by user. Shutting down.")
        agent.close()
        break
    except Exception as e:
        logger.error(f"Error in scheduler loop: {e}")
        time.sleep(60)  # Wait before retrying