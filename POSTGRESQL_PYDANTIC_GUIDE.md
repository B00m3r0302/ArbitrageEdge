# PostgreSQL + Pydantic: Understanding the Architecture

## Table of Contents
1. [The Big Picture: Why Three Layers?](#the-big-picture-why-three-layers)
2. [PostgreSQL Setup: Getting Your Database Running](#postgresql-setup-getting-your-database-running)
3. [Understanding the Separation: SQLAlchemy vs Pydantic vs Config](#understanding-the-separation)
4. [Database Layer: SQLAlchemy Models](#database-layer-sqlalchemy-models)
5. [Validation Layer: Pydantic Schemas](#validation-layer-pydantic-schemas)
6. [Configuration Layer: Settings](#configuration-layer-settings)
7. [How Data Flows Through Your Application](#how-data-flows-through-your-application)
8. [Common Patterns and Why They Matter](#common-patterns-and-why-they-matter)

---

## The Big Picture: Why Three Layers?

When building a FastAPI application with PostgreSQL, you'll work with three distinct types of "models":

```
User makes request → Pydantic validates → Business logic processes → SQLAlchemy saves → PostgreSQL stores
                                                                                              ↓
User receives response ← Pydantic formats ← SQLAlchemy retrieves ← PostgreSQL returns data ←
```

**The Three Layers:**

1. **Config Layer** (`config.py`) - "How do I connect to things?"
   - Database connection strings
   - API keys and secrets
   - Application settings
   - Think: *environment configuration*

2. **SQLAlchemy Layer** (`db/models.py`) - "What does the database look like?"
   - Table definitions
   - Column types and constraints
   - Relationships between tables
   - Think: *database schema*

3. **Pydantic Layer** (`schemas/`) - "What data is valid for my API?"
   - Request validation
   - Response formatting
   - Business rules
   - Think: *API contract*

**Why separate them?**
- **Single Responsibility**: Each layer has one job
- **Flexibility**: Change database structure without breaking API contracts
- **Security**: Validate data before it reaches the database
- **Type Safety**: Catch errors early in the request lifecycle

---

## PostgreSQL Setup: Getting Your Database Running

### Why PostgreSQL?

PostgreSQL offers:
- **ACID compliance** - Your arbitrage data stays consistent
- **Relationships** - Link events, odds, and bookmakers naturally
- **Performance** - Handle thousands of odds updates efficiently
- **JSON support** - Store flexible data when needed

### Setup Options

**Docker (Recommended for Development)**
Why: Isolated, reproducible, easy to reset

```bash
docker run -d \
  --name your_postgres \
  -e POSTGRES_USER=your_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=your_database \
  -p 5432:5432 \
  postgres:16-alpine
```

**Native Installation**
Why: Better for production, slightly faster

You'll need to:
1. Install PostgreSQL for your OS
2. Create a user with a password
3. Create a database owned by that user
4. Grant necessary privileges

The key SQL commands you'll need:
- `CREATE USER username WITH PASSWORD 'password';`
- `CREATE DATABASE dbname OWNER username;`
- `GRANT ALL PRIVILEGES ON DATABASE dbname TO username;`

---

## Understanding the Separation

### What Goes Where?

**config.py - Application Settings**
```python
# This is a SETTINGS class, not a data model
class Settings(BaseSettings):
    # Connection information
    database_url: str
    api_key: str

    # Application behavior
    debug: bool = False
    max_connections: int = 10
```

**db/models.py - Database Structure**
```python
# This defines TABLES in PostgreSQL
class Bookmaker(Base):
    __tablename__ = "bookmakers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    # ... defines what columns exist
```

**schemas/bookmaker.py - API Data Validation**
```python
# This defines what data the API ACCEPTS/RETURNS
class BookmakerCreate(BaseModel):
    name: str
    # ... defines what users can send
```

### The Key Insight

Your database structure and your API don't have to match!

Example: Your database has `created_at`, `updated_at`, and `deleted_at` timestamps. Users don't need to send those when creating a record - those are generated automatically. So:

- **SQLAlchemy model** has all 3 timestamp columns
- **Pydantic Create schema** has none of them
- **Pydantic Response schema** includes `created_at` to show users

This separation is powerful because it lets you:
- Hide sensitive database fields (like password hashes)
- Add computed fields to responses
- Accept flexible input formats
- Evolve your database without breaking your API

---

## Database Layer: SQLAlchemy Models

### What is SQLAlchemy Doing?

SQLAlchemy is an **ORM** (Object-Relational Mapper). It translates between:
- Python objects ↔ Database rows
- Python classes ↔ Database tables
- Python attributes ↔ Database columns

### The Basics You Need

**1. Declarative Base**
Every model inherits from a Base class. Why? SQLAlchemy needs to track all your models to create/update tables.

```python
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Now all your models inherit from Base
class YourModel(Base):
    # ...
```

**2. Table Name**
Tell PostgreSQL what to call the table:
```python
__tablename__ = "events"  # Table name in postgres
```

**3. Columns and Types**
Map Python types to PostgreSQL types:
```python
from sqlalchemy import Column, Integer, String, Float, DateTime

id = Column(Integer, primary_key=True)  # auto-incrementing ID
name = Column(String(200), nullable=False)  # VARCHAR(200) NOT NULL
price = Column(Float)  # REAL or DOUBLE PRECISION
created = Column(DateTime, default=datetime.utcnow)  # TIMESTAMP
```

**4. Relationships**
Connect tables together:
```python
# One Event has many Odds
class Event(Base):
    odds = relationship("Odds", back_populates="event")

class Odds(Base):
    event_id = Column(Integer, ForeignKey("events.id"))
    event = relationship("Event", back_populates="odds")
```

### Design Considerations

**Indexes**: Add them to columns you'll query frequently
- `event_id` - you'll look up odds by event
- `timestamp` - you'll filter by time ranges
- Composite indexes for multi-column queries

**Constraints**: Let PostgreSQL enforce data integrity
- `unique=True` - prevent duplicate bookmaker names
- `nullable=False` - require critical fields
- Foreign keys - maintain referential integrity

**Defaults**: Set at the database level
- Timestamps (`default=datetime.utcnow`)
- Status flags (`default=True`)
- Counters (`default=0`)

Why do this in the model instead of application code? **Database-level guarantees** - even if you write data from multiple places, constraints are always enforced.

---

## Validation Layer: Pydantic Schemas

### What is Pydantic Doing?

Pydantic validates data **before** it touches your database. It:
1. Type checks every field
2. Runs custom validation rules
3. Converts data to the right format
4. Rejects invalid requests automatically

### The Pattern: Base → Create → Response

Most entities follow this pattern:

```python
# Base: Shared fields between Create and Response
class BookmakerBase(BaseModel):
    name: str
    is_active: bool = True

# Create: What users send when creating
class BookmakerCreate(BookmakerBase):
    pass  # Just inherits the base fields

# Response: What users get back (includes DB-generated fields)
class BookmakerResponse(BookmakerBase):
    id: int  # Database generated this
    created_at: datetime  # Database generated this

    model_config = ConfigDict(from_attributes=True)  # Allow reading from SQLAlchemy
```

**Why this pattern?**
- **DRY**: Don't repeat field definitions
- **Clear intent**: Separate what comes in vs what goes out
- **Flexibility**: Easy to add response-only fields

### Field Validation

Pydantic's `Field()` lets you add constraints:

```python
from pydantic import Field

class OddsCreate(BaseModel):
    price: float = Field(gt=1.0, le=1000.0)  # Must be > 1.0 and ≤ 1000.0
    outcome: str = Field(min_length=1, max_length=200)
```

Common field validations:
- `gt`, `ge`, `lt`, `le` - numeric bounds
- `min_length`, `max_length` - string length
- `pattern` - regex matching
- `default` - fallback value

### Custom Validators

For complex rules, use validators:

```python
from pydantic import field_validator

class EventCreate(BaseModel):
    commence_time: datetime

    @field_validator('commence_time')
    @classmethod
    def must_be_future(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Event must be in the future')
        return v
```

Use `@field_validator` for:
- Business rules (minimum profit thresholds)
- Cross-field validation
- Data normalization (strip whitespace, round decimals)

### The Crucial Config

```python
model_config = ConfigDict(from_attributes=True)
```

**What does this do?**
Lets Pydantic read from SQLAlchemy objects. Without it, you can't convert database rows to Pydantic models.

**When do you need it?**
On any Pydantic model that will receive SQLAlchemy objects (typically Response models).

---

## Configuration Layer: Settings

### Why Pydantic for Settings?

`pydantic-settings` loads configuration from environment variables with:
- Type checking
- Default values
- Automatic .env file loading
- Validation

### The Settings Pattern

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",  # Load from .env file
        case_sensitive=True  # POSTGRES_USER != postgres_user
    )

    # Database connection
    postgres_user: str = Field(default="user")
    postgres_password: str
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

# Create a single instance
settings = Settings()
```

### Key Concepts

**Environment Variables**
Settings automatically loads from:
1. Environment variables
2. .env file
3. Default values

**Computed Properties**
Use `@property` for derived values like connection strings. Why? You only need to store the parts, and the full URL is built on demand.

**Singleton Pattern**
Create one `settings` instance and import it everywhere. Why? Configuration should be consistent across your app.

---

## How Data Flows Through Your Application

### The Request Journey

```
1. Request arrives: POST /api/v1/odds
   Body: {"event_id": 123, "price": 2.5, ...}

2. FastAPI + Pydantic: Validate input
   → Types correct?
   → Price > 1.0?
   → Required fields present?
   → If invalid: return 422 error immediately

3. Your endpoint: Business logic
   → Does event 123 exist?
   → Is user authorized?
   → Calculate derived values

4. SQLAlchemy: Save to database
   → Convert Pydantic → SQLAlchemy
   → Insert into PostgreSQL
   → Database enforces its constraints

5. PostgreSQL: Store data
   → Apply indexes
   → Maintain foreign keys
   → Return generated ID

6. SQLAlchemy: Fetch fresh data
   → Get the row with generated fields
   → Convert to Python object

7. Pydantic: Format response
   → Convert SQLAlchemy → Pydantic
   → Add computed fields
   → Exclude sensitive data

8. FastAPI: Return JSON
   → Serialize to JSON
   → Set status code
   → Send to client
```

### The Code Pattern

Here's the skeleton you'll use repeatedly:

```python
@router.post("/resource", response_model=ResourceResponse)
def create_resource(
    data: ResourceCreate,  # ← Pydantic validates this
    db: Session = Depends(get_db)  # ← Database connection
):
    # 1. Additional validation (business rules)
    # Check if related records exist, verify permissions, etc.

    # 2. Convert Pydantic → SQLAlchemy
    db_resource = ResourceModel(**data.model_dump())

    # 3. Save to database
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)  # Get generated fields

    # 4. Convert SQLAlchemy → Pydantic and return
    return ResourceResponse.model_validate(db_resource)
```

### Database Session Management

**The Dependency Pattern**
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI injects this automatically
def endpoint(db: Session = Depends(get_db)):
    # Use db here
    # Automatically closed when done
```

**Why this pattern?**
- **Automatic cleanup**: Connection closes even if errors occur
- **Scoped sessions**: Each request gets its own connection
- **Thread safety**: No shared state between requests

---

## Common Patterns and Why They Matter

### 1. The Base Schema Pattern

**Pattern:**
```python
class ResourceBase(BaseModel):
    # Shared fields

class ResourceCreate(ResourceBase):
    # Fields for creation

class ResourceResponse(ResourceBase):
    # Fields + DB-generated fields
```

**Why?**
Reduces duplication and makes intent clear. When you see `Create`, you know it's for incoming data. When you see `Response`, you know it's for outgoing data.

### 2. Nested Relationships

**Problem:** You want to return an Event with all its Odds.

**Solution:** Nested Pydantic models
```python
class OddsResponse(BaseModel):
    id: int
    price: float
    # ...

class EventDetailResponse(BaseModel):
    id: int
    name: str
    odds: list[OddsResponse]  # Nested list
```

**Why?** Pydantic handles the recursion. SQLAlchemy loads the relationships (use `joinedload` for efficiency).

### 3. Custom Validators for Business Logic

**Pattern:**
```python
class ArbitrageCreate(BaseModel):
    profit_percentage: float

    @field_validator('profit_percentage')
    @classmethod
    def validate_realistic_profit(cls, v):
        if v > 50:
            raise ValueError('Profit > 50% is unrealistic')
        return round(v, 2)
```

**Why?**
Validation happens once, automatically, before any business logic runs. Prevents bad data from ever entering your system.

### 4. Model Validators for Cross-Field Logic

**Pattern:**
```python
from pydantic import model_validator

class BetRequest(BaseModel):
    stake: float
    max_loss: float

    @model_validator(mode='after')
    def check_risk_tolerance(self):
        if self.stake > self.max_loss:
            raise ValueError('Stake exceeds risk tolerance')
        return self
```

**Why `mode='after'`?**
All fields are already validated individually. Now validate relationships between fields.

### 5. Database Connection Configuration

**Pattern:**
```python
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=10,        # Keep 10 connections ready
    max_overflow=20      # Allow 20 more if needed
)
```

**Why these settings?**
- `pool_pre_ping`: Detects dead connections (network issues, database restarts)
- `pool_size`: Reuses connections (faster than creating new ones)
- `max_overflow`: Handles traffic spikes without rejecting requests

### 6. Indexes for Query Performance

**Pattern:**
```python
class Odds(Base):
    timestamp = Column(DateTime, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), index=True)
```

**Why?**
Without indexes, PostgreSQL scans every row. With indexes, lookups are logarithmic.

**Rule of thumb:**
- Index foreign keys (you'll always filter by them)
- Index timestamp fields (range queries are common)
- Index fields in WHERE clauses
- Don't over-index (they slow down writes)

---

## Putting It Together: Your Next Steps

### 1. Start with the Database Layer

Create your SQLAlchemy models first. Why? They define what data you can store. Think about:
- What tables do you need?
- How do they relate?
- What constraints matter?

### 2. Build Config Next

Set up your Settings class to load database credentials. You'll need this to connect SQLAlchemy to PostgreSQL.

### 3. Create the Pydantic Schemas

For each SQLAlchemy model, think about:
- What do users send when creating? → Create schema
- What do they send when updating? → Update schema (optional)
- What do they get back? → Response schema
- What business rules apply? → Validators

### 4. Test the Flow

Write a simple endpoint that:
1. Accepts Pydantic input
2. Converts to SQLAlchemy
3. Saves to database
4. Returns Pydantic response

Once you understand this flow, everything else is variations on the theme.

---

## Common Mistakes to Avoid

❌ **Putting Pydantic models in config.py**
→ Config is for settings, not data models

❌ **Using dicts instead of Pydantic models**
→ You lose validation and type safety

❌ **Mixing SQLAlchemy and Pydantic models**
→ They serve different purposes; convert between them

❌ **Forgetting `from_attributes=True`**
→ You can't convert SQLAlchemy → Pydantic without it

❌ **Not using validators**
→ Let Pydantic catch invalid data early

❌ **Over-validating**
→ Database constraints handle some things; don't duplicate

❌ **Ignoring connection pooling**
→ Creating connections is expensive; reuse them

---

## Summary Table

| Layer | File | Purpose | Example |
|-------|------|---------|---------|
| **Config** | `config.py` | App settings & secrets | Database URL, API keys |
| **Database** | `db/models.py` | Table structure | `class Event(Base):` |
| **Validation** | `schemas/event.py` | API contract | `class EventCreate(BaseModel):` |
| **Connection** | `db/base.py` | DB engine & sessions | `engine = create_engine(...)` |
| **Endpoints** | `api/endpoints/` | Request handlers | `@router.post(...)` |

---

## The Core Principle

**Separation of concerns** is the key:
- PostgreSQL cares about storage and relationships
- SQLAlchemy translates between Python and SQL
- Pydantic validates and formats API data
- Config provides connection information

Each layer does one thing well. Together, they create a robust, type-safe, validated system.

When you're building your arbitrage app:
1. Model your data in SQLAlchemy (events, odds, bookmakers)
2. Validate inputs with Pydantic (realistic odds, future events)
3. Connect via Config (database URLs, API keys)
4. Let each layer do its job

That's the pattern. Now go build it!
