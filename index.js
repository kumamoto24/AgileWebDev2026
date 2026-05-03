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

// Fake user data
const user = {
  profilePic: "user_profile.png",
  name: "Jane Doe",
  age: 24,
  location: "Perth, Australia",
  interests: "Music, Movies, Fitness, Cooking",
  bio: "I love coffee, music, traveling, and meeting new people!",

  stories: [
    {
      pic: "beach.jpg",
      title: "Beach Day",
      description: "A day at the beach."
    },
    {
      pic: "coffee.jpg",
      title: "Coffee Date",
      description: "Coffee date vibes."
    },
    {
      pic: "operahouse.jpg",
      title: "Operahouse",
      description: "Operahouse sightseeing."
    }
  ]
};

// Display profile data
document.querySelector(".myprofile-img").src = user.profilePic;
document.getElementById("displayName").textContent = user.name;
document.getElementById("displayAge").textContent = user.age;
document.getElementById("displayLocation").textContent = user.location;
document.getElementById("displayInterests").textContent = user.interests;
document.getElementById("displayBio").textContent = user.bio;

// Display story cards
const storyCards = document.querySelectorAll(".story-card");

storyCards.forEach((card, index) => {
  card.querySelector(".story-img").src = user.stories[index].pic;
  card.querySelector(".story-title").textContent = user.stories[index].title;
  card.querySelector(".story-description").textContent = user.stories[index].description;
});