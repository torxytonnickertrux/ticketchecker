"""
Configurações personalizadas do Django Unfold para interface futurista
"""

from django.urls import reverse
from django.templatetags.static import static
from django.db.models import Sum

# Configurações do Django Unfold (Interface Futurista)
UNFOLD_CONFIG = {
    "SITE_TITLE": "TicketChecker Admin",
    "SITE_HEADER": "TicketChecker",
    "SITE_URL": "/",
    "SITE_SYMBOL": "🎫",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "TicketChecker Admin Panel",
    "DASHBOARD_CARDS": [
        {
            "name": "Eventos Ativos",
            "value": lambda request: "events.Event".objects.filter(is_active=True).count() if hasattr(request, 'user') and request.user.is_authenticated else 0,
            "url": lambda request: reverse("admin:events_event_changelist"),
        },
        {
            "name": "Ingressos Vendidos",
            "value": lambda request: "events.Purchase".objects.filter(status='confirmed').count() if hasattr(request, 'user') and request.user.is_authenticated else 0,
            "url": lambda request: reverse("admin:events_purchase_changelist"),
        },
        {
            "name": "Receita Total",
            "value": lambda request: f"R$ 0.00" if not hasattr(request, 'user') or not request.user.is_authenticated else f"R$ {0:.2f}",
            "url": lambda request: reverse("admin:events_purchase_changelist"),
        },
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": True,
                "items": [
                    {
                        "title": "Visão Geral",
                        "icon": "dashboard",
                        "link": lambda request: reverse("admin:index"),
                    },
                ],
            },
            {
                "title": "Gestão de Eventos",
                "separator": True,
                "items": [
                    {
                        "title": "Eventos",
                        "icon": "event",
                        "link": lambda request: reverse("admin:events_event_changelist"),
                    },
                    {
                        "title": "Ingressos",
                        "icon": "ticket",
                        "link": lambda request: reverse("admin:events_ticket_changelist"),
                    },
                ],
            },
            {
                "title": "Vendas e Compras",
                "separator": True,
                "items": [
                    {
                        "title": "Compras",
                        "icon": "shopping_cart",
                        "link": lambda request: reverse("admin:events_purchase_changelist"),
                    },
                    {
                        "title": "Cupons",
                        "icon": "local_offer",
                        "link": lambda request: reverse("admin:events_coupon_changelist"),
                    },
                ],
            },
            {
                "title": "Sistema",
                "separator": True,
                "items": [
                    {
                        "title": "Usuários",
                        "icon": "people",
                        "link": lambda request: reverse("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Validações QR",
                        "icon": "qr_code",
                        "link": lambda request: reverse("admin:events_ticketvalidation_changelist"),
                    },
                ],
            },
        ],
    },
    "COLORS": {
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "196 181 253",
            "500": "147 51 234",
            "600": "126 34 206",
            "700": "109 40 217",
            "800": "91 33 182",
            "900": "76 29 149",
            "950": "46 16 101",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇺🇸",
                "pt": "🇧🇷",
            },
        },
    },
}
