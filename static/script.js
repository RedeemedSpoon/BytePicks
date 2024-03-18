$(document).ready(function () {
   $(".hamburger-menu").click(() => $(".nav-links").toggleClass("visible"));
   if (window.location.pathname === "/") {
      const textList = ["Your Knowledge Hub.", "Discover. Learn. Thrive.", "Beyond the Ordinary.", "Quality Over Quantity.", "Future-Proof Yourself.", "Masterpieces at Your Fingertips!", "Explore. Decode. Dominate.", "The Web's Hidden Gems!", "Elevate Your Online Experience.", "Unleash Your Potential!"];
      let isTyping = true;
      let charIndex = 0;
      let index = 0;

      function typeText() {
         if (isTyping) {
            $("#welcome-text").text(textList[index].substring(0, charIndex)) && charIndex++;
				charIndex > textList[index].length ? (isTyping = false, setTimeout(typeText, 1500)) : setTimeout(typeText, 75);
         } else {
            $("#welcome-text").text(textList[index].substring(0, charIndex)) && charIndex--;
            charIndex < 0 ? (isTyping = true, index = (index + 1) % textList.length, setTimeout(typeText, 500)) : setTimeout(typeText, 50);
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
   });
   } else if (window.location.pathname === "/dashboard") {
   	$("select").change(() => window.location.href=`${window.location.pathname}?time=${$("#time").val()}&lang=${$("#language").val()}`)
   } else if (window.location.pathname === "/api-docs") {
   	$('a[href^="#"]').click(function(e) {e.preventDefault(); $($(this).attr("href"))[0].scrollIntoView({behavior:"smooth"})});
      $(".programming-language").click(function() {
      	$(".programming-language").removeClass("selected") && $(this).addClass("selected");
      	$(".api-call-example").css("display", "none") && $(".api-call-example").filter("." + $(this).attr("id")).css("display", "block");
      });
   } else if (["/newsletter", "/drop", "/edit", "/submit", "/contact"].includes(window.location.pathname)) {
      $(".subscribe").click(() => $("body").css("overflow", "hidden") && $(".popup").show() && $(".alt-popup").hide());
      $("#cancel").click(() => $("body").css("overflow", "auto") && $(".popup").hide());
      $(".popup").click((e) => {if (!$(e.target).closest("#sub .popup-content").length) $("body").css("overflow", "auto") && $(".popup").hide()})
      $("#closebtn").click(() => $(".popup").hide());
   }
});