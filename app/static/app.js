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

async function getPhones() {
  data = { key: apiKey, manufacturer: 'Apple', limit: 5, name: 'iPhone' }
  try {
    response = await axios.get('/api/get-devices', { params: data });
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
  data = { key: apiKey }
  try {
    response = await axios.get('/api/get-manufacturers', { params: data });
    console.log(response.data);
  }
  catch (e) {
    console.log(e.response.data);
  }
}

async function getPhoneData(names) {
  const promises = []
  for (let name of names) {
    let data = { key: apiKey, master_key: masterKey, name: name }
    try {
      let response = axios.get('/api/get-device-data', { params: data });
      promises.push(response);
    }
    catch (e) {
      console.log(e);
    }
  }
  try {
    fulfilledPromises = await Promise.all(promises);
    phoneData = fulfilledPromises.map(p => p.data);
    return phoneData;
  }
  catch (e) {
    console.log(e)
    return undefined
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
    let response = await axios.post('/api/add-device', data);
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

// This should hopefully be significantly faster!

// This works! cut time from 2 hours to 1 hour

async function parallelSeed() {
  let manufObj = await createManufacturers();
  const manufNames = manufObj.Manufacturers.map(m => m.name);
  let deviceDataPromises = await getPhoneData(manufNames)
  for (let dataPromise of deviceDataPromises) {
    const devicePromises = []
    try {
      console.log(dataPromise);
      for (let device of dataPromise[Object.keys(dataPromise)[0]]) {
        let manuf_id = dataPromise.id;
        let device_name = device.name;
        let device_url = device.url;
        devicePromises.push(createPhone(manuf_id, device_name, device_url))
      }
    }
    catch (e) {
      console.log(e)
    }
    fulfilledDevicePromises = await Promise.all(devicePromises);
    const specPromises = [];
    try {
      for (let devPromise of fulfilledDevicePromises) {
        console.log(devPromise);
        let deviceId = devPromise.Device.id;
        specPromises.push(addPhoneSpecs(deviceId));
      }
    }
    catch (e) {
      console.log(e);
    }
    await Promise.all(specPromises)
  }
  console.log('Finished!')
}