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
               setTimeout(typeText, 1750);
            } else {
               setTimeout(typeText, 75);
            }
         } else {
            typetext.textContent = currentText.substring(0, charIndex);
            charIndex--;

            if (charIndex < 0) {
               isDeleting = false;
               index = (index + 1) % textList.length;
               setTimeout(typeText, 750);
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
   } else if (window.location.pathname === "/Dashboard") {
      $(document).ready(function () {
         $("select").change(function () {
            updateURL();
         });

         function updateURL() {
            let time = $("#time").val();
            let language = $("#language").val();
            let url = `${window.location.pathname}?time=${time}&lang=${language}`;
            window.location.href = url;
         }
      });
   }
   if (window.location.pathname === "/Api-Docs") {
      const languageButtons = document.querySelectorAll(".programmingLanguage");
      const codeBlocks = document.querySelectorAll(".code");
      function showCode(language) {
         codeBlocks.forEach((block) => {
            if (block.classList.contains(language)) {
               block.style.display = "block";
               languageButtons.forEach((button) => {
                  button.classList.remove("selected");
                  if (button.id === language) {
                     button.classList.add("selected");
                  }
               });
            } else {
               block.style.display = "none";
            }
         });
      }

      languageButtons.forEach((button) => {
         button.addEventListener("click", function () {
            const language = this.id;
            showCode(language);
         });
      });

      showCode("python");
      document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
         anchor.addEventListener("click", function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute("href")).scrollIntoView({
               behavior: "smooth",
            });
         });
      });
   }
});
