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




function initAutocomplete() {
  const input = document.getElementById("locationInput");

  const autocomplete = new google.maps.places.Autocomplete(input, {
    types: ["(cities)"],
    fields: ["place_id", "name", "formatted_address"]
  });

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();

    document.getElementById("locationInput").value =
      place.formatted_address || place.name;

    document.getElementById("locationPlaceId").value =
      place.place_id;
  });
}