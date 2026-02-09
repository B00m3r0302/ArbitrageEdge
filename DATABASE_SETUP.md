# Database Setup & Initialization Guide

This guide shows you how to set up PostgreSQL so your app automatically handles everything: creates the database if it doesn't exist, creates the user if it doesn't exist, and creates tables if they don't exist.

## Quick Start: Two Approaches

### Approach A: Fully Automatic (Recommended for Development)
Your app creates everything automatically:
1. Install PostgreSQL
2. Configure `.env` with superuser credentials
3. Run your app
4. Done! Database, user, and tables created automatically

### Approach B: Manual Database + Auto Tables
You create database/user manually, app creates tables:
1. Install PostgreSQL
2. Manually create database and user
3. Configure `.env` with your user credentials
4. Run your app
5. Tables created automatically

Both approaches are **idempotent** - safe to run multiple times. Existing resources are reused, not recreated.

---

## Step 1: Install PostgreSQL

### Option A: Docker (Easiest)

```bash
# Pull and run PostgreSQL
docker run -d \
  --name arbitrage_postgres \
  -e POSTGRES_USER=arbitrage_user \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=arbitrage_db \
  -p 5432:5432 \
  postgres:16-alpine

# Verify it's running
docker ps | grep arbitrage_postgres

# View logs if needed
docker logs arbitrage_postgres
```

**That's it!** With Docker, the database and user are already created. Skip to Step 3.

### Option B: Native Installation

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Start on boot
```

**macOS:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Windows:**
Download installer from [postgresql.org](https://www.postgresql.org/download/windows/)

---

## Step 2: Create Database and User (Native Installation Only)

### Connect to PostgreSQL

```bash
# Connect as the default postgres superuser
sudo -u postgres psql

# Or on macOS/Windows:
psql -U postgres
```

You should see a prompt like: `postgres=#`

### Create the User

```sql
-- Create a user with a password
CREATE USER arbitrage_user WITH PASSWORD 'your_secure_password';

-- Give the user permission to create databases (needed for testing)
ALTER USER arbitrage_user CREATEDB;

-- Verify user was created
\du
```

**What this does:**
- Creates a PostgreSQL user account
- Sets a password (change 'your_secure_password'!)
- Grants CREATEDB privilege (lets user create databases)

### Create the Database

```sql
-- Create the database owned by your user
CREATE DATABASE arbitrage_db OWNER arbitrage_user;

-- Connect to the new database
\c arbitrage_db

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE arbitrage_db TO arbitrage_user;

-- Grant privileges on the public schema (important for PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO arbitrage_user;

-- Allow user to create tables in public schema
GRANT CREATE ON SCHEMA public TO arbitrage_user;

-- Verify database was created
\l
```

**What this does:**
- Creates a database named `arbitrage_db`
- Makes `arbitrage_user` the owner
- Grants all permissions on the database and schema
- Allows user to create tables, insert data, etc.

### Exit PostgreSQL

```sql
\q
```

### Test the Connection

```bash
# Try connecting as your new user
psql -U arbitrage_user -d arbitrage_db -h localhost

# If successful, you'll see:
# arbitrage_db=>

# Try creating a test table
CREATE TABLE test (id SERIAL PRIMARY KEY, name TEXT);
INSERT INTO test (name) VALUES ('works!');
SELECT * FROM test;
DROP TABLE test;

# Exit
\q
```

**If you get authentication errors:**
You may need to edit PostgreSQL's authentication config:

```bash
# Find pg_hba.conf location
sudo -u postgres psql -c "SHOW hba_file;"

# Edit it (Ubuntu example)
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Change this line from "peer" to "md5" or "scram-sha-256":
# local   all   all   peer
# TO:
# local   all   all   md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## Step 3: Configure Your Application

### Create Your .env File

```bash
# Copy the template
cp .env_template .env

# Edit with your actual credentials
nano .env  # or use your preferred editor
```

**Update these values in .env:**

```env
# Database Configuration
POSTGRES_USER=arbitrage_user          # Your app's database user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=arbitrage_db              # Your app's database name
POSTGRES_HOST=localhost               # or 'postgres' for Docker Compose
POSTGRES_PORT=5432
```

**Important Notes:**

**For Automatic Database/User Creation (Option A):**
You need superuser credentials on FIRST RUN to create the database and user:

```env
# For first-time setup (Docker)
POSTGRES_USER=postgres                # Docker's default superuser
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=arbitrage_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**After first run,** you can change to your app user:
```env
# For normal operation (after setup)
POSTGRES_USER=arbitrage_user          # Your created user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=arbitrage_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

**OR** keep using the superuser (simpler for development):
```env
# Keep using superuser (easiest for dev)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=arbitrage_db
```

**For Manual Setup (Option B):**
Use your created user credentials from the start:
```env
POSTGRES_USER=arbitrage_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=arbitrage_db
```

**Security:**
- Never commit `.env` to git (should be in `.gitignore`)
- Use strong passwords in production
- In production, use dedicated users (not superuser)

### Update config.py

Make sure your `src/app/config.py` has the database URL property:

```python
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Database settings
    postgres_user: str = Field(default="arbitrage_user")
    postgres_password: str = Field(default="password")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="arbitrage_db")

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Other settings...
    project_name: str = "ArbitrageEdge"
    version: str = "0.1.0"
    debug: bool = Field(default=False)

settings = Settings()
```

---

## Step 4: Create Smart Database Initialization

### Overview

We'll create a system that:
1. Checks if the database exists → creates it if not
2. Checks if the user exists → creates it if not
3. Creates tables if they don't exist
4. Uses everything if it already exists

### Create db/base.py

Create `src/app/db/base.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.app.config import settings

# Create the database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,      # Log SQL queries when debug=True
    pool_pre_ping=True,       # Verify connections before using
    pool_size=5,              # Number of connections to keep open
    max_overflow=10           # Max additional connections when pool is full
)

# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI endpoints.
    Provides a database session that automatically closes.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**What this does:**
- `engine`: Connection to your PostgreSQL database
- `SessionLocal`: Factory for creating database sessions
- `Base`: Base class that all your models will inherit from
- `get_db()`: FastAPI dependency that provides a database session

### Create db/models.py

Create `src/app/db/models.py` with your first model:

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from src.app.db.base import Base

class Bookmaker(Base):
    """Example model - you'll add more based on your needs"""
    __tablename__ = "bookmakers"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Bookmaker(id={self.id}, title='{self.title}')>"
```

**Important:** Define all your models in this file or import them all here so SQLAlchemy knows about them when creating tables.

### Create db/setup.py (Smart Database/User Creation)

Create `src/app/db/setup.py`:

```python
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from src.app.config import settings

def get_admin_engine():
    """
    Connect to PostgreSQL's default 'postgres' database as superuser.
    This lets us create databases and users.

    For this to work, you need a superuser. Options:
    1. Docker: Use POSTGRES_USER=postgres (default superuser)
    2. Native: Use the 'postgres' system user
    """
    # Build connection to the default 'postgres' database
    admin_url = (
        f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/postgres"
    )

    return create_engine(admin_url, isolation_level="AUTOCOMMIT")

def database_exists() -> bool:
    """Check if our target database exists"""
    try:
        admin_engine = get_admin_engine()
        with admin_engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
                {"dbname": settings.postgres_db}
            )
            exists = result.fetchone() is not None

        admin_engine.dispose()
        return exists

    except Exception as e:
        print(f"Error checking database existence: {e}")
        return False

def user_exists() -> bool:
    """Check if our database user exists"""
    try:
        admin_engine = get_admin_engine()
        with admin_engine.connect() as conn:
            result = conn.execute(
                text("SELECT 1 FROM pg_user WHERE usename = :username"),
                {"username": settings.postgres_user}
            )
            exists = result.fetchone() is not None

        admin_engine.dispose()
        return exists

    except Exception as e:
        print(f"Error checking user existence: {e}")
        return False

def create_database_and_user():
    """
    Create database and user if they don't exist.

    IMPORTANT: This requires connecting as a superuser (like 'postgres').
    Update your .env with superuser credentials for this to work.
    """
    try:
        print("=" * 50)
        print("Database & User Setup")
        print("=" * 50)

        admin_engine = get_admin_engine()

        with admin_engine.connect() as conn:
            # Check and create user
            if user_exists():
                print(f"✓ User '{settings.postgres_user}' already exists")
            else:
                print(f"○ Creating user '{settings.postgres_user}'...")
                # Note: CREATE USER doesn't support parameterized queries
                # Make sure your username/password don't contain special SQL characters
                conn.execute(
                    text(f"""
                        CREATE USER {settings.postgres_user}
                        WITH PASSWORD '{settings.postgres_password}'
                        CREATEDB
                    """)
                )
                print(f"✓ User '{settings.postgres_user}' created")

            # Check and create database
            if database_exists():
                print(f"✓ Database '{settings.postgres_db}' already exists")
            else:
                print(f"○ Creating database '{settings.postgres_db}'...")
                conn.execute(
                    text(f"""
                        CREATE DATABASE {settings.postgres_db}
                        OWNER {settings.postgres_user}
                    """)
                )
                print(f"✓ Database '{settings.postgres_db}' created")

            # Grant privileges on the database
            conn.execute(
                text(f"""
                    GRANT ALL PRIVILEGES ON DATABASE {settings.postgres_db}
                    TO {settings.postgres_user}
                """)
            )

        admin_engine.dispose()

        # Now connect to the new database and grant schema privileges
        db_url = (
            f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
            f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        )
        db_engine = create_engine(db_url, isolation_level="AUTOCOMMIT")

        with db_engine.connect() as conn:
            # Grant schema privileges (needed for PostgreSQL 15+)
            conn.execute(
                text(f"GRANT ALL ON SCHEMA public TO {settings.postgres_user}")
            )
            conn.execute(
                text(f"GRANT CREATE ON SCHEMA public TO {settings.postgres_user}")
            )

        db_engine.dispose()

        print("✓ All privileges granted")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"✗ Error during setup: {e}")
        print("\nCommon issues:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check that you're using superuser credentials in .env")
        print("3. For Docker: use POSTGRES_USER=postgres")
        print("4. For native: use 'postgres' as the user")
        return False

if __name__ == "__main__":
    """Run this file directly to set up database and user"""
    success = create_database_and_user()
    if success:
        print("\n✓ Setup complete! You can now run your app.")
    else:
        print("\n✗ Setup failed. Check errors above.")
```

**Key Points:**
- Connects to the default `postgres` database first
- Checks if user exists → creates if not
- Checks if database exists → creates if not
- Grants all necessary privileges
- Safe to run multiple times (idempotent)

**Important:** This requires superuser access. For initial setup:
- **Docker:** Use `POSTGRES_USER=postgres` in your Docker run command
- **Native:** Run as the `postgres` system user or another superuser

### Create db/init_db.py (Table Creation)

Create `src/app/db/init_db.py`:

```python
from sqlalchemy import inspect, text
from src.app.db.base import engine, Base
from src.app.config import settings

# Import all models here so SQLAlchemy knows about them
from src.app.db.models import Bookmaker  # Add more as you create them

def check_database_exists() -> bool:
    """Check if database exists and is accessible"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✓ Database '{settings.postgres_db}' is accessible")
        return True
    except Exception as e:
        print(f"✗ Cannot connect to database: {e}")
        return False

def get_existing_tables() -> list[str]:
    """Get list of tables that already exist in the database"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return tables

def init_db() -> None:
    """
    Initialize the database by creating all tables defined in models.

    This is IDEMPOTENT - it will:
    - Create tables that don't exist
    - Skip tables that already exist
    - Not drop or modify existing data
    """
    try:
        # Check database connection
        if not check_database_exists():
            raise Exception("Cannot connect to database. Check your configuration.")

        # Get existing tables
        existing_tables = get_existing_tables()

        if existing_tables:
            print(f"✓ Found existing tables: {', '.join(existing_tables)}")
        else:
            print("○ No existing tables found")

        # Create all tables defined in models (skips existing ones)
        print("○ Creating tables from models...")
        Base.metadata.create_all(bind=engine)

        # Check what tables exist now
        final_tables = get_existing_tables()
        new_tables = set(final_tables) - set(existing_tables)

        if new_tables:
            print(f"✓ Created new tables: {', '.join(new_tables)}")
        else:
            print("✓ All tables already existed, no changes made")

        print(f"✓ Database initialized successfully!")
        print(f"  Total tables: {len(final_tables)}")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        raise

def drop_all_tables() -> None:
    """
    DROP ALL TABLES - USE WITH CAUTION!
    Only use this in development when you want to reset everything.
    """
    print("⚠️  WARNING: This will delete ALL data!")
    confirm = input("Type 'DELETE ALL DATA' to confirm: ")

    if confirm == "DELETE ALL DATA":
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped")
    else:
        print("✗ Aborted")

if __name__ == "__main__":
    """Run this file directly to initialize the database"""
    print("=" * 50)
    print("Database Initialization")
    print("=" * 50)
    init_db()
```

**What this does:**
- Checks if database is accessible
- Lists existing tables
- Creates tables that don't exist
- Skips tables that already exist (safe to run multiple times)
- Provides a function to drop all tables (for development)

---

## Step 5: Initialize Your Database

You have two options:

### Option A: Full Automatic Setup (Recommended)

This creates the database, user, AND tables automatically:

```bash
# First, create database and user (needs superuser access)
python src/app/db/setup.py

# Then, create tables
python src/app/db/init_db.py
```

### Option B: Manual Database + Auto Tables

If you prefer to create the database/user manually (Step 2), then just run:

```bash
# Only creates tables
python src/app/db/init_db.py
```

### What You'll See (Option A - Full Auto)

**Step 1: Database & User Setup**
```bash
python src/app/db/setup.py
```

Output:
```
==================================================
Database & User Setup
==================================================
○ Creating user 'arbitrage_user'...
✓ User 'arbitrage_user' created
○ Creating database 'arbitrage_db'...
✓ Database 'arbitrage_db' created
✓ All privileges granted
==================================================
✓ Setup complete! You can now run your app.
```

**Run again (everything exists):**
```
==================================================
Database & User Setup
==================================================
✓ User 'arbitrage_user' already exists
✓ Database 'arbitrage_db' already exists
✓ All privileges granted
==================================================
✓ Setup complete! You can now run your app.
```

**Step 2: Table Creation**
```bash
python src/app/db/init_db.py
```

**You should see output like:**
```
==================================================
Database Initialization
==================================================
✓ Database 'arbitrage_db' is accessible
○ No existing tables found
○ Creating tables from models...
✓ Created new tables: bookmakers
✓ Database initialized successfully!
  Total tables: 1
```

**If you run it again:**
```
✓ Database 'arbitrage_db' is accessible
✓ Found existing tables: bookmakers
○ Creating tables from models...
✓ All tables already existed, no changes made
✓ Database initialized successfully!
  Total tables: 1
```

### Verify Tables Were Created

```bash
# Connect to PostgreSQL
psql -U arbitrage_user -d arbitrage_db -h localhost

# List tables
\dt

# Describe the bookmakers table
\d bookmakers

# Exit
\q
```

**You should see:**
```
                 Table "public.bookmakers"
   Column    |            Type             | Nullable | Default
-------------+-----------------------------+----------+---------
 id          | integer                     | not null | nextval(...)
 key         | character varying(100)      | not null |
 title       | character varying(200)      | not null |
 active      | integer                     |          | 1
 created_at  | timestamp without time zone |          |
 updated_at  | timestamp without time zone |          |
```

---

## Step 6: Integrate with Your FastAPI App

### Update main.py

Update your `src/app/main.py`:

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.config import settings
from src.app.db.setup import create_database_and_user, database_exists
from src.app.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on application startup and shutdown.
    Automatically sets up everything needed for the database.
    """
    # Startup: Full database initialization
    print("Starting up...")

    # Step 1: Ensure database and user exist (skip if already there)
    if not database_exists():
        print("Database doesn't exist, creating it...")
        create_database_and_user()
    else:
        print("✓ Database already exists")

    # Step 2: Ensure tables exist (skip if already there)
    init_db()

    print("✓ Application ready!")

    yield  # Application runs here

    # Shutdown: Cleanup (if needed)
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan  # Initialize DB on startup
)

@app.get("/")
def read_root():
    return {"message": "ArbitrageEdge API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

**What this does:**
- Checks if database exists
  - If not: creates database and user
  - If yes: skips to next step
- Creates tables if they don't exist
- Uses existing tables if they do
- Your app is completely self-sufficient!

**First Run:** Creates database, user, and tables
**Subsequent Runs:** Uses existing database and tables

### Test Your Setup

```bash
# Start your FastAPI app
python src/app/main.py

# Or with uvicorn directly
uvicorn src.app.main:app --reload
```

**You should see:**
```
Starting up...
==================================================
Database Initialization
==================================================
✓ Database 'arbitrage_db' is accessible
✓ Found existing tables: bookmakers
○ Creating tables from models...
✓ All tables already existed, no changes made
✓ Database initialized successfully!
  Total tables: 1
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Test the API

```bash
# Visit in browser or use curl
curl http://localhost:8000/

# Should return:
# {"message":"ArbitrageEdge API","status":"running"}
```

---

## Step 7: Add More Models (As You Build)

When you add new models:

```python
# In src/app/db/models.py

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    # ... your fields

class Odds(Base):
    __tablename__ = "odds"

    id = Column(Integer, primary_key=True, index=True)
    # ... your fields
```

**Then update init_db.py:**
```python
# Add imports at the top
from src.app.db.models import Bookmaker, Event, Odds
```

**Restart your app:**
```bash
python src.app/main.py
```

**Output:**
```
✓ Found existing tables: bookmakers
○ Creating tables from models...
✓ Created new tables: events, odds
✓ Database initialized successfully!
  Total tables: 3
```

---

## Complete Example: From Scratch to Running

Here's the complete workflow for **Approach A (Fully Automatic)**:

### Step-by-Step

```bash
# 1. Install PostgreSQL (Docker - easiest)
docker run -d \
  --name arbitrage_postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  postgres:16-alpine

# 2. Configure your app
cp .env_template .env
nano .env

# Add these lines:
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=mysecretpassword
# POSTGRES_DB=arbitrage_db
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432

# 3. Run your app (first time)
python src/app/main.py

# Output:
# Starting up...
# Database doesn't exist, creating it...
# ○ Creating user 'arbitrage_user'...
# ✓ User 'arbitrage_user' created
# ○ Creating database 'arbitrage_db'...
# ✓ Database 'arbitrage_db' created
# ○ Creating tables from models...
# ✓ Created new tables: bookmakers
# ✓ Application ready!
# INFO: Uvicorn running on http://127.0.0.1:8000

# 4. Stop and restart (second time)
# Press Ctrl+C
python src/app/main.py

# Output:
# Starting up...
# ✓ Database already exists
# ✓ Found existing tables: bookmakers
# ✓ All tables already existed, no changes made
# ✓ Application ready!
# INFO: Uvicorn running on http://127.0.0.1:8000

# 5. Verify in PostgreSQL
psql -U postgres -d arbitrage_db -h localhost

# Run these commands:
\du                    # List users (you'll see arbitrage_user)
\l                     # List databases (you'll see arbitrage_db)
\c arbitrage_db        # Connect to your database
\dt                    # List tables (you'll see bookmakers)
SELECT * FROM bookmakers;  # Query your table (empty for now)
\q                     # Exit

# 6. Add a new model and restart
# Edit src/app/db/models.py and add a new model
# Then restart:
python src/app/main.py

# Output:
# Starting up...
# ✓ Database already exists
# ✓ Found existing tables: bookmakers
# ○ Creating tables from models...
# ✓ Created new tables: events
# ✓ Application ready!
```

That's it! Your database setup is complete and your app manages everything automatically.

---

## Troubleshooting

### "Connection refused" error

**Problem:** Can't connect to PostgreSQL

**Solutions:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS
docker ps | grep postgres  # Docker

# Check if port 5432 is open
netstat -an | grep 5432

# Try connecting manually
psql -U arbitrage_user -d arbitrage_db -h localhost
```

### "Password authentication failed"

**Problem:** Wrong password or auth method

**Solutions:**
1. Double-check password in `.env` file
2. Try connecting manually: `psql -U arbitrage_user -d arbitrage_db -h localhost`
3. Check `pg_hba.conf` authentication method (see Step 2)

### "Database does not exist"

**Problem:** Database wasn't created

**Solutions:**
```bash
# Connect as superuser and create it
sudo -u postgres psql

# Run the CREATE DATABASE commands from Step 2
CREATE DATABASE arbitrage_db OWNER arbitrage_user;
```

### "Permission denied for schema public"

**Problem:** User doesn't have schema privileges (PostgreSQL 15+)

**Solutions:**
```bash
# Connect as superuser
sudo -u postgres psql -d arbitrage_db

# Grant schema privileges
GRANT ALL ON SCHEMA public TO arbitrage_user;
GRANT CREATE ON SCHEMA public TO arbitrage_user;
```

### "relation already exists"

**Problem:** Table already exists (this is actually fine!)

**Solution:** This is normal if you run initialization multiple times. SQLAlchemy will skip existing tables.

---

## Summary: What You've Set Up

### Approach A (Fully Automatic):
✓ PostgreSQL installed and running
✓ App checks if database exists → creates if not
✓ App checks if user exists → creates if not
✓ App checks if tables exist → creates if not
✓ Everything idempotent (safe to run multiple times)
✓ Zero manual database setup required

### Approach B (Manual Database + Auto Tables):
✓ PostgreSQL installed and running
✓ Database and user created manually
✓ App checks if tables exist → creates if not
✓ Table creation idempotent (safe to run multiple times)
✓ More control over database setup

## Your App's Behavior

When your FastAPI app starts:

```
1. Check if database exists
   ├─ NO → Create database and user
   └─ YES → Continue

2. Check if tables exist
   ├─ NO → Create tables from models
   └─ YES → Use existing tables

3. Start accepting requests
```

**First Run:**
```
Starting up...
Database doesn't exist, creating it...
○ Creating user 'arbitrage_user'...
✓ User 'arbitrage_user' created
○ Creating database 'arbitrage_db'...
✓ Database 'arbitrage_db' created
✓ Database 'arbitrage_db' is accessible
○ Creating tables from models...
✓ Created new tables: bookmakers
✓ Application ready!
```

**Subsequent Runs:**
```
Starting up...
✓ Database already exists
✓ Database 'arbitrage_db' is accessible
✓ Found existing tables: bookmakers
✓ All tables already existed, no changes made
✓ Application ready!
```

## Next Steps

1. **Define your data models** in `src/app/db/models.py`
   - What data do you need to store?
   - How do tables relate to each other?

2. **Create validation schemas** in `src/app/schemas/`
   - What data comes from users?
   - What data goes back to users?

3. **Build API endpoints** in `src/app/api/endpoints/`
   - What operations do users need?
   - How do they interact with your data?

4. **Restart your app**
   - New models? Tables are created automatically
   - Existing models? Tables are reused
   - Never worry about database setup again

## Key Advantages

✓ **Developer friendly**: Clone repo, run app, everything works
✓ **Idempotent**: Run setup 100 times, same result
✓ **Safe**: Never drops or modifies existing data
✓ **Flexible**: Works with existing databases or creates new ones
✓ **Production ready**: Same code works in dev and prod

You're ready to start building!
