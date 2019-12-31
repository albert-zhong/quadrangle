const likeButton = {
    element: $('#like-thread-button'),
    activeClass: 'btn btn-success',
    passiveClass: 'btn btn-outline-success'
}

const dislikeButton = {
    element: $('#dislike-thread-button'),
    activeClass: 'btn btn-danger',
    passiveClass: 'btn btn-outline-danger'
}

const threadScore = {
    element: $('#thread-score'),
    positiveClass: 'btn btn-success',
    neutralClass: 'btn btn-secondary',
    negativeClass: 'btn btn-danger',
    represent: function(score) {
        return `Score: ${score}`;
    }
}

function getLikeCommentButton(pk) {
    const likeCommentButton = {
        element: $(`#like-comment-button-${pk}`),
        activeClass: 'btn btn-success btn-sm',
        passiveClass: 'btn btn-outline-success btn-sm'
    }
    return likeCommentButton;
}

function getDislikeCommentButton(pk) {
    const dislikeCommentButton = {
        element: $(`#dislike-comment-button-${pk}`),
        activeClass: 'btn btn-danger btn-sm',
        passiveClass: 'btn btn-outline-danger btn-sm'
    }
    return dislikeCommentButton;
}

function getCommentScore(pk) {
    const commentScore = {
        element: $(`#comment-score-${pk}`),
        positiveClass: 'text-success',
        neutralClass: 'text-secondary',
        negativeClass: 'text-danger',
        represent: function(score) {
            return `${score} points`;
        }
    }
    return commentScore;
}

document.addEventListener("DOMContentLoaded", function() { 
    updateThreadButtons({{ thread_like_status }});
    updateScore(threadScore, {{ thread.score }});

    const comments = {{ comment_like_statuses|safe }};
    for (let pk in comments) {
        updateCommentButtons(comments[pk]['likeStatus'], pk);
        updateScore(getCommentScore(pk), comments[pk]['score']);
    }
});

function updateThreadButtons(likeStatus) {
    const hasLiked = (likeStatus === 1);
    const hasDisliked = (likeStatus === -1);
    updateButton(likeButton, hasLiked);
    updateButton(dislikeButton, hasDisliked);
}

function updateCommentButtons(likeStatus, pk) {
    const hasLiked = (likeStatus === 1);
    const hasDisliked = (likeStatus === -1);
    const likeCommentButton = getLikeCommentButton(pk);
    const dislikeCommentButton = getDislikeCommentButton(pk);
    updateButton(likeCommentButton, hasLiked);
    updateButton(dislikeCommentButton, hasDisliked);
}

function updateButton(button, isActive) {
    const buttonClass = (isActive) ? button.activeClass : button.passiveClass;
    button.element.attr('class', buttonClass);
}

function updateScore(scoreObject, score) {
    var scoreObjectClass;
    switch (score) {
        case -1:
            scoreObjectClass = scoreObject.negativeClass;
            break;
        case 0:
            scoreObjectClass = scoreObject.neutralClass;
            break;
        case 1:
            scoreObjectClass = scoreObject.positiveClass;
            break;
    }
    scoreObject.element.attr('class', scoreObjectClass);
    scoreObject.element.html(scoreObject.represent(score));
}

const token = '{{ csrf_token }}';

function handleThreadClick(hasLiked) {
    $.ajax({
        type: "POST",
        headers: { "X-CSRFToken": token },
        url: "{% url 'like_thread' thread.slug %}",
        data: { hasLiked: hasLiked },
        success: function(data) {
            updateScore(threadScore, data.newScore);
            updateThreadButtons(data.likeStatus);
        },
        error: function() {
            console.log('broke');
        }
    });
}

function handleCommentClick(hasLiked, pk) {
    const likeCommentURL = `/colleges/comments/${pk}/like`;
    $.ajax({
        type: "POST",
        headers: { "X-CSRFToken": token },
        url: likeCommentURL,
        data: { hasLiked: hasLiked },
        success: function(data) {
            updateScore(getCommentScore(pk), data.newScore);
            updateCommentButtons(data.likeStatus, pk);
        },
        error: function() {
            console.log('broke');
        }
    });
}
