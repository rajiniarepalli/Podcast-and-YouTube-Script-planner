import React, { useState } from 'react';

export default function ScriptForm({ onGenerate, isLoading }) {
  const [formData, setFormData] = useState({
    content_type: 'youtube',
    topic: '',
    target_audience: 'General Audience',
    language: 'English',
    tone: 'Conversational',
    duration: '5-7 minutes',
    keywords: '',
    additional_instructions: '',
  });

  const [validationError, setValidationError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleContentTypeChange = (type) => {
    setFormData((prev) => ({
      ...prev,
      content_type: type,
      duration: type === 'youtube' ? '5-7 minutes' : '15-20 minutes',
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setValidationError('');

    if (!formData.topic.trim()) {
      setValidationError('Please enter a content topic or idea.');
      return;
    }
    if (formData.topic.trim().length < 5) {
      setValidationError('Topic must be at least 5 characters long.');
      return;
    }

    onGenerate(formData);
  };

  return (
    <div className="card">
      <h2 style={{ marginBottom: '1.25rem', fontSize: '1.25rem', fontWeight: 700 }}>
        1. Content Specifications
      </h2>

      {validationError && <div className="alert alert-error">{validationError}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Format</label>
          <div className="pill-selector">
            <div
              className={`pill-option ${formData.content_type === 'youtube' ? 'active' : ''}`}
              onClick={() => handleContentTypeChange('youtube')}
            >
              📹 YouTube Video
            </div>
            <div
              className={`pill-option ${formData.content_type === 'podcast' ? 'active' : ''}`}
              onClick={() => handleContentTypeChange('podcast')}
            >
              🎙️ Podcast Episode
            </div>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Topic or Core Idea *</label>
          <input
            type="text"
            name="topic"
            className="form-input"
            placeholder="e.g., How to start freelance programming with zero experience"
            value={formData.topic}
            onChange={handleChange}
            maxLength={300}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Target Audience</label>
          <input
            type="text"
            name="target_audience"
            className="form-input"
            placeholder="e.g., Computer science students, beginners"
            value={formData.target_audience}
            onChange={handleChange}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div className="form-group">
            <label className="form-label">Language</label>
            <input
              type="text"
              name="language"
              className="form-input"
              value={formData.language}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Tone</label>
            <select
              name="tone"
              className="form-select"
              value={formData.tone}
              onChange={handleChange}
            >
              <option value="Conversational">Conversational</option>
              <option value="Educational">Educational</option>
              <option value="Entertaining">Entertaining</option>
              <option value="Professional">Professional</option>
              <option value="Friendly">Friendly</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Target Duration</label>
          <input
            type="text"
            name="duration"
            className="form-input"
            placeholder="e.g., 8-10 minutes"
            value={formData.duration}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Keywords (Optional)</label>
          <input
            type="text"
            name="keywords"
            className="form-input"
            placeholder="e.g., portfolio, outreach, GitHub"
            value={formData.keywords}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Additional Instructions</label>
          <textarea
            name="additional_instructions"
            className="form-textarea"
            placeholder="e.g., Emphasize practical examples."
            value={formData.additional_instructions}
            onChange={handleChange}
          />
        </div>

        <button
          type="submit"
          className="btn-primary"
          style={{ width: '100%', marginTop: '0.5rem' }}
          disabled={isLoading}
        >
          {isLoading ? 'Crafting Your Script...' : '✨ Generate Full Script'}
        </button>
      </form>
    </div>
  );
}
