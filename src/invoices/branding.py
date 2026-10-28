"""Profils de marque pour l'impression des documents (facture, proforma, bon de livraison).

Les valeurs sont modifiables dans Paramètres (modèle ``parametres.CompanyProfile``). Le
dictionnaire ``BRANDS`` ci-dessous n'est qu'un repli utilisé si la base ne contient pas
la ligne demandée. L'utilisateur choisit la marque au moment de l'impression via le
paramètre GET ``?marque=ctams|cta``.
"""

from django.templatetags.static import static

from parametres.models import CompanyProfile

BRANDS = {
    'ctams': {
        'key': 'ctams',
        'logo': 'app/assets/img/ctams-logo.jpg',
        'name': 'CTAMS',
        'tag': 'Centre Technique Auto & Multiservices',
        'full_name': 'CENTRE TECHNIQUE AUTO & MULTISERVICES (CTAMS)',
        'address': "Angré Nouveau CHU, Abidjan – Côte d'Ivoire",
        'tel': '07 77 90 68 45 / 05 05 21 67 92',
        'email': 'Sasava221@gmail.com',
        'signataire': 'M. Savadogo Salif — Gérant CTAMS',
    },
    'cta': {
        'key': 'cta',
        'logo': 'app/assets/img/cta-logo.png',
        'name': 'CTA',
        'tag': 'Centre Technique Auto — Entretien & Réparation',
        'full_name': 'CENTRE TECHNIQUE AUTO (CTA)',
        'address': 'Riviera Bonoumin, Abidjan – non loin de la direction du marché public',
        'tel': '07 77 90 68 45 / 05 05 21 67 92',
        'email': 'centretechniqueauto@outlook.com',
        'signataire': 'M. Savadogo Salif — Gérant CTA',
    },
}

DEFAULT_BRAND = 'ctams'


def _fallback_brand(key):
    data = dict(BRANDS.get(key, BRANDS[DEFAULT_BRAND]))
    data.update(
        tel_fixe='', rccm='', ncc='', bank_name='', bank_account='', mobile_money='',
        logo_url=static(data['logo']),
    )
    return data


def get_brand(request):
    """Retourne le profil de marque demandé (défaut : CTAMS)."""
    key = (request.GET.get('marque') or DEFAULT_BRAND).lower()
    profile = (
        CompanyProfile.objects.filter(key=key).first()
        or CompanyProfile.objects.filter(key=DEFAULT_BRAND).first()
    )
    return profile.as_brand() if profile else _fallback_brand(key)
