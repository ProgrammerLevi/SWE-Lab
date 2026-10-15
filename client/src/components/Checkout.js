// SCAFFOLD - Resource Management panel (Figure 3 of the spec).
// Props: { projectId, userId }
//
// Loads hardware sets with getAllHardwareSets() and the project with getProject(projectId).
// Renders one row per set (no hard-coded names):
//   Name | Capacity | Available | Checked out (project.hwSets[name] || 0) | Request [input] | Check in / Check out
//
// State: sets, project, requests ({ [hwName]: string }), busy, status ({ ok, text }).
// Behaviour:
//   - Validate each request as a positive whole number (/^[1-9]\d*$/) before calling the API.
//   - handleCheckOut(hwName) / handleCheckIn(hwName): call checkOut / checkIn, show the server
//     message on success or failure, then refetch sets + project so the numbers update.
//   - Disable the buttons while a request is in flight.
//   - Optional: poll every few seconds so other users' changes appear.
import React from 'react';

export default function Checkout({ projectId, userId }) {
  return null;
}
