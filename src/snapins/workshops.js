/**
 * Workshop Rooms — snap-in pack
 */

export const workshopsSnapIn = {
  id: 'workshops',
  type: 'workshop',
  name: 'Workshop Rooms',
  description: 'Persona, Perspective, Matrix, BIMO, Psalms, Mandel language workbenches',

  workshops: {
    matrix: {
      id: 'matrix',
      name: 'Matrix Workshop',
      description: 'Flower of Life / sphere mode, choose center, zoom shells',
      canEdit: ['center', 'zoom', 'shell-view', 'sphere-mode', 'flower-mode']
    },
    persona: {
      id: 'persona',
      name: 'Persona Workshop',
      description: 'Create and edit AIs — directives, abilities, limits, personality',
      canEdit: ['directives', 'abilities', 'limits', 'personality', 'emoji', 'role']
    },
    perspective: {
      id: 'perspective',
      name: 'Perspective Workshop',
      description: 'Design and tune view rooms / lenses',
      canEdit: ['lens-rules', 'filters', 'room-layout']
    },
    bimo: {
      id: 'bimo',
      name: 'BIMO Workshop',
      description: 'Fusion bodies that can hold multiple agents',
      canEdit: ['slots', 'fusion-rules', 'docking']
    },
    psalms: {
      id: 'psalms',
      name: 'Psalms Workshop',
      description: 'Create and edit psalms / guidance texts',
      canEdit: ['content', 'theme', 'archetype', 'strength']
    },
    mandel: {
      id: 'mandel',
      name: 'Mandel Workshop',
      description: 'Work on the language itself — commands, syntax, meaning',
      canEdit: ['commands', 'syntax', 'tokens', 'operators']
    }
  },

  attach(foundation) {
    foundation._workshops = this.workshops;
    foundation._activeWorkshop = null;
  },

  detach(foundation) {
    delete foundation._workshops;
    delete foundation._activeWorkshop;
  },

  api: {
    listWorkshops(foundation) {
      return Object.values(foundation._workshops || {});
    },
    enterWorkshop(foundation, workshopId) {
      if (!foundation._workshops?.[workshopId]) return null;
      foundation._activeWorkshop = workshopId;
      return foundation._workshops[workshopId];
    },
    leaveWorkshop(foundation) {
      const prev = foundation._activeWorkshop;
      foundation._activeWorkshop = null;
      return prev;
    },
    getActiveWorkshop(foundation) {
      const id = foundation._activeWorkshop;
      return id ? foundation._workshops[id] : null;
    }
  }
};

export default workshopsSnapIn;
