// Thin wrapper around the Flask project routes. Components never call fetch directly.
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

export const createProject = (projectName, projectId, description) =>
  post('/create_project', { projectName, projectId, description });

// Returns the project document: { projectName, projectId, description, hwSets, users }
export async function getProject(projectId) {
  const { project } = await post('/get_project_info', { projectId });
  return project;
}
