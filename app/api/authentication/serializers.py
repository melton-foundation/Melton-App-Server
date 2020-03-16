from rest_framework import serializers

from authentication.models import AppUser, PhoneNumber, Profile, ExpiringToken

AUTH_PROVIDERS = ['GOOGLE', 'WECHAT', 'MF']

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['email']


class PhoneNumberSerializer(serializers.ModelSerializer):
    countryCode = serializers.CharField(source='country_code')

    class Meta:
        model = PhoneNumber
        fields = ['number', 'countryCode']


class _ProfileSerializer(serializers.ModelSerializer):
    user = AppUserSerializer()
    isJuniorFellow = serializers.BooleanField(source='is_junior_fellow')
    points = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'name', 'isJuniorFellow',
                  'campus', 'batch', 'points', 'phoneNumber']
        depth = 1


class ProfileCreateSerializer(_ProfileSerializer):
    phoneNumber = PhoneNumberSerializer(source='phone_number')

    def create(self, validated_data):
        profile = Profile.objects.create(
            email=validated_data['user']['email'],
            name=validated_data['name'],
            is_junior_fellow=validated_data['is_junior_fellow'],
            campus=validated_data['campus'],
            batch=validated_data['batch'],
            number=validated_data['phone_number']['number'],
            country_code=validated_data['phone_number']['country_code']
        )
        return profile


class ProfileReadSerializer(_ProfileSerializer):
    phoneNumber = PhoneNumberSerializer(source='phone_number', many = True)


class RegistrationStatusSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    is_active = serializers.BooleanField(read_only=True)

    def check_status(self):
        user = AppUser.objects.filter(email=self.validated_data['email'])
        if user:
            return user.get().is_active

        else:
            return None


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    token = serializers.CharField(required=True)
    authProvider = serializers.ChoiceField(AUTH_PROVIDERS, required=True)