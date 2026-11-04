import React from 'react';

export default function HomePage({ onStartClick }) {
  return (
    <div className="container">
      <section className="hero">
        <span className="hero-badge">AI-Powered Content Creation</span>
        <h1 className="hero-title">
          Plan, Script, and Produce <br />
          Hit Videos & Podcasts.
        </h1>
        <p className="hero-subtitle">
          Turn rough ideas into engaging, high-retention video outlines, host narrations,
          catchy hooks, and SEO descriptions in seconds with Google Gemini.
        </p>
        <button className="btn-primary" onClick={onStartClick} style={{ fontSize: '1.1rem', padding: '0.85rem 2.2rem' }}>
          🚀 Create a Script Now
        </button>
      </section>

      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon">📹</div>
          <h3 className="feature-title">YouTube Script Architect</h3>
          <p className="feature-text">
            Generate 3 CTR-boosting titles, 45-second hooks, body breakdown with visual cues,
            descriptions, and hashtags.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🎙️</div>
          <h3 className="feature-title">Podcast Episode Engine</h3>
          <p className="feature-text">
            Create natural-sounding host scripts with pacing notes, guest interview questions,
            and show notes.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🪄</div>
          <h3 className="feature-title">One-Click AI Refinement</h3>
          <p className="feature-text">
            Easily tighten scripts, add real-world analogies, rewrite for different tones, or
            adjust lengths without restarting.
          </p>
        </div>
      </div>
    </div>
  );
}
