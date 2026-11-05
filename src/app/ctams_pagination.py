from datetime import timezone as datetime_timezone

from django.core.paginator import Paginator
from django.utils import timezone


PAGE_SIZE = 20


def paginate_newest_first(items, page_number):
    """Order CTAMS API items newest-first, then return a safe local page."""
    def sort_key(item):
        created_at = item.get("created_at_datetime")
        if created_at is None:
            created_timestamp = float("-inf")
        else:
            if timezone.is_naive(created_at):
                created_at = timezone.make_aware(created_at, datetime_timezone.utc)
            created_timestamp = created_at.timestamp()
        try:
            item_id = int(item.get("id") or 0)
        except (TypeError, ValueError):
            item_id = 0
        return created_timestamp, item_id

    ordered_items = sorted(items, key=sort_key, reverse=True)
    return Paginator(ordered_items, PAGE_SIZE).get_page(page_number)
