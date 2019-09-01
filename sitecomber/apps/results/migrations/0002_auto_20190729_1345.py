# Generated by Django 2.2.3 on 2019-07-29 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pagerequest',
            options={'ordering': ['-created']},
        ),
        migrations.RenameField(
            model_name='pageresult',
            old_name='last_load_time',
            new_name='last_load_end_time',
        ),
        migrations.AddField(
            model_name='pageresult',
            name='error_synopsis',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='last_content_length',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='last_content_type',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='last_load_start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='last_status_code',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='last_text_content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='load_end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='load_start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pageresult',
            name='warning_synoposis',
            field=models.TextField(blank=True, null=True),
        ),
    ]