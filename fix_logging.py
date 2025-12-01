#!/usr/bin/env python3
"""
Fix logging f-strings to use lazy % formatting (SonarQube W1203)
Converts: logger.info(f"Message {var}")
To: logger.info("Message %s", var)
"""
import re
import sys
from pathlib import Path


def fix_logging_fstring(content: str) -> tuple[str, int]:
    """Fix f-string in logging statements"""
    fixes = 0

    # Pattern to match logger.METHOD(f"...")
    # This is a simple fix for basic cases
    pattern = r'(logger\.(info|error|warning|debug|critical))\(f"([^"]*?)"\)'

    def replacer(match):
        nonlocal fixes
        method = match.group(1)
        message = match.group(3)

        # Find all {var} placeholders
        placeholders = re.findall(r'\{([^}]+)\}', message)

        if not placeholders:
            # No placeholders, just remove f prefix
            fixes += 1
            return f'{method}("{message}")'

        # Replace {var} with %s
        new_message = message
        for placeholder in placeholders:
            new_message = new_message.replace(f'{{{placeholder}}}', '%s', 1)

        # Build the new logging call
        args = ', '.join(placeholders)
        fixes += 1
        return f'{method}("{new_message}", {args})'

    new_content = re.sub(pattern, replacer, content)
    return new_content, fixes


def process_file(filepath: Path):
    """Process a single Python file"""
    try:
        content = filepath.read_text(encoding='utf-8')
        new_content, fixes = fix_logging_fstring(content)

        if fixes > 0:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"✓ {filepath}: {fixes} fixes")
            return fixes
        return 0
    except Exception as e:
        print(f"✗ {filepath}: {e}", file=sys.stderr)
        return 0


def main():
    """Main function"""
    total_fixes = 0

    # Process all Python files in api/ and apps/
    for directory in ['api', 'apps']:
        path = Path(directory)
        if not path.exists():
            continue

        for py_file in path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            total_fixes += process_file(py_file)

    print(f"\n🎉 Total fixes: {total_fixes}")


if __name__ == '__main__':
    main()
