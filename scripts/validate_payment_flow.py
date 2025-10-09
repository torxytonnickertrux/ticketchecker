import requests
import re
import os

BASE_URL = os.environ.get('BASE_URL', 'http://127.0.0.1:8003')
LOGIN_URL = f'{BASE_URL}/users/login/'
HISTORY_URL = f'{BASE_URL}/history/'

EMAIL = os.environ.get('TEST_EMAIL', 'test@example.com')
PASSWORD = os.environ.get('TEST_PASSWORD', 'Test1234!')


def get_csrf(session, url):
    r = session.get(url, allow_redirects=True)
    r.raise_for_status()
    m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
    return m.group(1) if m else None


def main():
    s = requests.Session()
    csrf = get_csrf(s, LOGIN_URL)
    print('Login CSRF token found:', bool(csrf))
    payload = {
        'csrfmiddlewaretoken': csrf,
        'username': EMAIL,
        'password': PASSWORD,
    }
    resp = s.post(LOGIN_URL, data=payload, headers={'Referer': LOGIN_URL}, allow_redirects=True)
    print('Login status:', resp.status_code)
    print('Login final URL:', resp.url)

    # Access purchase history
    hist = s.get(HISTORY_URL, allow_redirects=True)
    print('History status:', hist.status_code)
    has_payment_links = 'payment/form/' in hist.text
    print('History has payment links:', has_payment_links)

    # Try to extract a purchase_id for payment_form
    m = re.search(r'href="/payment/form/(\d+)/"', hist.text)
    if not m:
        print('No payment_form link found in history.')
        return
    purchase_id = m.group(1)
    payment_form_url = f'{BASE_URL}/payment/form/{purchase_id}/'
    print('Payment form URL:', payment_form_url)
    pf = s.get(payment_form_url, allow_redirects=True)
    print('Payment form status:', pf.status_code)
    print('Payment form contains sandbox note:', 'Sandbox habilitado' in pf.text)
    no_init_msg = 'Pagamento não inicializado' in pf.text
    print('Payment not initialized (expected without credentials):', no_init_msg)
    print('Payment form has QR base64:', 'data:image/png;base64,' in pf.text)

    # If checkout link exists, follow it
    cm = re.search(r'href="/payment/checkout/(\d+)/"', pf.text)
    if cm:
        checkout_id = cm.group(1)
        checkout_url = f'{BASE_URL}/payment/checkout/{checkout_id}/'
        print('Checkout URL:', checkout_url)
        co = s.get(checkout_url, allow_redirects=True)
        print('Checkout status:', co.status_code)
        # Show payment status snippet
        status_match = re.search(r'Status:\s*<strong>([^<]+)</strong>', co.text)
        print('Checkout payment status:', status_match.group(1) if status_match else 'unknown')
    else:
        print('No checkout link available (no payment created).')


if __name__ == '__main__':
    main()