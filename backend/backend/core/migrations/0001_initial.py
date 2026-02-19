from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DesignAsset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file", models.FileField(upload_to="assets/")),
                ("original_filename", models.CharField(max_length=255)),
                ("mime_type", models.CharField(blank=True, max_length=100)),
                ("size_bytes", models.PositiveIntegerField(default=0)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="JobRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("task_name", models.CharField(max_length=120)),
                ("reference_id", models.CharField(max_length=100)),
                ("status", models.CharField(choices=[("queued", "Queued"), ("running", "Running"), ("success", "Success"), ("failed", "Failed")], default="queued", max_length=16)),
                ("detail", models.JSONField(blank=True, default=dict)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Template",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("gelato_template_id", models.CharField(max_length=120, unique=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ProductDraft",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("tags", models.JSONField(blank=True, default=list)),
                ("seo", models.JSONField(blank=True, default=dict)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("queued", "Queued"), ("pushed", "Pushed"), ("failed", "Failed")], default="draft", max_length=16)),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("assets", models.ManyToManyField(related_name="drafts", to="core.designasset")),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="drafts", to="core.template")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ShopifyProduct",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("shopify_product_id", models.CharField(max_length=120, unique=True)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("draft", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="shopify_product", to="core.productdraft")),
            ],
            options={"abstract": False},
        ),
    ]
