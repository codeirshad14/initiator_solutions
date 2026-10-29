from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web2', '0043_alter_blog_alt_alter_blog_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_type', models.CharField(choices=[('product', 'Product'), ('service', 'Service'), ('module', 'Our Modules')], default='product', help_text='Product groups filter the Products page, Service groups the Services page and Our Modules groups the Our Modules page.', max_length=20, verbose_name='Group for')),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(blank=True, help_text='Used in page URLs. Leave blank to create it from the name.', max_length=150)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Product / Service / Module Group',
                'verbose_name_plural': 'Product / Service / Module Groups',
                'ordering': ['group_type', 'sort_order', 'name'],
            },
        ),
        migrations.AddConstraint(
            model_name='cataloggroup',
            constraint=models.UniqueConstraint(fields=('group_type', 'slug'), name='unique_catalog_group_slug_per_type'),
        ),
        # Temporary link fields, filled by 0045 and renamed by 0046.
        migrations.AddField(
            model_name='product',
            name='product_group_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='web2.cataloggroup'),
        ),
        migrations.AddField(
            model_name='service',
            name='service_group_ref',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='web2.cataloggroup'),
        ),
        migrations.AddField(
            model_name='service',
            name='module_group',
            field=models.ForeignKey(blank=True, help_text='Group shown on the Our Modules page. Required when "Show on module page" is ticked.', limit_choices_to={'group_type': 'module'}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='module_services', to='web2.cataloggroup'),
        ),
    ]
