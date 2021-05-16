"""
File: craigslist_scrape.py
--------------------------

Scrapes the craigslist postings and sends an email if there's something we
haven't seen yet.
"""
from requests_html import HTMLSession, Element
from utils import Posting
from warn import WarningDiscriminator, WarningPipeline
from send_email import postings_to_digest, send_email
import sys

SEARCH_URL = (
    'https://chicago.craigslist.org/search/sub'
    '?max_price=2500&min_bedrooms=2&availabilityMode=0&sale_date=all+dates'
)

CACHE_FILE = 'idx_cache'

if __name__ == '__main__':
    session = HTMLSession()
    r = session.get(SEARCH_URL)

    # parse the posts
    results = r.html.find('.result-info')
    results = {Posting.parse_from_elt(e) for e in results}
    results = [p.fill_from_url(session) for p in results]
    idx_seen = set(open(CACHE_FILE).read().split())
    results = [p for p in results if p.post_id not in idx_seen]
    results = sorted(results, key=lambda p: p.posted_at, reverse=True)

    if not results:
        print("No new posts!")
        sys.exit()

    # add warnings
    wp = WarningPipeline(
        WarningDiscriminator.no_image(),
        WarningDiscriminator.unfurnished(),
        WarningDiscriminator.shared_space(),
        WarningDiscriminator.price_too_low(1000)
    )
    results = [wp.run_on(p) for p in results]

    # send the email
    send_email(postings_to_digest(results))

    # cache the posts
    with open(CACHE_FILE, 'a') as f:
        f.write('\n'.join(p.post_id for p in results))