from django import template

register = template.Library()

@register.filter
def rupiah(nilai):
    """{{ 150000|rupiah }} → Rp 150.000"""
    if not nilai:
        return "Rp 0"
    return f"Rp {int(nilai):,}".replace(",", ".")