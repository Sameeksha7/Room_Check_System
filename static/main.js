
function setMinVal(){
    var today = document.getElementsByName("checkin")[0];
    document.getElementsByName("checkout")[0].setAttribute('min', today);
}