const editProfileBtn = document.getElementById("editProfileBtn");
const profileModal = document.getElementById("profileModal");
const profileForm = document.getElementById("profileForm");
const closeProfile = document.getElementById("closeProfile");

editProfileBtn.onclick = (e) => {
  e.preventDefault();
  profileModal.style.display = "block";
};

closeProfile.onclick = () => {
  profileModal.style.display = "none";
};

window.onclick = (e) => {
  if (e.target === profileModal) {
    profileModal.style.display = "none";
  }
};

profileForm.onsubmit = (e) => {
  e.preventDefault();

  displayName.textContent = nameInput.value;
  displayAge.textContent = ageInput.value;
  displayLocation.textContent = locationInput.value;
  displayInterests.textContent = interestsInput.value;
  displayBio.textContent = bioInput.value;

  profileModal.style.display = "none";
};