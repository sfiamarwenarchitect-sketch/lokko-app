import React from 'react';

function SearchScreen() {
  return (
    <div className="screen-white">
      <div className="screen-header">
        <h2 className="brand-serif">Recherche</h2>
      </div>
      <div className="screen-content">
        <input type="text" className="search-input" placeholder="Rechercher une pièce..." />
        <p>Recherche et filtres</p>
      </div>
    </div>
  );
}

export default SearchScreen;
