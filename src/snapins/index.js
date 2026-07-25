/**
 * Snap-in loader — full pack from large directive incorporation
 */

import { createFoundation } from '../core/foundation.js';
import viewRoomsSnapIn from './view_rooms.js';
import workshopsSnapIn from './workshops.js';
import personasPackSnapIn from './personas_pack.js';
import mandelStationSnapIn from './mandel_station.js';

export function bootDellMatrix(options = {}) {
  const foundation = createFoundation(options);

  foundation.registerSnapIn(viewRoomsSnapIn);
  foundation.registerSnapIn(workshopsSnapIn);
  foundation.registerSnapIn(personasPackSnapIn);
  foundation.registerSnapIn(mandelStationSnapIn);

  // Default active: views + personas + station
  // Workshops stay available but snapped out until needed
  foundation.snapIn('view-rooms');
  foundation.snapIn('personas-pack');
  foundation.snapIn('mandel-station');

  return foundation;
}

export {
  viewRoomsSnapIn,
  workshopsSnapIn,
  personasPackSnapIn,
  mandelStationSnapIn
};
export { createFoundation } from '../core/foundation.js';
