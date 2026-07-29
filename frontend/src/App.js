import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// --- Mock Data for Demo ---
const MOCK_PRODUCTS = [
  {
    id: 1,
    title: 'Chanel Classic Flap Bag',
    brand: 'Chanel',
    description: 'Authentique, taille petite',
    price: 3200,
    estimated_value: 3500,
    min_bid: 2450,
    size: 'S',
    condition: 'Like New',
    images: ['https://picsum.photos/400/500?random=1'],
    trust_score: 92,
    time_remaining: '46h',
    owner: 'amina_style'
  },
  {
    id: 2,
    title: 'Nike Air Max 90',
    brand: 'Nike',
    description: 'Nouvelles, taille 42',
    price: 145,
    estimated_value: 180,
    min_bid: 126,
    size: 'M',
    condition: 'New',
    images: ['https://picsum.photos/400/500?random=2'],
    trust_score: 88,
    time_remaining: '38h',
    owner: 'yassine_lux'
  },
  {
    id: 3,
    title: 'Lemarié Paris — Robe Soirée',
    brand: 'Lemarié',
    description: 'Pièce unique, parfait état',
    price: 850,
    estimated_value: 1000,
    min_bid: 700,
    size: 'M',
    condition: 'Like New',
    images: ['https://picsum.photos/400/500?random=3'],
    trust_score: 95,
    time_remaining: '22h',
    owner: 'sara_chic'
  },
  {
    id: 4,
    title: 'Vintage Levi\'s 501',
    brand: 'Levi\'s',
    description: 'Années 70, authentique',
    price: 120,
    estimated_value: 150,
    min_bid: 105,
    size: 'L',
    condition: 'Good',
    images: ['https://picsum.photos/400/500?random=4'],
    trust_score: 85,
    time_remaining: '40h',
    owner: 'karim_vintage'
  },
  {
    id: 5,
    title: 'Rolex Submariner',
    brand: 'Rolex',
    description: 'Année 2018, boîte et papiers',
    price: 6500,
    estimated_value: 7200,
    min_bid: 5040,
    size: 'S',
    condition: 'Like New',
    images: ['https://picsum.photos/400/500?random=5'],
    trust_score: 97,
    time_remaining: '15h',
    owner: 'amina_style'
  },
  {
    id: 6,
    title: 'Adidas Yeezy Boost 350',
    brand: 'Adidas',
    description: 'Taille 43, portées 3 fois',
    price: 220,
    estimated_value: 280,
    min_bid: 196,
    size: 'M',
    condition: 'Good',
    images: ['https://picsum.photos/400/500?random=6'],
    trust_score: 90,
    time_remaining: '28h',
    owner: 'yassine_lux'
  }
];

const AI_LOOK_CARD = {
  id: 'ai_look_1',
  is_ai_card: true,
  title: 'Look du Jour',
  description: 'Pièce IA recommandée pour vous',
  matching_score: 94,
  product: {
    id: 99,
    brand: 'Exchange',
    title: 'Maison Margiela Replica',
    description: 'Pièce d\'échange trouvée par l\'IA',
    images: ['https://picsum.photos/400/500?random=7'],
    trust_score: 96
  }
};

function App() {
  const [activeTab, setActiveTab] = useState('feed');
  const [products, setProducts] = useState(MOCK_PRODUCTS);
  const [currentProduct, setCurrentProduct] = useState(null);
  const [showPrice, setShowPrice] = useState(false);
  const [showBidModal, setShowBidModal] = useState(false);
  const [bidAmount, setBidAmount] = useState('');
  const [bidError, setBidError] = useState('');
  const [swipes, setSwipes] = useState([]);
  const [bids, setBids] = useState([]);
  const [myListings, setMyListings] = useState([]);
  const [priceTimer, setPriceTimer] = useState(null);
  const swipeCounter = useRef(0);
  const [showListings, setShowListings] = useState(false);

  // Simulate feed with AI card insertion every 3 swipes (demo: reduced from 10)
  const getFeedWithAICards = () => {
    const feed = [];
    products.forEach((product, index) => {
      feed.push(product);
      // Insert AI Look Card every 3 products
      if ((index + 1) % 3 === 0 && index < products.length - 1) {
        feed.push(AI_LOOK_CARD);
      }
    });
    return feed;
  }

  const feed = getFeedWithAICards();

  // Auto-show price after 3 seconds
  useEffect(() => {
    if (currentProduct && !currentProduct.is_ai_card) {
      setShowPrice(false);
      const timer = setTimeout(() => {
        setShowPrice(true);
      }, 3000);
      setPriceTimer(timer);
      return () => clearTimeout(timer);
    }
  }, [currentProduct]);

  const handleSwipe = (direction) => {
    if (currentProduct) {
      setSwipes(prev => [...prev, { product: currentProduct, direction, time: new Date() }]);
      swipeCounter.current++;
      setCurrentProduct(null);
      setShowPrice(false);
    }
  };

  const handleOffer = (product) => {
    if (product.is_ai_card) {
      setCurrentProduct(product.product || product);
      return;
    }
    setCurrentProduct(product);
    setShowBidModal(true);
    setBidAmount('');
    setBidError('');
  };

  const placeBid = () => {
    const amount = parseFloat(bidAmount);
    const minBid = currentProduct.min_bid || currentProduct.estimated_value * 0.7;

    if (amount < minBid) {
      setBidError(`Offre minimale: ${minBid.toFixed(0)}€ (70% de l'estimation)`);
      return;
    }

    setBids(prev => [...prev, {
      product: currentProduct,
      amount: amount,
      time: new Date(),
      status: 'pending'
    }]);
    setShowBidModal(false);
    setBidError('');

    // Reset to next product
    setCurrentProduct(null);
  };

  const renderProductCard = (product) => {
    if (product.is_ai_card || product.is_ai_look) {
      // AI Look Card
      const aiProduct = product.product || product;
      return (
        <div className="product-card fade-in">
          <div className="product-image-container">
            <img 
              src={aiProduct.images?.[0] || 'https://picsum.photos/400/500?random=ai'} 
              alt="AI Look"
              className="product-image"
            />
            <div className="brand-badge" style={{background: 'rgba(197, 162, 86, 0.3)', color: '#C5A256'}}>
              ✨ AI LOOK DU JOUR
            </div>
          </div>
          <div className="product-info">
            <p className="trust-badge" style={{marginBottom: '8px'}}>
              🤖 {product.matching_score || 94}% match IA
            </p>
            <h3 className="product-title">{aiProduct.brand} — {aiProduct.title}</h3>
            <p style={{color: 'var(--muted)', fontSize: '13px', marginTop: '4px'}}>
              {product.description || aiProduct.description}
            </p>
            <p style={{color: 'var(--gold)', fontSize: '12px', marginTop: '8px', fontStyle: 'italic'}}>
              Échange disponible avec {aiProduct.trust_score || 96}% confiance IA
            </p>
          </div>
        </div>
      );
    }

    // Regular product card
    return (
      <div className="product-card fade-in">
        <div className="product-image-container">
          <img 
            src={product.images?.[0] || 'https://picsum.photos/400/500?random=' + product.id} 
            alt={product.title}
            className="product-image"
          />
          <div className="brand-badge">{product.brand}</div>
          <div className="timer-badge">{product.time_remaining} restante(s)</div>
          <div className={`price-overlay ${showPrice ? 'price-visible' : 'price-hidden'}`}>
            <div className="price-value">{product.price}€</div>
            <div className="price-label">À partir de</div>
          </div>
        </div>
        <div className="product-info">
          <h3 className="product-title">{product.title}</h3>
          <div style={{display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '6px'}}>
            <span className="product-brand serif">{product.brand}</span>
            <span className="trust-badge">🏆 {product.trust_score} IA</span>
          </div>
          <div className="product-meta">
            <span>📏 {product.size}</span>
            <span>✨ {product.condition}</span>
            <span>👤 {product.owner}</span>
          </div>
        </div>
        <div className="swipe-buttons">
          <button className="swipe-btn swipe-btn-pass" onClick={() => handleSwipe('left')}>
            ← Passer
          </button>
          <button 
            className="swipe-btn swipe-btn-eye" 
            onClick={() => setShowPrice(!showPrice)}
          >
            👁
          </button>
          <button className="swipe-btn swipe-btn-offer" onClick={() => handleOffer(product)}>
            Offrir →
          </button>
        </div>
      </div>
    );
  };

  const renderBidModal = () => {
    if (!showBidModal || !currentProduct) return null;
    const minBid = currentProduct.min_bid || currentProduct.estimated_value * 0.7;

    return (
      <div className="modal-overlay" onClick={() => setShowBidModal(false)}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <h2 className="modal-title">Faire une offre privée</h2>
          <div style={{textAlign: 'center', marginBottom: '20px'}}>
            <img 
              src={currentProduct.images?.[0]} 
              alt={currentProduct.title}
              style={{width: '80px', height: '80px', objectFit: 'cover', borderRadius: '12px', marginBottom: '12px'}}
            />
            <p className="product-brand serif" style={{marginBottom: '4px'}}>{currentProduct.brand} — {currentProduct.title}</p>
            <p style={{color: 'var(--gold)', fontSize: '14px'}}>
              Prix départ: {currentProduct.price}€
            </p>
          </div>

          <input
            type="number"
            className="bid-input"
            placeholder="Votre offre en €"
            value={bidAmount}
            onChange={e => {
              setBidAmount(e.target.value);
              setBidError('');
            }}
            onFocus={e => e.target.select()}
          />

          <p className="min-bid-hint">
            Offre minimale: <strong>{minBid.toFixed(0)}€</strong> (70% de l'estimation {currentProduct.estimated_value}€)
          </p>

          {bidError && (
            <p style={{color: 'var(--timer-red)', textAlign: 'center', marginBottom: '12px', fontSize: '13px'}}>
              ⚠ {bidError}
            </p>
          )}

          <button className="modal-btn modal-btn-primary" onClick={placeBid}>
            Valider l'offre
          </button>
          <button className="modal-btn modal-btn-secondary" onClick={() => setShowBidModal(false)}>
            Annuler
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="app-container">
      {/* Header */}
      <div className="header">
        <div className="header-logo serif">LOKKO</div>
        <div style={{display: 'flex', gap: '16px', alignItems: 'center'}}>
          <span className="header-icon" onClick={() => {setActiveTab('dressing'); setShowListings(true);}}>👛</span>
          <span className="header-icon">🔔</span>
          <span className="header-icon" style={{fontSize: '16px'}}>👤</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'feed' ? 'tab-active' : ''}`}
          onClick={() => {setActiveTab('feed'); setShowListings(false);}}
        >
          FEED
        </div>
        <div 
          className={`tab ${activeTab === 'dressing' ? 'tab-active' : ''}`}
          onClick={() => {setActiveTab('dressing'); setShowListings(true);}}
        >
          DRESSING
        </div>
        <div 
          className={`tab ${activeTab === 'bids' ? 'tab-active' : ''}`}
          onClick={() => {setActiveTab('bids');}}
        >
          OFFRES {bids.length > 0 && `(${bids.length})`}
        </div>
        <div 
          className={`tab ${activeTab === 'exchanges' ? 'tab-active' : ''}`}
          onClick={() => {setActiveTab('exchanges');}}
        >
          ÉCHANGE
        </div>
      </div>

      {/* Content */}
      {showListings ? (
        <div style={{padding: '20px'}}>
          <div className="empty-state">
            <h2 className="serif">Mon Dressing</h2>
            <p style={{marginBottom: '20px'}}>Vos pièces en vente et échanges</p>
            <div style={{
              background: 'var(--card-bg)',
              padding: '20px',
              borderRadius: '12px',
              maxWidth: '300px'
            }}>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '12px'}}>
                <span style={{color: 'var(--muted)', fontSize: '13px'}}>Pièces actives</span>
                <span style={{fontWeight: '600'}}>3</span>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '12px'}}>
                <span style={{color: 'var(--muted)', fontSize: '13px'}}>Offres reçues</span>
                <span style={{fontWeight: '600'}}>5</span>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '12px'}}>
                <span style={{color: 'var(--muted)', fontSize: '13px'}}>Score de confiance</span>
                <span style={{fontWeight: '600', color: 'var(--gold)'}}>88 🏆</span>
              </div>
              <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '12px'}}>
                <span style={{color: 'var(--muted)', fontSize: '13px'}}>Vendus</span>
                <span style={{fontWeight: '600'}}>12</span>
              </div>
              <hr style={{border: 'none', borderTop: '1px solid rgba(245,245,240,0.08)', margin: '16px 0'}} />
              <button className="modal-btn modal-btn-primary" style={{width: '100%'}}>
                + Ajouter une pièce
              </button>
            </div>
            <p style={{marginTop: '16px', color: 'var(--muted)', fontSize: '12px', fontStyle: 'italic'}}>
              Commission Lokko: 8% par vente
            </p>
          </div>
        </div>
      ) : activeTab === 'bids' ? (
        <div style={{padding: '20px'}}>
          <h2 className="serif" style={{marginBottom: '16px'}}>Vos offres</h2>
          {bids.length === 0 ? (
            <div className="empty-state">
              <h2>Aucune offre</h2>
              <p>Vos offres privées apparaîtront ici</p>
            </div>
          ) : (
            bids.map((bid, i) => (
              <div key={i} style={{
                background: 'var(--card-bg)',
                padding: '16px',
                borderRadius: '12px',
                marginBottom: '12px'
              }}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '8px'}}>
                  <strong>{bid.product.title}</strong>
                  <span style={{color: 'var(--gold)', fontWeight: '600'}}>{bid.amount}€</span>
                </div>
                <p style={{color: 'var(--muted)', fontSize: '13px'}}>{bid.product.brand} — {bid.product.description}</p>
                <div style={{marginTop: '8px', display: 'flex', gap: '8px'}}>
                  <span className="trust-badge">⏱ En attente</span>
                  <span style={{fontSize: '11px', color: 'var(--timer-red)'}}>12h restants</span>
                </div>
              </div>
            ))
          )}
        </div>
      ) : activeTab === 'exchanges' ? (
        <div style={{padding: '20px'}}>
          <h2 className="serif" style={{marginBottom: '16px'}}>Échanges</h2>
          <div className="empty-state">
            <h2>Loop Bartering</h2>
            <p style={{marginBottom: '20px'}}>Proposez des pièces en échange d'autres pièces</p>
            <p style={{color: 'var(--muted)', fontSize: '12px', maxWidth: '280px', lineHeight: '1.6'}}>
              Plusieurs utilisateurs peuvent proposer des pièces via le bouton d'échange. 
              Vous validez plusieurs échanges en ordre de préférence.
            </p>
          </div>
        </div>
      ) : (
        <div className="swipe-feed">
          {feed.map((product, index) => {
            // Only show cards up to current index
            if (currentProduct) return null;
            if (index > 0) return null; // Show first card or after swiping
            return renderProductCard(product);
          })}
          
          {/* Show next product after swipe */}
          {swipes.length > 0 && !currentProduct && (
            <div style={{marginTop: '8px'}}>
              {feed[Math.min(swipes.length, feed.length - 1)] && 
                !feed[Math.min(swipes.length, feed.length - 1)].is_ai_card ?
                null : null // Will be handled by feed logic
              }
              <div className="empty-state">
                <p style={{color: 'var(--muted)', marginBottom: '12px'}}>
                  Vous avez swipé {swipes.length} pièce(s)
                </p>
                <button 
                  className="modal-btn modal-btn-secondary" 
                  style={{maxWidth: '200px'}}
                  onClick={() => setSwipes([])}
                >
                  Revoir tout le feed
                </button>
              </div>
            </div>
          )}

          {swipes.length === 0 && (
            <div className="empty-state">
              <h2 className="serif">Le Feed Lokko</h2>
              <p style={{color: 'var(--muted)', maxWidth: '280px', marginBottom: '24px', lineHeight: '1.6'}}>
                Découvrez des pièces uniques par swipe. Le prix reste caché jusqu'à ce que vous le vouliez.
              </p>
              <p style={{color: 'var(--gold)', fontSize: '13px', marginBottom: '20px'}}>
                ✨ L'IA insère des "Look du Jour" tous les 10 swipes
              </p>
              <p style={{fontSize: '12px', color: 'var(--muted)', lineHeight: '1.8'}}>
                ← Passer | 👁 Voir le prix | Offrir →
              </p>
            </div>
          )}
        </div>
      )}

      {/* Bid Modal */}
      {renderBidModal()}
    </div>
  );
}

export default App;
