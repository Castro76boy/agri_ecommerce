from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomerProfile, Review, Product

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        help_text='Requis. Entrez une adresse email valide.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Requis. Entrez votre prénom.'
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Requis. Entrez votre nom.'
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        help_text='Requis. Format: 2XXXXXXXX ou 5XXXXXXXX ou 6XXXXXXXX ou 7XXXXXXXX'
    )
    address = forms.CharField(
        max_length=255,
        required=True,
        help_text='Requis. Entrez votre adresse complète.'
    )
    region = forms.ChoiceField(
        choices=CustomerProfile.REGION_CHOICES,
        required=True,
        help_text='Requis. Sélectionnez votre région.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'phone', 'address', 'region', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = 'Requis. 150 caractères maximum. Lettres, chiffres et @/./+/-/_ uniquement.'
        self.fields['password1'].help_text = '''
            <ul>
                <li>Votre mot de passe doit contenir au moins 8 caractères.</li>
                <li>Votre mot de passe ne peut pas être trop similaire à vos autres informations personnelles.</li>
                <li>Votre mot de passe doit contenir au moins une lettre majuscule et une lettre minuscule.</li>
                <li>Votre mot de passe doit contenir au moins un chiffre.</li>
            </ul>
        '''

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        if not re.match(r'^[2567]\d{7}$', phone):
            raise forms.ValidationError(
                "Le numéro de téléphone doit être un numéro malien valide "
                "(8 chiffres commençant par 2, 5, 6 ou 7)"
            )
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Mettre à jour le profil client
            profile = user.customerprofile
            profile.phone = self.cleaned_data['phone']
            profile.address = self.cleaned_data['address']
            profile.region = self.cleaned_data['region']
            profile.save()
        return user

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address', 'region', 'profile_image', 'birth_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class ProductSearchForm(forms.Form):
    query = forms.CharField(required=False)
    category = forms.IntegerField(required=False)
    min_price = forms.DecimalField(required=False)
    max_price = forms.DecimalField(required=False)
    region = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].choices = [('', '---')] + [(c.id, c.name) for c in Category.objects.all()]
        self.fields['region'].choices = [('', '---')] + CustomerProfile.REGION_CHOICES

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock', 'image', 
                 'available', 'tags', 'promotion', 'unit', 'minimum_order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Le prix doit être positif")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError("Le stock ne peut pas être négatif")
        return stock

    def clean_minimum_order(self):
        min_order = self.cleaned_data.get('minimum_order')
        if min_order < 1:
            raise forms.ValidationError("La quantité minimum doit être d'au moins 1")
        return min_order
