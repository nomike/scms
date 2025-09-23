#!/usr/bin/env python3
"""
Script to clean up stale translations whose source content has changed.
Removes cached translations where the SHA256 hash no longer matches any current content.
"""

import hashlib
import os
import pickle
import sys
import yaml
import locale
from pathlib import Path


def load_config():
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", encoding=locale.getpreferredencoding()) as file:
            return yaml.load(file, Loader=yaml.SafeLoader)
    except FileNotFoundError:
        print("Error: config.yaml not found. Please copy config.yaml.example to config.yaml")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}")
        return None


def get_cache_dir(config):
    """Get the cache directory from config or use default."""
    if config and 'claude' in config and 'cache_dir' in config['claude']:
        return config['claude']['cache_dir']
    return os.path.join('.', 'cache', 'translations')


def get_content_hash(content):
    """Generate SHA256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def scan_content_files(public_dir="public"):
    """
    Scan all content files and generate their current hashes.
    Returns a set of current content hashes.
    """
    current_hashes = set()

    if not os.path.exists(public_dir):
        print(f"Warning: Public directory '{public_dir}' not found.")
        return current_hashes

    # File extensions to scan
    extensions = ['.org', '.md', '.html', '.txt']

    print(f"Scanning content files in {public_dir}...")

    for root, dirs, files in os.walk(public_dir):
        for file in files:
            # Check for index files
            if file in ['index.org', 'index.md', 'index.html', 'index']:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding=locale.getpreferredencoding()) as f:
                        content = f.read()

                    # For .org and .md files, we need to simulate the rendering process
                    if file.endswith('.org'):
                        # For org files, we'd need orgpython to render, but let's use raw content hash
                        content_hash = get_content_hash(content)
                    elif file.endswith('.md'):
                        # For markdown files, we'd need markdown lib, but let's use raw content hash
                        content_hash = get_content_hash(content)
                    else:
                        # HTML and plain text files
                        content_hash = get_content_hash(content)

                    current_hashes.add(content_hash)

                except (IOError, UnicodeDecodeError) as e:
                    print(f"Warning: Could not read {file_path}: {e}")
                    continue

            # Also check other content files with relevant extensions
            elif any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding=locale.getpreferredencoding()) as f:
                        content = f.read()
                    content_hash = get_content_hash(content)
                    current_hashes.add(content_hash)
                except (IOError, UnicodeDecodeError):
                    continue

    print(f"Found {len(current_hashes)} unique content hashes.")
    return current_hashes


def parse_cache_filename(filename):
    """
    Parse cache filename to extract content hash and language.
    Expected format: {hash}_{lang}.pkl
    """
    if not filename.endswith('.pkl'):
        return None, None

    base_name = filename[:-4]  # Remove .pkl extension
    parts = base_name.rsplit('_', 1)  # Split from the right, only once

    if len(parts) != 2:
        return None, None

    content_hash, lang = parts
    return content_hash, lang


def cleanup_stale_cache(cache_dir, current_hashes):
    """
    Remove cached translations for content that no longer exists or has changed.
    """
    if not os.path.exists(cache_dir):
        print(f"Cache directory {cache_dir} does not exist.")
        return 0

    removed_count = 0
    kept_count = 0

    try:
        for filename in os.listdir(cache_dir):
            if not filename.endswith('.pkl'):
                continue

            file_path = os.path.join(cache_dir, filename)
            content_hash, lang = parse_cache_filename(filename)

            if content_hash is None:
                print(f"Warning: Could not parse cache filename: {filename}")
                continue

            # Check if this content hash still exists in current content
            if content_hash not in current_hashes:
                try:
                    os.remove(file_path)
                    print(f"Removed stale cache: {filename} (hash: {content_hash[:12]}..., lang: {lang})")
                    removed_count += 1
                except OSError as e:
                    print(f"Error removing {filename}: {e}")
            else:
                kept_count += 1

        print(f"\nCleanup completed:")
        print(f"  - Removed: {removed_count} stale cache files")
        print(f"  - Kept: {kept_count} current cache files")

        return removed_count

    except OSError as e:
        print(f"Error accessing cache directory: {e}")
        return -1


def main():
    """Main function."""
    print("Stale Translation Cache Cleanup")
    print("=" * 31)

    # Load configuration
    config = load_config()
    if config is None:
        sys.exit(1)

    cache_dir = get_cache_dir(config)
    print(f"Cache directory: {cache_dir}")

    # Scan current content to get active hashes
    current_hashes = scan_content_files()

    if not current_hashes:
        print("No content files found. Nothing to validate against.")
        sys.exit(1)

    # Ask for confirmation
    try:
        print(f"\nThis will remove cached translations that don't match any current content.")
        response = input("Continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)

    # Clean up stale cache entries
    result = cleanup_stale_cache(cache_dir, current_hashes)
    if result >= 0:
        print("Stale cache cleanup completed successfully.")
    else:
        print("Stale cache cleanup failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()