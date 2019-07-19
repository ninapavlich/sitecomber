console.log("HELLO UI!")

$('.card-header-tabs a').on('click', function (e) {
  e.preventDefault()
  $(this).tab('show')
  console.log("TAB CLICKED")
})