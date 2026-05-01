
async function loadRecommendedProfiles() {
    try {
    const response = await fetch("/api/recommended-profiles");
    const profiles = await response.json();

    displayProfiles(profiles);
    } catch (error) {
    document.getElementById("profileList").innerHTML =
        "<p>Failed to load profiles.</p>";
    }
}

async function searchProfiles() {
    const keyword = document.getElementById("keywordInput").value;
    const location = document.getElementById("locationInput").value;
    const locationPlaceId = document.getElementById("locationPlaceIdInput").value;
    const selectedInterests = getSelectedInterests();

    const queryString = new URLSearchParams({
    keyword: keyword,
    location: location,
    location_place_id: locationPlaceId
    });

    selectedInterests.forEach(interest => {
      queryString.append("interests", interest);
    });

    try {
    const response = await fetch(`/api/search-profiles?${queryString}`);
    const profiles = await response.json();

    displayProfiles(profiles);
    } catch (error) {
    document.getElementById("profileList").innerHTML =
        "<p>Search failed. Please try again.</p>";
    }
}

function displayProfiles(profiles) {
    const profileList = document.getElementById("profileList");
    profileList.innerHTML = "";

    if (profiles.length === 0) {
    profileList.innerHTML = "<p>No profiles found.</p>";
    return;
    }

    profiles.forEach(profile => {
    const distanceText =
    profile.distance !== undefined && profile.distance !== null
      ? ` · ${profile.distance} km away`
      : "";
    const card = `
        <div class="col-md-4">
        <div class="card profilecard-custom">
            <img 
            src="${profile.image}" 
            class="card-img-top uniform-img" 
            alt="${profile.name}"
            >

            <div class="card-body">
            <h5 class="card-title">${profile.name}, ${profile.age}</h5>
            <p class="card-text text-muted">${profile.location} ${distanceText} </p>

            <div class="mb-3">
                ${(profile.interests || []).map(interest => `
                <span class="tag">${interest}</span>
                `).join("")}
            </div>

            <a href="/profile/${profile.id}" class="btn btn-primary-custom w-100" style="font-size: 1rem;">
                View Profile
            </a>
            </div>
        </div>
        </div>
    `;

    profileList.innerHTML += card;
    });
}

function getSelectedInterests() {
  return Array.from(document.querySelectorAll(".interest-checkbox:checked"))
    .map(checkbox => checkbox.value);
}

function updateInterestDropdownLabel() {
  const interestDropdownButton = document.getElementById("interestDropdownButton");
  const selectedInterests = getSelectedInterests();

  if (!interestDropdownButton) {
    return;
  }

  if (selectedInterests.length === 0) {
    interestDropdownButton.textContent = "Any interest";
  } else if (selectedInterests.length === 1) {
    interestDropdownButton.textContent = selectedInterests[0];
  } else {
    interestDropdownButton.textContent = `${selectedInterests.length} interests selected`;
  }
}

async function initLocationAutocomplete() {
  const locationInput = document.getElementById("locationInput");
  const locationPlaceIdInput = document.getElementById("locationPlaceIdInput");

  if (!locationInput || !locationPlaceIdInput || !window.google?.maps?.importLibrary) {
    return;
  }

  try {
    const { Autocomplete } = await google.maps.importLibrary("places");

    const autocomplete = new Autocomplete(locationInput, {
      componentRestrictions: { country: "au" },
      fields: [
        "address_components",
        "formatted_address",
        "geometry",
        "name",
        "place_id"
      ],
      types: ["(cities)"]
    });

    locationInput.addEventListener("input", function () {
      locationPlaceIdInput.value = "";
    });

    autocomplete.addListener("place_changed", function () {
      const place = autocomplete.getPlace();

      locationInput.value =
        place.formatted_address ||
        place.name ||
        locationInput.value ||
        "";

      locationPlaceIdInput.value = place.place_id || "";

      console.log("Selected city:", {
        name: place.name,
        formattedAddress: place.formatted_address,
        placeId: place.place_id,
        location: place.geometry?.location,
        addressComponents: place.address_components
      });
    });
  } catch (error) {
    console.error("Failed to load Google Places autocomplete:", error);
  }
}

window.initLocationAutocomplete = initLocationAutocomplete;

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".interest-checkbox").forEach(checkbox => {
    checkbox.addEventListener("change", updateInterestDropdownLabel);
  });

  updateInterestDropdownLabel();
  loadRecommendedProfiles();
});
