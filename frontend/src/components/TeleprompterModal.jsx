import React, { useState, useEffect, useRef } from 'react';

export default function TeleprompterModal({ isOpen, onClose, scriptText, title }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [scrollSpeed, setScrollSpeed] = useState(2);
  const [fontSize, setFontSize] = useState(28);
  const [isMirrored, setIsMirrored] = useState(false);
  const scrollContainerRef = useRef(null);

  useEffect(() => {
    let animationFrameId;
    const performScroll = () => {
      if (scrollContainerRef.current && isPlaying) {
        scrollContainerRef.current.scrollTop += scrollSpeed * 0.5;
        if (
          scrollContainerRef.current.scrollTop + scrollContainerRef.current.clientHeight >=
          scrollContainerRef.current.scrollHeight
        ) {
          setIsPlaying(false);
          return;
        }
      }
      if (isPlaying) {
        animationFrameId = requestAnimationFrame(performScroll);
      }
    };
    if (isPlaying) {
      animationFrameId = requestAnimationFrame(performScroll);
    }
    return () => cancelAnimationFrame(animationFrameId);
  }, [isPlaying, scrollSpeed]);

  if (!isOpen) return null;

  return (
    <div className="teleprompter-overlay">
      <div className="teleprompter-controls">
        <div className="teleprompter-info">
          <strong>Prompter:</strong> {title}
        </div>

        <div className="teleprompter-buttons">
          <button
            className={`btn-secondary ${isPlaying ? 'btn-active' : ''}`}
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? '⏸ Pause' : '▶ Start Scroll'}
          </button>

          <label className="control-label">
            Speed: {scrollSpeed}x
            <input
              type="range"
              min="1"
              max="8"
              value={scrollSpeed}
              onChange={(e) => setScrollSpeed(Number(e.target.value))}
            />
          </label>

          <label className="control-label">
            Font: {fontSize}px
            <input
              type="range"
              min="20"
              max="48"
              value={fontSize}
              onChange={(e) => setFontSize(Number(e.target.value))}
            />
          </label>

          <button
            className={`btn-secondary ${isMirrored ? 'btn-active' : ''}`}
            onClick={() => setIsMirrored(!isMirrored)}
          >
            🪞 Mirror
          </button>

          <button className="btn-secondary" onClick={onClose}>
            ✕ Exit
          </button>
        </div>
      </div>

      <div
        ref={scrollContainerRef}
        className={`teleprompter-screen ${isMirrored ? 'mirrored' : ''}`}
      >
        <div className="teleprompter-text" style={{ fontSize: `${fontSize}px` }}>
          {scriptText}
        </div>
      </div>
    </div>
  );
}
