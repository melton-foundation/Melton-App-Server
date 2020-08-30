from rest_framework import serializers

from authentication.models import AppUser, PhoneNumber, Profile, ExpiringToken, SocialMediaAccount, SustainableDevelopmentGoal

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

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaAccount
        fields = ['type', 'account']

class SustainableDevelopmentGoalSerializer(serializers.RelatedField):

    queryset = SustainableDevelopmentGoal.objects.all()

    def to_internal_value(self, data):
        if int(data) != data:
            raise serializers.ValidationError('Only integer values are allowed.')

        if not SustainableDevelopmentGoal.objects.filter(pk = data).exists():
            raise serializers.ValidationError('No such SDG exists.')
        return int(data)

    def to_representation(self, value):
         return value.code

    class Meta:
        model = SustainableDevelopmentGoal


class _ProfileSerializer(serializers.ModelSerializer):
    user = AppUserSerializer()
    isJuniorFellow = serializers.BooleanField(source='is_junior_fellow', read_only=True)
    points = serializers.IntegerField(read_only=True)
    phoneNumber = PhoneNumberSerializer(source='phone_number', many = True, required=False)
    picture = serializers.ImageField(read_only=True)
    socialMediaAccounts = SocialMediaAccountSerializer(source='social_media_account', many=True, required=False)
    sdgs = SustainableDevelopmentGoalSerializer(required=False, many=True)

    def validate_sdgs(self, sdgs):
        if sdgs is not None and len(sdgs) > 3:
            raise serializers.ValidationError('Only 3 SDGs are allowed')
        return sdgs

    class Meta:
        model = Profile
        fields = ['user', 'name', 'isJuniorFellow',
                  'campus','city','country', 'batch', 'work', 'points', 'phoneNumber','socialMediaAccounts', 'sdgs', 'picture']
        depth = 1


class ProfileListSerializer(_ProfileSerializer):
    id = serializers.IntegerField(source='user.id')
    phoneNumber = PhoneNumberSerializer(source='phone_number', many = True, required=False)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'name', 'isJuniorFellow',
                  'campus', 'city','country', 'batch', 'work', 'phoneNumber', 'socialMediaAccounts', 'sdgs', 'picture']
        depth = 1

class ProfileCreateSerializer(_ProfileSerializer):

    def create(self, validated_data):
        profile = Profile.objects.create(
            email=validated_data['user']['email'],
            name=validated_data['name'],
            is_junior_fellow=True,
            campus=validated_data['campus'],
            batch=validated_data['batch']
        )
        return profile

    class Meta:
        model = Profile
        fields = ['user', 'name', 'isJuniorFellow',
                  'campus', 'batch']


class ProfileReadUpdateSerializer(_ProfileSerializer):
    phoneNumber = PhoneNumberSerializer(source='phone_number', many = True, required=False)
    user = AppUserSerializer(read_only=True)
    points = serializers.IntegerField(read_only=True)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.campus = validated_data.get('campus', instance.campus)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.work = validated_data.get('work', instance.work)
        instance.batch = validated_data.get('batch', instance.batch)
        # Delete existing phone numbers and add new ones
        _ph_query = PhoneNumber.objects.filter(user_profile = instance)
        existing_phone_numbers = list(_ph_query)
        _ph_query.delete()
        for phone_number in validated_data.get('phone_number', existing_phone_numbers):
            phone_number_obj = PhoneNumber(user_profile = instance, country_code = phone_number.get('country_code'), 
                                        number = phone_number.get('number'))
            phone_number_obj.save()

        # Delete existing social media and add new ones
        _social_media_query = SocialMediaAccount.objects.filter(user_profile = instance)
        existing_social_media = list(_social_media_query)
        _social_media_query.delete()
        for social_media_account in validated_data.get('social_media_account', existing_social_media):
            social_media_acc_obj = SocialMediaAccount(user_profile = instance, type = social_media_account.get('type'), 
                                                account = social_media_account.get('account'))
            social_media_acc_obj.save()

        instance.update_sdgs(validated_data.get('sdgs', None))

        
        instance.save()
        instance.refresh_from_db()
        return instance


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