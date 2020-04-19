from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import AppUser, Profile, ExpiringToken


class RegistrationAPITest(APITestCase):

    EMAIL = 'test@email.com'
    NAME = 'test'
    ALTERNATE_NAME = 'test again'
    IS_JUNIOR_FELLOW = True
    CAMPUS = 'University of the World'
    BATCH = 2020
    NUMBER = '99999999999'
    COUNTRY_CODE = '+91'

    RESPONSE_TYPE_SUCCESS = "success"
    RESPONSE_TYPE_FAILURE = "failure"

    def test_register_success(self):
        url = reverse('register')
        data = {
            "user": {
                "email": self.EMAIL
            },
            "name": self.NAME,
            "isJuniorFellow": self.IS_JUNIOR_FELLOW,
            "campus": self.CAMPUS,
            "batch": self.BATCH,
            "phoneNumber": {
                "countryCode": self.COUNTRY_CODE,
                "number": self.NUMBER
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_SUCCESS)
        user = AppUser.objects.get(email=self.EMAIL)
        self.assertIsNotNone(user)
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, self.NAME)
        self.assertEqual(profile.is_junior_fellow, self.IS_JUNIOR_FELLOW)
        self.assertEqual(profile.campus, self.CAMPUS)
        self.assertEqual(profile.batch, self.BATCH)
        phone_number = profile.phone_number.first()
        self.assertIsNotNone(phone_number)
        self.assertEqual(phone_number.number, self.NUMBER)
        self.assertEqual(phone_number.country_code, self.COUNTRY_CODE)

    def _test_register_missing_required_field(self, field_name):
        url = reverse('register')
        data = {
            "user": {
                "email": self.EMAIL
            },
            "name": self.NAME,
            "isJuniorFellow": self.IS_JUNIOR_FELLOW,
            "campus": self.CAMPUS,
            "batch": self.BATCH,
            "phoneNumber": {
                "countryCode": self.COUNTRY_CODE,
                "number": self.NUMBER
            }
        }
        data.pop(field_name)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_FAILURE)
        self.assertEqual(response.data[field_name][0].code, 'required')

    def test_register_missing_user(self):
        self._test_register_missing_required_field('user')

    def test_register_missing_name(self):
        self._test_register_missing_required_field('name')

    def test_register_missing_jf(self):
        self._test_register_missing_required_field('isJuniorFellow')

    def test_register_missing_campus(self):
        self._test_register_missing_required_field('campus')

    def test_register_missing_batch(self):
        self._test_register_missing_required_field('batch')

    def test_register_missing_phone(self):
        self._test_register_missing_required_field('phoneNumber')

    def test_register_same_email(self):
        url = reverse('register')
        data = {
            "user": {
                "email": self.EMAIL
            },
            "name": self.NAME,
            "isJuniorFellow": self.IS_JUNIOR_FELLOW,
            "campus": self.CAMPUS,
            "batch": self.BATCH,
            "phoneNumber": {
                "countryCode": self.COUNTRY_CODE,
                "number": self.NUMBER
            }
        }
        # First registration attempt
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_count = AppUser.objects.filter(email=self.EMAIL).count()
        self.assertEqual(user_count, 1)

        # Second registration attempt with same email
        data['name'] = self.ALTERNATE_NAME
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_count = AppUser.objects.filter(email=self.EMAIL).count()
        self.assertEqual(user_count, 1)
        user = AppUser.objects.get(email=self.EMAIL)
        profile = Profile.objects.get(user=user)
        # Check if its the old user
        self.assertEqual(profile.name, self.NAME)


class RegistrationStatusAPITest(APITestCase):
    EMAIL = 'test@email.com'
    ALTERNATE_EMAIL = 'test@gmail.com'
    NAME = 'test'
    IS_JUNIOR_FELLOW = True
    CAMPUS = 'University of the World'
    BATCH = 2020
    NUMBER = '99999999999'
    COUNTRY_CODE = '+91'

    RESPONSE_TYPE_SUCCESS = "success"
    RESPONSE_TYPE_FAILURE = "failure"

    def _build_url(self, *args, **kwargs):
        get = kwargs.pop('get', {})
        url = reverse(*args, **kwargs)
        if get:
            url += '?' + urlencode(get)
        return url

    def _register_user(self):
        url = reverse('register')
        data = {
            "user": {
                "email": self.EMAIL
            },
            "name": self.NAME,
            "isJuniorFellow": self.IS_JUNIOR_FELLOW,
            "campus": self.CAMPUS,
            "batch": self.BATCH,
            "phoneNumber": {
                "countryCode": self.COUNTRY_CODE,
                "number": self.NUMBER
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_status_active(self):
        self._register_user()
        user = AppUser.objects.get(email=self.EMAIL)
        user.is_active = True
        user.save()

        url = self._build_url('check_registration', get={'email': self.EMAIL})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_SUCCESS)
        self.assertEqual(response.data.get('isApproved', None), True)

    def test_registration_status_pending(self):
        self._register_user()

        url = self._build_url('check_registration', get={'email': self.EMAIL})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_SUCCESS)
        self.assertEqual(response.data.get('isApproved', None), False)

    def test_registration_status_unknown_user(self):
        self._register_user()
        url = self._build_url('check_registration', get={
                              'email': self.ALTERNATE_EMAIL})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_FAILURE)
        self.assertIsNone(response.data.get('is_active', None))

    def test_registration_status_missing_email(self):
        self._register_user()
        url = self._build_url('check_registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_FAILURE)


class ProfileAPITest(APITestCase):
    EMAIL = 'test@email.com'
    ALTERNATE_EMAIL = 'test@gmail.com'
    NAME = 'test'
    IS_JUNIOR_FELLOW = True
    CAMPUS = 'University of the World'
    BATCH = 2020
    NUMBER = '99999999999'
    COUNTRY_CODE = '+91'
    POINTS = 0

    RESPONSE_TYPE_SUCCESS = "success"
    RESPONSE_TYPE_FAILURE = "failure"

    def _build_url(self, *args, **kwargs):
        get = kwargs.pop('get', {})
        url = reverse(*args, **kwargs)
        if get:
            url += '?' + urlencode(get)
        return url

    def setUp(self):
        self.profile = Profile.objects.create(email=self.EMAIL, name=self.NAME,
                                              is_junior_fellow=self.IS_JUNIOR_FELLOW, campus=self.CAMPUS,
                                              batch=self.BATCH, number=self.NUMBER, country_code=self.COUNTRY_CODE)
        self.user = self.profile.user
        self.token = ExpiringToken.objects.get(user=self.user)

        self.data = {
            "user": {
                "email": self.EMAIL
            },
            "name": self.NAME,
            "isJuniorFellow": self.IS_JUNIOR_FELLOW,
            "campus": self.CAMPUS,
            "batch": self.BATCH,
            "points": self.POINTS,
            "phoneNumber": [{
                            "countryCode": self.COUNTRY_CODE,
                            "number": self.NUMBER
                            }]
        }

    def _test_update_field(self, field, value):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('profile')
        self.data[field] = value
        response = self.client.post(url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_SUCCESS)
        return response

    def test_get_profile(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        url = self._build_url('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('type', None),
                         self.RESPONSE_TYPE_SUCCESS)
        profile = response.data.get('profile')
        self.assertEqual(profile.get('user').get('email'), self.EMAIL)
        self.assertEqual(profile.get('name'), self.NAME)
        self.assertEqual(profile.get('isJuniorFellow'), self.IS_JUNIOR_FELLOW)
        self.assertEqual(profile.get('campus'), self.CAMPUS)
        self.assertEqual(profile.get('batch'), self.BATCH)
        self.assertEqual(profile.get('points'), self.POINTS)
        self.assertEqual(profile.get('phoneNumber')[
                         0].get('number'), self.NUMBER)
        self.assertEqual(profile.get('phoneNumber')[0].get(
            'countryCode'), self.COUNTRY_CODE)

    def test_cant_update_points(self):
        points = 100
        response = self._test_update_field("points", points)
        self.assertNotEqual(response.data.get("profile").get("points"), points)

    def test_cant_update_is_junior_fellow(self):
        is_junior_fellow = False
        response = self._test_update_field("isJuniorFellow", is_junior_fellow)
        self.assertNotEqual(response.data.get("profile").get("isJuniorFellow"), is_junior_fellow)

    def test_update_name(self):
        name = "suhas"
        response = self._test_update_field("name", name)
        self.assertEqual(response.data.get("profile").get("name"), name)

    def test_update_campus(self):
        campus = "BMS"
        response = self._test_update_field("campus", campus)
        self.assertEqual(response.data.get("profile").get("campus"), campus)

    def test_update_batch(self):
        batch = 2021
        response = self._test_update_field("batch", batch)
        self.assertEqual(response.data.get("profile").get("batch"), batch)

    def test_update_phone_numbers(self):
        phone_numbers = [
            {
                'number': '1111',
                'countryCode': '+91'
            },
            {
                'number': '2222',
                'countryCode': '+92'
            }
        ]
        response = self._test_update_field("phoneNumber", phone_numbers)
        self.assertListEqual(response.data.get(
            "profile").get("phoneNumber"), phone_numbers)
