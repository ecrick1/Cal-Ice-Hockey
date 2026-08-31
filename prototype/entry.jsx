import { createRoot } from 'react-dom/client';
import CalIceHockey from '../reference/cal-ice-hockey-app.jsx';

/**
 * The prototype was written for an artifact host that provides an async
 * `window.storage`. Back it with localStorage so the file runs in a normal
 * browser. loadKey() expects `{ value: <json string> }` or a falsy result.
 */
window.storage = {
  async get(key) {
    const value = localStorage.getItem(key);
    return value === null ? null : { value };
  },
  async set(key, value) {
    localStorage.setItem(key, value);
  },
};

createRoot(document.getElementById('root')).render(<CalIceHockey />);
