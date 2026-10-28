from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0007_deliverynote_vehicule_immatriculation_and_more'),
    ]

    operations = [
        migrations.RenameField(model_name='proforma', old_name='destinataire_rccm_ncc', new_name='destinataire_rccm'),
        migrations.AlterField(
            model_name='proforma',
            name='destinataire_rccm',
            field=models.CharField(blank=True, max_length=100, verbose_name='RCCM'),
        ),
        migrations.AddField(
            model_name='proforma',
            name='destinataire_ncc',
            field=models.CharField(blank=True, max_length=100, verbose_name='NCC'),
        ),
        migrations.RenameField(model_name='proforma', old_name='vehicule_marque_modele', new_name='vehicule_marque'),
        migrations.AlterField(
            model_name='proforma',
            name='vehicule_marque',
            field=models.CharField(blank=True, max_length=80, verbose_name='Marque'),
        ),
        migrations.AddField(
            model_name='proforma',
            name='vehicule_modele',
            field=models.CharField(blank=True, max_length=80, verbose_name='Modèle'),
        ),
        migrations.RenameField(model_name='invoice', old_name='destinataire_rccm_ncc', new_name='destinataire_rccm'),
        migrations.AlterField(
            model_name='invoice',
            name='destinataire_rccm',
            field=models.CharField(blank=True, max_length=100, verbose_name='RCCM'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='destinataire_ncc',
            field=models.CharField(blank=True, max_length=100, verbose_name='NCC'),
        ),
        migrations.RenameField(model_name='invoice', old_name='vehicule_marque_modele', new_name='vehicule_marque'),
        migrations.AlterField(
            model_name='invoice',
            name='vehicule_marque',
            field=models.CharField(blank=True, max_length=80, verbose_name='Marque'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='vehicule_modele',
            field=models.CharField(blank=True, max_length=80, verbose_name='Modèle'),
        ),
        migrations.RenameField(model_name='deliverynote', old_name='destinataire_rccm_ncc', new_name='destinataire_rccm'),
        migrations.AlterField(
            model_name='deliverynote',
            name='destinataire_rccm',
            field=models.CharField(blank=True, max_length=100, verbose_name='RCCM'),
        ),
        migrations.AddField(
            model_name='deliverynote',
            name='destinataire_ncc',
            field=models.CharField(blank=True, max_length=100, verbose_name='NCC'),
        ),
        migrations.RenameField(model_name='deliverynote', old_name='vehicule_marque_modele', new_name='vehicule_marque'),
        migrations.AlterField(
            model_name='deliverynote',
            name='vehicule_marque',
            field=models.CharField(blank=True, max_length=80, verbose_name='Marque'),
        ),
        migrations.AddField(
            model_name='deliverynote',
            name='vehicule_modele',
            field=models.CharField(blank=True, max_length=80, verbose_name='Modèle'),
        ),
    ]
