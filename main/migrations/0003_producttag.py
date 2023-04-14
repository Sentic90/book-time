# Generated by Django 2.2.28 on 2023-04-13 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_productimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('slug', models.SlugField(max_length=48)),
                ('description', models.TextField(blank=True)),
                ('active', models.BooleanField(default=True)),
                ('products', models.ManyToManyField(blank=True, to='main.Product')),
            ],
        ),
    ]
