import React from 'react';
import Navigation from './components/Navigation';
import SwipeFeed from './components/SwipeFeed';
import SearchScreen from './components/SearchScreen';
import StudioScreen from './components/StudioScreen';
import DressingScreen from './components/DressingScreen';
import ProfileScreen from './components/ProfileScreen';

const MOCK_PRODUCTS = [
  {
    id: 1,
    brand: 'Chanel',
    title: 'Classic Flap Bag',
    price: 4200,
    currency: '€',
    image: 'https://images.unsplash.com/photo-1548031762-8ae7b1b20b35?w=800&h=1200&fit=crop',
    category: 'Sac',
    size: 'M',
    seller: 'Amina T.',
    trust: 96,
    status: 'active',
    timer: '47:12:33',
    isExchange: false
  },
  {
    id: 2,
    brand: 'Hermès',
    title: 'Birkin 30 — Noir Gold',
    price: 12500,
    currency: '€',
    image: 'https://images.unsplash.com/photo-1566150706505-5db913b6e6f7?w=800&h=1200&fit=crop',
    category: 'Sac',
    size: '30',
    seller: 'Leila M.',
    trust: 98,
    status: 'active',
    timer: '23:45:10',
    isExchange: false
  },
  {
    id: 3,
    brand: 'Dior',
    title: 'Lady Dior — Rose',
    price: 3800,
    currency: '€',
    image: 'https://images.unsplash.com/photo-1594271804399-c33b40e32130?w=800&h=1200&fit=crop',
    category: 'Sac',
    size: 'S',
    seller: 'Yassine B.',
    trust: 92,
    status: 'active',
    timer: '71:30:00',
    isExchange: false
  }
];

const DRESSING_ITEMS = [
  { id: 1, brand: 'Chanel', title: 'Classic Flap Bag', price: 4200, status: 'Enchère ouverte', type: 'vente', image: 'https://images.unsplash.com/photo-1548031762-8ae7b1b20b35?w=400&h=533&fit=crop' },
  { id: 2, brand: 'Dior', title: 'Lady Dior', price: 3800, status: 'Timer 12h', type: 'vente', image: 'https://images.unsplash.com/photo-1594271804399-c33b40e32130?w=400&h=533&fit=crop' },
  { id: 3, brand: 'Vintage', title: 'Rolex Datejust', price: 6500, status: 'Échange', type: 'echange', image: 'https://images.unsplash.com/photo-1547913247-953d4e7b8099?w=400&h=533&fit=crop' }
];

function App() {
  const [activeTab, setActiveTab] = React.useState('swipe');
  const [favorites, setFavorites] = React.useState([]);

  const handleAddFavorite = (product) => {
    setFavorites([...favorites, product]);
  };

  return (
    <div className="lokko-app">
      {activeTab === 'swipe' && <SwipeFeed products={MOCK_PRODUCTS} onFavorite={handleAddFavorite} />}
      {activeTab === 'search' && <SearchScreen />}
      {activeTab === 'publish' && <StudioScreen />}
      {activeTab === 'dressing' && <DressingScreen items={DRESSING_ITEMS} />}
      {activeTab === 'profile' && <ProfileScreen />}
      
      {activeTab !== 'publish' && (
        <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
      )}
    </div>
  );
}

export default App;