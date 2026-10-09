// Thin wrapper around the Flask hardware routes. Components never call fetch directly.
async function post(path, body = {}) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok || data.success === false) {
    throw new Error(data.message || `Request failed (${res.status})`);
  }
  return data;
}

export const createHardwareSet = (hwSetName, initCapacity) =>
  post('/create_hardware_set', { hwSetName, initCapacity });

export const getHwInfo = (hwSetName) => post('/get_hw_info', { hwSetName });

// Returns [{ hwName, capacity, availability }, ...]
export async function getAllHardwareSets() {
  const { hwNames } = await post('/get_all_hw_names');
  return Promise.all(hwNames.map((name) => getHwInfo(name)));
}
