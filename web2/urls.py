from django.urls import path
from web2 import views

urlpatterns = [

    ###project url details

    path('wbase', views.wbase, name='wbase'),

    #product Details here

    path('web_product', views.web_product, name='web_product'),
    path('product/<slug:group>/<int:id>/', views.product_detail, name='product_detail'),
    path('service/<slug:group>/<int:id>/', views.service_detail, name='service_detail'),
    path('allaccounting_software', views.allaccounting_software, name='allaccounting_software'),
    path('allerp_software', views.allerp_software, name='allerp_software'),



    ##blog
    path('homeblog', views.homeblog, name='homeblog'),
    path('blog/<slug:slug>/', views.blog_single, name='blog_detail'),
    path('blog_single/<int:id>/', views.blog_single, name='blog_single'),
    ##contact page

    path('contact', views.contact, name='contact'),
    path('contact_email', views.contact_email, name='contact_email'),

    ####service tage
    path('web_dev', views.web_dev, name='web_dev'),
    path('web_design', views.web_design, name='web_design'),
    path('web_port_dev', views.web_port_dev, name='web_port_dev'),
    path('mob_appdev', views.mob_appdev, name='mob_appdev'),
    path('tally_customization', views.tally_customization, name='tally_customization'),
    path('tally_ver_Solutions', views.tally_ver_Solutions, name='tally_ver_Solutions'),
    path('tally_cloud', views.tally_cloud, name='tally_cloud'),
    path('digi_mkt', views.digi_mkt, name='digi_mkt'),
    path('graphics_design', views.graphics_design, name='graphics_design'),
    path('cloud_services', views.cloud_services, name='cloud_services'),
    path('our_module_services', views.our_module_services, name='our_module_services'),



    ###about  us Who  We are
    path('aboutus', views.aboutus, name='aboutus'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('news_letter', views.news_letter, name='news_letter'),



]

