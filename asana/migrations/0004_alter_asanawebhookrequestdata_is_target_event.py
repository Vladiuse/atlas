# Generated by Django 5.0.4 on 2025-07-22 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("asana", "0003_completedtask_task_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asanawebhookrequestdata",
            name="is_target_event",
            field=models.BooleanField(default=False),
        ),
    ]
