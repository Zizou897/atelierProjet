from django.test import TestCase

from .models import CompanyProfile, DocumentDefaults


class SeedDataTests(TestCase):
    def test_both_companies_are_seeded_with_current_values(self):
        ctams = CompanyProfile.objects.get(key='ctams')
        self.assertEqual(ctams.name, 'CTAMS')
        self.assertEqual(ctams.full_name, 'CENTRE TECHNIQUE AUTO & MULTISERVICES (CTAMS)')
        self.assertEqual(ctams.email, 'Sasava221@gmail.com')
        self.assertEqual(ctams.tel, '07 77 90 68 45 / 05 05 21 67 92')

        cta = CompanyProfile.objects.get(key='cta')
        self.assertEqual(cta.full_name, 'CENTRE TECHNIQUE AUTO (CTA)')
        self.assertEqual(cta.email, 'centretechniqueauto@outlook.com')

    def test_document_defaults_are_seeded(self):
        defaults = DocumentDefaults.objects.get(pk=1)
        self.assertEqual(defaults.tva_taux, 18)
        self.assertIn('30 jours net', defaults.conditions_paiement)
        self.assertIn('1,5%', defaults.penalites_retard)

    def test_load_recreates_missing_row_and_is_stable(self):
        DocumentDefaults.objects.all().delete()
        first = DocumentDefaults.load()
        second = DocumentDefaults.load()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.tva_taux, 18)
        self.assertEqual(second.tva_taux, 18)
        self.assertEqual(DocumentDefaults.objects.count(), 1)

    def test_logo_url_falls_back_to_static_file(self):
        cta = CompanyProfile.objects.get(key='cta')
        self.assertTrue(cta.logo_url.endswith('app/assets/img/cta-logo.png'))
        ctams = CompanyProfile.objects.get(key='ctams')
        self.assertTrue(ctams.logo_url.endswith('app/assets/img/ctams-logo.jpg'))

    def test_as_brand_exposes_all_template_keys(self):
        brand = CompanyProfile.objects.get(key='cta').as_brand()
        for key in ('key', 'name', 'tag', 'full_name', 'address', 'tel', 'email', 'signataire',
                    'rccm', 'ncc', 'bank_name', 'bank_account', 'mobile_money', 'logo_url'):
            self.assertIn(key, brand)

    def test_as_brand_values_follow_the_profile(self):
        profile = CompanyProfile.objects.get(key='cta')
        profile.rccm = 'R-1'
        profile.ncc = 'N-2'
        profile.save()
        brand = profile.as_brand()
        self.assertEqual(brand['rccm'], 'R-1')
        self.assertEqual(brand['ncc'], 'N-2')
        self.assertEqual(brand['name'], profile.name)
        self.assertEqual(brand['email'], profile.email)
        self.assertEqual(brand['logo_url'], profile.logo_url)
