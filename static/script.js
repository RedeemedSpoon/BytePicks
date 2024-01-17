document.addEventListener("DOMContentLoaded", function () {
   if (window.location.pathname === "/") {
      const altHeader = document.querySelector(".alt_header");
      const logo = document.querySelector(".alt_header img");
      const welcomeImg = document.querySelector('img[alt="Welcome Image"]');
      const sections = Array.from(document.querySelectorAll("section"));
      const typetext = document.querySelector("#welcome_text");
      const textList = ["Your Gateway to Wonders!", "Discover, Learn, and Thrive.", "Quality Over Quantity.", "Tech Vibes, No Limits!", "Masterpieces at Your Fingertips!", "Elevate Your Online Experience!", "Where Ideas Take Flight!"];
      let index = 0;
      let charIndex = 0;
      let isDeleting = false;

      function typeText() {
         let currentText = textList[index];
         if (!isDeleting) {
            typetext.textContent = currentText.substring(0, charIndex);
            charIndex++;

            if (charIndex > currentText.length) {
               isDeleting = true;
               setTimeout(typeText, 2000);
            } else {
               setTimeout(typeText, 75);
            }
         } else {
            typetext.textContent = currentText.substring(0, charIndex);
            charIndex--;

            if (charIndex < 0) {
               isDeleting = false;
               index = (index + 1) % textList.length;
               setTimeout(typeText, 1000);
            } else {
               setTimeout(typeText, 50);
            }
         }
      }

      if (welcomeImg && typetext) {
         typeText();
      }

      let sectionTriggers = sections.map(() => false);
      const activateSection = (section, triggerPosition, offset, triggeredFlag) => {
         if (!triggeredFlag && window.scrollY - offset > triggerPosition) {
            section.classList.add("activated");
            triggeredFlag = true;
         }
         return triggeredFlag;
      };

      window.addEventListener("scroll", () => {
         const triggerWelcomeImgPosition = welcomeImg.getBoundingClientRect().bottom + 500;

         if (window.scrollY > triggerWelcomeImgPosition) {
            altHeader.classList.add("new_alt_header");
            logo.style.filter = "invert(0%)";
         } else {
            altHeader.classList.remove("new_alt_header");
            logo.style.filter = "invert(90%)";
         }

         sections.forEach((section, index) => {
            const triggerSectionPosition = section.getBoundingClientRect().top;
            const offset = index <= 3 ? index * 500 + 250 : 0;
            sectionTriggers[index] = activateSection(section, triggerSectionPosition, offset, sectionTriggers[index]);
         });
      });
   }
});
