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


@register.filter
def contains_character(value, arg):
    """
    Checks if 'arg' is a substring of 'value'.
    Value is passed as a list, hence take the first item.
    Usage: {{ value|contains:"substring" }}
    """
    return arg in value[0] if value else False
