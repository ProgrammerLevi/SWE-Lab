// Route /projects. Project area from Figure 2 (needs a logged-in user):
// the projects the user owns, the projects shared with them, the create /
// use-existing project forms, and the hardware sets in the system (HWSet1 and
// HWSet2, created by the server).
// Everything shown here comes from the database; nothing is hard-coded.
import React, { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import HardwareSetList from '../components/HardwareSetList';
import Navbar from '../components/Navbar';
import Project from '../components/Project';
import { getAllHardwareSets } from '../api/hardware';
import { getProjectsByOwnership } from '../api/projects';
import { useAuth } from '../context/AuthContext';

// One section of projects. showOwner is off for "My projects", where the owner is always you.
function ProjectSection({ title, projects, loading, error, emptyText, showOwner }) {
  return (
    <section className="card">
      <h2>{title}</h2>
      {loading && <p className="muted">Loading...</p>}
      {error && <p className="msg err">{error}</p>}
      {!loading && !error && projects.length === 0 && <p className="muted">{emptyText}</p>}
      {projects.length > 0 && (
        <ul>
          {projects.map((p) => (
            <li key={p.projectId}>
              <Link to={`/projects/${encodeURIComponent(p.projectId)}`}>
                <strong>{p.projectName}</strong>
              </Link>
              <span className="muted"> ({p.projectId})</span>
              {showOwner && <span className="muted"> · Owner: {p.ownerName || 'Unknown'}</span>}
              {p.description && <div className="muted">{p.description}</div>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function MyUserPortal() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [projects, setProjects] = useState({ owned: [], shared: [] });
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState(null);

  const [hwSets, setHwSets] = useState([]);
  const [hwError, setHwError] = useState(null);

  const loadProjects = useCallback(async () => {
    setProjectsLoading(true);
    setProjectsError(null);
    try {
      setProjects(await getProjectsByOwnership(user.userId));
    } catch (err) {
      setProjectsError(err.message);
    } finally {
      setProjectsLoading(false);
    }
  }, [user.userId]);

  const loadHardware = useCallback(async () => {
    try {
      setHwSets(await getAllHardwareSets());
      setHwError(null);
    } catch (err) {
      setHwError(err.message);
    }
  }, []);

  useEffect(() => { loadProjects(); }, [loadProjects]);
  useEffect(() => { loadHardware(); }, [loadHardware]);

  return (
    <>
      <Navbar />
      <main>
        <h1>Projects</h1>

        <ProjectSection
          title="My projects"
          projects={projects.owned}
          loading={projectsLoading}
          error={projectsError}
          emptyText="You haven't created any projects yet. Create one below."
        />

        <ProjectSection
          title="Shared projects"
          projects={projects.shared}
          loading={projectsLoading}
          error={projectsError}
          emptyText="No one has shared a project with you yet. Use an existing project ID below to join one."
          showOwner
        />

        <Project
          userId={user.userId}
          onSelect={(project) => navigate(`/projects/${encodeURIComponent(project.projectId)}`)}
        />

        <section className="card">
          <h2>Hardware sets</h2>
          {hwError ? <p className="msg err">{hwError}</p> : <HardwareSetList sets={hwSets} />}
        </section>
      </main>
    </>
  );
}
