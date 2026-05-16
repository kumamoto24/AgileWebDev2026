// Like button

function toggleLike(profileId) {
    const likeBtn = document.getElementById('likeBtn');
    if (!likeBtn || !profileId) {
        return;
    }
    
    // 1. Optimistic UI update (change color immediately)
    const isLiked = likeBtn.classList.toggle('active');
    likeBtn.textContent = isLiked ? '❤️ Liked' : '🤍 Like';

    // 2. Send the data
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    fetch(`/profile/${profileId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken || ''
        },
        body: JSON.stringify({ 
            profile_id: profileId, // Explicitly tell the backend which ID
            action: isLiked ? 'like' : 'unlike' 
        })
    })
    .then(response => {
        if (!response.ok) {
            // 3. Revert if the server fails
            throw new Error('Server error');
        }
        return response.json();
    })
    .then(data => {
        console.log('Database updated:', data);
    })
    .catch((error) => {
        // 4. Revert UI if error occurs
        console.error('Error:', error);
        likeBtn.classList.toggle('active');
        likeBtn.textContent = !isLiked ? '❤️ Liked' : '🤍 Like';
        alert("Couldn't save like. Please try again.");
    });
}



document.addEventListener("DOMContentLoaded", () => {
  const viewer = document.getElementById("storyViewer");
  const viewerImg = document.getElementById("viewerImg");
  const viewerTitle = document.getElementById("viewerTitle");
  const viewerDescription = document.getElementById("viewerDescription");
  const closeViewer = document.getElementById("closeViewer");
  if (!viewer || !viewerImg || !viewerTitle || !viewerDescription || !closeViewer) {
    return;
  }

  const openStoryViewer = (card) => {
    const image = card.querySelector(".story-img");
    const title = card.querySelector(".card-title");
    const description = card.querySelector(".card-text");

    viewerImg.src = image ? image.src : "";
    viewerTitle.textContent = title ? title.textContent.trim() : "";
    viewerDescription.textContent = description ? description.textContent.trim() : "";
    viewer.style.display = "block";
  };

  // Select all story cards
  const storyCards = document.querySelectorAll(".story-section .card");

  storyCards.forEach(card => {
    card.addEventListener("click", () => {
      openStoryViewer(card);
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
  const displayName = document.querySelector(".basic-info h1");
  const bioViewerName = document.getElementById("bioViewerName");
  if (!bioSpan || !bioModal || !bioFullText || !closeBio || !displayName || !bioViewerName) {
    return;
  }

  // Open Modal
  bioSpan.addEventListener("click", () => {
    // Get the full text (textContent ignores the CSS clamping)
    bioFullText.textContent = bioSpan.textContent.trim();
    bioViewerName.textContent = `${displayName.textContent.trim()}'s Bio`;
    
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
