import React from 'react';

function DressingScreen({ items }) {
  const [tab, setTab] = React.useState('vente');
  
  const filteredItems = items?.filter(i => i.type === tab) || [];

  return (
    <div className="screen-white">
      <div className="screen-header">
        <h2 className="brand-serif">Dressing</h2>
      </div>
      <div className="dressing-tabs">
        <button className={`tab ${tab === 'vente' ? 'active' : ''}`} onClick={() => setTab('vente')}>Vente</button>
        <button className={`tab ${tab === 'echange' ? 'active' : ''}`} onClick={() => setTab('echange')}>Échange</button>
      </div>
      <div className="dressing-grid">
        {filteredItems?.map(item => (
          <div key={item.id} className="dressing-item">
            <img src={item.image} alt={item.title} />
            <div className="item-info">
              <span className="item-brand brand-serif">{item.brand}</span>
              <span className="item-status">{item.status}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DressingScreen;