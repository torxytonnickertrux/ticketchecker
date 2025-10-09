"""
Template tags e filtros extras para Django
Inclui filtros que podem estar faltando em algumas versões
"""
from django import template
from django.contrib.auth.models import AnonymousUser

register = template.Library()


@register.filter
def length_is(value, arg):
    """
    Filtro length_is que verifica se o comprimento de uma lista é igual ao argumento
    """
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return False


@register.filter
def length_gt(value, arg):
    """
    Filtro length_gt que verifica se o comprimento de uma lista é maior que o argumento
    """
    try:
        return len(value) > int(arg)
    except (ValueError, TypeError):
        return False


@register.filter
def length_lt(value, arg):
    """
    Filtro length_lt que verifica se o comprimento de uma lista é menor que o argumento
    """
    try:
        return len(value) < int(arg)
    except (ValueError, TypeError):
        return False


@register.filter
def has_role(user, roles_csv):
    """
    Verifica se o usuário possui qualquer um dos roles informados (CSV).
    Considera superusuário como tendo acesso.
    Uso: {% if request.user|has_role:'admin,event_manager' %}
    """
    try:
        if isinstance(user, AnonymousUser) or not getattr(user, 'is_authenticated', False):
            return False
        # Superuser tem acesso irrestrito
        if getattr(user, 'is_superuser', False):
            return True
        required = {r.strip() for r in str(roles_csv).split(',') if r.strip()}
        user_roles = set(user.roles.values_list('role', flat=True))
        return bool(required & user_roles)
    except Exception:
        return False
