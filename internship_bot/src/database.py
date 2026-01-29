from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

Base = declarative_base()

class Internship(Base):
    __tablename__ = 'internships'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    link = Column(String, unique=True, nullable=False)
    date_posted = Column(DateTime)
    source = Column(String)
    country = Column(String)
    field = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class UserRequest(Base):
    __tablename__ = 'user_requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    date = Column(String, nullable=False) # YYYY-MM-DD
    count = Column(Integer, default=0)

class Database:
    def __init__(self, db_path='internships.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def add_internship(self, data):
        session = self.Session()
        try:
            # Check if exists
            exists = session.query(Internship).filter_by(link=data['link']).first()
            if not exists:
                internship = Internship(
                    title=data.get('title'),
                    company=data.get('company'),
                    location=data.get('location'),
                    link=data['link'],
                    date_posted=data.get('date_obj'), # Expecting datetime object
                    source=data.get('source'),
                    country=data.get('country'),
                    field=data.get('field')
                )
                session.add(internship)
                session.commit()
                return True
        except Exception as e:
            print(f"Error adding internship: {e}")
            session.rollback()
        finally:
            session.close()
        return False

    def search_internships(self, country=None, field=None, limit=5):
        session = self.Session()
        try:
            query = session.query(Internship)
            if country and country != 'All':
                query = query.filter(Internship.country.ilike(f'%{country}%'))
            if field and field != 'All':
                 # Simple substring match for now, or exact match depending on classifier
                query = query.filter(Internship.field == field)
            
            # Order by newest first
            results = query.order_by(Internship.date_posted.desc()).limit(limit).all()
            return results
        finally:
            session.close()

    def check_rate_limit(self, user_id, limit=100):
        session = self.Session()
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            user_req = session.query(UserRequest).filter_by(user_id=user_id, date=today).first()
            
            if not user_req:
                user_req = UserRequest(user_id=user_id, date=today, count=0)
                session.add(user_req)
            
            if user_req.count < limit:
                user_req.count += 1
                session.commit()
                return True, user_req.count
            else:
                return False, user_req.count
        finally:
            session.close()
