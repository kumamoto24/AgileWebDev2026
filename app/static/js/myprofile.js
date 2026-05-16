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
                    const prediction = predictions[0];
                    const detailsService = new google.maps.places.PlacesService(document.createElement("div"));

                    detailsService.getDetails(
                      {
                        placeId: prediction.place_id,
                        fields: ["place_id", "formatted_address", "name", "geometry"]
                      },
                      (place, detailsStatus) => {
                        if (detailsStatus !== "OK" || !place) {
                          resolve(null);
                          return;
                        }

                        resolve({
                          place_id: place.place_id,
                          description: place.formatted_address || place.name || prediction.description,
                          latitude: place.geometry?.location?.lat(),
                          longitude: place.geometry?.location?.lng()
                        });
                      }
                    );
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

  // 1. Name validation
  const nameValue = nameInput.value.trim();

  if (!nameValue) {
    alert("Name cannot be blank.");
    return;
  }

  const nameRegex = /^[A-Za-z\s\-']+$/;
  if (!nameRegex.test(nameValue)) {
    alert("Name can only contain letters, spaces, hyphens, and apostrophes.");
    return;
  }

  if (nameValue.length < 2) {
    alert("Name must be at least 2 characters long.");
    return;
  }

  // 2. Age validation
  if (Number(ageInput.value) < 18) {
    alert("Age must be 18 or above.");
    return;
  }

  // 3. Location validation
  const locIdInput = document.getElementById("locationPlaceId");
  let placeId = locIdInput ? locIdInput.value : null;

  if (!placeId && locationInput.value.trim()) {
    const verified = await verifyLocationManually(locationInput.value.trim());

    if (verified) {
      if (locIdInput) locIdInput.value = verified.place_id;
      locationInput.value = verified.description;
      document.getElementById("locationLatitude").value = verified.latitude || "";
      document.getElementById("locationLongitude").value = verified.longitude || "";
      placeId = verified.place_id;
    }
  }

  if (!placeId) {
    alert("Please select a valid city in Australia from the suggestions.");
    return;
  }

  // 4. Gender and orientation
  if (!genderInput.value || !orientationInput.value) {
    alert("Please select your Gender and Sexual Orientation.");
    return;
  }

  // 5. Interests
  const selectedInterests = Array.from(
    document.querySelectorAll(".interest-checkbox:checked")
  );

  if (selectedInterests.length === 0) {
    alert("Please select at least one interest.");
    return;
  }

  // 6. Bio word count
  const bioValue = bioInput.value.trim();
  const bioWordCount = bioValue.split(/\s+/).filter(Boolean).length;

  if (bioWordCount > 1000) {
    alert("Bio must be 1000 words or less.");
    return;
  }

  // 7. If all validation passes, submit form to Flask
  profileForm.submit();
});

function initAutocomplete() {
  if (!window.google) {
    return;
  }

  const autocomplete = new google.maps.places.Autocomplete(locationInput, {
    types: ["(cities)"],
    fields: ["place_id", "name", "formatted_address", "geometry"]
  });

  autocomplete.addListener("place_changed", () => {
    const place = autocomplete.getPlace();

    locationInput.value = place.formatted_address || place.name || "";
    document.getElementById("locationPlaceId").value = place.place_id || "";

    if (place.geometry && place.geometry.location) {
      document.getElementById("locationLatitude").value = place.geometry.location.lat();
      document.getElementById("locationLongitude").value = place.geometry.location.lng();
    }
  });
}

// profileimage

const profilePicInput = document.getElementById("profilePicInput");
const profileImage = document.querySelector(".myprofile-img");

profilePicInput.addEventListener("change", async function () {
  const file = this.files[0];

  if (!file) {
    return;
  }

  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const formData = new FormData();
  formData.append("profilePicture", file);
  formData.append("csrf_token", csrfToken || "");

  try {
    const response = await fetch("/profile/image", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      alert("Failed to upload profile picture.");
      return;
    }

    const result = await response.json();

    if (result.profile_image_url) {
      profileImage.src = result.profile_image_url;
    }
  } catch (error) {
    console.error("Profile image upload error:", error);
    alert("Network error. Please check your connection and try again.");
  }
});




// storymodal

const storyModal = document.getElementById("storyModal");
const storyForm = document.getElementById("storyForm");
const closeStory = document.getElementById("closeStory");

const storyPicInput = document.getElementById("storyPicInput");
const storyTitleInput = document.getElementById("storyTitleInput");
const storyDescriptionInput = document.getElementById("storyDescriptionInput");
const storyOrderInput = document.getElementById("storyOrderInput");

let selectedStoryCard = null;

function openStoryEditor(card) {
  selectedStoryCard = card;

  storyOrderInput.value = card.dataset.storyOrder;
  storyTitleInput.value = card.dataset.storyTitle || "";
  storyDescriptionInput.value = card.dataset.storyDescription || "";
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


storyForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (!selectedStoryCard) {
    return;
  }

  // --- 1. Validation Logic ---
  const titleValue = storyTitleInput.value.trim();
  const descValue = storyDescriptionInput.value.trim();
  
  const titleWords = titleValue.split(/\s+/).filter(Boolean).length;
  const descWords = descValue.split(/\s+/).filter(Boolean).length;

  if (titleWords > 21) {
    alert("Title must be 21 words or less.");
    return;
  }

  if (descWords > 1500) {
    alert("Description must be 1500 words or less.");
    return;
  }

  // --- 2. Prepare Data for Backend ---
  // Using FormData because it handles file uploads (images) automatically
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
  const formData = new FormData();
  formData.append("title", titleValue);
  formData.append("description", descValue);
  formData.append("display_order", storyOrderInput.value);
  formData.append("csrf_token", csrfToken || "");
  
  // Get the file from input
  const file = storyPicInput.files[0];
  if (file) {
    formData.append("image_path", file);
  }
  

  // --- 3. Send Data to Backend ---
  try {
    const response = await fetch("/update-story", {
      method: "POST",
      body: formData // Note: Do NOT set Content-Type header when using FormData
    });

    if (response.ok) {
      const result = await response.json();

      // --- 4. Success: Update UI Display ---
      const savedTitle = result.title || titleValue || "Untitled Story";
      const savedDescription = result.description || descValue || "No description yet.";

      selectedStoryCard.querySelector(".story-title").textContent = savedTitle;
      selectedStoryCard.querySelector(".story-description").textContent = savedDescription;
      selectedStoryCard.dataset.storyTitle = savedTitle;
      selectedStoryCard.dataset.storyDescription = result.description || descValue;
      selectedStoryCard.classList.remove("story-card-empty");

      // Update image preview using the local file (fast) or server path
      if (file) {
        const reader = new FileReader();
        reader.onload = function (loadEvent) {
          selectedStoryCard.querySelector(".story-img").src = loadEvent.target.result;
        };
        reader.readAsDataURL(file);
      } else if (result.image_url) {
        selectedStoryCard.querySelector(".story-img").src = result.image_url;
      }

      storyModal.style.display = "none";
      alert("Story updated successfully!");
    } else {
      alert("Failed to save story on the server.");
    }
  } catch (error) {
    console.error("Connection error:", error);
    alert("Network error. Please check your connection and try again.");
  }
});
