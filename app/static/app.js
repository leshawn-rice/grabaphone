const masterKey = 'masterkey';
const apiKey = '15800fe3842e';
const searchBar = $('#search-form');

function searchPage() {
  /*
   * Searches the current page
   * for the text inside the search
   * bar. Then scrolls to it
   */
  let foundIn = $('*:contains("GET")');
  console.log('Searching Page!');
  console.log(foundIn);
}

$('#endpoints > div').on('click', function (e) {
  $(this).find('.card-body').toggle();
});

async function getPhones() {
  data = { key: apiKey, manufacturer: 'Apple', limit: 5, name: 'iPhone' }
  try {
    response = await axios.get('/api/get-phones', { params: data });
    console.log(response.data);
    return response.data;
  }
  catch (e) {
    console.log(e.response.data)
    return e.response.data;
  }
}

async function createManufacturers() {
  data = { key: apiKey, master_key: masterKey }
  try {
    response = await axios.post('/api/add-manufacturers', data);
    console.log(response.data);
    return response.data;
  }
  catch (e) {
    console.log(e.response.data);
    return e.response.data;
  }
}

async function getManufacturers() {
  data = { key: apiKey, name: 'Apple' }
  try {
    response = await axios.get('/api/get-manufacturers', { params: data });
    console.log(response.data);
  }
  catch (e) {
    console.log(e.response.data);
  }
}

async function getPhoneData(manufName) {
  let data = { key: apiKey, master_key: masterKey, name: manufName };
  try {
    let response = await axios.get('/api/get-phone-data', { params: data });
    console.log(response.data);
    return response.data;
  }
  catch (e) {
    console.log(e.response.data);
    return e.response.data;
  }
}

async function addPhoneSpecs(phoneId) {
  let data = { key: apiKey, master_key: masterKey };
  try {
    let response = await axios.post(`/api/add-specs/${phoneId}`, data);
    console.log(response.data);
    return response.data;
  }
  catch (e) {
    console.log(e.response.data);
    return e.response.data;
  }
}

async function createPhone(manufId, name, url) {
  let data = { key: apiKey, master_key: masterKey, manuf_id: manufId, name: name, url: url };

  try {
    let response = await axios.post('/api/add-phone', data);
    console.log(response);
    return response.data;
  }
  catch (e) {
    console.log(e.response.data);
    return e.response.data;
  }
}

async function seedDb() {
  let manufObj = await createManufacturers();
  for (let manuf of manufObj.Manufacturers) {
    let phoneData = await getPhoneData(manuf.name);
    console.log(phoneData[Object.keys(phoneData)[0]]);
    for (let phone of phoneData[Object.keys(phoneData)[0]]) {
      let id = manuf.id;
      let name = phone.name;
      let url = phone.url;
      let phoneObj = await createPhone(id, name, url);
      let phoneId = phoneObj.Phone.id
      await addPhoneSpecs(phoneId);
      console.log(`Finished ${name}`);
    }
    console.log(`Finished ${manuf.name}`);
  }
}