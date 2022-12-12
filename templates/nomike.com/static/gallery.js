function setModal(index) {
    console.log("setModal: " + index);
    count = $("img.thumbnail").length
    current = $("img.thumbnail:eq(" + index + ")").attr("src");
    if (index == 0) {
        $(".previous").css("display", "none");
    } else {
        $(".previous").css("display", "inline-flex");
        $(".previous").off("click");
        $(".previous").click(function() {
            setModal(index - 1);
        });
    }

    if (index == count - 1) {
        $(".next").css("display", "none");
    } else {
        $(".next").css("display", "inline-flex");
        $(".next").off("click");
        $(".next").click(function() {
            setModal(index + 1);
        });
    }
    $("img.modal-content").attr('src', current);
    $("div#caption").html(current.split('/').reverse()[0])
    $(".modal").css("display", "block");
}

$(document).ready(function() {
    $("img.thumbnail").each(function(index) {
        $(this).click(function() {
            setModal(index)
        });
    });


    $("span.close").click(function() {
        $(".modal").css("display", "none");
    });
});

// // Get the modal
// var modal = document.getElementById("myModal");

// // Get the image and insert it inside the modal - use its "alt" text as a caption
// var img = document.getElementById("myImg");
// var modalImg = document.getElementById("img01");
// var captionText = document.getElementById("caption");
// img.onclick = function(){
//   modal.style.display = "block";
//   modalImg.src = this.src;
//   captionText.innerHTML = this.alt;
// }

// // Get the <span> element that closes the modal
// var span = document.getElementsByClassName("close")[0];

// // When the user clicks on <span> (x), close the modal
// span.onclick = function() {
//   modal.style.display = "none";
// }