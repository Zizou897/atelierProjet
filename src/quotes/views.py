import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.dateparse import parse_datetime

from app.ctams_pagination import paginate_newest_first

logger = logging.getLogger(__name__)


@login_required
def submitted_quote_list(request):
    """Display submitted CTAMS quote requests using the private read-only API."""
    quotes = []
    api_error = ""

    if not settings.CTAMS_QUOTES_API_URL or not settings.CTAMS_QUOTES_API_KEY:
        api_error = "La connexion aux demandes de devis CTAMS n’est pas configurée."
    else:
        api_request = Request(
            settings.CTAMS_QUOTES_API_URL,
            headers={
                "Accept": "application/json",
                "X-API-Key": settings.CTAMS_QUOTES_API_KEY,
            },
            method="GET",
        )
        try:
            with urlopen(api_request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
            results = payload.get("results") if isinstance(payload, dict) else None
            if not isinstance(results, list):
                raise ValueError("Invalid quote request response")
            for item in results:
                if not isinstance(item, dict):
                    continue
                created_at = parse_datetime(item.get("created_at", ""))
                quotes.append({**item, "created_at_datetime": created_at})
        except HTTPError as exc:
            logger.warning("CTAMS quote API returned HTTP %s", exc.code)
            api_error = "Les demandes de devis CTAMS sont temporairement indisponibles."
        except (URLError, TimeoutError, OSError, ValueError, UnicodeDecodeError) as exc:
            logger.warning("Could not retrieve CTAMS quote requests: %s", type(exc).__name__)
            api_error = "Impossible de joindre le site CTAMS pour le moment. Réessayez plus tard."

    page_obj = paginate_newest_first(quotes, request.GET.get("page", 1))
    return render(
        request,
        "quotes/submitted_list.html",
        {"quotes": page_obj.object_list, "page_obj": page_obj, "api_error": api_error},
    )
