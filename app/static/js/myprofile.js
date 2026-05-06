// profileform
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


profileForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (Number(ageInput.value) < 18) {
    alert("Age must be 18 or above.");
    return;
  }

  const bioWordCount = bioInput.value.trim().split(/\s+/).filter(Boolean).length;

  if (bioWordCount > 1000) {
    alert("Bio must be 1000 words or less.");
    return;
  }

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

// profileimage

const profilePicInput = document.getElementById("profilePicInput");
const profileImage = document.querySelector(".myprofile-img");

profilePicInput.addEventListener("change", function () {
  const file = this.files[0];

  if (!file) {
    return;
  }

  const reader = new FileReader();

  reader.onload = function (event) {
    profileImage.src = event.target.result;
  };

  reader.readAsDataURL(file);
});


// storymodal

const storyModal = document.getElementById("storyModal");
const storyForm = document.getElementById("storyForm");
const closeStory = document.getElementById("closeStory");

const storyPicInput = document.getElementById("storyPicInput");
const storyTitleInput = document.getElementById("storyTitleInput");
const storyDescriptionInput = document.getElementById("storyDescriptionInput");

let selectedStoryCard = null;

function openStoryEditor(card) {
  selectedStoryCard = card;

  storyTitleInput.value = card.querySelector(".story-title").textContent;
  storyDescriptionInput.value = card.querySelector(".story-description").textContent.trim();
  storyPicInput.value = "";

  storyModal.style.display = "block";
}

document.querySelectorAll(".story-card").forEach((card) => {
  card.addEventListener("click", () => openStoryEditor(card));
  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openStoryEditor(card);
    }
  });
});

closeStory.addEventListener("click", () => {
  storyModal.style.display = "none";
});

storyModal.addEventListener("click", (event) => {
  if (event.target === storyModal) {
    storyModal.style.display = "none";
  }
});

storyForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!selectedStoryCard) {
    return;
  }

  selectedStoryCard.querySelector(".story-title").textContent = storyTitleInput.value;
  selectedStoryCard.querySelector(".story-description").textContent = storyDescriptionInput.value;

  const file = storyPicInput.files[0];

  if (file) {
    const reader = new FileReader();

    reader.onload = function (loadEvent) {
      selectedStoryCard.querySelector(".story-img").src = loadEvent.target.result;
    };

    reader.readAsDataURL(file);
  }

  storyModal.style.display = "none";
});