#!/usr/bin/env python3
"""
Setup script for Nepal Cricket Database
"""
import os
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install required Python packages using uv"""
    print("📦 Installing Python dependencies with uv...")
    try:
        subprocess.run(["uv", "sync"], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Make sure uv is installed: https://docs.astral.sh/uv/")
        return False
    except FileNotFoundError:
        print("❌ uv not found! Please install uv first:")
        print("curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def create_env_file():
    """Create environment file for database configuration"""
    env_file = Path(".env")
    
    if env_file.exists():
        print("📄 .env file already exists")
        return True
    
    print("🔧 Creating database configuration file...")
    
    # Get database configuration from user
    print("\n🗄️  Database Configuration:")
    print("Press Enter to use default values in brackets")
    
    db_host = input("Database Host [localhost]: ").strip() or "localhost"
    db_port = input("Database Port [5432]: ").strip() or "5432"
    db_name = input("Database Name [cricket_nepal]: ").strip() or "cricket_nepal"
    db_user = input("Database User [postgres]: ").strip() or "postgres"
    db_password = input("Database Password: ").strip()
    
    # Write to .env file
    env_content = f"""# Database Configuration
DB_HOST={db_host}
DB_PORT={db_port}
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Database configuration saved to .env")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔌 Testing database connection...")
    
    try:
        # Add the code directory to the Python path
        import sys
        sys.path.append('code')
        
        from database_model import DatabaseManager, get_database_config
        
        db_url = get_database_config()
        db = DatabaseManager(db_url)
        
        if db.connect():
            print("✅ Database connection successful!")
            print("✅ Database tables created/verified!")
            db.close()
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def print_postgresql_setup():
    """Print PostgreSQL setup instructions"""
    print("\n🐘 PostgreSQL Setup Instructions:")
    print("=" * 50)
    print("1. Install PostgreSQL:")
    print("   macOS: brew install postgresql")
    print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
    print("   Windows: Download from https://www.postgresql.org/download/")
    print()
    print("2. Start PostgreSQL service:")
    print("   macOS: brew services start postgresql")
    print("   Ubuntu: sudo systemctl start postgresql")
    print()
    print("3. Create database:")
    print("   sudo -u postgres createdb cricket_nepal")
    print("   # OR connect to PostgreSQL and run:")
    print("   # CREATE DATABASE cricket_nepal;")
    print()
    print("4. Create user (optional):")
    print("   sudo -u postgres createuser --interactive")
    print()

def main():
    """Main setup function"""
    print("🏏 Nepal Cricket Database Setup")
    print("=" * 40)
    
    # Install dependencies
    if not install_dependencies():
        print("\n⚠️  Dependency installation failed. Please install manually:")
        print("uv sync")
        return
    
    # Load environment variables from .env if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("💡 Tip: Install python-dotenv for automatic .env loading")
        print("uv add python-dotenv")
    
    # Create environment configuration
    create_env_file()
    
    # Test database connection
    if not test_database_connection():
        print_postgresql_setup()
        print("\n⚠️  Please set up PostgreSQL and run this script again.")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 Next steps:")
    print("1. Run: python process_nepal_odi.py")
    print("2. This will process all Nepal ODI data into your database")
    print("\n📊 After processing, you can:")
    print("- Query the database directly")
    print("- Use pandas to read from database")
    print("- Build analytics dashboards")

if __name__ == "__main__":
    main()
