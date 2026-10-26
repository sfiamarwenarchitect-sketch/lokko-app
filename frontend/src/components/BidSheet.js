import { useState } from 'react';

function BidSheet({ product, onClose }) {
  const [bidAmount, setBidAmount] = useState(Math.round(product.price * 0.75));
  const minBid = Math.round(product.price * 0.70);

  return (
    <div className="sheet-overlay" onClick={onClose}>
      <div className="sheet-content" onClick={e => e.stopPropagation()}>
        <div className="sheet-handle"></div>
        <h3 className="brand-serif sheet-title">{product.brand} {product.title}</h3>
        <p className="sheet-subtitle">Offre privée — Enchère boucle</p>
        
        <div className="bid-input-group">
          <input
            type="number"
            className="bid-input"
            value={bidAmount}
            onChange={e => setBidAmount(Number(e.target.value))}
            placeholder="Montant de l'offre"
          />
          <span className="bid-currency">{product.currency}</span>
        </div>
        
        <div className="bid-rule">
          Règle des 70% : l'offre doit être ≥ <strong>{minBid}{product.currency}</strong> (70% de l'estimation)
        </div>
        
        <button className="btn-submit" onClick={onClose}>
          Soumettre l'offre
        </button>
        <button className="btn-cancel" onClick={onClose}>
          Annuler
        </button>
      </div>
    </div>
  );
}

export default BidSheet;