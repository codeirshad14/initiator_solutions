from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web2', '0045_populate_catalog_groups'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='product_group',
        ),
        migrations.RemoveField(
            model_name='service',
            name='service_group',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='product_group_ref',
            new_name='product_group',
        ),
        migrations.RenameField(
            model_name='service',
            old_name='service_group_ref',
            new_name='service_group',
        ),
        migrations.AlterField(
            model_name='product',
            name='product_group',
            field=models.ForeignKey(limit_choices_to={'group_type': 'product'}, on_delete=django.db.models.deletion.PROTECT, related_name='products', to='web2.cataloggroup'),
        ),
        migrations.AlterField(
            model_name='service',
            name='service_group',
            field=models.ForeignKey(limit_choices_to={'group_type': 'service'}, on_delete=django.db.models.deletion.PROTECT, related_name='services', to='web2.cataloggroup'),
        ),
    ]
