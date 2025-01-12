from django import template

register = template.Library()


@register.filter
def round_to_hundreds(value):
    """Custom filter to format numbers as 12.3k, 9.7k, etc."""
    try:
        value = int(value)
        if value >= 1000:
            return f"{round(value / 1000, 1)}k"
        return str(value)
    except (ValueError, TypeError):
        return value  # Return the value as-is if it's not a number
