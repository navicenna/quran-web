$(function () {
    $(".answer").hide();

    $(".btn").on("click", function () {
        var btn = $(this);
        console.log(btn);
        var answer = $(this).parent(".answer-container").find(".answer");
        console.log(answer);

        if (answer.is(":visible")) {
            answer.hide("slow");
            btn.html('Show')
        } else {
            answer.show("slow");
            btn.html('Hide')
        }
    })
})