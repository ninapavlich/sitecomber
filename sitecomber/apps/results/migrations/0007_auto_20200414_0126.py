# Generated by Django 2.2.10 on 2020-04-14 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0006_auto_20200414_0115'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pageresponse',
            name='text_content',
        ),
        migrations.RemoveField(
            model_name='pageresult',
            name='last_text_content',
        ),
        
    ]