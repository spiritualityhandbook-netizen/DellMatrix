# Nature Forces in DellMatrix

## What This Is

DellMatrix grows like nature.

Ideas are not static files. They are living things that flow, grow, breathe, pull, age, and weather.

**Forces** are modular matrices that snap into the main matrix. Each force affects how ideas behave. People can create new forces. Forces evolve with use.

---

## The Core Forces

### 1. Water
Ideas flow like water.
- They take the shape of any container
- Streams merge into rivers (synchronization)
- Pools are settled, stable ideas
- Mist is early, light ideas

**How to see it:** Watch streams form and merge. When two streams meet, resonance occurs.

### 2. Growth (Plant / Tree)
Ideas grow in visible stages:
```
seed → sprout → stem → branch → leaf → fruit
```
You can always see what stage an idea is in and how tall it has grown.

**How to see it:** The growth map shows every plant with its current stage and height.

### 3. Breath
The matrix breathes.
- **Inhale** = gather ideas
- **Exhale** = release and share
- Heartbeat creates shared rhythm
- Synchronization is matching rhythm

**How to see it:** Watch the phase (inhale/exhale) and cycle count.

### 4. Gravity
Ideas have mass.
- Important ideas become gravity wells
- Other ideas are pulled toward them
- Clusters form around heavy meaning

### 5. Time
Everything ages.
- Ideas ripen or fade
- Cycles create long rhythm
- The clock only moves forward

### 6. Weather
The atmosphere of the matrix.
- Clear = high visibility
- Rain = new seeds fall
- Storm = stuck ideas are shaken loose
- Fog = reduced clarity (planned fog from the Harmonic Cube)

### 7. Space
Distance and nearness.
- Ideas occupy positions
- Near ideas are more likely to resonate
- Distance creates perspective

---

## How Growth Becomes Visible

1. **Plant an idea** → it starts as a seed
2. **Water + sunlight** (attention + connection) → it grows stages
3. **Watch the growth map** → you see exactly what grew and when
4. **Streams meet** → resonance is recorded
5. **Breath cycles** → the whole matrix pulses together

---

## Creating New Forces

Anyone can create a force. A force is just a class that extends `ForceMatrix` and implements `apply()`.

```js
import { ForceMatrix } from './nature_forces.js';

class MyCustomForce extends ForceMatrix {
  constructor() {
    super({ name: 'MyForce', type: 'custom', intensity: 0.5 });
  }
  apply(target) {
    // your effect here
    return { applied: 'myforce' };
  }
}
```

Then register it:
```js
registry.register(new MyCustomForce());
```

---

## Next Steps

- Connect forces to the visual dashboard so growth is drawn, not just logged
- Let people drop ideas into the matrix and watch them become water streams or plants
- Make resonance visible as shared pulses between nodes
- Allow force evolution to unlock new behaviors
