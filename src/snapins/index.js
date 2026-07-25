/**
 * Snap-in loader — unified + control plane established
 */

import { createFoundation } from '../core/foundation.js';
import viewRoomsSnapIn from './view_rooms.js';
import workshopsSnapIn from './workshops.js';
import personasPackSnapIn from './personas_pack.js';
import mandelStationSnapIn from './mandel_station.js';
import smithPackSnapIn from './smith_pack.js';
import controlPlaneSnapIn from './control_plane_pack.js';

export function bootDellMatrix(options = {}) {
  const foundation = createFoundation(options);

  foundation.registerSnapIn(viewRoomsSnapIn);
  foundation.registerSnapIn(workshopsSnapIn);
  foundation.registerSnapIn(personasPackSnapIn);
  foundation.registerSnapIn(mandelStationSnapIn);
  foundation.registerSnapIn(smithPackSnapIn);
  foundation.registerSnapIn(controlPlaneSnapIn);

  foundation.snapIn('view-rooms');
  foundation.snapIn('personas-pack');
  foundation.snapIn('mandel-station');
  foundation.snapIn('smith-pack');
  foundation.snapIn('control-plane');

  return foundation;
}

export {
  viewRoomsSnapIn,
  workshopsSnapIn,
  personasPackSnapIn,
  mandelStationSnapIn,
  smithPackSnapIn,
  controlPlaneSnapIn
};
export { createFoundation } from '../core/foundation.js';
