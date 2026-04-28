const profilePicInput = document.getElementById("profilePicInput");
const profileImage = document.querySelector(".myprofile-img");

// Only set default if image has no src
if (!profileImage.getAttribute("src")) {
  profileImage.src = "user_profile.png";
}

profilePicInput.addEventListener("change", function () {
  const file = this.files[0];

  // If user cancels file explorer, do nothing
  if (!file) {
    return;
  }

  const reader = new FileReader();

  reader.onload = function (e) {
    profileImage.src = e.target.result;
  };

  reader.readAsDataURL(file);
});