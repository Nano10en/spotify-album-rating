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

    $('html, body').animate({ scrollTop: 0 }, 500);
});

$('.center').slick({
    infinite: true,
    slidesToShow: 5,
    slidesToScroll: 1,
    centerMode: false,
    arrows: true,
    prevArrow: '<button class="slick-prev slick-arrow" aria-label="Previous" type="button"><i class="fa-solid fa-arrow-left-long"></i></button>',
    nextArrow: '<button class="slick-next slick-arrow" aria-label="Next" type="button"><i class="fa-solid fa-arrow-right-long"></i></button>',
    responsive: [
        {
            breakpoint: 992,
            settings: {
                slidesToShow: 4,
                centerMode: false
            }
        },
        {
            breakpoint: 768,
            settings: {
                slidesToShow: 3,
                arrows: false,
                centerMode: false
            }
        },
        {
            breakpoint: 480,
            settings: {
                slidesToShow: 1,
                arrows: false,
                centerMode: false
            }
        }
    ]
});

$(document).on('click', '.close', function () {
    $(this).closest('.message').fadeOut(200);
});

$("#search").on("click", () => {
    $(".releases-list").hide();
    $(".rated-albums").hide();
});

//Ajax search
let timeout = null;

$("#searchInput").on("input", function () {
    if ($(this).val() != 0) {
        $(".releases-list").hide()
        $(".rated-albums").hide()
    } else {
        $(".releases-list").show()
        $(".rated-albums").show()
    }
    const query = $(this).val().trim();

    clearTimeout(timeout);

    timeout = setTimeout(function () {
        if (!query) {
            $("#searchResults").html("");
            return;
        }

        $.ajax({
            url: "/search/",
            type: "GET",
            data: { q: query },
            success: function (data) {
                let html = "";

                if (!data.albums.length) {
                    html = "<p>No albums found.</p>";
                } else {
                    data.albums.forEach(album => {
                        html += `
                            <div class="album" onclick="window.location.href='${album.url}'">
                                    ${album.image ? `<img src="${album.image}" alt="${album.name}">` : ""}
                                    <div class="album-content">
                                        <div class="album-title">${album.name}</div>
                                        <div class="album-artist">${album.artist}</div>
                                    </div>
                            </div>
                        `;
                    });
                }

                $("#searchResults").html(html);
            },
            error: function () {
                console.log("Search error");
            }
        });
    }, 300);
});
