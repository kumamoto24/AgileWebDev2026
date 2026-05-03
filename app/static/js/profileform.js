const editProfileBtn = document.getElementById("editProfileBtn");
const profileModal = document.getElementById("profileModal");
const profileForm = document.getElementById("profileForm");
const closeProfile = document.getElementById("closeProfile");

const displayName = document.getElementById("displayName");
const displayAge = document.getElementById("displayAge");
const displayLocation = document.getElementById("displayLocation");
const displayInterests = document.getElementById("displayInterests");
const displayBio = document.getElementById("displayBio");

const nameInput = document.getElementById("nameInput");
const ageInput = document.getElementById("ageInput");
const locationInput = document.getElementById("locationInput");
const interestsInput = document.getElementById("interestsInput");
const bioInput = document.getElementById("bioInput");

editProfileBtn.addEventListener("click", (event) => {
  event.preventDefault();
  profileModal.style.display = "block";
});

closeProfile.addEventListener("click", () => {
  profileModal.style.display = "none";
});

profileModal.addEventListener("click", (event) => {
  if (event.target === profileModal) {
    profileModal.style.display = "none";
  }
});

profileForm.addEventListener("submit", (event) => {
  event.preventDefault();

  displayName.textContent = nameInput.value;
  displayAge.textContent = ageInput.value;
  displayLocation.textContent = locationInput.value;
  displayInterests.textContent = interestsInput.value;
  displayBio.textContent = bioInput.value;

  profileModal.style.display = "none";
});

function initAutocomplete() {
  if (!window.google) {
    return;
  }

  const autocomplete = new google.maps.places.Autocomplete(locationInput, {
    types: ["(cities)"],
    fields: ["place_id", "name", "formatted_address"]
  });

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();

    locationInput.value = place.formatted_address || place.name || "";
    document.getElementById("locationPlaceId").value = place.place_id || "";
  });
}
