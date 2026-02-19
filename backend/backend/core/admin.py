from django.contrib import admin

from .models import DesignAsset, JobRun, ProductDraft, ShopifyProduct, Template

admin.site.register(Template)
admin.site.register(DesignAsset)
admin.site.register(ProductDraft)
admin.site.register(ShopifyProduct)
admin.site.register(JobRun)
