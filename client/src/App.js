import React, { useCallback, useEffect, useState } from 'react';
import './App.css';
import Project from './components/Project';
import HardwareSetList from './components/HardwareSetList';
import { createHardwareSet, getHwInfo } from './api/hardware';

// The two sets the spec asks for. They are created on first load if missing.
const HW_SETS = ['HWSet1', 'HWSet2'];
const DEFAULT_CAPACITY = 100;

export default function App() {
  const [project, setProject] = useState(null);
  const [sets, setSets] = useState([]);
  const [loadError, setLoadError] = useState(null);

  const refresh = useCallback(async () => {
    try {
      // Creating an existing set just returns 409, which we ignore
      await Promise.all(HW_SETS.map((n) => createHardwareSet(n, DEFAULT_CAPACITY).catch(() => {})));
      setSets(await Promise.all(HW_SETS.map(getHwInfo)));
      setLoadError(null);
    } catch (err) {
      setLoadError(err.message);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  return (
    <main>
      <h1>Resource Management</h1>
      <Project onSelect={setProject} />
      {project && (
        <section className="card">
          <h2>Project: {project.projectName} ({project.projectId})</h2>
          {project.description && <p className="muted">{project.description}</p>}
          {loadError && <p className="msg err">Could not load sets: {loadError}</p>}
          <HardwareSetList sets={sets} />
        </section>
      )}
    </main>
  );
}
