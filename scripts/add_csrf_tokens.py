#!/usr/bin/env python3
"""
Script to automatically add CSRF tokens to all HTML templates
Run this script once to update all forms with CSRF protection
"""

import os
import re
from pathlib import Path

def add_csrf_to_form(content):
    """
    Add CSRF token to forms that don't have it already

    Matches: <form method="POST"...>
    Inserts: <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    """
    # Pattern to match opening form tags with POST method
    form_pattern = r'(<form[^>]*method=["\']POST["\'][^>]*>)'

    # CSRF token line to insert
    csrf_token = '\n            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>'

    # Check if CSRF token already exists
    if 'csrf_token' in content:
        return content, False

    # Find all POST forms and add CSRF token after opening tag
    if re.search(form_pattern, content, re.IGNORECASE):
        modified_content = re.sub(
            form_pattern,
            r'\1' + csrf_token,
            content,
            flags=re.IGNORECASE
        )
        return modified_content, True

    return content, False


def process_template_file(filepath):
    """Process a single template file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        modified_content, was_modified = add_csrf_to_form(content)

        if was_modified:
            # Create backup
            backup_path = str(filepath) + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Write modified content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            return True, f"✓ Modified (backup created: {backup_path})"
        else:
            return False, "○ Already has CSRF token or no POST forms"

    except Exception as e:
        return False, f"✗ Error: {str(e)}"


def main():
    """Main function to process all templates"""
    print("=" * 70)
    print("CSRF Token Auto-Updater for Flask Templates")
    print("=" * 70)
    print()

    templates_dir = Path('templates')

    if not templates_dir.exists():
        print("Error: 'templates' directory not found!")
        print("Please run this script from the project root directory.")
        return

    # Find all HTML files
    html_files = list(templates_dir.rglob('*.html'))

    print(f"Found {len(html_files)} HTML template files")
    print()

    modified_count = 0
    skipped_count = 0

    for html_file in sorted(html_files):
        was_modified, message = process_template_file(html_file)

        # Show relative path
        relative_path = html_file.relative_to(templates_dir)

        if was_modified:
            print(f"{message}")
            print(f"  File: templates/{relative_path}")
            modified_count += 1
        else:
            print(f"{message}")
            print(f"  File: templates/{relative_path}")
            skipped_count += 1
        print()

    print("=" * 70)
    print(f"Summary:")
    print(f"  Modified: {modified_count} files")
    print(f"  Skipped:  {skipped_count} files")
    print(f"  Total:    {len(html_files)} files")
    print()

    if modified_count > 0:
        print("✓ CSRF tokens added successfully!")
        print()
        print("Next steps:")
        print("1. Review the changes in your templates")
        print("2. Enable CSRF protection in app.py:")
        print("   Change: app.config['WTF_CSRF_ENABLED'] = False")
        print("   To:     app.config['WTF_CSRF_ENABLED'] = True")
        print("3. Restart your Flask application")
        print()
        print("Note: Backup files (.backup) have been created for all modified files")
        print("      You can restore them if needed.")
    else:
        print("No changes needed - all templates already have CSRF tokens!")

    print("=" * 70)


if __name__ == '__main__':
    main()
