from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from manager.models import *


class StockView(TemplateView):
    template_name = "stock_list.html"

    def get(self, request, *args, **kwargs):
        context = super(StockView, self).get_context_data(**kwargs)
        stocks = Stock.objects.all()
        context['stocks'] = stocks
        
        return render(self.request, self.template_name, context)
        
        
        