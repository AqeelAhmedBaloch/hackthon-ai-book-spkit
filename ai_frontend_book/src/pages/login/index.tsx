import React, { useState } from 'react';
import Layout from '@theme/Layout';
import { useLocation } from '@docusaurus/router';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const location = useLocation();

  // Determine the login type based on the URL
  const loginType = location.pathname.includes('student') ? 'Student' :
                   location.pathname.includes('instructor') ? 'Instructor' :
                   location.pathname.includes('admin') ? 'Admin' : 'User';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Basic validation
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    // Here you would typically handle the login logic
    console.log(`Logging in as ${loginType}`, { email, password });
    setError('');

    // For now, just show a success message
    alert(`Login attempt for ${loginType} with email: ${email}`);
  };

  return (
    <Layout title={`${loginType} Login`} description={`Login as ${loginType}`}>
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--4 col--offset-4">
            <div className="card" style={{ boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)', borderRadius: '12px', overflow: 'hidden' }}>
              <div className="card__header text--center" style={{ backgroundColor: '#f8f9fa', padding: '1.5rem', borderBottom: '1px solid #e9ecef' }}>
                <h2 style={{ margin: 0, color: '#212529', fontWeight: '600' }}>Login as {loginType}</h2>
              </div>
              <div className="card__body" style={{ padding: '2rem' }}>
                <form onSubmit={handleSubmit}>
                  {error && (
                    <div className="alert alert--danger margin-bottom--md" style={{ borderRadius: '8px', padding: '0.75rem' }}>
                      {error}
                    </div>
                  )}
                  <div className="margin-bottom--md">
                    <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#495057' }}>
                      Email Address
                    </label>
                    <input
                      type="email"
                      id="email"
                      className="form-control"
                      placeholder="Enter your email address"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        border: '1px solid #ced4da',
                        fontSize: '1rem',
                        transition: 'border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out'
                      }}
                    />
                  </div>
                  <div className="margin-bottom--md">
                    <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500', color: '#495057' }}>
                      Password
                    </label>
                    <input
                      type="password"
                      id="password"
                      className="form-control"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.75rem 1rem',
                        borderRadius: '8px',
                        border: '1px solid #ced4da',
                        fontSize: '1rem',
                        transition: 'border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out'
                      }}
                    />
                  </div>
                  <div className="margin-bottom--md">
                    <button
                      type="submit"
                      className="button button--primary button--block"
                      style={{
                        padding: '0.75rem 1rem',
                        fontSize: '1rem',
                        fontWeight: '500',
                        borderRadius: '8px',
                        backgroundColor: '#0d6efd',
                        border: 'none',
                        cursor: 'pointer',
                        transition: 'background-color 0.15s ease-in-out, transform 0.1s ease-in-out'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#0b5ed7'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#0d6efd'}
                      onMouseDown={(e) => e.currentTarget.style.transform = 'translateY(1px)'}
                      onMouseUp={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                    >
                      Sign In
                    </button>
                  </div>
                  <div className="text--center" style={{ marginTop: '1rem' }}>
                    <a href="/forgot-password" className="link" style={{ color: '#6c757d', fontSize: '0.9rem', textDecoration: 'none' }}>
                      Forgot password?
                    </a>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default LoginPage;