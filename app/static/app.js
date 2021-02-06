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

$('div.card-header').on('click', function (e) {
  const $cardBody = $($(this)[0].nextSibling.nextSibling);
  $cardBody.toggle();
});

$('#route').on('change', function (e) {
  let selected = $(this).val();
  if (selected === 'get-devices') {
    $('#manuf-name-check').show();
    $('#limit-check').show();
    $('#device-name-check').show();
    $('#is-released-check').hide();
  }
  if (selected === 'get-manufacturers') {
    $('#manuf-name-check').show();
    $('#limit-check').show();
    $('#device-name-check').hide();
    $('#is-released-check').hide();
  }
  if (selected === 'get-latest-devices') {
    $('#manuf-name-check').show();
    $('#limit-check').hide();
    $('#device-name-check').show();
    $('#is-released-check').show();
  }
});