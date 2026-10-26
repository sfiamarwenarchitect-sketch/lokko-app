import React from 'react';

function Navigation({ activeTab, onTabChange }) {
  return (
    <div className="bottom-nav">
      <button className={`nav-item ${activeTab === 'swipe' ? 'active' : ''}`} onClick={() => onTabChange('swipe')}>
        <span className="nav-icon">◉</span>
        <span className="nav-label">Swipe</span>
      </button>
      <button className={`nav-item ${activeTab === 'search' ? 'active' : ''}`} onClick={() => onTabChange('search')}>
        <span className="nav-icon">🔍</span>
        <span className="nav-label">Recherche</span>
      </button>
      <button className="nav-publish" onClick={() => onTabChange('publish')}>+</button>
      <button className={`nav-item ${activeTab === 'dressing' ? 'active' : ''}`} onClick={() => onTabChange('dressing')}>
        <span className="nav-icon">👗</span>
        <span className="nav-label">Dressing</span>
      </button>
      <button className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => onTabChange('profile')}>
        <span className="nav-icon">👤</span>
        <span className="nav-label">Profil</span>
      </button>
    </div>
  );
}

export default Navigation;