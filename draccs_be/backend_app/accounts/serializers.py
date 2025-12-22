# from rest_framework import serializers
# from django.contrib.auth.hashers import make_password
# from django.db.models import Q
# from .models import Account

# class AccountSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

#     class Meta:
#         model = Account
#         fields = [
#             "id", "name", "email", "employee_id", "phone",
#             "designation", "address", "client_type",
#             "password", "confirm_password",
#             "is_active", "created_at", "updated_at",
#         ]
#         read_only_fields = ["id", "created_at", "updated_at"]
#         extra_kwargs = {
#             "name": {"required": True},
#             "email": {"required": True},
#             "employee_id": {"required": True},
#             "phone": {"required": True},
#             "designation": {"required": True},
#             "client_type": {"required": False, "allow_null": True, "allow_blank": True},
#             "password": {"write_only": True, "required": False},
#         }

#     def validate_email(self, value):
#         return value.strip().lower()

#     def validate(self, attrs):
#         instance = getattr(self, "instance", None)
#         pwd = attrs.get("password")
#         confirm = attrs.get("confirm_password")

#         # require password + confirm on create or when password provided
#         if instance is None or pwd is not None:
#             if not pwd:
#                 raise serializers.ValidationError({"password": "Password is required."})
#             if confirm != pwd:
#                 raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

#         email = (attrs.get("email") or (instance.email if instance else "")).strip().lower()
#         employee_id = attrs.get("employee_id")

#         if instance:
#             if email and Account.objects.exclude(pk=instance.pk).filter(email=email).exists():
#                 raise serializers.ValidationError({"email": "Email already exists."})
#             if employee_id and Account.objects.exclude(pk=instance.pk).filter(
#                 Q(employee_id__iexact=employee_id)
#             ).exists():
#                 raise serializers.ValidationError({"employee_id": "Employee ID already exists."})
#         else:
#             if email and Account.objects.filter(email=email).exists():
#                 raise serializers.ValidationError({"email": "Email already exists."})
#             if employee_id and Account.objects.filter(Q(employee_id__iexact=employee_id)).exists():
#                 raise serializers.ValidationError({"employee_id": "Employee ID already exists."})

#         attrs["email"] = email
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop("confirm_password", None)
#         raw_password = validated_data.pop("password")
#         validated_data["password"] = make_password(raw_password)
#         return Account.objects.create(**validated_data)

#     def update(self, instance, validated_data):
#         confirm = validated_data.pop("confirm_password", None)
#         pwd = validated_data.pop("password", None)

#         for k, v in validated_data.items():
#             setattr(instance, k, v)

#         if pwd is not None:
#             if confirm != pwd:
#                 raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
#             instance.password = make_password(pwd)

#         instance.save()
#         return instance


from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = [
            "id", "name", "email", "employee_id", "phone",
            "designation", "address", "client_type",
            "password", "confirm_password",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "employee_id", "created_at", "updated_at"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({
                "confirm_password": "Passwords do not match"
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return Account.objects.create(**validated_data)
