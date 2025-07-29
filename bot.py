import feedparser
import time
import socket
import openai
import os

socket.setdefaulttimeout(5)

rss_feeds = {
    "Reuters Markets": "https://feeds.reuters.com/reuters/marketsNews",
    "Seeking Alpha": "https://seekingalpha.com/market-news.xml",
    "Investing Earnings": "https://www.investing.com/rss/news_25.rss"
}

seen_entries = set()

openai.api_key = os.environ.get("OPENAI_API_KEY")  # Pobierze Twój klucz API z ustawień Rendera

def classify_sentiment(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Zanalizuj wpływ tej wiadomości na inwestorów giełdowych. Klasyfikuj ją jako: pozytywna, negatywna lub neutralna.\n\nNews:\n{text}"
            }],
            temperature=0.3,
        )
        return response['choices'][0]['message']['content'].strip().lower()
    except Exception as e:
        print(f"Błąd AI: {e}")
        return "nieokreślony"

print("🟢 RSS AI BOT uruchomiony (Render.com)")

loop_counter = 1

while True:
    print(f"\n🔁 Iteracja {loop_counter} – sprawdzam źródła...")

    for source, url in rss_feeds.items():
        print(f"📡 Źródło: {source}")
        try:
            feed = feedparser.parse(url)
        except Exception as e:
            print(f"❗ Błąd przy {source}: {e}")
            continue

        for entry in feed.entries:
            if entry.link in seen_entries:
                continue
            seen_entries.add(entry.link)

            title = entry.title
            summary = entry.get("summary", "")
            full_text = f"{title}\n\n{summary}"

            sentiment = classify_sentiment(full_text)
            label = sentiment.upper()
            print(f"[{source}] {label} >> {title}")

    print("⏳ Czekam 60 sekund...\n")
    time.sleep(60)
    loop_counter += 1
