# Generated by Django 3.1.6 on 2021-02-13 21:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_status_default_trialing")]

    operations = [
        migrations.AlterField(
            model_name="account",
            name="status",
            field=models.IntegerField(
                choices=[
                    (1, "Exempt"),
                    (2, "Beta"),
                    (3, "Trialing"),
                    (4, "Active"),
                    (5, "Past Due"),
                    (6, "Canceled"),
                    (7, "Trial Expired"),
                ],
                db_index=True,
                default=3,
            ),
        )
    ]
