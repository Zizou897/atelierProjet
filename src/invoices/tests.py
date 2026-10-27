from django.test import RequestFactory, TestCase

from parametres.models import CompanyProfile

from .branding import get_brand


class GetBrandTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_reads_values_from_database(self):
        CompanyProfile.objects.filter(key='cta').update(
            tel='01 02 03', rccm='CI-ABJ-2020-B-1', ncc='1234567 A',
        )
        brand = get_brand(self.factory.get('/', {'marque': 'cta'}))
        self.assertEqual(brand['key'], 'cta')
        self.assertEqual(brand['tel'], '01 02 03')
        self.assertEqual(brand['rccm'], 'CI-ABJ-2020-B-1')
        self.assertEqual(brand['ncc'], '1234567 A')

    def test_unknown_or_missing_key_returns_ctams(self):
        self.assertEqual(get_brand(self.factory.get('/'))['key'], 'ctams')
        self.assertEqual(get_brand(self.factory.get('/', {'marque': 'zzz'}))['key'], 'ctams')

    def test_empty_database_falls_back_to_hardcoded_values(self):
        CompanyProfile.objects.all().delete()
        brand = get_brand(self.factory.get('/', {'marque': 'cta'}))
        self.assertEqual(brand['key'], 'cta')
        self.assertEqual(brand['email'], 'centretechniqueauto@outlook.com')
        self.assertEqual(brand['rccm'], '')
        self.assertTrue(brand['logo_url'].endswith('app/assets/img/cta-logo.png'))
