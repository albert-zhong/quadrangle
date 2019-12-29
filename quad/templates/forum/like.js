document.addEventListener("DOMContentLoaded", function() { 
    updateButtons({{ initial_like_status }});
});

function updateButtons(likeStatus) {
    likeButton = {
        id: '#like-button',
        activeClass: 'btn btn-success',
        passiveClass: 'btn btn-outline-success'
    }

    dislikeButton = {
        id: '#dislike-button',
        activeClass: 'btn btn-danger',
        passiveClass: 'btn btn-outline-danger'
    }

    const hasLiked = (likeStatus === 1);
    const hasDisliked = (likeStatus === -1);

    updateButton(likeButton, hasLiked);
    updateButton(dislikeButton, hasDisliked);
}

function updateButton(button, isActive) {
    const buttonClass = (isActive) ? button.activeClass : button.passiveClass;
    $(button.id).attr('class', buttonClass);
}

function handleClick(is_like) {
    const token = getCookie('csrftoken');
    $.ajax({
        type: "POST",
        headers: { "X-CSRFToken": token },
        url: "{% url 'like_thread' thread.slug %}",
        data: { pressed: is_like },
        success: function(data) {
            $('#thread-score').html(data.votes);
            updateButtons(data.likeStatus);
        },
        error: function() {
            console.log('broke');
        }
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}