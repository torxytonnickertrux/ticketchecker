import requests
import re

BASE_URL = 'http://127.0.0.1:8003'
HOME_URL = f'{BASE_URL}/'
LOGIN_URL = f'{BASE_URL}/users/login/'
DASHBOARD_URL = f'{BASE_URL}/dashboard/'

EMAIL = 'admin@example.com'
PASSWORD = 'admin123'

def get_csrf(session):
    r = session.get(LOGIN_URL)
    r.raise_for_status()
    m = re.search(r'name=\"csrfmiddlewaretoken\" value=\"([^\"]+)\"', r.text)
    return m.group(1) if m else None

def main():
    # Check anonymous access should redirect to login
    anon = requests.get(DASHBOARD_URL, allow_redirects=True)
    print('Anon dashboard status:', anon.status_code)
    print('Anon final URL:', anon.url)

    s = requests.Session()
    csrf = get_csrf(s)
    print('CSRF token found:', bool(csrf))
    payload = {
        'csrfmiddlewaretoken': csrf,
        'username': EMAIL,
        'password': PASSWORD,
    }
    resp = s.post(LOGIN_URL, data=payload, headers={'Referer': LOGIN_URL}, allow_redirects=True)
    print('Login status:', resp.status_code)
    print('Final URL:', resp.url)

    # After login, check if Home shows Dashboard link in menu
    home = s.get(HOME_URL, allow_redirects=True)
    has_dash_link = ('href="/dashboard/"' in home.text) or ('>Dashboard<' in home.text)
    print('Home has Dashboard link:', has_dash_link)

    dash = s.get(DASHBOARD_URL, allow_redirects=True)
    print('Dashboard status:', dash.status_code)
    print('Contains Dashboard title:', 'Dashboard' in dash.text)

if __name__ == '__main__':
    main()