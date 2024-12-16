from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db.models import Q, Prefetch
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.core.validators import validate_email
from django_ratelimit.decorators import ratelimit
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review, FarmerProfile, CustomerProfile
from .forms import (
    CustomUserCreationForm, CustomerProfileForm, ReviewForm, 
    ProductSearchForm, ProductForm
)
from .notifications import send_order_confirmation_email, send_order_confirmation_sms
from decimal import Decimal

def is_farmer(user):
    return hasattr(user, 'farmerprofile')

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'store/account/register.html'
    success_url = reverse_lazy('store:login')

    @method_decorator(csrf_protect)
    @method_decorator(ratelimit(key='ip', rate='5/h', method=['POST']))
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                profile = self.object.customerprofile
                
                # Validation des données
                try:
                    validate_email(form.cleaned_data['email'])
                except ValidationError:
                    raise ValidationError('Email invalide')

                profile.phone = form.cleaned_data['phone']
                profile.address = form.cleaned_data['address']
                profile.region = form.cleaned_data['region']
                profile.save()

                # Envoyer un email de bienvenue de manière asynchrone
                transaction.on_commit(lambda: send_mail(
                    'Bienvenue sur BIO Recolte !',
                    f'Bonjour {self.object.first_name},\n\n'
                    'Merci de vous être inscrit sur BIO Recolte. '
                    'Votre compte a été créé avec succès.\n\n'
                    'Vous pouvez maintenant vous connecter et commencer à explorer '
                    'notre sélection de produits agricoles frais et locaux.\n\n'
                    'À bientôt sur BIO Recolte !',
                    settings.DEFAULT_FROM_EMAIL,
                    [self.object.email],
                    fail_silently=True,
                ))

                messages.success(
                    self.request,
                    'Votre compte a été créé avec succès ! Un email de confirmation '
                    'vous a été envoyé. Vous pouvez maintenant vous connecter.'
                )
                return response

        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(
                self.request,
                'Une erreur est survenue lors de la création de votre compte. '
                'Veuillez réessayer ou contacter le support si le problème persiste.'
            )
            return self.form_invalid(form)

@login_required
def profile(request):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    orders = Order.objects.filter(user=request.user).order_by('-created')[:5]
    
    context = {
        'profile': customer_profile,
        'recent_orders': orders,
    }
    return render(request, 'store/account/profile.html', context)

@login_required
def edit_profile(request):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    
    if request.method == 'POST':
        profile_form = CustomerProfileForm(request.POST, request.FILES, instance=customer_profile)
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('store:profile')
        else:
            messages.error(request, 'Erreur lors de la mise à jour du profil. Veuillez corriger les erreurs.')
    else:
        profile_form = CustomerProfileForm(instance=customer_profile)
    
    return render(request, 'store/account/edit_profile.html', {
        'profile_form': profile_form,
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'store/account/my_orders.html', {'orders': orders})

@login_required
@cache_page(60 * 15)  # Cache pour 15 minutes
def product_list(request, category_slug=None):
    cache_key = f'product_list_{category_slug}_{request.user.id}'
    products = cache.get(cache_key)
    
    if products is None:
        products = Product.objects.select_related('category', 'farmer')\
            .prefetch_related('reviews')\
            .filter(available=True)
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
            
        form = ProductSearchForm(request.GET)
        if form.is_valid() and form.cleaned_data.get('query'):
            query = form.cleaned_data['query']
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )
            
        cache.set(cache_key, products, 60 * 15)  # Cache pour 15 minutes
    
    context = {
        'products': products,
        'form': ProductSearchForm(),
    }
    return render(request, 'store/product/list.html', context)

@login_required
@cache_page(60 * 15)  # Cache pour 15 minutes
def category_list(request):
    categories = Category.objects.select_related('parent')\
        .prefetch_related('children', 'products')\
        .filter(parent=None)  # Récupérer uniquement les catégories parentes
    
    # Récupérer le panier de l'utilisateur
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = []
    if cart:
        cart_items = cart.items.select_related('product').all()
    
    context = {
        'categories': categories,
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/category/list.html', context)

@login_required
@cache_page(60 * 5)  # Cache pour 5 minutes
def product_detail(request, id, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'farmer')
        .prefetch_related(
            Prefetch('reviews', queryset=Review.objects.select_related('user'))
        ),
        id=id,
        slug=slug,
        available=True
    )
    
    context = {
        'product': product,
        'reviews': product.reviews.all(),
        'review_form': ReviewForm(),
    }
    return render(request, 'store/product/detail.html', context)

@login_required
@require_http_methods(["GET"])
def cart_detail(request):
    cart = Cart.objects.prefetch_related(
        Prefetch('items', queryset=CartItem.objects.select_related('product'))
    ).get_or_create(user=request.user)[0]
    
    return render(request, 'store/cart/detail.html', {'cart': cart})

@login_required
@require_http_methods(["POST"])
@csrf_protect
@ratelimit(key='user', rate='30/m')
def cart_add(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id, available=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            raise ValidationError('La quantité doit être positive')
            
        if quantity > product.stock:
            raise ValidationError('Stock insuffisant')
        
        cart = Cart.objects.get_or_create(user=request.user)[0]
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        messages.success(request, 'Produit ajouté au panier avec succès')
        
    except (ValueError, ValidationError) as e:
        messages.error(request, str(e))
    
    return redirect('store:cart_detail')

@login_required
@require_http_methods(["POST"])
@csrf_protect
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Le produit a été retiré de votre panier.')
    return redirect('store:cart_detail')

@login_required
@require_http_methods(["POST"])
@csrf_protect
def cart_update(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('store:cart_detail')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    # Vérification des stocks avant la commande
    stock_issues = []
    for item in cart_items:
        if item.quantity > item.product.stock:
            stock_issues.append(f"{item.product.name} - Stock insuffisant (Disponible: {item.product.stock})")
    
    if stock_issues:
        for issue in stock_issues:
            messages.error(request, issue)
        return redirect('store:cart_detail')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Création de la commande
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=request.POST['address'],
                    shipping_name=request.user.get_full_name() or request.user.username,
                    shipping_city=request.POST.get('city', ''),
                    shipping_region=request.POST.get('region', request.user.customerprofile.region),
                    phone=request.POST['phone'],
                    email=request.user.email,
                    payment_method=request.POST.get('payment_method', 'CASH'),
                    delivery_method=request.POST.get('delivery_method', 'HOME'),
                    subtotal=cart.get_total_price(),
                    delivery_fee=Decimal('2000'),  # Frais de livraison fixe pour l'instant
                    total=cart.get_total_price() + Decimal('2000'),  # Total = sous-total + frais de livraison
                    status='PENDING',
                    payment_status='PENDING'
                )
                
                # Validation du numéro de téléphone
                try:
                    order.clean_phone()
                except ValidationError as e:
                    messages.error(request, str(e))
                    order.delete()
                    return redirect('store:checkout')
                
                # Création des items de commande et mise à jour des stocks
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price,
                        quantity=item.quantity
                    )
                    # Mise à jour du stock
                    product = item.product
                    product.stock -= item.quantity
                    product.save()
                
                # Envoi des notifications
                try:
                    send_order_confirmation_email(order)
                    send_order_confirmation_sms(order)
                except Exception as e:
                    # Log l'erreur mais continue le processus
                    print(f"Erreur d'envoi de notification: {str(e)}")
                
                # Vider le panier
                cart.items.all().delete()
                
                messages.success(request, 'Votre commande a été créée avec succès!')
                return redirect('store:order_detail', order_id=order.id)
                
        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors de la création de votre commande: {str(e)}")
            return redirect('store:checkout')
            
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_detail(request, order_id):
    # Récupérer la commande avec ses items
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), id=order_id)
    
    # Vérifier que l'utilisateur a le droit de voir cette commande
    if not request.user.is_superuser and order.user != request.user:
        if not order.items.filter(product__farmer=request.user).exists():
            raise PermissionDenied
    
    context = {
        'order': order,
        'items': order.items.all(),
        'page_title': f'Commande #{order.id}',
        'can_cancel': order.can_cancel(),
    }
    
    return render(request, 'store/order_detail.html', context)

@login_required
def order_list(request):
    # Pour les superusers, montrer toutes les commandes
    if request.user.is_superuser:
        orders = Order.objects.all()
    else:
        # Pour les agriculteurs, montrer les commandes contenant leurs produits
        if hasattr(request.user, 'farmer_profile'):
            orders = Order.objects.filter(items__product__farmer=request.user).distinct()
        # Pour les clients normaux, montrer leurs propres commandes
        else:
            orders = Order.objects.filter(user=request.user)
    
    orders = orders.prefetch_related('items__product').order_by('-created')
    
    context = {
        'orders': orders,
        'page_title': 'Mes Commandes',
    }
    
    return render(request, 'store/order_list.html', context)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que l'utilisateur a le droit d'annuler cette commande
    if not request.user.is_superuser and order.user != request.user:
        raise PermissionDenied
    
    # Vérifier que la commande peut être annulée
    if not order.can_cancel():
        messages.error(request, "Cette commande ne peut plus être annulée.")
        return redirect('store:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        order.status = 'CANCELLED'
        order.save()
        order.send_status_update_email()
        messages.success(request, "La commande a été annulée avec succès.")
        return redirect('store:order_list')
    
    context = {
        'order': order,
        'page_title': f'Annuler la commande #{order.id}',
    }
    
    return render(request, 'store/order_cancel.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'Vous avez déjà donné votre avis sur ce produit.')
        return redirect('store:product_detail', id=product.id, slug=product.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Merci pour votre avis!')
            return redirect('store:product_detail', id=product.id, slug=product.slug)
    else:
        form = ReviewForm()
    
    return render(request, 'store/product/review.html', {
        'form': form,
        'product': product
    })

@login_required
@user_passes_test(is_farmer)
@csrf_protect
def manage_product(request, product_id=None):
    if product_id:
        product = get_object_or_404(
            Product.objects.select_related('category'),
            id=product_id,
            farmer=request.user.farmerprofile
        )
    else:
        product = None
        
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.farmer = request.user.farmerprofile
                
                # Validation supplémentaire
                if product.price <= 0:
                    raise ValidationError('Le prix doit être positif')
                if product.stock < 0:
                    raise ValidationError('Le stock ne peut pas être négatif')
                
                product.save()
                messages.success(request, 'Produit sauvegardé avec succès')
                return redirect('store:farmer_dashboard')
                
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'store/farmer/manage_product.html', {'form': form})

@login_required
@user_passes_test(is_farmer)
def farmer_dashboard(request):
    if not hasattr(request.user, 'farmerprofile'):
        return redirect('store:become_farmer')
    
    products = Product.objects.filter(farmer=request.user)
    orders = OrderItem.objects.filter(product__farmer=request.user).select_related('order')
    
    # Statistiques
    total_sales = request.user.farmerprofile.total_sales
    total_orders = orders.count()
    total_products = products.count()
    
    context = {
        'products': products,
        'orders': orders,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_products': total_products,
    }
    return render(request, 'store/farmer/dashboard.html', context)

@login_required
def become_farmer(request):
    if hasattr(request.user, 'farmerprofile'):
        return redirect('store:farmer_dashboard')
    
    if request.method == 'POST':
        description = request.POST.get('description')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        profile_image = request.FILES.get('profile_image')
        
        FarmerProfile.objects.create(
            user=request.user,
            description=description,
            address=address,
            phone=phone,
            profile_image=profile_image
        )
        
        messages.success(request, 'Vous êtes maintenant un agriculteur!')
        return redirect('store:farmer_dashboard')
    
    return render(request, 'store/farmer/become_farmer.html')

def home(request):
    products = Product.objects.filter(available=True)[:6]  # Limiter à 6 produits sur la page d'accueil
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories
    })

def about(request):
    return render(request, 'store/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Envoyer l'email
        send_mail(
            f'Contact de {name}',
            message,
            email,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        messages.success(request, 'Votre message a été envoyé avec succès !')
        return redirect('store:contact')
        
    return render(request, 'store/contact.html')

def terms(request):
    """Vue pour les conditions d'utilisation"""
    return render(request, 'store/legal/terms.html')

def privacy(request):
    """Vue pour la politique de confidentialité"""
    return render(request, 'store/legal/privacy.html')
