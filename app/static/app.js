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
      $($(`#${$(this)[0].id}`).nextSibling.nextSibling).show();
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
    $('#manuf-name-group').show();
    $('#limit-group').show();
    $('#device-name-group').show();
    $('#is-released-group').hide();
    $('#is-released').prop('checked', false);
  }
  if (selected === 'get-manufacturers') {
    $('#manuf-name-group').show();
    $('#limit-group').show();
    $('#device-name-group').hide();
    $('#device-name').val('');
    $('#is-released-group').hide();
    $('#is-released').prop('checked', false);
  }
  if (selected === 'get-latest-devices') {
    $('#manuf-name-group').show();
    $('#limit-group').show();
    $('#device-name-group').show();
    $('#is-released-group').show();
  }
});

function getFilledValues($textInputs, $checkedInputs, $numberInputs) {
  const vals = []

  for (let input of $textInputs) {
    if (!($(input).val() === '')) {
      const name = $(input).attr('name');
      const value = $(input).val();
      vals.push({ name, value });
    }
  }
  for (let input of $checkedInputs) {
    const name = $(input).attr('name');
    const value = $(input).val();
    vals.push({ name, value });
  }
  for (let input of $numberInputs) {
    if (!($(input).val() === '')) {
      const name = $(input).attr('name');
      const value = $(input).val();
      vals.push({ name, value });
    }
  }

  return vals;
}

function putInResponse(data) {
  let response = JSON.stringify(data, null, 2);
  const $resDiv = $('#response-div');
  $resDiv.empty();
  const dataPara = $('<pre class="text-light">').text(response);
  $resDiv.append(dataPara);
}

$('#example-request-form').on('submit', async function (e) {
  e.preventDefault();
  const $route = $('#example-request-form option:selected').val();
  const $textInputs = $('#example-request-form :input[type=text]');
  const $checkedInputs = $('#example-request-form :input:checked');
  const $numberInputs = $('#example-request-form :input[type=number]');
  const key = '111a99761fdb';
  data = { key };

  const vals = getFilledValues($textInputs, $checkedInputs, $numberInputs);

  for (let obj of vals) {
    data[obj.name] = obj.value;
  }

  try {
    const res = await axios.get(`/api/${$route}`, { params: data })
    console.log(res);
    putInResponse(res.data);
  }
  catch (err) {
    putInResponse(err.data);
  }




});