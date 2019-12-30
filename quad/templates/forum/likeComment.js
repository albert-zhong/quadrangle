function handleCommentClick(is_like, id) {
    const token = getCookie('csrftoken');
    const scoreID = `#comment-score-${id}`;
    const url =`/colleges/comments/${id}/like`;

    $.ajax({
        type: "POST",
        headers: { "X-CSRFToken": token },
        url: url,
        data: { pressed_like: is_like },
        success: function(data) {
            $(scoreID).html(data.score);
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