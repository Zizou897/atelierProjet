from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0002_deliverynote_deliverynoteline'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proforma',
            old_name='bon_de_commande',
            new_name='bon_de_livraison',
        ),
        migrations.RenameField(
            model_name='invoice',
            old_name='bon_de_commande',
            new_name='bon_de_livraison',
        ),
        migrations.AlterField(
            model_name='proforma',
            name='bon_de_livraison',
            field=models.CharField(blank=True, max_length=100, verbose_name='Bon de livraison'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='bon_de_livraison',
            field=models.CharField(blank=True, max_length=100, verbose_name='Bon de livraison'),
        ),
    ]
