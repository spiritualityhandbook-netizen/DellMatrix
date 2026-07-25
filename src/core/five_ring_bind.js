/**
 * Voynich-inspired 5-Ring structural bind (creative OS mapping only)
 * Herbal=Input, Astro=Clock, Bio=Process, Pharma=Transform, Recipe=Output
 */

export const FIVE_RINGS = {
  herbal:  { id: 'herbal',  role: 'input',         meaning: 'Data / seed intake' },
  astro:   { id: 'astro',   role: 'clock',         meaning: 'Time cycle / tempo' },
  bio:     { id: 'bio',     role: 'process',       meaning: 'Coherence / living process' },
  pharma:  { id: 'pharma',  role: 'transform',     meaning: 'Change / application' },
  recipe:  { id: 'recipe',  role: 'output',        meaning: 'Terminal result / query' }
};

export class FiveRingBind {
  constructor() {
    this.rings = {
      herbal: [],
      astro: [],
      bio: [],
      pharma: [],
      recipe: []
    };
  }

  place(ringId, item) {
    if (!this.rings[ringId]) return null;
    const entry = {
      ...item,
      ring: ringId,
      at: new Date().toISOString()
    };
    this.rings[ringId].push(entry);
    return entry;
  }

  /** Retrograde: recipe queries backward toward herbal */
  queryFromRecipe(recipeIndex = 0) {
    const recipe = this.rings.recipe[recipeIndex] || null;
    return {
      recipe,
      pharma: this.rings.pharma.slice(-3),
      bio: this.rings.bio.slice(-3),
      astro: this.rings.astro.slice(-3),
      herbal: this.rings.herbal.slice(-5),
      flow: 'recipe → pharma → bio → astro → herbal'
    };
  }

  snapshot() {
    return {
      counts: {
        herbal: this.rings.herbal.length,
        astro: this.rings.astro.length,
        bio: this.rings.bio.length,
        pharma: this.rings.pharma.length,
        recipe: this.rings.recipe.length
      },
      rings: FIVE_RINGS
    };
  }
}

export function createFiveRingBind() {
  return new FiveRingBind();
}
