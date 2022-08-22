const alert = document.getElementById("alert")
if (alert) {
    setTimeout(() => {
        alert.remove()
    }, 5000)
}