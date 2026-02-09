# 📐 ArbitrageEdge - Implementation Guide

This document provides the complete technical specification, project structure, and implementation details for building the Sports Betting Arbitrage Finder API.

## 📁 Project Structure

```
arbitrage-edge/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration and environment variables
│   ├── celery_app.py             # Celery configuration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── arbitrage.py   # Arbitrage endpoints
│   │   │   │   ├── odds.py        # Odds endpoints
│   │   │   │   ├── history.py     # Historical data endpoints
│   │   │   │   └── websocket.py   # WebSocket endpoints
│   │   │   └── router.py          # API router aggregation
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── arbitrage.py           # Arbitrage calculation logic
│   │   ├── odds_fetcher.py        # External API integration
│   │   └── utils.py               # Utility functions
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy base
│   │   ├── session.py             # Database session management
│   │   └── models.py              # Database models
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── arbitrage.py           # Pydantic schemas for arbitrage
│   │   ├── odds.py                # Pydantic schemas for odds
│   │   └── common.py              # Common schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── arbitrage_service.py   # Business logic for arbitrage
│   │   ├── odds_service.py        # Business logic for odds
│   │   └── cache_service.py       # Redis caching service
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── odds_updater.py        # Celery task for updating odds
│   │   └── arbitrage_scanner.py   # Celery task for scanning arbitrage
│   │
│   └── websocket/
│       ├── __init__.py
│       └── manager.py             # WebSocket connection manager
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Pytest fixtures
│   ├── test_arbitrage.py         # Arbitrage tests
│   ├── test_odds.py              # Odds tests
│   └── test_api.py               # API endpoint tests
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── scripts/
│   └── init_db.py                # Database initialization script
│
├── .env.example                   # Example environment variables
├── .gitignore
├── alembic.ini                    # Alembic configuration
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── README.md
└── IMPLEMENTATION.md             # This file
```

## 🔧 Technical Requirements

### Core Dependencies

```txt
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# Redis & Caching
redis==5.0.1
aioredis==2.0.1

# Celery
celery==5.3.4
celery[redis]==5.3.4

# HTTP Client
httpx==0.26.0
aiohttp==3.9.1

# WebSocket
websockets==12.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
pytest-mock==3.12.0

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6

# Monitoring (optional)
prometheus-client==0.19.0
```

### System Requirements

- Python 3.10 or higher
- PostgreSQL 14+
- Redis 7+
- Docker 24+ (for containerized deployment)
- 2GB RAM minimum (4GB recommended)
- The Odds API key (free tier: 500 requests/month)

## 🏗️ Implementation Steps

### Phase 1: Project Setup (Day 1)

1. **Initialize project structure**
```bash
mkdir arbitrage-edge && cd arbitrage-edge
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis celery httpx pydantic-settings alembic pytest
pip freeze > requirements.txt
```

2. **Create configuration system** (`app/config.py`)
   - Load environment variables
   - Define settings using Pydantic BaseSettings
   - Configure database, Redis, API keys

3. **Setup database models** (`app/db/models.py`)
   - Odds table (sport, event, bookmaker, outcome, odds, timestamp)
   - Arbitrage opportunities table
   - Historical data tables

4. **Initialize Alembic**
```bash
alembic init alembic
```

### Phase 2: Core Logic (Days 2-3)

5. **Implement arbitrage calculator** (`app/core/arbitrage.py`)
   - Calculate implied probabilities from decimal odds
   - Detect arbitrage opportunities
   - Calculate optimal stake distribution
   - Compute guaranteed profit

6. **Build odds fetcher** (`app/core/odds_fetcher.py`)
   - Integrate with The Odds API
   - Handle rate limiting
   - Parse and normalize odds data
   - Error handling and retries

7. **Create caching layer** (`app/services/cache_service.py`)
   - Redis integration
   - Cache odds data (TTL: 60 seconds)
   - Cache arbitrage results
   - Implement cache invalidation

### Phase 3: API Development (Days 4-5)

8. **Build API endpoints** (`app/api/v1/endpoints/`)
   - GET `/arbitrage/opportunities` - List current opportunities
   - GET `/arbitrage/opportunities/{sport}` - Filter by sport
   - POST `/arbitrage/calculate` - Calculate custom arbitrage
   - GET `/odds/sports` - Available sports
   - GET `/odds/{sport}` - Current odds for sport
   - GET `/history/arbitrage` - Historical arbitrage data

9. **Implement WebSocket support** (`app/websocket/manager.py`)
   - Connection manager
   - Broadcast arbitrage updates
   - Handle client subscriptions

10. **Add input validation** (`app/schemas/`)
    - Request/response models
    - Data validation with Pydantic
    - Error schemas

### Phase 4: Background Tasks (Day 6)

11. **Setup Celery** (`app/celery_app.py`)
    - Configure Celery with Redis broker
    - Define task routing

12. **Create periodic tasks** (`app/tasks/`)
    - `odds_updater.py` - Fetch odds every 60 seconds
    - `arbitrage_scanner.py` - Scan for opportunities
    - Store results in database and Redis

### Phase 5: Testing & Deployment (Days 7-8)

13. **Write tests** (`tests/`)
    - Unit tests for arbitrage calculations
    - API endpoint tests
    - Integration tests with mocked external APIs

14. **Docker setup**
    - Dockerfile for application
    - docker-compose.yml with services (app, postgres, redis, celery)

15. **Documentation**
    - OpenAPI/Swagger auto-generated
    - README with usage examples
    - API documentation

## 📊 Database Schema Design

You need to design tables that efficiently store odds data and arbitrage opportunities. Here's what to consider:

### Odds Table

**Purpose:** Store odds data fetched from The Odds API

**Required Fields:**
- `id` - Primary key (auto-increment integer)
- `sport` - Which sport (VARCHAR, e.g., "basketball_nba")
- `event_id` - Unique identifier for the sporting event (VARCHAR)
- `event_name` - Human-readable event name (VARCHAR, e.g., "Lakers vs Celtics")
- `commence_time` - When the game starts (TIMESTAMP)
- `bookmaker` - Which bookmaker (VARCHAR, e.g., "DraftKings")
- `market_type` - Type of bet (VARCHAR: "h2h", "spreads", "totals")
- `outcome` - What outcome (VARCHAR, e.g., "Los Angeles Lakers")
- `decimal_odds` - The odds in decimal format (DECIMAL)
- `american_odds` - Optional American format odds (INTEGER, nullable)
- `fetched_at` - When this data was retrieved (TIMESTAMP, default NOW)

**Constraints:**
- UNIQUE constraint on combination: (event_id, bookmaker, market_type, outcome)
  - Prevents duplicate odds entries for the same bet
  - Allows updates to existing odds when refetching

**Indexes to Create:**
- Index on `sport` - You'll filter by sport frequently
- Index on `event_id` - Grouping odds by event
- Index on `fetched_at` - Finding recent odds, cleaning old data

**Design Considerations:**
- Should you store historical odds or just current?
- How long to keep old odds data? (disk space vs analysis needs)
- Consider partitioning by sport for large datasets

---

### Arbitrage Opportunities Table

**Purpose:** Store detected arbitrage opportunities

**Required Fields:**
- `id` - Primary key (auto-increment integer)
- `arbitrage_id` - Unique identifier (VARCHAR, e.g., "arb_20250206_123456")
- `sport` - Which sport (VARCHAR)
- `event_id` - Links to the sporting event (VARCHAR)
- `event_name` - Human-readable event name (VARCHAR)
- `commence_time` - When the game starts (TIMESTAMP)
- `profit_percentage` - Profit margin (DECIMAL, e.g., 4.71)
- `total_stake` - Recommended total stake (DECIMAL, e.g., 1000.00)
- `guaranteed_profit` - Absolute profit amount (DECIMAL, e.g., 47.10)
- `bets` - Details of each bet (JSONB - PostgreSQL supports JSON storage)
- `detected_at` - When arbitrage was found (TIMESTAMP, default NOW)
- `expired` - Whether opportunity is still valid (BOOLEAN, default FALSE)

**JSONB Structure for `bets` Field:**
```json
[
  {
    "bookmaker": "DraftKings",
    "outcome": "Los Angeles Lakers",
    "odds": 2.15,
    "stake": 465.12,
    "potential_return": 1000.00
  },
  {
    "bookmaker": "FanDuel",
    "outcome": "Boston Celtics",
    "odds": 2.05,
    "stake": 534.88,
    "potential_return": 1000.00
  }
]
```

**Indexes to Create:**
- Index on `sport` - Filter by sport
- Index on `profit_percentage` - Find best opportunities
- Index on `detected_at` - Get recent opportunities
- Index on `expired` - Filter only active opportunities

**Design Considerations:**
- Should `arbitrage_id` be generated how? (timestamp + random, UUID, sequential)
- How to mark opportunities as expired? (Celery task, trigger, manual)
- Consider adding `expires_at` field (when commence_time approaches)

---

### Optional: Sports Table (For Reference Data)

**Purpose:** Store metadata about available sports

**Fields:**
- `id` - Primary key
- `sport_key` - API identifier (e.g., "basketball_nba")
- `sport_name` - Display name (e.g., "NBA")
- `active` - Whether to track this sport (BOOLEAN)
- `description` - Optional description

**Why Optional:**
- The Odds API provides this data
- Could cache it in database vs fetching repeatedly
- Useful for admin interface to enable/disable sports

---

### Database Migration Strategy

**Using Alembic:**

1. **Initialize Alembic** (if not done)
   ```bash
   alembic init alembic
   ```

2. **Configure** `alembic.ini` and `alembic/env.py`
   - Set database URL
   - Import your models

3. **Create Initial Migration**
   ```bash
   alembic revision -m "create odds and arbitrage tables"
   ```

4. **Write Migration**
   - Define `upgrade()` function to create tables
   - Define `downgrade()` function to drop tables

5. **Run Migration**
   ```bash
   alembic upgrade head
   ```

**Best Practices:**
- Always write reversible migrations (downgrade)
- Test migrations on dev database first
- Keep migrations small and focused
- Version control your migration files

---

### Data Retention Strategy

**Questions to Answer:**
- How long to keep odds data? (24 hours? 7 days? Forever?)
- How long to keep arbitrage opportunities? (Archive after 30 days?)
- Should you soft-delete or hard-delete old data?

**Recommendations:**
- **Odds Data:** Keep 24-48 hours for analysis, then delete
- **Arbitrage Opportunities:** Keep indefinitely (small data, useful for analysis)
- **Cleanup Task:** Celery periodic task to delete old odds

**Example Cleanup Logic:**
```
Delete odds where fetched_at < (NOW - 48 hours)
Mark arbitrage as expired where commence_time < NOW
```

---

### Performance Optimization

**For High-Volume Queries:**

1. **Partitioning:** Partition odds table by sport or date
2. **Materialized Views:** Pre-compute frequently accessed data
3. **Connection Pooling:** Configure SQLAlchemy pool size appropriately
4. **Bulk Inserts:** Use batch inserts when storing fetched odds
5. **Vacuum/Analyze:** Regular PostgreSQL maintenance

**Query Optimization:**
- Use EXPLAIN ANALYZE to understand query performance
- Add indexes based on actual query patterns
- Consider denormalization for read-heavy queries

---

### Example Queries You'll Need

**Find Current Arbitrage Opportunities:**
```
SELECT * FROM arbitrage_opportunities
WHERE expired = FALSE
  AND commence_time > NOW
  AND profit_percentage >= {min_threshold}
ORDER BY profit_percentage DESC
```

**Get Odds for Specific Event:**
```
SELECT * FROM odds
WHERE event_id = {event_id}
  AND market_type = 'h2h'
ORDER BY bookmaker, outcome
```

**Find Events with Multiple Bookmaker Odds:**
```
SELECT event_id, event_name, COUNT(DISTINCT bookmaker) as bookmaker_count
FROM odds
WHERE sport = {sport}
  AND fetched_at > (NOW - INTERVAL '5 minutes')
GROUP BY event_id, event_name
HAVING COUNT(DISTINCT bookmaker) >= 2
```

**Clean Up Old Odds:**
```
DELETE FROM odds
WHERE fetched_at < (NOW - INTERVAL '48 hours')
```

---

### SQLAlchemy Models Considerations

**When Defining Models:**
- Use declarative base
- Define relationships if needed (probably not for this project)
- Add `__repr__` methods for debugging
- Use Pydantic schemas for API serialization
- Consider using Alembic for migrations from start

**Async Support:**
- Use `AsyncSession` for async database operations
- Configure async engine in SQLAlchemy
- Import from `sqlalchemy.ext.asyncio`

---

### Testing Your Schema

**Test Cases:**
1. Insert odds for same event/bookmaker twice (should update, not duplicate)
2. Query odds by sport and recent timestamp
3. Store arbitrage opportunity with JSONB bets
4. Test index performance with EXPLAIN ANALYZE
5. Verify cascade deletes work as expected (if using)
6. Test data retention cleanup queries

## ⚡ Concurrency & Async Implementation

Concurrency is critical for this project's performance. Here's where and how to implement it:

### 1. Fetching Odds from Multiple Bookmakers (CRITICAL)

**Location:** `app/core/odds_fetcher.py`

**The Problem:** 
You need to fetch odds for multiple sports (NBA, NFL, MLB, Soccer, etc.). If you do this sequentially, and each API call takes 2 seconds, fetching 5 sports would take 10 seconds. With concurrency, you can do this in ~2-3 seconds.

**What You Need to Implement:**

**Class Structure:**
- Create an `OddsFetcher` class that holds your API key and base URL
- The base URL is `https://api.the-odds-api.com/v4`
- Use `httpx.AsyncClient()` instead of the `requests` library (requests is blocking)

**Async Function for Single Sport:**
- Create an async function `fetch_sport_odds(sport: str)` that:
  - Takes a sport key like "basketball_nba"
  - Makes an async GET request to `/sports/{sport}/odds`
  - Includes query params: `apiKey`, `regions` (use "us"), `markets` (use "h2h")
  - Returns the JSON response

**Concurrent Fetching:**
- Create an async function `fetch_all_sports_odds(sports: List[str])` that:
  - Takes a list of sport keys
  - Creates a task for each sport using list comprehension
  - Uses `asyncio.gather(*tasks, return_exceptions=True)` to run them concurrently
  - The `return_exceptions=True` means if one API call fails, others continue
  - Returns the list of results

**Why `return_exceptions=True`:**
- Without it, if one API call fails, the entire `gather()` raises an exception
- With it, failed calls return exception objects instead of raising
- You can then filter out exceptions and process successful results

**Celery Integration Challenge:**
Celery tasks are synchronous by default. To run your async function inside a Celery task:
- Get the event loop with `asyncio.get_event_loop()` or `asyncio.new_event_loop()`
- Run your async function with `loop.run_until_complete(your_async_function())`
- This bridges sync Celery with async code

**Expected Performance:**
- Without concurrency: 5 sports × 2 seconds = 10 seconds
- With concurrency: max(2 seconds) ≈ 2-3 seconds (5x faster!)

---

### 2. Scanning Multiple Events for Arbitrage (IMPORTANT)

**Location:** `app/tasks/arbitrage_scanner.py`

**The Problem:**
After fetching odds, you might have 100+ sporting events. For each event, you need to:
- Group odds by outcome across different bookmakers
- Find the best odds for each outcome
- Calculate if arbitrage exists

Doing this sequentially for 100 events takes ~5 seconds. With concurrency: ~200-300ms.

**What You Need to Implement:**

**Sync Function for Single Event:**
Create a regular (non-async) function `calculate_arbitrage_for_event(event_data: Dict)` that:
- Takes event data with multiple bookmaker odds
- Groups odds by outcome (e.g., all "Lakers" bets together)
- Finds the best (highest) odds for each outcome across bookmakers
- Calculates if arbitrage exists using your arbitrage logic
- Returns arbitrage details if found, or None

**Async Wrapper:**
Since the calculation itself is CPU-bound (math), not I/O-bound:
- Create an async function `scan_event_for_arbitrage_async(event_data: Dict)` that:
  - Calls your sync calculation function
  - Wraps it if needed (or just make it async anyway for consistent interface)
  - Returns the result

**Concurrent Scanning:**
Create an async function `scan_all_events(events: List[Dict])` that:
- Takes a list of events
- Creates a task for each event
- Uses `asyncio.gather(*tasks)` to process all concurrently
- Filters out None results (no arbitrage)
- Returns list of arbitrage opportunities

**Key Insight:**
Even though arbitrage calculation is CPU-bound, you're still gaining performance by:
- Avoiding sequential processing overhead
- Potentially using executor for true parallelism (advanced)
- Consistent async interface for your application

**Expected Performance:**
- Without concurrency: 100 events × 50ms = 5 seconds
- With concurrency: ~200-300ms (16x faster!)

---

### 3. WebSocket Broadcasting (MODERATE)

**Location:** `app/websocket/manager.py`

**The Problem:**
When you find an arbitrage opportunity, you need to notify all connected WebSocket clients. If you have 50 clients and send sequentially, slow clients block fast ones.

**What You Need to Implement:**

**ConnectionManager Class:**
Create a class that manages WebSocket connections:

**Properties:**
- `active_connections`: A list to store active WebSocket objects
- Consider also storing subscriptions (which sports each client wants)

**Methods to Implement:**

`async def connect(websocket: WebSocket)`:
- Call `await websocket.accept()` to accept the connection
- Add the websocket to your active_connections list
- Optionally initialize empty subscription list for this client

`def disconnect(websocket: WebSocket)`:
- Remove the websocket from active_connections
- Clean up any subscriptions for this client

`async def broadcast(message: dict)`:
- Create a list of send tasks: `[connection.send_json(message) for connection in self.active_connections]`
- Use `await asyncio.gather(*tasks, return_exceptions=True)`
- Process the results to identify failed connections
- Remove any connections that failed (they've disconnected)

**Why This Pattern:**
- Without concurrency: Send to client 1, wait... send to client 2, wait... (slow)
- With concurrency: Send to all clients simultaneously
- `return_exceptions=True` prevents one dead connection from blocking others

**Handling Failed Connections:**
After `gather()` returns, iterate through results:
- If a result is an Exception instance, that client disconnected
- Remove them from active_connections
- You can use enumerate to track which index failed

**Advanced: Subscription Management:**
- Store a dict mapping websocket → set of sports they want
- When broadcasting, only send to clients subscribed to that sport
- Messages should include sport identifier

---

### 4. Rate Limiting with Semaphores (IMPORTANT)

**Location:** `app/core/odds_fetcher.py`

**The Problem:**
The Odds API has rate limits (e.g., 500 requests/month on free tier). If you fire off 100 concurrent requests, you'll:
- Hit rate limits immediately
- Possibly get banned
- Waste your API quota

**What You Need to Implement:**

**Semaphore Initialization:**
In your `OddsFetcher` class `__init__`:
- Add a parameter `max_concurrent_requests: int = 5`
- Create a semaphore: `self.semaphore = asyncio.Semaphore(max_concurrent_requests)`

**What a Semaphore Does:**
- Acts like a "token bucket" with N tokens
- When you `async with semaphore:`, you acquire a token
- If no tokens available, the code waits until one is released
- When you exit the context, token is released
- Result: Maximum N operations run simultaneously

**Rate-Limited Fetch Function:**
Create `async def fetch_with_rate_limit(url: str, params: dict)`:
```
async with self.semaphore:  # Acquire token, wait if necessary
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response.json()
```

**Why This Works:**
- Even if you have 100 tasks, only 5 run at a time
- The rest wait in a queue
- No rate limit violations
- Still much faster than sequential (5 at a time vs 1 at a time)

**Fetching Multiple Markets:**
For example, fetching h2h, spreads, and totals for one sport:
- Create 3 tasks, each calling `fetch_with_rate_limit()`
- All 3 respect the same semaphore
- They run concurrently (if tokens available)
- Use `asyncio.gather()` to collect results

**Choosing the Right Limit:**
- Too low (1-2): Slow, not much better than sequential
- Too high (50+): Risk rate limits
- Sweet spot: 5-10 for most APIs
- Check API documentation for recommended limits

---

### 5. Concurrent Database Queries (OPTIONAL)

**Location:** `app/api/v1/endpoints/arbitrage.py`

**The Problem:**
API endpoints sometimes need multiple pieces of data from the database. If you query sequentially, latencies add up.

**What You Need to Implement:**

**Async Database Functions:**
Create async functions for different queries:
- `async def get_current_opportunities(db: AsyncSession) -> List[...]`
- `async def get_historical_arbitrage(db: AsyncSession, days: int) -> List[...]`
- `async def get_arbitrage_statistics(db: AsyncSession) -> Dict[...]`

Each function:
- Takes an `AsyncSession` from SQLAlchemy
- Performs its database query using `await db.execute(...)`
- Returns the results

**Concurrent Execution in Endpoint:**
```
In your endpoint function:
    current_opps, historical, stats = await asyncio.gather(
        get_current_opportunities(db),
        get_historical_arbitrage(db, days=7),
        get_arbitrage_statistics(db)
    )
```

**Requirements for This to Work:**
- Use `AsyncSession` from `sqlalchemy.ext.asyncio`
- Use `asyncpg` driver for PostgreSQL (supports async)
- Configure async engine in your database setup
- Import from `sqlalchemy.ext.asyncio` not regular sqlalchemy

**When This Helps:**
- Queries are independent (no dependencies between them)
- Queries access different tables or data
- All queries are read operations (SELECTs)

**When NOT to Use:**
- Queries depend on each other (query 2 needs result from query 1)
- Write operations that need to be ordered
- Queries that should run in a transaction together

**Expected Performance:**
- Sequential: 3 queries × 100ms = 300ms
- Concurrent: max(100ms, 100ms, 100ms) ≈ 100ms

---

### 6. Async Redis Caching (MODERATE)

**Location:** `app/services/cache_service.py`

**The Problem:**
You'll frequently cache odds data in Redis. Blocking Redis calls slow down your async application.

**What You Need to Implement:**

**CacheService Class:**

**Initialization:**
- Store redis_url
- Initialize redis connection as None (connect later)

**Connection Method:**
Create `async def connect()`:
- Use `aioredis.from_url(redis_url)` or `redis.asyncio.from_url(redis_url)`
- Store the connection as `self.redis`
- Call this at application startup

**Single Item Operations:**

`async def get(key: str)`:
- `result = await self.redis.get(key)`
- If result exists: `return json.loads(result)`
- If not: `return None`

`async def set(key: str, value: dict, ttl: int = 60)`:
- `await self.redis.setex(key, ttl, json.dumps(value))`
- TTL is time-to-live in seconds

**Multiple Item Operations:**

`async def get_multiple(keys: List[str])`:
- Create tasks: `[self.redis.get(key) for key in keys]`
- Results: `await asyncio.gather(*tasks)`
- Parse JSON for non-None results
- Return list of values

`async def set_multiple(items: Dict[str, Dict], ttl: int = 60)`:
- Create tasks: `[self.redis.setex(key, ttl, json.dumps(value)) for key, value in items.items()]`
- `await asyncio.gather(*tasks)`

**Why Use Async Redis:**
- Redis operations are usually very fast (< 1ms)
- But in high-traffic scenarios, async prevents blocking
- Especially important when getting/setting multiple keys
- Maintains consistent async pattern across your app

**Libraries to Use:**
- `aioredis` (older, still works)
- `redis-py` with async support (newer, recommended)

---

### 7. Background Tasks in FastAPI (OPTIONAL)

**Location:** Various API endpoints

**The Problem:**
Some operations shouldn't delay the HTTP response:
- Sending email notifications
- Logging analytics
- Cleanup operations
- Non-critical data processing

**What You Need to Implement:**

**In Your Endpoint:**
Add `BackgroundTasks` as a dependency:
```
from fastapi import BackgroundTasks

@router.post("/arbitrage/notify")
async def create_notification(
    arbitrage_id: str,
    background_tasks: BackgroundTasks
):
    # Do critical work first (store in DB, etc.)
    
    # Queue background tasks
    background_tasks.add_task(send_email_notification, arbitrage_id)
    background_tasks.add_task(send_sms_notification, arbitrage_id)
    background_tasks.add_task(log_to_analytics, arbitrage_id)
    
    # Return immediately (tasks run after response)
    return {"status": "notifications queued"}
```

**Background Task Functions:**
Create async or sync functions:
```
async def send_email_notification(arbitrage_id: str):
    # Fetch arbitrage details from DB
    # Make API call to email service
    # Log success/failure
```

**How It Works:**
1. Your endpoint receives request
2. You queue background tasks with `add_task()`
3. Endpoint returns response to client immediately
4. FastAPI executes background tasks after response is sent
5. Client doesn't wait for these operations

**When to Use:**
- Email/SMS notifications
- Webhook calls to external services
- Analytics logging
- Cache warming
- File cleanup

**When NOT to Use:**
- Critical operations that must complete
- Tasks that might fail and need retry logic
- Long-running tasks (use Celery instead)
- Tasks that need to survive server restart

**Limitations:**
- Tasks run in same process (not distributed)
- If server crashes, tasks are lost
- No retry mechanism
- No task monitoring/management

**BackgroundTasks vs Celery:**
- BackgroundTasks: Simple, immediate, non-critical
- Celery: Reliable, distributed, mission-critical, with retries

---

### Concurrency Summary Table

| Component | Location | Concurrency Pattern | Priority | Performance Gain | Complexity |
|-----------|----------|---------------------|----------|------------------|------------|
| Fetch multiple sports odds | `odds_fetcher.py` | `asyncio.gather()` | **CRITICAL** | 5x faster | Medium |
| Rate-limited API calls | `odds_fetcher.py` | `Semaphore` + `gather()` | **IMPORTANT** | Prevents rate limits | Medium |
| Scan events for arbitrage | `arbitrage_scanner.py` | `asyncio.gather()` | **IMPORTANT** | 10x faster | Low |
| WebSocket broadcasting | `manager.py` | `asyncio.gather()` | **MODERATE** | Better UX | Medium |
| Multiple DB queries | `endpoints/*.py` | `asyncio.gather()` | **OPTIONAL** | 2-3x faster | High |
| Redis operations | `cache_service.py` | `aioredis` library | **MODERATE** | Non-blocking | Low |
| Background tasks | API endpoints | `BackgroundTasks` | **OPTIONAL** | Faster responses | Low |

---

### Performance Impact Example

**Realistic Workflow Without Concurrency:**
```
1. Fetch NBA odds:        2.0s
2. Fetch NFL odds:        2.0s  
3. Fetch MLB odds:        2.0s
4. Fetch Soccer odds:     2.0s
5. Scan 50 NBA events:    2.5s
6. Scan 30 NFL events:    1.5s
7. Scan 40 MLB events:    2.0s
8. Scan 25 Soccer events: 1.2s
───────────────────────────────
Total:                   15.2s
```

**Same Workflow With Concurrency:**
```
1. Fetch all sports (parallel):     2.5s (all at once, max is 2.5s)
2. Scan all events (parallel):      2.5s (all at once, max is 2.5s)
──────────────────────────────────────
Total:                               5.0s (3x faster!)
```

---

### Key Async Patterns You'll Use

**Pattern 1: asyncio.gather() - Run Multiple Tasks**
- Use when: You have multiple independent async operations
- Purpose: Run them all concurrently, wait for all to complete
- Example: Fetching odds from multiple sports
- Return value: List of results in same order as input

**Pattern 2: asyncio.Semaphore - Limit Concurrency**
- Use when: You need to limit how many operations run simultaneously
- Purpose: Prevent overwhelming external APIs or resources
- Example: Limit to 5 concurrent API requests
- Pattern: `async with semaphore:` before the operation

**Pattern 3: async with - Async Context Managers**
- Use when: Working with async resources (clients, connections)
- Purpose: Proper resource management and cleanup
- Example: `async with httpx.AsyncClient() as client:`
- Automatically closes/cleans up when done

**Pattern 4: BackgroundTasks - Fire and Forget**
- Use when: Non-critical work that shouldn't delay response
- Purpose: Improve response time, defer non-essential work
- Example: Sending notifications, logging
- Pattern: `background_tasks.add_task(function, args)`

**Pattern 5: AsyncSession - Async Database**
- Use when: Making database queries in async endpoints
- Purpose: Non-blocking database operations
- Example: Querying arbitrage opportunities
- Requires: AsyncEngine and asyncpg driver

---

### Common Concurrency Pitfalls

**Pitfall 1: Using Blocking Libraries in Async Code**
Problem: Using `requests.get()` in async function blocks the event loop
Solution: Use `httpx.AsyncClient()` or `aiohttp`
Why: Blocking calls freeze all other async operations

**Pitfall 2: Too Many Concurrent Operations**
Problem: Creating 1000 concurrent tasks overwhelms APIs or resources
Solution: Use Semaphore to limit concurrency (e.g., max 10)
Why: External services have rate limits and resource constraints

**Pitfall 3: Not Handling Exceptions in gather()**
Problem: One failed task crashes all concurrent tasks
Solution: Use `return_exceptions=True` in gather()
Why: Failed tasks return exceptions instead of raising

**Pitfall 4: Mixing Event Loops**
Problem: Creating new event loop when one exists
Solution: Use `asyncio.get_event_loop()` to get existing loop
Why: Multiple loops cause conflicts and errors

**Pitfall 5: Forgetting await**
Problem: Calling async function without await
Solution: Always `await` async function calls
Why: Without await, you get a coroutine object, not the result

**Pitfall 6: Database Connection Pool Exhaustion**
Problem: Too many concurrent DB queries exhaust connection pool
Solution: Configure pool size appropriately, limit concurrent queries
Why: Databases have connection limits

**Pitfall 7: Shared Mutable State**
Problem: Multiple tasks modifying same variable without locks
Solution: Avoid shared state, or use `asyncio.Lock()` if needed
Why: Race conditions lead to data corruption

---

### Testing Your Concurrency

**Test 1: Measure Performance Improvement**
```
Without concurrency:
    start = time.time()
    for sport in sports:
        fetch_odds(sport)  # Sequential
    print(time.time() - start)  # e.g., 10 seconds

With concurrency:
    start = time.time()
    await fetch_all_sports_odds(sports)  # Concurrent
    print(time.time() - start)  # e.g., 2.5 seconds
```

**Test 2: Verify Semaphore Limiting**
- Set semaphore limit to 2
- Create 10 tasks
- Monitor: Only 2 should run at a time
- Use logging to track active tasks

**Test 3: Test Exception Handling**
- Mock one API call to fail
- Verify: Other API calls still complete
- Check: Exception is returned in results, not raised

**Test 4: WebSocket Broadcast**
- Connect 10 WebSocket clients
- Send broadcast message
- Verify: All clients receive message
- Disconnect one client mid-broadcast
- Verify: Others still receive message

---

### Resources for Learning Async Python

**Official Documentation:**
- Python asyncio docs: https://docs.python.org/3/library/asyncio.html
- Real Python async tutorial: https://realpython.com/async-io-python/
- FastAPI async guide: https://fastapi.tiangolo.com/async/

**Key Concepts to Study:**
- Event loop (the core scheduler for async operations)
- Coroutines (functions defined with `async def`)
- Tasks (wrapped coroutines running in event loop)
- await (pause execution until operation completes)
- gather() (run multiple coroutines concurrently)
- Semaphore (limit concurrent operations)
- AsyncClient (async HTTP client)
- AsyncSession (async database session)

**Recommended Learning Path:**
1. Understand event loop basics
2. Practice async/await syntax
3. Learn gather() for concurrent operations
4. Study Semaphore for rate limiting
5. Integrate async libraries (httpx, asyncpg)
6. Build this project!

---

### Implementation Strategy

**Phase 1: Build Without Concurrency**
- Get everything working synchronously first
- Verify logic is correct
- Easier to debug

**Phase 2: Add Concurrency to Critical Paths**
- Start with fetching odds (biggest impact)
- Measure performance improvement
- Fix any issues

**Phase 3: Add Concurrency to Secondary Operations**
- Arbitrage scanning
- WebSocket broadcasting
- Redis operations

**Phase 4: Optimize**
- Tune semaphore limits
- Add connection pooling
- Monitor performance

**Testing Each Phase:**
- Measure time with `time.time()` or `time.perf_counter()`
- Use logging to track concurrent operations
- Verify results are same as synchronous version
- Check for race conditions or deadlocks

## 🧮 Arbitrage Calculation Algorithm

This is the mathematical heart of your application. You need to implement these calculations:

### Step 1: Convert Odds to Implied Probability

**What You Need to Know:**
- Decimal odds represent the total payout per dollar wagered
- Implied probability = (1 / decimal_odds) × 100
- Example: Decimal odds of 2.0 = 50% implied probability
- This tells you what percentage chance the bookmaker thinks this outcome has

**What to Implement:**
- A function that takes decimal odds (float) and returns implied probability (percentage)
- Handle edge cases: odds of 1.0 or less (invalid)
- Consider rounding to appropriate decimal places

**Formula to Use:**
```
implied_probability(%) = (1 / decimal_odds) × 100
```

---

### Step 2: Detect Arbitrage Opportunity

**What You Need to Know:**
- Arbitrage exists when total implied probability of all outcomes < 100%
- In a fair market, probabilities should sum to 100% (or slightly higher due to bookmaker margin)
- If sum < 100%, there's a guaranteed profit opportunity
- The difference (100% - sum) represents your profit margin

**What to Implement:**
- Function that takes a list of implied probabilities
- Returns boolean: True if arbitrage exists, False otherwise
- Calculate the profit margin when arbitrage exists

**Logic:**
```
total_probability = sum(all implied probabilities)
is_arbitrage = total_probability < 100
profit_margin = 100 - total_probability (if arbitrage exists)
```

**Example:**
- Bookmaker A offers 2.15 odds on Team X = 46.51% probability
- Bookmaker B offers 2.05 odds on Team Y = 48.78% probability
- Total = 95.29% < 100% → Arbitrage exists! (4.71% profit margin)

---

### Step 3: Calculate Optimal Stakes

**What You Need to Know:**
- You need to bet on ALL outcomes to guarantee profit
- Stakes must be distributed so that you win the same amount regardless of outcome
- The formula ensures equal returns from any outcome

**What to Implement:**
- Function that takes total stake amount and list of decimal odds
- Returns list of optimal stakes for each outcome
- All bets should produce the same return

**Formula for Each Stake:**
```
For outcome i:
stake_i = (total_stake × (1/odds_i)) / sum(1/odds_j for all outcomes j)
```

**Key Points:**
- Stakes should sum to your total stake amount
- When multiplied by their respective odds, all outcomes return the same amount
- This guaranteed return will be higher than your total stake (that's your profit)

**Example Logic:**
```
Total stake: $1000
Odds: [2.15, 2.05]

Calculate inverse odds sum: (1/2.15) + (1/2.05)
For stake 1: $1000 × (1/2.15) / inverse_sum
For stake 2: $1000 × (1/2.05) / inverse_sum

Verify: stake_1 + stake_2 should equal $1000
Verify: stake_1 × 2.15 should equal stake_2 × 2.05
```

---

### Step 4: Calculate Guaranteed Profit

**What You Need to Know:**
- Pick any outcome and calculate: stake × odds = guaranteed return
- All outcomes produce the same return (from step 3)
- Profit = guaranteed return - total stake invested

**What to Implement:**
- Function that calculates the guaranteed return from any bet
- Subtract total stake to get profit
- Return both absolute profit and profit percentage

**Formula:**
```
guaranteed_return = stake[0] × odds[0]  (or any index, all equal)
profit = guaranteed_return - total_stake
profit_percentage = (profit / total_stake) × 100
```

---

### Complete Example Walkthrough

**Given:**
- Event: Lakers vs Celtics
- Bookmaker A: Lakers @ 2.15
- Bookmaker B: Celtics @ 2.05
- Total stake: $1000

**Step 1 - Implied Probabilities:**
- Lakers: (1 / 2.15) × 100 = 46.51%
- Celtics: (1 / 2.05) × 100 = 48.78%

**Step 2 - Check Arbitrage:**
- Total probability: 46.51% + 48.78% = 95.29%
- Is arbitrage? 95.29% < 100% → YES
- Profit margin: 100% - 95.29% = 4.71%

**Step 3 - Calculate Stakes:**
- Inverse sum: (1/2.15) + (1/2.05) = 0.9529
- Lakers stake: $1000 × (1/2.15) / 0.9529 = $488.09
- Celtics stake: $1000 × (1/2.05) / 0.9529 = $511.91
- Verify: $488.09 + $511.91 ≈ $1000 ✓

**Step 4 - Calculate Profit:**
- If Lakers win: $488.09 × 2.15 = $1049.39
- If Celtics win: $511.91 × 2.05 = $1049.42
- Guaranteed return: ~$1049
- Profit: $1049 - $1000 = $49
- Profit %: ($49 / $1000) × 100 = 4.9%

---

### Edge Cases to Handle

1. **Invalid Odds:**
   - Odds ≤ 1.0 (impossible in real betting)
   - Missing odds for any outcome
   - Non-numeric odds values

2. **Floating Point Precision:**
   - Stakes might not sum exactly to total due to rounding
   - Acceptable difference: ±$0.01
   - Use decimal.Decimal for financial calculations if needed

3. **More Than Two Outcomes:**
   - Some sports have 3 outcomes (win/loss/draw)
   - Formula works the same, just more items in the list
   - Example: Soccer has home/away/draw

4. **Minimum Profit Threshold:**
   - Don't report arbitrage with < 1% profit (transaction costs)
   - Configuration: MIN_PROFIT_THRESHOLD

5. **Maximum Stake Limits:**
   - Bookmakers have betting limits
   - You might not be able to place the full calculated stake
   - Consider checking if calculated stakes are realistic

---

### Testing Your Implementation

**Test Case 1: Clear Arbitrage**
```
Input: odds = [2.15, 2.05], stake = 1000
Expected: is_arbitrage = True, profit ≈ $49, profit_% ≈ 4.9%
```

**Test Case 2: No Arbitrage**
```
Input: odds = [1.90, 1.80], stake = 1000
Expected: is_arbitrage = False
(Probabilities: 52.63% + 55.56% = 108.19% > 100%)
```

**Test Case 3: Three Outcomes (Soccer)**
```
Input: odds = [3.50, 3.40, 2.30], stake = 1000
Calculate: implied probabilities sum
Determine: arbitrage exists?
```

**Test Case 4: Perfect Market (No Arbitrage)**
```
Input: odds = [2.00, 2.00], stake = 1000
Expected: probabilities = 50% + 50% = 100% (no arbitrage)
```

**Test Case 5: Edge of Profitability**
```
Input: odds that give 0.5% profit margin
Should you report this? (Consider MIN_PROFIT_THRESHOLD)
```

---

### Implementation Tips

1. **Start with Clear Functions:**
   - One function per step (conversion, detection, stake calculation, profit)
   - Keep them pure functions (no side effects)
   - Easy to test individually

2. **Data Structures:**
   - Input: List of odds with metadata (bookmaker, outcome)
   - Output: Dictionary with all arbitrage details
   - Consider using Pydantic models for validation

3. **Validation:**
   - Validate odds are positive numbers
   - Validate total stake is positive
   - Validate all outcomes are present

4. **Precision:**
   - Financial calculations need precision
   - Round appropriately for display
   - Consider using Decimal type for calculations

5. **Documentation:**
   - Comment the formulas in your code
   - Include examples in docstrings
   - Future you will thank you!

## 🔄 Data Flow

### Odds Update Flow
```
┌─────────────┐
│ Celery Beat │ Triggers every 60 seconds
└──────┬──────┘
       │
       v
┌──────────────────┐
│ odds_updater.py  │ Celery task
└────────┬─────────┘
         │
         v
┌─────────────────────┐
│ The Odds API        │ External API call
└──────────┬──────────┘
           │
           v
┌──────────────────────┐
│ Parse & Normalize    │
└──────────┬───────────┘
           │
           ├─→ PostgreSQL (persist)
           │
           └─→ Redis (cache, TTL: 60s)
```

### Arbitrage Detection Flow
```
┌─────────────┐
│ Celery Beat │ Triggers every 30 seconds
└──────┬──────┘
       │
       v
┌───────────────────────┐
│ arbitrage_scanner.py  │ Celery task
└────────┬──────────────┘
         │
         v
┌────────────────────────┐
│ Fetch from Redis cache │
└────────┬───────────────┘
         │
         v
┌──────────────────────────┐
│ Group by event           │
│ Compare odds across      │
│ different bookmakers     │
└────────┬─────────────────┘
         │
         v
┌──────────────────────────┐
│ Calculate arbitrage      │
│ (core/arbitrage.py)      │
└────────┬─────────────────┘
         │
         ├─→ PostgreSQL (if arbitrage found)
         │
         ├─→ Redis (cache result)
         │
         └─→ WebSocket broadcast to clients
```

### API Request Flow
```
┌─────────────┐
│ HTTP Client │
└──────┬──────┘
       │
       v
┌──────────────────────────┐
│ FastAPI Endpoint         │
│ /arbitrage/opportunities │
└────────┬─────────────────┘
         │
         v
┌─────────────────────┐
│ Check Redis Cache   │
└────────┬────────────┘
         │
         ├─→ Cache Hit? Return immediately
         │
         └─→ Cache Miss?
             │
             v
         ┌──────────────────┐
         │ Query PostgreSQL │
         └────────┬─────────┘
                  │
                  v
         ┌─────────────────────┐
         │ Update Redis Cache  │
         └────────┬────────────┘
                  │
                  v
         ┌────────────────┐
         │ Return to User │
         └────────────────┘
```

## 🎯 API Endpoints Specification

Design and implement these RESTful endpoints:

### GET `/api/v1/arbitrage/opportunities`

**Purpose:** Retrieve all current arbitrage opportunities

**Query Parameters:**
- `sport` (optional, string): Filter by specific sport
  - Example: "basketball_nba", "americanfootball_nfl"
- `min_profit` (optional, float, default: 1.0): Minimum profit percentage
- `max_profit` (optional, float): Maximum profit percentage
- `limit` (optional, int, default: 50): Number of results to return
- `offset` (optional, int, default: 0): Pagination offset

**Response Status Codes:**
- 200: Success
- 400: Invalid query parameters
- 500: Server error

**Response Body Structure:**
```json
{
  "total": 15,
  "opportunities": [
    {
      "arbitrage_id": "arb_20250206_123456",
      "sport": "basketball_nba",
      "event": "Los Angeles Lakers vs Boston Celtics",
      "commence_time": "2025-02-07T01:00:00Z",
      "profit_percentage": 4.2,
      "total_stake": 1000,
      "bets": [
        {
          "bookmaker": "DraftKings",
          "outcome": "Los Angeles Lakers",
          "odds": 2.15,
          "stake": 465.12,
          "potential_return": 1000
        },
        {
          "bookmaker": "FanDuel",
          "outcome": "Boston Celtics",
          "odds": 2.05,
          "stake": 534.88,
          "potential_return": 1000
        }
      ],
      "guaranteed_profit": 42.00,
      "detected_at": "2025-02-06T12:34:56Z"
    }
  ]
}
```

**Implementation Considerations:**
- Query database with filters
- Use Redis cache (key: sport, TTL: 30 seconds)
- Handle pagination properly
- Validate query parameters with Pydantic

---

### POST `/api/v1/arbitrage/calculate`

**Purpose:** Calculate arbitrage for custom odds provided by user

**Request Body:**
```json
{
  "odds": [
    {
      "outcome": "Team A",
      "decimal_odds": 2.10,
      "bookmaker": "Bookmaker1"
    },
    {
      "outcome": "Team B",
      "decimal_odds": 2.20,
      "bookmaker": "Bookmaker2"
    }
  ],
  "total_stake": 1000
}
```

**Request Validation:**
- `odds` array must have at least 2 items
- Each odds entry must have outcome, decimal_odds, bookmaker
- `decimal_odds` must be > 1.0
- `total_stake` must be > 0

**Response Status Codes:**
- 200: Success (calculation completed)
- 400: Invalid input (missing fields, invalid odds)
- 422: Validation error

**Response Body:**
```json
{
  "is_arbitrage": true,
  "profit_percentage": 4.76,
  "guaranteed_profit": 47.62,
  "total_stake": 1000,
  "bets": [
    {
      "outcome": "Team A",
      "bookmaker": "Bookmaker1",
      "odds": 2.10,
      "stake": 511.90,
      "potential_return": 1075.00
    },
    {
      "outcome": "Team B",
      "bookmaker": "Bookmaker2",
      "odds": 2.20,
      "stake": 488.10,
      "potential_return": 1073.82
    }
  ]
}
```

**Implementation Considerations:**
- This is a stateless calculation (no database needed)
- Use your arbitrage calculation logic
- Return results immediately (no caching needed)
- Consider rate limiting (prevent abuse)

---

### GET `/api/v1/odds/sports`

**Purpose:** List all available sports

**Query Parameters:**
- None (or optional `active_only` boolean)

**Response:**
```json
{
  "sports": [
    {
      "key": "basketball_nba",
      "name": "NBA",
      "description": "US National Basketball Association"
    },
    {
      "key": "americanfootball_nfl",
      "name": "NFL",
      "description": "US National Football League"
    }
  ]
}
```

**Implementation Considerations:**
- Could fetch from The Odds API `/sports` endpoint
- Or maintain static list in config
- Cache heavily (sports don't change often)

---

### GET `/api/v1/odds/{sport}`

**Purpose:** Get current odds for a specific sport

**Path Parameters:**
- `sport`: Sport key (e.g., "basketball_nba")

**Query Parameters:**
- `market` (optional, default: "h2h"): Market type
  - Options: "h2h" (head-to-head), "spreads", "totals"
- `bookmakers` (optional): Comma-separated list of bookmakers to include
  - Example: "draftkings,fanduel,betmgm"

**Response:**
```json
{
  "sport": "basketball_nba",
  "events": [
    {
      "event_id": "abc123",
      "event_name": "Los Angeles Lakers vs Boston Celtics",
      "commence_time": "2025-02-07T01:00:00Z",
      "bookmakers": [
        {
          "bookmaker": "DraftKings",
          "markets": [
            {
              "market_type": "h2h",
              "outcomes": [
                {
                  "name": "Los Angeles Lakers",
                  "decimal_odds": 2.15
                },
                {
                  "name": "Boston Celtics",
                  "decimal_odds": 1.80
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Implementation Considerations:**
- Query from database (recently fetched odds)
- Or fetch from The Odds API in real-time
- Use Redis cache (TTL: 60 seconds)
- Filter by bookmakers if requested

---

### GET `/api/v1/history/arbitrage`

**Purpose:** Get historical arbitrage opportunities

**Query Parameters:**
- `sport` (optional): Filter by sport
- `start_date` (optional): ISO 8601 date
- `end_date` (optional): ISO 8601 date
- `min_profit` (optional): Minimum profit percentage
- `limit` (optional, default: 100)
- `offset` (optional, default: 0)

**Response:**
Similar to opportunities endpoint but includes expired opportunities

**Implementation Considerations:**
- Query arbitrage_opportunities table
- Include expired opportunities
- Order by detected_at DESC
- Support date range filtering

---

### WebSocket `/ws/arbitrage`

**Purpose:** Real-time arbitrage opportunity updates

**Connection Protocol:**
- Standard WebSocket connection
- Client connects: `ws://localhost:8000/ws/arbitrage`

**Client → Server Messages:**
```json
{
  "action": "subscribe",
  "sports": ["basketball_nba", "americanfootball_nfl"]
}
```

```json
{
  "action": "unsubscribe",
  "sports": ["basketball_nba"]
}
```

**Server → Client Messages:**
```json
{
  "type": "arbitrage_opportunity",
  "data": {
    "arbitrage_id": "arb_20250206_123456",
    "sport": "basketball_nba",
    "event": "Los Angeles Lakers vs Boston Celtics",
    "profit_percentage": 4.2,
    "bets": [...]
  }
}
```

```json
{
  "type": "error",
  "message": "Invalid sport key"
}
```

**Implementation Considerations:**
- Maintain connection manager with active connections
- Store client subscriptions (which sports they want)
- When arbitrage is detected (Celery task), broadcast to subscribed clients
- Handle disconnections gracefully
- Consider heartbeat/ping-pong to detect dead connections

---

### Additional Endpoint Ideas (Optional)

**GET `/api/v1/stats/sports/{sport}`**
- Statistics about a sport (avg profit, opportunities count, etc.)

**GET `/api/v1/bookmakers`**
- List all bookmakers being tracked

**POST `/api/v1/alerts`**
- Create alert for specific criteria (profit threshold, sport, etc.)

---

### API Design Best Practices

**Versioning:**
- Use `/api/v1/` prefix
- Allows future API changes without breaking clients

**Error Responses:**
- Consistent error format
```json
{
  "error": "ValidationError",
  "message": "Invalid sport key",
  "details": { ... }
}
```

**Rate Limiting:**
- Consider implementing rate limits (e.g., 100 requests/minute)
- Return 429 status code when exceeded
- Include rate limit headers in response

**CORS:**
- Configure CORS for frontend access
- Set allowed origins in environment config

**Authentication (Future):**
- Currently open API, but consider adding API keys
- Use FastAPI dependencies for auth
- Protect certain endpoints (POST, DELETE)

**Documentation:**
- FastAPI auto-generates OpenAPI docs
- Available at `/docs` and `/redoc`
- Add docstrings to endpoint functions for better docs

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
ODDS_API_KEY=your_api_key_here

# Database Configuration
POSTGRES_USER=arbitrage_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=arbitrage_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/${REDIS_DB}

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# API Settings
API_V1_PREFIX=/api/v1
PROJECT_NAME=ArbitrageEdge
VERSION=1.0.0

# Arbitrage Settings
MIN_PROFIT_THRESHOLD=1.0        # Minimum profit % to report
MAX_STAKE=1000                  # Maximum stake per arbitrage
ODDS_UPDATE_INTERVAL=60         # Seconds between odds updates
ARBITRAGE_SCAN_INTERVAL=30      # Seconds between arbitrage scans

# The Odds API Settings
ODDS_API_BASE_URL=https://api.the-odds-api.com/v4
ODDS_REGIONS=us                 # us, uk, eu, au
ODDS_MARKETS=h2h                # h2h, spreads, totals
ODDS_DATE_FORMAT=iso

# Caching
CACHE_TTL_ODDS=60              # Cache odds for 60 seconds
CACHE_TTL_ARBITRAGE=30         # Cache arbitrage results for 30 seconds

# Rate Limiting
RATE_LIMIT_REQUESTS=100        # Requests per minute
RATE_LIMIT_PERIOD=60           # Period in seconds

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Development
DEBUG=False
RELOAD=False
```

## 🧪 Testing Strategy

A comprehensive testing strategy for production-ready code:

### Unit Tests

**What to Test:**
- Arbitrage calculation logic (core business logic)
- Odds conversion functions
- Data validation and serialization
- Utility functions

**Location:** `tests/test_arbitrage.py`, `tests/test_core.py`

**Testing Framework:** pytest

**Example Test Cases for Arbitrage Calculator:**

**Test 1: Decimal to Implied Probability**
- Input: decimal odds = 2.0
- Expected: 50.0% probability
- Input: decimal odds = 4.0
- Expected: 25.0% probability

**Test 2: Arbitrage Detection (Positive Case)**
- Input: implied probabilities = [48.0, 47.0]
- Expected: is_arbitrage = True (sum = 95% < 100%)

**Test 3: Arbitrage Detection (Negative Case)**
- Input: implied probabilities = [51.0, 52.0]
- Expected: is_arbitrage = False (sum = 103% > 100%)

**Test 4: Stake Calculation**
- Input: total_stake = 1000, odds = [2.15, 2.05]
- Expected: stakes sum to 1000, equal returns from each bet
- Verify: abs(sum(stakes) - 1000) < 0.01
- Verify: abs(stakes[0] * 2.15 - stakes[1] * 2.05) < 0.01

**Test 5: Edge Cases**
- Invalid odds (≤ 1.0)
- Missing odds
- Single outcome (need at least 2)
- Very small profit margins (< 0.1%)

**How to Structure Tests:**
```
tests/
├── test_arbitrage.py      # Core arbitrage logic
├── test_odds_fetcher.py   # API integration (mocked)
├── test_cache_service.py  # Redis caching
└── test_utils.py          # Utility functions
```

**Pytest Features to Use:**
- Fixtures for setup/teardown
- Parametrize for testing multiple inputs
- Mock external API calls
- Async test support with pytest-asyncio

---

### Integration Tests

**What to Test:**
- API endpoints (full request/response cycle)
- Database operations
- Celery tasks
- WebSocket connections

**Location:** `tests/test_api.py`, `tests/test_integration.py`

**Test Database:**
- Use separate test database
- Reset database between tests
- Use pytest fixtures for database setup

**Example Test Cases for API:**

**Test 1: GET /arbitrage/opportunities**
- Expected: 200 status code
- Expected: Response contains "opportunities" key
- Expected: Data structure matches schema

**Test 2: POST /arbitrage/calculate**
- Input: Valid odds data
- Expected: 200 status code
- Expected: Correct arbitrage calculation
- Expected: Response matches Pydantic schema

**Test 3: POST /arbitrage/calculate (Invalid Input)**
- Input: Missing required fields
- Expected: 422 status code (validation error)

**Test 4: GET /odds/{sport} (Invalid Sport)**
- Input: Non-existent sport key
- Expected: 404 status code

**Test 5: WebSocket Connection**
- Test: Connect and subscribe to sport
- Expected: Connection accepted
- Test: Send arbitrage update
- Expected: Client receives message

**Testing Tools:**
- FastAPI TestClient for API testing
- httpx for async requests
- pytest-asyncio for async tests
- Factory Boy or factories for test data

---

### Mocking External APIs

**Why Mock:**
- The Odds API has rate limits
- Don't want to make real API calls in tests
- Tests should be fast and reliable
- Control test scenarios (success, failure, edge cases)

**What to Mock:**
- HTTP requests to The Odds API
- Redis operations (optional - could use Redis mock or real Redis)
- Database operations (optional - could use test database)

**Libraries to Use:**
- pytest-mock
- responses (for HTTP mocking)
- fakeredis (for Redis mocking)

**Example Mock Scenarios:**

**Scenario 1: Successful Odds Fetch**
- Mock response: Valid odds data
- Verify: Data is parsed correctly
- Verify: Data is stored in database

**Scenario 2: API Rate Limit Error**
- Mock response: 429 status code
- Verify: Error is handled gracefully
- Verify: Retry logic works (if implemented)

**Scenario 3: API Timeout**
- Mock: Request times out
- Verify: Timeout is caught
- Verify: Appropriate error logged

**Scenario 4: Invalid API Response**
- Mock: Malformed JSON response
- Verify: Parsing error is handled
- Verify: System continues operating

---

### Testing Celery Tasks

**Challenges:**
- Async task execution
- Task scheduling
- Testing periodic tasks

**Approaches:**

**Approach 1: Synchronous Testing**
- Call task function directly (not .delay())
- Test logic without Celery overhead
- Fast and simple

**Approach 2: Eager Mode**
- Configure Celery to run tasks synchronously
- Set `task_always_eager = True` in test config
- Tasks execute immediately, not in background

**Test Cases:**

**Test: Odds Update Task**
- Mock: The Odds API response
- Run: Task function
- Verify: Database contains new odds
- Verify: Redis cache is updated

**Test: Arbitrage Scanner Task**
- Setup: Database with odds data
- Run: Scanner task
- Verify: Arbitrage opportunities detected and stored

**Test: Cleanup Task**
- Setup: Database with old odds
- Run: Cleanup task
- Verify: Old data is deleted
- Verify: Recent data remains

---

### Performance Testing (Optional)

**What to Test:**
- API endpoint response times
- Concurrent request handling
- Database query performance
- Celery task throughput

**Tools:**
- locust (load testing)
- pytest-benchmark (microbenchmarks)
- EXPLAIN ANALYZE (database queries)

**Example Scenarios:**

**Load Test 1: GET /arbitrage/opportunities**
- Simulate: 100 concurrent users
- Measure: Response time, error rate
- Expected: < 200ms response time, 0% errors

**Load Test 2: WebSocket Connections**
- Simulate: 100 concurrent WebSocket connections
- Measure: Broadcast latency
- Expected: All clients receive updates within 1 second

**Benchmark: Arbitrage Calculation**
- Test: Calculate arbitrage for 1000 events
- Measure: Time taken
- Expected: < 1 second (with concurrency)

---

### Test Coverage

**Goal:** Aim for 80%+ code coverage

**How to Measure:**
```bash
pytest --cov=app --cov-report=html
```

**What to Cover:**
- All business logic (arbitrage calculations)
- API endpoints
- Database models
- Error handling paths
- Edge cases

**What Can Skip:**
- Configuration files
- Database migrations
- Simple getters/setters
- External library code

---

### Testing Best Practices

**1. Arrange-Act-Assert Pattern**
- Arrange: Set up test data and conditions
- Act: Execute the code being tested
- Assert: Verify the results

**2. Test Independence**
- Each test should run independently
- Don't rely on execution order
- Clean up after each test

**3. Use Descriptive Names**
- test_arbitrage_detection_returns_true_when_sum_less_than_100
- test_api_returns_422_for_invalid_odds_input

**4. Test Edge Cases**
- Empty inputs
- Null values
- Extreme values (very large, very small)
- Boundary conditions

**5. Keep Tests Fast**
- Mock expensive operations
- Use in-memory databases where possible
- Run slow tests separately

**6. Test Error Paths**
- Don't just test happy path
- Test what happens when things fail
- Verify error messages are helpful

---

### Continuous Integration (CI)

**GitHub Actions Workflow Example:**

**On Every Commit:**
- Run linter (black, flake8, mypy)
- Run all tests
- Check code coverage
- Verify migrations can run

**Pre-Deployment:**
- Run integration tests
- Run load tests (optional)
- Check for security vulnerabilities

**Tools:**
- GitHub Actions
- GitLab CI
- CircleCI
- Travis CI

---

### Test Data Management

**Fixtures:**
- Create reusable test data with pytest fixtures
- Examples: sample odds data, mock API responses

**Factories:**
- Use Factory Boy to generate test objects
- Easier to create variations of test data

**Database Seeding:**
- Script to populate test database with realistic data
- Useful for manual testing and integration tests

---

### Running Tests

**Run All Tests:**
```bash
pytest
```

**Run Specific Test File:**
```bash
pytest tests/test_arbitrage.py
```

**Run Specific Test Function:**
```bash
pytest tests/test_arbitrage.py::test_calculate_implied_probability
```

**Run with Coverage:**
```bash
pytest --cov=app --cov-report=html
```

**Run Async Tests:**
```bash
pytest -v tests/test_async.py
```

**Run in Parallel (Faster):**
```bash
pytest -n auto
```

## 🚀 Deployment Checklist

- [ ] Set up production environment variables
- [ ] Configure PostgreSQL database
- [ ] Set up Redis instance
- [ ] Obtain The Odds API key
- [ ] Build Docker images
- [ ] Run database migrations
- [ ] Start Celery workers
- [ ] Start Celery beat scheduler
- [ ] Start FastAPI application
- [ ] Configure reverse proxy (nginx)
- [ ] Set up SSL certificates
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging aggregation
- [ ] Configure automated backups
- [ ] Test all endpoints
- [ ] Load testing
- [ ] Set up alerts for errors

## 📈 Performance Optimization Tips

1. **Database Indexes:** Ensure proper indexes on frequently queried columns
2. **Connection Pooling:** Use SQLAlchemy connection pooling
3. **Redis Caching:** Cache frequently accessed data
4. **Async Operations:** Use asyncio for concurrent API calls
5. **Rate Limiting:** Implement rate limiting to protect external API quotas
6. **Query Optimization:** Use database query optimization techniques
7. **CDN:** Use CDN for static assets if you add a frontend
8. **Horizontal Scaling:** Scale Celery workers based on load

## 🎓 Learning Resources

- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Arbitrage Betting Guide](https://en.wikipedia.org/wiki/Arbitrage_betting)

## 🤔 Common Issues & Solutions

**Issue:** Rate limit exceeded on The Odds API
- **Solution:** Implement exponential backoff, increase cache TTL, reduce polling frequency

**Issue:** Arbitrage opportunities disappear before execution
- **Solution:** This is normal - odds change rapidly. Reduce detection latency, implement faster execution

**Issue:** WebSocket connections dropping
- **Solution:** Implement heartbeat/ping-pong, reconnection logic, connection pooling

**Issue:** High database load
- **Solution:** Implement read replicas, optimize queries, increase connection pool size

---

Ready to build! Start with Phase 1 and work through systematically. Good luck with your tech lead interview prep! 🚀
