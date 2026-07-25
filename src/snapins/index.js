/**
 * Snap-in loader
 * Registers the standard modular packs into a foundation instance.
 */

import { createFoundation } from '../core/foundation.js';
import viewRoomsSnapIn from './view_rooms.js';
import workshopsSnapIn from './workshops.js';

export function bootDellMatrix(options = {}) {
  const foundation = createFoundation(options);

  // Register modular packs (they are not active until snapped in)
  foundation.registerSnapIn(viewRoomsSnapIn);
  foundation.registerSnapIn(workshopsSnapIn);

  // Default: snap view-rooms in so looking works immediately
  // Workshops stay registered but snapped out until needed
  foundation.snapIn('view-rooms');

  return foundation;
}

export { viewRoomsSnapIn, workshopsSnapIn };
export { createFoundation } from '../core/foundation.js';
