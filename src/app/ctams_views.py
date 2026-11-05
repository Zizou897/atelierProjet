import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)


@login_required
def contact_message_list(request):
    """Show website contact messages from CTAMS through its private GET API."""
    messages = []
    api_error = ""

    if not settings.CTAMS_CONTACT_MESSAGES_API_URL or not settings.CTAMS_CONTACT_MESSAGES_API_KEY:
        api_error = "La connexion aux messages de contact CTAMS n’est pas configurée."
    else:
        api_request = Request(
            settings.CTAMS_CONTACT_MESSAGES_API_URL,
            headers={
                "Accept": "application/json",
                "X-API-Key": settings.CTAMS_CONTACT_MESSAGES_API_KEY,
            },
            method="GET",
        )
        try:
            with urlopen(api_request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
            results = payload.get("results") if isinstance(payload, dict) else None
            if not isinstance(results, list):
                raise ValueError("Invalid contact message response")
            for item in results:
                if not isinstance(item, dict):
                    continue
                created_at = parse_datetime(item.get("created_at", ""))
                messages.append({**item, "created_at_datetime": created_at})
        except HTTPError as exc:
            logger.warning("CTAMS contact API returned HTTP %s", exc.code)
            api_error = "Les messages de contact CTAMS sont temporairement indisponibles."
        except (URLError, TimeoutError, OSError, ValueError, UnicodeDecodeError) as exc:
            logger.warning("Could not retrieve CTAMS contact messages: %s", type(exc).__name__)
            api_error = "Impossible de joindre le site CTAMS pour le moment. Réessayez plus tard."

    return render(
        request,
        "contact_messages/list.html",
        {"contact_messages": messages, "api_error": api_error},
    )
