import React from 'react';

export default function SavedScripts({ savedList, onSelectScript, onDeleteScript }) {
  if (savedList.length === 0) {
    return (
      <div className="card empty-state" style={{ marginTop: '2rem' }}>
        <div className="empty-icon">📂</div>
        <h3>No Saved Scripts Yet</h3>
        <p style={{ marginTop: '0.5rem' }}>
          Generate a script in the studio and click <strong>Save</strong> to store it in your browser.
        </p>
      </div>
    );
  }

  return (
    <div style={{ marginTop: '2rem' }}>
      <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Saved Scripts ({savedList.length})</h2>
      <div className="history-grid">
        {savedList.map((item) => (
          <div key={item.id} className="history-card">
            <div>
              <div className="history-meta">
                <span
                  className={`badge ${
                    item.content_type === 'youtube' ? 'badge-youtube' : 'badge-podcast'
                  }`}
                >
                  {item.content_type}
                </span>
                <span>{new Date(item.savedAt).toLocaleDateString()}</span>
              </div>
              <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>{item.title}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Duration: {item.estimated_duration}
              </p>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1.25rem' }}>
              <button
                className="btn-primary"
                style={{ flex: 1, padding: '0.45rem' }}
                onClick={() => onSelectScript(item)}
              >
                Open in Studio
              </button>
              <button
                className="btn-secondary"
                style={{ color: '#ef4444', borderColor: 'rgba(239, 68, 68, 0.3)' }}
                onClick={() => onDeleteScript(item.id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
