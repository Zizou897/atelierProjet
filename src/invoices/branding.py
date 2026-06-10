"""Profils de marque pour l'impression des documents (facture, proforma, bon de livraison).

CTAMS et CTA partagent le même gérant (mêmes numéros de téléphone) mais ont un
logo, une dénomination et des coordonnées distincts. L'utilisateur choisit la
marque au moment de l'impression via le paramètre GET ``?marque=ctams|cta``.
"""

BRANDS = {
    'ctams': {
        'key': 'ctams',
        'logo': 'app/assets/img/ctams-logo.jpg',
        'name': 'CTAMS',
        'tag': 'Centre Technique Auto & Multi-Services',
        'full_name': 'CENTRE TECHNIQUE AUTO & MULTI-SERVICES (CTAMS)',
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


def get_brand(request):
    """Retourne le profil de marque demandé (défaut : CTAMS)."""
    key = (request.GET.get('marque') or DEFAULT_BRAND).lower()
    return BRANDS.get(key, BRANDS[DEFAULT_BRAND])
