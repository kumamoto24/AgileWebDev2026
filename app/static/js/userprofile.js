document.addEventListener("DOMContentLoaded", () => {
  const viewer = document.getElementById("storyViewer");
  const viewerImg = document.getElementById("viewerImg");
  const viewerTitle = document.getElementById("viewerTitle");
  const viewerDescription = document.getElementById("viewerDescription");
  const closeViewer = document.getElementById("closeViewer");

  // Select all story cards
  const storyCards = document.querySelectorAll(".story-section .card");

  storyCards.forEach(card => {
    card.addEventListener("click", () => {
      // Extract data from the clicked card
      const imgPath = card.querySelector(".story-img").src;
      const title = card.querySelector(".card-title").textContent;
      const description = card.querySelector(".card-text").textContent;

      // Inject into modal
      viewerImg.src = imgPath;
      viewerTitle.textContent = title;
      viewerDescription.textContent = description;

      // Show modal
      viewer.style.display = "block";
    });
  });

  // Close when clicking 'X'
  closeViewer.addEventListener("click", () => {
    viewer.style.display = "none";
  });

  // Close when clicking outside the box
  window.addEventListener("click", (event) => {
    if (event.target === viewer) {
      viewer.style.display = "none";
    }
  });
});