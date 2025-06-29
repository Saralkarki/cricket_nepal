from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

Base = declarative_base()

class CricketDelivery(Base):
    __tablename__ = 'cricket_deliveries'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Match identification
    match_id = Column(String(50), nullable=False)  # From JSON filename
    innings_number = Column(Integer, nullable=False)  # 0 or 1
    
    # Ball identification
    overs = Column(Integer, nullable=False)
    balls = Column(Integer, nullable=False)
    
    # Players
    batter = Column(String(100), nullable=False)
    non_striker = Column(String(100), nullable=False)
    bowler = Column(String(100), nullable=False)
    
    # Runs
    runs_batter = Column(Integer, default=0)
    runs_extras = Column(Integer, default=0)
    runs_total = Column(Integer, default=0)
    
    # Extras
    extras_wides = Column(Integer, default=None)
    extras_legbyes = Column(Integer, default=None)
    extras_noballs = Column(Integer, default=None)
    extras_byes = Column(Integer, default=None)
    
    # Future columns
    description = Column(Text, default="")
    ball_areas = Column(Text, default="")
    
    # Wicket information
    is_wicket = Column(Integer, default=0)  # 0 or 1
    wicket_player_out = Column(String(100), default=None)
    wicket_kind = Column(String(50), default=None)
    wicket_fielder = Column(String(100), default=None)
    
    # DRS and umpire calls (future use)
    is_drs = Column(String(10), default="")
    is_umpires_call = Column(String(10), default="")
    
    def __repr__(self):
        return f"<CricketDelivery(match_id='{self.match_id}', overs={self.overs}, balls={self.balls}, batter='{self.batter}')>"

class CricketMatch(Base):
    __tablename__ = 'cricket_matches'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Match identification
    match_id = Column(String(50), unique=True, nullable=False)
    
    # Match details (from info section)
    match_type = Column(String(20))
    match_type_number = Column(Integer)
    gender = Column(String(10))
    venue = Column(String(200))
    city = Column(String(100))
    dates = Column(String(50))  # Can be parsed to datetime later
    
    # Teams
    team1 = Column(String(100))
    team2 = Column(String(100))
    toss_winner = Column(String(100))
    toss_decision = Column(String(20))
    
    # Result
    winner = Column(String(100))
    result_type = Column(String(50))  # runs/wickets
    result_margin = Column(String(100))
    
    # Player of the match
    player_of_match = Column(String(100))
    
    def __repr__(self):
        return f"<CricketMatch(match_id='{self.match_id}', teams='{self.team1} vs {self.team2}')>"

class DatabaseManager:
    def __init__(self, database_url="postgresql://username:password@localhost:5432/cricket_nepal"):
        """
        Initialize database connection
        
        Args:
            database_url: PostgreSQL connection string
                         Format: postgresql://username:password@localhost:5432/database_name
        """
        self.database_url = database_url
        self.engine = None
        self.Session = None
    
    def connect(self):
        """Create database connection and tables"""
        try:
            self.engine = create_engine(self.database_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            print("✅ Database connected successfully!")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def get_session(self):
        """Get a database session"""
        if self.Session:
            return self.Session()
        else:
            raise Exception("Database not connected. Call connect() first.")
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            print("Database connection closed.")

# Example usage and configuration
def get_database_config():
    """
    Get database configuration from environment variables or return default
    """
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'cricket_nepal'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    return f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

if __name__ == "__main__":
    # Test database connection
    db_url = get_database_config()
    db = DatabaseManager(db_url)
    
    if db.connect():
        print("Database tables created successfully!")
        db.close()
    else:
        print("Failed to connect to database.")
        print("\nTo set up PostgreSQL:")
        print("1. Install PostgreSQL")
        print("2. Create database: CREATE DATABASE cricket_nepal;")
        print("3. Set environment variables or update the database_url in this file")
