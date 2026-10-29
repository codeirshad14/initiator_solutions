from django.contrib import admin
from django import forms
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Tally_Prime_Model, Blog, ContactModel, \
    WebDevModel, AboutUSModel, AboutVisionModel, PortfolioModel, All_AccoutingModel, All_ERPModel, Web_DesignModel, \
    Web_Portal_Dev, MobileAppModel, Tally_Customization, Tally_VerticalModel, Tally_CloudModel, Digital_Mkt_Model, \
    Graphics_Model, CloudModel, OurNewsLetter, Lan_PageBanModel, Lan_AboutusModel, Lan_ProductModel, Lan_ServicesModel, \
    SiteSEO, ProductUpload, Product, Service, ContactIntegrationSettings, CatalogGroup


SEO_FIELDSET_HINT = (
    'All fields are optional: blank fields use automatic values from the name and description. '
    'Quick rules: meta title 50-60 characters, meta description 120-155 characters, one focus keyword, '
    'canonical URL blank.'
)


class RichTextEditorWidget(forms.Textarea):
    class Media:
        css = {
            'all': ('web2/admin/rich_text_editor.css',)
        }
        js = ('web2/admin/rich_text_editor.js',)

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs['class'] = f"{attrs.get('class', '')} rich-text-source".strip()
        attrs.setdefault('rows', 16)
        super().__init__(attrs=attrs)


class BlogAdminForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = '__all__'
        widgets = {
            'body': RichTextEditorWidget,
        }


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'short_description': RichTextEditorWidget,
            'description': RichTextEditorWidget,
        }


class ServiceAdminForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'short_description': RichTextEditorWidget,
            'description': RichTextEditorWidget,
        }


class AboutRichTextForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {
            'p1': RichTextEditorWidget,
            'p2': RichTextEditorWidget,
            'p3': RichTextEditorWidget,
        }


class LegacyProductRichTextForm(forms.ModelForm):
    rich_text_fields = ('p1', 'p2', 'p3', 'p4', 'p5')

    class Meta:
        fields = '__all__'
        widgets = {
            'p1': RichTextEditorWidget,
            'p2': RichTextEditorWidget,
            'p3': RichTextEditorWidget,
            'p4': RichTextEditorWidget,
            'p5': RichTextEditorWidget,
        }


class ProductUploadInline(GenericTabularInline):
    model = ProductUpload
    extra = 3
    max_num = 100
    fields = ('title', 'file', 'alt_text', 'sort_order', 'is_active')
    verbose_name = 'Product File'
    verbose_name_plural = 'Product Files - upload up to 100 files'


class LegacyProductAdminMixin:
    def has_module_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class LegacyServiceAdminMixin(LegacyProductAdminMixin):
    pass


@admin.register(CatalogGroup)
class CatalogGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'group_type', 'slug', 'sort_order', 'item_count')
    list_display_links = ('id', 'name')
    list_editable = ('sort_order',)
    list_filter = ('group_type',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('create_time', 'update_time')
    fields = ('group_type', 'name', 'slug', 'sort_order', 'create_time', 'update_time')

    @admin.display(description='Items')
    def item_count(self, obj):
        if obj.group_type == CatalogGroup.TYPE_PRODUCT:
            return obj.products.count()
        if obj.group_type == CatalogGroup.TYPE_MODULE:
            return obj.module_services.count()
        return obj.services.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('id', 'name', 'title', 'product_group', 'show_in_catalog', 'show_on_landing', 'is_published', 'sort_order')
    list_filter = ('product_group', 'show_in_catalog', 'show_on_landing', 'is_published', 'allow_index')
    search_fields = ('name', 'title', 'short_description', 'description', 'focus_keyword', 'meta_keywords')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('create_time', 'update_time')
    fieldsets = (
        ('Product Basic Details', {
            'fields': ('user', 'product_group', 'title', 'name', 'slug', 'img', 'sort_order')
        }),
        ('Rich Product Details', {
            'fields': ('short_description', 'description')
        }),
        ('Display Controls', {
            'fields': ('show_in_catalog', 'show_on_landing', 'is_published')
        }),
        ('Product SEO', {
            'description': SEO_FIELDSET_HINT,
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'focus_keyword', 'canonical_url', 'allow_index', 'answer_summary')
        }),
        ('Tracking', {
            'fields': ('create_time', 'update_time')
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceAdminForm
    list_display = (
        'id', 'name', 'title', 'service_group', 'module_group', 'show_in_services',
        'show_on_landing', 'show_on_module_page', 'is_published', 'sort_order'
    )
    list_filter = ('service_group', 'module_group', 'show_in_services', 'show_on_landing', 'show_on_module_page', 'is_published', 'allow_index')
    search_fields = ('name', 'title', 'short_description', 'description', 'focus_keyword', 'meta_keywords')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('create_time', 'update_time')
    fieldsets = (
        ('Service Basic Details', {
            'fields': ('user', 'service_group', 'module_group', 'title', 'name', 'slug', 'img', 'image_alt', 'sort_order')
        }),
        ('Rich Service Details', {
            'fields': ('short_description', 'description')
        }),
        ('Display Controls', {
            'fields': ('show_in_services', 'show_on_landing', 'show_on_module_page', 'is_published')
        }),
        ('Service SEO', {
            'description': SEO_FIELDSET_HINT,
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'focus_keyword', 'canonical_url', 'allow_index', 'answer_summary')
        }),
        ('Tracking', {
            'fields': ('create_time', 'update_time')
        }),
    )


@admin.register(Tally_Prime_Model)
class Tally_Prime_ModelAdmin(LegacyProductAdminMixin, admin.ModelAdmin):
    form = LegacyProductRichTextForm
    inlines = [ProductUploadInline]
    list_display = ('id','name','user')


@admin.register(All_AccoutingModel)
class All_AccoutingModelAdmin(LegacyProductAdminMixin, admin.ModelAdmin):
    form = LegacyProductRichTextForm
    inlines = [ProductUploadInline]
    list_display = ('id','name','title','p1','p2','user')

#All_ERPModel
@admin.register(All_ERPModel)
class All_ERPModelAdmin(LegacyProductAdminMixin, admin.ModelAdmin):
    form = LegacyProductRichTextForm
    inlines = [ProductUploadInline]
    list_display = ('id','name','title','p1','p2','user')


#####Service Model
@admin.register(WebDevModel)
class WebDevModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','name','user')

@admin.register(Web_DesignModel)
class Web_DesignModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')

##### All Portal  Develpment Details ***********

@admin.register(Web_Portal_Dev)
class Web_Portal_DevAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')

@admin.register(MobileAppModel)
class MobileAppModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')

###### Tally  Customization
@admin.register(Tally_Customization)
class Tally_CustomizationAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')



###### Tally  Customization  Vetcal  solutions
@admin.register(Tally_VerticalModel)
class Tally_CustomizationAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','url','name','user')



@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    list_display = ['id', 'title', 'type', 'pub_date', 'is_published', 'allow_index']
    list_filter = ['is_published', 'allow_index', 'type', 'pub_date']
    search_fields = ['title', 'body', 'type', 'tags', 'focus_keyword']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['updated_at']
    fieldsets = (
        ('Blog Content', {
            'fields': ('title', 'slug', 'type', 'pub_date', 'author_name', 'image', 'alt', 'body')
        }),
        ('Blog SEO', {
            'description': SEO_FIELDSET_HINT,
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'focus_keyword', 'tags', 'canonical_url')
        }),
        ('AEO / GEO / AI Search', {
            'description': 'Write each section as a question heading followed by a direct 40-60 word answer; AI tools quote these blocks.',
            'fields': ('answer_summary',)
        }),
        ('Publishing Controls', {
            'fields': ('is_published', 'allow_index', 'updated_at')
        }),
    )


@admin.register(SiteSEO)
class SiteSEOAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_domain', 'google_analytics_id', 'google_tag_manager_id', 'robots_allow', 'updated_at']
    readonly_fields = ['updated_at', 'indexnow_key', 'indexnow_last_status']
    fieldsets = (
        ('Website Defaults', {
            'description': 'Home page title and description, and fallbacks for every other page.',
            'fields': ('site_name', 'site_domain', 'default_title', 'default_description', 'default_keywords', 'default_og_image')
        }),
        ('Analytics / Verification', {
            'fields': (
                'google_analytics_id', 'google_tag_manager_id', 'microsoft_clarity_id',
                'google_site_verification', 'bing_site_verification'
            )
        }),
        ('Local Business / Map SEO', {
            'description': 'Name, address and phone (NAP) must be identical here, in the footer, on Google Business Profile and on every directory listing.',
            'fields': (
                'organization_name', 'business_type', 'founder_name', 'founding_year', 'phone', 'email',
                'street_address', 'locality', 'region', 'postal_code', 'country', 'latitude', 'longitude',
                'google_maps_url', 'opening_hours', 'service_area', 'same_as'
            )
        }),
        ('AEO / GEO / AI Search', {
            'description': 'Shown to AI tools (ChatGPT, Claude, Perplexity, Copilot) via structured data and /llms.txt. Use plain facts.',
            'fields': ('ai_answer_summary', 'llms_summary')
        }),
        ('IndexNow (Bing / Copilot instant indexing)', {
            'description': 'When enabled, every saved product, service or blog post is reported to Bing instantly. Google does not use IndexNow.',
            'fields': ('indexnow_enabled', 'indexnow_key', 'indexnow_last_status')
        }),
        ('Crawler Controls', {
            'fields': ('robots_allow', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        if SiteSEO.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(ContactModel)
class ContactModelAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'user','title','iconcode','p1','p2','p3','type']


@admin.register(ContactIntegrationSettings)
class ContactIntegrationSettingsAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'is_enabled', 'endpoint_url', 'auth_header_name', 'last_status', 'last_sent_at')
    readonly_fields = ('last_status', 'last_response', 'last_sent_at', 'create_time', 'update_time')
    fieldsets = (
        ('Integration Control', {
            'fields': ('provider_name', 'is_enabled', 'endpoint_url')
        }),
        ('API Authentication', {
            'fields': ('api_key', 'auth_header_name', 'auth_token_prefix', 'extra_headers')
        }),
        ('Status', {
            'fields': ('timeout_seconds', 'last_status', 'last_response', 'last_sent_at', 'create_time', 'update_time')
        }),
    )

    def has_add_permission(self, request):
        if ContactIntegrationSettings.objects.exists():
            return False
        return super().has_add_permission(request)

#####################_######## Tally  On Cloud Model

@admin.register(Tally_CloudModel)
class Tally_CloudModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')

#####################_######## Tally  On Cloud Model

@admin.register(Digital_Mkt_Model)
class Tally_CloudModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')


@admin.register(Graphics_Model)
class Graphics_ModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')


@admin.register(CloudModel)
class CloudModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')


#####our News Letter Details

@admin.register(OurNewsLetter)
class OurNewsLetterAdmin(admin.ModelAdmin):
    list_display = ('id','title','name')

##about us
"""
@admin.register(AboutUSModel_Title)
class AboutUSModel_TitleAdmin(admin.ModelAdmin):
    list_display = ['id','title']
"""

@admin.register(AboutUSModel)
class AboutUSModelAdmin(admin.ModelAdmin):
    form = AboutRichTextForm
    list_display = [ 'id', 'user','p1','p2','p3']


"""
@admin.register(AboutVisionModel_Title)
class AboutVisionModel_TitleAdmin(admin.ModelAdmin):
    list_display = ['id']#['id','title']
"""
@admin.register(AboutVisionModel)
class AboutVisionModelAdmin(admin.ModelAdmin):
    form = AboutRichTextForm
    list_display = [ 'id', 'user','p1','p2','p3'] #'title'

@admin.register(PortfolioModel)
class PortfolioModelAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'user','name'] #'title'



########Landing Page Details ************

@admin.register(Lan_PageBanModel)
class Lan_PageBanModelAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'user','Slogen','Slogen2','imagalt','img']

@admin.register(Lan_AboutusModel)
class Lan_AboutusModelAdmin(admin.ModelAdmin):
    list_display = [ 'id', 'user','text1','text2','imagalt','img']


@admin.register(Lan_ProductModel)
class Lan_ProductModelAdmin(LegacyProductAdminMixin, admin.ModelAdmin):
    form = LegacyProductRichTextForm
    inlines = [ProductUploadInline]
    list_display = ('id','title','name','p1','p2','p3','p4','p5','user')


@admin.register(Lan_ServicesModel)
class Lan_ServicesModelAdmin(LegacyServiceAdminMixin, admin.ModelAdmin):
    list_display = ('id','title','name','p1','p2','user')


@admin.register(ProductUpload)
class ProductUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'product', 'file', 'sort_order', 'is_active', 'uploaded_at')
    list_filter = ('is_active', 'content_type')
    search_fields = ('title', 'alt_text', 'file')
    readonly_fields = ('uploaded_at',)

