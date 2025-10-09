import os
from typing import Dict, Any, Optional
from django.conf import settings
from mercadopago import SDK
from events.models import Payment, Purchase
from django.utils.dateparse import parse_datetime


class MercadoPagoService:
    def __init__(self):
        self.access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
        self.public_key = settings.MERCADO_PAGO_PUBLIC_KEY
        self.sandbox = settings.MERCADO_PAGO_SANDBOX
        self.site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        self.sdk = SDK(self.access_token) if self.access_token else None

    def create_pix_payment(self, purchase: Purchase, description: str = "Pagamento de ingresso") -> Optional[Payment]:
        # Tentar obter pagamento existente pela purchase
        existing = None
        try:
            existing = purchase.payment
        except Exception:
            existing = Payment.objects.filter(purchase=purchase).first()

        if not self.sdk:
            # Fallback sandbox: gerar QR Code local e Payment dummy
            if self.sandbox:
                try:
                    import qrcode
                    import io
                    import base64
                except Exception:
                    # Criar/atualizar Payment com placeholder base64 sem dependências
                    payer_name = getattr(purchase.user, 'name', None) or purchase.user.email
                    qr_content = f"pix|purchase:{purchase.id}|amount:{purchase.total_price}|user:{purchase.user.email}"
                    qr_b64 = (
                        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
                    )
                    if existing:
                        payment = existing
                        payment.description = description
                        payment.payment_method = getattr(purchase, 'payment_method', 'pix')
                        payment.amount = purchase.total_price
                        payment.currency = 'BRL'
                        payment.payer_email = purchase.user.email or ""
                        payment.payer_name = payer_name
                        payment.payer_document = payment.payer_document or ""
                        payment.pix_qr_code = qr_content
                        payment.pix_qr_code_base64 = qr_b64
                        payment.mp_response = (payment.mp_response or {}) | {'local': True, 'sandbox': True, 'placeholder': True}
                        payment.save(update_fields=[
                            'description','payment_method','amount','currency','payer_email','payer_name',
                            'payer_document','pix_qr_code','pix_qr_code_base64','mp_response'
                        ])
                        return payment
                    else:
                        mp_payment_id = f"LOCAL-PIX-{purchase.id}"
                        payment = Payment(
                            purchase=purchase,
                            mercado_pago_id=mp_payment_id,
                            status='pending',
                            payment_method=getattr(purchase, 'payment_method', 'pix'),
                            amount=purchase.total_price,
                            currency='BRL',
                            description=description,
                            payer_email=purchase.user.email or "",
                            payer_name=payer_name,
                            payer_document="",
                            pix_qr_code=qr_content,
                            pix_qr_code_base64=qr_b64,
                            mp_response={'local': True, 'sandbox': True, 'placeholder': True},
                        )
                        payment.save()
                        return payment

                payer_name = getattr(purchase.user, 'name', None) or purchase.user.email
                qr_content = f"pix|purchase:{purchase.id}|amount:{purchase.total_price}|user:{purchase.user.email}"
                img = qrcode.make(qr_content)
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                mp_payment_id = f"LOCAL-PIX-{purchase.id}"

                payment, created = Payment.objects.get_or_create(
                    mercado_pago_id=mp_payment_id,
                    defaults={
                        'purchase': purchase,
                        'status': 'pending',
                        'payment_method': getattr(purchase, 'payment_method', 'pix'),
                        'amount': purchase.total_price,
                        'currency': 'BRL',
                        'description': description,
                        'payer_email': purchase.user.email or "",
                        'payer_name': payer_name,
                        'payer_document': "",
                        'pix_qr_code': qr_content,
                        'pix_qr_code_base64': qr_b64,
                        'mp_response': {'local': True, 'sandbox': True},
                    }
                )
                return payment
            return None

        # Determinar nome do pagador de forma compatível com usuário customizado
        user = purchase.user
        full_name_fn = getattr(user, 'get_full_name', None)
        payer_name = full_name_fn() if callable(full_name_fn) else (getattr(user, 'name', None) or user.email)

        # Criar pagamento PIX diretamente (em vez de preferência de checkout)
        payload = {
            "transaction_amount": float(purchase.total_price),
            "description": description,
            "payment_method_id": "pix",
            "external_reference": str(purchase.id),
            "notification_url": f"{self.site_url}/webhook/mercadopago/",
            "payer": {
                "email": purchase.user.email or "",
                "first_name": payer_name or "",
            },
        }

        result = self.sdk.payment().create(payload)
        response = result.get("response", {})
        mp_payment_id = str(response.get("id") or "").strip()
        status = response.get("status") or "pending"

        # Não criar Payment se a API não retornar um ID válido
        if not mp_payment_id:
            # Em sandbox, fazer fallback local gerando QR mesmo com SDK presente
            if self.sandbox:
                try:
                    import qrcode
                    import io
                    import base64
                    payer_name = payer_name  # já definido acima
                    qr_content = f"pix|purchase:{purchase.id}|amount:{purchase.total_price}|user:{purchase.user.email}"
                    img = qrcode.make(qr_content)
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                except Exception:
                    payer_name = payer_name
                    qr_content = f"pix|purchase:{purchase.id}|amount:{purchase.total_price}|user:{purchase.user.email}"
                    qr_b64 = (
                        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
                    )
                mp_payment_id = f"LOCAL-PIX-{purchase.id}"
                if existing:
                    payment = existing
                    payment.status = 'pending'
                    payment.payment_method = getattr(purchase, 'payment_method', 'pix')
                    payment.amount = purchase.total_price
                    payment.currency = 'BRL'
                    payment.description = description
                    payment.payer_email = purchase.user.email or ""
                    payment.payer_name = payer_name
                    payment.payer_document = payment.payer_document or ""
                    payment.pix_qr_code = qr_content
                    payment.pix_qr_code_base64 = qr_b64
                    payment.mp_response = (payment.mp_response or {}) | {'local': True, 'sandbox': True}
                    payment.save(update_fields=['status','payment_method','amount','currency','description','payer_email','payer_name','payer_document','pix_qr_code','pix_qr_code_base64','mp_response'])
                    return payment
                else:
                    payment = Payment(
                        purchase=purchase,
                        mercado_pago_id=mp_payment_id,
                        status='pending',
                        payment_method=getattr(purchase, 'payment_method', 'pix'),
                        amount=purchase.total_price,
                        currency='BRL',
                        description=description,
                        payer_email=purchase.user.email or "",
                        payer_name=payer_name,
                        payer_document="",
                        pix_qr_code=qr_content,
                        pix_qr_code_base64=qr_b64,
                        mp_response={'local': True, 'sandbox': True},
                    )
                    payment.save()
                    return payment
            return None

        # Extrair dados do QR Code (se disponíveis)
        poi = response.get("point_of_interaction", {}) or {}
        tx_data = poi.get("transaction_data", {}) or {}
        qr_code = tx_data.get("qr_code")
        qr_code_base64 = tx_data.get("qr_code_base64")

        if existing:
            payment = existing
            if payment.mercado_pago_id != mp_payment_id:
                payment.mercado_pago_id = mp_payment_id
            payment.status = status
            payment.payment_method = getattr(purchase, 'payment_method', 'pix')
            payment.amount = purchase.total_price
            payment.currency = 'BRL'
            payment.description = description
            payment.payer_email = purchase.user.email or ""
            payment.payer_name = payer_name
            payment.payer_document = payment.payer_document or ""
            if qr_code:
                payment.pix_qr_code = qr_code
            if qr_code_base64:
                payment.pix_qr_code_base64 = qr_code_base64
            payment.mp_response = response
            payment.save()
        else:
            payment = Payment(
                purchase=purchase,
                mercado_pago_id=mp_payment_id,
                status=status,
                payment_method=getattr(purchase, 'payment_method', 'pix'),
                amount=purchase.total_price,
                currency='BRL',
                description=description,
                payer_email=purchase.user.email or "",
                payer_name=payer_name,
                payer_document="",
                pix_qr_code=qr_code,
                pix_qr_code_base64=qr_code_base64,
                mp_response=response,
            )
            payment.save()
        
        return payment

    def ensure_local_pix_qr(self, payment: Optional[Payment], purchase: Purchase, description: str = "Pagamento de ingresso") -> Optional[Payment]:
        """
        Em sandbox sem SDK, garante que o Payment tenha um QR Code local.
        Não altera o mercado_pago_id existente.
        """
        # Em sandbox, mesmo com SDK presente, garantir fallback local
        if not self.sandbox:
            return payment
        # Se não há Payment ainda, buscar por purchase; se não existir, criar LOCAL-PIX
        if payment is None:
            payment = Payment.objects.filter(purchase=purchase).first()
            if payment is None:
                mp_payment_id = f"LOCAL-PIX-{purchase.id}"
                payment = Payment(
                    purchase=purchase,
                    mercado_pago_id=mp_payment_id,
                    status='pending',
                    payment_method=getattr(purchase, 'payment_method', 'pix'),
                    amount=purchase.total_price,
                    currency='BRL',
                    description=description,
                    payer_email=purchase.user.email or "",
                    payer_name=getattr(purchase.user, 'name', None) or purchase.user.email,
                    payer_document="",
                )
                payment.save()
        try:
            has_b64 = bool(getattr(payment, 'pix_qr_code_base64', None))
        except Exception:
            has_b64 = False
        if has_b64:
            return payment

        try:
            import qrcode
            import io
            import base64
        except Exception:
            # Definir placeholder base64 mesmo sem biblioteca qrcode
            payer_name = getattr(purchase.user, 'name', None) or purchase.user.email
            qr_content = f"pix|purchase:{purchase.id}|amount:{purchase.total_price}|user:{purchase.user.email}"
            qr_b64 = (
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
            )
            payment.description = description
            payment.payment_method = getattr(purchase, 'payment_method', 'pix')
            payment.amount = purchase.total_price
            payment.currency = 'BRL'
            payment.payer_email = purchase.user.email or ""
            payment.payer_name = payer_name
            payment.payer_document = payment.payer_document or ""
            payment.pix_qr_code = qr_content
            payment.pix_qr_code_base64 = qr_b64
            payment.mp_response = (payment.mp_response or {}) | {'local': True, 'sandbox': True, 'placeholder': True}
            payment.save(update_fields=[
                'description','payment_method','amount','currency','payer_email','payer_name',
                'payer_document','pix_qr_code','pix_qr_code_base64','mp_response'
            ])
            return payment

        payer_name = getattr(purchase.user, 'name', None) or purchase.user.email
        qr_content = f"pix|purchase:{purchase.id}|amount:{purchase.total_price}|user:{purchase.user.email}"
        img = qrcode.make(qr_content)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        qr_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        payment.description = description
        payment.payment_method = getattr(purchase, 'payment_method', 'pix')
        payment.amount = purchase.total_price
        payment.currency = 'BRL'
        payment.payer_email = purchase.user.email or ""
        payment.payer_name = payer_name
        payment.payer_document = payment.payer_document or ""
        payment.pix_qr_code = qr_content
        payment.pix_qr_code_base64 = qr_b64
        payment.mp_response = (payment.mp_response or {}) | {'local': True, 'sandbox': True}
        payment.save(update_fields=[
            'description','payment_method','amount','currency','payer_email','payer_name',
            'payer_document','pix_qr_code','pix_qr_code_base64','mp_response'
        ])
        return payment

    def get_payment_status(self, payment: Payment) -> str:
        if not self.sdk or not payment.mercado_pago_id:
            return payment.status
        try:
            result = self.sdk.payment().get(payment.mercado_pago_id)
            response = result.get("response", {})
            status = response.get("status") or payment.status
            if status != payment.status:
                payment.status = status
                # Definir paid_at se aprovado
                if status == 'approved':
                    date_approved = response.get('date_approved')
                    if date_approved:
                        dt = parse_datetime(date_approved)
                        if dt:
                            payment.paid_at = dt
                payment.mp_response = response
                payment.save()
            return status
        except Exception:
            return payment.status

    def handle_webhook(self, payload: Dict[str, Any]) -> Optional[Payment]:
        # Handler robusto: extrai ID e consulta API para obter status real
        mp_id = None
        # Formato novo: {"type":"payment","data":{"id":123}}
        data = payload.get("data")
        if isinstance(data, dict) and data.get("id"):
            mp_id = str(data.get("id"))
        # Formato antigo: {"id":123, "action":"payment.approved"}
        if not mp_id:
            mp_id = str(payload.get("id", ""))

        if not mp_id:
            return None

        try:
            payment = Payment.objects.get(mercado_pago_id=mp_id)
        except Payment.DoesNotExist:
            return None

        # Consultar status na API do MP
        if self.sdk:
            try:
                result = self.sdk.payment().get(mp_id)
                response = result.get("response", {})
                status = response.get("status")
                if status:
                    payment.status = status
                    if status == 'approved':
                        date_approved = response.get('date_approved')
                        if date_approved:
                            dt = parse_datetime(date_approved)
                            if dt:
                                payment.paid_at = dt
                payment.mp_response = response
                payment.save()
                return payment
            except Exception:
                return payment
        return payment