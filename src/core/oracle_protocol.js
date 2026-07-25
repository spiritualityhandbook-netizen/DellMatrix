/**
 * Oracle Protocol mechanics (structural)
 *
 * Not mysticism. Mechanics:
 * - Deferred prediction with horizon + direction
 * - Uncertainty labeled (never presented as proven fact)
 * - Optional residual path (skip / add) like neural residuals
 * - Attention = current center + active lens
 * - Aligns with Cheat Code Mode in Evo directive
 */

export const ORACLE_DIRECTIONS = ['forward', 'back', 'side', 'up', 'down', 'in', 'out'];
export const ORACLE_HORIZONS = {
  cold: 1,
  warm: 2,
  hot: 3
};

export class OracleProtocol {
  constructor() {
    this.active = false;
    this.direction = 'forward';
    this.horizon = 'cold';
    this.log = [];
  }

  enable({ direction = 'forward', horizon = 'cold' } = {}) {
    this.active = true;
    this.direction = ORACLE_DIRECTIONS.includes(direction) ? direction : 'forward';
    this.horizon = ORACLE_HORIZONS[horizon] ? horizon : 'cold';
    return this.status();
  }

  disable() {
    this.active = false;
    return this.status();
  }

  status() {
    return {
      active: this.active,
      direction: this.direction,
      horizon: this.horizon,
      steps: ORACLE_HORIZONS[this.horizon] || 1
    };
  }

  /**
   * Project N steps along direction from a lattice snapshot.
   * Output is always labeled projected — not fact.
   */
  project(latticeSnapshot = {}, context = {}) {
    if (!this.active) {
      return { ok: false, error: 'Oracle off. Enable first.' };
    }
    const steps = ORACLE_HORIZONS[this.horizon] || 1;
    const baseNodes = latticeSnapshot.nodeCount || 0;
    const generation = latticeSnapshot.generation || 0;

    // Simple structural projection (not ML training claim)
    const projections = [];
    for (let i = 1; i <= steps; i += 1) {
      projections.push({
        step: i,
        direction: this.direction,
        estimatedNodes: baseNodes + i,
        estimatedGeneration: generation + i,
        note: 'projected'
      });
    }

    const result = {
      ok: true,
      label: 'PROJECTED_NOT_FACT',
      direction: this.direction,
      horizon: this.horizon,
      steps,
      projections,
      context,
      at: new Date().toISOString()
    };
    this.log.push(result);
    return result;
  }
}

export function createOracle() {
  return new OracleProtocol();
}
