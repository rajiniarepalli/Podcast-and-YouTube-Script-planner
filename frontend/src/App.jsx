
import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import PlannerPage from './pages/PlannerPage';
import SavedScripts from './components/SavedScripts';
import DocumentPage from './pages/DocumentPage';
import { storageService } from './services/storage';

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [currentScript, setCurrentScript] = useState(null);
  const [savedList, setSavedList] = useState([]);

  useEffect(() => {
    setSavedList(storageService.getSavedScripts());
  }, []);

  const handleSaveCurrentScript = (scriptToSave) => {
    const saved = storageService.saveScript(scriptToSave);
    if (saved) {
      setSavedList(storageService.getSavedScripts());
    }
  };

  const handleDeleteSavedScript = (id) => {
    const updated = storageService.deleteScript(id);
    setSavedList(updated);
  };

  const handleSelectFromSaved = (item) => {
    setCurrentScript(item);
    setActiveTab('planner');
  };

  return (
    <div>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main>
        {activeTab === 'home' && (
          <HomePage onStartClick={() => setActiveTab('planner')} />
        )}

        {activeTab === 'planner' && (
          <PlannerPage
            currentScript={currentScript}
            setCurrentScript={setCurrentScript}
            onSaveScript={handleSaveCurrentScript}
          />
        )}

        {activeTab === 'saved' && (
          <div className="container">
            <SavedScripts
              savedList={savedList}
              onSelectScript={handleSelectFromSaved}
              onDeleteScript={handleDeleteSavedScript}
            />
          </div>
        )}

        {activeTab === 'documents' && <DocumentPage />}
      </main>
    </div>
  );
}
