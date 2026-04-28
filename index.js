document.addEventListener("DOMContentLoaded", () => {
  fetch("navbar.html")
    .then(response => response.text())
    .then(data => {
      document.getElementById("navbar").innerHTML = data;

      setupLoginModal();
    });
});

function setupLoginModal() {
  const loginModal = document.getElementById("loginModal");
  const openLogin = document.getElementById("openLogin");
  const closeLogin = document.getElementById("closeLogin");

  openLogin.onclick = (e) => {
    e.preventDefault();
    loginModal.style.display = "block";
  };

  closeLogin.onclick = () => {
    loginModal.style.display = "none";
  };
}