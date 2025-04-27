#!/usr/bin/env python
import os
import sys
from pathlib import Path

def main():
    # AÑADE ESTO PRIMERO (antes de cualquier import de Django)
    BASE_DIR = Path(__file__).parent
    sys.path.append(str(BASE_DIR))
    sys.path.append(str(BASE_DIR / 'apps'))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'condomanager.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(...) from exc
        
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()