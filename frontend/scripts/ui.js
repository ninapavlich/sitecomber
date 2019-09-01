$('.card-header-tabs a').on('click', function (e) {
  e.preventDefault()
  $(this).tab('show')
  window.location.hash = this.hash;
})

if(window.location.hash){
  $('a[href="'+window.location.hash+'"]').tab('show')
}

$('.viewlink.overview').on('click', function (e) {
  e.preventDefault()
  $(".viewlink").removeClass('badge-info').addClass('badge-secondary');
  $('#links').addClass('sitemap').addClass('zoomed-out');
  $(".viewlink.overview").addClass('badge-info').removeClass('badge-secondary');
})
$('.viewlink.sitemap').on('click', function (e) {
  e.preventDefault()
  $(".viewlink").removeClass('badge-info').addClass('badge-secondary');
  $('#links').addClass('sitemap').removeClass('zoomed-out');
  $(".viewlink.sitemap").addClass('badge-info').removeClass('badge-secondary');
})
$('.viewlink.list').on('click', function (e) {
  e.preventDefault()
  $(".viewlink").removeClass('badge-info').addClass('badge-secondary');
  $('#links').removeClass('sitemap').removeClass('zoomed-out');
  $(".viewlink.list").addClass('badge-info').removeClass('badge-secondary');
})


$("#sitemap").sitemap(); 