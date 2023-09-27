from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy, reverse
from django.conf import settings
from django.http import Http404
import stripe

from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    TemplateView,
    DeleteView,
    UpdateView,
)

from .models import (
    Genre,
    Product,
    Like,
    ProductImage,
    Address,
    Payment,
    Order,
    Notification,
)

from .forms import (
    CustomProductImageFormSet,
    PaymentForm,
    ProductSearchForm,
    ProductSellForm,
    AddressForm,
    AccountUpdateForm,
)

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    template_name = "main/home.html"
    model = Product
    context_object_name = "items"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (
            queryset.exclude(exhibitor=self.request.user)
            .filter(sales_status="on_display")
            .prefetch_related("product_images")
            .order_by("-uploaded_at")[:6]
        )
        genre = self.request.GET.get("genre")
        if genre:
            queryset = queryset.filter(genre__name=genre)
        search_form = ProductSearchForm(self.request.GET)
        if search_form.is_valid():
            keyword = search_form.cleaned_data["keyword"]
            if keyword:
                keywords = keyword.split()
                for k in keywords:
                    queryset = queryset.filter(name__icontains=k)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["genres"] = Genre.objects.all()
        return context
    
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = "items"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related("product_images").order_by("-uploaded_at")
        genre = self.request.GET.get("genre")
        if genre:
            queryset = queryset.filter(genre__name=genre)
        return queryset

@require_POST
def product_like(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Like.objects.create(user=request.user, product=product)
    return redirect("main:product_detail", pk)


@require_POST
def product_unlike(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Like.objects.filter(user=request.user, product=product).delete()
    return redirect("main:product_detail", pk)

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    context_object_name = "item"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("exhibitor", "genre").annotate(
            likes_count=Count("likes_received"),
            is_liked=Exists(
                Like.objects.filter(user=self.request.user, product=OuterRef("pk"))
            ),
        )
        return queryset
    
@login_required
def product_sell(request):
    if request.method == "GET":
        product_image_formset = CustomProductImageFormSet(
            queryset=ProductImage.objects.none()
        )
        product_sell_form = ProductSellForm()
    elif request.method == "POST":
        product_image_formset = CustomProductImageFormSet(
            request.POST,
            request.FILES,
        )
        product_sell_form = ProductSellForm(request.POST)
        if product_image_formset.is_valid() and product_sell_form.is_valid():
            new_product = product_sell_form.save(commit=False)
            new_product.exhibitor = request.user
            new_product.sales_status = "on_display"
            new_product.save()
            new_product_images = product_image_formset.save(commit=False)
            for new_product_image in new_product_images:
                if new_product_image.image:
                    new_product_image.product = new_product
                    new_product_image.save()
            return redirect("main:home")
    context = {
        "image_form": product_image_formset,
        "text_form": product_sell_form,
    }
    return render(request, "main/product_sell.html", context)

class PurchaseConfirmationView(LoginRequiredMixin, FormView):
    template_name = "main/purchase_confirmation.html"
    form_class = PaymentForm
    success_url = reverse_lazy("main:address")

    def dispatch(self, request, *args, **kwargs):
        self.item = get_object_or_404(
            Product.objects.prefetch_related("product_images"), pk=self.kwargs["pk"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item"] = self.item
        return context

    def form_valid(self, form):
        self.request.session["item_pk_info"] = self.kwargs["pk"]
        self.request.session["purchase_info"] = form.cleaned_data
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["price"] = self.item.value
        return kwargs

class InputAddressView(LoginRequiredMixin, FormView):
    template_name = "main/input_address.html"
    form_class = AddressForm
    success_url = reverse_lazy("main:payment")

    def dispatch(self, request, *args, **kwargs):
        if "purchase_info" not in request.session or "item_pk_info" not in request.session:
            return redirect("main:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session["address_info"] = form.cleaned_data
        return super().form_valid(form)

class InputPaymentView(LoginRequiredMixin, TemplateView):
    template_name = "main/input_payment.html"

    def dispatch(self, request, *args, **kwargs):
        if "address_info" not in request.session:
            return redirect("main:address")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item_pk = self.request.session["item_pk_info"]
        item = get_object_or_404(
            Product.objects.prefetch_related("product_images"), pk=item_pk
        )
        context["item"] = item
        context["STRIPE_PUBLISHABLE_KEY"] = settings.STRIPE_PUBLISHABLE_KEY
        return context

    def post(self, request, *args, **kwargs):
        if "stripeToken" not in self.request.POST:
            return render(
                request,
                "main/input_payment.html",
                {"message": "正しく処理されませんでした。もう一度入力してください。"},
            )
        else:
            self.request.session["card_info"] = request.POST["stripeToken"]
            return redirect("main:final_confirmation")

class CreateCheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "main/final_confirmation.html"

    def dispatch(self, request, *args, **kwargs):
        if "card_info" not in request.session:
            return redirect("main:payment")
        self.item_pk = self.request.session["item_pk_info"]
        self.purchase_info = self.request.session["purchase_info"]
        self.address_info = self.request.session["address_info"]
        self.stripe_token = self.request.session["card_info"]
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = get_object_or_404(
            Product.objects.prefetch_related("product_images"), pk=self.item_pk
        )
        context["item"] = item
        context["purchase"] = self.purchase_info
        context["address"] = self.address_info
        return context

    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY
        price = self.purchase_info["total_amount"]
        try:
            charge = stripe.Charge.create(
                amount=int(price),
                currency="jpy",
                source=self.stripe_token,
                description="FreeMa",
            )
        except stripe.error.CardError:
            return render(
                request,
                "main/error.html",
                {"message": "決済に失敗しました。"},
            )
        # データベースの保存
        # Aderess
        address = Address.objects.create(
            first_name=self.address_info["first_name"],
            last_name=self.address_info["last_name"],
            first_name_kana=self.address_info["first_name_kana"],
            last_name_kana=self.address_info["last_name_kana"],
            postal_code=self.address_info["postal_code"],
            prefecture=self.address_info["prefecture"],
            address=self.address_info["address"],
            tel=self.address_info["tel"],
        )
        # Payment
        payment = Payment.objects.create(
            user=request.user, stripe_charge_id=charge["id"]
        )
        # Order
        # 商品履歴の作成
        product = get_object_or_404(Product, pk=self.item_pk)
        order = Order.objects.create(
            product=product,
            price=price,
            purchaser=request.user,
            delivery_status="before_shipping",
            address=address,
            payment=payment,
        )
        # 購入済みにする
        product.sales_status = "sold"
        product.save()
        # ポイントの付与と削除
        # 購入者のポイントを削除
        request.user.point -= int(self.request.session["purchase_info"]["point"])
        request.user.save()
        # 出品者にポイントを付与
        exhibitor = product.exhibitor
        point = product.value - int(product.value * 0.1)
        exhibitor.point += point
        exhibitor.save()
        # 出品者に対する通知の生成
        Notification.objects.create(user=exhibitor, order=order, is_action=True)
        # セッションの削除
        del self.request.session["item_pk_info"]
        del self.request.session["purchase_info"]
        del self.request.session["address_info"]
        del self.request.session["card_info"]
        return redirect("main:product_detail", self.item_pk)

@require_POST
def change_delivery_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.delivery_status == "before_shipping":
        order.delivery_status = "shipped"
        order.save()
        # 購入者に対する通知の作成
        purchaser = order.purchaser
        Notification.objects.create(user=purchaser, order=order, is_action=False)
    elif order.delivery_status == "shipped":
        order.delivery_status = "delivered"
        order.save()
    return redirect("main:product_detail", order.product.pk)

@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, exhibitor=request.user)
    product.delete()
    return redirect("main:home")

class AccountView(LoginRequiredMixin, DetailView):
    template_name = "main/account.html"
    model = User

    def get_object(self):
        return self.request.user

class TermsView(TemplateView):
    template_name = "main/terms.html"

class PrivacyPolicyView(TemplateView):
    template_name = "main/privacy_policy.html"

class AccountDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "main/account_delete.html"
    model = User
    success_url = reverse_lazy("main:account_delete_done")

    def get_object(self):
        return self.request.user

class AccountDeleteDoneView(TemplateView):
    template_name = "main/account_delete_done.html"

class AccountDetailView(LoginRequiredMixin, DetailView):
    template_name = "main/account_detail.html"
    model = User

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
            "products_exhibited__product_images"
        ).annotate(products_count=Count("products_exhibited"))
        return queryset
    
class ProductLikedListView(LoginRequiredMixin, ListView):
    template_name = "main/product_liked_list.html"
    model = Product
    context_object_name = "liked_products"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            likes_received__user=self.request.user
        ).prefetch_related("product_images")
        return queryset

class ProductExibitListView(LoginRequiredMixin, ListView):
    template_name = "main/product_exhibited_list.html"
    model = Product
    context_object_name = "exhibited_products"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(exhibitor=self.request.user).prefetch_related("product_images").order_by("-uploaded_at")
        if "salesStatus" in self.request.GET:
            sales_status = self.request.GET["salesStatus"]
            if sales_status:
                if sales_status == "all":
                    queryset = queryset
                elif sales_status == "on_display":
                    queryset = queryset.filter(sales_status="on_display")
                elif sales_status == "sold":
                    queryset = queryset.filter(sales_status="sold")
                else:
                    raise Http404
        return queryset

class ProductPurchasedListView(LoginRequiredMixin, ListView):
    template_name = "main/product_purchased_list.html"
    model = Product
    context_object_name = "purchased_products"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (
            queryset.filter(orders_received__purchaser=self.request.user)
            .prefetch_related("product_images")
            .order_by("-uploaded_at")
        )
        if "delivery_status" in self.request.GET:
            delivery_status = self.request.GET["delivery_status"]
            if delivery_status:
                if delivery_status == "before_shipping":
                    queryset = queryset.filter(
                        orders_received__delivery_status="before_shipping"
                    )
                elif delivery_status == "other":
                    queryset = queryset.exclude(
                        orders_received__delivery_status="before_shipping"
                    )
                else:
                    raise Http404
        else:
            queryset = queryset.filter(
                orders_received__delivery_status="before_shipping"
            )
        return queryset    

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = AccountUpdateForm
    template_name = "main/account_update.html"

    def get_success_url(self):
        return reverse("main:account_detail", kwargs={"pk": self.request.user.pk})

    def get_object(self):
        return self.request.user

class NotificationView(LoginRequiredMixin, ListView):
    template_name = "main/notification.html"
    model = Notification
    context_object_name = "notifications"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = (
            queryset.filter(user=self.request.user, is_action=True)
            .select_related("order__product")
            .prefetch_related("order__product__product_images")
            .order_by("-created_at")
        )
        is_action = self.request.GET.get("isAction")
        if is_action:
            if is_action == "true":
                queryset = queryset.filter(is_action=True)
            elif is_action == "false":
                queryset = queryset.filter(is_action=False)
            else:
                return Http404
        else:
            queryset = queryset.filter(is_action=True)
        print(queryset)
        return queryset

