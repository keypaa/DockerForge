import requests
import time
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
import psycopg2
from datetime import datetime
import os

def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load environment variables
load_env()

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Load from .env or environment
DB_DSN = "dbname=dockerfile_data user=harvester password=mysecurepassword host=localhost"

# GitHub API endpoints
GITHUB_API = "https://api.github.com"

class GitHubDockerfileScraper:
    def __init__(self, github_token: str):
        self.token = github_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        })
        
    def check_rate_limit(self):
        """Check GitHub API rate limit"""
        response = self.session.get(f"{GITHUB_API}/rate_limit")
        data = response.json()
        core_limit = data['resources']['core']
        search_limit = data['resources']['search']
        
        print(f"[*] Rate Limits:")
        print(f"    Core API: {core_limit['remaining']}/{core_limit['limit']}")
        print(f"    Search API: {search_limit['remaining']}/{search_limit['limit']}")
        
        return core_limit['remaining'], search_limit['remaining']
    
    def search_code_for_dockerfiles(self, language: str = None, min_size: int = 100,
                                     page: int = 1, per_page: int = 100) -> List[Dict]:
        """Search GitHub CODE for Dockerfiles (not repos)"""
        
        # Build search query - search for CODE not REPOS
        query_parts = ["filename:Dockerfile"]
        
        if language:
            query_parts.append(f"language:{language}")
        
        # Add size filter to avoid empty files
        query_parts.append(f"size:>={min_size}")
        
        query = " ".join(query_parts)
        
        params = {
            'q': query,
            'sort': 'indexed',  # Recently indexed files
            'order': 'desc',
            'per_page': min(per_page, 100),  # Max 100 for code search
            'page': page
        }
        
        url = f"{GITHUB_API}/search/code"
        
        try:
            response = self.session.get(url, params=params)
            
            # Rate limit handling
            if response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - time.time(), 0) + 5
                print(f"[!] Rate limited. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
                return self.search_code_for_dockerfiles(language, min_size, page, per_page)
            
            # Check for 422 (validation failed)
            if response.status_code == 422:
                print(f"[!] Query validation failed: {query}")
                return []
            
            response.raise_for_status()
            data = response.json()
            
            total = data.get('total_count', 0)
            items = data.get('items', [])
            
            print(f"[*] Found {total} Dockerfiles (returning {len(items)} on page {page})")
            
            return items
            
        except Exception as e:
            print(f"[!] Error searching code: {e}")
            return []
    
    def get_file_content(self, repo_full_name: str, file_path: str) -> Optional[str]:
        """Fetch file content from a repository"""
        url = f"{GITHUB_API}/repos/{repo_full_name}/contents/{file_path}"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 404:
                return None
            
            if response.status_code == 403:
                time.sleep(60)
                return self.get_file_content(repo_full_name, file_path)
            
            response.raise_for_status()
            data = response.json()
            
            # Decode base64 content
            if 'content' in data:
                content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
                return content
            
            return None
            
        except Exception as e:
            print(f"[!] Error fetching {file_path}: {e}")
            return None
    
    def get_repo_info(self, repo_full_name: str) -> Optional[Dict]:
        """Get repository metadata"""
        url = f"{GITHUB_API}/repos/{repo_full_name}"
        
        try:
            response = self.session.get(url)
            
            if response.status_code == 404:
                return None
            
            if response.status_code == 403:
                time.sleep(60)
                return self.get_repo_info(repo_full_name)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"[!] Error fetching repo info: {e}")
            return None
    
    def scrape_dockerfile(self, code_item: Dict) -> Optional[Dict]:
        """Scrape a single Dockerfile and its context"""
        
        repo_full_name = code_item['repository']['full_name']
        dockerfile_path = code_item['path']
        
        print(f"\n[*] Processing: {repo_full_name}")
        print(f"    -> Dockerfile at: {dockerfile_path}")
        
        # Get repository info
        repo_info = self.get_repo_info(repo_full_name)
        if not repo_info:
            print(f"    [!] Could not fetch repo info")
            return None
        
        # Filter by stars
        stars = repo_info.get('stargazers_count', 0)
        if stars < 10:
            print(f"    [!] Too few stars ({stars}), skipping")
            return None
        
        # Get Dockerfile content
        dockerfile = self.get_file_content(repo_full_name, dockerfile_path)
        if not dockerfile or len(dockerfile) < 50:
            print(f"    [!] Dockerfile too short or empty")
            return None
        
        # Get README
        readme = None
        for readme_name in ['README.md', 'README.MD', 'readme.md', 'Readme.md']:
            readme = self.get_file_content(repo_full_name, readme_name)
            if readme:
                break
        
        # Get requirements/dependencies based on language
        language = repo_info.get('language', '')
        requirements = None
        package_json = None
        
        if language == 'Python':
            requirements = self.get_file_content(repo_full_name, 'requirements.txt')
            if not requirements:
                requirements = self.get_file_content(repo_full_name, 'pyproject.toml')
        
        elif language in ['JavaScript', 'TypeScript']:
            package_json = self.get_file_content(repo_full_name, 'package.json')
        
        # Extract README excerpt
        readme_excerpt = readme[:500] if readme else ""
        
        # Build result
        result = {
            'repo_name': repo_full_name,
            'description': repo_info.get('description', ''),
            'stars': stars,
            'language': language,
            'topics': repo_info.get('topics', []),
            'dockerfile_path': dockerfile_path,
            'dockerfile': dockerfile,
            'readme_excerpt': readme_excerpt,
            'has_readme': readme is not None,
            'has_requirements': requirements is not None or package_json is not None,
            'requirements': requirements,
            'package_json': package_json,
            'scraped_at': datetime.utcnow().isoformat(),
            'url': repo_info['html_url']
        }
        
        print(f"    [✓] Successfully scraped ({stars} stars, {len(dockerfile)} bytes)")
        
        return result
    
    def save_to_db(self, example: Dict):
        """Save a single example to PostgreSQL database"""
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        
        try:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'dockerfile_repos'
                )
            """)
            table_exists = cur.fetchone()[0]
            
            if not table_exists:
                try:
                    # Create table if not exists
                    cur.execute("""
                        CREATE TABLE dockerfile_repos (
                            id SERIAL PRIMARY KEY,
                            repo_name TEXT UNIQUE,
                            description TEXT,
                            stars INTEGER,
                            language TEXT,
                            topics TEXT[],
                            dockerfile_path TEXT,
                            dockerfile TEXT,
                            readme_excerpt TEXT,
                            has_requirements BOOLEAN,
                            requirements TEXT,
                            package_json TEXT,
                            scraped_at TIMESTAMP,
                            url TEXT
                        )
                    """)
                except Exception as e:
                    if "permission denied" in str(e).lower():
                        print("[!] Permission denied creating table. Please run as postgres:")
                        print("   GRANT CREATE ON SCHEMA public TO harvester;")
                        return
                    else:
                        raise
            
            cur.execute("""
                INSERT INTO dockerfile_repos 
                (repo_name, description, stars, language, topics, dockerfile_path,
                 dockerfile, readme_excerpt, has_requirements, requirements, 
                 package_json, scraped_at, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (repo_name) DO NOTHING
            """, (
                example['repo_name'],
                example['description'],
                example['stars'],
                example['language'],
                example['topics'],
                example['dockerfile_path'],
                example['dockerfile'],
                example['readme_excerpt'],
                example['has_requirements'],
                example.get('requirements'),
                example.get('package_json'),
                example['scraped_at'],
                example['url']
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"[!] Database error: {e}")
        finally:
            cur.close()
            conn.close()


def main():
    """Main scraping workflow"""
    
    # Get GitHub token
    github_token = GITHUB_TOKEN or input("Enter your GitHub Personal Access Token: ").strip()
    
    if not github_token:
        print("[!] GitHub token required. Get one at: https://github.com/settings/tokens")
        return
    
    scraper = GitHubDockerfileScraper(github_token)
    
    # Check rate limits
    scraper.check_rate_limit()
    print()
    
    # Define languages to scrape
    languages = [
        'Python',
        'JavaScript',
        'TypeScript', 
        'Go',
        'Java',
        'Ruby',
        'PHP',
        'Rust',
        'C++',
        'C#',
        'Shell',
        None  # Any language
    ]
    
    total_scraped = 0
    target = 10000  # Realistic target (GitHub code search limits to 1000 results per query)
    
    print(f"[*] Target: {target} repositories with Dockerfiles")
    print(f"[*] Starting scrape...")
    print()
    
    for language in languages:
        lang_name = language or "All"
        print(f"\n{'='*60}")
        print(f"Scraping {lang_name} repositories")
        print(f"{'='*60}\n")
        
        page = 1
        max_pages = 10  # GitHub limits to 1000 results (10 pages x 100)
        
        while page <= max_pages and total_scraped < target:
            print(f"\n[*] Page {page}/{max_pages} for {lang_name}")
            
            # Search for Dockerfiles in code
            code_items = scraper.search_code_for_dockerfiles(
                language=language,
                page=page,
                per_page=100
            )
            
            if not code_items:
                print(f"[*] No more Dockerfiles found for {lang_name}")
                break
            
            # Process each Dockerfile
            for code_item in code_items:
                result = scraper.scrape_dockerfile(code_item)
                
                if result:
                    scraper.save_to_db(result)
                    total_scraped += 1
                    print(f"[*] Progress: {total_scraped}/{target} repositories scraped")
                
                if total_scraped >= target:
                    break
                
                time.sleep(2)  # Be nice to GitHub API
            
            page += 1
            time.sleep(5)  # Longer pause between pages
            
            if total_scraped >= target:
                break
    
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total repositories scraped: {total_scraped}")
    print(f"Data saved to PostgreSQL database")


if __name__ == "__main__":
    main()