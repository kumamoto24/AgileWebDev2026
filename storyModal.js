const storyModal = document.getElementById("storyModal");
const storyForm = document.getElementById("storyForm");
const closeStory = document.getElementById("closeStory");

const storyPicInput = document.getElementById("storyPicInput");
const storyTitleInput = document.getElementById("storyTitleInput");
const storyDescriptionInput = document.getElementById("storyDescriptionInput");

let selectedStoryCard = null;

document.querySelectorAll(".story-card").forEach((card) => {
  card.onclick = () => {
    selectedStoryCard = card;

    storyTitleInput.value = card.querySelector(".story-title").textContent;
    storyDescriptionInput.value = card.querySelector(".story-description").textContent.trim();

    storyPicInput.value = "";

    storyModal.style.display = "block";
  };
});

closeStory.onclick = () => {
  storyModal.style.display = "none";
};

storyForm.onsubmit = (e) => {
  e.preventDefault();

  selectedStoryCard.querySelector(".story-title").textContent = storyTitleInput.value;
  selectedStoryCard.querySelector(".story-description").textContent = storyDescriptionInput.value;

  const file = storyPicInput.files[0];

  if (file) {
    const reader = new FileReader();

    reader.onload = function (e) {
      selectedStoryCard.querySelector(".story-img").src = e.target.result;
    };

    reader.readAsDataURL(file);
  }

  storyModal.style.display = "none";
};