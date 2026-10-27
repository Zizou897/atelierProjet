from django.db import migrations

COMPANIES = [
    {
        'key': 'ctams',
        'name': 'CTAMS',
        'tag': 'Centre Technique Auto & Multiservices',
        'full_name': 'CENTRE TECHNIQUE AUTO & MULTISERVICES (CTAMS)',
        'address': "Angré Nouveau CHU, Abidjan – Côte d'Ivoire",
        'tel': '07 77 90 68 45 / 05 05 21 67 92',
        'email': 'Sasava221@gmail.com',
        'signataire': 'M. Savadogo Salif — Gérant CTAMS',
    },
    {
        'key': 'cta',
        'name': 'CTA',
        'tag': 'Centre Technique Auto — Entretien & Réparation',
        'full_name': 'CENTRE TECHNIQUE AUTO (CTA)',
        'address': 'Riviera Bonoumin, Abidjan – non loin de la direction du marché public',
        'tel': '07 77 90 68 45 / 05 05 21 67 92',
        'email': 'centretechniqueauto@outlook.com',
        'signataire': 'M. Savadogo Salif — Gérant CTA',
    },
]


def seed(apps, schema_editor):
    CompanyProfile = apps.get_model('parametres', 'CompanyProfile')
    DocumentDefaults = apps.get_model('parametres', 'DocumentDefaults')
    for data in COMPANIES:
        CompanyProfile.objects.get_or_create(key=data['key'], defaults=data)
    DocumentDefaults.objects.get_or_create(pk=1)


class Migration(migrations.Migration):

    dependencies = [
        ('parametres', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
