$(document).ready(function () {
   $(".hamburger-menu").click(() => $(".nav-links").toggleClass("visible"));
   if (window.location.pathname === "/") {
      const textList = ["Your Gateway to Wonders!", "Discover, Learn, and Thrive.", "Quality Over Quantity.", "Beyond the Ordinary.", "Masterpieces at Your Fingertips!", "Elevate Your Online Experience!", "Your Knowledge Hub.", "Where Curiosity Take Flight!", "Unleash Your Potential!"];
      let isTyping = true;
      let charIndex = 0;
      let index = 0;

      function typeText() {
         if (isTyping) {
            $("#welcome-text").text(textList[index].substring(0, charIndex)) && charIndex++;
				charIndex > textList[index].length ? (isTyping = false, setTimeout(typeText, 1750)) : setTimeout(typeText, 75);
         } else {
            $("#welcome-text").text(textList[index].substring(0, charIndex)) && charIndex--;
            charIndex < 0 ? (isTyping = true, index = (index + 1) % textList.length, setTimeout(typeText, 750)) : setTimeout(typeText, 50);
         };
      };
      
      typeText();
      $(window).scroll(() => {
         const triggerWelcomeImgPosition = $(".welcome img").offset().top - $(".welcome img").outerHeight() - 700;
         if ($(window).scrollTop() > triggerWelcomeImgPosition) {
            $("header").addClass("new-alt-header");
            $(".bar").css("background-color", "#252525");
            $("header img").css("filter", "invert(0%)");
         } else {
            $("header").removeClass("new-alt-header");
            $(".bar").css("background-color", "rgb(215, 230, 230)");
            $("header img").css("filter", "invert(90%)");
         }
         
		let sectionTriggers = Array($("section").length).fill(false);
		$("section").each((index, section) => {
		  const triggerPosition = $(section).offset().top;
		  const offset = index <= 3 ? index * 100 - 1000 : 0;
		  if (!sectionTriggers[index] && $(window).scrollTop() - offset > triggerPosition) {
			 $(section).addClass("activated");
			 sectionTriggers[index] = true;
		  }
		});
      
         $("section").each((index, section) => sectionTriggers[index] = activateSection($(section), $(section).offset().top, index <= 3 ? index * 100 - 1000 : 0, sectionTriggers[index]));
      });
   } else if (window.location.pathname === "/Dashboard") {
   	$("select").change(() => window.location.href=`${window.location.pathname}?time=${$("#time").val()}&lang=${$("#language").val()}`)
   } else if (window.location.pathname === "/Api-Docs") {
   	$('a[href^="#"]').click(function(e){e.preventDefault();$($(this).attr("href"))[0].scrollIntoView({behavior:"smooth"})});
      $(".programming-language").click(function() {
      	$(".programming-language").removeClass("selected") && $(this).addClass("selected");
      	$(".api-call-example").css("display", "none") && $(".api-call-example").filter("." + $(this).attr("id")).css("display", "block");
      });
   } else if (["/Newsletter", "/Drop", "/Edit", "/Submit", "/Contact"].includes(window.location.pathname)) {
      $(".subscribe").click(() => $("body").css("overflow", "hidden") && $(".popup").show());
      $("#cancel").click(() => $("body").css("overflow", "auto") && $(".popup").hide());
		$(".popup").click((e) => !$(e.target).closest("#sub .popup-content").length && $("body").css("overflow", "auto") && $(".popup").hide());
      $("#closebtn").click(() => popUp.hide());
   }
});
