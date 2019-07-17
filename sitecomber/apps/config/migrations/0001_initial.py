# Generated by Django 2.2.3 on 2019-07-17 05:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('recursive', models.BooleanField(default=True)),
                ('override_user_agent', models.TextField(blank=True, null=True)),
                ('override_max_redirects', models.IntegerField(blank=True, null=True)),
                ('override_max_timeout_seconds', models.IntegerField(blank=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteTestSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('test', models.CharField(choices=[('sitecomber.apps.tests.core.BrokenLinkTest', 'BrokenLinkTest')], max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('settings', models.TextField(blank=True, null=True)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteDomain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('authentication_type', models.CharField(choices=[('none', 'None'), ('basic_auth', 'Basic Auth')], default='none', max_length=16)),
                ('authentication_data', encrypted_model_fields.fields.EncryptedCharField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(max_length=2000)),
                ('should_crawl', models.BooleanField(default=True)),
                ('alias_of', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='config.SiteDomain')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IgnoreURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('authentication_type', models.CharField(choices=[('none', 'None'), ('basic_auth', 'Basic Auth')], default='none', max_length=16)),
                ('authentication_data', encrypted_model_fields.fields.EncryptedCharField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(max_length=2000)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IgnoreQueryParam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('param', models.CharField(max_length=255)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
