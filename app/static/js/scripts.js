function toggleFields() {
    const type = document.getElementById("mediaType").value;
    const sections = ["book", "movie", "tvShow", "music"];
  
    sections.forEach(section => {
      const sectionDiv = document.getElementById(section + "Fields");
      if (sectionDiv) {
        sectionDiv.style.display = section === type ? "block" : "none";
      }
    });
  }