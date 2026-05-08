from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="campusitem",
            name="reporter",
            field=models.BigIntegerField(
                blank=True,
                db_column="reporter_id",
                null=True,
                verbose_name="publicado por",
            ),
        ),
    ]
