# accounts/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from shops.models import Shop

User = get_user_model()


# --- Nested Serializers for Validation ---

class NestedShopSerializer(serializers.ModelSerializer):
    """
    Validates the shop data.
    """
    class Meta:
        model = Shop
        fields = ['name', 'address', 'contact_phone', 'contact_email', 'language']


class NestedUserCreationSerializer(serializers.ModelSerializer):
    """
    Validates the user data (for owner and shopkeeper).
    """
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            'password': {'write_only': True}
        }


# --- Main Registration Serializer ---

class ShopRegistrationSerializer(serializers.Serializer):
    """
    Orchestrates the registration process using nested serializers for robust validation.
    """
    shop = NestedShopSerializer()
    owner = NestedUserCreationSerializer()
    create_shopkeeper = serializers.BooleanField(default=False)
    shopkeeper = NestedUserCreationSerializer(required=False)

    def validate(self, data):
        if User.objects.filter(username=data['owner']['username']).exists():
            raise serializers.ValidationError({'owner': 'An owner with this username already exists.'})

        if data.get('create_shopkeeper') and data.get('shopkeeper'):
            if User.objects.filter(username=data['shopkeeper']['username']).exists():
                raise serializers.ValidationError({'shopkeeper': 'A shopkeeper with this username already exists.'})
        return data

    @transaction.atomic
    def create(self, validated_data):
        shop_data = validated_data.pop("shop")
        owner_data = validated_data.pop("owner")
        create_shopkeeper = validated_data.pop("create_shopkeeper")
        shopkeeper_data = validated_data.pop("shopkeeper", None)

        # 1. Create Shop
        shop = Shop.objects.create(**shop_data)

        # 2. Create Owner User
        owner_password = owner_data.pop('password', None)
        owner = User.objects.create_user(
            **{k: v for k, v in owner_data.items() if k != 'password'},
            role=User.Role.SHOP_OWNER,
            shop=shop
        )
        if owner_password:
            owner.set_password(owner_password)
            owner.save()

        # 3. Create Shopkeeper if requested
        shopkeeper = None
        if create_shopkeeper and shopkeeper_data:
            shopkeeper_password = shopkeeper_data.pop('password', None)
            shopkeeper = User.objects.create_user(
                **{k: v for k, v in shopkeeper_data.items() if k != 'password'},
                role=User.Role.SHOPKEEPER,
                shop=shop
            )
            if shopkeeper_password:
                shopkeeper.set_password(shopkeeper_password)
                shopkeeper.save()

        return {
            "shop": shop,
            "owner": owner,
            "shopkeeper": shopkeeper,
        }


# --- Staff Serializer ---

class StaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', 'default123')
        # create_user is used to respect any custom user manager behavior
        user = User.objects.create_user(**{k: v for k, v in validated_data.items()})
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
