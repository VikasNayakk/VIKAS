const deployProgress = document.getElementById("deployProgress");
const totalHours = document.getElementById("totalHours");
const floatingCard = document.querySelector("[data-float]");

function animateProgress() {
  if (!deployProgress) {
    return;
  }

  const target = 88;
  let current = 0;

  const timer = setInterval(() => {
    current += 1;
    deployProgress.style.width = `${current}%`;

    if (current >= target) {
      clearInterval(timer);
    }
  }, 20);
}

function animateHours() {
  if (!totalHours) {
    return;
  }

  const finalValue = 12340;
  let value = 11800;

  const timer = setInterval(() => {
    value += 12;
    if (value >= finalValue) {
      value = finalValue;
      clearInterval(timer);
    }
    totalHours.textContent = `${value}h`;
  }, 22);
}

function addHeroFloat() {
  if (!floatingCard) {
    return;
  }

  window.addEventListener("mousemove", (event) => {
    const x = (event.clientX / window.innerWidth - 0.5) * 8;
    const y = (event.clientY / window.innerHeight - 0.5) * 8;
    floatingCard.style.transform = `translate(${x}px, ${y}px)`;
  });
}

function addImageFallback() {
  const fallback =
    "data:image/svg+xml;utf8," +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1a4eb9"/><stop offset="1" stop-color="#7a2adf"/></linearGradient></defs><rect width="400" height="400" fill="url(#g)"/><text x="200" y="210" text-anchor="middle" fill="#dff6ff" font-size="28" font-family="Arial">ALIENS CHARACTER</text></svg>'
    );

  document.querySelectorAll("img").forEach((img) => {
    img.addEventListener("error", () => {
      img.src = fallback;
    });
  });
}

animateProgress();
animateHours();
addHeroFloat();
addImageFallback();
