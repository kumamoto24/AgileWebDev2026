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
