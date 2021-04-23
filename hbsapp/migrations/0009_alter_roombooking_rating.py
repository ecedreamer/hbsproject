# Generated by Django 3.2 on 2021-04-23 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hbsapp', '0008_alter_roombooking_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roombooking',
            name='rating',
            field=models.PositiveIntegerField(blank=True, choices=[(5, 'One of the best room, I highly recommend to stay here'), (4, 'Very Good Room, I recommend to stay here'), (3, 'Good Room and nice service'), (2, 'Its ok, no comment'), (1, 'I do not recommend this room')], null=True),
        ),
    ]