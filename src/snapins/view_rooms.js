/**
 * View Rooms — snap-in pack
 * These only CHANGE HOW YOU LOOK at the foundation lattice.
 * They do not own the data.
 */

export const viewRoomsSnapIn = {
  id: 'view-rooms',
  type: 'view',
  name: 'View Rooms',
  description: 'Growth, Water, Force, Network, Personal, Shared, Ancient Psalms — lenses only',

  rooms: {
    growth: { id: 'growth', name: 'Growth', description: 'Ideas as plants with stages' },
    water: { id: 'water', name: 'Water', description: 'Ideas as streams that merge' },
    force: { id: 'force', name: 'Force', description: 'Forces in the voids' },
    network: { id: 'network', name: 'Network', description: 'Connections and strength' },
    personal: { id: 'personal', name: 'Personal', description: 'Only what you planted' },
    shared: { id: 'shared', name: 'Shared', description: 'Ideas that resonated with others' },
    ancient_psalms: {
      id: 'ancient_psalms',
      name: 'Ancient Psalms',
      description: 'Ledger lists, totals, reverse walk, short tokens',
      emoji: '🏺📜🗿'
    }
  },

  attach(foundation) {
    foundation._viewRooms = this.rooms;
    foundation._activeView = foundation._activeView || 'growth';
  },

  detach(foundation) {
    delete foundation._viewRooms;
    delete foundation._activeView;
  },

  api: {
    listRooms(foundation) {
      return Object.values(foundation._viewRooms || {});
    },
    setView(foundation, roomId) {
      if (!foundation._viewRooms?.[roomId]) return null;
      foundation._activeView = roomId;
      return roomId;
    },
    getView(foundation) {
      return foundation._activeView || null;
    }
  }
};

export default viewRoomsSnapIn;
