from datetime import datetime, timezone
import pandas as pd
import json

NOW = datetime.now(tz=timezone.utc).isoformat(timespec='milliseconds').split('+')[0] + 'Z'
DATA_FILE = 'DB snapshot - FINAL - app db from website db.csv'
USER_DATA = 'users.json'
PROFILE_DATA = 'profiles.json'
ACCOUNTS_DATA = 'accounts.json'


SOCIAL_MEDIA_TYPES = ['Facebook', 'LinkedIn', 'Twitter', 'Wechat', 'Other']

class AppUser:

    count = 1

    @classmethod
    def increment_app_user(cls):
        AppUser.count += 1


    def __init__(self, email):
        self.model = 'authentication.appuser'
        self.pk = AppUser.count
        self.fields = {
            'password': '',
            'last_login': None,
            'is_superuser': False,
            'first_name': '',
            'last_name': '',
            'is_staff': False,
            'is_active': True,
            'date_joined': NOW,
            'email': email,
            'groups': [],
            'user_permissions': []
        }

    def to_json(self):
        return self.__dict__

class Profile:

    def __init__(self, user_id, name, batch, campus='', city='', country='', bio='', work='', sdgs=[]):
        self.model = 'authentication.profile'
        self.pk = user_id
        self.fields = {
            'name': name,
            'is_junior_fellow': False,
            'campus': campus,
            'city': city,
            'country': country,
            'bio': bio,
            'work': work,
            'batch': batch,
            'points': 0,
            'picture': '',
            'sdgs': sdgs
        }

    def to_json(self):
        return self.__dict__

class SocialMediaAccount:
    count = 1

    @classmethod
    def increment_social_media_account(cls):
        SocialMediaAccount.count += 1

    def __init__(self, profile_id, account, account_type):
        self.model = 'authentication.socialmediaaccount'
        self.pk = SocialMediaAccount.count
        self.fields = {
            "user_profile": profile_id,
            "account": account,
            "type": account_type
        }
    
    def to_json(self):
        return self.__dict__



all_users = []
all_profiles = []
all_accounts = []

def format_sdgs(sdgs):
    sdg_list = []
    if (sdgs.strip() != ''):
        sdg_list = list(map(lambda sdg: int(sdg.strip()), sdgs.split(',')))
    return sdg_list

def create_social_media_accounts(profile_id, row):
    social_media_accounts = []
    for social_media_type in SOCIAL_MEDIA_TYPES:
        if (row[social_media_type] != ''):
            account = SocialMediaAccount(profile_id, account=row[social_media_type], account_type=social_media_type)
            SocialMediaAccount.increment_social_media_account()
            social_media_accounts.append(account.to_json())
    
    return social_media_accounts

def create_models(row):
    global all_users, all_profiles, all_accounts
    name = row['Full name']
    email = row['Email']
    batch = int(row['Batch'])
    campus = row['Campus']
    city = row['City']
    country = row['Country']
    sdgs = format_sdgs(row['SDGs'])
    bio = row['Bio']
    work = row['Work']

    user = AppUser(email)
    AppUser.increment_app_user()
    profile = Profile(user.pk, name, batch, campus=campus, city=city, country=country, bio=bio, work=work, sdgs=sdgs)
    social_media_accounts = create_social_media_accounts(profile.pk, row)

    assert user.pk == profile.pk, 'User and Profile IDs do not match'
    assert all([account['fields']['user_profile'] == user.pk for account in social_media_accounts]), 'All accounts dont have same user ID'

    all_users.append(user.to_json())
    all_profiles.append(profile.to_json())
    all_accounts.extend(social_media_accounts)
    


def main():
    data = pd.read_csv(DATA_FILE, encoding='UTF8')
    data.rename(columns = {'Website': 'Other'}, inplace = True)
    data.fillna('', inplace = True)
    data.apply(create_models, axis=1)

    with open(USER_DATA, 'w', encoding='UTF8') as file:
        json.dump(all_users, file, indent=4)

    with open(PROFILE_DATA, 'w', encoding='UTF8') as file:
        json.dump(all_profiles, file, indent=4)

    with open(ACCOUNTS_DATA, 'w', encoding='UTF8') as file:
        json.dump(all_accounts, file, indent=4)



if __name__ == "__main__":
    main()