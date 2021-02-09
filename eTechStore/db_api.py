import pprint
import os
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import time

from eTechStore import general

# DB_URL = f"sqlite:///{os.path.dirname(__file__)}/../db/UrlsManager.sqlite"
DB_URL = general.DB_URL


class BaseExt(object):
    """Does much nicer repr/print of class instances
    from sqlalchemy list suggested by Michael Bayer
    """

    def __repr__(self):
        return "%s(%s)" % (
            (self.__class__.__name__),
            ', '.join(["%s=%r" % (key, getattr(self, key))
                       for key in sorted(self.__dict__.keys())
                       if not key.startswith('_')]))

Base = declarative_base(cls=BaseExt)


class AllUrls(Base):

    __tablename__ = 'AllUrls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class NewUrls(Base):

    __tablename__ = 'NewUrls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class SqlAlchemy:

    def __init__(self, db_url=""):
        self.engine = db.create_engine(db_url if db_url else os.environ.get("DB_URL", DB_URL))
        print (self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.create_tables()

    def create_connection(self):
        pass

    def close_connection(self):
        pass

    def drop_all_tables(self):
        Base.metadata.drop_all(self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def insert_all_urls(self, dict_data={}):

        if dict_data and not self.session.query(AllUrls.id).filter_by(**dict_data).first() is not None:
            url = AllUrls(**dict_data)
            self.session.add(url)
            self.session.flush()
            # print("Inserted into AllUrls: {0}".format(url))
            self.session.commit()

    def insert_new_urls(self, dict_data={}):

        if dict_data and not self.session.query(NewUrls.id).filter_by(**dict_data).first() is not None:
            url = NewUrls(**dict_data)
            self.session.add(url)
            self.session.flush()
            # print("Inserted into NewUrls: {0}".format(url))
            self.session.commit()


    def get_new_urls(self):
        return self.session.query(NewUrls).all()

    def get_all_urls(self):
        return self.session.query(AllUrls).all()

    def transfer_url(self, url):
        new_url = self.session.query(NewUrls).filter_by(url=url).first()
        if new_url:
            self.insert_all_urls({"url": new_url.url})
            self.session.delete(new_url)
            self.session.commit()
            # print("Remove from NewUrls: {0}".format(new_url))


def main():
    db_api = SqlAlchemy(DB_URL)
    # db_api.drop_all_tables()
    # db_api.create_tables()
    #
    # pprint.pprint(db_api.get_all_urls())

    lst_items = [
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/LED-FUEGO-32-EL-600-T'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/FUEGO-32-EL-610-AND-T'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/FUEGO-40-EL-600-T'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/GRUNDIG-32-VLE-4820'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/HITACHI-32-HE-1000'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/GRUNDIG-32-GEH-6600-B'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/FUEGO-43-EL-610-AND-T'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/LG-32-LM-630B-PLA'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/GRUNDIG-40-GEF-6600-B'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/LG-32-LM-6300-PLA'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/GRUNDIG-43-GEF-6600-B'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/FUEGO-50-ELU-610-AND-T'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/HITACHI-43-HK-6000'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/GRUNDIG-43-VLE-6735-BP'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/FUEGO-50-VEU-720-T2'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/SCHNEIDER-50-SL-55'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/GRUNDIG-43-GEU-7800-B'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/GRUNDIG-43-GDU-7500-B'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/HITACHI-50-HAK-6150-'},
        {'url': 'https://www.neptun.mk/pocetna/categories/TV_AUDIO_VIDEO/televizori.nspx/LG-43-LM-6300-PLA'}
    ]

    # for dict_data_ in lst_items:
    #     # db_api.insert_new_urls(dict_data_)
    #
    #     db_api.transfer_url(dict_data_["url"])

    result = db_api.get_new_urls()
    print (len(result))

# if __name__ == '__main__':
#     main()