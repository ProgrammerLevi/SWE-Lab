// SCAFFOLD - route /projects/:projectId.
// Reads :projectId from the URL (useParams), loads the project with getProject to show its
// name and description (404 -> message + link back), and renders <Navbar/> and
// <Checkout projectId userId/> with userId from useAuth().
import React from 'react';
import { useParams } from 'react-router-dom';

export default function ProjectPage() {
  const { projectId } = useParams();
  return <main><h1>Project {projectId}</h1><p className="muted">TODO: ProjectPage</p></main>;
}
