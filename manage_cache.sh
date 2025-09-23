#!/bin/bash
# Translation Cache Management Script

show_help() {
    echo "Translation Cache Management"
    echo "Usage: $0 [clear|cleanup|help]"
    echo ""
    echo "Commands:"
    echo "  clear   - Clear the entire translation cache"
    echo "  cleanup - Remove stale translations (source content changed)"
    echo "  help    - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 clear          # Clear all cached translations"
    echo "  $0 cleanup        # Remove outdated cache entries"
}

case "$1" in
    "clear")
        echo "Clearing entire translation cache..."
        python3 clear_translation_cache.py
        ;;
    "cleanup")
        echo "Cleaning up stale translations..."
        python3 cleanup_stale_translations.py
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        echo "Error: No command specified."
        echo ""
        show_help
        exit 1
        ;;
    *)
        echo "Error: Unknown command '$1'"
        echo ""
        show_help
        exit 1
        ;;
esac