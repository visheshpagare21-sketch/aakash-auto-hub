from django.db import migrations


def enable_pg_trgm(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_category_homepage_order_category_show_on_homepage_and_more'),
    ]

    operations = [
        migrations.RunPython(enable_pg_trgm, migrations.RunPython.noop),
    ]
