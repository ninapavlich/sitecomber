$('.card-header-tabs a').on('click', function (e) {
  e.preventDefault()
  $(this).tab('show')
  window.location.hash = this.hash;
})

if(window.location.hash){
  $('a[href="'+window.location.hash+'"]').tab('show')
}