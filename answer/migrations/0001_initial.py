# Generated by Django 2.1.7 on 2019-03-21 10:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('question', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meetup', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by',
                 models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL,
                                   to_field='username')),
                ('meetup', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='meetup.Meeting')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='question.Question')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='answers',
            unique_together={('body', 'question', 'meetup')},
        ),
    ]
