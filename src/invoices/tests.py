from datetime import date

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from parametres.models import CompanyProfile

from .branding import get_brand
from .models import DeliveryNote, Invoice, Proforma


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
        self.assertEqual(get_brand(self.factory.get('/', {'marque': 'CTA'}))['key'], 'cta')

    def test_empty_database_falls_back_to_hardcoded_values(self):
        CompanyProfile.objects.all().delete()
        brand = get_brand(self.factory.get('/', {'marque': 'cta'}))
        self.assertEqual(brand['key'], 'cta')
        self.assertEqual(brand['email'], 'centretechniqueauto@outlook.com')
        self.assertEqual(brand['rccm'], '')
        self.assertTrue(brand['logo_url'].endswith('app/assets/img/cta-logo.png'))


class PrintTemplatesTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='printer', password='pass12345')
        self.client.force_login(user)
        today = date.today()
        self.urls = {
            'invoice': reverse('invoice_print', args=[
                Invoice.objects.create(destinataire_nom='Client', date_emission=today).pk]),
            'proforma': reverse('proforma_print', args=[
                Proforma.objects.create(destinataire_nom='Client', date_emission=today).pk]),
            'delivery': reverse('delivery_print', args=[
                DeliveryNote.objects.create(destinataire_nom='Client', date_livraison=today).pk]),
        }

    def test_legal_and_payment_info_shown_when_filled(self):
        CompanyProfile.objects.filter(key='ctams').update(
            rccm='CI-ABJ-2020-B-1', ncc='1234567 A',
            bank_name='Banque Test', bank_account='CI93 0000', mobile_money='Wave 07 00 00 00 00',
        )
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            for text in ('CI-ABJ-2020-B-1', '1234567 A', 'Banque Test', 'CI93 0000', 'Wave 07 00 00 00 00'):
                self.assertIn(text, html, f'{text} absent de {name}')

    def test_nothing_shown_when_empty(self):
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            for label in ('RCCM :', 'NCC :', 'Banque :', 'Mobile Money :'):
                self.assertNotIn(label, html, f'{label} affiché sur {name}')

    def test_uploaded_logo_url_used_in_header(self):
        CompanyProfile.objects.filter(key='ctams').update(logo='logos/test.png')
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            self.assertIn('/media/logos/test.png', html, name)
