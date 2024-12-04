document.addEventListener("DOMContentLoaded", () => {
  const banner = document.getElementById("birthday-banner");
  const closeButton = document.getElementById("close-birthday-banner");

  const isBannerClosed = document.cookie.split("; ").find(
    row => row.startsWith("birthday_banner_closed=")
  );
  if (!isBannerClosed || isBannerClosed.split("=")[1] !== "true") {
    banner.style.display = "block";
  }
  closeButton.addEventListener("click", () => {
    banner.style.display = "none";
    document.cookie = "birthday_banner_closed=true; path=/; max-age=86400";
  });
});