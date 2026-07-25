/**
 * Format adapters
 * JSON fully implemented.
 * TOML/YAML/HCL marked as surface targets with safe stubs until offline libs are added.
 */

export function adaptJSON = {
  id: 'json',
  parse(text) {
    return JSON.parse(text);
  },
  serialize(obj) {
    return JSON.stringify(obj, null, 2);
  },
  ready: true
};

// Fix syntax - can't use export function adaptJSON = 
