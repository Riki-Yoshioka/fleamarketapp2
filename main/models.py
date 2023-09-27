from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Genre(models.Model):
    name = models.CharField(max_length=20)
    image = models.ImageField(
        upload_to="genre_image/",
        blank=True,
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    SALES_STATUS_CHOICES = [
        ("on_display", "出品中"),
        ("sold", "売却済"),
    ]
    PRODUCT_STATUS_CHOICES = [
        ("new", "新品、未使用"),
        ("almost_new", "未使用に近い"),
        ("little_blemish", "目立った傷や汚れなし"),
        ("a_little_blemish", "やや傷や汚れあり"),
        ("some_blemish", "傷や汚れあり"),
        ("bad", "全体的に状態が悪い"),
    ]
    exhibitor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products_exhibited"
    )
    name = models.CharField(max_length=30)
    explanation = models.TextField(max_length=500)
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    product_status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES)
    sales_status = models.CharField(max_length=20, choices=SALES_STATUS_CHOICES)
    value = models.IntegerField(validators=[MinValueValidator(300), MaxValueValidator(999999)])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"商品名:{self.name},出品者:{self.exhibitor}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_images"
    )
    image = models.ImageField(
        upload_to="product_image/",
        blank=True,
    )

    def __str__(self):
        return f"{self.image}"


class Address(models.Model):
    PREFECTURES = (
        ("北海道", "北海道"),
        ("青森県", "青森県"),
        ("岩手県", "岩手県"),
        ("宮城県", "宮城県"),
        ("秋田県", "秋田県"),
        ("山形県", "山形県"),
        ("福島県", "福島県"),
        ("茨城県", "茨城県"),
        ("栃木県", "栃木県"),
        ("群馬県", "群馬県"),
        ("埼玉県", "埼玉県"),
        ("千葉県", "千葉県"),
        ("東京都", "東京都"),
        ("神奈川県", "神奈川県"),
        ("新潟県", "新潟県"),
        ("富山県", "富山県"),
        ("石川県", "石川県"),
        ("福井県", "福井県"),
        ("山梨県", "山梨県"),
        ("長野県", "長野県"),
        ("岐阜県", "岐阜県"),
        ("静岡県", "静岡県"),
        ("愛知県", "愛知県"),
        ("三重県", "三重県"),
        ("滋賀県", "滋賀県"),
        ("京都府", "京都府"),
        ("大阪府", "大阪府"),
        ("兵庫県", "兵庫県"),
        ("奈良県", "奈良県"),
        ("和歌山県", "和歌山県"),
        ("鳥取県", "鳥取県"),
        ("島根県", "島根県"),
        ("岡山県", "岡山県"),
        ("広島県", "広島県"),
        ("山口県", "山口県"),
        ("徳島県", "徳島県"),
        ("香川県", "香川県"),
        ("愛媛県", "愛媛県"),
        ("高知県", "高知県"),
        ("福岡県", "福岡県"),
        ("佐賀県", "佐賀県"),
        ("長崎県", "長崎県"),
        ("熊本県", "熊本県"),
        ("大分県", "大分県"),
        ("宮崎県", "宮崎県"),
        ("鹿児島県", "鹿児島県"),
        ("沖縄県", "沖縄県"),
    )
    first_name = models.CharField(max_length=10)
    last_name = models.CharField(max_length=10)
    first_name_kana = models.CharField(max_length=20)
    last_name_kana = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=7)
    prefecture = models.CharField(max_length=4, choices=PREFECTURES)
    address = models.CharField(max_length=255)
    tel = models.CharField(max_length=11)


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    stripe_charge_id = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.stripe_charge_id}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes_given")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="likes_received"
    )

    def __str__(self):
        return f"いいねしたユーザー:{self.user},いいねの対象:{self.product.name}"


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("before_shipping", "発送待ち"),
        ("shipped", "発送済み"),
        ("delivered", "配達済"),
    ]
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="orders_received"
    )
    price = models.IntegerField()
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders_given"
    )
    order_time = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=20)
    address = models.OneToOneField(
        Address, on_delete=models.CASCADE, related_name="orders_delivered_to"
    )
    payment = models.OneToOneField(
        Payment, on_delete=models.CASCADE, related_name="orders_paid_with"
    )

    def __str__(self):
        return f"購入者:{self.product.name},配達状況{self.delivery_status}"


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications_received"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="notifications_given"
    )
    is_action = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}への{'アクション' if self.is_action == True else 'お知らせ'}"