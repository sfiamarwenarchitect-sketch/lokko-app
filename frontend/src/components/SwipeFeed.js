import { useState, useEffect, useRef } from 'react';
import BidSheet from './BidSheet';

function SwipeFeed({ products, onFavorite }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [priceVisible, setShowPrice] = useState(false);
  const [swipeDir, setShowSwipe] = useState(null);
  const [bidProduct, setBidProduct] = useState(null);
  const touchStart = useRef(null);
  const cardRef = useRef(null);

  const currentProduct = products[currentIndex];
  const isLast = currentIndex >= products.length - 1;

  useEffect(() => {
    if (swipeDir) return;
    const timer = setTimeout(() => {
      setShowPrice(true);
    }, 3000);
    return () => clearTimeout(timer);
  }, [currentIndex, swipeDir]);

  const handleSwipe = (dir) => {
    setShowSwipe(dir);
    if (dir === 'right') {
      if (currentProduct) onFavorite(currentProduct);
    }
    setTimeout(() => {
      if (currentIndex < products.length - 1) {
        setCurrentIndex(prev => prev + 1);
      }
      setShowSwipe(null);
      setShowPrice(false);
    }, 350);
  };

  const handleTouchStart = (e) => {
    touchStart.current = { x: e.touches[0].clientX, y: e.touches[0].clientY };
  };

  const handleTouchEnd = (e) => {
    if (!touchStart.current) return;
    const touch = e.changedTouches[0];
    const dx = touch.clientX - touchStart.current.x;
    const dy = touch.clientY - touchStart.current.y;
    if (Math.abs(dx) > 80 && dx < 0) handleSwipe('left');
    else if (Math.abs(dx) > 80 && dx > 0) handleSwipe('right');
    else if (Math.abs(dy) > 80 && dy < 0) handleSwipe('up');
    touchStart.current = null;
  };

  const openBid = () => {
    if (currentProduct) setBidProduct(currentProduct);
  };

  const closeBid = () => setBidProduct(null);

  if (isLast) {
    return (
      <div className="lokko-screen-black">
        <div className="feed-end">
          <h2 className="brand-serif">FIN DU FEED</h2>
          <p className="brand-sans">Revenez plus tard</p>
        </div>
      </div>
    );
  }

  if (!currentProduct) return null;

  const swipeClass = swipeDir === 'left' ? 'swipe-left' : 
                     swipeDir === 'right' ? 'swipe-right' : 
                     swipeDir === 'up' ? 'swipe-up' : '';

  return (
    <div className="lokko-screen-black">
      <div 
        ref={cardRef}
        className={`product-card ${swipeClass}`}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        style={{ backgroundImage: `url(${currentProduct.image})` }}
      >
        <div className="card-overlay">
          <h2 className="brand-serif card-brand">{currentProduct.brand}</h2>
          <p className="brand-sans card-title">{currentProduct.title}</p>
          <div className={`card-price ${priceVisible ? 'visible' : ''}`}>
            {currentProduct.price} {currentProduct.currency}
          </div>
          <div className="card-meta">
            <span className="trust-badge">{currentProduct.seller} • Trust {currentProduct.trust}%</span>
            {currentProduct.timer && <span className="timer-badge">⏱ {currentProduct.timer}</span>}
          </div>
        </div>
        <div className="action-bar">
          <button className="action-btn" onClick={openBid} title="Proposer un échange">⇄</button>
          <button className="action-btn eye-btn" onClick={openBid} title="Voir le prix">👁</button>
          <button className="action-btn" onClick={openBid} title="Sauvegarder">🔖</button>
        </div>
      </div>
      {bidProduct && <BidSheet product={bidProduct} onClose={closeBid} />}
    </div>
  );
}

export default SwipeFeed;
