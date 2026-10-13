// SCAFFOLD - route /projects. Project area from Figure 2 (needs a logged-in user).
// Renders <Navbar/>, the existing <Project/> forms, and a "My projects" list.
//   - "My projects": getUserProjects(user.userId); each item links to /projects/:id.
//   - After Project.js creates/loads a project, navigate to /projects/:id
//     (change its onSelect handler accordingly).
import React from 'react';

export default function MyUserPortal() {
  return <main><h1>Projects</h1><p className="muted">TODO: MyUserPortal</p></main>;
}
