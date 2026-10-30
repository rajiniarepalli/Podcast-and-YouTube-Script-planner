import React, { useState } from 'react';

export default function RefineModal({ isOpen, onClose, onApplyRefine, isRefining }) {
  const [action, setAction] = useState('improve_hook');
  const [targetTone, setTargetTone] = useState('Conversational');
  const [customInstruction, setCustomInstruction] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    onApplyRefine({
      action,
      target_tone: action === 'change_tone' ? targetTone : null,
      custom_instruction: action === 'custom' ? customInstruction : null,
    });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h2 style={{ marginBottom: '1rem', fontSize: '1.3rem' }}>🪄 Refine Script with Gemini</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
          Select how you want the AI to polish or reshape your existing script.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Select Refinement Goal</label>
            <select
              className="form-select"
              value={action}
              onChange={(e) => setAction(e.target.value)}
            >
              <option value="improve_hook">🎣 Make Hook & Intro punchier</option>
              <option value="make_shorter">✂️ Make it shorter (Remove filler)</option>
              <option value="make_longer">📖 Expand with deeper talking points</option>
              <option value="add_examples">💡 Add concrete real-world examples</option>
              <option value="simplify">🧩 Simplify jargon for beginners</option>
              <option value="change_tone">🎭 Shift overall tone</option>
              <option value="custom">✏️ Custom prompt instruction</option>
            </select>
          </div>

          {action === 'change_tone' && (
            <div className="form-group">
              <label className="form-label">New Tone</label>
              <select
                className="form-select"
                value={targetTone}
                onChange={(e) => setTargetTone(e.target.value)}
              >
                <option value="Conversational">Conversational</option>
                <option value="Educational">Educational</option>
                <option value="Entertaining">Entertaining</option>
                <option value="Professional">Professional</option>
                <option value="Friendly">Friendly</option>
              </select>
            </div>
          )}

          {action === 'custom' && (
            <div className="form-group">
              <label className="form-label">Custom Instruction</label>
              <textarea
                className="form-textarea"
                placeholder="e.g., Focus more on budget-friendly gear."
                value={customInstruction}
                onChange={(e) => setCustomInstruction(e.target.value)}
                required
              />
            </div>
          )}

          <div className="modal-footer">
            <button
              type="button"
              className="btn-secondary"
              onClick={onClose}
              disabled={isRefining}
            >
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={isRefining}>
              {isRefining ? 'Polishing Script...' : 'Apply Refinement'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
