```python
import os
import requests
import logging
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhaleTracker:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = Bot(token=self.token)
        
    def get_whale_transactions(self):
        """دریافت تراکنش‌های بزرگ از mempool.space"""
        try:
            logger.info("🔍 در حال بررسی تراکنش‌های بیت‌کوین...")
            response = requests.get('https://mempool.space/api/mempool', timeout=10)
            mempool = response.json()
            
            large_txs = []
            for tx_id, tx_data in list(mempool.items())[:100]:  # بررسی 100 تراکنش اول
                if tx_data.get('fee', 0) > 50000:  # فیلتر کارمزد بالا
                    large_txs.append({
                        'id': tx_id,
                        'fee': tx_data['fee'],
                        'size': tx_data['size']
                    })
            
            logger.info(f"✅ {len(large_txs)} تراکنش بزرگ یافت شد")
            return large_txs[:5]  # حداکثر 5 تراکنش
            
        except Exception as e:
            logger.error(f"❌ خطا در دریافت تراکنش‌ها: {e}")
            return []
    
    def send_alert(self, transactions):
        """ارسال هشدار به تلگرام"""
        if not transactions:
            return
            
        message = "🐋 **هشدار تراکنش بزرگ بیت‌کوین** 🚨\n\n"
        for i, tx in enumerate(transactions, 1):
            message += f"**تراکنش #{i}**\n"
            message += f"💰 کارمزد: {tx['fee']:,} ساتوشی\n"
            message += f"📦 حجم: {tx['size']} بایت\n"
            message += f"🆔 شناسه: `{tx['id'][:20]}...`\n"
            message += "─────────────────\n"
        
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("📤 پیام با موفقیت ارسال شد")
        except Exception as e:
            logger.error(f"❌ خطا در ارسال پیام: {e}")
    
    def check_and_alert(self):
        """بررسی و ارسال هشدار"""
        transactions = self.get_whale_transactions()
        if transactions:
            self.send_alert(transactions)
        else:
            logger.info("✅ هیچ تراکنش بزرگی یافت نشد")
    
    def start(self):
        """شروع ربات"""
        logger.info("🚀 ربات نهنگ‌یاب بیت‌کوین شروع به کار کرد")
        
        # اولین بررسی
        self.check_and_alert()
        
        # زمان‌بندی هر 20 دقیقه
        scheduler = BlockingScheduler()
        scheduler.add_job(self.check_and_alert, 'interval', minutes=20)
        
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("⏹️ ربات متوقف شد")

if __name__ == "__main__":
    tracker = WhaleTracker()
    tracker.start()
```
