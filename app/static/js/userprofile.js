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



document.addEventListener("DOMContentLoaded", () => {
  const bioSpan = document.getElementById("displayBio");
  const bioModal = document.getElementById("bioViewer");
  const bioFullText = document.getElementById("bioViewerFullText");
  const closeBio = document.getElementById("closeBioViewer");
  const displayName = document.querySelector(".basic-info h1").textContent;

  // Open Modal
  bioSpan.addEventListener("click", () => {
    // Get the full text (textContent ignores the CSS clamping)
    bioFullText.textContent = bioSpan.textContent.trim();
    document.getElementById("bioViewerName").textContent = displayName + "'s Bio";
    
    bioModal.style.display = "block";
  });

  // Close Modal
  closeBio.addEventListener("click", () => {
    bioModal.style.display = "none";
  });

  // Close on outside click
  window.addEventListener("click", (event) => {
    if (event.target === bioModal) {
      bioModal.style.display = "none";
    }
  });
});