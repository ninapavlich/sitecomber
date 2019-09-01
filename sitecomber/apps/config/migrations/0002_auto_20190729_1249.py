# Generated by Django 2.2.3 on 2019-07-29 19:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IgnoreResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('path', models.CharField(help_text='Match either a fully qualified URL or paths using Unix shell-style wildcards, e.g. */files/*.txt', max_length=2000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IncludeSeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.URLField(max_length=2000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='site',
            name='max_page_results',
            field=models.IntegerField(blank=True, help_text='Limit the total number of pages crawled on a given site.', null=True),
        ),
        migrations.DeleteModel(
            name='IgnoreURL',
        ),
        migrations.AddField(
            model_name='includeseed',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Site'),
        ),
        migrations.AddField(
            model_name='ignoreresult',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='config.Site'),
        ),
    ]