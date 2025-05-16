  //projects js functions stored here
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
