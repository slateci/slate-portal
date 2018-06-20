// window.onload = console.log('ello poppit');
// Back to top button
jQuery(window).scroll(function() {

    if (jQuery(this).scrollTop() > 100) {
        jQuery('.back-to-top').fadeIn('slow');
    } else {
        jQuery('.back-to-top').fadeOut('slow');
    }

});

jQuery('.back-to-top').click(function(){
    jQuery('html, body').animate({scrollTop : 0},1500, 'easeInOutExpo');
    return false;
});


(function($) {
  "use strict"; // Start of use strict

  // Smooth scrolling using jQuery easing
  $('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
    if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
      if (target.length) {
        $('html, body').animate({
          scrollTop: (target.offset().top - 54)
        }, 1000, "easeInOutExpo");
        return false;
      }
    }
  });

  // Closes responsive menu when a scroll trigger link is clicked
  $('.js-scroll-trigger').click(function() {
    $('.navbar-collapse').collapse('hide');
  });

  // Activate scrollspy to add active class to navbar items on scroll
  $('body').scrollspy({
    target: '#mainNav',
    offset: 54
  });

})(jQuery); // End of use strict
