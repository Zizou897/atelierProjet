import io
import shutil
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import CompanyProfileForm, DocumentDefaultsForm
from .models import CompanyProfile, DocumentDefaults

User = get_user_model()


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


def make_image(name='logo.png', fmt='PNG', size=(10, 10)):
    buf = io.BytesIO()
    Image.new('RGB', size, 'red').save(buf, fmt)
    return SimpleUploadedFile(name, buf.getvalue(), content_type=f'image/{fmt.lower()}')


def company_data(**overrides):
    data = {
        'name': 'CTA', 'tag': '', 'full_name': 'CENTRE TECHNIQUE AUTO (CTA)',
        'address': 'Riviera', 'tel': '01 02', 'email': 'cta@example.com', 'signataire': '',
        'rccm': 'CI-1', 'ncc': '123', 'bank_name': '', 'bank_account': '', 'mobile_money': '',
    }
    data.update(overrides)
    return data


class CompanyProfileFormTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)
        override = override_settings(MEDIA_ROOT=self.media)
        override.enable()
        self.addCleanup(override.disable)
        self.profile = CompanyProfile.objects.get(key='cta')

    def test_saves_valid_data(self):
        form = CompanyProfileForm(company_data(), instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.rccm, 'CI-1')
        self.assertEqual(self.profile.ncc, '123')

    def test_required_fields(self):
        form = CompanyProfileForm(company_data(email='', tel='', address=''), instance=self.profile)
        self.assertFalse(form.is_valid())
        for field in ('email', 'tel', 'address'):
            self.assertIn(field, form.errors)

    def test_rejects_invalid_email(self):
        form = CompanyProfileForm(company_data(email='pas-un-email'), instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_accepts_png_logo(self):
        form = CompanyProfileForm(company_data(), {'logo': make_image()}, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.logo.name.startswith('logos/'))

    def test_rejects_non_image_logo(self):
        fake = SimpleUploadedFile('logo.png', b'pas une image', content_type='image/png')
        form = CompanyProfileForm(company_data(), {'logo': fake}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_rejects_wrong_extension(self):
        form = CompanyProfileForm(company_data(), {'logo': make_image('logo.gif', 'GIF')}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_rejects_logo_over_2mb(self):
        big = SimpleUploadedFile('logo.png', make_image().read() + b'0' * (2 * 1024 * 1024), content_type='image/png')
        form = CompanyProfileForm(company_data(), {'logo': big}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)
        self.assertIn('2 Mo', str(form.errors['logo']))

    def test_gif_renamed_png_is_rejected(self):
        form = CompanyProfileForm(company_data(), {'logo': make_image('logo.png', 'GIF')}, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('logo', form.errors)

    def test_upload_wins_over_remove_checkbox(self):
        self.profile.logo = 'logos/old.png'
        self.profile.save()
        form = CompanyProfileForm(company_data(remove_logo='on'), {'logo': make_image()}, instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.logo.name.startswith('logos/'))
        self.assertNotEqual(self.profile.logo.name, 'logos/old.png')

    def test_remove_logo_checkbox_restores_default(self):
        self.profile.logo = 'logos/old.png'
        self.profile.save()
        form = CompanyProfileForm(company_data(remove_logo='on'), instance=self.profile)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.logo)
        self.assertTrue(self.profile.logo_url.endswith('cta-logo.png'))


class DocumentDefaultsFormTests(TestCase):
    def test_saves_valid_data(self):
        form = DocumentDefaultsForm(
            {'tva_taux': '10', 'conditions_paiement': 'Comptant', 'penalites_retard': ''},
            instance=DocumentDefaults.load(),
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(DocumentDefaults.load().tva_taux, 10)

    def test_tva_must_be_between_0_and_100(self):
        for bad in ('-1', '101'):
            form = DocumentDefaultsForm(
                {'tva_taux': bad, 'conditions_paiement': '', 'penalites_retard': ''},
                instance=DocumentDefaults.load(),
            )
            self.assertFalse(form.is_valid(), bad)
            self.assertIn('tva_taux', form.errors)


class SettingsViewTests(TestCase):
    def setUp(self):
        self.url = reverse('settings_home')
        self.admin = User.objects.create_superuser(username='boss', password='pass12345')
        self.user = User.objects.create_user(username='simple', password='pass12345')

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_non_admin_gets_403(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, company_data()).status_code, 403)

    def test_admin_sees_each_tab(self):
        self.client.force_login(self.admin)
        for tab in ('ctams', 'cta', 'documents'):
            response = self.client.get(self.url, {'onglet': tab})
            self.assertEqual(response.status_code, 200, tab)
        self.assertEqual(self.client.get(self.url, {'onglet': 'inconnu'}).status_code, 200)

    def test_admin_saves_company_tab(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url + '?onglet=cta', company_data(rccm='CI-ABJ-2020-B-77', ncc='9999 Z'),
        )
        self.assertRedirects(response, self.url + '?onglet=cta')
        cta = CompanyProfile.objects.get(key='cta')
        self.assertEqual(cta.rccm, 'CI-ABJ-2020-B-77')
        self.assertEqual(CompanyProfile.objects.get(key='ctams').rccm, '')

    def test_invalid_company_form_is_not_saved(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url + '?onglet=cta', company_data(email='nope'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CompanyProfile.objects.get(key='cta').email, 'centretechniqueauto@outlook.com')

    def test_admin_saves_documents_tab(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url + '?onglet=documents',
            {'tva_taux': '10', 'conditions_paiement': 'Comptant', 'penalites_retard': 'Aucune'},
        )
        self.assertRedirects(response, self.url + '?onglet=documents')
        defaults = DocumentDefaults.load()
        self.assertEqual(defaults.tva_taux, 10)
        self.assertEqual(defaults.conditions_paiement, 'Comptant')

    def test_menu_link_visible_for_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, self.url)
