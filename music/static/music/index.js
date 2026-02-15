$(".track-separator").hide();

$(".track-info").on("click", function () {
    $(this).next(".track-separator").toggle();
});