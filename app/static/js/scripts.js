

  // This file is used to store javascript functions for the project
  // Some js functions are also present in settings.html and foryou.html

  // Function to toggle visibility of media type fields
  function toggleFields() {
    const type = document.getElementById("mediaType").value;

    const sections = {
      book: document.getElementById("bookFields"),
      movie: document.getElementById("movieFields"),
      tv_show: document.getElementById("tvShowFields"),
      music: document.getElementById("musicFields")
    };

    // Hide all sections & remove 'required' from genre dropdowns
    Object.values(sections).forEach(section => {
      section.style.display = "none";
      const genreField = section.querySelector("select");
      if (genreField) genreField.removeAttribute("required");
    });

    // Show selected section & apply 'required' to its genre dropdown
    if (sections[type]) {
      sections[type].style.display = "block";
      const genreField = sections[type].querySelector("select");
      if (genreField) genreField.setAttribute("required", "true");
    }
  }

  document.addEventListener("DOMContentLoaded", toggleFields);

// Function to handle friend search submission
function submitFriendSearch() {
      const query = document.getElementById("friend-search-input").value;
      if (query.trim() !== "") {
        window.location.href = "/search?query=" + encodeURIComponent(query);
      }
}

// Function to check if passwords match
function checkPasswords() {
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm_password").value;

    if (password !== confirm) {
      alert("Passwords do not match!");
      return false; // Prevent form submission
    }
    return true; // Allow form to submit to Flask
  }

// Function to open the image modal
function openImageModal(src) {
    const modal = document.getElementById("imageModal");
    const modalImage = document.getElementById("modalImage");
    modalImage.src = src;
    modal.style.display = "block";
  }

// Function to close the image modal
function closeImageModal() {
    const modal = document.getElementById("imageModal");
    modal.style.display = "none";
  }

  // Close the modal when clicking outside the image
  window.onclick = function (event) {
    const modal = document.getElementById("imageModal");
    if (event.target == modal) {
      modal.style.display = "none";
    }
  };

// Function to handle notification click
function markAllAsRead() {
    fetch(`/mark_all_notifications_read`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Mark all notifications as seen
          const notifications = document.querySelectorAll(".notification-item");
          notifications.forEach((item) => {
            item.classList.add("seen");
            const markReadBtn = item.querySelector(".mark-read-btn");
            if (markReadBtn) markReadBtn.remove();
          });

          // Clear the notification badge
          const notificationBadge = document.querySelector(
            ".notification-badge"
          );
          if (notificationBadge) notificationBadge.remove();
        } else {
          alert(data.message);
        }
      })
      .catch((error) => {
        console.error("Error marking all notifications as read:", error);
      });
  }