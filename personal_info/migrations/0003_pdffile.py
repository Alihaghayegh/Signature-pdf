# Generated by Django 5.0.6 on 2024-06-16 06:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal_info', '0002_remove_userinfo_credentials_alter_userinfo_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='pdfs/')),
                ('status', models.CharField(default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='personal_info.userinfo')),
            ],
        ),
    ]
