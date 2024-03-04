$(document).ready(function () {
   $(".hamburger-menu").click(() => $(".nav-links").toggleClass("visible"));
   if (window.location.pathname === "/") {
      const altHeader = $("header");
      const logo = $("header img");
      const bar = $(".bar");
      const welcomeImg = $(".welcome img");
      const sections = $("section");
      const typetext = $("#welcome_text");
      let index = 0;
      let charIndex = 0;
      let isDeleting = false;
      const textList = ["Your Gateway to Wonders!", "Discover, Learn, and Thrive.", "Quality Over Quantity.", "Tech Vibes, No Limits!", "Masterpieces at Your Fingertips!", "Elevate Your Online Experience!", "Where Curiosity Take Flight!"];

      function typeText() {
         let currentText = textList[index];
         if (!isDeleting) {
            typetext.text(currentText.substring(0, charIndex));
            charIndex++;

            if (charIndex > currentText.length) {
               isDeleting = true;
               setTimeout(typeText, 1750);
            } else {
               setTimeout(typeText, 75);
            }
         } else {
            typetext.text(currentText.substring(0, charIndex));
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

      if (welcomeImg.length > 0 && typetext.length > 0) {
         typeText();
      }

      let sectionTriggers = Array(sections.length).fill(false);
      const activateSection = (section, triggerPosition, offset, triggeredFlag) => {
         if (!triggeredFlag && $(window).scrollTop() - offset > triggerPosition) {
            section.addClass("activated");
            triggeredFlag = true;
         }

         return triggeredFlag;
      };

      altHeader.addClass("alt_header");
      logo.css("filter", "invert(90%)");
      bar.css("background-color", "rgb(215, 230, 230)");
      $(window).scroll(() => {
         const triggerWelcomeImgPosition = welcomeImg.offset().top - welcomeImg.outerHeight() - 600;

         if ($(window).scrollTop() > triggerWelcomeImgPosition) {
            altHeader.addClass("new_alt_header");
            bar.css("background-color", "#252525");
            logo.css("filter", "invert(0%)");
         } else {
            altHeader.removeClass("new_alt_header");
            bar.css("background-color", "rgb(215, 230, 230)");
            logo.css("filter", "invert(90%)");
         }

         sections.each((index, section) => {
            const triggerSectionPosition = $(section).offset().top;
            const offset = index <= 3 ? index * 100 - 1000 : 0;
            sectionTriggers[index] = activateSection($(section), triggerSectionPosition, offset, sectionTriggers[index]);
         });
      });
   } else if (window.location.pathname === "/Dashboard") {
      $("select").change(function () {
         updateURL();
      });

      function updateURL() {
         let time = $("#time").val();
         let language = $("#language").val();
         let url = `${window.location.pathname}?time=${time}&lang=${language}`;
         window.location.href = url;
      }
   } else if (window.location.pathname === "/Api-Docs") {
      const languageButtons = $(".programming_language");
      const codeBlocks = $(".api_call_example");
      function showCode(language) {
         codeBlocks.each((index, block) => {
            if ($(block).hasClass(language)) {
               $(block).css("display", "block");
               languageButtons.removeClass("selected");
               languageButtons.filter(`#${language}`).addClass("selected");
            } else {
               $(block).css("display", "none");
            }
         });
      }

      languageButtons.click(function () {
         const language = $(this).attr("id");
         showCode(language);
      });

      showCode("python");
      $('a[href^="#"]').click(function (e) {
         e.preventDefault();

         $($(this).attr("href"))[0].scrollIntoView({
            behavior: "smooth",
         });
      });
   } else if (["/Newsletter", "/Drop", "/Edit", "/Submit", "/Contact"].includes(window.location.pathname)) {
      const subBtn = $(".subscribe");
      const cancelBtn = $("#cancel");
      const popUp = $(".popup");
      const closeBtn = $("#closebtn");

      subBtn.click(function () {
         $("body").css("overflow", "hidden");
         popUp.show();
      });

      cancelBtn.click(function () {
         $("body").css("overflow", "auto");
         popUp.hide();
      });

      popUp.click(function (event) {
         if (!$(event.target).closest("#sub .popup-content").length) {
            $("body").css("overflow", "auto");
            popUp.hide();
         }
      });

      closeBtn.click(function () {
         popUp.hide();
      });
   }
});
