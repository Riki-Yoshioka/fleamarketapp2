from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Product, ProductImage, Address
import re

User = get_user_model()


class ProductSearchForm(forms.Form):
    keyword = forms.CharField(
        label="検索",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "商品を検索"}),
    )

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ("image",)
        labels = {"image": ""}


ProductImageFormSet = forms.modelformset_factory(
    ProductImage,
    form=ProductImageForm,
    extra=5,
)


class ProductSellForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "genre",
            "product_status",
            "name",
            "explanation",
            "value",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "商品名",
                    "onkeyup": "showNameLength(value);",
                }
            ),
            "explanation": forms.Textarea(
                attrs={
                    "placeholder": "商品の説明",
                    "onkeyup": "showExplanationLength(value);",
                }
            ),
            "value": forms.NumberInput(
                attrs={"placeholder": "販売価格（¥）"}
            ),
        }

class CustomProductImageFormSet(ProductImageFormSet):
    def clean(self):
        super().clean()
        has_image = False
        for form in self.forms:
            if form.cleaned_data.get("image"):
                has_image = True
                break
        if not has_image:
            raise ValidationError("1枚以上の画像を選択してください。")
        
class PaymentForm(forms.Form):
    def __init__(self, price=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = price
        self.fields["total_amount"].initial = self.price

    point = forms.IntegerField(widget=forms.HiddenInput(attrs={"value": "0"}))
    total_amount = forms.IntegerField(widget=forms.HiddenInput())

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            "last_name",
            "first_name",
            "last_name_kana",
            "first_name_kana",
            "postal_code",
            "prefecture",
            "address",
            "tel",
        )
        widgets = {
            "last_name": forms.TextInput(attrs={"placeholder": "姓"}),
            "first_name": forms.TextInput(attrs={"placeholder": "名"}),
            "last_name_kana": forms.TextInput(attrs={"placeholder": "姓カナ"}),
            "first_name_kana": forms.TextInput(attrs={"placeholder": "名カナ"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "郵便番号（数字）"}),
            "prefecture": forms.Select(attrs={"placeholder": "都道府県"}),
            "address": forms.TextInput(attrs={"placeholder": "住所"}),
            "tel": forms.TextInput(attrs={"placeholder": "電話番号"}),
        }

    def clean_first_name_kana(self):
        first_name_kana = self.cleaned_data["first_name_kana"]
        if not re.match(r"^[ァ-ヴー]*$", first_name_kana):
            raise ValidationError("カタカナのみ入力してください。")
        return first_name_kana

    def clean_last_name_kana(self):
        last_name_kana = self.cleaned_data["last_name_kana"]
        if not re.match(r"^[ァ-ヴー]*$", last_name_kana):
            raise ValidationError("カタカナのみ入力してください。")
        return last_name_kana

    def clean_postal_code(self):
        postal_code = self.cleaned_data["postal_code"]
        if len(postal_code) != 7 or not postal_code.isdigit():
            raise ValidationError("郵便番号には7桁の数字を入力してください。")
        return postal_code

    def clean_tel(self):
        tel = self.cleaned_data["tel"]
        if not (10 <= len(tel) <= 11) or not tel.isdigit():
            raise ValidationError("電話番号には10桁または11桁の数字を入力してください。")
        return tel

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("icon", "username", "profile")
        labels = {
            "username": "ユーザー名",
            "profile": "紹介文",
        }
        widgets = {
            "icon": forms.FileInput(attrs={"onchange": "previewImage(this);"}),
            "username": forms.TextInput(attrs={"onkeyup": "showUsernameLength(value);"}),
            "profile": forms.Textarea(attrs={"onkeyup": "showProfileLength(value);"}),
        }



