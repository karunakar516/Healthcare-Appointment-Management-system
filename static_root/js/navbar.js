const origin_top_right = document.querySelector(".origin-top-right")
const profile_button = document.querySelector('.profile-button')
const toggle_btn = document.querySelector(".toggle-btn ")
const mobile_menu = document.querySelector("#mobile-menu")



// top right profile dropdown
profile_button.addEventListener("click", () => {
    origin_top_right.classList.toggle("origin-top-right-show")
})

document.addEventListener('click', function (event) {
    if (event.target.closest(".profile-button")) return
    origin_top_right.classList.remove('origin-top-right-show')

})



// toggle nav
toggle_btn.addEventListener("click", () => {
    mobile_menu.classList.toggle("show-mobile-menu")
})

document.addEventListener('click', function (event) {
    if (event.target.closest(".toggle-btn")) return
    mobile_menu.classList.remove("show-mobile-menu")
})
