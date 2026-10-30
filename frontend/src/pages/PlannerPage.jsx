import React, { useState } from 'react';
import ScriptForm from '../components/ScriptForm';
import ScriptViewer from '../components/ScriptViewer';
import RefineModal from '../components/RefineModal';
import { scriptApi } from '../services/api';

export default function PlannerPage({ currentScript, setCurrentScript, onSaveScript }) {
  const [isLoading, setIsLoading] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleGenerateScript = async (formData) => {
    setIsLoading(true);
    setErrorMessage('');
    try {
      const result = await scriptApi.generateScript(formData);
      setCurrentScript(result);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to communicate with AI server. Is the backend running?';
      setErrorMessage(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplyRefine = async (refinePayload) => {
    if (!currentScript) return;
    setIsRefining(true);
    setErrorMessage('');
    try {
      const result = await scriptApi.refineScript({
        script: currentScript.script,
        ...refinePayload,
      });

      setCurrentScript((prev) => ({
        ...prev,
        script: result.refined_script,
      }));
      setIsModalOpen(false);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to refine script.';
      setErrorMessage(detail);
    } finally {
      setIsRefining(false);
    }
  };

  return (
    <div className="container">
      {errorMessage && (
        <div className="alert alert-error" style={{ marginTop: '1.5rem' }}>
          <strong>Error:</strong> {errorMessage}
        </div>
      )}

      <div className="planner-grid">
        <ScriptForm onGenerate={handleGenerateScript} isLoading={isLoading} />
        <ScriptViewer
          currentScript={currentScript}
          onOpenRefine={() => setIsModalOpen(true)}
          onSaveScript={onSaveScript}
        />
      </div>

      <RefineModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onApplyRefine={handleApplyRefine}
        isRefining={isRefining}
      />
    </div>
  );
}
