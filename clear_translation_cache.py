#!/usr/bin/env python3
"""
Script to clear the entire translation cache.
"""

import os
import shutil
import sys
import yaml
import locale


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


def clear_cache(cache_dir):
    """Clear the entire translation cache directory."""
    if not os.path.exists(cache_dir):
        print(f"Cache directory {cache_dir} does not exist.")
        return 0

    try:
        # Count files before deletion
        file_count = 0
        for root, dirs, files in os.walk(cache_dir):
            file_count += len([f for f in files if f.endswith('.pkl')])

        if file_count == 0:
            print("No cache files found.")
            return 0

        # Remove the entire cache directory
        shutil.rmtree(cache_dir)
        print(f"Successfully cleared {file_count} cached translations from {cache_dir}")
        return file_count

    except OSError as e:
        print(f"Error clearing cache: {e}")
        return -1


def main():
    """Main function."""
    print("Translation Cache Cleaner")
    print("=" * 25)

    # Load configuration
    config = load_config()
    if config is None:
        sys.exit(1)

    cache_dir = get_cache_dir(config)
    print(f"Cache directory: {cache_dir}")

    # Ask for confirmation
    try:
        response = input("Are you sure you want to clear the entire cache? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)

    # Clear the cache
    result = clear_cache(cache_dir)
    if result >= 0:
        print("Cache clearing completed successfully.")
    else:
        print("Cache clearing failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()