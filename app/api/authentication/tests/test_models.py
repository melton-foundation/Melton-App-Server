from django.test import TestCase

from authentication.models import Profile

class ProfileModelTest(TestCase):

    EMAIL = 'test@email.com'
    NAME = 'test'
    IS_JUNIOR_FELLOW = True
    CAMPUS = 'University of the World'
    BATCH = 2020
    NUMBER = '99999999999'
    COUNTRY_CODE = '+91'

    @classmethod
    def setUpTestData(cls):
        Profile.objects.create(email = cls.EMAIL,
                                name = cls.NAME,
                                is_junior_fellow = cls.IS_JUNIOR_FELLOW,
                                campus = cls.CAMPUS,
                                batch = cls.BATCH)
    
    def test_user_field(self):
        profile = Profile.objects.get(pk = 1)
        user = profile.user
        self.assertEqual(user.email, self.EMAIL)
        self.assertIsNone(user.username)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_profile(self):
        profile = Profile.objects.get(pk = 1)
        self.assertEqual(profile.name, self.NAME)
        self.assertEqual(profile.is_junior_fellow, self.IS_JUNIOR_FELLOW)
        self.assertEqual(profile.campus, self.CAMPUS)
        self.assertEqual(profile.batch, self.BATCH)
