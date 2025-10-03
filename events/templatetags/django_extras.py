"""
Template tags e filtros extras para Django
Inclui filtros que podem estar faltando em algumas versões
"""
from django import template

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
