// SCAFFOLD - route /login. Sign-in area from Figure 2.
// Fields: userId, password (no username). Submit calls useAuth().signIn, then navigates to /projects.
// Shows the server error inline (e.g. "Invalid credentials").
// Has a "New User" button that opens <MyRegistrationPage/> in a <Modal>.
// If already signed in, redirect to /projects.
import React from 'react';
import DevLogin from '../components/DevLogin';

export default function MyLoginPage() {
  return (
    <main>
      <h1>Login</h1>
      <p className="muted">TODO: MyLoginPage</p>
      <DevLogin />
    </main>
  );
}
