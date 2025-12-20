# DockerForge Project Structure

## 📁 Directory Layout

```
dockerforge/
├── README.md                          # Main project documentation
├── GUIDE.md                           # This file - complete workflow guide
├── .gitignore                         # Git ignore patterns
├── requirements.txt                   # Python dependencies
│
├── 1-scraping/                        # Phase 1: Data Collection
│   ├── github_scraper.py              # Main scraper script
│   ├── config.py                      # Configuration (DB, API tokens)
│   ├── database_setup.sql             # PostgreSQL schema
│   └── README.md                      # Scraping instructions
│
├── 2-dataset/                         # Phase 2: Dataset Preparation
│   ├── generate_training_data.py      # Convert DB → training JSONL
│   ├── analyze_dataset.py             # Dataset statistics
│   ├── validate_dockerfiles.py        # Quality checks
│   └── README.md                      # Dataset documentation
│
├── 3-training/                        # Phase 3: Model Training
│   ├── train.py                       # Main training script
│   ├── config.yml                     # Training hyperparameters
│   ├── test_model.py                  # Model testing
│   └── README.md                      # Training guide
│
├── 4-deployment/                      # Phase 4: Deployment
│   ├── cli.py                         # Command-line interface
│   ├── api.py                         # REST API (FastAPI)
│   ├── push_to_hf.py                  # Upload to HuggingFace
│   └── README.md                      # Deployment docs
│
├── data/                              # Data storage (gitignored)
│   ├── raw/                           # Raw scraped data
│   ├── processed/                     # Training data
│   └── checkpoints/                   # Model checkpoints
│
└── tests/                             # Test files
    ├── test_scraper.py
    ├── test_generator.py
    └── sample_dockerfiles/
```

---

## 🎯 Project Goal

**Build an AI model that generates production-ready Dockerfiles from natural language descriptions.**

**Input**: "Create a Dockerfile for a FastAPI app with PostgreSQL and Redis"  
**Output**: Complete, optimized Dockerfile with multi-stage build

---

## 📋 Complete Workflow

### Phase 1: Data Collection (Current Phase) 🔄

**Goal**: Scrape 50,000 Dockerfiles from GitHub with context

**Steps**:
1. Set up PostgreSQL database
2. Get GitHub Personal Access Token
3. Run `github_scraper.py`
4. Wait 10-12 hours for completion
5. Verify data quality

**Location**: `1-scraping/`

**Status**: Ready to start

---

### Phase 2: Dataset Preparation (Next)

**Goal**: Convert raw GitHub data into training format

**Steps**:
1. Extract Dockerfiles + context from database
2. Clean and validate Dockerfiles
3. Create prompt/completion pairs
4. Generate `train.jsonl` and `val.jsonl`
5. Analyze dataset statistics

**Location**: `2-dataset/`

**Expected Output**: 
- `train.jsonl` (~45K examples)
- `val.jsonl` (~5K examples)

---

### Phase 3: Model Training

**Goal**: Fine-tune LLM on Dockerfile generation

**Base Model**: DeepSeek-Coder-6.7B (or similar code model)

**Steps**:
1. Load training data
2. Configure LoRA fine-tuning
3. Train for 3 epochs (~8-10 hours on L40S)
4. Evaluate on validation set
5. Save best checkpoint

**Location**: `3-training/`

---

### Phase 4: Deployment

**Goal**: Make the model usable

**Deliverables**:
- CLI tool: `dockerforge generate "description"`
- REST API for integrations
- HuggingFace model hosting
- Documentation

**Location**: `4-deployment/`

---

## 🗄️ Database Schema

```sql
CREATE TABLE dockerfile_repos (
    id SERIAL PRIMARY KEY,
    repo_name TEXT UNIQUE,              -- e.g., "tiangolo/fastapi"
    description TEXT,                   -- Repo description
    stars INTEGER,                      -- GitHub stars
    language TEXT,                      -- Primary language
    topics TEXT[],                      -- GitHub topics/tags
    dockerfile_path TEXT,               -- Path to Dockerfile in repo
    dockerfile TEXT,                    -- Full Dockerfile content
    readme_excerpt TEXT,                -- First 500 chars of README
    has_requirements BOOLEAN,           -- Has requirements.txt/package.json
    requirements TEXT,                  -- requirements.txt content
    package_json TEXT,                  -- package.json content
    scraped_at TIMESTAMP,              -- When scraped
    url TEXT                           -- GitHub URL
);
```

**Current Count**: 0 repos (starting fresh)  
**Target**: 50,000+ repos

---

## 📊 Dataset Statistics (To Be Collected)

### Target Distribution:
- Python: 15,000 examples
- JavaScript/TypeScript: 12,000 examples
- Go: 8,000 examples
- Java: 5,000 examples
- Rust: 3,000 examples
- Other: 7,000 examples

### Quality Filters:
- Minimum 10 stars per repo
- Valid Dockerfile syntax
- Has README or description
- Recently updated (< 2 years)

---

## 🔧 Configuration Files

### `config.py` (Create this in 1-scraping/)
```python
# GitHub API
GITHUB_TOKEN = "ghp_your_token_here"  # Get from https://github.com/settings/tokens

# Database
DB_HOST = "localhost"
DB_NAME = "dockerfile_data"
DB_USER = "harvester"
DB_PASSWORD = "mysecurepassword"
DB_PORT = 5432

# Scraping settings
MIN_STARS = 10
LANGUAGES = ["Python", "JavaScript", "TypeScript", "Go", "Java", "Rust", "Ruby", "PHP"]
TARGET_REPOS = 50000
MAX_PAGES_PER_LANGUAGE = 10
```

### `.env` (Create this, add to .gitignore)
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
DB_PASSWORD=mysecurepassword
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
```

---

## 🚀 Quick Start Commands

### Setup (One-time)
```bash
# Clone repo
git clone https://github.com/keypa/dockerforge.git
cd dockerforge

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb dockerfile_data
psql dockerfile_data < 1-scraping/database_setup.sql

# Configure
cp 1-scraping/config.py.example 1-scraping/config.py
# Edit config.py with your tokens
```

### Run Scraper
```bash
cd 1-scraping
python github_scraper.py
# Wait 10-12 hours
```

### Generate Training Data
```bash
cd 2-dataset
python generate_training_data.py
# Creates train.jsonl and val.jsonl
```

### Train Model
```bash
cd 3-training
python train.py
# Wait 8-10 hours on GPU
```

### Test Model
```bash
cd 3-training
python test_model.py
# Try generating Dockerfiles
```

---

## 📈 Progress Tracking

### Phase 1: Scraping ⏳
- [ ] Database setup
- [ ] GitHub token obtained
- [ ] Scraper running
- [ ] 10,000 repos collected
- [ ] 25,000 repos collected
- [ ] 50,000 repos collected
- [ ] Data validation complete

### Phase 2: Dataset ⏹️
- [ ] Training data generated
- [ ] Validation split created
- [ ] Quality checks passed
- [ ] Dataset statistics analyzed

### Phase 3: Training ⏹️
- [ ] Training started
- [ ] Epoch 1 complete
- [ ] Epoch 2 complete
- [ ] Epoch 3 complete
- [ ] Best model saved

### Phase 4: Deployment ⏹️
- [ ] CLI tool working
- [ ] API deployed
- [ ] Model on HuggingFace
- [ ] Documentation complete

---

## 💡 Key Decisions Made

1. **Dataset Source**: GitHub (real-world examples)
2. **Target Size**: 50,000 Dockerfiles
3. **Base Model**: DeepSeek-Coder-6.7B
4. **Training Method**: LoRA fine-tuning
5. **Storage**: PostgreSQL for structured data
6. **Languages**: Multi-language support (Python, JS, Go, etc.)

---

## 🔄 If Switching Machines

1. **Clone repo**: `git clone https://github.com/keypa/dockerforge.git`
2. **Install deps**: `pip install -r requirements.txt`
3. **Copy `.env`** with your tokens
4. **Database**: 
   - If continuing scraping: Connect to same DB
   - If starting fresh: Create new DB
5. **Resume**: Check this GUIDE.md for current phase

---

## 📝 Important Notes

- **GitHub Token**: Required, get from https://github.com/settings/tokens (public_repo scope)
- **Rate Limits**: 5,000 API calls/hour with token
- **Database**: PostgreSQL required (or adapt to SQLite)
- **GPU**: Training requires GPU (L40S, A100, or similar)
- **Time**: Full pipeline takes ~24-30 hours total
- **Storage**: ~10GB for dataset, ~15GB for model

---

## 🆘 Troubleshooting

### Scraper Issues
- **Rate Limited**: Wait 1 hour, token resets
- **No Dockerfiles Found**: Check search query
- **Database Connection**: Verify PostgreSQL running

### Training Issues  
- **Out of Memory**: Reduce batch size
- **Slow Training**: Check GPU utilization
- **Poor Quality**: Need more/better data

---

## 📚 Resources

- GitHub API Docs: https://docs.github.com/en/rest
- HuggingFace Transformers: https://huggingface.co/docs/transformers
- LoRA Paper: https://arxiv.org/abs/2106.09685
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/

---

**Last Updated**: December 2024  
**Current Phase**: Phase 1 - Data Collection  
**Status**: Ready to start scraping
