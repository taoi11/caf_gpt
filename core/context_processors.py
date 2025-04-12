import logging
from .services import CostTrackerService

logger = logging.getLogger(__name__)

cost_tracker_service = CostTrackerService()


def cost_context(request):
    """
    Adds the current total API usage cost to the template context.
    """
    total_cost = 0.0
    try:
        total_cost = cost_tracker_service.get_total_usage()
    except Exception as e:
        logger.error(f"Failed to get total usage for context processor: {e}", exc_info=True)

    return {'current_total_usage_cost': total_cost}
