# Phase 1: Data Collection - GitHub Dockerfile Scraper

This scraper collects 50,000+ Dockerfiles from GitHub repositories with full context (README, dependencies, metadata).

---

## Prerequisites

- GitHub Personal Access Token
- PostgreSQL database
- Python 3.8+

---

## Step 1: PostgreSQL Setup

### On WSL2/Ubuntu/Debian

#### 1.1 Install PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

#### 1.2 Start PostgreSQL
```bash
sudo service postgresql start
```

#### 1.3 Create Database and User

**Option A: Individual Commands (Works with Fish shell)**
```bash
sudo -u postgres psql -c "CREATE USER harvester WITH PASSWORD 'mysecurepassword';"
sudo -u postgres psql -c "CREATE DATABASE dockerfile_data OWNER harvester;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dockerfile_data TO harvester;"
```

**Option B: Interactive (Most reliable)**
```bash
# Enter PostgreSQL as postgres user
sudo -u postgres psql

# Then run these commands:
CREATE USER harvester WITH PASSWORD 'mysecurepassword';
CREATE DATABASE dockerfile_data OWNER harvester;
GRANT ALL PRIVILEGES ON DATABASE dockerfile_data TO harvester;
\q
```

**Option C: For Bash/Zsh users**
```bash
sudo -u postgres psql << EOF
CREATE USER harvester WITH PASSWORD 'mysecurepassword';
CREATE DATABASE dockerfile_data OWNER harvester;
GRANT ALL PRIVILEGES ON DATABASE dockerfile_data TO harvester;
EOF
```

#### 1.4 Verify Installation
```bash
# Test connection
psql -U harvester -d dockerfile_data -h localhost

# You should see:
# Password for user harvester: (enter: mysecurepassword)
# dockerfile_data=>

# Type \q to exit
```

#### 1.5 Auto-start PostgreSQL (Optional)
```bash
# For Bash/Zsh - Add to ~/.bashrc or ~/.zshrc
echo 'sudo service postgresql start' >> ~/.bashrc

# For Fish - Add to ~/.config/fish/config.fish
echo 'sudo service postgresql start' >> ~/.config/fish/config.fish
```

---

### On macOS

```bash
# Install via Homebrew
brew install postgresql@15

# Start PostgreSQL
brew services start postgresql@15

# Create database and user
psql postgres << EOF
CREATE USER harvester WITH PASSWORD 'mysecurepassword';
CREATE DATABASE dockerfile_data OWNER harvester;
GRANT ALL PRIVILEGES ON DATABASE dockerfile_data TO harvester;
EOF
```

---

### Using Docker (Cross-platform)

```bash
# Run PostgreSQL in Docker
docker run -d \
  --name dockerforge-db \
  -e POSTGRES_USER=harvester \
  -e POSTGRES_PASSWORD=mysecurepassword \
  -e POSTGRES_DB=dockerfile_data \
  -p 5432:5432 \
  -v dockerforge-data:/var/lib/postgresql/data \
  postgres:15-alpine

# Verify it's running
docker ps | grep dockerforge-db

# Connect to test
docker exec -it dockerforge-db psql -U harvester -d dockerfile_data
```

---

## Step 2: GitHub Personal Access Token

### 2.1 Create Token
1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Give it a name: `dockerforge-scraper`
4. Select scopes:
   - ✅ `public_repo` (Access public repositories)
   - ✅ `read:org` (Read organization data)
5. Click **"Generate token"**
6. **Copy the token** (starts with `ghp_...`)

⚠️ **Important**: Save this token somewhere safe! GitHub only shows it once.

### 2.2 Test Your Token
```bash
# Test the token works
curl -H "Authorization: token ghp_YOUR_TOKEN_HERE" https://api.github.com/user

# You should see your GitHub user info
```

---

## Step 3: Install Python Dependencies

```bash
# Navigate to project root
cd dockerforge

# Install dependencies
pip install requests psycopg2-binary

# Or use requirements.txt if it exists
pip install -r requirements.txt
```

---

## Step 4: Configure the Scraper

### Option A: Environment Variables (Recommended)
```bash
# Create .env file in 1-scraping/
cd 1-scraping
cat > .env << 'EOF'
GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
DB_HOST=localhost
DB_NAME=dockerfile_data
DB_USER=harvester
DB_PASSWORD=mysecurepassword
DB_PORT=5432
EOF

# Make sure .env is in .gitignore (should already be there)
```

### Option B: Edit Script Directly
```bash
# Edit github_scraper.py
nano github_scraper.py

# Change these lines near the top:
GITHUB_TOKEN = "ghp_YOUR_TOKEN_HERE"
DB_DSN = "dbname=dockerfile_data user=harvester password=mysecurepassword host=localhost"
```

---

## Step 5: Run the Scraper

### 5.1 Start Scraping
```bash
cd 1-scraping
python github_scraper.py

# You'll be prompted for your GitHub token if not configured
# Enter: ghp_YOUR_TOKEN_HERE
```

### 5.2 Expected Output
```
============================================================
[*] Rate Limits:
    Core API: 5000/5000
    Search API: 30/30

[*] Target: 50000 repositories with Dockerfiles
[*] Starting scrape...

============================================================
Scraping Python repositories
============================================================

[*] Page 1/10 for Python
[*] Found 2847 repos (page 1)

[*] Processing: tiangolo/fastapi
    -> Dockerfile at: Dockerfile
[✓] Saved 1 examples to database

[*] Progress: 1/50000 repositories scraped
...
```

### 5.3 Run in Background (Optional)
```bash
# Run in background with logging
nohup python github_scraper.py > scraper.log 2>&1 &

# Get the process ID
echo $!

# Check logs
tail -f scraper.log

# Check if still running
ps aux | grep github_scraper
```

---

## Step 6: Monitor Progress

### Check Database
```bash
# Connect to database
psql -U harvester -d dockerfile_data -h localhost

# Check row count
SELECT COUNT(*) FROM dockerfile_repos;

# Check by language
SELECT language, COUNT(*) 
FROM dockerfile_repos 
GROUP BY language 
ORDER BY COUNT(*) DESC;

# Check most recent entries
SELECT repo_name, stars, language, scraped_at 
FROM dockerfile_repos 
ORDER BY scraped_at DESC 
LIMIT 10;

# Exit
\q
```

### Check API Rate Limits
```bash
# Check remaining API calls
curl -H "Authorization: token ghp_YOUR_TOKEN_HERE" \
     https://api.github.com/rate_limit
```

---

## Expected Timeline

| Time | Progress | Repos |
|------|----------|-------|
| 1 hour | 5% | ~2,500 |
| 3 hours | 15% | ~7,500 |
| 6 hours | 30% | ~15,000 |
| 12 hours | 60% | ~30,000 |
| 20 hours | 100% | 50,000+ |

**Total Time**: 18-24 hours for full dataset

---

## Troubleshooting

### ❌ "PostgreSQL is not running"
```bash
# Check status
sudo service postgresql status

# Start if stopped
sudo service postgresql start

# Check if port 5432 is in use
sudo lsof -i :5432
```

### ❌ "password authentication failed for user harvester"
```bash
# Reset password
sudo -u postgres psql -c "ALTER USER harvester WITH PASSWORD 'mysecurepassword';"

# Try connecting again
psql -U harvester -d dockerfile_data -h localhost
```

### ❌ "API rate limit exceeded"
```bash
# Check when it resets
curl -H "Authorization: token ghp_YOUR_TOKEN" https://api.github.com/rate_limit

# Wait for reset (shown in 'reset' field as Unix timestamp)
# Or reduce scraping speed in script
```

### ❌ "Connection refused on localhost:5432"
```bash
# Check PostgreSQL is listening
sudo netstat -plnt | grep 5432

# Edit postgresql.conf
sudo nano /etc/postgresql/*/main/postgresql.conf
# Set: listen_addresses = 'localhost'

# Restart
sudo service postgresql restart
```

### ❌ "Could not import module psycopg2"
```bash
# Reinstall with binary
pip install psycopg2-binary --force-reinstall
```

### ❌ Scraper crashes or stops
```bash
# Check logs if running in background
tail -f scraper.log

# Resume by just running again - it skips existing repos
python github_scraper.py
```

---

## Database Schema

The scraper creates this table automatically:

```sql
CREATE TABLE dockerfile_repos (
    id SERIAL PRIMARY KEY,
    repo_name TEXT UNIQUE,              -- e.g., "tiangolo/fastapi"
    description TEXT,                   -- Repository description
    stars INTEGER,                      -- GitHub stars count
    language TEXT,                      -- Primary programming language
    topics TEXT[],                      -- GitHub topics/tags
    dockerfile_path TEXT,               -- Path to Dockerfile in repo
    dockerfile TEXT,                    -- Full Dockerfile content
    readme_excerpt TEXT,                -- First 500 chars of README
    has_requirements BOOLEAN,           -- Has dependency file
    requirements TEXT,                  -- requirements.txt content
    package_json TEXT,                  -- package.json content
    scraped_at TIMESTAMP,              -- When data was collected
    url TEXT                           -- GitHub repository URL
);
```

---

## Data Quality Filters

The scraper only collects repositories that meet these criteria:

- ✅ Minimum 10 GitHub stars
- ✅ Contains valid Dockerfile
- ✅ Has description or README
- ✅ Successfully fetched via GitHub API

---

## Next Steps

After scraping completes:

1. **Verify data quality**:
   ```bash
   cd ../2-dataset
   python analyze_dataset.py
   ```

2. **Generate training data**:
   ```bash
   python generate_training_data.py
   ```

3. **Proceed to Phase 2**: Dataset preparation

---

## Useful Commands

```bash
# Stop scraper (if running in foreground)
Ctrl+C

# Stop scraper (if running in background)
ps aux | grep github_scraper
kill <PID>

# Backup database
pg_dump -U harvester dockerfile_data > backup.sql

# Restore database
psql -U harvester dockerfile_data < backup.sql

# Clear database (start fresh)
psql -U harvester -d dockerfile_data -c "TRUNCATE TABLE dockerfile_repos;"

# Export to CSV
psql -U harvester -d dockerfile_data -c "COPY dockerfile_repos TO '/tmp/dockerfiles.csv' CSV HEADER;"
```

---

## Configuration Reference

### Default Settings
- **Target repos**: 50,000
- **Minimum stars**: 10
- **Languages**: Python, JavaScript, TypeScript, Go, Java, Rust, Ruby, PHP, C++
- **Rate limit respect**: Yes (automatic delays)
- **Retry on failure**: Yes (with exponential backoff)

### Customization
Edit `github_scraper.py` and modify these variables:
```python
MIN_STARS = 10              # Minimum GitHub stars
TARGET_REPOS = 50000        # Total repositories to scrape
MAX_PAGES_PER_LANGUAGE = 10 # Pages per language (100 repos/page)
```

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify PostgreSQL is running: `sudo service postgresql status`
3. Test GitHub token: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`
4. Check database connection: `psql -U harvester -d dockerfile_data -h localhost`
5. Review scraper logs: `tail -f scraper.log`

---

**Current Phase**: Phase 1 - Data Collection  
**Next Phase**: Phase 2 - Dataset Preparation  
**Expected Duration**: 18-24 hours for complete scraping