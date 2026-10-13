// SCAFFOLD - New User sign-up form, rendered inside <Modal> on the login page.
// Props: { onDone }   (called after a successful sign-up so the login page can close the modal)
// Fields: username, userId, password (+ confirm password, checked client-side).
// Submit calls api/users.addUser; shows "That userId is already taken" (409) and other errors inline.
// NOTE: addUser still needs a username on the backend - keep the field, or drop it with the backend change.
import React from 'react';

export default function MyRegistrationPage({ onDone }) {
  return null;
}
