// window.onload = console.log('ello poppit');

// // Smoth scroll on page hash links
// jQuery('a[href*="#"]:not([data-toggle="tab"])').on('click', function() {
//     if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
//         var target = jQuery(this.hash);
//         if (target.length) {
//
//             var top_space = 0;
//
//             if( jQuery('#header').length ) {
//               top_space = jQuery('#header').outerHeight();
//             }
//
//             jQuery('html, body').animate({
//                 scrollTop: target.offset().top - top_space
//             }, 1500, 'easeInOutExpo');
//
//             if ( jQuery(this).parents('.nav-menu').length ) {
//               jQuery('.nav-menu .menu-active').removeClass('menu-active');
//               jQuery(this).closest('li').addClass('menu-active');
//             }
//
//             if ( jQuery('body').hasClass('mobile-nav-active') ) {
//                 jQuery('body').removeClass('mobile-nav-active');
//                 jQuery('#mobile-nav-toggle i').toggleClass('fa-times fa-bars');
//                 jQuery('#mobile-body-overly').fadeOut();
//             }
//
//             return false;
//         }
//     }
// });


// Smooth scrolling using jQuery easing
// jQuery('a.js-scroll-trigger[href*="#"]:not([href="#"])').click(function() {
//   if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
//     var target = jQuery(this.hash);
//     target = target.length ? target : jQuery('[name=' + this.hash.slice(1) + ']');
//     if (target.length) {
//       jQuery('html, body').animate({
//         scrollTop: (target.offset().top - 54)
//       }, 1000, "easeInOutExpo");
//       return false;
//     }
//   }
// });

// Closes responsive menu when a scroll trigger link is clicked
jQuery('.js-scroll-trigger').click(function() {
  jQuery('.navbar-collapse').collapse('hide');
});

// Activate scrollspy to add active class to navbar items on scroll
jQuery('body').scrollspy({
  target: '#mainNav',
  offset: 54
});


// Back to top button
$(document).ready(function(){
    $(window).scroll(function(){
        if ($(this).scrollTop() > 100) {
            $('#scroll').fadeIn();
        } else {
            $('#scroll').fadeOut();
        }
    });
    $('#scroll').click(function(){
        $("html, body").animate({ scrollTop: 0 }, 600);
        return false;
    });
});

$(document).ready(function () {

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
});
