const masterKey = 'masterkey';
const apiKey = '829c7dd80297';

const endpointContainer = $('#endpoints');

function searchPage() {
  let foundIn = $('*:contains("GET")');
  console.log('Searching Page!');
  console.log(foundIn);
}

$('#endpoints > div').on('click', function (e) {
  console.log('Clicked a div!');
  $(this).find('.card-body').toggle();
});

// endpointContainer.on('click', 'div', (e) => {
//   console.log('Clicked a div!');
// });

function addListeners() {
  for (let child of endpointContainer.children()) {
    console.log(child);
  }
}

async function createManufacturers() {
  data = { key: apiKey, master_key: masterKey }
  response = await axios.post('/api/add-manufacturers', data);
  console.log(response);
}

async function getManufacturers() {
  data = { key: apiKey, name: 'Apple' }
  try {
    response = await axios.get('/api/get-manufacturers', { params: data });
    console.log(response)
  }
  catch (e) {
    console.log(e.response.data);
  }
}

async function getPhoneData(manufName) {
  let data = { key: apiKey, master_key: masterKey, name: manufName };
  let response = await axios.get('/api/get-phone-data', { params: data });
  console.log(response);
}

async function addPhoneSpecs(phoneId) {
  let data = { key: apiKey, master_key: masterKey };
  let response = await axios.post(`/api/add-specs/${phoneId}`, data);
  console.log(response);
}

async function createPhone(manufId, name, url) {
  let data = { key: apiKey, master_key: masterKey, manuf_id: manufId, name: name, url: url };
  let response = await axios.post('/api/add-phone', data);
  console.log(response);
}

async function createAllPhones() {
  let data = { key: apiKey, master_key: masterKey };
  let response = await axios.post('/api/add-phones', data);
  for (let i = 1; i < 130; i++) {
    response = await createPhone(i, 1);
  }
  console.log(response);
}