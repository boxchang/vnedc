# context_processors.py
from warehouse.forms import BinValueForm
from .models import Warehouse

def warehouse_items(request):
    return {
        'warehouse_items': Warehouse.objects.all()
    }

