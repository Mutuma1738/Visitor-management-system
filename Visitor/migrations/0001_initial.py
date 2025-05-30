# Generated by Django 5.1.6 on 2025-04-16 15:25

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Directorate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("director_name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="PredefinedResponse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Approved", "Approved"),
                            ("Declined", "Declined"),
                            ("Forwarded", "Forwarded"),
                        ],
                        max_length=20,
                    ),
                ),
                ("response_text", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Visitor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("Id_number", models.CharField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("mobile", models.CharField(max_length=15)),
                ("email", models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("senior_manager_name", models.CharField(max_length=100)),
                (
                    "directorate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Visitor.directorate",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Employee",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "designation",
                    models.CharField(
                        choices=[
                            ("Director", "Director"),
                            ("Senior Manager", "Senior Manager"),
                            ("Junior Manager", "Junior Manager"),
                            ("Employee", "Employee"),
                            ("Attachee", "Attachee"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Visitor.department",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VisitLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "purpose",
                    models.CharField(
                        choices=[("Personal", "Personal"), ("Official", "Official")],
                        max_length=10,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Approved", "Approved"),
                            ("Declined", "Declined"),
                            ("Forwarded", "Forwarded"),
                        ],
                        default="Pending",
                        max_length=10,
                    ),
                ),
                ("comments", models.TextField(blank=True, null=True)),
                ("arrival_time", models.DateTimeField(blank=True, null=True)),
                ("delayed_arrival_time", models.DateTimeField(blank=True, null=True)),
                (
                    "expiry_duration",
                    models.DurationField(default=datetime.timedelta(seconds=7200)),
                ),
                ("expiry_time", models.DateTimeField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("wait_duration", models.DurationField(blank=True, null=True)),
                ("wait_until", models.DateTimeField(blank=True, null=True)),
                ("reminder_count", models.PositiveIntegerField(default=0)),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assigned_visits",
                        to="Visitor.employee",
                    ),
                ),
                (
                    "forwarded_from",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="forwarded_visits_sent",
                        to="Visitor.employee",
                    ),
                ),
                (
                    "forwarded_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="forwarded_visits_received",
                        to="Visitor.employee",
                    ),
                ),
                (
                    "visitor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="Visitor.visitor",
                    ),
                ),
            ],
        ),
    ]
