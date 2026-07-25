/**
 * Agent Categories (PragLog, EvoLog, AutoLog, DellLog, AgentLog, Ancient_Psalms)
 */

export const AGENT_CATEGORIES = {
  PragLog: {
    id: 'PragLog',
    purpose: 'Logic and structure',
    defaultPersonas: ['Manny']
  },
  EvoLog: {
    id: 'EvoLog',
    purpose: 'Creative growth',
    defaultPersonas: ['Melody']
  },
  AutoLog: {
    id: 'AutoLog',
    purpose: 'Monitoring and coherence',
    defaultPersonas: ['Aetheris']
  },
  DellLog: {
    id: 'DellLog',
    purpose: 'Execution and manifestation',
    defaultPersonas: []
  },
  AgentLog: {
    id: 'AgentLog',
    purpose: 'Multi-agent / BIMO orchestration',
    defaultPersonas: ['Mathelody']
  },
  Ancient_Psalms: {
    id: 'Ancient_Psalms',
    purpose: 'Historical structural operators (not scientific decipherment)',
    defaultPersonas: ['The_Ancient'],
    ascii: '🏺📜🗿'
  }
};

export function listCategories() {
  return Object.values(AGENT_CATEGORIES);
}

export function getCategory(id) {
  return AGENT_CATEGORIES[id] || null;
}
