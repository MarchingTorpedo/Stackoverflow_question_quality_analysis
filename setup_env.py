#!/usr/bin/env python3
"""
Setup script to configure environment variables and security settings.
Run this script once to set up your development environment.
"""
import os
import secrets
import shutil
from pathlib import Path

def generate_secure_token(length=32):
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)

def setup_environment():
    """Set up the development environment."""
    # Create .env from example if it doesn't exist
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("Created .env file from .env.example")
    
    # Generate secure Jupyter token
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    with open(env_file, 'w') as f:
        for line in lines:
            if 'JUPYTER_TOKEN=' in line:
                line = f'JUPYTER_TOKEN={generate_secure_token()}\n'
            f.write(line)
    
    print("Generated secure Jupyter token")

def create_secrets_readme():
    """Create a README for secrets management."""
    readme_content = """# Security and Secrets Management

This project uses environment variables for configuration. Never commit the `.env` file to version control.

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Run the setup script:
   ```bash
   python setup_env.py
   ```

3. Update the values in `.env` with your actual configuration.

## GitHub Actions Secrets

The following secrets should be set in your GitHub repository:
- `GITGUARDIAN_API_KEY`: For automated security scanning
- Any API keys or tokens needed for deployment

## Best Practices

1. Never commit secrets or API keys to version control
2. Use environment variables for configuration
3. Rotate secrets regularly
4. Use GitHub's secret scanning feature
5. Run security scans before merging PRs
"""
    
    with open('SECURITY.md', 'w') as f:
        f.write(readme_content)
    print("Created SECURITY.md")

if __name__ == '__main__':
    setup_environment()
    create_secrets_readme()
    print("\nSetup complete! Please update your .env file with your actual configuration.")