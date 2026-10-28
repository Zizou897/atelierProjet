from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_customer_rccm_ncc'),
    ]

    operations = [
        migrations.RenameField(model_name='customer', old_name='rccm_ncc', new_name='rccm'),
        migrations.AlterField(
            model_name='customer',
            name='rccm',
            field=models.CharField(blank=True, max_length=100, verbose_name='RCCM'),
        ),
        migrations.AddField(
            model_name='customer',
            name='ncc',
            field=models.CharField(blank=True, max_length=100, verbose_name='NCC'),
        ),
    ]
