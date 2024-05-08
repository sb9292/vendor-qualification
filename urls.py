"""
URL configuration for vendorproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
from django.urls import path
from myapp import views
from myapp.views import VendorApi, PurchaseOrderApi, HistoricalPerformanceApi, vendor_performance_metrics


urlpatterns = [
    path('vendors/', VendorApi.as_view(), name='vendor-list-create'),
    path('purchase_orders/', PurchaseOrderApi.as_view(), name='purchase-order-list-create'),
    path('historical_performances/', HistoricalPerformanceApi.as_view(), name='historical-performance-list-create'),
    path('vendors/<int:vendor_id>/performance/', vendor_performance_metrics, name='vendor-performance-metrics'),

]

