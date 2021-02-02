const masterKey = 'masterkey';
const apiKey = '583f6187e9a4';
const searchBar = $('#search-form');

function searchPage() {
  /*
   * Searches the current page
   * for the text inside the search
   * bar. Then scrolls to it
   */

  let searchTerm = $('#search-input').val();
  if (searchTerm.length < 3) {
    return
  }
  $(`*:contains("${searchTerm}")`).each(function () {
    try {
      document.getElementById($(this)[0].id).scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    catch (e) {
      // ignore elements that have no id
    }
  });
}

$('#endpoints > div').on('click', function (e) {
  $(this).find('.card-body').toggle();
});