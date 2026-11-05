
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

  const scriptText = currentScript.script || '';
  const scriptTitle = currentScript.title || 'Generated_Script';

  const wordCount = scriptText.trim().split(/\s+/).filter(Boolean).length;
  const charCount = scriptText.length;
  const estimatedMins = Math.max(1, Math.round(wordCount / 140));

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(scriptText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      alert('Unable to copy script.');
    }
  };

  const handleDownloadTxt = () => {
    const filename = `${scriptTitle.replace(/[^a-zA-Z0-9_-]/g, '_')}.txt`;
    const blob = new Blob([scriptText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const handleDownloadPdf = () => {
    try {
      if (!scriptText.trim()) {
        alert('No script available to download.');
        return;
      }

      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      });

      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 15;
      const maxLineWidth = pageWidth - margin * 2;

      // Title
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(16);

      const titleLines = doc.splitTextToSize(scriptTitle, maxLineWidth);
      let cursorY = 20;

      doc.text(titleLines, margin, cursorY);
      cursorY += titleLines.length * 8;

      // Script information
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.setTextColor(100);

      const contentType = (currentScript.content_type || 'Script').toUpperCase();

      doc.text(
        `Format: ${contentType} | Estimated Time: ${estimatedMins} min | Words: ${wordCount}`,
        margin,
        cursorY
      );

      cursorY += 8;

      doc.setDrawColor(180);
      doc.setLineWidth(0.5);
      doc.line(margin, cursorY, pageWidth - margin, cursorY);

      cursorY += 8;

      // Script body
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(11);
      doc.setTextColor(20);

      const lines = doc.splitTextToSize(scriptText, maxLineWidth);
      const lineHeight = 6;

      for (let i = 0; i < lines.length; i++) {
        if (cursorY + lineHeight > pageHeight - margin) {
          doc.addPage();
          cursorY = margin + 5;
        }

        doc.text(lines[i], margin, cursorY);
        cursorY += lineHeight;
      }

      const filename = `${scriptTitle.replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`;

      doc.save(filename);

    } catch (error) {
      console.error('PDF download error:', error);
      alert('PDF download failed. Please try again.');
    }
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
                currentScript.content_type === 'youtube'
                  ? 'badge-youtube'
                  : 'badge-podcast'
              }`}
            >
              {currentScript.content_type || 'Script'}
            </span>

            <h2 style={{ fontSize: '1.25rem', marginTop: '0.35rem', fontWeight: 700 }}>
              {scriptTitle}
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

            <button className="btn-secondary" onClick={handleCopy}>
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>

            <button className="btn-secondary" onClick={handleDownloadPdf}>
              📄 Download PDF
            </button>

            <button className="btn-secondary" onClick={handleDownloadTxt}>
              💾 .txt
            </button>

            <button className="btn-secondary" onClick={handleSave}>
              {savedSuccess ? '✓ Saved!' : '⭐ Save'}
            </button>

            <button
              className="btn-primary"
              onClick={onOpenRefine}
              style={{ padding: '0.5rem 1rem' }}
            >
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

        <div className="script-content">{scriptText}</div>
      </div>

      <TeleprompterModal
        isOpen={isPrompterOpen}
        onClose={() => setIsPrompterOpen(false)}
        scriptText={scriptText}
        title={scriptTitle}
      />
    </>
  );
}
