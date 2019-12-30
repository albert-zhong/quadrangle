from django.contrib import messages


# Bootstrap alert colors
PRIMARY = 'primary'
SECONDARY = 'secondary'
SUCCESS = 'success'
DANGER = 'danger'
WARNING = 'warning'
INFO = 'info'
LIGHT = 'light'
DARK = 'dark'

# Django message dispatch functions
CALL_MESSAGE = {
    'debug': messages.debug,
    'info': messages.info,
    'success': messages.success,
    'warning': messages.warning,
    'error': messages.error,
}

def get_tags(color):
    return f"alert alert-{color} alert-dismissible fade show"

def alert(request, message, color, type='success'):
    if type not in CALL_MESSAGE:
        raise ValueError('Incorrect message type')
    CALL_MESSAGE[type](request, message, extra_tags=get_tags(color))

def wrong_college_alert(request):
    alert(
        request,
        'You do not belong to this college.',
        color=WARNING,
        type='warning',
    )

def failed_update_alert(request, model_name):
    alert(
        request,
        f"Something went wrong with trying to update the {model_name}, try again in a few minutes",
        color=DANGER,
        type='error'
    )

def successful_update_alert(request, model_name):
    alert(
        request,
        f"{model_name} successfully updated!",
        color=SUCCESS,
        type='success'
    )

def successful_delete_alert(request, model_name):
    alert(
        request,
        f"{model_name} successfully deleted!",
        color=SUCCESS,
        type='success',
    )

def no_perms_alert(request):
    alert(
        request,
        f"You do not have permissions to modify this.",
        color=WARNING,
        type='warning',
    )
