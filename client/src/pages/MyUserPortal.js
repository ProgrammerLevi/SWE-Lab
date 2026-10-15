// Route /projects. Project area from Figure 2 (needs a logged-in user).
// TODO: render <Navbar/> once it exists.
import React from 'react';
import { useNavigate } from 'react-router-dom';
import Project from '../components/Project';
import { useAuth } from '../context/AuthContext';

export default function MyUserPortal() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <main>
      <h1>Projects</h1>
      <Project
        userId={user.userId}
        onSelect={(project) => navigate(`/projects/${project.projectId}`)}
      />
    </main>
  );
}
