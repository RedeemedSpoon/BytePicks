const textContent = document.getElementById("welcome_text");
const phrases = ["Welcome to BytePicks", "We code with passion", "Innovate with us", "Learn and grow with BytePicks"];
let index = 0;
let charIndex = 0;
let isDeleting = false;

function typeText() {
   const currentPhrase = phrases[index];

   if (!isDeleting) {
      textContent.textContent = currentPhrase.substring(0, charIndex);
      charIndex++;

      if (charIndex > currentPhrase.length) {
         isDeleting = true;
         setTimeout(deleteText, 2000);
      } else {
         setTimeout(typeText, 100);
      }
   } else {
      textContent.textContent = currentPhrase.substring(0, charIndex);
      charIndex--;

      if (charIndex < 0) {
         isDeleting = false;
         index = (index + 1) % phrases.length;
         setTimeout(typeText, 100);
      } else {
         setTimeout(deleteText, 50);
      }
   }
}

function deleteText() {
   typeText();
}

if (window.location.href.includes("/")) {
   typeText();
}
