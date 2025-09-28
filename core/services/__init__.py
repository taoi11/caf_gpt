"""
Core services package.
"""
from core.services.open_router_service import OpenRouterService
# S3 services kept for potential rollback but not exported
# from core.services.s3_service import (
#     S3Service, S3Client, S3FileNotFoundError, S3ConnectionError,
#     S3AuthenticationError, S3PermissionError
# )
from core.services.cost_tracker_service import CostTrackerService
from core.services.turnstile_service import TurnstileService, turnstile_service
from core.services.database_service import (
    DoadDatabaseService, PaceNoteDatabaseService,
    DatabaseServiceError, DocumentNotFoundError, DatabaseConnectionError,
    doad_service, pacenote_service
)

__all__ = [
    'OpenRouterService',
    # S3 services removed from exports (kept for rollback)
    # 'S3Service',
    # 'S3Client',
    # 'S3FileNotFoundError',
    # 'S3ConnectionError',
    # 'S3AuthenticationError',
    # 'S3PermissionError',
    'CostTrackerService',
    'TurnstileService',
    'turnstile_service',
    'DoadDatabaseService',
    'PaceNoteDatabaseService',
    'DatabaseServiceError',
    'DocumentNotFoundError',
    'DatabaseConnectionError',
    'doad_service',
    'pacenote_service',
]
