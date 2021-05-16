"""
File: utils.py
--------------

Utilities for scraping Craigslist data.
"""
from requests_html import HTMLSession, Element
from datetime import datetime
import re
from typing import Union


class Posting:
    def __init__(
        self,
        posted_at: datetime,
        price: int,
        num_rooms: int,
        size: int,
        neighborhood: str,
        title: str,
        post_id: int,
        post_url: str,
    ):
        """
        Arguments
        ---------
        posted_at    -- The time the Craigslist post was made
        price        -- The monthly price for the posting
        num_rooms    -- The number of bedrooms in the posting
        size         -- The size of the posting in square feet
        neighborhood -- The neighborhood for the posting
        title        -- The posting title
        post_id      -- Craigslist's unique integer id for the posting
        post_url     -- A direct link to the post
        """
        self.posted_at = posted_at
        self.price = price
        self.num_rooms = num_rooms
        self.size = size
        self.neighborhood = neighborhood
        self.title = title
        self.post_id = post_id
        self.post_url = post_url


    def __hash__(self):
        return hash(self.post_id)


    def __eq__(self, other):
        return self.post_id == other.post_id


    def __repr__(self):
        return f'<Posting title={repr(self.title)} price=${self.price} size={self.size}>'


    def fill_from_url(self, session: Union[HTMLSession, None] = None):
        """
        Fills in more data about the posting from its url.
        """
        if session is None:
            session = HTMLSession()

        r = session.get(self.post_url)

        # description
        body = r.html.find('#postingbody', first=True).text
        m = re.match(r'(QR Code Link to This Post\s*)(.*)', body)
        if m:
            self.description = m.group(2)
        else:
            self.description = body

        # map and attrs
        map_and_attrs = r.html.find('.mapAndAttrs', first=True)
        attrs = map_and_attrs.find('span')
        self.attrs = [a.text for a in attrs if not a.attrs.get('class')]
        try:
            self.address = map_and_attrs.find('div.mapaddress', first=True).text
        except AttributeError:
            # the address isn't set
            self.address = None

        # image
        try:
            self.img_url = r.html.find('img', first=True).attrs['src']
        except AttributeError:
            self.img_url = None

        return self


    @classmethod
    def parse_from_elt(cls, e: Element):
        """
        Parses a Posting object from the element provided.

        Arguments
        ---------
        e -- An element with the class 'result-info' which represents a posting
            on Craigslist.


        Returns
        -------
        Posting -- The object representing the posting for the given element.
        """
        assert 'result-info' in e.attrs['class']

        kwargs = {}

        # posted_at
        ds = e.find('.result-date', first=True).attrs['datetime']
        kwargs['posted_at'] = datetime.strptime(ds, '%Y-%m-%d %H:%M')

        # price
        kwargs['price'] = int(
            e.find('.result-price', first=True).text.strip('$').replace(',', '')
        )

        # num_rooms, size
        br, size, *a = e.find('.housing', first=True).text.split('-')
        br = int(br.strip(' br'))
        try:
            size = int(re.match(r'^\s*(\d+)', size).group(1))
        except AttributeError:
            # no size found
            size = -1

        kwargs['num_rooms'] = br
        kwargs['size'] = size

        # neighborhood
        try:
            kwargs['neighborhood'] = e.find('.result-hood', first=True).text \
                                      .strip(' ()')
        except AttributeError:
            kwargs['neighborhood'] = ''

        # title
        kwargs['title'] = e.find('.result-title', first=True).text

        # link parsing
        link_attrs = e.find('a.result-title', first=True).attrs
        kwargs['post_id'] = link_attrs['data-id']
        kwargs['post_url'] = link_attrs['href']

        return cls(**kwargs)