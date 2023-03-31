from django.views import generic
from django.views.generic import ListView
from django.db import models
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from product.models import Variant
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from product.models import ProductVariantPrice, Variant, Product

class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def product_detail(request, slug):
        product = get_object_or_404(Product, slug=slug)
        variants = Variant.objects.filter(product=product, active=True).values('id', 'title').annotate(price=models.Min('prices__price'), stock=models.Sum('prices__stock'))
        return render(request, 'products/product_detail.html', {'product': product, 'variants': variants})

class EditProductView(UpdateView):
    model = Product
    template_name = 'edit_product.html'
    fields = ['title', 'sku', 'description', 'active', 'variants', 'variant_info'] # Add 'variants' to fields

    def get_success_url(self):
        return reverse_lazy('product:list.product')


class Variants(APIView):
    def get_price(self, variant):
        variant_price = ProductVariantPrice.objects.filter(variant=variant).first()
        if variant_price:
            return variant_price.price
        return None

    def get_stock(self, variant):
        variant_price = ProductVariantPrice.objects.filter(variant=variant).first()
        if variant_price:
            return variant_price.stock
        return None

    def get(self, request):
        variants = Variant.objects.filter(active=True)
        variant_list = []
        for variant in variants:
            price = self.get_price(variant)
            stock = self.get_stock(variant)
            variant_dict = {
                'id': variant.id,
                'title': variant.title,
                'price': price,
                'stock': stock,
            }
            variant_list.append(variant_dict)
        return Response(variant_list)



class ProductListView(ListView):
    template_name = 'products/list.html'
    queryset = Product.objects.all()
    paginate_by = 5  # Change this to adjust the number of items per page

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply filters based on GET parameters
        title = self.request.GET.get('title')
        variant = self.request.GET.get('variant')
        price_from = self.request.GET.get('price_from')
        price_to = self.request.GET.get('price_to')
        date = self.request.GET.get('date')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if variant:
            queryset = queryset.filter(variant=variant)
        if price_from and price_to:
            queryset = queryset.filter(price__range=(price_from, price_to))
        if date:
            queryset = queryset.filter(created_at__date=date)

        # Pass the variant value to the context
        variant_value = variant if variant else '--Select A Variant--'
        self.extra_context = {'variant': variant_value}

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.queryset, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            products = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results.
            products = paginator.page(paginator.num_pages)

        # Define the range of pages to show in the pagination
        index = products.number - 1
        max_index = len(paginator.page_range)
        start_index = index - 5 if index >= 5 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = list(paginator.page_range[start_index:end_index])

        context['products'] = products
        context['product_list'] = products  # Add the paginator object to the context
        context['products_start'] = (products.number - 1) * self.paginate_by + 1  # Define products_start
        context['products_end'] = min(products.number * self.paginate_by, paginator.count)  # Define products_end
        context['page_num'] = int(page) if page else 1  # Add page_num to the context
        context['page_range'] = page_range  # Add page_range to the context

        return context