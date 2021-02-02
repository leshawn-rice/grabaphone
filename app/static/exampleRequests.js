async function getManufacturers(key, name, limit) {
  /*
  * Get manufacturers, can sort by name and limit
  * This is an example of how a user might retrieve manufacturers
  * from the API
  */
  data = { key, name, limit }
  try {
    response = await axios.get('/api/get-manufacturers', { params: data });
    console.log(response.data);
    return response.data;
  }
  catch (e) {
    console.log(e.response.data);
    return e.response.data;
  }
}

async function getDevices(key, manufacturer, name, limit) {
  /*
  * Get devices, can sort by name, manuf, and limit
  * This is an example of how a user might retrieve devices
  * from the API
  */
  data = { key, manufacturer, limit, name }
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