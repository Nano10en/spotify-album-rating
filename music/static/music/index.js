$(".track-separator").hide();

// $(".track-info").on("click", function () {
//     $(this).next(".track-separator").toggle();
// });


$(".track-info").on("click", function () {
    const $clicked = $(this);
    const $sep = $clicked.next(".track-separator");
    const $album = $(".album-details");

    if ($album.css("height") === "auto") {
        $album.height($album.outerHeight());
    }

    // если уже открыт — вернуть всё обратно
    if ($sep.is(":visible")) {
        $(".track-separator").stop(true, true).slideUp(200);
        $(".track-info").stop(true, true).fadeIn(200);
        // $(".album-details").stop(true, true).animate({ height: 900 }, 200);

        const natural = $album.css("height", "auto").outerHeight();
        $album.height($album.outerHeight()).stop(true, true).animate({ height: natural }, 200, function () {
            $album.css("height", ""); // убираем height полностью (возвращается CSS/auto)
        });

        return;
    }

    $(".track-separator").stop(true, true).slideUp(200);
    $(".track-info").not($clicked).stop(true, true).fadeOut(200);
    $sep.stop(true, true).slideDown(200);

    $album.stop(true, true).animate({ height: 900 }, 200);
});