from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils import timezone
from django.urls import reverse

from parametres.models import CompanyProfile, DocumentDefaults

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
            for text in ('RCCM : CI-ABJ-2020-B-1', 'NCC : 1234567 A', 'Banque : Banque Test',
                         'IBAN / RIB : CI93 0000', 'Mobile Money : Wave 07 00 00 00 00'):
                self.assertIn(text, html, f'{text} absent de {name}')

    def test_rccm_ncc_always_listed_in_emitter(self):
        CompanyProfile.objects.filter(key='ctams').update(
            rccm='', ncc='', bank_name='', bank_account='', mobile_money='')
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            emitter = html.split('<div class="party-info">')[1].split('</div>')[0]
            self.assertIn('RCCM : —', emitter, name)
            self.assertIn('NCC : —', emitter, name)
            for label in ('Banque :', 'IBAN / RIB :', 'Mobile Money :'):
                self.assertNotIn(label, html, f'{label} affiché sur {name}')

    def test_site_link_in_footer_and_contacts_not_in_header(self):
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            self.assertIn('href="https://www.ctams.net/"', html, name)
            header = html.split('<div class="doc-header">')[1].split('<div class="parties">')[0]
            self.assertNotIn('@', header, f"email dans l'en-tête de {name}")
            for field_id in ('edit-tel', 'edit-email'):
                self.assertNotIn(field_id, html, f'{field_id} encore présent dans {name}')

    def test_issuer_values_are_html_escaped(self):
        CompanyProfile.objects.filter(key='ctams').update(bank_name='<b>x</b>')
        html = self.client.get(self.urls['invoice']).content.decode()
        self.assertIn('&lt;b&gt;x&lt;/b&gt;', html)
        self.assertNotIn('<b>x</b>', html)

    def test_uploaded_logo_url_used_in_header(self):
        CompanyProfile.objects.filter(key='ctams').update(logo='logos/test.png')
        for name, url in self.urls.items():
            html = self.client.get(url).content.decode()
            self.assertIn(settings.MEDIA_URL + 'logos/test.png', html, name)


class DocumentDefaultsPrefillTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username='creator', password='pass12345')
        self.client.force_login(user)
        defaults = DocumentDefaults.load()
        defaults.tva_taux = 10
        defaults.conditions_paiement = 'Comptant'
        defaults.penalites_retard = 'Aucune'
        defaults.save()

    def test_new_invoice_form_uses_defaults(self):
        form = self.client.get(reverse('invoice_create')).context['form']
        self.assertEqual(form['tva_taux'].value(), 10)
        self.assertEqual(form['conditions_paiement'].value(), 'Comptant')
        self.assertEqual(form['penalites_retard'].value(), 'Aucune')

    def test_new_proforma_form_uses_default_tva(self):
        form = self.client.get(reverse('proforma_create')).context['form']
        self.assertEqual(form['tva_taux'].value(), 10)


class ProformaValiditeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='pf', password='pass12345')
        self.client.force_login(self.user)
        self.expected = timezone.localdate() + timedelta(days=7)

    def post_data(self, **extra):
        data = {
            'date_emission': date.today().isoformat(), 'tva_taux': '18', 'remise_globale': '0',
            'status': 'DRAFT', 'destinataire_nom': 'Client',
            'line-0-designation': 'Vidange', 'line-0-quantite': '1', 'line-0-prix_unitaire': '10000',
        }
        data.update(extra)
        return data

    def test_validity_is_seven_days_after_creation(self):
        proforma = Proforma.objects.create(destinataire_nom='Client', date_emission=date(2020, 1, 1))
        self.assertEqual(proforma.date_validite, self.expected)

    def test_created_from_form_ignores_posted_validity(self):
        response = self.client.post(
            reverse('proforma_create'), self.post_data(date_validite='2030-01-01'),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Proforma.objects.get().date_validite, self.expected)

    def test_editing_does_not_change_validity(self):
        proforma = Proforma.objects.create(destinataire_nom='Client', date_emission=date.today())
        Proforma.objects.filter(pk=proforma.pk).update(date_validite=date(2026, 1, 15))
        response = self.client.post(
            reverse('proforma_edit', args=[proforma.pk]),
            self.post_data(destinataire_nom='Autre', date_validite='2030-01-01'),
        )
        self.assertEqual(response.status_code, 302)
        proforma.refresh_from_db()
        self.assertEqual(proforma.destinataire_nom, 'Autre')
        self.assertEqual(proforma.date_validite, date(2026, 1, 15))

    def test_print_shows_the_validity_date(self):
        proforma = Proforma.objects.create(destinataire_nom='Client', date_emission=date.today())
        html = self.client.get(reverse('proforma_print', args=[proforma.pk])).content.decode()
        self.assertIn(self.expected.strftime('%d/%m/%Y'), html)


class VehicleOnDocumentsTests(TestCase):
    VEHICLE = {
        'vehicule_marque': 'Toyota',
        'vehicule_modele': 'Corolla',
        'vehicule_immatriculation': '1234 AB 01',
        'vehicule_kilometrage': 125000,
    }

    def setUp(self):
        user = get_user_model().objects.create_user(username='veh', password='pass12345')
        self.client.force_login(user)
        today = date.today()
        self.docs = {
            'invoice': Invoice.objects.create(destinataire_nom='C', date_emission=today, **self.VEHICLE),
            'proforma': Proforma.objects.create(destinataire_nom='C', date_emission=today, **self.VEHICLE),
            'delivery': DeliveryNote.objects.create(destinataire_nom='C', date_livraison=today, **self.VEHICLE),
        }

    def print_html(self, name):
        return self.client.get(reverse(f'{name}_print', args=[self.docs[name].pk])).content.decode()

    def test_vehicle_blue_box_top_right_under_dates(self):
        for name in self.docs:
            html = self.print_html(name)
            self.assertIn('.vehicle-box{', html, name)
            box = html.split('<div class="vehicle-box">')[1].split('</div>')[0]
            for text in ('Marque :</span><b>Toyota</b>', 'Modèle :</span><b>Corolla</b>',
                         'Immatriculation :</span><b>1234 AB 01</b>'):
                self.assertIn(text, box, f'{text} absent de {name}')
            dates = html.split('<div class="doc-dates">')[1].split('</div>')[0]
            self.assertNotIn('Immatriculation', dates, name)
            self.assertIn('class="doc-id"', html.split('<div class="vehicle-box">')[0], name)
            self.assertEqual(html.count('<div class="vehicle-box">'), 1, name)
            box_at = html.index('<div class="vehicle-box">')
            self.assertGreater(box_at, html.index('<div class="doc-dates">'), name)
            self.assertLess(box_at, html.index('class="parties"'), name)

    def test_nothing_shown_without_vehicle(self):
        Invoice.objects.filter(pk=self.docs['invoice'].pk).update(
            vehicule_marque='', vehicule_modele='', vehicule_immatriculation='', vehicule_kilometrage=None,
        )
        html = self.print_html('invoice')
        self.assertNotIn('<div class="vehicle-box">', html)
        for label in ('Marque :', 'Modèle :', 'Immatriculation :'):
            self.assertNotIn(label, html)

    def test_mileage_not_printed(self):
        for name in self.docs:
            html = self.print_html(name)
            self.assertNotIn('Kilométrage', html, name)
            self.assertNotIn('125000', html, name)

    def test_forms_offer_existing_vehicles_and_save_fields(self):
        from customers.models import Customer
        from vehicles.models import Vehicle
        customer = Customer.objects.create(customer_type='INDIVIDUAL', first_name='Awa', last_name='Kone')
        Vehicle.objects.create(
            registration_number='9999 ZZ 01', make='Peugeot', model='206', mileage=88000, customer=customer,
        )
        for url_name in ('invoice_create', 'proforma_create', 'delivery_create'):
            html = self.client.get(reverse(url_name)).content.decode()
            self.assertIn('data-immat="9999 ZZ 01"', html, url_name)
            self.assertIn('data-km="88000"', html, url_name)
            self.assertIn('name="vehicule_immatriculation"', html, url_name)

        response = self.client.post(reverse('invoice_create'), {
            'date_emission': date.today().isoformat(), 'tva_taux': '18', 'remise_globale': '0',
            'acompte_verse': '0', 'status': 'DRAFT', 'destinataire_nom': 'Awa',
            'vehicule_marque': 'Peugeot', 'vehicule_modele': '206', 'vehicule_immatriculation': '9999 ZZ 01',
            'vehicule_kilometrage': '88000',
            'line-0-designation': 'Vidange', 'line-0-quantite': '1', 'line-0-prix_unitaire': '10000',
        })
        self.assertEqual(response.status_code, 302)
        invoice = Invoice.objects.exclude(pk=self.docs['invoice'].pk).get()
        self.assertEqual((invoice.vehicule_marque, invoice.vehicule_modele), ('Peugeot', '206'))
        self.assertEqual(invoice.vehicule_kilometrage, 88000)

    def test_vehicle_copied_on_proforma_to_invoice_and_invoice_to_delivery(self):
        self.client.post(reverse('proforma_to_invoice', args=[self.docs['proforma'].pk]))
        converted = Invoice.objects.get(proforma=self.docs['proforma'])
        self.assertEqual(converted.vehicule_immatriculation, '1234 AB 01')
        self.assertEqual(converted.vehicule_kilometrage, 125000)

        self.client.post(reverse('invoice_to_delivery', args=[self.docs['invoice'].pk]))
        delivery = DeliveryNote.objects.get(invoice=self.docs['invoice'])
        self.assertEqual((delivery.vehicule_marque, delivery.vehicule_modele), ('Toyota', 'Corolla'))
        self.assertEqual(delivery.vehicule_kilometrage, 125000)


class DestinataireRccmNccTests(TestCase):
    def test_rccm_and_ncc_on_separate_lines_on_every_print(self):
        user = get_user_model().objects.create_user(username='dest', password='pass12345')
        self.client.force_login(user)
        today = date.today()
        common = dict(destinataire_nom='Garage Elite', destinataire_adresse='Cocody', destinataire_tel='01 02',
                      destinataire_rccm='CI-ABJ-2020-B-1234', destinataire_ncc='1234567 A')
        docs = {
            'invoice': Invoice.objects.create(date_emission=today, **common),
            'proforma': Proforma.objects.create(date_emission=today, **common),
            'delivery': DeliveryNote.objects.create(date_livraison=today, **common),
        }
        for name, doc in docs.items():
            html = self.client.get(reverse(f'{name}_print', args=[doc.pk])).content.decode()
            for text in ('<span>Adresse :</span>Cocody', '<span>Tél :</span>01 02',
                         '<span>RCCM :</span>CI-ABJ-2020-B-1234', '<span>NCC :</span>1234567 A'):
                self.assertIn(text, html, f'{text} absent de {name}')
