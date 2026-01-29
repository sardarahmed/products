from src.database import Database, Internship, UserRequest
from src.filters import extract_country, classify_field

def verify_db():
    db = Database()
    session = db.get_session()
    
    # 1. Check Count
    count = session.query(Internship).count()
    print(f"Total Internships in DB: {count}")
    
    # 2. Check Sample
    internship = session.query(Internship).first()
    if internship:
        print(f"Sample: {internship.title} | {internship.country} | {internship.field}")
    
    # 3. Test Filters
    print("\nTesting Filters Logic:")
    print(f"Remote Application: {extract_country('Remote')}")
    print(f"New York, USA: {extract_country('New York, USA')}")
    print(f"Python Developer: {classify_field('Senior Python Developer')}")
    
    # 4. Test Rate Limit
    print("\nTesting Rate Limit:")
    user_id = 99999
    # Reset for test
    session.query(UserRequest).filter_by(user_id=user_id).delete()
    session.commit()
    
    for i in range(105):
        allowed, count = db.check_rate_limit(user_id)
        if not allowed:
            print(f"Rate Check {i+1}: Blocked (Count: {count})")
            break
            
    session.close()

if __name__ == "__main__":
    verify_db()
