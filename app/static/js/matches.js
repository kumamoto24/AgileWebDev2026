function displayProfiles(profiles, listId, emptyMessage) {
  const profileList = document.getElementById(listId);
  profileList.innerHTML = "";

  if (!profiles || profiles.length === 0) {
    profileList.innerHTML = `<p class="text-muted">${emptyMessage}</p>`;
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
            <p class="card-text text-muted">${profile.location || ""}${distanceText}</p>

            <div class="mb-3 profile-card-interests">
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

fetch("/api/matches")
  .then(response => response.json())
  .then(data => {
    displayProfiles(
      data.likerprofiles,
      "likedYouList",
      "Users who like your profile will show up here."
    );

    displayProfiles(
      data.likedprofiles,
      "youLikedList",
      "Profiles you like will show up here."
    );
  })
  .catch(error => {
    console.error("Error loading matches:", error);

    document.getElementById("likedYouList").innerHTML =
      "<p>Could not load users who liked you.</p>";

    document.getElementById("youLikedList").innerHTML =
      "<p>Could not load profiles you liked.</p>";
  });




// function displayProfiles(profiles) {
//   const profileList = document.getElementById("profileList");
//   profileList.innerHTML = "";

//   if (!profiles || profiles.length === 0) {
//     profileList.innerHTML = "<p>No users have liked you yet.</p>";
//     return;
//   }

//   profiles.forEach(profile => {
//     const distanceText =
//       profile.distance !== undefined && profile.distance !== null
//         ? ` · ${profile.distance} km away`
//         : "";

//     const card = `
//       <div class="col-md-4">
//         <div class="card profilecard-custom">
//           <img 
//             src="${profile.image}" 
//             class="card-img-top uniform-img" 
//             alt="${profile.name}"
//           >

//           <div class="card-body">
//             <h5 class="card-title">${profile.name}, ${profile.age}</h5>
//             <p class="card-text text-muted">${profile.location || ""}${distanceText}</p>

//             <div class="mb-3 profile-card-interests">
//               ${(profile.interests || []).map(interest => `
//                 <span class="tag">${interest}</span>
//               `).join("")}
//             </div>

//             <a href="/profile/${profile.id}" class="btn btn-primary-custom w-100" style="font-size: 1rem;">
//               View Profile
//             </a>
//           </div>
//         </div>
//       </div>
//     `;

//     profileList.innerHTML += card;
//   });
// }

// fetch("/api/matches")
//   .then(response => response.json())
//   .then(data => {
//     displayProfiles(data.profiles);
//   })
//   .catch(error => {
//     console.error("Error loading matches:", error);
//     document.getElementById("profileList").innerHTML =
//       "<p>Could not load matches.</p>";
//   });