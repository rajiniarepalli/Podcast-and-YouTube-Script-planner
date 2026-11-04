import React, { useState } from 'react';
import TeleprompterModal from './TeleprompterModal';
import { jsPDF } from 'jspdf';

export default function ScriptViewer({ currentScript, onOpenRefine, onSaveScript }) {
  const [copied, setCopied] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isPrompterOpen, setIsPrompterOpen] = useState(false);

  if (!currentScript) {
    return (
      <div className="card empty-state">
        <div className="empty-icon">📝</div>
        <h3>No Script Generated Yet</h3>
        <p style={{ marginTop: '0.5rem' }}>
          Fill in the content brief on the left and click Generate to produce a structured,
          teleprompter-ready script.
        </p>
      </div>
    );
  }

  const wordCount = currentScript.script
    .trim()
    .split(/\s+/)
    .filter((w) => w.length > 0).length;
  const charCount = currentScript.script.length;
  const estimatedMins = Math.max(1, Math.round(wordCount / 140));

  const handleCopy = () => {
    navigator.clipboard.writeText(currentScript.script);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    const filename = `${currentScript.title.replace(/[^a-zA-Z0-9_-]/g, '_')}.txt`;
    const blob = new Blob([currentScript.script], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Professional Multi-Page PDF Exporter
  const handleDownloadPdf = () => {
    const doc = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 15;
    const maxLineWidth = pageWidth - margin * 2;

    // Title & Header
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(16);
    doc.text(currentScript.title, margin, 20);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(
      `Format: ${currentScript.content_type.toUpperCase()} | Est. Speaking Time: ~${estimatedMins} min | Words: ${wordCount}`,
      margin,
      27
    );

    // Decorative separator line
    doc.setDrawColor(180);
    doc.setLineWidth(0.5);
    doc.line(margin, 31, pageWidth - margin, 31);

    // Body text with multi-page automatic wrapping
    doc.setTextColor(20);
    doc.setFontSize(11);
    const lines = doc.splitTextToSize(currentScript.script, maxLineWidth);
    let cursorY = 38;
    const lineHeight = 6;

    for (let i = 0; i < lines.length; i++) {
      if (cursorY + lineHeight > pageHeight - margin) {
        doc.addPage();
        cursorY = margin + 5;
      }
      doc.text(lines[i], margin, cursorY);
      cursorY += lineHeight;
    }

    const filename = `${currentScript.title.replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`;
    doc.save(filename);
  };

  const handleSave = () => {
    onSaveScript(currentScript);
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <>
      <div className="card">
        <div className="viewer-header">
          <div>
            <span
              className={`badge ${
                currentScript.content_type === 'youtube' ? 'badge-youtube' : 'badge-podcast'
              }`}
            >
              {currentScript.content_type}
            </span>
            <h2 style={{ fontSize: '1.25rem', marginTop: '0.35rem', fontWeight: 700 }}>
              {currentScript.title}
            </h2>
          </div>

          <div className="action-bar">
            <button
              className="btn-secondary"
              onClick={() => setIsPrompterOpen(true)}
              title="Open full-screen teleprompter"
            >
              📺 Teleprompter
            </button>
            <button className="btn-secondary" onClick={handleCopy} title="Copy to clipboard">
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
            <button className="btn-secondary" onClick={handleDownloadPdf} title="Download formatted PDF">
              📄 Download PDF
            </button>
            <button className="btn-secondary" onClick={handleDownloadTxt} title="Download text file">
              💾 .txt
            </button>
            <button className="btn-secondary" onClick={handleSave} title="Save to local storage">
              {savedSuccess ? '✓ Saved!' : '⭐ Save'}
            </button>
            <button className="btn-primary" onClick={onOpenRefine} style={{ padding: '0.5rem 1rem' }}>
              🪄 AI Refine
            </button>
          </div>
        </div>

        <div className="metrics-bar">
          <div className="metric-pill">
            <span>Words:</span> <strong>{wordCount}</strong>
          </div>
          <div className="metric-pill">
            <span>Est. Time:</span> <strong>~{estimatedMins} min</strong>
          </div>
          <div className="metric-pill">
            <span>Chars:</span> <strong>{charCount}</strong>
          </div>
          <div className="metric-pill">
            <span>Engine:</span> <strong>{currentScript.model_used || 'Gemini'}</strong>
          </div>
        </div>

        <div className="script-content">{currentScript.script}</div>
      </div>

      <TeleprompterModal
        isOpen={isPrompterOpen}
        onClose={() => setIsPrompterOpen(false)}
        scriptText={currentScript.script}
        title={currentScript.title}
      />
    </>
  );
}
