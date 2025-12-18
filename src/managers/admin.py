"""
Manager Admin Configuration - Notification about registrations relocation.

IMPORTANT: All manager-related model admin registrations have been moved to
authentication/admin.py for centralized role-specific entity management:
    - Feedback admin (with mark_as_processed/mark_as_unprocessed actions)
    - SystemLog admin (with custom permissions)
    - SystemSettings admin (with value_preview display)

Manage these models through Django Admin:
    - Feedback: /admin/authentication/feedback/
    - SystemLog: /admin/authentication/systemlog/
    - SystemSettings: /admin/authentication/systemsettings/

For more information, see:
    - /src/authentication/admin.py
    - /src/authentication/decorators.py (role-based access control)
    - /src/managers/models.py (Feedback, SystemLog, SystemSettings models)

Author: Pyland Team
Date: 2025
"""
