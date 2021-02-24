
/*
* When the user clicks on one of the endpoint cards on the
* lefthand side of the screen, expand the card body
*/

$('div.card-header').on('click', function (e) {
  const $cardBody = $($(this)[0].nextSibling.nextSibling);
  $cardBody.toggle();
});


/*
* Functions to handle example request form options
*/

function toggleRouteOptions(dataToShow, dataToHide, dataToUncheck, dataToReset) {
  if (dataToShow && dataToShow.length > 0) {
    for (let domElement of dataToShow) {
      domElement.show()
    }
  }
  if (dataToHide && dataToHide.length > 0) {
    for (let domElement of dataToHide) {
      domElement.hide()
    }
  }
  if (dataToUncheck) {
    dataToUncheck.prop('checked', false)
  }
  if (dataToReset) {
    dataToReset.val('')
  }
}

function toggleDeviceRoute() {
  const dataToShow = [$('#manuf-name-group'), $('#limit-group'), $('#device-name-group')];
  const dataToHide = [$('#is-released-group')];
  const dataToUncheck = $('#is-released');
  toggleRouteOptions(dataToShow, dataToHide, dataToUncheck);
}

function toggleManufacturerRoute() {
  const dataToShow = [$('#manuf-name-group'), $('#limit-group')];
  const dataToHide = [$('#device-name-group'), $('#is-released-group')];
  const dataToUncheck = $('#is-released');
  const dataToReset = $('#device-name');
  toggleRouteOptions(dataToShow, dataToHide, dataToUncheck, dataToReset);
}

function toggleLatestDeviceRoute() {
  const dataToShow = [$('#manuf-name-group'), $('#limit-group'), $('#device-name-group'), $('#is-released-group')];
  toggleRouteOptions(dataToShow);
}

/*
* When the user changes the route in the 
* example request form, update the options
* to the available query params for that route
*/

$('#route').on('change', function (e) {
  let selected = $(this).val();
  if (selected === 'get-devices') {
    toggleDeviceRoute();
  }
  if (selected === 'get-manufacturers') {
    toggleManufacturerRoute();
  }
  if (selected === 'get-latest-devices') {
    toggleLatestDeviceRoute();
  }
});

/*
* Handle changing the DOM to reflect example
* requests/responses 
*/

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

function addLoadingScreen() {
  const $parentDiv = $('#response-div');
  $parentDiv.empty();
  const $loadingDiv = $('<div class="text-center">')
  const $loadingIcon = $('<i class="fas fa-cog fa-spin text-light">');
  $loadingDiv.append($loadingIcon);
  $parentDiv.append($loadingDiv);
}

/*
* Handle sending example requests
* and displaying the responses
*/

async function getAPIKey() {
  const result = await axios.get('/generate-api-key');
  const $page = $(result.data)
  const key = $page.find('strong').text();
  return key;
}

function addParamValues(input, params) {
    const name = $(input).attr('name');
    const value = $(input).val();
    params.push({name, value})
}

function fillQueryParams($text, $checked, $number) {
  const params = []

  for (let input of $text) {
    if ($(input).val() !== '') {
      addParamValues(input, params)
    }
  }
  for (let input of $checked) {
    addParamValues(input, params)
  }
  for (let input of $number) {
    if ($(input).val() !== '') {
      addParamValues(input, params)
    }
  }

  return params;
}

function getQueryParams($route) {
  const $text = $('#example-request-form :input[type=text]');
  const $checked = $('#example-request-form :input:checked');
  const $number = $('#example-request-form :input[type=number]');
  const params = fillQueryParams($text, $checked, $number)
  return params
}

function getData() {
  const key = await getAPIKey();
  const $route = $('#example-request-form option:selected').val();
  const params = getQueryParams();
  const data = { key };

  for (let param of params) {
    data[param.name] = param.value;
  }
  return data;
}

/*
* When the user submits the example request
* form, send the request and display the example
* response/error to the user
*/

$('#example-request-form').on('submit', async function (e) {
  e.preventDefault();

  addLoadingScreen();

  const data = getData();

  try {
    const res = await axios.get(`/api/${$route}`, { params: data })
    putInResponse(res.data);
  }
  catch (err) {
    putInResponse(err.response.data);
  }
});