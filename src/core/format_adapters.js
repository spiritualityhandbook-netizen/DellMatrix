/**
 * Format adapters
 * JSON fully implemented.
 * TOML / YAML / HCL are declared surfaces with stubs until offline libs are added.
 */

export const adaptJSON = {
  id: 'json',
  ready: true,
  parse(text) {
    return JSON.parse(text);
  },
  serialize(obj) {
    return JSON.stringify(obj, null, 2);
  }
};

export const adaptTOML = {
  id: 'toml',
  ready: false,
  parse() {
    throw new Error('TOML adapter stub — add offline TOML lib to enable');
  },
  serialize() {
    throw new Error('TOML adapter stub — add offline TOML lib to enable');
  }
};

export const adaptYAML = {
  id: 'yaml',
  ready: false,
  parse() {
    throw new Error('YAML adapter stub — add offline YAML lib to enable');
  },
  serialize() {
    throw new Error('YAML adapter stub — add offline YAML lib to enable');
  }
};

export const adaptHCL = {
  id: 'hcl',
  ready: false,
  parse() {
    throw new Error('HCL adapter stub — add offline HCL lib to enable');
  },
  serialize() {
    throw new Error('HCL adapter stub — add offline HCL lib to enable');
  }
};

export const ADAPTERS = {
  json: adaptJSON,
  toml: adaptTOML,
  yaml: adaptYAML,
  hcl: adaptHCL
};

export function getAdapter(format) {
  return ADAPTERS[format] || null;
}

export function listAdapters() {
  return Object.values(ADAPTERS).map(a => ({ id: a.id, ready: a.ready }));
}
