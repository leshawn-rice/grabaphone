const searchBar = $('#search-form');

$('div.card-header').on('click', function (e) {
  const $cardBody = $($(this)[0].nextSibling.nextSibling);
  $cardBody.toggle();
});

function toggleGetDeviceOptions() {
  $('#manuf-name-group').show();
  $('#limit-group').show();
  $('#device-name-group').show();
  $('#is-released-group').hide();
  $('#is-released').prop('checked', false);
}

function toggleGetManufacturerOptions() {
  $('#manuf-name-group').show();
  $('#limit-group').show();
  $('#device-name-group').hide();
  $('#device-name').val('');
  $('#is-released-group').hide();
  $('#is-released').prop('checked', false);
}

function toggleGetLatestOptions() {
  $('#manuf-name-group').show();
  $('#limit-group').show();
  $('#device-name-group').show();
  $('#is-released-group').show();
}

$('#route').on('change', function (e) {
  let selected = $(this).val();
  if (selected === 'get-devices') {
    toggleGetDeviceOptions();
  }
  if (selected === 'get-manufacturers') {
    toggleGetManufacturerOptions();
  }
  if (selected === 'get-latest-devices') {
    toggleGetLatestOptions();
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

function syntaxHighlight(json) {
  /**
   * This function was copied from StackOverflow
   * Poster: user123444555621
   * Post link: https://stackoverflow.com/questions/4810841/pretty-print-json-using-javascript/7220510#7220510
   */
  if (typeof json != 'string') {
    json = JSON.stringify(json, undefined, 2);
  }
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
    var cls = 'number';
    if (/^"/.test(match)) {
      if (/:$/.test(match)) {
        cls = 'key';
      } else {
        cls = 'string';
      }
    } else if (/true|false/.test(match)) {
      cls = 'boolean';
    } else if (/null/.test(match)) {
      cls = 'null';
    }
    return '<span class="' + cls + '">' + match + '</span>';
  });
}

function putInResponse(data) {
  let response = JSON.stringify(data, null, 2);
  response = syntaxHighlight(response);
  const $resDiv = $('#response-div');
  $resDiv.empty();
  const dataPara = $('<pre class="text-light">').html(response);
  $resDiv.append(dataPara);
}

async function getAPIKey() {
  const result = await axios.get('/generate-api-key');
  const $page = $(result.data)
  const key = $page.find('strong').text();
  return key;
}

function addLoadingScreen() {
  const $parentDiv = $('#response-div');
  $parentDiv.empty();
  const $loadingDiv = $('<div class="text-center">')
  const $loadingIcon = $('<i class="fas fa-cog fa-spin text-light">');
  $loadingDiv.append($loadingIcon);
  $parentDiv.append($loadingDiv);
}

$('#example-request-form').on('submit', async function (e) {
  e.preventDefault();

  addLoadingScreen();

  const $route = $('#example-request-form option:selected').val();
  const $textInputs = $('#example-request-form :input[type=text]');
  const $checkedInputs = $('#example-request-form :input:checked');
  const $numberInputs = $('#example-request-form :input[type=number]');
  const key = await getAPIKey();
  data = { key };

  const vals = getFilledValues($textInputs, $checkedInputs, $numberInputs);

  for (let obj of vals) {
    data[obj.name] = obj.value;
  }

  try {
    const res = await axios.get(`/api/${$route}`, { params: data })
    putInResponse(res.data);
  }
  catch (err) {
    putInResponse(err.response.data);
  }
});