# Generated by Django 2.2.10 on 2020-04-14 05:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0004_auto_20200304_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageResponseText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('text_content', models.TextField(blank=True, null=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='results.PageResponse')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
