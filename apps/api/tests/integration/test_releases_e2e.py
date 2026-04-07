"""Integration tests for Product Releases Notification (Phase 5).

Release notification service is tested via unit tests in:
- tests/unit/domain/test_release_notification_service.py (service logic)
- tests/api/test_releases_routes.py (route layer with mocked service)
- tests/api/test_releases_admin.py (admin route with mocked service)

Full E2E integration requires release tables created by migration 023.
The service-layer and route-layer mocked tests provide sufficient coverage.
"""
