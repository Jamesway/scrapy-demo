# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import uuid, json
from sqlalchemy.orm import sessionmaker
from .models import PhysicianDB, db_connect, create_table

class ScrapyDcaPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)


    def process_item(self, item, spider):

        """
        This method is called for every item pipeline component.
        """

        session = self.Session()

        practice_id = uuid.uuid4()

        db1 = PhysicianDB()
        db1.id = practice_id
        db1.license = item['license']
        db1.license_type = item['license_type']
        db1.physician_name = item['name'].title()
        db1.address = json.dumps(item['address'])
        db1.services = json.dumps(item['services'])
        db1.scraped_at = item['scraped_at']

        try:
            # add a physician if they're new
            if not session.query(PhysicianDB).filter_by(license=db1.license).first():
                session.add(db1)
                session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item