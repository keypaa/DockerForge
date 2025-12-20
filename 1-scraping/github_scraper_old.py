import requests
import time
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
import psycopg2
from datetime import datetime

# Configuration
GITHUB_TOKEN = None  # Set this to your GitHub token
DB_DSN = "dbname=dockerfile_data user=harvester password=mysecurepassword host=localhost"

# GitHub API endpoints
GITHUB_API = "https://api.github.com"
SEARCH_REPOS = f"{GITHUB_API}/search/repositories"
SEARCH_CODE = f"{GITHUB_API}/search/code"

class GitHubDockerfileScraper:
    def __init__(self, github_token: str):
        self.token = github_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        })
        self.rate_limit_remaining = 5000
        self.search_rate_limit = 30
        
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
    
    def search_repos_with_dockerfile(self, language: str = None, min_stars: int = 10, 
                                     page: int = 1, per_page: int = 100) -> List[Dict]:
        """Search GitHub for repositories containing Dockerfiles"""
        
        # Build search query
        query_parts = ["filename:Dockerfile"]
        
        if language:
            query_parts.append(f"language:{language}")
        
        if min_stars:
            query_parts.append(f"stars:>={min_stars}")
        
        query = " ".join(query_parts)
        
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = self.session.get(SEARCH_REPOS, params=params)
            
            if response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - time.time(), 0) + 5
                print(f"[!] Rate limited. Waiting {wait_time:.0f} seconds...")
                time.sleep(wait_time)
                return self.search_repos_with_dockerfile(language, min_stars, page, per_page)
            
            response.raise_for_status()
            data = response.json()
            
            print(f"[*] Found {data.get('total_count', 0)} repos (page {page})")
            return data.get('items', [])
            
        except Exception as e:
            print(f"[!] Error searching repos: {e}")
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
    
    def extract_repo_metadata(self, repo: Dict) -> Dict:
        """Extract relevant metadata from repository"""
        return {
            'repo_name': repo['full_name'],
            'description': repo.get('description', ''),
            'stars': repo.get('stargazers_count', 0),
            'language': repo.get('language', ''),
            'topics': repo.get('topics', []),
            'url': repo['html_url'],
            'created_at': repo.get('created_at', ''),
            'updated_at': repo.get('updated_at', ''),
            'size': repo.get('size', 0),
            'forks': repo.get('forks_count', 0),
        }
    
    def find_dockerfiles_in_repo(self, repo_full_name: str) -> List[str]:
        """Find all Dockerfiles in a repository"""
        url = f"{GITHUB_API}/search/code"
        params = {
            'q': f'filename:Dockerfile repo:{repo_full_name}',
            'per_page': 10
        }
        
        try:
            response = self.session.get(url, params=params)
            
            if response.status_code == 403:
                time.sleep(60)
                return self.find_dockerfiles_in_repo(repo_full_name)
            
            response.raise_for_status()
            data = response.json()
            
            dockerfile_paths = [item['path'] for item in data.get('items', [])]
            return dockerfile_paths
            
        except Exception as e:
            print(f"[!] Error finding Dockerfiles in {repo_full_name}: {e}")
            return ['Dockerfile']  # Default fallback
    
    def scrape_repo(self, repo: Dict) -> Optional[Dict]:
        """Scrape a single repository for Dockerfile and context"""
        
        repo_name = repo['full_name']
        print(f"\n[*] Processing: {repo_name}")
        
        metadata = self.extract_repo_metadata(repo)
        
        # Find all Dockerfiles
        dockerfile_paths = self.find_dockerfiles_in_repo(repo_name)
        time.sleep(2)  # Rate limit protection
        
        results = []
        
        for dockerfile_path in dockerfile_paths[:3]:  # Max 3 Dockerfiles per repo
            print(f"    -> Dockerfile at: {dockerfile_path}")
            
            # Get Dockerfile content
            dockerfile = self.get_file_content(repo_name, dockerfile_path)
            if not dockerfile:
                print(f"    [!] Could not fetch Dockerfile")
                continue
            
            # Get README
            readme = None
            for readme_name in ['README.md', 'README.MD', 'readme.md', 'Readme.md']:
                readme = self.get_file_content(repo_name, readme_name)
                if readme:
                    break
            
            # Get requirements/dependencies
            requirements = None
            package_json = None
            
            if metadata['language'] == 'Python':
                requirements = self.get_file_content(repo_name, 'requirements.txt')
                if not requirements:
                    requirements = self.get_file_content(repo_name, 'pyproject.toml')
            
            elif metadata['language'] == 'JavaScript' or metadata['language'] == 'TypeScript':
                package_json = self.get_file_content(repo_name, 'package.json')
            
            # Extract README excerpt (first 500 chars)
            readme_excerpt = readme[:500] if readme else ""
            
            # Build training example
            example = {
                **metadata,
                'dockerfile_path': dockerfile_path,
                'dockerfile': dockerfile,
                'readme_excerpt': readme_excerpt,
                'has_readme': readme is not None,
                'has_requirements': requirements is not None or package_json is not None,
                'requirements': requirements,
                'package_json': package_json,
                'scraped_at': datetime.utcnow().isoformat(),
            }
            
            results.append(example)
            time.sleep(1)  # Be nice to GitHub
        
        return results if results else None
    
    def save_to_db(self, examples: List[Dict]):
        """Save examples to PostgreSQL database"""
        conn = psycopg2.connect(DB_DSN)
        cur = conn.cursor()
        
        try:
            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dockerfile_repos (
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
            
            for example in examples:
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
            print(f"[✓] Saved {len(examples)} examples to database")
            
        except Exception as e:
            conn.rollback()
            print(f"[!] Database error: {e}")
        finally:
            cur.close()
            conn.close()


def main():
    """Main scraping workflow"""
    
    # Get GitHub token
    github_token = input("Enter your GitHub Personal Access Token: ").strip()
    
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
        None  # Any language
    ]
    
    total_scraped = 0
    target = 50000
    
    print(f"[*] Target: {target} repositories with Dockerfiles")
    print(f"[*] Starting scrape...")
    print()
    
    for language in languages:
        lang_name = language or "All"
        print(f"\n{'='*60}")
        print(f"Scraping {lang_name} repositories")
        print(f"{'='*60}\n")
        
        page = 1
        max_pages = 10  # 1000 repos per language
        
        while page <= max_pages and total_scraped < target:
            print(f"\n[*] Page {page}/{max_pages} for {lang_name}")
            
            # Search for repos
            repos = scraper.search_repos_with_dockerfile(
                language=language,
                min_stars=10,
                page=page,
                per_page=100
            )
            
            if not repos:
                print(f"[*] No more repos found for {lang_name}")
                break
            
            # Scrape each repo
            batch = []
            for repo in repos:
                results = scraper.scrape_repo(repo)
                if results:
                    batch.extend(results)
                    total_scraped += len(results)
                
                if total_scraped >= target:
                    break
                
                time.sleep(2)  # Rate limit protection
            
            # Save batch to database
            if batch:
                scraper.save_to_db(batch)
            
            print(f"\n[*] Progress: {total_scraped}/{target} repositories scraped")
            
            page += 1
            time.sleep(5)  # Pause between pages
    
    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total repositories scraped: {total_scraped}")
    print(f"Data saved to PostgreSQL database")


if __name__ == "__main__":
    main()
