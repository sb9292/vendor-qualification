# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from myapp.models import Vendor, PurchaseOrder, HistoricalPerformance
from myapp.serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer
from rest_framework.response import Response
from django.db.models import Avg, F

from rest_framework import generics

class VendorApi(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

class PurchaseOrderApi(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

class HistoricalPerformanceApi(generics.ListCreateAPIView):
    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer


def calculate_on_time_delivery_rate(vendor):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
    total_completed_orders = completed_orders.count()
    on_time_delivered_orders = completed_orders.filter(delivery_date__lte=F('acknowledgment_date')).count()
    return (on_time_delivered_orders / total_completed_orders) * 100 if total_completed_orders > 0 else 0

def calculate_quality_rating_avg(vendor):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed').exclude(quality_rating__isnull=True)
    return completed_orders.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0

def calculate_average_response_time(vendor):
    completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed').exclude(acknowledgment_date__isnull=True)
    
    response_times = []
    for po in completed_orders:
        response_time = (po.acknowledgment_date - po.issue_date).total_seconds()
        response_times.append(response_time)
    
    return sum(response_times) / len(response_times) if len(response_times) > 0 else 0


def calculate_fulfillment_rate(vendor):
    total_orders = PurchaseOrder.objects.filter(vendor=vendor).count()
    fulfilled_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed').exclude(quality_rating__isnull=False).count()
    return (fulfilled_orders / total_orders) * 100 if total_orders > 0 else 0


@api_view(['GET'])
def vendor_performance_metrics(request, vendor_id):
    try:
        vendor = Vendor.objects.get(id=vendor_id)
    except Vendor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    on_time_delivery_rate = calculate_on_time_delivery_rate(vendor)
    quality_rating_average = calculate_quality_rating_avg(vendor)
    average_response_time = calculate_average_response_time(vendor)
    fulfilment_rate = calculate_fulfillment_rate(vendor)

    # Create or update HistoricalPerformance object
    historical_performance, _ = HistoricalPerformance.objects.get_or_create(vendor=vendor)
    historical_performance.on_time_delivery_rate = on_time_delivery_rate
    historical_performance.quality_rating_average = quality_rating_average
    historical_performance.average_response_time = average_response_time
    historical_performance.fulfilment_rate = fulfilment_rate
    historical_performance.save()

    serializer = HistoricalPerformanceSerializer(historical_performance)
    return Response(serializer.data)
