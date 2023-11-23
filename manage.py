#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django.core.management.commands.runserver as runserver


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exchange_account_api.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    runserver.Command.default_port = os.getenv('PORT')
    runserver.Command.default_addr = '0.0.0.0'
    main()
