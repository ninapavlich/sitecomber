# Generated by Django 2.2.3 on 2019-07-17 05:25

from django.db import migrations, models
import django.db.models.deletion
import encrypted_model_fields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('request_url', models.URLField()),
                ('method', models.CharField(blank=True, choices=[('GET', 'GET'), ('HEAD', 'HEAD'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'), ('CONNECT', 'CONNECT'), ('OPTIONS', 'OPTIONS'), ('TRACE', 'TRACE'), ('PATCH', 'PATCH')], max_length=255, null=True)),
                ('load_start_time', models.DateTimeField(blank=True, null=True)),
                ('load_end_time', models.DateTimeField(blank=True, null=True)),
                ('retain', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PageResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('response_url', models.URLField()),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('content_type', models.CharField(blank=True, max_length=255, null=True)),
                ('content_length', models.IntegerField(blank=True, null=True)),
                ('http_version', models.CharField(blank=True, max_length=255, null=True)),
                ('remote_address', models.CharField(blank=True, max_length=255, null=True)),
                ('load_start_time', models.DateTimeField(blank=True, null=True)),
                ('load_end_time', models.DateTimeField(blank=True, null=True)),
                ('text_content', models.TextField(blank=True, null=True)),
                ('redirected_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='results.PageResponse')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.PageRequest')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PageResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('authentication_type', models.CharField(choices=[('none', 'None'), ('basic_auth', 'Basic Auth')], default='none', max_length=16)),
                ('authentication_data', encrypted_model_fields.fields.EncryptedCharField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(max_length=2000)),
                ('last_load_time', models.DateTimeField(blank=True, null=True)),
                ('is_sitemap', models.BooleanField(default=False)),
                ('is_root', models.BooleanField(default=False)),
                ('is_internal', models.BooleanField(default=True)),
                ('incoming_links', models.ManyToManyField(related_name='page_incoming_links', to='results.PageResult')),
                ('outgoing_links', models.ManyToManyField(related_name='page_outgoing_links', to='results.PageResult')),
                ('site_domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.SiteDomain')),
            ],
            options={
                'ordering': ['site_domain', 'url'],
            },
        ),
        migrations.CreateModel(
            name='SiteTestResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('test', models.CharField(choices=[('sitecomber.apps.tests.core.BrokenLinkTest', 'BrokenLinkTest')], max_length=255)),
                ('data', models.TextField(blank=True, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('success', 'Success'), ('error', 'Error')], default='info', max_length=16)),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteDomainTestResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('test', models.CharField(choices=[('sitecomber.apps.tests.core.BrokenLinkTest', 'BrokenLinkTest')], max_length=255)),
                ('data', models.TextField(blank=True, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('success', 'Success'), ('error', 'Error')], default='info', max_length=16)),
                ('site_domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.SiteDomain')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResponseHeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.PageResponse')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RequestHeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('value', models.CharField(blank=True, max_length=255, null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.PageRequest')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PageTestResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('test', models.CharField(choices=[('sitecomber.apps.tests.core.BrokenLinkTest', 'BrokenLinkTest')], max_length=255)),
                ('data', models.TextField(blank=True, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('info', 'Info'), ('warning', 'Warning'), ('success', 'Success'), ('error', 'Error')], default='info', max_length=16)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.PageResult')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='pagerequest',
            name='page_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.PageResult'),
        ),
        migrations.AddField(
            model_name='pagerequest',
            name='response',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='results.PageResponse'),
        ),
    ]
