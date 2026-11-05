
import React, { useState } from 'react';

export default function DocumentPage() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [asking, setAsking] = useState(false);
  const [message, setMessage] = useState('');

  // Render Backend URL
  const API_URL =
    import.meta.env.VITE_API_URL ||
    'https://podcast-script-planner.onrender.com';

  // Upload PDF
  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a PDF file.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      setUploaded(false);
      setMessage('');
      setAnswer('');

      const response = await fetch(
        `${API_URL}/api/documents/upload`,
        {
          method: 'POST',
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'PDF upload failed.');
      }

      setUploaded(true);
      setMessage(
        'PDF uploaded successfully! You can now ask questions.'
      );

    } catch (error) {
      setUploaded(false);
      setMessage(error.message || 'Unable to upload PDF.');
    } finally {
      setUploading(false);
    }
  };

  // Ask Gemini about uploaded PDF
  const handleAsk = async () => {
    if (!question.trim()) {
      setMessage('Please enter a question.');
      return;
    }

    if (!uploaded) {
      setMessage('Please upload a PDF first.');
      return;
    }

    try {
      setAsking(true);
      setMessage('');
      setAnswer('');

      const response = await fetch(
        `${API_URL}/api/documents/ask`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            question: question.trim()
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to get answer.');
      }

      setAnswer(data.answer || 'No answer received from Gemini.');

    } catch (error) {
      setMessage(error.message || 'Something went wrong.');
    } finally {
      setAsking(false);
    }
  };

  return (
    <div
      className="container"
      style={{
        padding: '30px 20px',
        maxWidth: '1100px',
        margin: '0 auto',
        fontFamily:
          "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
      }}
    >
      <h1
        style={{
          color: '#ffffff',
          fontWeight: 800,
          fontSize: '36px',
          letterSpacing: '-0.5px',
          marginBottom: '8px'
        }}
      >
        PDF Knowledge Base
      </h1>

      <p
        style={{
          color: '#cbd5e1',
          fontSize: '16px',
          fontWeight: 600,
          lineHeight: '1.5',
          marginBottom: '28px'
        }}
      >
        Upload your PDF and ask questions. Gemini AI will answer
        using information retrieved from your document.
      </p>

      <div
        style={{
          background: '#ffffff',
          color: '#111827',
          padding: '30px',
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
        }}
      >
        <h2
          style={{
            color: '#0f172a',
            fontWeight: 800,
            fontSize: '22px',
            marginBottom: '14px'
          }}
        >
          Upload PDF
        </h2>

        <input
          type="file"
          accept=".pdf,application/pdf"
          style={{
            color: '#111827',
            display: 'block',
            marginBottom: '16px',
            fontSize: '14px'
          }}
          onChange={(e) => {
            setFile(e.target.files[0] || null);
            setUploaded(false);
            setAnswer('');
            setMessage('');
          }}
        />

        <button
          onClick={handleUpload}
          disabled={uploading || !file}
          style={{
            padding: '10px 20px',
            fontWeight: 600,
            borderRadius: '6px',
            cursor: uploading || !file ? 'not-allowed' : 'pointer',
            background: '#2563eb',
            color: '#ffffff',
            border: 'none',
            opacity: uploading || !file ? 0.6 : 1
          }}
        >
          {uploading ? 'Uploading...' : 'Upload PDF'}
        </button>

        <hr
          style={{
            margin: '28px 0',
            border: 'none',
            borderTop: '1px solid #e2e8f0'
          }}
        />

        <h2
          style={{
            color: '#0f172a',
            fontWeight: 800,
            fontSize: '22px',
            marginBottom: '14px'
          }}
        >
          Ask Questions
        </h2>

        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Example: Summarize the main topics in this PDF."
          rows="4"
          style={{
            width: '100%',
            padding: '12px 14px',
            borderRadius: '8px',
            border: '1px solid #cbd5e1',
            boxSizing: 'border-box',
            color: '#0f172a',
            background: '#ffffff',
            fontSize: '15px',
            outline: 'none'
          }}
        />

        <br />
        <br />

        <button
          onClick={handleAsk}
          disabled={asking || uploading || !uploaded || !question.trim()}
          style={{
            padding: '10px 20px',
            fontWeight: 600,
            borderRadius: '6px',
            cursor:
              asking || uploading || !uploaded || !question.trim()
                ? 'not-allowed'
                : 'pointer',
            background: '#16a34a',
            color: '#ffffff',
            border: 'none',
            opacity:
              asking || uploading || !uploaded || !question.trim()
                ? 0.6
                : 1
          }}
        >
          {asking ? 'Generating Answer...' : 'Ask Gemini'}
        </button>

        {message && (
          <p
            style={{
              marginTop: '15px',
              color: '#0284c7',
              fontWeight: 600
            }}
          >
            {message}
          </p>
        )}

        {answer && (
          <div
            style={{
              marginTop: '25px',
              padding: '20px',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '10px',
              color: '#0f172a'
            }}
          >
            <h3
              style={{
                color: '#0f172a',
                fontWeight: 700,
                marginBottom: '8px'
              }}
            >
              AI Generated Answer
            </h3>

            <p
              style={{
                whiteSpace: 'pre-wrap',
                color: '#334155',
                fontSize: '15px',
                lineHeight: '1.7',
                fontWeight: 500,
                margin: 0
              }}
            >
              {answer}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
