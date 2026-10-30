import React from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  return (
    <nav className="navbar">
      <div className="container nav-container">
        <div className="nav-brand" onClick={() => setActiveTab('home')}>
          <div className="brand-icon">⚡</div>
          <span>ScriptCraft AI</span>
        </div>
        <div className="nav-links">
          <button
            className={`nav-btn ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            Overview
          </button>
          <button
            className={`nav-btn ${activeTab === 'planner' ? 'active' : ''}`}
            onClick={() => setActiveTab('planner')}
          >
            Script Studio
          </button>
          <button
            className={`nav-btn ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            Saved Scripts
          </button>
        </div>
      </div>
    </nav>
  );
}
