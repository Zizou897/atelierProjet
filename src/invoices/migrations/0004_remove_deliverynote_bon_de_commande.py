from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_rename_bon_de_commande_to_livraison'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverynote',
            name='bon_de_commande',
        ),
    ]
