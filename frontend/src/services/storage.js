const STORAGE_KEY = 'scriptcraft_saved_scripts';

export const storageService = {
  getSavedScripts: () => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (err) {
      return [];
    }
  },
  saveScript: (scriptItem) => {
    try {
      const existing = storageService.getSavedScripts();
      const newEntry = {
        id: Date.now().toString(),
        savedAt: new Date().toISOString(),
        ...scriptItem,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify([newEntry, ...existing]));
      return newEntry;
    } catch (err) {
      return null;
    }
  },
  deleteScript: (id) => {
    try {
      const existing = storageService.getSavedScripts();
      const filtered = existing.filter((item) => item.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return filtered;
    } catch (err) {
      return [];
    }
  },
};
