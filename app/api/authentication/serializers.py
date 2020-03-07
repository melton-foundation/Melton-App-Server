from rest_framework import serializers

from authentication.models import AppUser, PhoneNumber, Profile


class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['email']


class PhoneNumberSerializer(serializers.ModelSerializer):
    user_profile = serializers.PrimaryKeyRelatedField(
        read_only=True, required=False)

    class Meta:
        model = PhoneNumber
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    user = AppUserSerializer()
    points = serializers.IntegerField(read_only=True)
    phone_number = PhoneNumberSerializer()

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

    class Meta:
        model = Profile
        fields = '__all__'
        depth = 1


class RegistrationStatusSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    is_active = serializers.BooleanField(read_only=True)

    def check_status(self):
        user = AppUser.objects.filter(email=self.validated_data['email'])
        if user:
            return user.get().is_active

        else:
            return None
