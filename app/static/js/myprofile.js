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
// const interestsInput = document.getElementById("interestsInput");


const bioInput = document.getElementById("bioInput");

const displayGender = document.getElementById("displayGender");
const displayOrientation = document.getElementById("displayOrientation");

const genderInput = document.getElementById("genderInput");
const orientationInput = document.getElementById("orientationInput");

const orientationContainer = document.getElementById("orientationContainer");

editProfileBtn.addEventListener("click", (event) => {
  event.preventDefault();
  profileModal.style.display = "block";
});

closeProfile.addEventListener("click", () => {
  profileModal.style.display = "none";
});

// Function to verify manual text against Google Places

async function verifyLocationManually(text) {
    try {
        const { AutocompleteService } = await google.maps.importLibrary("places");
        const service = new AutocompleteService();
        const request = { input: text, types: ['(cities)'], componentRestrictions: { country: "au" } };
        
        return new Promise((resolve) => {
            service.getPlacePredictions(request, (predictions, status) => {
                if (status === "OK" && predictions.length > 0) {
                    resolve(predictions[0]);
                } else {
                    resolve(null);
                }
            });
        });
    } catch (e) {
        return null;
    }
}

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  // --- 1. Name Validation (Syntax Fixed) ---
  const nameValue = nameInput.value.trim();
  if (!nameValue) {
    alert("Name cannot be blank.");
    return;
  }

  // Pattern allows letters, spaces, hyphens, and apostrophes
  const nameRegex = /^[A-Za-z\s\-']+$/;
  if (!nameRegex.test(nameValue)) {
    alert("Name can only contain letters, spaces, hyphens, and apostrophes.");
    return;
  }

  if (nameValue.length < 2) {
    alert("Name must be at least 2 characters long.");
    return;
  }

  // --- 2. Age Check ---
  if (Number(ageInput.value) < 18) {
    alert("Age must be 18 or above.");
    return;
  }

  // --- 3. Location Validation (Async) ---
  const locIdInput = document.getElementById("locationPlaceIdInput"); 
  let placeId = locIdInput ? locIdInput.value : null;

  // Manual verification if user typed a city but didn't click a suggestion
  if (!placeId && locationInput.value.trim()) {
      const verified = await verifyLocationManually(locationInput.value.trim());
      if (verified) {
          if (locIdInput) locIdInput.value = verified.place_id;
          locationInput.value = verified.description;
          placeId = verified.place_id;
      }
  }

  if (!placeId) {
      alert("Please select a valid city in Australia from the suggestions.");
      return;
  }

  // --- 4. Gender and Orientation ---
  if (!genderInput.value || !orientationInput.value) {
    alert("Please select your Gender and Sexual Orientation.");
    return;
  }

  // --- 5. Interests ---
  const selectedInterests = Array.from(document.querySelectorAll('.interest-checkbox:checked')).map(cb => cb.value);
  if (selectedInterests.length === 0) {
    alert("Please select at least one interest.");
    return;
  }

  // --- 6. Bio Word Count ---
  const bioValue = bioInput.value.trim();
  const bioWordCount = bioValue.split(/\s+/).filter(Boolean).length;
  if (bioWordCount > 1000) {
    alert("Bio must be 1000 words or less.");
    return;
  }

  // --- Success: Update UI Display ---
  displayName.textContent = nameValue;
  displayAge.textContent = ageInput.value;
  displayLocation.textContent = locationInput.value;
  displayInterests.textContent = selectedInterests.join(", ");
  displayGender.textContent = genderInput.value;
  displayOrientation.textContent = orientationInput.value;
  displayBio.textContent = bioValue;

  // Handle Orientation visibility
  const showOrientationInput = document.getElementById("showOrientationInput");
  if (showOrientationInput && orientationContainer) {
      orientationContainer.style.display = showOrientationInput.checked ? "block" : "none";
  }

  // Close Modal
  profileModal.style.display = "none";
});
// profileForm.addEventListener("submit", async(event) => {
//   event.preventDefault();

//   const nameValue = nameInput.value.trim();

//   // 1. Name cannot be blank
//   if (!nameInput.value.trim()) {
//   if (!nameValue) {
//     alert("Name cannot be blank.");
//     return;
//   }

//   const nameRegex = /^[A-Za-z\s\-']+$/;

//   if (!nameRegex.test(nameValue)) {
//     alert("Name can only contain letters, spaces, hyphens, and apostrophes.");
//     return;
//   }

//   if (nameValue.length < 2) {
//     alert("Name must be at least 2 characters long.");
//     return;
//   }

//   // 2. Age check (Existing)
//   if (Number(ageInput.value) < 18) {
//     alert("Age must be 18 or above.");
//     return;
//   }

//   // 3. Location must be from Google suggestions
//   // We check if the hidden 'locationPlaceId' has a value
//   const locInput = document.getElementById("locationInput");
//   const locIdInput = document.getElementById("locationPlaceIdInput"); // Ensure this ID exists in HTML
  
//   let placeId = locIdInput.value;

//   // If the user typed manually and didn't trigger 'place_changed'
//   if (!placeId && locInput.value.trim()) {
//       const verified = await verifyLocationManually(locInput.value.trim());
//       if (verified) {
//           locIdInput.value = verified.place_id;
//           locInput.value = verified.description;
//           placeId = verified.place_id;
//       }
//   }

//   if (!placeId) {
//       alert("Please select a valid city in Australia from the suggestions.");
//       return;
//   }

//   // const placeId = document.getElementById("locationPlaceId").value;
//   // if (!placeId) {
//   //   alert("Please select a location from the dropdown suggestions.");
//   //   return;
//   // }

//   // 4. Gender and Orientation cannot be blank
//   if (!genderInput.value || !orientationInput.value) {
//     alert("Please select your Gender and Sexual Orientation.");
//     return;
//   }

//   const selectedInterests = Array.from(document.querySelectorAll('.interest-checkbox:checked')).map(cb => cb.value);
//   const bioWordCount = bioInput.value.trim().split(/\s+/).filter(Boolean).length;

//   // 5. Interest constraint (Frontend check)
//   if (selectedInterests.length === 0) {
//     alert("Please select at least one interest.");
//     return;
//   }

//   // 6. Bio word limitation
//   if (bioWordCount > 1000) {
//     alert("Bio must be 1000 words or less.");
//     return;
//   }

//   displayName.textContent = nameInput.value;
//   displayAge.textContent = ageInput.value;
//   displayLocation.textContent = locationInput.value;
//   // displayInterests.textContent = interestsInput.value;
//   displayInterests.textContent = selectedInterests.join(", ");
//   displayGender.textContent = genderInput.value;
//   displayOrientation.textContent = orientationInput.value;
//   displayBio.textContent = bioInput.value;
//   profileModal.style.display = "none";
// });

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

  const titleWords = storyTitleInput.value.trim().split(/\s+/).filter(Boolean).length;
  const descWords = storyDescriptionInput.value.trim().split(/\s+/).filter(Boolean).length;

  if (titleWords > 21) {
    alert("Title must be 21 words or less.");
    return; // Stops the execution
  }

  if (descWords > 1500) {
    alert("Description must be 1500 words or less.");
    return; // Stops the execution
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



