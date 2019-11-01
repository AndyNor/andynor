// Activate jQuery chosen
$( '.chzn-select' ).chosen({});

// Add 'bootstrap' class to form labels
$( "form label" ).addClass( 'control-label' );

// Bootstrap scrollspy
$( '#navbar' ).scrollspy()

// Bootstrap tooltip
$( '[rel=tooltip]' ).tooltip()

// jQuery UI datepicker
$(function(){
	$('.datepicker').datepicker({
		changeMonth: true,
		changeYear: true,
		showButtonPanel: true,
		showOtherMonths: true,
		selectOtherMonths: false,
		showWeek: true,
		firstDay: 1,
		dateFormat: 'yy-mm-dd',
	});
	//hover states on the static widgets
	$('#dialog_link, ul#icons li').hover(
		function() { $(this).addClass('ui-state-hover'); },
		function() { $(this).removeClass('ui-state-hover'); }
	);
});

$('.nav-tabs li').on('click', function() {
	var tabname = $(this).children('a').data('tabname');
	history.pushState( {}, document.title + ' - ' + tabname, tabname );
});

// Make selected images visible
$('#blog_image_form input:checkbox').hide();
$('#blog_image_form input:checkbox').on('click', function() {
	$(this).parent().parent().toggleClass('checkbox_active');
});

$(document).ready(function() {
	$("img").unveil();
	prettyPrint();
});