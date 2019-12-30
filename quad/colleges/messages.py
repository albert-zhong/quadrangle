from django.contrib import messages


COLORS_FUNCTIONS = {
    'primary': messages.success,
    'secondary': messages.success,
    'success': messages.success,
    'danger': messages.error,
    'warning': messages.warning,
    'info': messages.info,
    'light': messages.info,
    'dark': messages.debug,
}

def get_tags(color):
    return f"alert alert-{color} alert-dismissible fade show"

def alert(request, message, color):
    if type not in COLORS_FUNCTIONS:
        raise ValueError('Incorrect message type')
    COLORS_FUNCTIONS[type](request, message, extra_tags=get_tags(color))
