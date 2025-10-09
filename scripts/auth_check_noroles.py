import requests
import re
import time

BASE_URL = 'http://127.0.0.1:8003'
HOME_URL = f'{BASE_URL}/'
REGISTER_URL = f'{BASE_URL}/users/register/'
LOGIN_URL = f'{BASE_URL}/users/login/'

PROTECTED_ENDPOINTS = [
    ('dashboard', f'{BASE_URL}/dashboard/'),
    ('validate_ticket', f'{BASE_URL}/validate/'),
    ('coupon_management', f'{BASE_URL}/coupons/'),
    ('analytics', f'{BASE_URL}/analytics/1/'),
]


def get_csrf(session, url):
    r = session.get(url)
    r.raise_for_status()
    m = re.search(r'name=\"csrfmiddlewaretoken\" value=\"([^\"]+)\"', r.text)
    return m.group(1) if m else None


def register_no_role_user(session):
    csrf = get_csrf(session, REGISTER_URL)
    print('Register CSRF token found:', bool(csrf))
    email = f"no-role-{int(time.time())}@example.com"
    payload = {
        'csrfmiddlewaretoken': csrf,
        'email': email,
        'name': 'No Role User',
        'cpf': '',
        'phone': '',
        'password1': 'Test12345!A',
        'password2': 'Test12345!A',
    }
    resp = session.post(REGISTER_URL, data=payload, headers={'Referer': REGISTER_URL}, allow_redirects=True)
    print('Register status:', resp.status_code)
    print('Register final URL:', resp.url)
    return email


def main():
    s = requests.Session()
    email = register_no_role_user(s)

    # After registration, Home should NOT have Dashboard link
    home = s.get(HOME_URL, allow_redirects=True)
    has_dash_link = ('href="/dashboard/"' in home.text) or ('>Dashboard<' in home.text)
    print('Home has Dashboard link (no-role user):', has_dash_link)

    for name, url in PROTECTED_ENDPOINTS:
        r = s.get(url, allow_redirects=True)
        print(f"{name} status:", r.status_code)
        print(f"{name} final URL:", r.url)


if __name__ == '__main__':
    main()