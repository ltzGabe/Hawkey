$(document).on('click', '.closeTab', function() {
    csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value
    var numItems = $('.tabs').length
    if (numItems == 2) {
        //document.getElementById("error3").style.display = "block"
        setTimeout(function() {
            document.getElementById("error3").style.display = "none"
        }, 2000);
    } else {
        index = $(".closeTab").index(this);
        $.ajax({
            url: "",
            type: 'post',
            data: {
                csrfmiddlewaretoken: csrf,
                closingTab: index,
                name: "closetab",
            },
            success: function(response) {
                tab = document.getElementsByClassName("tab")[index]
                tab.id = "closetab"
                setTimeout(function() { window.location.href = "http://127.0.0.1:8000/products/" + response.redirect; }, 200);
            }
        })

    }


});

$(document).ready(function() {
    csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value
    $("#addbut").click(function() {
        if (document.getElementsByClassName("tabs")[0].offsetWidth < 190) {
            //document.getElementById("error2").style.display = "block"
            setTimeout(function() {
                document.getElementById("error2").style.display = "none"
            }, 2000);
        } else {
            $.ajax({
                url: "",
                type: 'post',
                data: {
                    name: "newtab",
                    csrfmiddlewaretoken: csrf
                },
                success: function(response) {
                    aTab = document.createElement("button")
                    tab = document.createElement("div")
                    closeButton = document.createElement("button")
                    closeButton.className = "closeTab"
                    closeButton.innerHTML = "✖"
                    tab.className = "tab"
                    aTab.className = "tabs"

                    tab.appendChild(aTab)
                    tab.appendChild(closeButton)
                    tab.id = "newtab"
                    aTab.setAttribute("onclick", "window.location='http://127.0.0.1:8000/products" + "/" + ($('.tabs').length) + "'")
                    document.getElementById("tabcon").appendChild(tab)

                }
            })
        }
    });
});

$(document).on("keyup", '.myTextInputID', function(event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        var input = document.getElementsByClassName("myTextInputID")[0].value;
        if (input == "") {
            //document.getElementsByClassName("error")[2].style.display = "block"
            setTimeout(function() {
                document.getElementsByClassName("error")[2].style.display = "none"
            }, 2000);
        } else {
            if (input.includes("amazon")) {
                document.getElementsByClassName("amazonURL")[0].submit();
            } else {
                for (let index = 0; index < $(".rows").length; index++) {
                    document.getElementsByClassName("titlecontainerTEXT")[index].innerHTML = ""
                    document.getElementsByClassName("smallImage")[index].setAttribute("src", "")
                }
                for (let index = 0; index < $(".loading").length; index++) {
                    document.getElementsByClassName("loading")[index].style.display = "block"
                }
                if ($("#prodcon").is(":visible") == false) {
                    document.getElementById("prodcon").style.display = "block"
                    document.getElementById("containFORM").style.backgroundColor = "#12abd1"
                    document.getElementById("containFORM").style.borderBottomStyle = "none"
                    $.ajax({
                        url: "",
                        type: 'post',
                        data: {
                            name: "searching",
                            csrfmiddlewaretoken: csrf,
                            text: input,

                        },
                        success: function(response) {
                            productNames = JSON.parse(response.names)
                            productPrice = JSON.parse(response.prices)
                            productImages = JSON.parse(response.images)
                            for (let index = 0; index < productNames.length; index++) {
                                document.getElementsByClassName("smallImage")[index].setAttribute("src", productImages[index])
                                document.getElementsByClassName("titlecontainerTEXT")[index].innerHTML = productNames[index] + " - " + productPrice[index]
                            }
                            for (let index = 0; index < $(".loading").length; index++) {
                                document.getElementsByClassName("loading")[index].style.display = "none"
                            }
                        }
                    })
                } else {
                    for (let index = 0; index < $(".rows").length; index++) {
                        document.getElementsByClassName("titlecontainerTEXT")[index].innerHTML = ""
                        document.getElementsByClassName("smallImage")[index].setAttribute("src", "")
                    }
                    for (let index = 0; index < $(".loading").length; index++) {
                        document.getElementsByClassName("loading")[index].style.display = "block"
                    }
                    $.ajax({
                        url: "",
                        type: 'post',
                        data: {
                            name: "searching",
                            csrfmiddlewaretoken: csrf,
                            text: input,
                            versionOfSearch: "list",
                        },
                        success: function(response) {
                            productNames = JSON.parse(response.names)
                            productPrice = JSON.parse(response.prices)
                            productImages = JSON.parse(response.images)
                            for (let index = 0; index < productNames.length; index++) {
                                document.getElementsByClassName("smallImage")[index].setAttribute("src", productImages[index])
                                document.getElementsByClassName("titlecontainerTEXT")[index].innerHTML = productNames[index] + " - " + productPrice[index]
                            }
                            for (let index = 0; index < $(".loading").length; index++) {
                                document.getElementsByClassName("loading")[index].style.display = "none"
                            }
                        }
                    })
                }

            }
            window.addEventListener('click', function(e) {
                if (document.getElementById('containFORM').contains(e.target)) {
                    // Clicked in box
                } else {
                    document.getElementById("prodcon").style.display = "none"
                }
            });
        }
    }

});
$(".rows").on("click", function(event) {
    $.ajax({
        url: "",
        type: 'post',
        data: {
            text: document.getElementsByClassName("myTextInputID")[0].value,
            name: "choosing",
            versionOfSearch: "choose",
            chosenProduct: $(this).index(),
            csrfmiddlewaretoken: csrf,
        },
        success: function(response) {
            window.location.href = "http://127.0.0.1:8000/products/" + response.redirect, 200
        }
    })
})


function send_email() {
    csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value
    $.ajax({
        url: "",
        type: 'post',
        data: {
            csrfmiddlewaretoken: csrf,
            name: "verification_email",
        },
        success: function(response) {}

    })
}


//Ajax request to set a reminder for the user price

csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value
$("#sendReminder").click(function() {

    $.ajax({
        url: "",
        type: 'post',
        data: {
            name: "priceNoti",
            csrfmiddlewaretoken: csrf,
            reminderPrice: document.getElementById("NumberValue").value, //value of number input 
            reminderType: document.getElementById("methods").value
        },
        success: function(response) {}
    })
});

function Landing() {
    if (window.location.href.includes("product")) {
        document.getElementsByClassName("tabs")[0].click()
    } else {
        window.location.href = "http://127.0.0.1:8000";
        document.getElementsByClassName("tabs")[0].addEventListener("load", self.click);
    }

}


function greyout() {
    document.getElementsByClassName("row gutters-sm")[0].style.opacity = "0.2"
    document.getElementsByClassName("btn btn-danger")[0].style.opacity = "0.2"
    document.getElementsByClassName("btn btn-primary")[0].style.opacity = "0.2"
    document.getElementById("activate").style.opacity = "0.2"

};

$('#logoutModal').on('hidden.bs.modal', function() {
    document.getElementsByClassName("row gutters-sm")[0].style.opacity = "1"
    document.getElementsByClassName("btn btn-danger")[0].style.opacity = "1"
    document.getElementsByClassName("btn btn-primary")[0].style.opacity = "1"
    document.getElementById("activate").style.opacity = "1"
});
$('#changeEmailModal').on('hidden.bs.modal', function() {
    document.getElementsByClassName("row gutters-sm")[0].style.opacity = "1"
    document.getElementsByClassName("btn btn-danger")[0].style.opacity = "1"
    document.getElementsByClassName("btn btn-primary")[0].style.opacity = "1"
    document.getElementById("activate").style.opacity = "1"
});
$('#deleteModal').on('hidden.bs.modal', function() {
    document.getElementsByClassName("row gutters-sm")[0].style.opacity = "1"
    document.getElementsByClassName("btn btn-danger")[0].style.opacity = "1"
    document.getElementsByClassName("btn btn-primary")[0].style.opacity = "1"
    document.getElementById("activate").style.opacity = "1"
});
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})