document.addEventListener("DOMContentLoaded", function () {

  const themeSelect = document.getElementById("bgTheme");
  const themes = {
    dark: "linear-gradient(135deg,#0f0f0f,#181818)",
    blue: "linear-gradient(135deg,#0f2027,#203a43,#2c5364)",
    purple: "linear-gradient(135deg,#41295a,#2F0743)",
    green: "linear-gradient(135deg,#134E5E,#71B280)",
    red: "linear-gradient(135deg,#3b0a0a,#8b0000)",
    sunset: "linear-gradient(135deg,#ff7e5f,#feb47b)",
    space: "linear-gradient(135deg,#000428,#004e92)",
    pink: "linear-gradient(135deg,#ff9a9e,#fad0c4)"
  };
  function applyTheme(theme) {
    document.body.style.background = themes[theme] || themes.dark;
    localStorage.setItem("selectedTheme", theme);
  }
  const savedTheme = localStorage.getItem("selectedTheme");
  if (savedTheme) {
    applyTheme(savedTheme);

    if (themeSelect) {
      themeSelect.value = savedTheme;
    }
  }
  if (themeSelect) {
    themeSelect.addEventListener("change", function () {
      applyTheme(this.value);
    });
  }

});
