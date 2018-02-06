import uuid

from bs4 import BeautifulSoup
import requests
import re
from src.common.database import Database
import src.models.items.constants as ItemConstants
from src.models.stores.store import Store

class Item(object):
    def __init__(self, name, url, price=None, _id=None):
        self.name = name
        self.url = url
        store = Store.find_by_url(url)
        self.tag_name = store.tag_name
        self.query = store.query
        self.price = None if price is None else price
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Item {} with URL {}>".format(self.name, self.url)

    def load_price(self):
        # <div id="quote-header-info" class="quote-header-section Cf
        # Pos(r) Mb(5px) Maw($maxModuleWidth) Miw($minGridWidth) smartphone_Miw(ini)
        # Miw(ini)!--tab768 Miw(ini)!--tab1024 Mstart(a) Mend(a) Px(20px)" data-test="quote-header">

        # <span class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"><!-- react-text: 337 -->2,849.25<!-- /react-text --></span>
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content, "html.parser")
        element = soup.find(self.tag_name, attrs=self.query)
        # element = soup.find(string='Fight History').find_parent(class_='module fight_history').find('table')


        string_price = element.text.strip()

        pattern = re.compile("(\d+.\d+)") # include the bracket to get the real number
        match = pattern.search(string_price)
        self.price = float(match.group().replace(",",""))

        return self.price

    def save_to_mongo(self):
        Database.update(ItemConstants.COLLECTION, {'_id': self._id}, self.json())

    def json(self):
        return {
            "name": self.name,
            "url": self.url,
            "_id": self._id,
            "price": self.price
        }

    @classmethod
    def get_by_name(cls, item_name):
        return cls(**Database.find_one(ItemConstants.COLLECTION, {"name": item_name}))

    @classmethod
    def get_by_id(cls, _id):
        return cls(**Database.find_one(ItemConstants.COLLECTION, {"_id": _id}))