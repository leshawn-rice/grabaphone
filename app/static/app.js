const masterKey = 'masterkey';
const apiKey = 'c372886b88f3'

async function createManufacturers() {
  data = { key: apiKey, master_key: masterKey }
  response = await axios.post('/api/add-manufacturers', data);
  console.log(response);
}

async function getManufacturers() {
  data = { key: apiKey }
  response = await axios.get('/api/get-manufacturers', { params: { key: apiKey } });
  console.log(response)
}

async function createPhone(offset, limit) {
  let data = { key: apiKey, master_key: masterKey, offset, limit };
  let response = await axios.post('/api/add-phones', data);
  return response
}

async function createAllPhones() {
  let data = { key: apiKey, master_key: masterKey };
  let response = await axios.post('/api/add-phones', data);
  for (let i = 1; i < 130; i++) {
    response = await createPhone(i, 1);
  }
  console.log(response);
}